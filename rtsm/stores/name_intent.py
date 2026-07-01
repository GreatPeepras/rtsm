"""
name_intent.py  —  Deferred name-intent reconciliation for RTSM.
Marker: NAME_INTENT_2026-06-29

Problem this solves
-------------------
`name_object()` on Albert can only label objects RTSM has ALREADY confirmed.
Ingest confirmation lags dispatch by tens of seconds (the "giant egg" took ~60s
/ 19 hits / 2 view-bins), so a one-shot search at +9s finds nothing and the
label is silently dropped. This module lets Albert register a PENDING intent
carrying the named-moment crop; RTSM then reconciles it against objects as they
confirm, using image->image CLIP cosine (the object's emb_mean vs the crop's
embedding) as the match signal.

Why image->image: the egg's own object scored 0.0869 for the TEXT query
"large white egg" — inside RTSM's indoor text->image noise band (0.05-0.15), so
a score floor is useless there. Same-modality (image->image) cosine for the same
physical object sits at ~0.7-0.9 and drops sharply for different objects. That
gap is what separates the egg from the carpet/bowl/knife that confirm seconds
apart.

This module is dependency-light (numpy + stdlib) and holds NO references to
ObjectState. The caller (WorkingMemory) passes in the object's emb_mean / xyz and
applies label_user on a returned hit. The registry owns its own RLock.
"""

from __future__ import annotations

import math
import os
import time
import uuid
import logging
from dataclasses import dataclass, field
from threading import RLock
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

logger = logging.getLogger("rtsm.name_intent")


def _now_mono() -> float:
    return time.monotonic()


def _now_wall() -> float:
    return time.time()


def _envf(name: str, default: float) -> float:
    try:
        return float(os.environ.get(name, str(default)))
    except (TypeError, ValueError):
        return default


def _envi(name: str, default: int) -> int:
    try:
        return int(os.environ.get(name, str(default)))
    except (TypeError, ValueError):
        return default


@dataclass
class NameIntent:
    intent_id: str
    label: str                      # -> becomes label_user, e.g. "giant egg"
    description: str                # what name_object searched, e.g. "large white egg"
    memory_name: str                # local memory.json entry name to backfill
    intent_emb: Optional[np.ndarray]      # L2-normalized image embedding (float32) or None
    robot_pose: Optional[Dict[str, Any]]  # {xyz, quaternion_xyzw, timestamp} at register
    t_register_mono: float
    t_register_wall: float
    ttl_s: float
    resolved_oid: Optional[str] = None
    resolved_sim: Optional[float] = None
    resolved_wall: Optional[float] = None
    acked: bool = False

    def age_s(self) -> float:
        return _now_mono() - self.t_register_mono

    def expired(self) -> bool:
        return (self.resolved_oid is None) and (self.age_s() > self.ttl_s)

    def to_public(self) -> Dict[str, Any]:
        return {
            "intent_id": self.intent_id,
            "label": self.label,
            "description": self.description,
            "memory_name": self.memory_name,
            "age_s": round(self.age_s(), 2),
            "ttl_s": self.ttl_s,
            "has_emb": self.intent_emb is not None,
            "oid": self.resolved_oid,
            "sim": (round(self.resolved_sim, 4) if self.resolved_sim is not None else None),
            "acked": self.acked,
        }


@dataclass
class ResolvedMatch:
    intent_id: str
    label: str
    memory_name: str
    oid: str
    sim: float


def _quat_conj_rotate(q_xyzw, v) -> Tuple[float, float, float]:
    """Rotate world vector v into body frame using the CONJUGATE of q (world->body).
    q is [x,y,z,w]. Returns body-frame vector."""
    x, y, z, w = q_xyzw
    # conjugate (inverse for unit quat) = [-x,-y,-z,w]
    cx, cy, cz, cw = -x, -y, -z, w
    vx, vy, vz = v
    # rotate v by quaternion cq: t = 2 * cross(cq.xyz, v); v' = v + cw*t + cross(cq.xyz, t)
    tx = 2.0 * (cy * vz - cz * vy)
    ty = 2.0 * (cz * vx - cx * vz)
    tz = 2.0 * (cx * vy - cy * vx)
    rx = vx + cw * tx + (cy * tz - cz * ty)
    ry = vy + cw * ty + (cz * tx - cx * tz)
    rz = vz + cw * tz + (cx * ty - cy * tx)
    return rx, ry, rz


def bearing_ok(robot_pose: Optional[Dict[str, Any]],
               obj_xyz,
               fov_deg: float) -> bool:
    """Soft geometric sanity: is obj roughly in front of the robot within the
    camera half-FOV? Returns True (pass) when pose is missing — the gate is a
    secondary signal only; image cosine is primary.

    Body-frame convention assumed: +X forward. If your map/body frame differs,
    adjust the forward axis below. Because object xyz drifts for movables, this
    is intentionally permissive."""
    if not robot_pose:
        return True
    try:
        rxyz = robot_pose.get("xyz")
        q = robot_pose.get("quaternion_xyzw")
        if rxyz is None or q is None or obj_xyz is None:
            return True
        dx = float(obj_xyz[0]) - float(rxyz[0])
        dy = float(obj_xyz[1]) - float(rxyz[1])
        dz = float(obj_xyz[2]) - float(rxyz[2])
        bx, by, bz = _quat_conj_rotate(q, (dx, dy, dz))
        # forward = +X; angle off boresight in the horizontal plane
        horiz = math.hypot(bx, by)
        if horiz < 1e-6:
            return True
        ang = math.degrees(math.atan2(abs(by), bx))   # 0 = dead ahead
        return (bx > 0.0) and (ang <= fov_deg)
    except Exception:
        return True


class NameIntentRegistry:
    """Thread-safe registry of pending name-intents with image->image matching.

    Caller contract:
      * register(...) -> intent_id
      * reconcile_object(oid, emb_mean, xyz_world, has_user_label) -> ResolvedMatch|None
            Call this right after an object is confirmed (and also against recent
            confirmed objects at registration time). On a hit it marks the intent
            resolved internally; the CALLER applies obj.label_user = match.label.
      * list_live(), list_resolved_unacked(), ack(intent_id), prune()
    """

    def __init__(self, cfg: Optional[Dict[str, Any]] = None) -> None:
        cfg = cfg or {}
        self._lock = RLock()
        self._intents: Dict[str, NameIntent] = {}
        self.ttl_s_default = _envf("NAME_INTENT_TTL_S", float(cfg.get("ttl_s", 300.0)))
        self.img_floor = _envf("NAME_INTENT_IMG_FLOOR", float(cfg.get("img_floor", 0.62)))
        self.max_pending = _envi("NAME_INTENT_MAX_PENDING", int(cfg.get("max_pending", 8)))
        self.resolved_grace_s = _envf("NAME_INTENT_RESOLVED_GRACE_S",
                                      float(cfg.get("resolved_grace_s", 300.0)))
        self.fov_deg = _envf("NAME_INTENT_FOV_DEG", float(cfg.get("fov_deg", 35.0)))
        self.bearing_penalty = _envf("NAME_INTENT_BEARING_PENALTY",
                                     float(cfg.get("bearing_penalty", 0.10)))
        self.bearing_fallback_sim = _envf("NAME_INTENT_BEARING_FALLBACK_SIM",
                                          float(cfg.get("bearing_fallback_sim", 0.63)))
        logger.info(
            f"[name-intent] registry init: ttl={self.ttl_s_default}s "
            f"img_floor={self.img_floor} max_pending={self.max_pending} "
            f"fov={self.fov_deg}deg"
        )

    # ---------------- registration ----------------

    def register(self, *, label: str, description: str, memory_name: str,
                 intent_emb: Optional[np.ndarray],
                 robot_pose: Optional[Dict[str, Any]],
                 ttl_s: Optional[float] = None) -> str:
        if intent_emb is not None:
            intent_emb = np.asarray(intent_emb, dtype=np.float32)
            n = float(np.linalg.norm(intent_emb))
            if n > 1e-8:
                intent_emb = intent_emb / n
        it = NameIntent(
            intent_id=uuid.uuid4().hex,
            label=label,
            description=description,
            memory_name=memory_name,
            intent_emb=intent_emb,
            robot_pose=robot_pose,
            t_register_mono=_now_mono(),
            t_register_wall=_now_wall(),
            ttl_s=float(ttl_s if ttl_s is not None else self.ttl_s_default),
        )
        with self._lock:
            self._prune_locked()
            # cap on live unresolved: evict oldest unresolved if over
            live = [x for x in self._intents.values() if x.resolved_oid is None]
            if len(live) >= self.max_pending:
                oldest = min(live, key=lambda x: x.t_register_mono)
                self._intents.pop(oldest.intent_id, None)
                logger.warning(
                    f"[name-intent] pending cap hit; evicted oldest "
                    f"intent={oldest.intent_id[:8]} label={oldest.label!r}"
                )
            self._intents[it.intent_id] = it
        logger.info(
            f"[name-intent] registered intent={it.intent_id[:8]} label={label!r} "
            f"desc={description!r} has_emb={intent_emb is not None} ttl={it.ttl_s}s"
        )
        return it.intent_id

    # ---------------- reconciliation ----------------

    def reconcile_object(self, oid: str, emb_mean: Optional[np.ndarray],
                         xyz_world: Optional[Any],
                         has_user_label: bool) -> Optional[ResolvedMatch]:
        """Match a (newly-confirmed) object against pending intents.
        Returns a ResolvedMatch on success (intent marked resolved), else None.
        The caller applies obj.label_user = match.label."""
        if has_user_label or emb_mean is None:
            return None
        oemb = np.asarray(emb_mean, dtype=np.float32)
        n = float(np.linalg.norm(oemb))
        if n < 1e-8:
            return None
        oemb = oemb / n

        with self._lock:
            self._prune_locked()
            best: Optional[NameIntent] = None
            best_sim = -1.0
            for it in self._intents.values():
                if it.resolved_oid is not None:
                    continue
                if it.intent_emb is None:
                    # no crop embedding: bearing-only fallback (weak)
                    if bearing_ok(it.robot_pose, xyz_world, self.fov_deg):
                        sim = self.bearing_fallback_sim
                    else:
                        continue
                else:
                    sim = float(np.dot(it.intent_emb, oemb))
                    if not bearing_ok(it.robot_pose, xyz_world, self.fov_deg):
                        sim -= self.bearing_penalty
                if sim > best_sim:
                    best_sim = sim
                    best = it
            if best is None or best_sim < self.img_floor:
                return None
            best.resolved_oid = oid
            best.resolved_sim = best_sim
            best.resolved_wall = _now_wall()
            logger.info(
                f"[name-intent] RESOLVED intent={best.intent_id[:8]} "
                f"label={best.label!r} -> oid={str(oid)[:8]} sim={best_sim:.3f}"
            )
            return ResolvedMatch(
                intent_id=best.intent_id, label=best.label,
                memory_name=best.memory_name, oid=oid, sim=best_sim,
            )

    # ---------------- queries / lifecycle ----------------

    def list_live(self) -> List[Dict[str, Any]]:
        with self._lock:
            self._prune_locked()
            return [it.to_public() for it in self._intents.values()]

    def list_resolved_unacked(self) -> List[Dict[str, Any]]:
        with self._lock:
            self._prune_locked()
            return [
                {
                    "intent_id": it.intent_id,
                    "label": it.label,
                    "memory_name": it.memory_name,
                    "oid": it.resolved_oid,
                    "sim": (round(it.resolved_sim, 4) if it.resolved_sim is not None else None),
                }
                for it in self._intents.values()
                if it.resolved_oid is not None and not it.acked
            ]

    def ack(self, intent_id: str) -> bool:
        with self._lock:
            it = self._intents.get(intent_id)
            if it is None:
                return False
            it.acked = True
            # drop immediately once acked
            self._intents.pop(intent_id, None)
            return True

    def prune(self) -> int:
        with self._lock:
            return self._prune_locked()

    def _prune_locked(self) -> int:
        now_m = _now_mono()
        drop = []
        for iid, it in self._intents.items():
            if it.resolved_oid is None:
                if it.age_s() > it.ttl_s:
                    drop.append(iid)
            else:
                # resolved: keep for grace window so Albert can poll, unless acked
                if it.acked:
                    drop.append(iid)
                elif (now_m - it.t_register_mono) > (it.ttl_s + self.resolved_grace_s):
                    drop.append(iid)
        for iid in drop:
            it = self._intents.pop(iid, None)
            if it is not None and it.resolved_oid is None:
                logger.info(
                    f"[name-intent] EXPIRED intent={iid[:8]} label={it.label!r} "
                    f"(no object confirmed within {it.ttl_s}s)"
                )
        return len(drop)


__all__ = ["NameIntent", "NameIntentRegistry", "ResolvedMatch", "bearing_ok"]

"""Offline unit tests for Tier-2 movability-aware eviction.

Mirrors the house style in tests/test_object_patch.py: a check() helper,
direct _map stuffing with SimpleNamespace stubs, print-based progress.
No live robot, no camera, no FAISS -- pure WM policy logic.

Run:  cd /path/to/rtsm && python3 test_eviction_policy.py
"""
from __future__ import annotations
from types import SimpleNamespace
from typing import Any, Optional

from rtsm.stores.working_memory import WorkingMemory

DAY = 86400.0
HOUR = 3600.0
NOW = 1_000_000_000.0  # fixed wall clock for determinism

results: list[tuple[str, bool, str]] = []

def check(name: str, cond: bool, detail: str = "") -> None:
    results.append((name, cond, detail))
    mark = "PASS" if cond else "FAIL"
    print(f"  [{mark}] {name}" + (f"  -- {detail}" if detail else ""))
    assert cond, f"{name}: {detail}" if detail else name

def make_obj(oid: str, *, confirmed: bool = True, movability: Optional[str] = None,
             label_user: Optional[str] = None, age_s: float = 0.0,
             label_primary: str = "thing") -> Any:
    """A WM-object stub with last_seen age_s SECONDS before NOW."""
    return SimpleNamespace(
        id=oid,
        confirmed=confirmed,
        movability_class=movability,
        label_user=label_user,
        label_primary=label_primary,
        last_seen_wall_utc=(NOW - age_s),
        last_update_frame_id=None,
    )

def fresh_wm(cfg: dict | None = None) -> WorkingMemory:
    return WorkingMemory(cfg=cfg or {})

def stuff(wm: WorkingMemory, *objs: Any) -> None:
    with wm._lock:
        for o in objs:
            wm._map[o.id] = o


print("=== test_eviction_policy.py ===\n")

print("[1] disabled by default -> evict_stale is a no-op")
wm = fresh_wm()
stuff(wm, make_obj("o_old", movability="ephemeral", age_s=999 * DAY))
res = wm.evict_stale(now_wall=NOW)
check("1a enabled False by default", res["enabled"] is False)
check("1b nothing evicted", res["evicted"] == [], f"got {res['evicted']}")
check("1c object still present", wm.get("o_old") is not None)

print("\n[2] TTL boundaries per class (enabled)")
cfg = {"eviction": {"enabled": True}}
wm = fresh_wm(cfg)
stuff(
    wm,
    make_obj("perm",      movability="permanent",   age_s=10_000 * DAY),  # never
    make_obj("static_ok", movability="static",      age_s=89 * DAY),      # < 90d keep
    make_obj("static_go", movability="static",      age_s=91 * DAY),      # > 90d evict
    make_obj("semi_ok",   movability="semi_static",  age_s=13 * DAY),     # < 14d keep
    make_obj("semi_go",   movability="semi_static",  age_s=15 * DAY),     # > 14d evict
    make_obj("mov_ok",    movability="movable",      age_s=2 * DAY),      # < 3d keep
    make_obj("mov_go",    movability="movable",      age_s=4 * DAY),      # > 3d evict
    make_obj("roam_ok",   movability="roaming",      age_s=0.5 * DAY),    # < 1d keep
    make_obj("roam_go",   movability="roaming",      age_s=2 * DAY),      # > 1d evict
    make_obj("eph_ok",    movability="ephemeral",    age_s=6 * HOUR),     # < 12h keep
    make_obj("eph_go",    movability="ephemeral",    age_s=13 * HOUR),    # > 12h evict
)
sel = {d["oid"] for d in wm.select_evictable(now_wall=NOW)}
expected_go = {"static_go", "semi_go", "mov_go", "roam_go", "eph_go"}
expected_keep = {"perm", "static_ok", "semi_ok", "mov_ok", "roam_ok", "eph_ok"}
check("2a exactly the >TTL objects selected", sel == expected_go,
      f"selected={sorted(sel)}")
check("2b permanent never selected", "perm" not in sel)

print("\n[3] HARD INVARIANT: label_user is never evicted")
wm = fresh_wm({"eviction": {"enabled": True}})
stuff(
    wm,
    make_obj("named", movability="ephemeral", age_s=999 * DAY, label_user="Quackers"),
    make_obj("anon",  movability="ephemeral", age_s=999 * DAY),
)
sel = {d["oid"] for d in wm.select_evictable(now_wall=NOW)}
check("3a named object excluded from selection", "named" not in sel)
check("3b anon object selected", "anon" in sel)
res = wm.evict_stale(now_wall=NOW)
check("3c named survives actual eviction", wm.get("named") is not None)
check("3d anon actually removed", wm.get("anon") is None)

print("\n[4] None/unset movability -> falls back to semi_static (14d)")
wm = fresh_wm({"eviction": {"enabled": True}})
stuff(
    wm,
    make_obj("unset_ok", movability=None, age_s=13 * DAY),  # < 14d keep
    make_obj("unset_go", movability=None, age_s=15 * DAY),  # > 14d evict
)
sel = wm.select_evictable(now_wall=NOW)
sel_ids = {d["oid"] for d in sel}
check("4a unset<14d kept", "unset_ok" not in sel_ids)
check("4b unset>14d evicted", "unset_go" in sel_ids)
check("4c reported effective class is semi_static",
      all(d["movability_class"] == "semi_static" for d in sel),
      f"got {[d['movability_class'] for d in sel]}")

print("\n[5] protos (confirmed=False) are ignored")
wm = fresh_wm({"eviction": {"enabled": True}})
stuff(wm, make_obj("proto", confirmed=False, movability="ephemeral", age_s=999 * DAY))
check("5a proto not selected", wm.select_evictable(now_wall=NOW) == [])
wm.evict_stale(now_wall=NOW)
check("5b proto still present", wm.get("proto") is not None)

print("\n[6] unknown last_seen (==0) is never evicted (conservative)")
wm = fresh_wm({"eviction": {"enabled": True}})
o = make_obj("noseen", movability="ephemeral", age_s=999 * DAY)
o.last_seen_wall_utc = 0.0
stuff(wm, o)
check("6a not selected", wm.select_evictable(now_wall=NOW) == [])

print("\n[7] dry_run reports but does not mutate")
wm = fresh_wm({"eviction": {"enabled": True}})
stuff(wm, make_obj("d1", movability="ephemeral", age_s=999 * DAY))
res = wm.evict_stale(now_wall=NOW, dry_run=True)
check("7a dry_run flag echoed", res["dry_run"] is True)
check("7b candidate reported", {d["oid"] for d in res["evicted"]} == {"d1"})
check("7c object NOT removed", wm.get("d1") is not None)

print("\n[8] cfg ttl_s override is honored")
wm = fresh_wm({"eviction": {"enabled": True, "ttl_s": {"static": 1 * DAY}}})
stuff(wm, make_obj("s", movability="static", age_s=2 * DAY))  # 2d > overridden 1d
check("8a override shortens static TTL -> evicted",
      {d["oid"] for d in wm.select_evictable(now_wall=NOW)} == {"s"})

print("\n[9] cfg ttl_s override to None = make a class permanent")
wm = fresh_wm({"eviction": {"enabled": True, "ttl_s": {"ephemeral": None}}})
stuff(wm, make_obj("e", movability="ephemeral", age_s=999 * DAY))
check("9a ephemeral->None is never evicted", wm.select_evictable(now_wall=NOW) == [])

print("\n[10] telemetry: by_class counts + ghost_sink hook fires")
wm = fresh_wm({"eviction": {"enabled": True}})
stuff(
    wm,
    make_obj("g1", movability="ephemeral", age_s=2 * DAY),
    make_obj("g2", movability="ephemeral", age_s=3 * DAY),
    make_obj("g3", movability="roaming",   age_s=5 * DAY),
)
seen: list[str] = []
res = wm.evict_stale(now_wall=NOW, ghost_sink=lambda oid, o: seen.append(oid))
check("10a by_class counts correct",
      res["by_class"] == {"ephemeral": 2, "roaming": 1},
      f"got {res['by_class']}")
check("10b ghost_sink saw all evicted", set(seen) == {"g1", "g2", "g3"},
      f"got {seen}")
check("10c all removed", all(wm.get(x) is None for x in ("g1", "g2", "g3")))
check("10d scanned counts confirmed objects", res["scanned"] == 3, f"got {res['scanned']}")

print("\n[11] index.remove called for evicted oids when an index is present")
class _StubIndex:
    def __init__(self): self.removed = []
    def insert(self, *a, **k): pass
    def update(self, *a, **k): pass
    def remove(self, oid, last_xyz_world=None): self.removed.append(oid)
idx = _StubIndex()
wm = WorkingMemory(cfg={"eviction": {"enabled": True}}, index=idx)
stuff(wm, make_obj("ix", movability="ephemeral", age_s=999 * DAY))
wm.evict_stale(now_wall=NOW)
check("11a index.remove received the oid", idx.removed == ["ix"], f"got {idx.removed}")

print(f"\n=== {sum(1 for _,c,_ in results if c)}/{len(results)} checks passed ===")

"""
Gate 2.5 prototype: embedding-based identity matching.

Read-only against the on-disk FAISS sidecar. Demonstrates:
  1. Current PATCH P1 leaks duplicates when same object is re-observed
     at positions separated by more than the 10cm grid.
  2. Embedding-similarity matching (same label + cosine > tau) collapses
     these duplicates correctly.
  3. Safe threshold selection via cross-label similarity audit.

Usage:
    docker exec rtsm-dev python3 /workspace/rtsm/prototype_gate_2_5.py
"""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

import numpy as np

SIDECAR_DIR = Path("/mnt/rtsm-data/model_store/faiss")
META_PATH = SIDECAR_DIR / "index.flatip.meta.json"
IDS_PATH = SIDECAR_DIR / "index.flatip.ids"
EMBS_PATH = SIDECAR_DIR / "index.flatip.embs.npy"


def load_sidecar():
    """Return (meta: dict[oid, meta], emb_by_oid: dict[oid, np.ndarray])."""
    meta = json.loads(META_PATH.read_text())
    ids = [l for l in IDS_PATH.read_text().splitlines() if l.strip()]
    embs = np.load(EMBS_PATH)
    assert len(ids) == embs.shape[0] == len(meta), (
        f"Sidecar inconsistent: {len(ids)} ids, {embs.shape[0]} embs, {len(meta)} meta"
    )
    emb_by_oid = {oid: embs[i] for i, oid in enumerate(ids)}
    return meta, emb_by_oid


# -------- Current P1 identity key (for reference / comparison) --------
def p1_identity_key(m: dict):
    xyz = m.get("xyz")
    label = m.get("label_primary")
    if xyz is None or label is None:
        return None
    try:
        coords = tuple(round(float(c), 1) for c in xyz)
    except (TypeError, ValueError):
        return None
    return (label, coords)


# -------- Gate 2.5 identity match --------
def find_identity_match(
    incoming_label: str,
    incoming_emb: np.ndarray,
    meta: dict,
    emb_by_oid: dict,
    tau: float,
):
    """
    Find an existing OID that is 'the same object' as the incoming observation.
    Returns (matched_oid, cosine_similarity) or (None, best_sim_seen).

    Algorithm: restrict to same label_primary; among those, return the OID
    with highest cosine similarity, iff it exceeds tau. Embeddings are
    assumed L2-normalized (verified in sidecar: norm = 1.0).
    """
    best_oid, best_sim = None, -1.0
    for oid, m in meta.items():
        if m.get("label_primary") != incoming_label:
            continue
        sim = float(np.dot(incoming_emb, emb_by_oid[oid]))
        if sim > best_sim:
            best_sim, best_oid = sim, oid
    if best_oid is not None and best_sim >= tau:
        return best_oid, best_sim
    return None, best_sim


# -------- Diagnostics --------
def cross_label_similarity_audit(meta: dict, emb_by_oid: dict):
    """
    Report the maximum cosine similarity between any two objects with
    DIFFERENT label_primary. This is the headroom below which we can
    safely set tau without causing cross-label merges.
    """
    oids = list(meta.keys())
    worst_sim = -1.0
    worst_pair = None
    for i, a in enumerate(oids):
        la = meta[a]["label_primary"]
        ea = emb_by_oid[a]
        for b in oids[i + 1 :]:
            lb = meta[b]["label_primary"]
            if la == lb:
                continue
            sim = float(np.dot(ea, emb_by_oid[b]))
            if sim > worst_sim:
                worst_sim, worst_pair = sim, (a, la, b, lb)
    return worst_sim, worst_pair


def within_label_similarity_audit(meta: dict, emb_by_oid: dict):
    """
    Report, for each label that has 2+ entries, the min/max/mean pairwise
    cosine similarity. This reveals the existing duplicates in the sidecar.
    """
    by_label = defaultdict(list)
    for oid in meta:
        by_label[meta[oid]["label_primary"]].append(oid)
    report = {}
    for label, oids in by_label.items():
        if len(oids) < 2:
            continue
        sims = []
        for i, a in enumerate(oids):
            for b in oids[i + 1 :]:
                sims.append(float(np.dot(emb_by_oid[a], emb_by_oid[b])))
        report[label] = {
            "n_oids": len(oids),
            "n_pairs": len(sims),
            "min_sim": min(sims),
            "mean_sim": sum(sims) / len(sims),
            "max_sim": max(sims),
            "oids": oids,
        }
    return report


# -------- Synthetic "moved object" test --------
def synthesize_moved_observation(
    source_oid: str, meta: dict, emb_by_oid: dict, delta_xyz=(2.0, 0.0, 0.0), noise_sigma=0.01, seed=0
):
    """
    Construct an incoming observation as if `source_oid` had been re-observed
    after physically moving by `delta_xyz`. Embedding gets small Gaussian
    noise then re-normalized (simulating real observation jitter).
    """
    rng = np.random.default_rng(seed)
    m = meta[source_oid]
    new_xyz = [m["xyz"][i] + delta_xyz[i] for i in range(3)]
    e = emb_by_oid[source_oid].copy()
    e = e + rng.normal(0, noise_sigma, size=e.shape).astype(np.float32)
    e = e / np.linalg.norm(e)
    incoming = {
        "object_id": "synthetic_moved_" + source_oid[:8],
        "xyz": new_xyz,
        "label_primary": m["label_primary"],
    }
    return incoming, e


# -------- Main --------
def main():
    meta, emb_by_oid = load_sidecar()
    print(f"=== Gate 2.5 prototype ===")
    print(f"Sidecar: {len(meta)} objects, embeddings L2-normalized\n")

    # ---- Audit 1: existing within-label duplicates ----
    print("--- Within-label similarity (existing possible duplicates) ---")
    within = within_label_similarity_audit(meta, emb_by_oid)
    if not within:
        print("  (no labels with 2+ entries)")
    for label, r in sorted(within.items(), key=lambda kv: -kv[1]["max_sim"]):
        print(
            f"  {label!r:20s}  n={r['n_oids']}  "
            f"sim min={r['min_sim']:.3f}  mean={r['mean_sim']:.3f}  max={r['max_sim']:.3f}"
        )
    print()

    # ---- Audit 2: cross-label max similarity (tau headroom) ----
    print("--- Cross-label similarity audit (tau headroom) ---")
    worst_sim, worst_pair = cross_label_similarity_audit(meta, emb_by_oid)
    if worst_pair:
        a, la, b, lb = worst_pair
        print(f"  max cross-label sim = {worst_sim:.4f}")
        print(f"    between {a[:8]} ({la!r}) and {b[:8]} ({lb!r})")
    print()

    # ---- Synthetic move test ----
    source_oid = next(oid for oid, m in meta.items() if m["label_primary"] == "night light")
    incoming, incoming_emb = synthesize_moved_observation(source_oid, meta, emb_by_oid)
    print(f"--- Synthetic moved-object test ---")
    print(f"Source OID:   {source_oid}  label={meta[source_oid]['label_primary']!r}")
    print(f"Source xyz:   {[round(c, 3) for c in meta[source_oid]['xyz']]}")
    print(f"Incoming xyz: {[round(c, 3) for c in incoming['xyz']]}  (moved +2.0m in x)")
    print(f"Embedding cosine vs source: {float(np.dot(incoming_emb, emb_by_oid[source_oid])):.4f}")
    print()

    # P1 behavior
    old_key = p1_identity_key(meta[source_oid])
    new_key = p1_identity_key({"xyz": incoming["xyz"], "label_primary": incoming["label_primary"]})
    print(f"P1 identity key (source):   {old_key}")
    print(f"P1 identity key (incoming): {new_key}")
    print(f"P1 would match? {'YES' if old_key == new_key else 'NO (duplicate would be created)'}")
    print()

    # Gate 2.5 behavior at several tau
    print(f"Gate 2.5 match at varying tau:")
    for tau in (0.80, 0.85, 0.90, 0.92, 0.95, 0.98, 0.999):
        matched, sim = find_identity_match(
            incoming["label_primary"], incoming_emb, meta, emb_by_oid, tau
        )
        status = f"match {matched[:8]} (sim={sim:.4f})" if matched else f"no match (best sim={sim:.4f})"
        print(f"  tau={tau:.3f}  ->  {status}")
    print()

    # ---- Recommendation ----
    # Safe tau: above cross-label max, below within-label existing-duplicate min.
    max_cross = worst_sim
    min_within_dup = min(
        (r["min_sim"] for r in within.values()), default=None
    )
    print("--- Threshold recommendation ---")
    print(f"  max cross-label similarity:  {max_cross:.4f}  (tau must be >= this)")
    if min_within_dup is not None:
        print(f"  min within-label duplicate:  {min_within_dup:.4f}  (tau must be <= this to collapse them)")
        if max_cross < min_within_dup:
            suggested = round((max_cross + min_within_dup) / 2, 3)
            print(f"  -> SAFE WINDOW EXISTS. Suggested tau = {suggested}")
        else:
            print(f"  -> NO SAFE WINDOW: cross-label sim exceeds within-label dup sim.")
            print(f"     Would need richer identity signal (position proximity, temporal context).")
    else:
        print("  (no within-label duplicates detected; cannot bound tau from above)")


if __name__ == "__main__":
    main()

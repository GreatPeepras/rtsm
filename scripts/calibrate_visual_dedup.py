"""Calibrate (tau, R_max) for visual+spatial composite dedup.

Reads the same FAISS sidecar as prototype_gate_2_5.py.

Three reports:
  1. Known Mode B suspect groups (from handoff_2026-06-01.md) -- pairwise
     cosine + distance. Sets the LOWER bound: tau must be <= these
     cosines, R_max must be >= these distances.
  2. Cross-label pairs above a high cosine threshold, sorted by
     distance. These are the confounders -- a spatial gate has to
     separate them. Sets the UPPER bound on R_max.
  3. Dry-run merge counts under various (tau, R_max) settings. Shows
     how many OIDs would collapse and into what.

Usage:
    docker exec rtsm-dev python3 /workspace/rtsm/calibrate_visual_dedup.py
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path

import numpy as np

SIDECAR_DIR = Path("/mnt/rtsm-data/model_store/faiss")
META_PATH = SIDECAR_DIR / "index.flatip.meta.json"
IDS_PATH = SIDECAR_DIR / "index.flatip.ids"
EMBS_PATH = SIDECAR_DIR / "index.flatip.embs.npy"

# Mode B clusters identified in handoff_2026-06-01.md by visual inspection.
# These are pairs/groups KNOWN to be the same physical object.
SUSPECT_GROUPS = [
    ("4-chair cluster (one physical chair)", [
        "25bf519d", "939fee67", "0943e0a2", "9b57be88",
    ]),
    ("underneath table (desk + window labels)", [
        "504b78fe", "82aebeff",
    ]),
    ("two-desk cluster (likely same physical desk)", [
        "d58c5a8f", "7ec9d8da",
    ]),
]


def load_sidecar():
    meta = json.loads(META_PATH.read_text())
    ids = [l for l in IDS_PATH.read_text().splitlines() if l.strip()]
    embs = np.load(EMBS_PATH)
    assert len(ids) == embs.shape[0] == len(meta)
    emb_by_oid = {oid: embs[i] for i, oid in enumerate(ids)}
    return meta, emb_by_oid


def resolve_prefix(prefix, meta):
    matches = [oid for oid in meta if oid.startswith(prefix)]
    if len(matches) == 1:
        return matches[0]
    return None


def cos(ea, eb):
    return float(np.dot(ea, eb))


def dist(xa, xb):
    return float(np.linalg.norm(np.asarray(xa) - np.asarray(xb)))


# ---------------- Report 1: known suspect groups ----------------
def report_suspect_groups(meta, emb_by_oid):
    print("=== Report 1: Known Mode B suspect groups ===")
    print("(These are pairs we WANT to merge. tau must be <= min(cos), R_max >= max(dist).)\n")

    min_cos_seen = 1.0
    max_dist_seen = 0.0

    for name, prefixes in SUSPECT_GROUPS:
        print(f"--- {name} ---")
        resolved = [(p, resolve_prefix(p, meta)) for p in prefixes]
        missing = [p for p, oid in resolved if oid is None]
        if missing:
            print(f"  WARNING: prefixes not found / ambiguous: {missing}")
        present = [(p, oid) for p, oid in resolved if oid is not None]
        if len(present) < 2:
            print("  (need at least 2 resolved OIDs for pairwise analysis)\n")
            continue

        for (pa, a), (pb, b) in combinations(present, 2):
            c = cos(emb_by_oid[a], emb_by_oid[b])
            d = dist(meta[a]["xyz"], meta[b]["xyz"])
            la = meta[a].get("label_primary", "?")
            lb = meta[b].get("label_primary", "?")
            print(f"  {pa} ({la!r:14s}) <-> {pb} ({lb!r:14s}): "
                  f"cos={c:.4f}  dist={d:.3f}m")
            min_cos_seen = min(min_cos_seen, c)
            max_dist_seen = max(max_dist_seen, d)
        print()

    print(f"  >> Lower bound: tau <= {min_cos_seen:.4f}, "
          f"R_max >= {max_dist_seen:.3f}m\n")
    return min_cos_seen, max_dist_seen


# ---------------- Report 2: cross-label confounders ----------------
def report_cross_label_confounders(meta, emb_by_oid, sim_thresh=0.92,
                                    top_n=30):
    print(f"=== Report 2: Cross-label pairs with cos >= {sim_thresh} ===")
    print("(These are pairs that visual-only dedup would falsely merge. "
          "Sorted by distance ascending -- the closest are the dangerous "
          "ones; spatial gate must exclude them.)\n")

    oids = list(meta.keys())
    rows = []
    for i, a in enumerate(oids):
        la = meta[a].get("label_primary")
        for b in oids[i + 1:]:
            lb = meta[b].get("label_primary")
            if la == lb:
                continue
            c = cos(emb_by_oid[a], emb_by_oid[b])
            if c < sim_thresh:
                continue
            d = dist(meta[a]["xyz"], meta[b]["xyz"])
            rows.append((c, d, a, la, b, lb))

    rows.sort(key=lambda r: r[1])  # ascending by distance
    print(f"  total cross-label pairs above sim={sim_thresh}: {len(rows)}\n")

    if not rows:
        print("  (none)")
        return None

    print(f"  closest {min(top_n, len(rows))} (sorted by distance):")
    for c, d, a, la, b, lb in rows[:top_n]:
        print(f"    cos={c:.4f}  dist={d:.3f}m  "
              f"{a[:8]} ({la!r}) <-> {b[:8]} ({lb!r})")
    if len(rows) > top_n:
        print(f"    ... ({len(rows) - top_n} more)")
    print()

    closest_confounder_dist = rows[0][1]
    print(f"  >> Closest cross-label confounder is {closest_confounder_dist:.3f}m apart.")
    print(f"     For safety, R_max < {closest_confounder_dist:.3f}m, OR the system")
    print(f"     accepts that this pair would merge under the chosen R_max.\n")
    return closest_confounder_dist


# ---------------- Report 3: dry-run merge sweep ----------------
def dry_run_merges(meta, emb_by_oid, tau_visual, R_max):
    """Build union-find graph, return (n_edges, components_with_multi_members)."""
    oids = list(meta.keys())
    parent = {oid: oid for oid in oids}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(x, y):
        rx, ry = find(x), find(y)
        if rx != ry:
            parent[rx] = ry

    edges = 0
    for i, a in enumerate(oids):
        for b in oids[i + 1:]:
            c = cos(emb_by_oid[a], emb_by_oid[b])
            if c < tau_visual:
                continue
            d = dist(meta[a]["xyz"], meta[b]["xyz"])
            if d > R_max:
                continue
            union(a, b)
            edges += 1

    groups = defaultdict(list)
    for oid in oids:
        groups[find(oid)].append(oid)
    multi = {root: members for root, members in groups.items() if len(members) > 1}
    return edges, multi


def report_dry_run_sweep(meta, emb_by_oid):
    print("=== Report 3: Dry-run merge sweep ===")
    print("(How many OIDs would collapse under various thresholds.)\n")

    configs = [
        (0.90, 1.5), (0.90, 2.0), (0.90, 3.0),
        (0.92, 1.0), (0.92, 1.5), (0.92, 2.0), (0.92, 3.0),
        (0.95, 1.0), (0.95, 1.5), (0.95, 2.0),
        (0.97, 1.0), (0.97, 2.0),
    ]

    n_total = len(meta)
    print(f"  Starting count: {n_total} OIDs\n")
    print(f"  {'tau':>6} {'R_max':>7}   {'edges':>6} {'groups':>7} "
          f"{'absorbed':>9}   {'net':>5}   largest 3 groups (labels)")
    print(f"  {'-'*6} {'-'*7}   {'-'*6} {'-'*7} {'-'*9}   {'-'*5}   {'-'*40}")

    for tau, R in configs:
        edges, multi = dry_run_merges(meta, emb_by_oid, tau, R)
        absorbed = sum(len(m) for m in multi.values())
        net = n_total - absorbed + len(multi)
        # Top 3 groups by size
        top_groups = sorted(multi.values(), key=lambda m: -len(m))[:3]
        top_strs = []
        for members in top_groups:
            labels = [meta[m].get("label_primary", "?") for m in members]
            top = Counter(labels).most_common(2)
            label_summary = ",".join(f"{l}x{c}" for l, c in top)
            top_strs.append(f"[{len(members)}: {label_summary}]")
        top_repr = " ".join(top_strs) if top_strs else "(none)"
        print(f"  {tau:>6.2f} {R:>6.1f}m   {edges:>6} {len(multi):>7} "
              f"{absorbed:>9}   {net:>5}   {top_repr}")
    print()


# ---------------- Main ----------------
def main():
    meta, emb_by_oid = load_sidecar()
    print(f"Sidecar: {len(meta)} objects, embeddings L2-normalized\n")
    print("=" * 70 + "\n")

    report_suspect_groups(meta, emb_by_oid)
    print("=" * 70 + "\n")
    report_cross_label_confounders(meta, emb_by_oid, sim_thresh=0.92)
    print("=" * 70 + "\n")
    report_dry_run_sweep(meta, emb_by_oid)


if __name__ == "__main__":
    main()

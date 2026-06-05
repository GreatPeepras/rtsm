#!/usr/bin/env python3
"""
promote_furniture_2026-06-05.py

Bulk-promote furniture objects from `movable` to `static` (90d TTL)
before flipping eviction's dry_run off.

Background: Phase B.3 dry-run observation on 2026-06-05 revealed that
fixed-fixture furniture (door, drawer, cabinet, bench, heater, mattress,
rug) defaulted to `movable` (3d, bumped to 7d) on spawn. Without
explicit promotion, eviction-armed-live would age them out within a
week of no observation. This script promotes them to `static` so
they're protected by the 90d TTL.

IDEMPOTENT: re-running is safe; objects already at target class are
skipped. Default is dry-run; pass `--apply` to actually PATCH.

Usage:
    python3 promote_furniture_2026-06-05.py                      # dry run
    python3 promote_furniture_2026-06-05.py --apply              # commit
    python3 promote_furniture_2026-06-05.py --url http://192.168.0.53:8002

Excludes fragmented-cluster labels (mirror, television, light switch,
computer, night light) -- those belong to task #2's merge pass first,
then single-OID promotion after.
"""
import argparse
import sys
import requests

# ---------------------------------------------------------------------------
# Scope -- edit this dict to expand. Labels matched against display_label
# (label_user > label_primary), normalized to lowercase.
# ---------------------------------------------------------------------------
PROMOTIONS = {
    "door":     "static",
    "drawer":   "static",
    "cabinet":  "static",
    "bench":    "static",
    "heater":   "static",
    "mattress": "static",
    "rug":      "static",
}

# Skip these for now: they're in the merge-pass scope (task #2) because
# multiple OIDs share the same physical fixture. Promote them after merge.
SKIP_FRAGMENTED = {
    "mirror",
    "television",
    "light switch",
    "computer",
    "night light",
}


def fetch_all_objects(base_url: str) -> list:
    """Page through /objects?pose_state=any and return everything."""
    objs = []
    offset = 0
    limit = 500
    while True:
        r = requests.get(
            f"{base_url}/objects",
            params={"pose_state": "any", "limit": limit, "offset": offset},
            timeout=10,
        )
        r.raise_for_status()
        data = r.json()
        page = data.get("objects", [])
        objs.extend(page)
        if len(page) < limit:
            break
        offset += limit
    return objs


def display_label(obj: dict) -> str:
    """Mirror server's display_label gating, lowercased."""
    lu = obj.get("label_user")
    if lu:
        return lu.strip().lower()
    lp = obj.get("label_primary") or obj.get("display_label") or ""
    return lp.strip().lower()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n", 1)[0])
    ap.add_argument("--url", default="http://localhost:8002",
                    help="RTSM base URL (default: http://localhost:8002)")
    ap.add_argument("--apply", action="store_true",
                    help="Actually PATCH (default: dry-run preview only)")
    args = ap.parse_args()

    base = args.url.rstrip("/")
    print(f"[+] Fetching objects from {base}/objects?pose_state=any ...")
    try:
        objs = fetch_all_objects(base)
    except requests.RequestException as e:
        print(f"[!] Fetch failed: {e}", file=sys.stderr)
        return 2
    print(f"[+] {len(objs)} total objects in WM.\n")

    # Bucket
    targets = []
    already = []
    fragmented = []
    for o in objs:
        lab = display_label(o)
        if lab in SKIP_FRAGMENTED:
            fragmented.append((o.get("id"), lab, o.get("movability_class")))
            continue
        if lab not in PROMOTIONS:
            continue
        current = o.get("movability_class")
        target = PROMOTIONS[lab]
        if current == target:
            already.append((o.get("id"), lab, current))
            continue
        targets.append((o.get("id"), lab, current, target))

    # Preview
    print(f"[+] {len(targets)} objects to promote:")
    for oid, lab, current, target in targets:
        oid_short = (oid or "?")[:16]
        print(f"    {oid_short}  {lab:<13} {current or 'None':<12} -> {target}")
    print()
    print(f"[+] {len(already)} already at target (idempotent skip).")
    if fragmented:
        print(f"[+] {len(fragmented)} fragmented-cluster (deferred to merge pass):")
        for oid, lab, current in fragmented:
            oid_short = (oid or "?")[:16]
            print(f"    {oid_short}  {lab:<13} {current or 'None'}")

    if not args.apply:
        print("\n[ ] DRY RUN. Re-run with --apply to commit.")
        return 0

    if not targets:
        print("\n[+] Nothing to apply.")
        return 0

    # Apply
    print(f"\n[+] Applying {len(targets)} PATCHes ...")
    ok = 0
    fail = []
    for oid, lab, current, target in targets:
        oid_short = (oid or "?")[:16]
        try:
            r = requests.patch(
                f"{base}/objects/{oid}",
                json={"movability_class": target},
                timeout=5,
            )
            r.raise_for_status()
            ok += 1
            print(f"    [OK]   {oid_short}  {lab:<13} -> {target}")
        except requests.RequestException as e:
            fail.append((oid, lab, str(e)))
            print(f"    [FAIL] {oid_short}  {lab:<13} {e}")

    print(f"\n[+] Done. {ok}/{len(targets)} succeeded.")
    if fail:
        print(f"[!] {len(fail)} failures.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

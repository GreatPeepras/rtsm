#!/usr/bin/env python3
"""
auto_merge_2026-06-05.py

Apply conservative auto-merge to /objects/suggest_merges output.

Rule derivation: the merge_review session on 2026-06-05 produced 45
"yes" decisions and 38 "no" decisions. Every "confirmed different"
case shared at least one of:
  - label_user set on either side, OR
  - distance > 0.05m, OR
  - hits > 2 on either side (established observation history)

Conversely, the "easy yes" pattern was unambiguous:
  - Both label_user is None
  - Both hits == 2 (transient spawn pair, no observation history)
  - Neither has reference_image (no canonical photo at risk)
  - distance < 0.05m (basically same physical position)
  - cosine > 0.99 (very similar appearance)

If all five hold, auto-merge. Otherwise, defer to manual review.

Iterative: refetches /objects/suggest_merges after each merge because
the winner's emb_mean is a hits-weighted average and shifts on merge,
which can either consolidate or evaporate later pairs.

Usage:
    python3 auto_merge_2026-06-05.py                       # dry run (preview)
    python3 auto_merge_2026-06-05.py --apply               # commit
    python3 auto_merge_2026-06-05.py --apply --max 20      # cap merges per run
    python3 auto_merge_2026-06-05.py --apply --dist 0.08   # looser distance

Run this BEFORE merge_review_2026-06-05.py — it clears the easy yeses
so manual review only sees the borderline cases.
"""
import argparse
import datetime as dt
import sys
import requests


# Tier-1 auto-merge gate. Edit these only after reviewing the patterns
# from the previous session log.
AUTO_MERGE_RULES = {
    "max_distance_m": 0.05,
    "min_cosine": 0.99,
    "max_hits_per_side": 2,
    "require_no_label_user": True,
    "require_no_reference": True,
}


def fetch_candidates(base, cos=0.95, dist=1.0, limit=500):
    r = requests.post(
        f"{base}/objects/suggest_merges",
        json={
            "cos_threshold": cos,
            "dist_threshold_m": dist,
            "require_same_label": False,
            "limit": limit,
            "include_unconfirmed": False,
        },
        timeout=15,
    )
    r.raise_for_status()
    return r.json()


def is_auto_eligible(c, rules):
    if c["cosine"] < rules["min_cosine"]:
        return False
    if c["distance_m"] > rules["max_distance_m"]:
        return False
    if c["a_hits"] > rules["max_hits_per_side"]:
        return False
    if c["b_hits"] > rules["max_hits_per_side"]:
        return False
    if rules["require_no_label_user"]:
        if c["a_label_user"] is not None or c["b_label_user"] is not None:
            return False
    if rules["require_no_reference"]:
        if c["a_has_reference"] or c["b_has_reference"]:
            return False
    return True


def post_merge(base, winner, loser):
    r = requests.post(
        f"{base}/objects/merge",
        json={"winner_oid": winner, "loser_oid": loser, "dry_run": False},
        timeout=60,
    )
    return r.status_code, r.json()


def fmt_labels(c):
    al = c.get("a_display_label") or c.get("a_label_primary") or "?"
    bl = c.get("b_display_label") or c.get("b_label_primary") or "?"
    return f"{al!r} <-> {bl!r}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default="http://localhost:8002")
    ap.add_argument("--apply", action="store_true",
                    help="Actually merge. Default is dry-run preview.")
    ap.add_argument("--max", type=int, default=None,
                    help="Cap the number of merges per run (safety).")
    ap.add_argument("--dist", type=float, default=None,
                    help=f"Override max_distance_m "
                         f"(default {AUTO_MERGE_RULES['max_distance_m']})")
    ap.add_argument("--cos", type=float, default=None,
                    help=f"Override min_cosine "
                         f"(default {AUTO_MERGE_RULES['min_cosine']})")
    ap.add_argument("--max-hits", type=int, default=None, dest="max_hits",
                    help=f"Override max_hits_per_side "
                         f"(default {AUTO_MERGE_RULES['max_hits_per_side']})")
    args = ap.parse_args()

    base = args.url.rstrip("/")
    rules = dict(AUTO_MERGE_RULES)
    if args.dist is not None:
        rules["max_distance_m"] = args.dist
    if args.cos is not None:
        rules["min_cosine"] = args.cos
    if args.max_hits is not None:
        rules["max_hits_per_side"] = args.max_hits

    ts = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log_path = f"auto_merge_log_{ts}.tsv"

    print(f"[+] Server: {base}")
    print(f"[+] Rules:  {rules}")
    print(f"[+] Mode:   {'APPLY' if args.apply else 'DRY-RUN'}")
    if args.max is not None:
        print(f"[+] Cap:    {args.max} merges max")
    if args.apply:
        print(f"[+] Log:    {log_path}")
    print()

    if not args.apply:
        # Single-pass preview
        try:
            data = fetch_candidates(base)
        except requests.RequestException as e:
            print(f"[!] Fetch failed: {e}", file=sys.stderr)
            return 2
        cands = data["candidates"]
        eligible = [c for c in cands if is_auto_eligible(c, rules)]
        print(f"[+] {len(cands)} total candidates above suggest_merges gate.")
        print(f"[+] {len(eligible)} auto-eligible under current rules:")
        for c in eligible:
            print(f"    cos={c['cosine']:.4f}  dist={c['distance_m']:.4f}m  "
                  f"{c['a_oid'][:8]} <-> {c['b_oid'][:8]}  {fmt_labels(c)}")
        print()
        print(f"[ ] DRY-RUN. Re-run with --apply to commit.")
        print(f"[ ] {len(cands) - len(eligible)} candidates would remain "
              f"for manual review.")
        return 0

    # Apply mode: iterative refetch loop
    decisions = []
    merged = 0
    iterations = 0

    def write_log():
        with open(log_path, "w") as f:
            f.write("ts\twinner_oid\tloser_oid\tcosine\tdistance_m\ta_label\tb_label\n")
            for row in decisions:
                f.write("\t".join(str(x) for x in row) + "\n")

    while True:
        iterations += 1
        if args.max is not None and merged >= args.max:
            print(f"\n[+] Hit cap of {args.max} merges. Stopping.")
            break
        try:
            data = fetch_candidates(base)
        except requests.RequestException as e:
            print(f"[!] Fetch failed: {e}", file=sys.stderr)
            write_log()
            return 2
        cands = data["candidates"]
        target = None
        for c in cands:
            if is_auto_eligible(c, rules):
                target = c
                break
        if target is None:
            print(f"\n[+] No more auto-eligible pairs.")
            print(f"[+] {len(cands)} candidates remain for manual review.")
            break
        winner = target["suggested_winner_oid"]
        loser = (target["b_oid"]
                 if winner == target["a_oid"] else target["a_oid"])
        try:
            code, body = post_merge(base, winner, loser)
        except requests.RequestException as e:
            print(f"[!] Merge failed: {e}")
            write_log()
            return 2
        if code >= 400 or "error" in body:
            print(f"[!] Merge rejected (status={code}): {body}")
            write_log()
            return 2
        decisions.append((
            dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
            winner, loser,
            target["cosine"], target["distance_m"],
            target.get("a_display_label") or target.get("a_label_primary") or "",
            target.get("b_display_label") or target.get("b_label_primary") or "",
        ))
        merged += 1
        print(f"  [{merged:3d}] {winner[:8]} <- {loser[:8]}  "
              f"cos={target['cosine']:.4f}  dist={target['distance_m']:.4f}m  "
              f"{fmt_labels(target)}")
        if merged % 10 == 0:
            write_log()

    write_log()
    print(f"\n[+] Done. {merged} merges applied over {iterations} iterations.")
    print(f"[+] Log: {log_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
merge_review_2026-06-05.py

Interactive Mode B merge review tool. Walks /objects/suggest_merges
candidate list one pair at a time, prints metadata + snapshot URLs,
and POSTs /objects/merge on confirmation. Refreshes the candidate
list after each successful merge.

Skipped pairs are remembered for the duration of the process so you
don't see them again until you re-run. Decisions are also written to
./merge_review_log_<timestamp>.tsv for audit.

Usage:
    python3 merge_review_2026-06-05.py
    python3 merge_review_2026-06-05.py --url http://192.168.0.53:8002
    python3 merge_review_2026-06-05.py --cos 0.95 --dist 1.0

Keys during review:
    y         merge (use suggested winner)
    sy        swap winner, then merge (the other side wins)
    n         skip this pair (won't see it again until restart)
    d         dry-run preview (shows merge stats, no mutation)
    p         print full pair JSON
    i <oid>   print snapshot index URLs 0-5 for the OID (a or b allowed)
    q         quit
    ?         help

All applied merges write a server-side audit JSON under merge_log_dir.
"""
import argparse
import datetime as dt
import json
import sys
import requests


def fetch_candidates(base, cos, dist, limit=500, require_same_label=False):
    r = requests.post(
        f"{base}/objects/suggest_merges",
        json={
            "cos_threshold": cos,
            "dist_threshold_m": dist,
            "require_same_label": require_same_label,
            "limit": limit,
            "include_unconfirmed": False,
        },
        timeout=15,
    )
    r.raise_for_status()
    return r.json()


def post_merge(base, winner, loser, dry_run=False):
    r = requests.post(
        f"{base}/objects/merge",
        json={"winner_oid": winner, "loser_oid": loser, "dry_run": dry_run},
        timeout=60,
    )
    return r.status_code, r.json()


def pair_key(c):
    return tuple(sorted([c["a_oid"], c["b_oid"]]))


def fmt_xyz(xyz):
    if xyz is None or len(xyz) < 3:
        return "?"
    return f"({xyz[0]:.2f},{xyz[1]:.2f},{xyz[2]:.2f})"


def render_pair(c, base):
    winner = c["suggested_winner_oid"]
    winner_side = "A" if winner == c["a_oid"] else "B"
    out = []
    out.append("=" * 72)
    out.append(
        f"cos={c['cosine']}  dist={c['distance_m']}m  "
        f"same_label={c['same_display_label']}  suggested winner: {winner_side}"
    )
    out.append("")
    for side, prefix in (("A", "a"), ("B", "b")):
        oid = c[f"{prefix}_oid"]
        mark = " <-- winner" if oid == winner else ""
        out.append(f"{side}: {oid[:16]}{mark}")
        out.append(
            f"   label_user={c[f'{prefix}_label_user']!r}  "
            f"label_primary={c[f'{prefix}_label_primary']!r}"
        )
        out.append(
            f"   hits={c[f'{prefix}_hits']}  "
            f"ref_image={c[f'{prefix}_has_reference']}  "
            f"xyz={fmt_xyz(c.get(f'{prefix}_xyz'))}"
        )
        out.append(f"   snapshot: {base}/objects/{oid}/snapshots/0/image")
        out.append("")
    out.append("=" * 72)
    return "\n".join(out)


HELP = """
Commands:
  y        merge (use suggested winner)
  sy       swap winner, then merge (the other side wins)
  n        skip this pair (won't appear again this session)
  d        dry-run preview (shows merge stats, no mutation)
  p        print full pair JSON
  i a      print snapshot index URLs 0-5 for object A
  i b      print snapshot index URLs 0-5 for object B
  q        quit
  ?        this help
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default="http://localhost:8002")
    ap.add_argument("--cos", type=float, default=0.95)
    ap.add_argument("--dist", type=float, default=1.0)
    ap.add_argument("--limit", type=int, default=500)
    args = ap.parse_args()

    base = args.url.rstrip("/")
    ts = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log_path = f"merge_review_log_{ts}.tsv"

    print(f"[+] Log: {log_path}")
    print(f"[+] Server: {base}")
    print(f"[+] Gate: cos>={args.cos}, dist<={args.dist}m")
    print(HELP)

    decisions = []
    seen = set()
    merged = 0
    skipped = 0

    def write_log():
        with open(log_path, "w") as f:
            f.write("ts\taction\twinner_oid\tloser_oid\tcosine\tdistance_m\tnote\n")
            for row in decisions:
                f.write("\t".join(str(x) for x in row) + "\n")

    def record(action, c, winner=None, loser=None, note=""):
        decisions.append((
            dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
            action,
            winner or "",
            loser or "",
            c["cosine"],
            c["distance_m"],
            note,
        ))
        write_log()

    while True:
        try:
            data = fetch_candidates(base, args.cos, args.dist, args.limit)
        except requests.RequestException as e:
            print(f"[!] Fetch failed: {e}", file=sys.stderr)
            return 2

        cands = data["candidates"]
        if not cands:
            print(f"\n[+] No more candidates above gate.")
            break

        # Find next unseen
        next_c = None
        for c in cands:
            if pair_key(c) not in seen:
                next_c = c
                break

        if next_c is None:
            print(
                f"\n[+] All {len(cands)} remaining candidates were skipped "
                f"this session."
            )
            ans = input("Reset skip-set and review again? [y/N]: ").strip().lower()
            if ans == "y":
                seen.clear()
                continue
            else:
                break

        print(render_pair(next_c, base))
        unseen_count = sum(1 for c in cands if pair_key(c) not in seen)
        print(
            f"({merged} merged, {skipped} skipped, {unseen_count} unseen "
            f"of {len(cands)} total above gate)"
        )

        try:
            action = input("> ").strip().lower()
        except (KeyboardInterrupt, EOFError):
            print("\n[+] Interrupted.")
            break

        if action in ("?", "h", "help"):
            print(HELP)
            continue
        if action == "q":
            break
        if action == "p":
            print(json.dumps(next_c, indent=2))
            continue
        if action.startswith("i "):
            which = action.split(None, 1)[1].strip()
            if which not in ("a", "b"):
                print("[!] Use 'i a' or 'i b'")
                continue
            oid = next_c[f"{which}_oid"]
            for idx in range(6):
                print(f"  [{idx}] {base}/objects/{oid}/snapshots/{idx}/image")
            continue
        if action == "n":
            seen.add(pair_key(next_c))
            skipped += 1
            record("skip", next_c)
            continue
        if action == "d":
            try:
                code, body = post_merge(
                    base,
                    next_c["suggested_winner_oid"],
                    (next_c["b_oid"] if next_c["suggested_winner_oid"] == next_c["a_oid"]
                     else next_c["a_oid"]),
                    dry_run=True,
                )
                stats = body.get("stats", {})
                print(f"  status={code}")
                print(f"  hits: {stats.get('hits_before')} -> {stats.get('hits_after')}")
                print(f"  gallery: {stats.get('emb_gallery_before')} -> {stats.get('emb_gallery_after')}")
                print(f"  view_bins: {stats.get('view_bins_before')} -> {stats.get('view_bins_after')}")
                print(f"  inherited_label_user: {stats.get('label_user_inherited_from_loser')}")
            except requests.RequestException as e:
                print(f"[!] Dry-run failed: {e}")
            continue
        if action in ("y", "sy"):
            if action == "y":
                winner = next_c["suggested_winner_oid"]
            else:
                winner = (next_c["b_oid"]
                          if next_c["suggested_winner_oid"] == next_c["a_oid"]
                          else next_c["a_oid"])
            loser = (next_c["b_oid"] if winner == next_c["a_oid"]
                     else next_c["a_oid"])
            try:
                code, body = post_merge(base, winner, loser, dry_run=False)
            except requests.RequestException as e:
                print(f"[!] Merge failed: {e}")
                record("error", next_c, note=str(e))
                seen.add(pair_key(next_c))
                continue
            if code >= 400 or "error" in body:
                print(f"[!] Merge rejected (status={code}): {body}")
                record("error", next_c, winner=winner, loser=loser,
                       note=str(body)[:200])
                seen.add(pair_key(next_c))
                continue
            stats = body.get("stats", {})
            print(
                f"  [OK] merged {winner[:8]} <- {loser[:8]}  "
                f"hits {stats.get('hits_before')} -> {stats.get('hits_after')}"
            )
            merged += 1
            record("merge", next_c, winner=winner, loser=loser)
            # Don't add to seen — loser is gone. Refetch will not return it.
            continue

        print("[!] Unrecognized. Type ? for help.")

    write_log()
    print()
    print(f"[+] Session done. Merged: {merged}, Skipped: {skipped}")
    print(f"[+] Log: {log_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

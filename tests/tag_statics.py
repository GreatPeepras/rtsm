#!/usr/bin/env python3
"""tag_statics.py — interactive CLI for the manual static pass.

Per movability_assignment_design.md (accepted 2026-05-28), the
landmark-eligible classes (`static`, `permanent`) are assigned by a human,
once, after the first recording burst(s) for an environment. This tool is
that human pass: walks you through confirmed WM objects and lets you mark
which ones are static, permanent, or semi_static via PATCH /objects/{oid}.

Common workflow:

    # First pass: dry-run, see candidates
    python3 scripts/tag_statics.py --dry-run --sort label

    # Filter to a likely-static label class and tag interactively
    python3 scripts/tag_statics.py --label couch
    python3 scripts/tag_statics.py --label table

    # Final sweep across everything not yet tagged
    python3 scripts/tag_statics.py

Identification when no snapshots are available (rehydrated objects):
look at label_primary + xyz_world + stability. xyz tells you where in the
apartment the object is; high stability + hits is the trust signal.

Hidden by default: objects already marked permanent/static (idempotent
re-runs don't pester you about them). Use --include-tagged to see them.
"""
from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Dict, List, Optional

import requests


DEFAULT_URL = "http://localhost:8002"
HTTP_TIMEOUT_S = 10.0

# Auto-assignable classes (matches working_memory._AUTO_DEFAULT_MOVABILITY_OK).
# Anything in this set is NOT a manual-pass target.
_AUTO_CLASSES = frozenset({"semi_static", "movable", "roaming", "ephemeral"})
_MANUAL_CLASSES = frozenset({"permanent", "static"})


def list_candidates(
    base_url: str,
    *,
    label_filter: Optional[str] = None,
    include_tagged: bool = False,
) -> List[Dict[str, Any]]:
    """Fetch confirmed objects from RTSM, apply filters, return as list of dicts."""
    r = requests.get(
        f"{base_url}/objects",
        params={"confirmed_only": "true", "pose_state": "any", "limit": 500},
        timeout=HTTP_TIMEOUT_S,
    )
    r.raise_for_status()
    objs = r.json().get("objects", [])

    if not include_tagged:
        # Hide already-tagged objects (manual classes only); leave None and
        # auto-assigned classes visible since those are the actual targets.
        objs = [o for o in objs if o.get("movability_class") not in _MANUAL_CLASSES]

    if label_filter:
        lf = label_filter.lower()
        def _match(o):
            for k in ("display_label", "label_primary", "label_user"):
                v = o.get(k)
                if v and v.lower() == lf:
                    return True
            return False
        objs = [o for o in objs if _match(o)]

    return objs


def patch_movability(base_url: str, oid: str, value: Optional[str]) -> Dict[str, Any]:
    """PATCH /objects/{oid} with a new movability_class. Returns server response."""
    r = requests.patch(
        f"{base_url}/objects/{oid}",
        json={"movability_class": value},
        timeout=HTTP_TIMEOUT_S,
    )
    r.raise_for_status()
    return r.json()


def _format_row(o: Dict[str, Any], idx: int, total: int) -> str:
    """One-line summary of an object for the prompt."""
    oid = o["id"]
    short = oid[:8]
    label = o.get("display_label") or o.get("label_primary") or "(unlabeled)"
    xyz = o.get("xyz_world")
    xyz_str = (
        f"[{xyz[0]:+.2f},{xyz[1]:+.2f},{xyz[2]:+.2f}]"
        if isinstance(xyz, (list, tuple)) and len(xyz) == 3
        else "(no xyz)"
    )
    cur = o.get("movability_class")
    stab = float(o.get("stability", 0.0) or 0.0)
    hits = int(o.get("hits", 0) or 0)
    age = o.get("last_seen_age_s")
    age_str = f"{age:.0f}s ago" if isinstance(age, (int, float)) else "?"
    has_ref = "ref" if o.get("reference_image_path") else ""
    parts = [
        f"[{idx}/{total}]",
        short,
        f"label={label!r}",
        f"xyz={xyz_str}",
        f"stab={stab:.2f}",
        f"hits={hits}",
        f"seen={age_str}",
        f"class={cur!r}",
    ]
    if has_ref:
        parts.append(has_ref)
    return "  ".join(parts)


def _print_legend() -> None:
    print(
        "  p = permanent (wall, doorframe, built-in shelves -- NEVER moves)\n"
        "  s = static    (couch, fridge, desk -- moves rarely)\n"
        "  m = semi_static (lamp, basket -- moves occasionally)\n"
        "  u = revert to movable (undo a previous decision in this run)\n"
        "  Enter/n = next, no change\n"
        "  q = quit (preserves changes already applied)\n"
        "  ? = show this legend"
    )


def _sort_objects(objs: List[Dict[str, Any]], sort_key: str) -> List[Dict[str, Any]]:
    if sort_key == "stability":
        return sorted(objs, key=lambda o: float(o.get("stability", 0.0) or 0.0), reverse=True)
    elif sort_key == "last_seen":
        return sorted(objs, key=lambda o: float(o.get("last_seen_mono", 0.0) or 0.0), reverse=True)
    elif sort_key == "label":
        return sorted(objs, key=lambda o: (o.get("display_label") or o.get("label_primary") or "ZZZ").lower())
    return objs


def interactive_loop(
    base_url: str,
    candidates: List[Dict[str, Any]],
) -> Dict[str, int]:
    """Walk through candidates one at a time. Returns a tally dict."""
    tally = {"permanent": 0, "static": 0, "semi_static": 0, "movable": 0, "skip": 0, "error": 0}
    total = len(candidates)
    print(f"\n{total} candidate(s). Commands:")
    _print_legend()
    print()

    for i, o in enumerate(candidates, 1):
        print(_format_row(o, i, total))
        while True:
            try:
                choice = input("  -> [p/s/m/u/Enter/q/?]: ").strip().lower()
            except (EOFError, KeyboardInterrupt):
                print("\n  (interrupted)")
                return tally
            if choice in ("", "n"):
                tally["skip"] += 1
                break
            elif choice == "q":
                print("  quitting; preserving changes applied so far")
                return tally
            elif choice == "?":
                _print_legend()
                continue
            mapping = {"p": "permanent", "s": "static", "m": "semi_static", "u": "movable"}
            if choice in mapping:
                new_cls = mapping[choice]
                try:
                    patch_movability(base_url, o["id"], new_cls)
                    tally[new_cls] += 1
                    print(f"  -> PATCHed {o['id'][:8]} movability_class={new_cls}")
                except requests.HTTPError as e:
                    tally["error"] += 1
                    print(f"  -> PATCH failed: HTTP {e.response.status_code}: {e.response.text[:200]}")
                except Exception as e:
                    tally["error"] += 1
                    print(f"  -> PATCH failed: {e}")
                break
            print("  (unknown command; try p/s/m/u, Enter to skip, q to quit, ? for help)")

    return tally


def _summarize(tally: Dict[str, int]) -> None:
    print("\n--- Summary ---")
    total_changes = sum(v for k, v in tally.items() if k not in ("skip", "error"))
    for k in ("permanent", "static", "semi_static", "movable", "skip", "error"):
        v = tally.get(k, 0)
        if v:
            print(f"  {k:12s}: {v}")
    print(f"  total PATCHes applied: {total_changes}")


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(
        description="Interactive CLI for marking objects static/permanent/semi_static.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    ap.add_argument("--url", default=DEFAULT_URL,
                    help=f"RTSM base URL (default: {DEFAULT_URL})")
    ap.add_argument("--label", default=None,
                    help="Filter to objects whose display/label_primary/label_user equals this (case-insensitive)")
    ap.add_argument("--include-tagged", action="store_true",
                    help="Include objects already marked permanent/static (default: hide)")
    ap.add_argument("--sort", default="stability",
                    choices=("stability", "last_seen", "label"),
                    help="Sort order for candidate list (default: stability)")
    ap.add_argument("--dry-run", action="store_true",
                    help="List candidates without prompting or patching")
    ap.add_argument("--json", action="store_true",
                    help="Output candidates as JSON, no interactive prompts")
    args = ap.parse_args(argv)

    try:
        candidates = list_candidates(
            args.url,
            label_filter=args.label,
            include_tagged=args.include_tagged,
        )
    except Exception as e:
        print(f"FAIL: could not fetch /objects from {args.url}: {e}", file=sys.stderr)
        return 2

    if not candidates:
        msg = f"No candidates"
        if args.label:
            msg += f" matching label={args.label!r}"
        if not args.include_tagged:
            msg += " (already-tagged objects hidden; --include-tagged to see them)"
        print(msg)
        return 0

    candidates = _sort_objects(candidates, args.sort)

    if args.json:
        slim = [
            {
                "id": o["id"],
                "display_label": o.get("display_label") or o.get("label_primary"),
                "movability_class": o.get("movability_class"),
                "xyz_world": o.get("xyz_world"),
                "stability": o.get("stability"),
                "hits": o.get("hits"),
                "last_seen_age_s": o.get("last_seen_age_s"),
                "has_reference_image": bool(o.get("reference_image_path")),
            }
            for o in candidates
        ]
        json.dump(slim, sys.stdout, indent=2)
        sys.stdout.write("\n")
        return 0

    if args.dry_run:
        total = len(candidates)
        for i, o in enumerate(candidates, 1):
            print(_format_row(o, i, total))
        print(f"\n--- dry run: {total} candidate(s); no PATCHes applied ---")
        return 0

    tally = interactive_loop(args.url, candidates)
    _summarize(tally)
    return 0


if __name__ == "__main__":
    sys.exit(main())

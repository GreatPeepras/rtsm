#!/usr/bin/env python3
"""
deploy_persist_iff_durable_2026-06-29.py   (RTSM / .53)

Gates rehydrate_from_faiss() so only DURABLE objects are reloaded into working
memory on restart. Durable = named (label_user set) OR static/semi_static/
permanent landmark. Unnamed, non-landmark objects become session-volatile and
evaporate on restart instead of accumulating across sessions.

This is the clean implementation of the 06-29 "Option B" persistence decision
and the "forget the unnamed objects" cleanup -- without a per-object delete.

Marker: PERSIST_IFF_DURABLE_2026-06-29

SAFETY: at the WM layer this only SKIPS loading; it does not delete. But the
FAISS store may be re-saved from WM after a skipped rehydrate, which would
prune the skipped objects from disk too. **Back up the FAISS sidecar before the
first restart** (see run notes printed at the end). Revert + restart reloads
everything IF FAISS has not yet been re-saved.

Usage:
    python3 deploy_persist_iff_durable_2026-06-29.py            # dryrun
    python3 deploy_persist_iff_durable_2026-06-29.py --apply
    python3 deploy_persist_iff_durable_2026-06-29.py --revert
    # optional: --path /abs/path/to/working_memory.py  (else auto-located under --root)
    #           --root ~/rtsm
"""
import argparse, ast, glob, os, shutil, sys, time

MARKER = "PERSIST_IFF_DURABLE_2026-06-29"

# ---- anchored edits: (old, new) ; revert swaps them ----
EDITS = [
    # 1) counts dict: add skipped_volatile
    (
        '            "skipped_dup": 0,\n',
        '            "skipped_dup": 0,\n'
        '            "skipped_volatile": 0,\n',
    ),
    # 2) the durability gate, right after the dup-skip block
    (
        "            if oid in self._map:\n"
        '                counts["skipped_dup"] += 1\n'
        "                continue\n",
        "            if oid in self._map:\n"
        '                counts["skipped_dup"] += 1\n'
        "                continue\n"
        "\n"
        f"            # {MARKER}: only rehydrate durable objects. Durable =\n"
        "            # named (label_user set) OR static/semi_static/permanent\n"
        "            # landmark. Unnamed non-landmark objects are volatile and\n"
        "            # are allowed to evaporate on restart.\n"
        "            _piid_lu = meta.get(\"label_user\")\n"
        "            _piid_mov = meta.get(\"movability_class\")\n"
        "            _piid_durable = bool(_piid_lu) or (\n"
        "                _piid_mov in (\"static\", \"semi_static\", \"permanent\")\n"
        "            )\n"
        "            if not _piid_durable:\n"
        '                counts["skipped_volatile"] += 1\n'
        "                continue\n",
    ),
    # 3) summary log line: surface the volatile count
    (
        '            f"dup={counts[\'skipped_dup\']}) | "\n',
        '            f"dup={counts[\'skipped_dup\']} "\n'
        '            f"volatile={counts[\'skipped_volatile\']}) | "\n',
    ),
]


def locate(root):
    hits = [p for p in glob.glob(os.path.join(os.path.expanduser(root), "**", "working_memory.py"),
                                 recursive=True) if "/node_modules/" not in p]
    return hits


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--revert", action="store_true")
    ap.add_argument("--path", default=None)
    ap.add_argument("--root", default="~/rtsm")
    args = ap.parse_args()
    if args.apply and args.revert:
        print("choose one of --apply / --revert", file=sys.stderr); sys.exit(2)

    path = args.path
    if not path:
        hits = locate(args.root)
        if len(hits) != 1:
            print(f"could not uniquely locate working_memory.py under {args.root} "
                  f"(found {len(hits)}). Pass --path.", file=sys.stderr)
            for h in hits:
                print("  ", h, file=sys.stderr)
            sys.exit(2)
        path = hits[0]
    print(f"target: {path}")

    with open(path) as f:
        src = f.read()
    applied = MARKER in src
    print(f"marker present: {applied}")

    pairs = [(b, a) for (a, b) in EDITS] if args.revert else list(EDITS)
    mode = "revert" if args.revert else "apply"

    if mode == "apply" and applied:
        print("already applied; nothing to do."); return
    if mode == "revert" and not applied:
        print("not applied; nothing to revert."); return

    new = src
    for old, repl in pairs:
        n = new.count(old)
        if n != 1:
            print(f"ANCHOR ERROR ({mode}): expected 1 match, found {n} for:\n---\n{old}\n---",
                  file=sys.stderr)
            print("Live file has drifted from expectations. Aborting (no write).", file=sys.stderr)
            sys.exit(3)
        new = new.replace(old, repl, 1)

    # AST validation before any write
    try:
        ast.parse(new)
    except SyntaxError as e:
        print(f"AST validation FAILED: {e}", file=sys.stderr); sys.exit(4)
    print("AST: OK")

    if not (args.apply or args.revert):
        print("\nDRYRUN -- no file written. Re-run with --apply (or --revert).")
        return

    bak = f"{path}.bak.{time.strftime('%Y%m%d-%H%M%S')}"
    shutil.copy2(path, bak)
    tmp = f"{path}.tmp"
    with open(tmp, "w") as f:
        f.write(new)
    with open(tmp) as f:
        ast.parse(f.read())
    os.replace(tmp, path)
    print(f"{mode.upper()}ED. backup -> {bak}")

    print("\nNEXT:")
    print("  1) BACK UP FAISS FIRST (skip-load may prune disk on next save):")
    print("       sudo cp -a /mnt/rtsm-data/model_store/faiss "
          "/mnt/rtsm-data/model_store/faiss.bak.$(date +%Y%m%d-%H%M%S)")
    print("  2) Restart the dev container:")
    print("       cd ~/rtsm/docker && docker compose restart rtsm-dev")
    print("  3) Verify the volatile drop in the logs + object count:")
    print("       docker compose logs --tail=20 rtsm-dev | grep -i rehydrate")
    print("       curl -s 'http://localhost:8002/objects?limit=1000&pose_state=any' "
          "| python3 -c 'import sys,json;d=json.load(sys.stdin);"
          "o=d if isinstance(d,list) else d.get(\"objects\",[]);"
          "print(len(o),\"objects;\",sum(1 for x in o if x.get(\"label_user\")),\"named\")'")
    print("  (If the change is bind-mounted it loads on restart; if the image bakes "
          "working_memory.py, rebuild instead: docker compose up -d --build rtsm-dev)")


if __name__ == "__main__":
    main()

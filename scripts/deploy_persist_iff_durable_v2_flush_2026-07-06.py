#!/usr/bin/env python3
"""
deploy_persist_iff_durable_v2_flush_2026-07-06.py   (RTSM / .53)

CORRECT-LAYER replacement for deploy_persist_iff_durable_2026-06-29.py.

The 06-29 script gated rehydrate_from_faiss() -- the WRONG layer. A partial
rehydrate desynced FAISS from ingest's association state and broke the ingest
queue (queue saturation). It was reverted.

This version gates at the FLUSH layer instead: collect_ready_for_upsert() is
the ONE ambient path that writes objects to FAISS (confirmed via grep:
pipeline._maybe_flush_vectors:879 periodic + run.py:563 shutdown, both call it;
force_flush_now is the SEPARATE naming path and is NOT gated). We add the
durability predicate to BOTH branches of collect_ready_for_upsert:

  durable = label_user set  OR  movability_class in
            (static, semi_static, permanent)

Result:
  - Unnamed non-landmark objects are NEVER written to FAISS -> volatile ->
    evaporate on the next reboot.
  - Named objects persist (gated-in here AND force-flushed on PATCH label_user).
  - rehydrate_from_faiss stays a DUMB full loader (untouched) -> ingest sees a
    complete, consistent WM+FAISS on boot -> NO saturation. Since the disk only
    ever holds durables, "load everything" == "load only named" by construction.

Clears the EXISTING unnamed fragments for free: with this gate live, the next
clean shutdown's run.py force_all collect->save rebuilds the sidecar from only
durable objects (and PATCH H's empty-index guard prevents a wipe). No per-object
delete, no merge.

Marker: PERSIST_IFF_DURABLE_FLUSH_2026-07-06  (expected count: 2)

  python3 deploy_persist_iff_durable_v2_flush_2026-07-06.py            # dryrun
  python3 deploy_persist_iff_durable_v2_flush_2026-07-06.py --apply
  python3 deploy_persist_iff_durable_v2_flush_2026-07-06.py --revert
  python3 deploy_persist_iff_durable_v2_flush_2026-07-06.py --check
  #   --path /abs/working_memory.py  (else auto-located under --root, default ~/rtsm)

SAFETY: before the first shutdown-save after apply, back up the sidecar:
    sudo cp -a /mnt/rtsm-data/model_store/faiss \
               /mnt/rtsm-data/model_store/faiss.bak.$(date +%Y%m%d-%H%M%S)
Revert + restart restores the ungated flush (named + unnamed both persist again).
"""
import argparse, ast, glob, os, py_compile, shutil, sys, tempfile

MARKER = "PERSIST_IFF_DURABLE_FLUSH_2026-07-06"

# ---- anchored edits: (old, new). revert swaps them. ----
EDITS = [
    # Branch 1 -- force_all bulk path
    (
        "            if force_all:\n"
        "                for o in self._map.values():\n"
        "                    if not o.confirmed or o.emb_mean is None:\n"
        "                        continue\n",
        "            if force_all:\n"
        "                for o in self._map.values():\n"
        "                    if not o.confirmed or o.emb_mean is None:\n"
        "                        continue\n"
        f"                    # {MARKER}: persist only durable\n"
        "                    # objects (named OR static/semi_static/permanent\n"
        "                    # landmark). Unnamed non-landmarks are session-\n"
        "                    # volatile -> never written to FAISS -> evaporate on\n"
        "                    # the next reboot. Gate is at FLUSH, NOT rehydrate\n"
        "                    # (rehydrate stays a dumb full loader; disk only ever\n"
        "                    # holds durables, so both agree by construction).\n"
        "                    if not (o.label_user or o.movability_class in\n"
        "                            (\"static\", \"semi_static\", \"permanent\")):\n"
        "                        continue\n",
    ),
    # Branch 2 -- periodic heap loop
    (
        "                o = self._map.get(oid)\n"
        "                if o is None or not o.confirmed:\n"
        "                    continue\n",
        "                o = self._map.get(oid)\n"
        "                if o is None or not o.confirmed:\n"
        "                    continue\n"
        f"                # {MARKER}: skip volatile (unnamed\n"
        "                # non-landmark) objects -- same durability predicate as\n"
        "                # the force_all branch. force_flush_now (naming path) is\n"
        "                # NOT gated, so naming still persists immediately.\n"
        "                if not (o.label_user or o.movability_class in\n"
        "                        (\"static\", \"semi_static\", \"permanent\")):\n"
        "                    continue\n",
    ),
]


def locate(root, explicit):
    if explicit:
        return [os.path.expanduser(explicit)]
    root = os.path.expanduser(root)
    return [
        p for p in glob.glob(os.path.join(root, "**", "working_memory.py"), recursive=True)
        if "/node_modules/" not in p and "/site-packages/" not in p
    ]


def validate_py(path):
    fd, cfile = tempfile.mkstemp(suffix=".pyc")
    os.close(fd)
    try:
        py_compile.compile(path, cfile=cfile, doraise=True)
    finally:
        try:
            os.remove(cfile)
        except OSError:
            pass


def atomic_write(path, text):
    d = os.path.dirname(path)
    fd, tmp = tempfile.mkstemp(dir=d, suffix=".tmp")
    try:
        with os.fdopen(fd, "w") as f:
            f.write(text)
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--revert", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--path", default=None)
    ap.add_argument("--root", default="~/rtsm")
    args = ap.parse_args()

    targets = [p for p in locate(args.root, args.path) if os.path.isfile(p)]
    if not targets:
        print("ERROR: working_memory.py not found (try --path).")
        sys.exit(1)

    rc = 0
    for path in targets:
        print(f"target: {path}")
        src = open(path).read()
        nm = src.count(MARKER)
        EXPECTED = 2

        if args.check:
            state = "PRESENT" if nm >= EXPECTED else ("PARTIAL" if nm else "ABSENT")
            print(f"  {state} ({nm}/{EXPECTED})")
            continue

        if args.revert:
            if nm == 0:
                print("  no marker -- nothing to revert")
                continue
            rev = src
            for old, new in EDITS:
                rev = rev.replace(new, old, 1)
            if rev.count(MARKER) != 0:
                print("  ERROR: revert residue -- ABORT")
                rc = 1
                continue
            try:
                ast.parse(rev)
            except SyntaxError as e:
                print(f"  ERROR: revert breaks syntax ({e}) -- ABORT")
                rc = 1
                continue
            bak = f"{path}.{MARKER}.prerevert.bak"
            shutil.copy2(path, bak)
            atomic_write(path, rev)
            validate_py(path)
            print(f"  REVERTED (backup: {bak})")
            continue

        # dryrun / apply
        if nm >= EXPECTED:
            print(f"  marker already present ({nm}/{EXPECTED}) -- skipping (idempotent)")
            continue
        counts = [src.count(old) for old, _ in EDITS]
        if counts != [1, 1]:
            print(f"  ERROR: anchor drift {counts} (each must be 1) -- ABORT")
            rc = 1
            continue

        new_src = src
        for old, new in EDITS:
            new_src = new_src.replace(old, new, 1)
        tf = tempfile.NamedTemporaryFile("w", suffix=".py", delete=False)
        tf.write(new_src)
        tf.close()
        try:
            py_compile.compile(tf.name, doraise=True)
            ast.parse(new_src)
        except Exception as e:
            print(f"  ERROR: patched compile/AST fail ({e}) -- ABORT")
            rc = 1
            os.remove(tf.name)
            continue
        os.remove(tf.name)
        if new_src.count(MARKER) != EXPECTED:
            print(f"  ERROR: post-patch marker {new_src.count(MARKER)} != {EXPECTED} -- ABORT")
            rc = 1
            continue

        if not args.apply:
            print(f"  DRYRUN: both anchors matched; would gate flush (marker {EXPECTED}/{EXPECTED})")
            continue

        bak = f"{path}.{MARKER}.bak"
        shutil.copy2(path, bak)
        atomic_write(path, new_src)
        validate_py(path)
        print(f"  APPLYED  (backup: {bak})")

    print()
    print(f"Marker: {MARKER}   (expected occurrences per file: 2)")
    print(f"Verify: grep -c '{MARKER}' <file>   == 2")
    if args.apply:
        print()
        print("Next:")
        print("  1. BACK UP the sidecar before the first shutdown-save:")
        print("     sudo cp -a /mnt/rtsm-data/model_store/faiss \\")
        print("                /mnt/rtsm-data/model_store/faiss.bak.$(date +%Y%m%d-%H%M%S)")
        print("  2. cd ~/rtsm/docker && docker compose restart rtsm-dev")
        print("  3. Session test: unnamed objects appear in /objects live, but do")
        print("     NOT survive a restart; the named survivors DO.")
        print("  4. The 92 existing unnamed fragments drop off disk on the first")
        print("     clean shutdown (run.py force_all collect->save, now gated;")
        print("     PATCH H empty-index guard prevents a wipe).")
    sys.exit(rc)


if __name__ == "__main__":
    main()

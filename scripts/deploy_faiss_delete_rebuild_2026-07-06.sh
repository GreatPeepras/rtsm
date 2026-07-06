#!/usr/bin/env bash
# deploy_faiss_delete_rebuild_2026-07-06.sh
# FAISS_DELETE_REBUILD_2026-07-06
#
# Runs on Execution (.53), in the rtsm repo.
# Fixes FaissClient.delete() leaving an EMPTY index (stores/vectors/faiss_client.py).
#
# THE BUG (verbatim from the live file):
#   delete() trims the shadow stores (_embeddings/_metadata) and the id maps
#   correctly, then does:
#       self._index.reset()
#       if ids_sorted:
#           # require caller to upsert with embeddings later; empty index for now
#           pass                       <-- unfinished stub: does NOTHING
#       if self.persistent_path:
#           self.save(...)             <-- persists the EMPTY index to disk
#   So after any delete, the FAISS index is empty (search returns nothing) while
#   the shadow stores still hold every survivor, and save() writes that empty
#   index over the sidecar. This is the blocker for the corpus prune: a bulk
#   delete of the 92 label_user:null fragments would wipe the whole index.
#
# THE FIX: mirror upsert_batch's proven rebuild tail -- after reset(), rebuild
# the embs matrix from the surviving _embeddings and add() it, guarding the
# 0-survivor case (faiss.add on a 0-row array throws). Byte-for-byte the same
# pattern already used a few lines up in upsert_batch.
#
# STACKED_PLACEMENT convention -- expected marker count after apply: 1
#
# ANCHOR PROVENANCE: anchor is the exact delete() reset+stub+save block pasted
# from the live .53 file 2026-07-06; verified unique + patched fragment
# py_compiles + delete's rebuild now matches upsert_batch. Still: RUN --dryrun
# FIRST. Aborts on drift.
#
# Convention: anchor-based, py_compile + AST validated, timestamped backups
# under ~/.rtsm_deploy_backups/, atomic .tmp + os.replace, marker-gated
# idempotency, --dryrun/--apply/--revert/--check. Success token: APPLYED
#
# AFTER APPLY: restart the container so the running process picks it up:
#   cd ~/rtsm/docker && docker compose restart rtsm-dev
# (the fix only matters for future deletes; it does not repair an already-
#  emptied sidecar -- but you have not run a real delete yet, so the current
#  index is intact.)
set -euo pipefail

MARKER="FAISS_DELETE_REBUILD_2026-07-06"
BK_DIR="${HOME}/.rtsm_deploy_backups"
STAMP="$(date +%Y%m%d_%H%M%S)"

# Patch the host-side file (bind-mounted into the container at /workspace/rtsm).
CANDIDATES=(
  "${HOME}/rtsm/rtsm/stores/vectors/faiss_client.py"
)
MODE="${1:---dryrun}"

TARGETS=()
for f in "${CANDIDATES[@]}"; do [ -f "$f" ] && TARGETS+=("$f"); done
if [ "${#TARGETS[@]}" -eq 0 ]; then
  echo "ERROR: faiss_client.py not found at expected path."
  echo "       Edit CANDIDATES if your repo layout differs."
  exit 1
fi
mkdir -p "${BK_DIR}"

python3 - "$MODE" "$MARKER" "$BK_DIR" "$STAMP" "${TARGETS[@]}" <<'PYEOF'
import sys, os, shutil, py_compile, ast, tempfile
mode, marker, bk_dir, stamp = sys.argv[1:5]
targets = sys.argv[5:]

OLD = ('''        self._ensure_index()
        self._index.reset()
        if ids_sorted:
            # require caller to upsert with embeddings later; empty index for now
            pass
        if self.persistent_path:''')

NEW = ('''        self._ensure_index()
        assert self._index is not None
        self._index.reset()
        # FAISS_DELETE_REBUILD_2026-07-06: previously left the index EMPTY after
        # reset (the `pass` stub), so search returned nothing and save() wrote an
        # empty index to disk while the shadow stores still held survivors. Mirror
        # upsert_batch's rebuild: re-add the survivor embeddings after reset,
        # guarding the 0-survivor case (faiss.add on a 0-row array throws).
        if ids_sorted:
            embs = np.zeros((len(ids_sorted), self.dim), dtype=np.float32)
            for row, oid in enumerate(ids_sorted):
                embs[row] = self._embeddings[oid]
            if len(embs) > 0:
                self._index.add(embs)
        if self.persistent_path:''')

def atomic_write(path, text):
    d=os.path.dirname(path); fd,tmp=tempfile.mkstemp(dir=d,suffix=".tmp")
    try:
        with os.fdopen(fd,"w") as f: f.write(text)
        os.replace(tmp,path)
    finally:
        if os.path.exists(tmp): os.remove(tmp)

rc=0
for path in targets:
    print(f"--- {path}")
    src=open(path).read(); nm=src.count(marker)

    if mode=="--check":
        print(f"  {'PRESENT' if nm else 'ABSENT'} ({nm}/1)"); continue

    if mode=="--revert":
        if nm==0: print("  no marker -- nothing to revert"); continue
        rev=src.replace(NEW,OLD,1)
        if rev.count(marker)!=0: print("  ERROR revert residue -- ABORT"); rc=1; continue
        try: ast.parse(rev)
        except SyntaxError as e: print(f"  ERROR revert syntax ({e})"); rc=1; continue
        shutil.copy2(path,f"{bk_dir}/{os.path.basename(path)}.{marker}.{stamp}.prerevert.bak")
        atomic_write(path,rev); py_compile.compile(path,doraise=True)
        print("  REVERTED (restores the empty-index stub -- not recommended)"); continue

    if nm>=1: print("  marker already present -- skipping (idempotent)"); continue

    c=src.count(OLD)
    if c!=1:
        print(f"  ERROR: anchor count {c} (want 1) -- ABORT (has delete() changed?)"); rc=1; continue

    new=src.replace(OLD,NEW,1)
    tf=tempfile.NamedTemporaryFile("w",suffix=".py",delete=False); tf.write(new); tf.close()
    try: py_compile.compile(tf.name,doraise=True); ast.parse(new)
    except Exception as e:
        print(f"  ERROR patched compile/AST ({e}) -- ABORT"); rc=1; os.remove(tf.name); continue
    os.remove(tf.name)
    if new.count(marker)!=1:
        print(f"  ERROR post-patch marker {new.count(marker)} != 1 -- ABORT"); rc=1; continue

    if mode=="--dryrun":
        print("  DRYRUN: anchor matched; would patch (marker 1/1)"); continue
    if mode=="--apply":
        shutil.copy2(path,f"{bk_dir}/{os.path.basename(path)}.{marker}.{stamp}.bak")
        atomic_write(path,new); py_compile.compile(path,doraise=True)
        print(f"  APPLYED  (backup: {os.path.basename(path)}.{marker}.{stamp}.bak)")
    else:
        print(f"  ERROR unknown mode {mode!r}"); rc=1

print()
print(f"Marker: {marker}")
print(f"Verify: grep -c '{marker}' <file>  == 1")
sys.exit(rc)
PYEOF

echo
echo "Next:"
echo "  cd ~/rtsm/docker && docker compose restart rtsm-dev   # load the fix"
echo "Test (safe, non-destructive round-trip on a throwaway oid):"
echo "  - note current /objects count, delete ONE disposable label_user:null oid,"
echo "    confirm /objects count drops by exactly 1 and OTHER objects still return"
echo "    from /search/semantic (index NOT emptied). Then it's safe for the 92-prune."

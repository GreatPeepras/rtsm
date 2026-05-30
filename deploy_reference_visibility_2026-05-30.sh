#!/usr/bin/env bash
# deploy_reference_visibility_2026-05-30.sh
#
# Ships the snapshot/reference visibility patch plus cleanup endpoints.
#
# Changes:
#
#   working_memory.py
#     1. Add WorkingMemory.remove_object(oid) method.
#
#   server.py
#     2. /objects/{oid}/snapshots falls back to reference_image_path when
#        image_crops is empty -> named objects show their reference JPEG in
#        the webui snapshot panel even when crops aren't accumulated.
#     3. DELETE /objects/{oid}/reference -- clear reference fields and
#        delete the JPEG file. Used for cleanup of polluted references
#        (e.g. the 88bfa9db integration-test residue).
#     4. DELETE /objects/{oid} -- remove an object entirely from WM. Note
#        that FAISS sidecar entries persist until restart (rehydrate will
#        bring them back). For permanent removal, also stop RTSM, edit
#        the sidecar, restart.
#
#   tests/integration/test_end_to_end_naming.py
#     5. Add DELETE /reference call to teardown so the integration test
#        cleans up its own reference upload.
#
# Usage:
#   cd ~/rtsm
#   bash deploy_reference_visibility_2026-05-30.sh
#
# Rollback: backups with .bak.<ts> suffix written next to each edited file.
#
set -euo pipefail

REPO_ROOT="${REPO_ROOT:-$(pwd)}"
WM_PATH="$REPO_ROOT/rtsm/stores/working_memory.py"
SRV_PATH="$REPO_ROOT/rtsm/api/server.py"
TEST_PATH="$REPO_ROOT/tests/integration/test_end_to_end_naming.py"
TS="$(date +%Y%m%d-%H%M%S)"

for p in "$WM_PATH" "$SRV_PATH" "$TEST_PATH"; do
  [ -f "$p" ] || { echo "FAIL: not found: $p" >&2; exit 1; }
done

cp "$WM_PATH"   "$WM_PATH.bak.$TS"
cp "$SRV_PATH"  "$SRV_PATH.bak.$TS"
cp "$TEST_PATH" "$TEST_PATH.bak.$TS"
echo "[+] backups written with suffix .bak.$TS"

python3 - <<PYEOF
import sys
from pathlib import Path

WM   = Path("$WM_PATH")
SRV  = Path("$SRV_PATH")
TEST = Path("$TEST_PATH")

wm_src   = WM.read_text()
srv_src  = SRV.read_text()
test_src = TEST.read_text()

# -------------------------------------------------------------------- #
# Edit 1: WM.remove_object() method
# Anchor: end of set_object_reference (the last method in WM).
# -------------------------------------------------------------------- #
old1 = '''            # Force a fresh LTM upsert so the new reference fields make it
            # to the sidecar without waiting for the regular cadence.
            if o.confirmed:
                heapq.heappush(self._ltm_heap, (_now_mono(), oid))
            return o'''
new1 = '''            # Force a fresh LTM upsert so the new reference fields make it
            # to the sidecar without waiting for the regular cadence.
            if o.confirmed:
                heapq.heappush(self._ltm_heap, (_now_mono(), oid))
            return o

    # ---------- removal ----------

    def remove_object(self, oid: str) -> bool:
        """Remove an object from WM entirely. Mirrors the cleanup logic in
        expire_timeouts() (proto) and evict_stale() (Tier-2 confirmed).

        Returns True if removed, False if oid was not in WM.

        Note: does NOT remove from the FAISS sidecar. If the caller wants
        permanent removal, they must also clean the sidecar (typically by
        stopping RTSM, editing the on-disk sidecar, and restarting). Without
        that, the object will rehydrate on the next startup. The HTTP layer
        attempts vectors.remove(oid) if the FaissClient exposes it.
        """
        last_xyz = None
        with self._lock:
            o = self._map.get(oid)
            if o is None:
                return False
            # frame -> objects reverse index cleanup
            fid = getattr(o, "last_update_frame_id", None)
            if fid is not None:
                fset = self._frame_to_objects.get(fid)
                if fset is not None:
                    fset.discard(oid)
                    if not fset:
                        del self._frame_to_objects[fid]
            if getattr(o, "xyz_world", None) is not None:
                last_xyz = o.xyz_world.copy()
            del self._map[oid]
        if self.index is not None:
            try:
                self.index.remove(oid, last_xyz)
            except Exception:
                logger.exception("remove_object: index.remove failed for %s", oid)
        logger.info("[WM] removed oid=%s", oid)
        return True'''

if "def remove_object(self" in wm_src:
    print("[1/5] working_memory.py: remove_object already present, skipping")
elif wm_src.count(old1) == 1:
    wm_src = wm_src.replace(old1, new1, 1)
    print("[1/5] working_memory.py: added remove_object method")
else:
    sys.exit(f"[1/5] FAIL: set_object_reference end-anchor not unique ({wm_src.count(old1)} matches)")

WM.write_text(wm_src)

# -------------------------------------------------------------------- #
# Edit 2: server.py get_object_snapshots fallback to reference image
# Anchor: the early-return when crops is empty.
# -------------------------------------------------------------------- #
old2 = '''        crops = getattr(o, 'image_crops', []) or []
        if not crops:
            return {"id": oid, "count": 0, "snapshots": []}'''
new2 = '''        crops = getattr(o, 'image_crops', []) or []
        if not crops:
            # 2026-05-30: fall back to the persisted reference snapshot if
            # set. Named objects (via name_object) get a canonical JPEG that
            # survives restart even when image_crops is empty (which it
            # always is post-rehydrate, since crops aren't persisted to
            # FAISS).
            ref_path = getattr(o, "reference_image_path", None)
            if ref_path and os.path.isfile(ref_path):
                try:
                    with open(ref_path, "rb") as _f:
                        _ref_bytes = _f.read()
                    _ref_b64 = base64.b64encode(_ref_bytes).decode("ascii")
                    _ref_uri = f"data:image/jpeg;base64,{_ref_b64}"
                    if index is not None and index != 0:
                        raise HTTPException(
                            status_code=404,
                            detail=(
                                f"Snapshot index {index} out of range "
                                f"(only the reference snapshot is available)"
                            ),
                        )
                    if index == 0:
                        return {
                            "id": oid,
                            "index": 0,
                            "total": 1,
                            "snapshot": _ref_uri,
                            "source": "reference",
                        }
                    return {
                        "id": oid,
                        "count": 1,
                        "snapshots": [{
                            "index": 0,
                            "data": _ref_uri,
                            "size_bytes": len(_ref_bytes),
                            "source": "reference",
                        }],
                    }
                except (OSError, IOError) as _e:
                    logger.warning(
                        "[snapshots] failed to read reference for %s: %s",
                        oid, _e,
                    )
            return {"id": oid, "count": 0, "snapshots": []}'''

if 'source": "reference"' in srv_src:
    print("[2/5] server.py: snapshot-reference fallback already present, skipping")
elif srv_src.count(old2) == 1:
    srv_src = srv_src.replace(old2, new2, 1)
    print("[2/5] server.py: get_object_snapshots falls back to reference")
else:
    sys.exit(f"[2/5] FAIL: get_object_snapshots empty-crops anchor not unique ({srv_src.count(old2)} matches)")

# -------------------------------------------------------------------- #
# Edit 3 + 4: server.py add DELETE /objects/{oid}/reference and
# DELETE /objects/{oid}. Anchor: just before the debug endpoint.
# -------------------------------------------------------------------- #
old3 = '''    @app.get("/objects/{oid}/debug")'''
new3 = '''    # 2026-05-30: cleanup endpoints. Mirror the design doc's intent
    # that named objects are user-managed and pollution should be
    # explicitly removable.
    @app.delete("/objects/{oid}/reference")
    def delete_object_reference(oid: str) -> Dict[str, Any]:
        """Clear the reference snapshot fields on a WM object and delete
        the on-disk JPEG.

        Triggers an LTM heap push so the FAISS sidecar loses the reference
        fields on the next upsert cycle (asynchronous; restart inside
        flush_period_s can lose this -- mirrors the 5/29 PATCH timing
        caveat).
        """
        if not hasattr(working_memory, "set_object_reference"):
            raise HTTPException(
                status_code=405,
                detail="reference not supported on frozen working memory",
            )
        o = working_memory.get(oid)
        if o is None:
            raise HTTPException(status_code=404, detail=f"Object {oid} not found")
        old_path = getattr(o, "reference_image_path", None)
        try:
            working_memory.set_object_reference(oid, image_path=None, embedding=None)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
        file_deleted = False
        if old_path and os.path.isfile(old_path):
            try:
                os.remove(old_path)
                file_deleted = True
            except OSError as e:
                logger.warning(
                    "[delete_reference] failed to remove %s: %s", old_path, e
                )
        return {
            "id": oid,
            "cleared": True,
            "old_reference_image_path": old_path,
            "file_deleted": file_deleted,
        }

    @app.delete("/objects/{oid}")
    def delete_object(oid: str) -> Dict[str, Any]:
        """Remove an object from WM entirely.

        Also deletes the reference JPEG if present, and attempts to remove
        from the FAISS sidecar if the configured vectors client exposes a
        remove() method. Without sidecar removal, the object will rehydrate
        on next restart.
        """
        if not hasattr(working_memory, "remove_object"):
            raise HTTPException(
                status_code=405,
                detail="DELETE not supported on frozen working memory",
            )
        o = working_memory.get(oid)
        if o is None:
            raise HTTPException(status_code=404, detail=f"Object {oid} not found")
        ref_path = getattr(o, "reference_image_path", None)
        file_deleted = False
        if ref_path and os.path.isfile(ref_path):
            try:
                os.remove(ref_path)
                file_deleted = True
            except OSError as e:
                logger.warning(
                    "[delete_object] failed to remove reference %s: %s", ref_path, e
                )
        faiss_removed = False
        if vectors is not None and hasattr(vectors, "remove"):
            try:
                vectors.remove(oid)
                faiss_removed = True
            except Exception as e:
                logger.warning(
                    "[delete_object] vectors.remove failed for %s: %s", oid, e
                )
        removed = working_memory.remove_object(oid)
        if not removed:
            raise HTTPException(
                status_code=500,
                detail=f"Object {oid} disappeared from WM during delete",
            )
        return {
            "id": oid,
            "removed": True,
            "reference_file_deleted": file_deleted,
            "faiss_sidecar_removed": faiss_removed,
        }

    @app.get("/objects/{oid}/debug")'''

if "@app.delete(\"/objects/{oid}/reference\")" in srv_src:
    print("[3/5] server.py: DELETE endpoints already present, skipping")
elif srv_src.count(old3) == 1:
    srv_src = srv_src.replace(old3, new3, 1)
    print("[3/5] server.py: added DELETE /objects/{oid}/reference + DELETE /objects/{oid}")
else:
    sys.exit(f"[3/5] FAIL: debug endpoint anchor not unique ({srv_src.count(old3)} matches)")

SRV.write_text(srv_src)

# -------------------------------------------------------------------- #
# Edit 4 (test): add reference cleanup to the integration test teardown.
# Anchor: the existing PATCH restore in the finally block.
# -------------------------------------------------------------------- #
old4 = '''    finally:
        # Restore the original label_user. None -> clears it (which is
        # also fine if it was None to begin with). Best-effort: a restore
        # failure shouldn't mask the test outcome.
        try:
            r = requests.patch(
                f"{RTSM_URL}/objects/{oid}",
                json={"label_user": original_label_user},
                timeout=TIMEOUT_S,
            )
            print(f"[restore] label_user <- {original_label_user!r}: HTTP {r.status_code}")
        except Exception as e:
            print(f"[restore] WARNING: failed to restore label_user: {e}", file=sys.stderr)'''
new4 = '''    finally:
        # 2026-05-30: clean up the reference image we POSTed in step 2.
        # Without this, every test run leaves a stray purple JPEG on disk
        # plus polluted reference_emb on the object (caught the hard way).
        try:
            r = requests.delete(
                f"{RTSM_URL}/objects/{oid}/reference",
                timeout=TIMEOUT_S,
            )
            print(f"[cleanup] DELETE /reference: HTTP {r.status_code}")
        except Exception as e:
            print(f"[cleanup] WARNING: failed to delete reference: {e}", file=sys.stderr)
        # Restore the original label_user. None -> clears it (which is
        # also fine if it was None to begin with). Best-effort: a restore
        # failure shouldn't mask the test outcome.
        try:
            r = requests.patch(
                f"{RTSM_URL}/objects/{oid}",
                json={"label_user": original_label_user},
                timeout=TIMEOUT_S,
            )
            print(f"[restore] label_user <- {original_label_user!r}: HTTP {r.status_code}")
        except Exception as e:
            print(f"[restore] WARNING: failed to restore label_user: {e}", file=sys.stderr)'''

if "DELETE /reference" in test_src:
    print("[4/5] test_end_to_end_naming.py: cleanup call already present, skipping")
elif test_src.count(old4) == 1:
    test_src = test_src.replace(old4, new4, 1)
    print("[4/5] test_end_to_end_naming.py: added reference cleanup to teardown")
else:
    sys.exit(f"[4/5] FAIL: test finally-block anchor not unique ({test_src.count(old4)} matches)")

TEST.write_text(test_src)

# -------------------------------------------------------------------- #
# Edit 5: verify server.py has 'import os' (needed for os.path.isfile and
# os.remove in the new endpoints).
# -------------------------------------------------------------------- #
if "import os\\n" in srv_src or "import os," in srv_src or "\\nimport os\\n" in srv_src:
    print("[5/5] server.py: import os already present")
else:
    print("[5/5] WARNING: 'import os' was not found in server.py. The new")
    print("       endpoints use os.path.isfile and os.remove. If the server")
    print("       fails to start with NameError on 'os', add 'import os' to")
    print("       the imports block at the top of rtsm/api/server.py.")

print()
print("Applied. Restart RTSM:")
print("  docker compose -f docker/docker-compose.yml restart rtsm-dev")
print()
print("Verify (after restart, give it ~15s to warm up):")
print()
print("  # 1. healthz")
print("  curl -s http://localhost:8002/healthz | jq .")
print()
print("  # 2. snapshot fallback for the gloves (should now show 1 snapshot")
print("  #    with source='reference')")
print("  curl -s http://localhost:8002/objects/7543b81b2084438f/snapshots | \\\\")
print("    jq '{count, source: (.snapshots[0].source // .source)}'")
print()
print("  # 3. clean up my test residue on the bench (88bfa9db)")
print("  curl -X DELETE http://localhost:8002/objects/88bfa9db078b4496/reference | jq .")
print("  # Expect: {\"cleared\": true, \"file_deleted\": false, ...}")
print("  # file_deleted=false because you already rm'd it manually")
print()
print("  # 4. Remove the bench entirely if it's pure noise (optional):")
print("  # curl -X DELETE http://localhost:8002/objects/88bfa9db078b4496 | jq .")
print()
print("  # 5. Re-run the integration test to confirm teardown is clean")
print("  RTSM_URL=http://localhost:8002 python3 tests/integration/test_end_to_end_naming.py")
print("  # And then: ls /mnt/rtsm-data/rtsm-workdir/refs/ should NOT have a fresh")
print("  # __inttest__ JPEG -- it should have been cleaned up automatically.")
PYEOF

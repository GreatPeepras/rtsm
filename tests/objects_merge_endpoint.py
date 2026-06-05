# =============================================================================
# POST /objects/merge: paste into server.py
#
# Two paste locations:
#   (A) Pydantic body model. Add this near the other module-scoped models
#       (around line 70, with ObjectPatch and PoseStateRequest).
#   (B) The endpoint itself. Add this inside the function that registers
#       routes -- adjacent to the PATCH /objects/{oid} handler (around
#       line 432 in the current server.py).
#
# This module is a paste-helper, not a runnable file by itself.
# =============================================================================


# ----- (A) Body model: paste near ObjectPatch -----

class MergeObjectsRequest(BaseModel):
    """Body schema for POST /objects/merge.

    winner_oid and loser_oid both required. winner_oid keeps its id, xyz,
    and canonical position; loser_oid is dissolved into the winner.
    """
    winner_oid: str = Field(..., min_length=1)
    loser_oid: str = Field(..., min_length=1)
    dry_run: bool = False

    model_config = {"extra": "forbid"}


# ----- (B) Endpoint: paste next to PATCH /objects/{oid} -----

    @app.post("/objects/merge")
    def merge_objects_endpoint(
        req: MergeObjectsRequest = Body(...),
    ) -> Dict[str, Any]:
        """Consolidate two confirmed OIDs into one.

        Use cases:
          - Mode B duplicates: same physical object split across two OIDs
            because of CLIP label drift or position drift.
          - Manual cleanup during ground-truth annotation pass.

        Semantics:
          - winner_oid keeps its id, xyz_world, cov_world.
          - Galleries (emb_gallery + image_crops) are unioned with the
            same dedup + FIFO gates that update_object uses.
          - view_bins are unioned; collisions averaged.
          - label_scores: per-key hits-weighted average.
          - label_hits: per-key sum.
          - label_user / movability_class / reference_image_path:
            winner's if set, else loser's (human pins survive).
          - hits summed; stability = max; created_* = older; last_seen_* =
            most recent.

        Side effects:
          - WM mutated atomically under lock.
          - Persistent gallery on disk: winner's directory rewritten,
            loser's removed.
          - FAISS sidecar updated: loser deleted, winner upserted.
          - Audit log JSON written under cfg.object.merge_log_dir.

        Errors:
          400 - winner_oid == loser_oid, dim mismatch, validation
          404 - either oid not found
          405 - WM is frozen (serve-mode)
        """
        # Frozen WM (serve-mode) is read-only.
        if not hasattr(working_memory, "merge_objects"):
            raise HTTPException(
                status_code=405,
                detail="merge not supported on frozen working memory (serve-mode)",
            )

        winner_oid = req.winner_oid.strip()
        loser_oid = req.loser_oid.strip()

        try:
            result = working_memory.merge_objects(
                winner_oid, loser_oid, dry_run=req.dry_run,
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

        # Method returns {"error": "not_found", ...} for unknown oids,
        # instead of raising. Translate to 404.
        if result.get("error") == "not_found":
            raise HTTPException(
                status_code=404,
                detail=f"Object {result.get('missing_oid')} not found",
            )

        # On dry-run we skip the FAISS sync (no state change).
        if req.dry_run:
            return result

        # Sync to FAISS: delete loser, upsert winner with merged state.
        # Best-effort with logging -- if this fails, the in-memory state
        # is still correct and the next normal upsert cycle will reconcile.
        # The audit log captures intent so manual recovery is possible.
        try:
            if faiss_client is not None:
                # Delete loser first. The current FaissClient.delete()
                # leaves the index empty after the call but the next
                # upsert_batch fully rebuilds, so this ordering is safe.
                faiss_client.delete([loser_oid])
                record = working_memory.build_faiss_record_for_merge(winner_oid)
                if record is not None:
                    faiss_client.upsert_batch([record])
        except Exception:
            import traceback
            traceback.print_exc()
            # Don't fail the response -- WM is the source of truth, and
            # the merge has already succeeded there. Surface a warning in
            # the result instead.
            result["faiss_sync_warning"] = (
                "FAISS sync raised; check logs. WM state is correct; "
                "next observation or restart will reconcile."
            )

        # Re-fetch and return the merged winner's full detail.
        winner = working_memory.get(winner_oid)
        if winner is not None:
            result["winner"] = _obj_detail(winner)
        return result

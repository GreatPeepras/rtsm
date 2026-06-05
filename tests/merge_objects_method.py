# =============================================================================
# merge_objects: paste these two methods into the WorkingMemory class.
#
# Location: somewhere after `evict_stale` (around line ~670 in the current
# working_memory.py), before `iter_objects` is fine. The exact position
# doesn't matter as long as it's inside `class WorkingMemory`.
#
# This module is a paste-helper, not a runnable file by itself.
# =============================================================================

    # ------------------------------------------------------------------ #
    # 2026-06-01: Mode B duplicate consolidation.
    #
    # POST /objects/merge calls merge_objects(winner_oid, loser_oid).
    # The winner's id and xyz survive; the loser is dissolved into the
    # winner (galleries unioned with dedup, hits summed, view_bins
    # unioned, label_scores hits-weighted averaged, user-pinned fields
    # preserved). Disk gallery for loser is removed; winner's is rewritten
    # to match merged state.
    #
    # The merge is an in-WM operation. The caller (POST /objects/merge in
    # server.py) is responsible for syncing the change to FAISS by
    # calling faiss_client.delete([loser_oid]) followed by
    # faiss_client.upsert_batch([winner_record]) using the helper
    # build_faiss_record_for_merge() below.
    # ------------------------------------------------------------------ #

    def merge_objects(
        self,
        winner_oid: str,
        loser_oid: str,
        *,
        dry_run: bool = False,
        audit_log_dir: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Consolidate loser_oid into winner_oid.

        Returns a result dict with stats and the audit log path (if written).
        Raises ValueError on winner==loser, dim mismatch, etc.
        Returns {"error": "not_found", ...} if either oid is unknown.

        Side effects on success (non-dry-run):
          - winner's ObjectState in WM gets the merged values
          - loser is removed from WM map, spatial index, frame tracking
          - winner's persistent gallery directory is rewritten on disk
          - loser's persistent gallery directory is removed
          - audit log JSON written under audit_log_dir (best-effort)

        FAISS is NOT touched here. The caller must sync separately.
        """
        if winner_oid == loser_oid:
            raise ValueError("winner_oid and loser_oid must differ")

        # Snapshot both states under the lock so we have a consistent
        # picture for the audit log AND the merge computation. We hold the
        # lock for the whole modify-and-remove phase to keep the operation
        # atomic from the WM's perspective.
        with self._lock:
            winner = self._map.get(winner_oid)
            loser = self._map.get(loser_oid)
            if winner is None:
                return {"error": "not_found", "missing_oid": winner_oid}
            if loser is None:
                return {"error": "not_found", "missing_oid": loser_oid}
            if winner._dim != loser._dim:
                raise ValueError(
                    f"dim mismatch: winner={winner._dim} loser={loser._dim}"
                )

            # Pre-merge snapshots for the audit log (taken before any mutation).
            winner_pre = self._snapshot_for_audit(winner)
            loser_pre = self._snapshot_for_audit(loser)

            # Compute the merged values as a pure function over the two
            # ObjectStates. No side effects yet.
            merged = self._compute_merge_locked(winner, loser)

            stats = {
                "hits_before": {"winner": winner.hits, "loser": loser.hits},
                "hits_after": merged["hits"],
                "emb_gallery_before": {
                    "winner": int(winner.emb_gallery.shape[0]),
                    "loser": int(loser.emb_gallery.shape[0]),
                },
                "emb_gallery_after": int(merged["emb_gallery"].shape[0]),
                "image_crops_before": {
                    "winner": len(winner.image_crops),
                    "loser": len(loser.image_crops),
                },
                "image_crops_after": len(merged["image_crops"]),
                "view_bins_before": {
                    "winner": len(winner.view_bins),
                    "loser": len(loser.view_bins),
                },
                "view_bins_after": len(merged["view_bins"]),
                "label_user_inherited_from_loser":
                    merged["_label_user_inherited_from_loser"],
                "winner_xyz": winner.xyz_world.tolist(),
                "loser_xyz": loser.xyz_world.tolist(),
                "spatial_distance_m": float(
                    np.linalg.norm(winner.xyz_world - loser.xyz_world)
                ),
            }

            if dry_run:
                return {
                    "winner_oid": winner_oid,
                    "loser_oid": loser_oid,
                    "dry_run": True,
                    "stats": stats,
                    "audit_log_path": None,
                    "winner_pre": winner_pre,
                    "loser_pre": loser_pre,
                }

            # ---- Apply merge to winner in-place ----
            winner.emb_mean = merged["emb_mean"]
            winner.emb_gallery = merged["emb_gallery"]
            winner.view_bins = merged["view_bins"]
            winner.label_scores = merged["label_scores"]
            winner.label_hits = merged["label_hits"]
            winner.label_primary = merged["label_primary"]
            winner.label_user = merged["label_user"]
            winner.movability_class = merged["movability_class"]
            winner.reference_image_path = merged["reference_image_path"]
            winner.reference_emb = merged["reference_emb"]
            winner.hits = merged["hits"]
            winner.stability = merged["stability"]
            winner.image_crops = merged["image_crops"]
            winner.created_mono = merged["created_mono"]
            winner.created_wall_utc = merged["created_wall_utc"]
            winner.last_seen_mono = merged["last_seen_mono"]
            winner.last_seen_wall_utc = merged["last_seen_wall_utc"]
            # xyz / cov / pose_state stay as winner's (the canonical position).
            # last_upsert_* stay as winner's; the caller is expected to
            # re-upsert to FAISS, which will overwrite these on success.

            # ---- Remove loser from WM (mirrors evict_stale pattern) ----
            loser_frame_id = loser.last_update_frame_id
            if loser_frame_id is not None:
                fset = self._frame_to_objects.get(loser_frame_id)
                if fset is not None:
                    fset.discard(loser_oid)
                    if not fset:
                        del self._frame_to_objects[loser_frame_id]
            del self._map[loser_oid]

            # Take a snapshot of the merged winner for the audit log.
            winner_post = self._snapshot_for_audit(winner)

        # ---- Outside the lock: spatial index + disk persistence ----
        if self.index is not None:
            try:
                self.index.remove(loser_oid, None)
            except Exception:
                logger.exception(
                    "[WM] merge: index.remove failed for loser %s",
                    loser_oid[:8],
                )

        # Rewrite winner's gallery on disk to match the merged state.
        # We do this by clearing winner's directory first, then writing
        # all merged crops and the merged embs. Atomic enough for our
        # purposes -- if a crash occurs mid-rewrite, rehydrate falls back
        # to whatever's on disk and the next observation rebuilds it.
        try:
            self._rewrite_gallery_after_merge(winner_oid, winner)
        except Exception:
            logger.exception(
                "[WM] merge: gallery rewrite failed for winner %s",
                winner_oid[:8],
            )

        # Remove loser's disk gallery.
        try:
            self._gallery.remove(loser_oid)
        except Exception:
            logger.exception(
                "[WM] merge: gallery.remove failed for loser %s",
                loser_oid[:8],
            )

        # ---- Audit log (best-effort) ----
        audit_log_path: Optional[str] = None
        try:
            audit_log_path = self._write_merge_audit(
                audit_log_dir, winner_oid, loser_oid,
                winner_pre, loser_pre, winner_post, stats,
            )
        except Exception:
            logger.exception("[WM] merge: audit log write failed")

        logger.info(
            "[WM] merge: %s <- %s | hits %d->%d, gallery %d->%d, bins %d->%d",
            winner_oid[:8], loser_oid[:8],
            winner_pre.get("hits", 0), stats["hits_after"],
            winner_pre.get("emb_gallery_n", 0), stats["emb_gallery_after"],
            len(winner_pre.get("view_bin_keys", [])), stats["view_bins_after"],
        )

        return {
            "winner_oid": winner_oid,
            "loser_oid": loser_oid,
            "dry_run": False,
            "stats": stats,
            "audit_log_path": audit_log_path,
            "winner_pre": winner_pre,
            "loser_pre": loser_pre,
            "winner_post": winner_post,
        }

    # ---- Merge internals (private; safe to call only under self._lock) ----

    def _compute_merge_locked(
        self,
        winner: "ObjectState",
        loser: "ObjectState",
    ) -> Dict[str, Any]:
        """Compute the merged field values. Pure: no side effects.

        Caller must hold self._lock (we read multiple fields from both
        ObjectStates and the read needs to be consistent).
        """
        w_hits = max(1, int(winner.hits))
        l_hits = max(1, int(loser.hits))

        # emb_mean: hits-weighted, renormalized.
        new_emb_mean = _l2norm(
            winner.emb_mean.astype(np.float32) * w_hits
            + loser.emb_mean.astype(np.float32) * l_hits
        )

        # emb_gallery: combine with the same dedup + FIFO gate that
        # update_object enforces, so the merged gallery satisfies the
        # invariant that all entries are >= gallery_dupe_cos apart.
        new_gallery = self._merge_galleries(winner.emb_gallery, loser.emb_gallery)

        # view_bins: union. On bin collision, average and renormalize
        # (same rule as update_object's per-bin update).
        new_view_bins: Dict[int, Emb] = {}
        for bin_id, emb in winner.view_bins.items():
            new_view_bins[bin_id] = emb.astype(np.float32).copy()
        for bin_id, emb in loser.view_bins.items():
            if bin_id in new_view_bins:
                new_view_bins[bin_id] = _l2norm(
                    0.5 * new_view_bins[bin_id]
                    + 0.5 * emb.astype(np.float32)
                )
            else:
                new_view_bins[bin_id] = emb.astype(np.float32).copy()

        # label_scores: per-key hits-weighted average. label_hits: sum.
        all_label_keys = (
            set(winner.label_scores.keys()) | set(loser.label_scores.keys())
        )
        new_label_scores: Dict[str, float] = {}
        new_label_hits: Dict[str, int] = {}
        for k in all_label_keys:
            w_s = float(winner.label_scores.get(k, 0.0))
            l_s = float(loser.label_scores.get(k, 0.0))
            w_k = int(winner.label_hits.get(k, 0))
            l_k = int(loser.label_hits.get(k, 0))
            denom = max(1, w_k + l_k)
            new_label_scores[k] = (w_s * w_k + l_s * l_k) / denom
            new_label_hits[k] = w_k + l_k

        # label_primary: recomputed from the merged scores. Gate on
        # min_label_hits to match the surfacing rule used elsewhere.
        gated = {
            k: v for k, v in new_label_scores.items()
            if new_label_hits.get(k, 0) >= self.min_label_hits
        }
        if gated:
            new_label_primary = max(gated, key=gated.get)
        elif new_label_scores:
            new_label_primary = max(
                new_label_scores.items(), key=lambda kv: kv[1]
            )[0]
        else:
            new_label_primary = winner.label_primary

        # image_crops: concat + FIFO truncate.
        new_crops = list(winner.image_crops) + list(loser.image_crops)
        if len(new_crops) > self.max_image_crops:
            new_crops = new_crops[-self.max_image_crops:]

        # User-pinned fields: winner wins if set, else inherit from loser.
        label_user_winner = winner.label_user
        label_user_loser = loser.label_user
        new_label_user = label_user_winner or label_user_loser
        label_user_inherited = (
            label_user_winner is None and label_user_loser is not None
        )

        new_movability = winner.movability_class or loser.movability_class

        new_ref_path = winner.reference_image_path or loser.reference_image_path
        new_ref_emb = (
            winner.reference_emb if winner.reference_image_path is not None
            else loser.reference_emb
        )

        return {
            "emb_mean": new_emb_mean,
            "emb_gallery": new_gallery,
            "view_bins": new_view_bins,
            "label_scores": new_label_scores,
            "label_hits": new_label_hits,
            "label_primary": new_label_primary,
            "label_user": new_label_user,
            "_label_user_inherited_from_loser": label_user_inherited,
            "movability_class": new_movability,
            "reference_image_path": new_ref_path,
            "reference_emb": new_ref_emb,
            "hits": winner.hits + loser.hits,
            "stability": max(winner.stability, loser.stability),
            "image_crops": new_crops,
            "created_mono": min(winner.created_mono, loser.created_mono),
            "created_wall_utc": min(
                winner.created_wall_utc, loser.created_wall_utc
            ),
            "last_seen_mono": max(winner.last_seen_mono, loser.last_seen_mono),
            "last_seen_wall_utc": max(
                winner.last_seen_wall_utc, loser.last_seen_wall_utc
            ),
        }

    def _merge_galleries(
        self,
        winner_emb: np.ndarray,
        loser_emb: np.ndarray,
    ) -> np.ndarray:
        """Combine two emb_galleries respecting dedup + FIFO.

        Same gate as update_object: each candidate emb is dropped if it's
        within gallery_dupe_cos of any existing entry. Survivors are
        appended with FIFO truncation to max_gallery.

        Returns float16 array of shape (M, D), 0 <= M <= max_gallery.
        """
        if (winner_emb is None or winner_emb.size == 0) and \
           (loser_emb is None or loser_emb.size == 0):
            # Both empty -- preserve dimensionality from whichever exists.
            ref = winner_emb if winner_emb is not None else loser_emb
            if ref is None:
                # Truly nothing; return a zero-row float16 with unknown D.
                # Shouldn't happen for confirmed objects but defensive.
                return np.zeros((0, 1), dtype=np.float16)
            return np.zeros((0, ref.shape[-1]), dtype=np.float16)

        # Start with winner's gallery as the base (preserves winner's
        # observation order at the front of the FIFO).
        if winner_emb is None or winner_emb.size == 0:
            combined = np.zeros((0, loser_emb.shape[-1]), dtype=np.float16)
        else:
            combined = winner_emb.astype(np.float16).copy()

        if loser_emb is None or loser_emb.size == 0:
            return combined

        # Append loser's entries one by one, applying the same dedup
        # gate as update_object's per-observation accumulation.
        for i in range(int(loser_emb.shape[0])):
            e32 = loser_emb[i].astype(np.float32)
            if combined.shape[0] > 0:
                cos_max = float(np.max(
                    combined.astype(np.float32) @ e32
                ))
                if cos_max >= self.gallery_dupe_cos:
                    continue  # near-duplicate; drop it
            e16 = e32.astype(np.float16)[None, :]
            if combined.shape[0] < self.max_gallery:
                combined = np.vstack([combined, e16])
            else:
                combined = np.vstack([combined[1:], e16])

        return combined

    def _rewrite_gallery_after_merge(
        self,
        oid: str,
        o: "ObjectState",
    ) -> None:
        """After in-memory merge, sync winner's disk gallery to match.

        Strategy: clear winner's directory, then re-write all current
        image_crops (numbered fresh from 1) and the merged embs.npy.
        This is simpler than trying to in-place-extend and avoids
        FIFO-numbering drift.

        Best-effort -- exceptions are logged but don't propagate. The
        in-memory state is the source of truth; disk is a cache.
        """
        if not self._gallery.enabled:
            return
        # Remove anything currently in winner's dir (.jpg, embs.npy,
        # manifest.json). Then write the merged contents fresh.
        self._gallery.remove(oid)
        # Re-create dir lazily via write_crop / write_embs.
        for jpeg_bytes in o.image_crops:
            self._gallery.write_crop(oid, jpeg_bytes, self.max_image_crops)
        if o.emb_gallery.shape[0] > 0:
            self._gallery.write_embs(oid, o.emb_gallery)

    def _snapshot_for_audit(
        self,
        o: "ObjectState",
    ) -> Dict[str, Any]:
        """Compact JSON-safe snapshot of an ObjectState for audit logs.

        Excludes embeddings (too large) but records their shapes. Keeps
        everything needed to identify and partially reconstruct the
        object if a merge needs to be manually reversed.
        """
        return {
            "id": o.id,
            "xyz_world": o.xyz_world.tolist(),
            "cov_world": o.cov_world.tolist(),
            "emb_mean_norm": float(np.linalg.norm(o.emb_mean)),
            "emb_gallery_n": int(o.emb_gallery.shape[0]),
            "view_bin_keys": sorted(int(k) for k in o.view_bins.keys()),
            "label_scores": dict(o.label_scores),
            "label_hits": dict(o.label_hits),
            "label_primary": o.label_primary,
            "label_user": o.label_user,
            "movability_class": o.movability_class,
            "pose_state_at_observation": o.pose_state_at_observation,
            "reference_image_path": o.reference_image_path,
            "hits": int(o.hits),
            "stability": float(o.stability),
            "confirmed": bool(o.confirmed),
            "created_wall_utc": float(o.created_wall_utc),
            "last_seen_wall_utc": float(o.last_seen_wall_utc),
            "image_crops_count": len(o.image_crops),
            "last_update_frame_id": o.last_update_frame_id,
        }

    def _write_merge_audit(
        self,
        audit_log_dir: Optional[str],
        winner_oid: str,
        loser_oid: str,
        winner_pre: Dict[str, Any],
        loser_pre: Dict[str, Any],
        winner_post: Dict[str, Any],
        stats: Dict[str, Any],
    ) -> Optional[str]:
        """Write merge audit JSON. Returns path written, or None."""
        # Resolve audit log directory. Caller-provided takes precedence;
        # else read from cfg.object.merge_log_dir; else default under
        # the persistent gallery's parent (so it sits alongside crops).
        if audit_log_dir is None:
            audit_log_dir = self.cfg.get("object", {}).get(
                "merge_log_dir", "/workspace/workdir/merge_log"
            )
        if not audit_log_dir:
            return None
        os.makedirs(audit_log_dir, exist_ok=True)

        ts = time.strftime("%Y-%m-%dT%H-%M-%SZ", time.gmtime())
        fname = f"{ts}_{winner_oid[:8]}_{loser_oid[:8]}.json"
        path = os.path.join(audit_log_dir, fname)

        payload = {
            "timestamp_iso": time.strftime(
                "%Y-%m-%dT%H:%M:%SZ", time.gmtime()
            ),
            "timestamp_wall_utc": _now_wall_utc(),
            "winner_oid": winner_oid,
            "loser_oid": loser_oid,
            "stats": stats,
            "winner_pre": winner_pre,
            "loser_pre": loser_pre,
            "winner_post": winner_post,
        }
        tmp = path + ".tmp"
        with open(tmp, "w") as fp:
            json.dump(payload, fp, indent=2, default=str)
        os.replace(tmp, path)
        return path

    # ---- FAISS record builder for the merge endpoint ----

    def build_faiss_record_for_merge(
        self,
        winner_oid: str,
    ) -> Optional[Dict[str, Any]]:
        """Construct the payload that the endpoint should upsert into
        FaissClient after a merge. Returns None if winner is gone.

        Mirrors the shape collect_ready_for_upsert produces. Read this
        AFTER merge_objects has completed; the values reflect merged
        state.
        """
        with self._lock:
            o = self._map.get(winner_oid)
            if o is None:
                return None
            label_topk = sorted(
                o.label_scores.items(), key=lambda kv: kv[1], reverse=True
            )
            label_topk_keys = [k for k, _ in label_topk]
            label_topk_scores = [float(v) for _, v in label_topk]
            label_topk_hits = [
                int(o.label_hits.get(k, 0)) for k in label_topk_keys
            ]
            return {
                "object_id": winner_oid,
                "emb": o.emb_mean.astype(np.float32),
                "xyz": o.xyz_world.astype(np.float32),
                "label_primary": o.label_primary,
                "label_user": o.label_user,
                "display_label": o.label_user or o.label_primary,
                "movability_class": o.movability_class,
                "label_topk": label_topk_keys,
                "label_scores": label_topk_scores,
                "label_hits": label_topk_hits,
                "stability": float(o.stability),
                "created_at": float(o.created_wall_utc),
                "created_mono": float(o.created_mono),
                "pose_state_at_observation": o.pose_state_at_observation,
            }

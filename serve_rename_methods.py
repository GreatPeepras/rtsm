    # ---- 2026-05-28: serve-mode user-label write (rename support) ----
    def update_user_fields(self, oid, *, label_user=_UNSET, movability_class=_UNSET):
        """Set user-controllable fields on a frozen object AND persist to the
        meta sidecar, so renames work in serve mode (previously 405).

        Mirrors WorkingMemory.update_user_fields' contract: _UNSET = leave
        unchanged, None = clear, empty label_user / invalid movability_class
        raise ValueError. Returns the updated object, or None if oid unknown.
        Writes through to the on-disk sidecar (serve mode is single-writer) so
        the change survives restart/reload.
        """
        with self._lock:
            o = self._map.get(oid)
            if o is None:
                return None
            sets = {}
            if label_user is not _UNSET:
                if label_user is not None:
                    if not isinstance(label_user, str) or not label_user.strip():
                        raise ValueError("label_user must be a non-empty string or None")
                    o.label_user = label_user.strip()
                else:
                    o.label_user = None
                o.display_label = o.label_user or getattr(o, "label_primary", None)
                sets["label_user"] = o.label_user
                sets["display_label"] = o.display_label
            if movability_class is not _UNSET:
                if movability_class is not None and movability_class not in _VALID_MOVABILITY:
                    raise ValueError(
                        f"movability_class must be one of {sorted(_VALID_MOVABILITY)} "
                        f"or None, got {movability_class!r}"
                    )
                o.movability_class = movability_class
                sets["movability_class"] = movability_class
            if sets:
                self._persist_user_fields(oid, sets)
            return o

    def _persist_user_fields(self, oid, sets):
        """Atomic read-modify-write of the meta sidecar for one oid. Lock held.

        Failure to persist is logged but does not raise -- the in-memory change
        already succeeded; a missing sidecar just means the rename is not
        durable (visible until next restart). Single-writer in serve mode, so
        no contention with an ingest pipeline.
        """
        path = self._meta_path
        try:
            if not os.path.exists(path):
                logger.warning("[FrozenWM] cannot persist rename; sidecar missing: %s", path)
                return
            with open(path, "r") as f:
                data = json.load(f)
            if not isinstance(data, dict) or oid not in data:
                logger.warning("[FrozenWM] oid %s not in sidecar; in-memory only", oid)
                return
            data[oid].update(sets)
            tmp = path + ".tmp"
            with open(tmp, "w") as f:
                json.dump(data, f)
            os.replace(tmp, path)
            # Our own write bumps mtime; refresh the load marker so _is_stale()
            # doesn't flag this self-induced change as external staleness.
            self._loaded_wall_utc = time.time()
            logger.info("[FrozenWM] persisted %s to sidecar for oid=%s", list(sets), oid)
        except Exception:
            logger.exception("[FrozenWM] failed to persist user fields for %s", oid)


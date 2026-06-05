
    # ------------------------------------------------------------------ #
    # 2026-05-28: Tier-2 time-based eviction policy (movability-aware).
    #
    # Phase scope: the *time axis* of Tier-2 from docs/design/persistence.md.
    # NOT included here (Phase-2b): Tier-1 frustum-miss counters (need the
    # live camera) and the soft-eviction ghost-log + re-id buffer (a
    # `ghost_sink` hook is provided for forward-compat, but this first cut
    # hard-removes from WM). DISABLED by default: deploying changes nothing
    # until cfg["eviction"]["enabled"] is set true AND the movability classes
    # are confirmed to be assigned at ingest.
    # ------------------------------------------------------------------ #

    # Class -> default TTL in SECONDS. These are the "Tier-2 TTL" column from
    # docs/design/persistence.md and are explicitly PLACEHOLDERS for Phase-2
    # calibration, not committed operating points. None == never evict (infinite).
    # Override any class via cfg["eviction"]["ttl_s"][<class>].
    _DEFAULT_EVICTION_TTL_S = {
        "permanent":   None,            # walls/doors/built-ins -> never
        "static":      90.0 * 86400.0,  # couch/fridge/desk     -> 90 days
        "semi_static": 14.0 * 86400.0,  # chair/lamp/basket     -> 14 days
        "movable":      3.0 * 86400.0,  # mug/book/remote        -> 3 days
        "roaming":      1.0 * 86400.0,  # toys/robot/person      -> 1 day
        "ephemeral":   12.0 * 3600.0,   # snack bag/mail         -> 12 hours
    }
    # Fallback when movability_class is None/unset. Matches the ObjectState
    # field docstring ("eviction logic falls back to ... 'semi_static'").
    _EVICTION_FALLBACK_CLASS = "semi_static"

    def _eviction_ttl_s(self, cls: Optional[str]) -> Optional[float]:
        """Resolve the Tier-2 TTL (seconds) for a movability class.

        Merges cfg["eviction"]["ttl_s"] over the class defaults. Returns
        None for an infinite TTL (never evict). Pure / lock-free.
        """
        if cls not in self._VALID_MOVABILITY:
            cls = self._EVICTION_FALLBACK_CLASS
        ttl = dict(self._DEFAULT_EVICTION_TTL_S)
        override = (self.cfg.get("eviction", {}) or {}).get("ttl_s", {}) or {}
        for k, v in override.items():
            if k in self._VALID_MOVABILITY:
                ttl[k] = (None if v is None else float(v))
        return ttl.get(cls)

    def _compute_evictable_locked(self, now_wall: float) -> List[Dict[str, Any]]:
        """Return Tier-2 eviction candidates. Caller MUST hold self._lock.

        A confirmed object is a candidate iff ALL of:
          * label_user is None          (HARD INVARIANT: user-named is treasured)
          * its class TTL is finite     (permanent / ?-override never evict)
          * last_seen_wall_utc is known (>0)   (conservative: unknown -> keep)
          * (now_wall - last_seen_wall_utc) > TTL
        Protos are ignored (handled by expire_timeouts()).
        """
        out: List[Dict[str, Any]] = []
        for oid, o in self._map.items():
            if not getattr(o, "confirmed", False):
                continue
            if getattr(o, "label_user", None) is not None:
                continue  # treasured; never auto-evict
            raw_cls = getattr(o, "movability_class", None)
            eff_cls = (raw_cls if raw_cls in self._VALID_MOVABILITY
                       else self._EVICTION_FALLBACK_CLASS)
            ttl = self._eviction_ttl_s(eff_cls)
            if ttl is None:
                continue  # infinite TTL
            ls = float(getattr(o, "last_seen_wall_utc", 0.0) or 0.0)
            if ls <= 0.0:
                continue  # unknown last-seen; never evict on absence of data
            age = now_wall - ls
            if age > ttl:
                out.append({
                    "oid": oid,
                    "movability_class": eff_cls,
                    "movability_class_raw": raw_cls,
                    "age_s": round(age, 3),
                    "ttl_s": ttl,
                    "label": (getattr(o, "label_user", None)
                              or getattr(o, "label_primary", None)),
                })
        out.sort(key=lambda d: d["age_s"], reverse=True)
        return out

    def select_evictable(self, now_wall: Optional[float] = None) -> List[Dict[str, Any]]:
        """Pure inspector: which confirmed objects WOULD Tier-2 eviction take?

        No mutation; ignores the enabled flag (always reports). For a dry-run
        curl / UI before arming the sweep. Sorted most-stale first.
        """
        if now_wall is None:
            now_wall = _now_wall_utc()
        with self._lock:
            return self._compute_evictable_locked(now_wall)

    def evict_stale(
        self,
        now_wall: Optional[float] = None,
        *,
        dry_run: Optional[bool] = None,
        ghost_sink: Optional[Callable[[str, "ObjectState"], None]] = None,
    ) -> Dict[str, Any]:
        """Tier-2 sweep: evict confirmed objects past their class TTL.

        DISABLED by default (cfg["eviction"]["enabled"] = False) -> no-op.
        dry_run (arg overrides cfg["eviction"]["dry_run"], default False):
            report candidates without mutating.
        ghost_sink: optional callable(oid, ObjectState) invoked BEFORE removal
            -- the forward-compat hook for the Phase-2 ghost-log/re-id buffer.

        Mirrors expire_timeouts() for removal (frame-index cleanup, del from
        _map, index.remove). Returns a telemetry dict.
        """
        evic_cfg = self.cfg.get("eviction", {}) or {}
        enabled = bool(evic_cfg.get("enabled", False))
        if dry_run is None:
            dry_run = bool(evic_cfg.get("dry_run", False))
        if now_wall is None:
            now_wall = _now_wall_utc()

        result: Dict[str, Any] = {
            "enabled": enabled,
            "dry_run": bool(dry_run),
            "ts_wall": now_wall,
            "scanned": 0,
            "evicted": [],
            "by_class": {},
        }
        if not enabled:
            return result  # safe no-op until explicitly armed

        removed: List[str] = []
        with self._lock:
            result["scanned"] = sum(
                1 for o in self._map.values() if getattr(o, "confirmed", False)
            )
            candidates = self._compute_evictable_locked(now_wall)
            result["evicted"] = candidates
            for c in candidates:
                cls = c["movability_class"]
                result["by_class"][cls] = result["by_class"].get(cls, 0) + 1
            if dry_run:
                return result
            for c in candidates:
                oid = c["oid"]
                o = self._map.get(oid)
                if o is None:
                    continue
                # Defensive re-check of the hard invariant under the same lock.
                if getattr(o, "label_user", None) is not None:
                    continue
                if ghost_sink is not None:
                    try:
                        ghost_sink(oid, o)
                    except Exception:
                        logger.exception("eviction ghost_sink failed for %s", oid)
                # frame -> objects reverse index cleanup (mirrors expire_timeouts)
                fid = getattr(o, "last_update_frame_id", None)
                if fid is not None:
                    fset = self._frame_to_objects.get(fid)
                    if fset is not None:
                        fset.discard(oid)
                        if not fset:
                            del self._frame_to_objects[fid]
                del self._map[oid]
                removed.append(oid)
        if self.index is not None:
            for oid in removed:
                try:
                    self.index.remove(oid, None)
                except Exception:
                    logger.exception("eviction index.remove failed for %s", oid)
        return result

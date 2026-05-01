from __future__ import annotations

import os
from typing import Any, Dict, Iterable, List, Optional, Tuple

import numpy as np
import faiss

class FaissClient:
    """
    Minimal FAISS-backed vector store for MVP.

    Interface mirrors expected methods used by the pipeline's LTM hook:
    - upsert_batch(records)
    - search(emb, top_k)
    - delete(ids)
    - save(path)
    - load(path)
    - close()

    Records are dicts produced by WorkingMemory.collect_ready_for_upsert():
        {
            "object_id": str,
            "emb": np.ndarray (float32, L2-normalized),
            ... other metadata we keep in a side map ...
        }

    Notes:
    - Uses IndexFlatIP over L2-normalized embeddings => cosine similarity == inner product.
    - Maintains an in-memory ID→row mapping and arrays; rebuild is O(N) on upsert.
      This is acceptable for MVP scale. Optimize later with IDMap or IVF if needed.
    """

    def __init__(self, cfg: Dict[str, Any]):
        if faiss is None:
            raise ImportError(
                "faiss is not installed. Please install faiss-cpu for MVP usage."
            )
        vcfg = cfg.get("vectors", {})
        self.enabled: bool = bool(vcfg.get("enable", True))
        self.dim: int = int(vcfg.get("dim", 512))
        self.persistent_path: Optional[str] = vcfg.get("faiss", {}).get("index_path")
        self._index: Optional[Any] = None
        self._id_to_row: Dict[str, int] = {}
        self._row_to_id: List[str] = []
        self._metadata: Dict[str, Dict[str, Any]] = {}
        self._embeddings: Dict[str, np.ndarray] = {}

        # eager load if path exists
        if self.persistent_path and os.path.exists(self.persistent_path):
            self.load(self.persistent_path)
        else:
            self._ensure_index()

    # ---------- public API ----------
    def upsert_batch(self, records: Iterable[Dict[str, Any]]) -> None:
        """Insert or update vectors by object_id. Rebuilds the FAISS index.
        Accepts an iterable of payload dicts as produced by WorkingMemory.
        """
        to_add: List[Tuple[str, np.ndarray, Dict[str, Any]]] = []
        for rec in records:
            oid = str(rec["object_id"])  # required
            emb = np.asarray(rec["emb"], dtype=np.float32)
            if emb.ndim != 1:
                emb = emb.reshape(-1)
            if emb.shape[0] != self.dim:
                raise ValueError(f"Embedding dim {emb.shape[0]} != configured dim {self.dim}")
            # Store normalized inputs (should already be L2-normalized)
            n = float(np.linalg.norm(emb) + 1e-12)
            emb = (emb / n).astype(np.float32)
            meta = {k: v for k, v in rec.items() if k not in ("emb",)}
            to_add.append((oid, emb, meta))

        # --- PATCH P1 20260501: semantic-spatial dedup ---
        # Prevent the same real-world object (same primary label at same 10cm
        # grid cell) from accumulating duplicate OIDs across re-ingests.
        # Incoming records win; pre-existing OIDs with matching identity are evicted.
        def _identity_key(m):
            xyz = m.get("xyz")
            label = m.get("label_primary")
            if xyz is None or label is None:
                return None
            try:
                coords = tuple(round(float(c), 1) for c in xyz)  # 10cm grid
            except (TypeError, ValueError):
                return None
            return (label, coords)

        _incoming_keys = set()
        for _oid, _emb, _meta in to_add:
            k = _identity_key(_meta)
            if k is not None:
                _incoming_keys.add(k)

        if _incoming_keys:
            _incoming_oids = {oid for oid, _, _ in to_add}
            _evict = [
                eoid for eoid, emeta in self._metadata.items()
                if eoid not in _incoming_oids
                and _identity_key(emeta) in _incoming_keys
            ]
            for eoid in _evict:
                self._metadata.pop(eoid, None)
                self._embeddings.pop(eoid, None)
            if _evict:
                print(f"[FAISS] P1 dedup: evicted {len(_evict)} stale OIDs "
                      f"superseded by {len(_incoming_keys)} incoming identities")
        # --- END PATCH P1 ---

        # Merge/update metadata and materialize dense arrays
        for oid, emb, meta in to_add:
            self._metadata[oid] = meta
            self._embeddings[oid] = emb

        # Rebuild arrays from shadow stores
        ids_sorted = sorted(self._embeddings.keys())  # deterministic rebuild
        embs = np.zeros((len(ids_sorted), self.dim), dtype=np.float32)
        for row, oid in enumerate(ids_sorted):
            embs[row] = self._embeddings[oid]

        self._row_to_id = ids_sorted
        self._id_to_row = {oid: i for i, oid in enumerate(ids_sorted)}

        self._ensure_index()
        assert self._index is not None
        self._index.reset()
        if len(embs) > 0:
            self._index.add(embs)

        # auto-save if configured
        if self.persistent_path:
            try:
                self.save(self.persistent_path)
            except Exception:
                pass

    def search(self, emb: np.ndarray, top_k: int = 5) -> List[Tuple[str, float]]:
        """Return top_k (object_id, score) by inner product (cosine)"""
        if self._index is None or len(self._row_to_id) == 0:
            return []
        q = np.asarray(emb, dtype=np.float32).reshape(1, -1)
        if q.shape[1] != self.dim:
            raise ValueError(f"Query dim {q.shape[1]} != configured dim {self.dim}")
        # normalize to keep cosine semantics
        n = float(np.linalg.norm(q) + 1e-12)
        q = (q / n).astype(np.float32)
        D, I = self._index.search(q, min(top_k, len(self._row_to_id)))
        out: List[Tuple[str, float]] = []
        for d, i in zip(D[0].tolist(), I[0].tolist()):
            if i == -1:
                continue
            out.append((self._row_to_id[int(i)], float(d)))
        return out

    def delete(self, ids: Iterable[str]) -> None:
        """Remove ids and rebuild index."""
        id_set = set(str(x) for x in ids)
        for oid in list(self._metadata.keys()):
            if oid in id_set:
                del self._metadata[oid]
        for oid in list(self._embeddings.keys()):
            if oid in id_set:
                del self._embeddings[oid]
        ids_sorted = sorted(self._embeddings.keys())
        self._row_to_id = ids_sorted
        self._id_to_row = {oid: i for i, oid in enumerate(ids_sorted)}
        self._ensure_index()
        self._index.reset()
        if ids_sorted:
            # require caller to upsert with embeddings later; empty index for now
            pass
        if self.persistent_path:
            try:
                self.save(self.persistent_path)
            except Exception:
                pass

    def save(self, path: str) -> None:
        if self._index is None:
            self._ensure_index()
        # Persist both index and id list
        faiss.write_index(self._index, path)
        with open(path + ".ids", "w", encoding="utf-8") as f:
            for oid in self._row_to_id:
                f.write(oid + "\n")
        # Persist embeddings aligned with ids list
        if self._row_to_id:
            embs = np.vstack([self._embeddings[oid] for oid in self._row_to_id]).astype(np.float32)
            np.save(path + ".embs.npy", embs)
        # Persist metadata sidecar (ndarray-safe).  Added for cross-restart
        # metadata recovery so semantic search can enrich results after the
        # rtsm process is killed and a fresh one loads the index from disk.
        import json as _json
        meta_out = {}
        for oid, meta in self._metadata.items():
            clean = {}
            for k, v in meta.items():
                if isinstance(v, np.ndarray):
                    clean[k] = v.tolist()
                elif isinstance(v, (np.integer, np.floating)):
                    clean[k] = v.item()
                else:
                    clean[k] = v
            meta_out[oid] = clean
        tmp_path = path + ".meta.json.tmp"
        with open(tmp_path, "w", encoding="utf-8") as f:
            _json.dump(meta_out, f)
        os.replace(tmp_path, path + ".meta.json")

    def load(self, path: str) -> None:
        if not os.path.exists(path):
            raise FileNotFoundError(path)
        self._index = faiss.read_index(path)
        ids_path = path + ".ids"
        self._row_to_id = []
        if os.path.exists(ids_path):
            with open(ids_path, "r", encoding="utf-8") as f:
                self._row_to_id = [line.strip() for line in f if line.strip()]
        self._id_to_row = {oid: i for i, oid in enumerate(self._row_to_id)}
        # Load embeddings shadow store if present
        embs_path = path + ".embs.npy"
        self._embeddings = {}
        if self._row_to_id and os.path.exists(embs_path):
            embs = np.load(embs_path).astype(np.float32)
            for oid, vec in zip(self._row_to_id, embs):
                self._embeddings[oid] = vec
        # Load metadata sidecar if present.  Absent on legacy indexes (pre-fix);
        # _metadata stays empty and semantic search falls back gracefully.
        meta_path = path + ".meta.json"
        self._metadata = {}
        if os.path.exists(meta_path):
            import json as _json
            try:
                with open(meta_path, "r", encoding="utf-8") as f:
                    raw = _json.load(f)
                for oid, meta in raw.items():
                    restored = dict(meta)
                    xyz = restored.get("xyz")
                    if isinstance(xyz, list):
                        restored["xyz"] = np.asarray(xyz, dtype=np.float32)
                    self._metadata[oid] = restored
            except Exception:
                # corrupt sidecar should not break load; callers fall back to WM
                self._metadata = {}

    def get_metadata(self, oid: str):
        """Return the stored metadata dict for oid, or None if unknown.

        Used by the REST API to enrich semantic-search results when the
        corresponding WorkingMemory entry has been lost (e.g. across
        process restart).
        """
        return self._metadata.get(oid)

    def close(self) -> None:
        self._index = None

    # ---------- helpers ----------
    def _ensure_index(self) -> None:
        if self._index is None:
            self._index = faiss.IndexFlatIP(self.dim)



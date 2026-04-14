#!/usr/bin/env python3
"""
Semantic Search Quality Evaluator — RTSM
=========================================
Fetches all confirmed objects with embeddings from the RTSM API,
then evaluates semantic search quality using local CLIP text encoding.
This bypasses FAISS flush timing issues by searching against ALL
confirmed objects in working memory.

Usage:
    # Baseline (raw queries)
    python scripts/eval_semantic_search.py

    # Compare all prompt templates
    python scripts/eval_semantic_search.py --compare-templates

    # Save results
    python scripts/eval_semantic_search.py --save reports/semantic_eval.json
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

API_PORT = 8002
API_BASE = f"http://127.0.0.1:{API_PORT}"

# Target objects expected in session1
TARGETS = ["TV", "pillow", "doll", "air conditioner", "speaker", "laptop"]

# Ground truth: target -> list of known OIDs from visual inspection of session1
# This supplements label-based matching for objects whose CLIP labels are wrong.
GROUND_TRUTH_OIDS = {
    "TV": ["ec98dcd3"],                                 # monitor (labeled "monitor")
    "pillow": ["647d95bb"],                             # pillow (correct label)
    "doll": [],                                         # not detected in this recording
    "air conditioner": ["7c219266"],                    # portable air conditioner (correct label)
    "speaker": ["4905c564"],                            # speaker (correct label)
    "laptop": ["ce2c9ea8", "03d98675"],                 # laptop + tablet (both are laptop variants)
}

# Prompt templates to compare
TEMPLATES = {
    "raw": "{}",
    "a_photo_of": "a photo of a {}",
    "cropped_photo": "a cropped photo of a {}",
    "closeup_photo": "a close-up photo of a {}",
    "indoor_photo": "an indoor photo of a {}",
}


# ─────── API helpers ───────

def api_get(path: str) -> Optional[Dict[str, Any]]:
    try:
        url = f"{API_BASE}{path}"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read())
    except Exception as e:
        print(f"  API error on {path}: {e}")
        return None


def fetch_objects_with_vectors() -> List[Dict]:
    """Fetch all confirmed objects with their CLIP embeddings."""
    data = api_get("/objects?include_vectors=true&confirmed_only=true&limit=500")
    if not data or "objects" not in data:
        return []
    objs = []
    for o in data["objects"]:
        emb = o.get("emb_mean")
        if emb is not None:
            o["_emb"] = np.array(emb, dtype=np.float32)
            objs.append(o)
    return objs


def fetch_all_objects() -> List[Dict]:
    """Fetch all objects (confirmed + proto) for inventory."""
    data = api_get("/objects?confirmed_only=false&limit=500")
    if not data or "objects" not in data:
        return []
    return data["objects"]


# ─────── CLIP text encoding ───────

_clip_adapter = None

def get_clip_adapter():
    global _clip_adapter
    if _clip_adapter is None:
        from rtsm.cfg import load_config
        cfg = load_config("rtsm.yaml")
        clip_cfg = cfg.get("clip", {})
        model_name = clip_cfg.get("model", "ViT-B-32")
        pretrained = clip_cfg.get("pretrained", "openai")
        print(f"Loading CLIP model for text encoding: {model_name} ({pretrained})...")
        from rtsm.models.clip.adapter import CLIPAdapter
        _clip_adapter = CLIPAdapter(model_name=model_name, pretrained=pretrained, device="cuda")
        print("CLIP loaded.")
    return _clip_adapter


def encode_text(text: str) -> np.ndarray:
    """Encode text with CLIP and return L2-normalized embedding."""
    adapter = get_clip_adapter()
    return adapter.encode_text(text)


# ─────── WM-direct search ───────

def search_wm_direct(query_emb: np.ndarray, objects: List[Dict], top_k: int = 10) -> List[Dict]:
    """Compute cosine similarity against all WM object embeddings."""
    if not objects:
        return []

    # Build matrix of object embeddings
    embs = np.stack([o["_emb"] for o in objects])  # [N, D]
    # Normalize query
    q = query_emb / (np.linalg.norm(query_emb) + 1e-12)
    # Normalize embeddings
    norms = np.linalg.norm(embs, axis=1, keepdims=True)
    embs_normed = embs / np.maximum(norms, 1e-12)
    # Cosine similarity
    scores = embs_normed @ q  # [N]

    # Sort by score descending
    indices = np.argsort(-scores)[:top_k]
    results = []
    for idx in indices:
        o = objects[idx]
        results.append({
            "id": o["id"],
            "score": round(float(scores[idx]), 4),
            "label": o.get("label_primary"),
            "hits": o.get("hits", 0),
            "stability": o.get("stability", 0),
        })
    return results


# ─────── Evaluation ───────

def find_target_rank(results: List[Dict], target: str) -> Tuple[Optional[int], Optional[str]]:
    """Find which result matches the target query.

    Uses ground truth OID mapping first (from visual inspection),
    then falls back to label-based matching.
    """
    # 1. Ground truth OID matching (highest priority)
    gt_oids = GROUND_TRUTH_OIDS.get(target, [])
    for i, r in enumerate(results):
        oid = r["id"]
        for gt_oid in gt_oids:
            if oid.startswith(gt_oid):
                return (i + 1, oid)

    # 2. Label-based fallback
    target_lower = target.lower()
    for i, r in enumerate(results):
        label = (r.get("label") or "").lower()
        if target_lower in label or label in target_lower:
            return (i + 1, r["id"])
        if target_lower == "tv" and ("television" in label or "tv" in label or "monitor" in label):
            return (i + 1, r["id"])
        if target_lower == "laptop" and ("laptop" in label or "computer" in label):
            return (i + 1, r["id"])
        if target_lower == "air conditioner" and ("air" in label or "conditioner" in label):
            return (i + 1, r["id"])
        if target_lower == "speaker" and ("speaker" in label or "audio" in label):
            return (i + 1, r["id"])
        if target_lower == "doll" and ("doll" in label or "figurine" in label or "toy" in label or "cushion" in label):
            return (i + 1, r["id"])

    return (None, None)


def eval_single_template(template_name: str, template: str,
                          objects_with_emb: List[Dict], top_k: int = 10) -> Dict:
    """Run evaluation for a single prompt template."""
    results = {}
    for target in TARGETS:
        query = template.format(target)
        query_emb = encode_text(query)
        search_results = search_wm_direct(query_emb, objects_with_emb, top_k=top_k)

        rank, matched_oid = find_target_rank(search_results, target)

        scores = [r["score"] for r in search_results]
        target_score = None
        if rank is not None and rank <= len(scores):
            target_score = scores[rank - 1]

        results[target] = {
            "query": query,
            "rank": rank,
            "matched_oid": matched_oid,
            "target_score": target_score,
            "top1_score": scores[0] if scores else None,
            "top1_label": search_results[0]["label"] if search_results else None,
            "top1_oid": search_results[0]["id"] if search_results else None,
            "score_spread": round(scores[0] - scores[-1], 4) if len(scores) >= 2 else 0,
            "score_margin_1_2": round(scores[0] - scores[1], 4) if len(scores) >= 2 else 0,
            "num_results": len(search_results),
            "all_results": [
                {"rank": i+1, "oid": r["id"], "score": r["score"], "label": r["label"]}
                for i, r in enumerate(search_results[:5])
            ],
        }

    return {
        "template_name": template_name,
        "template": template,
        "targets": results,
        "summary": _compute_summary(results),
    }


def _compute_summary(results: Dict) -> Dict:
    ranks = []
    in_top1 = 0
    in_top3 = 0
    found = 0
    target_scores = []

    for target, data in results.items():
        if "error" in data:
            continue
        rank = data.get("rank")
        if rank is not None:
            found += 1
            ranks.append(rank)
            target_scores.append(data["target_score"])
            if rank == 1:
                in_top1 += 1
            if rank <= 3:
                in_top3 += 1

    total = len(TARGETS)
    return {
        "found": found,
        "total": total,
        "in_top1": in_top1,
        "in_top3": in_top3,
        "mean_rank": round(sum(ranks) / len(ranks), 2) if ranks else None,
        "mean_target_score": round(sum(target_scores) / len(target_scores), 4) if target_scores else None,
        "top1_rate": f"{in_top1}/{total}",
        "top3_rate": f"{in_top3}/{total}",
    }


# ─────── Printing ───────

def print_results_table(eval_result: Dict):
    tpl = eval_result["template_name"]
    template = eval_result["template"]
    print(f"\n### Template: `{tpl}` — `{template}`\n")
    print(f"| Target | Query | Rank | Score | Top-1 Label | Top-1 Score | Spread | Margin |")
    print(f"|--------|-------|------|-------|-------------|-------------|--------|--------|")

    for target in TARGETS:
        data = eval_result["targets"].get(target, {})
        if "error" in data:
            print(f"| {target} | — | ERROR | — | — | — | — | — |")
            continue

        query = data["query"]
        rank = data["rank"]
        rank_str = str(rank) if rank else "NOT FOUND"
        score = f"{data['target_score']:.4f}" if data["target_score"] else "—"
        top1_label = data["top1_label"] or "?"
        top1_score = f"{data['top1_score']:.4f}" if data["top1_score"] else "—"
        spread = f"{data['score_spread']:.4f}"
        margin = f"{data['score_margin_1_2']:.4f}"

        print(f"| {target} | {query} | {rank_str} | {score} | {top1_label} | {top1_score} | {spread} | {margin} |")

    s = eval_result["summary"]
    print(f"\n**Summary:** Found {s['found']}/{s['total']} | "
          f"Top-1: {s['top1_rate']} | Top-3: {s['top3_rate']} | "
          f"Mean rank: {s['mean_rank']} | Mean score: {s['mean_target_score']}")


def print_top5_detail(eval_result: Dict):
    print(f"\n#### Top-5 Detail for `{eval_result['template_name']}`\n")
    for target in TARGETS:
        data = eval_result["targets"].get(target, {})
        if "error" in data:
            continue
        print(f"**{target}** (query: `{data['query']}`):")
        for r in data.get("all_results", []):
            marker = " <-- TARGET" if data.get("matched_oid") == r["oid"] else ""
            print(f"  #{r['rank']} [{r['score']:.4f}] {r['label'] or '?'} ({r['oid'][:8]}){marker}")
        if data["rank"] is None:
            print(f"  TARGET NOT FOUND in top results")
        print()


def print_comparison_table(all_results: List[Dict]):
    print(f"\n## Template Comparison Summary\n")
    print(f"| Template | Found | Top-1 | Top-3 | Mean Rank | Mean Score |")
    print(f"|----------|-------|-------|-------|-----------|------------|")
    for res in all_results:
        s = res["summary"]
        name = res["template_name"]
        mean_rank = f"{s['mean_rank']:.2f}" if s['mean_rank'] else "—"
        mean_score = f"{s['mean_target_score']:.4f}" if s['mean_target_score'] else "—"
        print(f"| {name} | {s['found']}/{s['total']} | {s['top1_rate']} | {s['top3_rate']} | {mean_rank} | {mean_score} |")

    # Per-target rank comparison
    print(f"\n### Per-Target Rank by Template\n")
    header = "| Target |" + "|".join(f" {r['template_name']} " for r in all_results) + "|"
    sep = "|--------|" + "|".join("-------" for _ in all_results) + "|"
    print(header)
    print(sep)
    for target in TARGETS:
        row = f"| {target} |"
        for res in all_results:
            data = res["targets"].get(target, {})
            rank = data.get("rank")
            row += f" {rank if rank else '—'} |"
        print(row)


# ─────── Main ───────

def main():
    parser = argparse.ArgumentParser(description="RTSM Semantic Search Evaluator")
    parser.add_argument("--template", type=str, default=None,
                        help='Prompt template, e.g. "a photo of a {}"')
    parser.add_argument("--template-name", type=str, default=None,
                        help="Name for the template (for reports)")
    parser.add_argument("--compare-templates", action="store_true",
                        help="Compare all built-in templates")
    parser.add_argument("--top-k", type=int, default=10,
                        help="Top-K results per query")
    parser.add_argument("--save", type=str, default=None,
                        help="Save results to JSON file")
    parser.add_argument("--detail", action="store_true",
                        help="Print top-5 detail for each target")
    parser.add_argument("--api-port", type=int, default=8002,
                        help="API port (default 8002)")
    args = parser.parse_args()

    global API_BASE
    API_BASE = f"http://127.0.0.1:{args.api_port}"

    # Check API is up
    health = api_get("/healthz")
    if health is None:
        print(f"ERROR: RTSM API not reachable at {API_BASE}")
        print("Start RTSM first: rtsm --replay recordings/session1")
        sys.exit(1)

    # Fetch all objects for inventory
    all_objects = fetch_all_objects()
    confirmed = [o for o in all_objects if o.get("confirmed")]

    # Fetch confirmed objects WITH embeddings for direct WM search
    objects_with_emb = fetch_objects_with_vectors()

    print(f"# RTSM Semantic Search Evaluation")
    print(f"**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"**API:** {API_BASE}")
    print(f"**Objects:** {len(all_objects)} total, {len(confirmed)} confirmed, {len(objects_with_emb)} with embeddings")
    print(f"**Targets:** {', '.join(TARGETS)}")
    print(f"**Mode:** Direct WM search (bypasses FAISS)")

    if not objects_with_emb:
        print("\nERROR: No confirmed objects with embeddings found!")
        sys.exit(1)

    # Print object inventory
    print(f"\n## Object Inventory ({len(objects_with_emb)} with embeddings)\n")
    print(f"| ID (short) | Label | Hits | Stability | View Bins |")
    print(f"|------------|-------|------|-----------|-----------|")
    for o in sorted(objects_with_emb, key=lambda x: x.get("hits", 0), reverse=True):
        oid = o.get("id", "?")[:8]
        label = o.get("label_primary") or "?"
        hits = o.get("hits", 0)
        stab = o.get("stability", 0)
        vb = o.get("view_bins", 0)
        print(f"| {oid} | {label} | {hits} | {stab:.3f} | {vb} |")

    # Load CLIP for text encoding
    get_clip_adapter()

    all_eval_results = []

    if args.compare_templates:
        for name, tpl in TEMPLATES.items():
            result = eval_single_template(name, tpl, objects_with_emb, top_k=args.top_k)
            all_eval_results.append(result)
            print_results_table(result)
            if args.detail:
                print_top5_detail(result)
        print_comparison_table(all_eval_results)
    else:
        if args.template:
            tpl_name = args.template_name or "custom"
            tpl = args.template
        else:
            tpl_name = "raw"
            tpl = "{}"

        result = eval_single_template(tpl_name, tpl, objects_with_emb, top_k=args.top_k)
        all_eval_results.append(result)
        print_results_table(result)
        if args.detail:
            print_top5_detail(result)

    # Save results
    if args.save:
        save_path = Path(args.save)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        save_data = {
            "timestamp": datetime.now().isoformat(),
            "api_base": API_BASE,
            "objects_total": len(all_objects),
            "objects_confirmed": len(confirmed),
            "objects_with_embeddings": len(objects_with_emb),
            "targets": TARGETS,
            "evaluations": all_eval_results,
        }
        with open(save_path, "w") as f:
            json.dump(save_data, f, indent=2)
        print(f"\nResults saved to: {save_path}")


if __name__ == "__main__":
    main()

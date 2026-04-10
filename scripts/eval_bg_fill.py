#!/usr/bin/env python3
"""
Background Fill Comparison — RTSM Semantic Search
===================================================
Runs the pipeline with different bg_fill settings and compares
semantic search quality using the eval harness.

Usage:
    python scripts/eval_bg_fill.py
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / "rtsm" / "cfg" / "rtsm.yaml"
RECORDING = ROOT / "recordings" / "session1"
REPORT_DIR = ROOT / "reports"

API_PORT = 8002
FILLS = ["mean", "white", "black", "blur"]


def api_get(path: str):
    try:
        url = f"http://127.0.0.1:{API_PORT}{path}"
        with urllib.request.urlopen(url, timeout=10) as resp:
            return json.loads(resp.read())
    except Exception:
        return None


def wait_for_api(timeout=180):
    t0 = time.monotonic()
    while time.monotonic() - t0 < timeout:
        if api_get("/healthz") is not None:
            return True
        time.sleep(2)
    return False


def patch_bg_fill(fill: str):
    with open(CONFIG_PATH) as f:
        cfg = yaml.safe_load(f)
    cfg["staging"]["bg_fill"] = fill
    with open(CONFIG_PATH, "w") as f:
        yaml.dump(cfg, f, default_flow_style=False, sort_keys=False)


def run_one_fill(fill: str) -> dict:
    print(f"\n{'='*50}")
    print(f"  Testing bg_fill: {fill}")
    print(f"{'='*50}")

    # Patch config
    patch_bg_fill(fill)

    # Clear pycache
    for p in ROOT.rglob("__pycache__"):
        for pyc in p.glob("*.pyc"):
            pyc.unlink()

    # Start pipeline
    log_path = REPORT_DIR / f"bg_fill_{fill}.log"
    REPORT_DIR.mkdir(exist_ok=True)
    log_f = open(log_path, "w")
    proc = subprocess.Popen(
        [sys.executable, "-u", "-m", "rtsm", "--replay", str(RECORDING), "--replay-speed", "0.5"],
        cwd=str(ROOT),
        stdout=log_f,
        stderr=subprocess.STDOUT,
        env={**os.environ, "PYTHONUNBUFFERED": "1"},
    )
    print(f"  PID: {proc.pid}")

    try:
        if not wait_for_api(timeout=300):
            print("  ERROR: API timeout")
            proc.kill()
            return {"fill": fill, "error": "API timeout"}

        # Wait for replay to complete
        for _ in range(60):
            time.sleep(5)
            log_f.flush()
            try:
                with open(log_path) as lf:
                    if "[replay] Complete" in lf.read():
                        break
            except Exception:
                pass
        else:
            print("  WARNING: Replay didn't complete in time")

        # Drain
        time.sleep(20)

        # Run eval
        print(f"  Running eval...")
        eval_result = subprocess.run(
            [sys.executable, "scripts/eval_semantic_search.py",
             "--compare-templates",
             "--save", str(REPORT_DIR / f"semantic_eval_{fill}.json")],
            cwd=str(ROOT),
            capture_output=True, text=True, timeout=120
        )
        print(eval_result.stdout[-500:] if len(eval_result.stdout) > 500 else eval_result.stdout)

        # Load eval results
        eval_path = REPORT_DIR / f"semantic_eval_{fill}.json"
        if eval_path.exists():
            with open(eval_path) as f:
                return {"fill": fill, "eval": json.load(f)}
        return {"fill": fill, "error": "eval failed"}

    finally:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(5)
        log_f.close()
        time.sleep(5)


def main():
    print("RTSM Background Fill Comparison")
    print(f"Fills to test: {FILLS}")

    # Backup config
    import shutil
    backup = str(CONFIG_PATH) + ".bg_fill_bak"
    shutil.copy2(CONFIG_PATH, backup)

    all_results = []
    try:
        for fill in FILLS:
            result = run_one_fill(fill)
            all_results.append(result)
    finally:
        # Restore config
        shutil.copy2(backup, CONFIG_PATH)
        if os.path.exists(backup):
            os.remove(backup)

    # Summary
    print(f"\n{'='*60}")
    print(f"  COMPARISON SUMMARY")
    print(f"{'='*60}")
    print(f"\n| Fill | Template | Found | Top-1 | Top-3 | Mean Rank | Mean Score |")
    print(f"|------|----------|-------|-------|-------|-----------|------------|")

    for result in all_results:
        fill = result["fill"]
        if "error" in result:
            print(f"| {fill} | — | ERROR: {result['error']} | — | — | — | — |")
            continue
        evals = result["eval"].get("evaluations", [])
        for ev in evals:
            s = ev["summary"]
            name = ev["template_name"]
            mean_rank = f"{s['mean_rank']:.2f}" if s['mean_rank'] else "—"
            mean_score = f"{s['mean_target_score']:.4f}" if s['mean_target_score'] else "—"
            print(f"| {fill} | {name} | {s['found']}/{s['total']} | {s['top1_rate']} | {s['top3_rate']} | {mean_rank} | {mean_score} |")

    # Save combined results
    combined_path = REPORT_DIR / "bg_fill_comparison.json"
    with open(combined_path, "w") as f:
        json.dump(all_results, f, indent=2)
    print(f"\nCombined results saved to: {combined_path}")


if __name__ == "__main__":
    main()

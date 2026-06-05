"""In-process proof that PATCH /objects/{oid} works in SERVE mode with the
patched FrozenWorkingMemory -- and that server.py needed NO change.

Mirrors tests/test_object_patch.py but backs the app with FrozenWorkingMemory.
"""
from __future__ import annotations
import json, os, tempfile
from fastapi.testclient import TestClient
from prometheus_client import CollectorRegistry
from rtsm.stores.frozen_wm import FrozenWorkingMemory
from rtsm.api.server import create_app

results = []
def check(name, cond, detail=""):
    results.append(cond); print(f"  [{'PASS' if cond else 'FAIL'}] {name}" + (f"  -- {detail}" if detail else "")); assert cond, detail

print("=== test_serve_patch_inprocess.py (serve-mode PATCH) ===\n")
with tempfile.TemporaryDirectory() as tmp:
    meta = os.path.join(tmp, "idx.flatip.meta.json")
    with open(meta, "w") as f:
        json.dump({
            "obj1": {"object_id": "obj1", "xyz": [1, 2, 0.5], "label_primary": "duck",
                     "label_topk": ["duck"], "label_scores": [0.3], "stability": 0.9},
        }, f)

    fw = FrozenWorkingMemory(meta)
    check("0 serve_mode WM in use", fw.stats().get("serve_mode") is True)
    app = create_app(working_memory=fw, registry=CollectorRegistry())
    client = TestClient(app)

    print("[1] PATCH label_user no longer 405s; sets the name")
    r = client.patch("/objects/obj1",
                      content=json.dumps({"label_user": "Quackers"}),
                      headers={"Content-Type": "application/json"})
    check("1a status 200 (was 405)", r.status_code == 200, f"got {r.status_code} body={r.text[:200]}")
    check("1b label_user set", r.json().get("label_user") == "Quackers")
    check("1c display_label == label_user", r.json().get("display_label") == "Quackers")

    print("[2] GET reflects it")
    g = client.get("/objects/obj1")
    check("2a GET label_user", g.json().get("label_user") == "Quackers")

    print("[3] persisted to sidecar on disk")
    with open(meta) as f:
        disk = json.load(f)
    check("3a sidecar has label_user", disk["obj1"]["label_user"] == "Quackers")

    print("[4] invalid + clear still behave")
    r = client.patch("/objects/obj1", content=json.dumps({"movability_class": "NOPE"}),
                      headers={"Content-Type": "application/json"})
    check("4a invalid movability -> 400", r.status_code == 400, f"got {r.status_code}")
    r = client.patch("/objects/obj1", content=json.dumps({"label_user": None}),
                      headers={"Content-Type": "application/json"})
    check("4b clear -> 200, display_label falls back",
          r.status_code == 200 and r.json().get("display_label") == "duck",
          f"got {r.status_code} {r.json().get('display_label')!r}")

print(f"\n=== {sum(results)}/{len(results)} checks passed ===")

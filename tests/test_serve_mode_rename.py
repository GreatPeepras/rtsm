"""Serve-mode rename: read fix + write-through against a real meta sidecar.

frozen_wm only needs numpy + stdlib, so this runs fully offline.
Run:  cd /path/to/rtsm && python3 test_serve_mode_rename.py
"""
from __future__ import annotations
import json, os, tempfile
from rtsm.stores.frozen_wm import FrozenWorkingMemory

results = []
def check(name, cond, detail=""):
    results.append(cond); print(f"  [{'PASS' if cond else 'FAIL'}] {name}" + (f"  -- {detail}" if detail else "")); assert cond, detail

def write_sidecar(path, recs):
    with open(path, "w") as f:
        json.dump(recs, f)

def read_sidecar(path):
    with open(path) as f:
        return json.load(f)

print("=== test_serve_mode_rename.py ===\n")

with tempfile.TemporaryDirectory() as tmp:
    meta = os.path.join(tmp, "idx.flatip.meta.json")
    write_sidecar(meta, {
        "named": {   # already named during ingest
            "object_id": "named", "xyz": [1, 2, 0.5], "label_primary": "duck",
            "label_user": "Quackers", "display_label": "Quackers",
            "movability_class": "roaming", "label_topk": ["duck"],
            "label_scores": [0.3], "stability": 0.9,
        },
        "legacy": {  # no user fields at all (pre-feature sidecar)
            "object_id": "legacy", "xyz": [0, 0, 0], "label_primary": "rug",
            "label_topk": ["rug"], "label_scores": [0.5], "stability": 0.8,
        },
    })

    print("[1] READ fix: user fields restored from sidecar")
    fw = FrozenWorkingMemory(meta)
    n = fw.get("named"); l = fw.get("legacy")
    check("1a named.label_user read", n.label_user == "Quackers")
    check("1b named.display_label read", n.display_label == "Quackers")
    check("1c named.movability_class read", n.movability_class == "roaming")
    check("1d legacy.label_user is None", l.label_user is None)
    check("1e legacy.display_label falls back to label_primary",
          l.display_label == "rug", f"got {l.display_label!r}")

    print("\n[2] WRITE: set label_user -> in-memory + on-disk + display_label")
    o = fw.update_user_fields("legacy", label_user="Rug-of-Honor")
    check("2a returns updated object", o is not None and o.label_user == "Rug-of-Honor")
    check("2b display_label recomputed", o.display_label == "Rug-of-Honor")
    disk = read_sidecar(meta)
    check("2c persisted label_user to sidecar", disk["legacy"]["label_user"] == "Rug-of-Honor")
    check("2d persisted display_label to sidecar", disk["legacy"]["display_label"] == "Rug-of-Honor")

    print("\n[3] CLEAR: label_user=None -> display_label falls back, persisted")
    o = fw.update_user_fields("named", label_user=None)
    check("3a cleared in memory", o.label_user is None)
    check("3b display_label falls back to label_primary", o.display_label == "duck")
    check("3c persisted null to sidecar", read_sidecar(meta)["named"]["label_user"] is None)

    print("\n[4] movability_class write + validation")
    o = fw.update_user_fields("legacy", movability_class="static")
    check("4a movability set + persisted",
          o.movability_class == "static" and read_sidecar(meta)["legacy"]["movability_class"] == "static")
    try:
        fw.update_user_fields("legacy", movability_class="NOPE"); raised = False
    except ValueError: raised = True
    check("4b invalid movability_class -> ValueError", raised)

    print("\n[5] validation + unknown oid")
    try:
        fw.update_user_fields("named", label_user=""); raised = False
    except ValueError: raised = True
    check("5a empty label_user -> ValueError", raised)
    check("5b unknown oid -> None", fw.update_user_fields("ghost", label_user="x") is None)

    print("\n[6] DURABILITY: fresh FrozenWM (simulated restart) sees the rename")
    fw.update_user_fields("legacy", label_user="Persisted")
    fw2 = FrozenWorkingMemory(meta)   # re-loads from disk
    check("6a rename survived reload", fw2.get("legacy").label_user == "Persisted")
    check("6b display_label survived", fw2.get("legacy").display_label == "Persisted")

print(f"\n=== {sum(results)}/{len(results)} checks passed ===")

"""In-process FastAPI smoke test for PATCH /objects/{oid}.

V2: explicit Content-Type, fresh registry per app.
"""
from __future__ import annotations
import sys
import json as _json
from types import SimpleNamespace
from typing import Any

from fastapi.testclient import TestClient
from prometheus_client import CollectorRegistry

from rtsm.stores.working_memory import WorkingMemory
from rtsm.api.server import create_app


# ---------- helpers ----------

results: list[tuple[str, bool, str]] = []

def check(name: str, cond: bool, detail: str = "") -> None:
    results.append((name, cond, detail))
    mark = "PASS" if cond else "FAIL"
    print(f"  [{mark}] {name}" + (f"  -- {detail}" if detail else ""))
    assert cond, f"{name}: {detail}" if detail else name

def patch_json(client: TestClient, url: str, body: dict | None) -> Any:
    """PATCH with explicit Content-Type. Works across httpx versions."""
    return client.patch(
        url,
        content=_json.dumps(body if body is not None else {}),
        headers={"Content-Type": "application/json"},
    )

def make_obj(oid: str, label_primary: str = "chair") -> Any:
    return SimpleNamespace(
        id=oid,
        label_primary=label_primary,
        label_user=None,
        movability_class=None,
    )


# ---------- setup ----------

print("=== smoke_patch.py: PATCH /objects/{oid} (V2) ===\n")
print("[setup] Building fresh WorkingMemory + app...")

wm = WorkingMemory(cfg={})
oid_real = "smoketest00000001"
oid_real_2 = "smoketest00000002"
oid_missing = "doesnotexist0000"

with wm._lock:
    wm._map[oid_real] = make_obj(oid_real, label_primary="chair")
    wm._map[oid_real_2] = make_obj(oid_real_2, label_primary="table")

# Fresh registry to avoid global-state collisions on multi-app construction.
reg1 = CollectorRegistry()
app = create_app(working_memory=wm, registry=reg1)
client = TestClient(app)
print(f"[setup] WM has {len(wm._map)} stub objects\n")


# ---------- tests ----------

print("[1] GET /objects/{oid} returns PR fields")
r = client.get(f"/objects/{oid_real}")
check("1a status 200", r.status_code == 200, f"got {r.status_code}")
body = r.json() if r.status_code == 200 else {}
check("1b has label_user key", "label_user" in body)
check("1c has movability_class key", "movability_class" in body)
check("1d has display_label", "display_label" in body)
check("1e label_user starts None", body.get("label_user") is None)
check("1f movability_class starts None", body.get("movability_class") is None)
check("1g display_label falls back to label_primary",
      body.get("display_label") == "chair",
      f"got {body.get('display_label')!r}")


print("\n[2] PATCH label_user='Albert's mug' -> 200, set")
r = patch_json(client, f"/objects/{oid_real}", {"label_user": "Albert's mug"})
check("2a status 200", r.status_code == 200, f"got {r.status_code} body={r.text[:200]}")
check("2b label_user reflected",
      r.json().get("label_user") == "Albert's mug",
      f"got {r.json().get('label_user')!r}")


print("\n[3] GET after PATCH reflects override")
r = client.get(f"/objects/{oid_real}")
body = r.json()
check("3a label_user persisted", body.get("label_user") == "Albert's mug")
check("3b display_label == label_user",
      body.get("display_label") == "Albert's mug",
      f"got {body.get('display_label')!r}")


print("\n[4] PATCH movability_class='movable' -> 200, set")
r = patch_json(client, f"/objects/{oid_real}", {"movability_class": "movable"})
check("4a status 200", r.status_code == 200, f"got {r.status_code}")
check("4b movability_class set", r.json().get("movability_class") == "movable")


print("\n[5] PATCH movability_class='INVALID' -> 400")
r = patch_json(client, f"/objects/{oid_real}", {"movability_class": "INVALID"})
check("5a status 400", r.status_code == 400, f"got {r.status_code} body={r.text[:200]}")
check("5b error mentions movability_class", "movability_class" in r.text.lower())
r_check = client.get(f"/objects/{oid_real}")
check("5c state unchanged",
      r_check.json().get("movability_class") == "movable",
      f"got {r_check.json().get('movability_class')!r}")


print("\n[6] PATCH label_user=null -> 200, cleared")
r = patch_json(client, f"/objects/{oid_real}", {"label_user": None})
check("6a status 200", r.status_code == 200, f"got {r.status_code}")
check("6b label_user cleared", r.json().get("label_user") is None)
check("6c display_label falls back",
      r.json().get("display_label") == "chair",
      f"got {r.json().get('display_label')!r}")


print("\n[7] PATCH label_user='' -> 400")
r = patch_json(client, f"/objects/{oid_real}", {"label_user": ""})
check("7a status 400", r.status_code == 400, f"got {r.status_code} body={r.text[:200]}")
check("7b error mentions label_user", "label_user" in r.text.lower())


print("\n[8] PATCH nonexistent oid -> 404")
r = patch_json(client, f"/objects/{oid_missing}", {"label_user": "x"})
check("8a status 404", r.status_code == 404, f"got {r.status_code}")


print("\n[9] PATCH {} -> 200 no-op")
r = patch_json(client, f"/objects/{oid_real_2}", {})
check("9a status 200", r.status_code == 200, f"got {r.status_code}")
r_check = client.get(f"/objects/{oid_real_2}")
check("9b state untouched", r_check.json().get("label_user") is None)


print("\n[10] PATCH unknown field -> 422")
r = patch_json(client, f"/objects/{oid_real}", {"bogus_field": "x"})
check("10a status 422", r.status_code == 422, f"got {r.status_code}")


print("\n[11] PATCH on frozen WM -> 405")
class FrozenWM:
    def __init__(self, real_wm: WorkingMemory):
        self._real = real_wm
    def get(self, oid): return self._real.get(oid)
    def iter_objects(self): return self._real.iter_objects()
    def stats(self): return {}

frozen = FrozenWM(wm)
reg2 = CollectorRegistry()  # FRESH registry
app2 = create_app(working_memory=frozen, registry=reg2)
client2 = TestClient(app2)
r = patch_json(client2, f"/objects/{oid_real}", {"label_user": "x"})
check("11a status 405", r.status_code == 405, f"got {r.status_code} body={r.text[:200]}")
check("11b mentions frozen/not supported",
      any(s in r.text.lower() for s in ("frozen", "not supported", "serve-mode")))


# ---------- summary ----------

print("\n" + "=" * 60)
total = len(results)
passed = sum(1 for _, ok, _ in results if ok)
print(f"RESULT: {passed}/{total} passed")
if passed != total:
    print("\nFailed:")
    for n, ok, d in results:
        if not ok:
            print(f"  - {n}: {d}")
    sys.exit(1)
print("All assertions passed.")
sys.exit(0)


# ─── pytest entry point ─────────────────────────────────────────────
# This file is dual-mode:
#   - As a script:  `python3 tests/test_object_patch.py`
#                   Runs all assertions at module-import time, prints a
#                   PASS/FAIL summary, exits 0 on full pass.
#   - Under pytest: `pytest tests/test_object_patch.py -v`
#                   Module import runs the assertions; check() raises
#                   AssertionError on any failure, so pytest sees the
#                   failing line. test_patch_objects_smoke() exists to
#                   give pytest a discoverable test_* function.
#
# Pytest is not currently a declared project dependency (see pyproject.toml),
# but tests/test_serve_api.py uses pytest fixtures, so this file mirrors
# that convention.

def test_patch_objects_smoke():
    """PATCH /objects/{oid} end-to-end: 27 assertions covering the PR contract.

    All assertions execute at module import time via check(), which raises
    on failure. If you're reading this because the test failed, scroll up
    in pytest output for the AssertionError — its message names the failing
    assertion (e.g. "5a status 400  -- got 200").
    """
    failed = [(n, d) for (n, ok, d) in results if not ok]
    assert not failed, f"{len(failed)} assertion(s) failed: {failed}"

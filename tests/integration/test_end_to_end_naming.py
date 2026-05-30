"""End-to-end integration test for the B1 reference-snapshot pipeline.

Hits a LIVE RTSM server over HTTP. Designed to catch the four 5/29 bugs
that the unit-test suite missed because each required real runtime
(real CLIP adapter, real GPU, real FastAPI routing, real production
object shapes):

  Bug 2 (PIL.Image vs ndarray)    -> POST /reference exercises encode_image
  Bug 3 (CUDA tensor -> CPU)       -> POST /reference returns from GPU
  Bug 4 (xyz.tolist() on list)     -> GET /by_label_user serializes xyz
  Bug 7 (FastAPI route shadow)     -> GET /by_label_user must NOT be caught
                                      by /objects/{oid} (returns the not_found
                                      error envelope with id='by_label_user')

The test mutates a real WM object's label_user briefly, then restores it.
A unique time-based marker is used so concurrent test runs don't collide
and so the marker is easy to spot in logs.

Usage:
    # Against production RTSM on Execution Jetson:
    RTSM_URL=http://192.168.0.53:8002 python3 tests/integration/test_end_to_end_naming.py

    # Against a local dev server:
    python3 tests/integration/test_end_to_end_naming.py

Exit codes: 0 = pass, 1 = assertion failed, 2 = setup/connectivity error.
"""
import base64
import io
import os
import sys
import time

import requests
from PIL import Image


RTSM_URL = os.environ.get("RTSM_URL", "http://192.168.0.53:8002").rstrip("/")
TIMEOUT_S = float(os.environ.get("RTSM_TIMEOUT_S", "15.0"))
MARKER = f"__inttest_{int(time.time())}__"


def _fixture_jpeg_b64() -> str:
    """Synthesize a 224x224 solid-color JPEG and return base64-encoded bytes.

    Real bytes that decode to a real RGB image are required so the server's
    CLIP encode path actually runs (catches bugs 2 and 3). A solid color is
    fine -- CLIP doesn't reject low-information images.
    """
    img = Image.new("RGB", (224, 224), color=(120, 80, 200))
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=85)
    return base64.b64encode(buf.getvalue()).decode("ascii")


def _pick_test_object() -> tuple:
    """Find a confirmed WM object to test against. Returns (oid, original_label_user)."""
    r = requests.get(
        f"{RTSM_URL}/objects",
        params={"confirmed_only": "true", "pose_state": "any", "limit": 50},
        timeout=TIMEOUT_S,
    )
    r.raise_for_status()
    objs = r.json().get("objects", [])
    if not objs:
        raise RuntimeError(
            f"No confirmed objects in RTSM at {RTSM_URL}. "
            f"Create one (e.g. have Albert look at something) and retry."
        )
    o = objs[0]
    return o["id"], o.get("label_user")


def main() -> int:
    print(f"[*] RTSM = {RTSM_URL}")
    print(f"[*] marker = {MARKER}")

    try:
        oid, original_label_user = _pick_test_object()
    except Exception as e:
        print(f"[!] setup failed: {e}", file=sys.stderr)
        return 2
    print(f"[*] testing against oid={oid[:8]} (original label_user={original_label_user!r})")

    try:
        # --- Step 1: pin the marker label_user via PATCH ---
        r = requests.patch(
            f"{RTSM_URL}/objects/{oid}",
            json={"label_user": MARKER},
            timeout=TIMEOUT_S,
        )
        r.raise_for_status()
        print(f"[1] PATCH label_user={MARKER!r}: HTTP {r.status_code}")

        # --- Step 2: POST a real JPEG to /reference ---
        # Catches Bug 2 (PIL.Image vs ndarray) and Bug 3 (CUDA->CPU) by
        # exercising the live CLIP encode path. Either bug would surface
        # here as an HTTP 500 with a traceback in the body.
        r = requests.post(
            f"{RTSM_URL}/objects/{oid}/reference",
            json={"jpeg_b64": _fixture_jpeg_b64()},
            timeout=TIMEOUT_S,
        )
        assert r.ok, (
            f"POST /objects/{oid[:8]}/reference failed: "
            f"HTTP {r.status_code}: {r.text[:400]}"
        )
        print(f"[2] POST /reference: HTTP {r.status_code}")

        # --- Step 3: GET by_label_user, verify response ---
        # Response shape is {"primary": {...obj fields...}, possibly more}.
        # That wrapper is itself a useful bug-7 sentinel: the shadowed-route
        # response is {"error":"not_found", "id":"by_label_user"} (no
        # "primary" key) and the wrapped happy-path response has "primary".
        # Catches Bug 4 (xyz.tolist() on list): malformed shapes from the
        # FAISS sidecar deserialization would surface here either as HTTP
        # 500 or as a missing/wrong xyz_world field on the primary.
        r = requests.get(
            f"{RTSM_URL}/objects/by_label_user",
            params={"name": MARKER},
            timeout=TIMEOUT_S,
        )
        r.raise_for_status()
        body = r.json()

        # Bug 7 detector 1: shadowed-route response is {"error":..., "id":"by_label_user"}.
        assert "error" not in body, (
            f"GET /by_label_user returned an error envelope -- route may be "
            f"shadowed by /objects/{{oid}} (bug 7 regression): {body!r}"
        )
        # Bug 7 detector 2: real endpoint wraps the match in {"primary": {...}}.
        # If "primary" is absent, either we are shadowed OR the response shape
        # has changed -- both are worth surfacing loudly.
        primary = body.get("primary")
        assert primary is not None, (
            f"GET /by_label_user: 'primary' key missing -- response shape "
            f"unexpected (possible regression or shadow): {body!r}"
        )

        # Object identity: must be the object we just patched. Accept either
        # 'id' or 'oid' since the endpoint's _entry() builder differs from
        # _obj_summary's field naming.
        got_oid = primary.get("id") or primary.get("oid")
        assert got_oid == oid, (
            f"wrong oid in primary: got {got_oid!r}, expected {oid!r}; "
            f"full primary={primary!r}"
        )
        # Label propagation: the marker we patched must be readable back.
        assert primary.get("label_user") == MARKER, (
            f"label_user mismatch in primary: got {primary.get('label_user')!r}, "
            f"expected {MARKER!r}"
        )
        # Bug 4 detector: xyz_world must be a 3-element list, not a numpy
        # array or some other shape that would crash serialization.
        xyz = primary.get("xyz_world") or primary.get("xyz")
        assert isinstance(xyz, list) and len(xyz) == 3, (
            f"xyz_world malformed in primary (possible bug 4 regression): "
            f"{xyz!r}; full primary={primary!r}"
        )
        print(f"[3] GET /by_label_user: primary.id ok, label ok, xyz_world={xyz}")
        print(f"\nPASS  oid={oid[:8]}  marker={MARKER}")
        return 0

    except AssertionError as e:
        print(f"\nFAIL  {e}", file=sys.stderr)
        return 1

    finally:
        # 2026-05-30: clean up the reference image we POSTed in step 2.
        # Without this, every test run leaves a stray purple JPEG on disk
        # plus polluted reference_emb on the object (caught the hard way).
        try:
            r = requests.delete(
                f"{RTSM_URL}/objects/{oid}/reference",
                timeout=TIMEOUT_S,
            )
            print(f"[cleanup] DELETE /reference: HTTP {r.status_code}")
        except Exception as e:
            print(f"[cleanup] WARNING: failed to delete reference: {e}", file=sys.stderr)
        # Restore the original label_user. None -> clears it (which is
        # also fine if it was None to begin with). Best-effort: a restore
        # failure shouldn't mask the test outcome.
        try:
            r = requests.patch(
                f"{RTSM_URL}/objects/{oid}",
                json={"label_user": original_label_user},
                timeout=TIMEOUT_S,
            )
            print(f"[restore] label_user <- {original_label_user!r}: HTTP {r.status_code}")
        except Exception as e:
            print(f"[restore] WARNING: failed to restore label_user: {e}", file=sys.stderr)


if __name__ == "__main__":
    sys.exit(main())

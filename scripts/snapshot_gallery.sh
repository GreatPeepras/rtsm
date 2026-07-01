#!/usr/bin/env bash
# =============================================================================
# snapshot_gallery.sh
#
# Render all image_crops for one or more OIDs as a single self-contained
# HTML page. Strip layout: each OID gets its own section with up to ~10
# 160x160 thumbnails in a horizontal row.
#
# Use case: investigating anchors that might be mis-anchored — the latest
# snapshot alone doesn't tell you whether the whole gallery is consistent
# or whether one bad observation is polluting the canonical view.
#
# Usage:
#   ./snapshot_gallery.sh <oid1> [oid2 ...]
#   ./snapshot_gallery.sh --output review.html <oid1> [oid2 ...]
#
# Defaults: output = snapshot_gallery_<timestamp>.html
#
# Environment:
#   RTSM_BASE  Default http://localhost:8002
# =============================================================================

set -euo pipefail

RTSM_BASE="${RTSM_BASE:-http://localhost:8002}"
OUTPUT=""
OIDS=()

while [ $# -gt 0 ]; do
    case "$1" in
        --output) OUTPUT="$2"; shift 2 ;;
        --help|-h)
            sed -n '/^# Usage:/,/^# ===/p' "$0" | sed 's/^# //'
            exit 0 ;;
        -*)
            echo "Unknown flag: $1" >&2; exit 2 ;;
        *)
            OIDS+=("$1"); shift ;;
    esac
done

if [ ${#OIDS[@]} -eq 0 ]; then
    echo "Usage: $0 <oid1> [oid2 ...]" >&2
    echo "       Pass --help for details." >&2
    exit 2
fi

if [ -z "$OUTPUT" ]; then
    OUTPUT="snapshot_gallery_$(date +%Y%m%d_%H%M%S).html"
fi

# Pre-flight
if ! curl -s -o /dev/null -f "$RTSM_BASE/objects" 2>/dev/null; then
    printf "\033[31mFATAL: cannot reach RTSM at %s\033[0m\n" "$RTSM_BASE" >&2
    exit 1
fi

python3 - "$RTSM_BASE" "$OUTPUT" "${OIDS[@]}" <<'PYEOF'
import json
import sys
import html
import urllib.request
import urllib.error
from datetime import datetime

RTSM_BASE = sys.argv[1]
OUTPUT = sys.argv[2]
OIDS = sys.argv[3:]


def fetch_json(url, timeout=10):
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            return json.load(resp)
    except (urllib.error.URLError, urllib.error.HTTPError,
            json.JSONDecodeError, TimeoutError):
        return None


def esc(s):
    return html.escape(str(s) if s is not None else "")


now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

PLACEHOLDER = (
    "data:image/svg+xml;utf8,"
    "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 160 160'>"
    "<rect width='160' height='160' fill='%23222'/>"
    "<text x='80' y='80' fill='%23666' font-family='monospace' font-size='10' "
    "text-anchor='middle' dominant-baseline='middle'>no data</text></svg>"
)

CSS = """
body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", system-ui, sans-serif;
       background: #1a1a1a; color: #ddd; margin: 0; padding: 24px; }
h1 { font-size: 18px; color: #fff; margin: 0 0 4px 0; }
.meta { color: #888; font-size: 12px; margin-bottom: 24px; }
.oid-section { background: #252525; border: 1px solid #333; border-radius: 8px;
               padding: 16px; margin-bottom: 24px; }
.oid-header h2 { margin: 0 0 4px 0; font-size: 18px; color: #ffc857; }
.oid-header h2 .sub { color: #888; font-size: 13px; font-weight: 400; margin-left: 6px; }
.oid-header .meta-row { font-family: ui-monospace, "SF Mono", Menlo, monospace;
                         font-size: 11px; color: #888; margin-top: 4px;
                         word-break: break-all; }
.strip { display: flex; gap: 8px; flex-wrap: wrap; margin-top: 12px; }
.snap { background: #1a1a1a; border: 1px solid #333; border-radius: 4px;
        padding: 4px; }
.snap img { width: 160px; height: 160px; object-fit: cover; background: #000;
            border-radius: 3px; display: block; }
.snap .idx { color: #888; font-family: ui-monospace, monospace; font-size: 10px;
              margin-top: 2px; text-align: center; }
.error { color: #d97757; font-style: italic; }
.has-ref { color: #5fb878; font-weight: 600; }
.no-ref { color: #d97757; }
"""

parts = []
parts.append('<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">\n')
parts.append(f"<title>Snapshot Galleries &mdash; {esc(now)}</title>\n")
parts.append(f"<style>{CSS}</style></head><body>\n")
parts.append("<h1>Snapshot Galleries</h1>\n")
parts.append(
    f'<div class="meta">Generated {esc(now)} &middot; {len(OIDS)} OIDs '
    f'&middot; RTSM @ {esc(RTSM_BASE)}</div>\n'
)

for oid in OIDS:
    obj = fetch_json(f"{RTSM_BASE}/objects/{oid}")
    if obj is None or obj.get("error") == "not_found":
        parts.append('<div class="oid-section">\n')
        parts.append(f'  <div class="oid-header"><h2>{esc(oid)}</h2></div>\n')
        parts.append('  <div class="error">OID not found.</div>\n')
        parts.append("</div>\n")
        continue

    label_user = obj.get("label_user") or "(unnamed)"
    label_primary = obj.get("label_primary") or "?"
    mov = obj.get("movability_class") or "null"
    xyz = obj.get("xyz_world") or []
    xyz_str = ", ".join(f"{v:.2f}" for v in xyz) if xyz else "?"
    hits = obj.get("hits") or 0
    pose_state = obj.get("pose_state_at_observation") or "?"
    confirmed = obj.get("confirmed")
    has_ref = bool(obj.get("reference_image_path"))
    ref_text = "has reference" if has_ref else "no reference"
    ref_class = "has-ref" if has_ref else "no-ref"

    snaps = fetch_json(f"{RTSM_BASE}/objects/{oid}/snapshots")
    snaps_list = snaps.get("snapshots", []) if snaps else []

    parts.append('<div class="oid-section">\n')
    parts.append('  <div class="oid-header">\n')
    parts.append(
        f'    <h2>{esc(label_user)}<span class="sub">label_primary={esc(label_primary)}</span></h2>\n'
    )
    parts.append(
        f'    <div class="meta-row">{esc(oid)} &middot; {esc(mov)} &middot; '
        f'{esc(pose_state)} &middot; hits={esc(hits)} &middot; '
        f'<span class="{ref_class}">{esc(ref_text)}</span> &middot; '
        f'xyz=[{esc(xyz_str)}] &middot; {len(snaps_list)} crops</div>\n'
    )
    parts.append("  </div>\n")

    parts.append('  <div class="strip">\n')
    if not snaps_list:
        parts.append('    <div class="error">No snapshots stored.</div>\n')
    else:
        for s in snaps_list:
            idx = s.get("index", "?")
            data = s.get("data") or PLACEHOLDER
            parts.append('    <div class="snap">\n')
            parts.append(f'      <img src="{data}" alt="snap{esc(idx)}">\n')
            parts.append(f'      <div class="idx">#{esc(idx)}</div>\n')
            parts.append("    </div>\n")
    parts.append("  </div>\n")
    parts.append("</div>\n")

parts.append("</body></html>\n")

with open(OUTPUT, "w", encoding="utf-8") as f:
    f.writelines(parts)

print(f"Wrote: {OUTPUT}")
PYEOF

echo
ls -la "$OUTPUT"
echo
echo "Open in browser. Fully self-contained — no server needed."

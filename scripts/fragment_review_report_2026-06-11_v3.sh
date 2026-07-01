#!/usr/bin/env bash
# =============================================================================
# fragment_review_report_2026-06-11_v3.sh
#
# v3: replaces all bash JSON manipulation with a single Python pass.
# Eliminates the jq 'label' keyword collision in v2 and a nested-subshell
# bug that was producing malformed JSON between data collection and
# rendering.
#
# Output: a single self-contained HTML file with inline base64 JPEG
# snapshots embedded via data: URIs. No image server needed; scp and
# open anywhere.
#
# Usage:
#   ./fragment_review_report_2026-06-11_v3.sh [output.html]
#   ./fragment_review_report_2026-06-11_v3.sh --cos 0.92 review.html
#   ./fragment_review_report_2026-06-11_v3.sh --label "desk" desk_only.html
#
# Defaults: cos=0.95, output=fragment_review_<timestamp>.html
#
# Environment:
#   RTSM_BASE  Default http://localhost:8002
# =============================================================================

set -euo pipefail

RTSM_BASE="${RTSM_BASE:-http://localhost:8002}"
COS_THRESHOLD="0.95"
FILTER_LABEL=""
OUTPUT=""

while [ $# -gt 0 ]; do
    case "$1" in
        --cos)   COS_THRESHOLD="$2"; shift 2 ;;
        --label) FILTER_LABEL="$2"; shift 2 ;;
        --help|-h)
            sed -n '/^# Usage:/,/^# ===/p' "$0" | sed 's/^# //'
            exit 0 ;;
        *)
            if [ -z "$OUTPUT" ]; then OUTPUT="$1"; shift
            else echo "Unknown arg: $1" >&2; exit 2
            fi
            ;;
    esac
done

if [ -z "$OUTPUT" ]; then
    OUTPUT="fragment_review_$(date +%Y%m%d_%H%M%S).html"
fi

# Pre-flight: server up?
if ! curl -s -o /dev/null -f "$RTSM_BASE/objects" 2>/dev/null; then
    printf "\033[31mFATAL: cannot reach RTSM at %s\033[0m\n" "$RTSM_BASE" >&2
    exit 1
fi

# Everything else: one Python pass. No jq, no nested bash loops, no JSON
# stitching in shell.
python3 - "$RTSM_BASE" "$COS_THRESHOLD" "${FILTER_LABEL:-}" "$OUTPUT" <<'PYEOF'
import json
import sys
import html
import urllib.request
import urllib.error
from datetime import datetime

RTSM_BASE, COS_STR, FILTER_LABEL, OUTPUT = sys.argv[1:5]
COS = float(COS_STR)


def fetch_json(url, method="GET", body=None, timeout=10):
    """Lightweight JSON HTTP client. Returns None on failure."""
    try:
        data = None
        headers = {}
        if body is not None:
            data = json.dumps(body).encode("utf-8")
            headers["Content-Type"] = "application/json"
        req = urllib.request.Request(url, method=method, headers=headers, data=data)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.load(resp)
    except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError, TimeoutError):
        return None


def get_data_uri(oid, cache):
    """Fetch latest snapshot data URI for an OID. Cached. Empty if absent."""
    if oid in cache:
        return cache[oid]
    body = fetch_json(f"{RTSM_BASE}/objects/{oid}/snapshots")
    uri = ""
    if body and body.get("snapshots"):
        snaps = body["snapshots"]
        uri = snaps[-1].get("data", "") if snaps else ""
    cache[oid] = uri
    return uri


# ----- 1. Get named OIDs ----------------------------------------------------
print("Fetching named OIDs...", file=sys.stderr)
all_objs = fetch_json(f"{RTSM_BASE}/objects?limit=1000&pose_state=any")
if not all_objs:
    print("FATAL: /objects fetch failed", file=sys.stderr)
    sys.exit(1)

named = [
    {
        "oid": o["id"],
        "label_user": o["label_user"],
        "movability_class": o.get("movability_class"),
    }
    for o in all_objs.get("objects", [])
    if o.get("label_user")
]

if FILTER_LABEL:
    named = [n for n in named if n["label_user"] == FILTER_LABEL]
    if not named:
        print(f"No named OID matches label_user={FILTER_LABEL!r}", file=sys.stderr)
        sys.exit(1)

print(f"  {len(named)} named anchors", file=sys.stderr)

# ----- 2. For each anchor, find_fragments + collect snapshot URIs -----------
print(f"Querying find_fragments (cos={COS}) and fetching snapshots...", file=sys.stderr)
sn_cache = {}
records = []
body = {"cos_threshold": COS, "limit": 100}

for n in named:
    oid = n["oid"]
    resp = fetch_json(
        f"{RTSM_BASE}/objects/{oid}/find_fragments", method="POST", body=body
    )
    if resp is None:
        resp = {"returned": 0, "fragments": [], "thresholds": {}}

    anchor_uri = get_data_uri(oid, sn_cache)
    for frag in resp.get("fragments", []):
        frag["data_uri"] = get_data_uri(frag["oid"], sn_cache)

    records.append(
        {
            "label_user": n["label_user"],
            "oid": oid,
            "movability_class": n.get("movability_class"),
            "anchor_uri": anchor_uri,
            "dist_threshold_m": resp.get("thresholds", {}).get("dist_threshold_m"),
            "returned": resp.get("returned", 0),
            "fragments": resp.get("fragments", []),
        }
    )

print(f"  cached {len(sn_cache)} snapshots", file=sys.stderr)

# ----- 3. Render HTML --------------------------------------------------------
print("Rendering HTML...", file=sys.stderr)

now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
total_anchors = len(records)
anchors_with_candidates = sum(1 for r in records if (r.get("returned") or 0) > 0)


def esc(s):
    return html.escape(str(s) if s is not None else "")


PLACEHOLDER = (
    "data:image/svg+xml;utf8,"
    "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 224 224'>"
    "<rect width='224' height='224' fill='%23222'/>"
    "<text x='112' y='112' fill='%23666' font-family='monospace' font-size='14' "
    "text-anchor='middle' dominant-baseline='middle'>no snapshot</text>"
    "</svg>"
)

CSS = """
body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", system-ui, sans-serif;
       background: #1a1a1a; color: #ddd; margin: 0; padding: 24px; }
h1 { font-size: 18px; color: #fff; margin: 0 0 4px 0; }
.meta { color: #888; font-size: 12px; margin-bottom: 24px; }
.summary { background: #2a2a2a; padding: 12px 16px; border-radius: 6px;
           margin-bottom: 24px; font-size: 13px; }
.anchor { background: #252525; border: 1px solid #333; border-radius: 8px;
          padding: 16px; margin-bottom: 32px; }
.anchor-header { display: flex; align-items: center; gap: 16px; margin-bottom: 12px;
                 flex-wrap: wrap; }
.anchor-header h2 { margin: 0; font-size: 20px; color: #ffc857; }
.anchor-header .meta-row { font-family: ui-monospace, "SF Mono", Menlo, monospace;
                            font-size: 12px; color: #888; }
.row { display: flex; gap: 16px; align-items: flex-start; flex-wrap: wrap; }
.card { background: #1a1a1a; border: 1px solid #333; border-radius: 6px;
        padding: 8px; width: 240px; }
.card.anchor-card { border-color: #ffc857; border-width: 2px; }
.card img { width: 224px; height: 224px; object-fit: cover; background: #000;
            border-radius: 4px; display: block; }
.card .label { color: #fff; font-weight: 600; margin: 6px 0 2px 0;
               word-break: break-word; }
.card .oid { font-family: ui-monospace, "SF Mono", Menlo, monospace;
             font-size: 11px; color: #888; word-break: break-all; }
.card .stats { font-size: 11px; color: #aaa; margin-top: 6px; line-height: 1.5; }
.card .stats span { display: inline-block; padding: 1px 5px; background: #2a2a2a;
                    border-radius: 3px; margin-right: 4px; }
.card .cosine { color: #5fb878; font-weight: 600; }
.card .has-ref { color: #5fb878; }
.card .no-ref { color: #d97757; }
.clean { color: #5fb878; font-style: italic; padding: 16px;
         align-self: center; }
.copy-cmd { background: #1a1a1a; border: 1px solid #333; border-radius: 4px;
            padding: 8px 12px; font-family: ui-monospace, "SF Mono", Menlo, monospace;
            font-size: 11px; color: #aaa; margin-top: 12px; overflow-x: auto;
            white-space: pre; }
"""

out = []
out.append('<!DOCTYPE html>\n<html lang="en"><head>\n')
out.append('<meta charset="utf-8">\n')
out.append(f"<title>RTSM Fragment Review &mdash; {esc(now)}</title>\n")
out.append(f"<style>{CSS}</style>\n")
out.append("</head><body>\n")
out.append("<h1>RTSM Fragment Review</h1>\n")
out.append(
    f'<div class="meta">Generated {esc(now)} &middot; '
    f"cos &ge; {esc(COS_STR)} &middot; RTSM @ {esc(RTSM_BASE)}</div>\n"
)
out.append(
    f'<div class="summary"><strong>{total_anchors} named OIDs</strong> audited at '
    f"cos &ge; {esc(COS_STR)}. <strong>{anchors_with_candidates}</strong> have "
    "at least one candidate above gate.<br>"
    'Anchor snapshots have a <span style="color:#ffc857">yellow border</span>. '
    "Eyeball each candidate against the anchor; real duplicates get the merge curl "
    "below.</div>\n"
)

for rec in records:
    label = rec["label_user"]
    oid = rec["oid"]
    mov = rec.get("movability_class") or "null"
    anchor_uri = rec.get("anchor_uri") or PLACEHOLDER
    dist = rec.get("dist_threshold_m")
    if dist is None:
        dist = "?"
    returned = rec.get("returned") or 0
    fragments = rec.get("fragments") or []

    out.append('<div class="anchor">\n')
    out.append('  <div class="anchor-header">\n')
    out.append(f"    <h2>{esc(label)}</h2>\n")
    out.append(
        f'    <div class="meta-row">{esc(oid)} &middot; {esc(mov)} &middot; '
        f"cos&ge;{esc(COS_STR)} &middot; dist&le;{esc(dist)}m</div>\n"
    )
    out.append("  </div>\n")
    out.append('  <div class="row">\n')
    # Anchor card
    out.append('    <div class="card anchor-card">\n')
    out.append(f'      <img src="{anchor_uri}" alt="anchor">\n')
    out.append(
        f'      <div class="label">{esc(label)} '
        f'<span style="color:#ffc857">(anchor)</span></div>\n'
    )
    out.append(f'      <div class="oid">{esc(oid)}</div>\n')
    out.append(f'      <div class="stats"><span>{esc(mov)}</span></div>\n')
    out.append("    </div>\n")

    if returned == 0:
        out.append(
            '    <div class="clean">No candidates above gate. Anchor appears clean.</div>\n'
        )
    else:
        for frag in fragments:
            f_oid = frag.get("oid", "")
            f_uri = frag.get("data_uri") or PLACEHOLDER
            f_lab_p = frag.get("label_primary") or "?"
            f_lab_u = frag.get("label_user") or ""
            f_cos = frag.get("cosine") or 0
            f_dist = frag.get("distance_m") or 0
            f_hits = frag.get("hits") or 0
            f_mov = frag.get("movability_class") or "null"
            f_pose = frag.get("pose_state_at_observation") or "?"
            f_has_ref = frag.get("has_reference") or False
            ref_class = "has-ref" if f_has_ref else "no-ref"
            ref_text = "has ref" if f_has_ref else "no ref"

            label_with_user = esc(f_lab_p)
            if f_lab_u:
                label_with_user += (
                    f' <span style="color:#ffc857">[{esc(f_lab_u)}]</span>'
                )

            out.append('    <div class="card">\n')
            out.append(f'      <img src="{f_uri}" alt="candidate">\n')
            out.append(f'      <div class="label">{label_with_user}</div>\n')
            out.append(f'      <div class="oid">{esc(f_oid)}</div>\n')
            out.append('      <div class="stats">\n')
            out.append(f'        <span class="cosine">cos={esc(f_cos)}</span>\n')
            out.append(f"        <span>{esc(f_dist)}&nbsp;m</span><br>\n")
            out.append(f"        <span>{esc(f_mov)}</span>\n")
            out.append(f"        <span>{esc(f_pose)}</span>\n")
            out.append(f"        <span>hits={esc(f_hits)}</span>\n")
            out.append(f'        <span class="{ref_class}">{esc(ref_text)}</span>\n')
            out.append("      </div>\n")
            out.append("    </div>\n")

    out.append("  </div>\n")

    if returned > 0:
        out.append('  <div class="copy-cmd">\n')
        out.append(
            "# Merge a candidate INTO this anchor (anchor wins, candidate dies):\n"
        )
        out.append(f"curl -s -X POST {esc(RTSM_BASE)}/objects/merge \\\n")
        out.append("     -H 'Content-Type: application/json' \\\n")
        out.append(
            f'     -d \'{{"a_oid": "{esc(oid)}", "b_oid": "&lt;CANDIDATE_OID&gt;", '
            f'"winner_oid": "{esc(oid)}"}}\' | jq\n'
        )
        out.append("  </div>\n")

    out.append("</div>\n")

out.append("</body></html>\n")

with open(OUTPUT, "w", encoding="utf-8") as f:
    f.writelines(out)

print(f"Wrote: {OUTPUT}")
PYEOF

echo
ls -la "$OUTPUT"
echo
echo "Done. Open $OUTPUT in any browser — fully self-contained, no server needed."

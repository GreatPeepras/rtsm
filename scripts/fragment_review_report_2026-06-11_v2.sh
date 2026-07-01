#!/usr/bin/env bash
# =============================================================================
# fragment_review_report_2026-06-11_v2.sh
#
# v2: uses /objects/{oid}/snapshots (the listing endpoint) and embeds the
# returned base64 data URIs directly into <img src="data:...">. This
# bypasses the broken /snapshots/{index}/image route entirely.
#
# Side benefits:
#  * Fully self-contained HTML — no IMG_BASE_URL games, scp the file
#    anywhere and it just works.
#  * No browser-side fetches at render time; the page loads instantly.
#
# Cost: ~1-2 MB HTML for a full audit (12 anchors × ~20 cards × ~6KB
# base64-encoded JPEG). Still fine for any modern browser.
#
# Usage:
#   ./fragment_review_report_2026-06-11_v2.sh [output.html]
#   ./fragment_review_report_2026-06-11_v2.sh --cos 0.92 review.html
#   ./fragment_review_report_2026-06-11_v2.sh --label "desk" desk_only.html
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

REQ_BODY=$(jq -n --argjson c "$COS_THRESHOLD" '{cos_threshold: $c, limit: 100}')

# Pre-flight
if ! curl -s -o /dev/null -f "$RTSM_BASE/objects" 2>/dev/null; then
    echo "FATAL: cannot reach RTSM at $RTSM_BASE" >&2; exit 1
fi

NAMED_JSON=$(curl -s "$RTSM_BASE/objects" \
    | jq -c '[.objects[] | select(.label_user != null) | {oid: .id, label: .label_user, mov: .movability_class}]')
if [ -n "$FILTER_LABEL" ]; then
    NAMED_JSON=$(echo "$NAMED_JSON" | jq -c --arg lbl "$FILTER_LABEL" \
                 '[.[] | select(.label == $lbl)]')
fi
if [ "$(echo "$NAMED_JSON" | jq 'length')" -eq 0 ]; then
    echo "No matching named OIDs." >&2; exit 0
fi

# Snapshot cache (avoid re-fetching the same OID if it appears as
# candidate of multiple anchors). Keys are OIDs, values are data URIs
# (empty string if no snapshot available).
declare -A SNAP_CACHE

fetch_data_uri() {
    local oid="$1"
    if [ -n "${SNAP_CACHE[$oid]+set}" ]; then
        echo "${SNAP_CACHE[$oid]}"
        return
    fi
    local uri
    uri=$(curl -s "$RTSM_BASE/objects/$oid/snapshots" 2>/dev/null \
          | jq -r '.snapshots // [] | if length > 0 then .[length-1].data // "" else "" end' \
          2>/dev/null || echo "")
    SNAP_CACHE["$oid"]="$uri"
    echo "$uri"
}

# -----------------------------------------------------------------------
# Build HTML
# -----------------------------------------------------------------------

echo "Fetching anchors and snapshots..." >&2

# We do two passes: data collection first (so we know counts), then HTML.
DATA_TMP=$(mktemp /tmp/fragment_review_data.XXXXXX.json)
trap 'rm -f "$DATA_TMP"' EXIT

# Build a JSON list of {label, oid, mov, anchor_data_uri, fragments[...]}
# entries, one per anchor.
{
    printf "["
    first=1
    echo "$NAMED_JSON" | jq -c '.[]' | while read -r row; do
        oid=$(echo "$row" | jq -r '.oid')
        label=$(echo "$row" | jq -r '.label')
        mov=$(echo "$row" | jq -r '.mov // "null"')

        if [ $first -eq 1 ]; then first=0; else printf ","; fi

        response=$(curl -s -X POST "$RTSM_BASE/objects/$oid/find_fragments" \
                   -H 'Content-Type: application/json' --data "$REQ_BODY" 2>/dev/null || echo '{}')
        returned=$(echo "$response" | jq -r '.returned // 0')

        anchor_data_uri=$(fetch_data_uri "$oid")

        # Build fragment array with embedded data URIs.
        fragments_with_data='[]'
        if [ "$returned" -gt 0 ]; then
            fragments_with_data='['
            frag_first=1
            echo "$response" | jq -c '.fragments[]' | while read -r frag; do
                f_oid=$(echo "$frag" | jq -r '.oid')
                f_data=$(fetch_data_uri "$f_oid")
                if [ $frag_first -eq 1 ]; then frag_first=0; else printf ","; fi
                # Inject data_uri into the fragment object.
                echo "$frag" | jq -c --arg uri "$f_data" '. + {data_uri: $uri}'
            done
            printf "]"
        fi

        # Compose the per-anchor record. We use jq to safely embed the
        # data URIs as JSON string values (so quotes/special chars are
        # properly escaped).
        jq -n \
           --arg label "$label" \
           --arg oid "$oid" \
           --arg mov "$mov" \
           --arg anchor_uri "$anchor_data_uri" \
           --arg dist "$(echo "$response" | jq -r '.thresholds.dist_threshold_m // 0')" \
           --argjson resp "$response" \
           '{
              label: $label,
              oid: $oid,
              mov: $mov,
              anchor_uri: $anchor_uri,
              dist_threshold_m: $dist,
              returned: ($resp.returned // 0),
              fragments: ($resp.fragments // [])
           }'
    done
    printf "]"
} > "$DATA_TMP"

# Now fetch data URIs for each fragment OID and merge into the JSON.
# (We had to do this in a second pass because nested while loops with
# pipes don't share env vars cleanly in bash.)
echo "Embedding fragment snapshots..." >&2

ENRICHED_TMP=$(mktemp /tmp/fragment_review_enriched.XXXXXX.json)
trap 'rm -f "$DATA_TMP" "$ENRICHED_TMP"' EXIT

# Walk every anchor record, fetch data URIs for each candidate, write enriched JSON.
jq -c '.[]' "$DATA_TMP" | while read -r anchor_rec; do
    echo "$anchor_rec" | jq -c '.fragments[]?' | while read -r frag; do
        f_oid=$(echo "$frag" | jq -r '.oid')
        fetch_data_uri "$f_oid" > /dev/null  # populates cache
    done
done

# Now stream through the data and inject data_uri into each fragment by
# looking up the snapshot cache. We do this in a Python pass for clarity.
python3 - "$DATA_TMP" "$ENRICHED_TMP" "$RTSM_BASE" <<'PYEOF'
import json
import sys
import urllib.request
import urllib.error

DATA_TMP, ENRICHED_TMP, RTSM_BASE = sys.argv[1], sys.argv[2], sys.argv[3]

with open(DATA_TMP) as f:
    data = json.load(f)

cache = {}
def fetch_uri(oid):
    if oid in cache:
        return cache[oid]
    url = f"{RTSM_BASE}/objects/{oid}/snapshots"
    try:
        with urllib.request.urlopen(url, timeout=5) as resp:
            body = json.load(resp)
            snaps = body.get("snapshots", [])
            uri = snaps[-1].get("data", "") if snaps else ""
    except Exception:
        uri = ""
    cache[oid] = uri
    return uri

for anchor_rec in data:
    # Anchor data URI is already filled in by the bash pass; re-confirm.
    if not anchor_rec.get("anchor_uri"):
        anchor_rec["anchor_uri"] = fetch_uri(anchor_rec["oid"])
    for frag in anchor_rec.get("fragments", []):
        frag["data_uri"] = fetch_uri(frag["oid"])

with open(ENRICHED_TMP, "w") as f:
    json.dump(data, f)

print(f"Cached {len(cache)} OID snapshots", file=sys.stderr)
PYEOF

# -----------------------------------------------------------------------
# Render HTML from enriched data
# -----------------------------------------------------------------------
echo "Rendering HTML..." >&2

python3 - "$ENRICHED_TMP" "$OUTPUT" "$COS_THRESHOLD" "$RTSM_BASE" <<'PYEOF'
import json
import sys
import html
from datetime import datetime

ENRICHED_TMP, OUTPUT, COS_THRESHOLD, RTSM_BASE = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]

with open(ENRICHED_TMP) as f:
    data = json.load(f)

now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
total_anchors = len(data)
anchors_with_candidates = sum(1 for a in data if (a.get("returned") or 0) > 0)

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

parts = []
parts.append('<!DOCTYPE html>\n<html lang="en"><head>\n')
parts.append('<meta charset="utf-8">\n')
parts.append(f'<title>RTSM Fragment Review — {esc(now)}</title>\n')
parts.append(f'<style>{CSS}</style>\n')
parts.append('</head><body>\n')
parts.append('<h1>RTSM Fragment Review</h1>\n')
parts.append(
    f'<div class="meta">Generated {esc(now)} &middot; '
    f'cos &ge; {esc(COS_THRESHOLD)} &middot; RTSM @ {esc(RTSM_BASE)}</div>\n'
)
parts.append(
    f'<div class="summary"><strong>{total_anchors} named OIDs</strong> audited at '
    f'cos &ge; {esc(COS_THRESHOLD)}. <strong>{anchors_with_candidates}</strong> have '
    'at least one candidate above gate.<br>'
    'Anchor snapshots have a <span style="color:#ffc857">yellow border</span>. '
    'Eyeball each candidate against the anchor; real duplicates get the merge curl '
    'below.</div>\n'
)

for anchor_rec in data:
    label = anchor_rec["label"]
    oid = anchor_rec["oid"]
    mov = anchor_rec.get("mov") or "null"
    anchor_uri = anchor_rec.get("anchor_uri") or PLACEHOLDER
    dist = anchor_rec.get("dist_threshold_m") or "?"
    returned = anchor_rec.get("returned") or 0
    fragments = anchor_rec.get("fragments") or []

    parts.append('<div class="anchor">\n')
    parts.append('  <div class="anchor-header">\n')
    parts.append(f'    <h2>{esc(label)}</h2>\n')
    parts.append(
        f'    <div class="meta-row">{esc(oid)} &middot; {esc(mov)} &middot; '
        f'cos&ge;{esc(COS_THRESHOLD)} &middot; dist&le;{esc(dist)}m</div>\n'
    )
    parts.append('  </div>\n')
    parts.append('  <div class="row">\n')
    # Anchor card
    parts.append('    <div class="card anchor-card">\n')
    parts.append(f'      <img src="{anchor_uri}" alt="anchor">\n')
    parts.append(
        f'      <div class="label">{esc(label)} <span style="color:#ffc857">(anchor)</span></div>\n'
    )
    parts.append(f'      <div class="oid">{esc(oid)}</div>\n')
    parts.append(f'      <div class="stats"><span>{esc(mov)}</span></div>\n')
    parts.append('    </div>\n')

    if returned == 0:
        parts.append('    <div class="clean">No candidates above gate. Anchor appears clean.</div>\n')
    else:
        for frag in fragments:
            f_oid = frag["oid"]
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

            parts.append('    <div class="card">\n')
            parts.append(f'      <img src="{f_uri}" alt="candidate">\n')
            label_with_user = esc(f_lab_p)
            if f_lab_u:
                label_with_user = f'{esc(f_lab_p)} <span style="color:#ffc857">[{esc(f_lab_u)}]</span>'
            parts.append(f'      <div class="label">{label_with_user}</div>\n')
            parts.append(f'      <div class="oid">{esc(f_oid)}</div>\n')
            parts.append('      <div class="stats">\n')
            parts.append(f'        <span class="cosine">cos={esc(f_cos)}</span>\n')
            parts.append(f'        <span>{esc(f_dist)}&nbsp;m</span><br>\n')
            parts.append(f'        <span>{esc(f_mov)}</span>\n')
            parts.append(f'        <span>{esc(f_pose)}</span>\n')
            parts.append(f'        <span>hits={esc(f_hits)}</span>\n')
            parts.append(f'        <span class="{ref_class}">{esc(ref_text)}</span>\n')
            parts.append('      </div>\n')
            parts.append('    </div>\n')

    parts.append('  </div>\n')

    if returned > 0:
        parts.append('  <div class="copy-cmd">\n')
        parts.append(f'# Merge a candidate INTO this anchor (anchor wins, candidate dies):\n')
        parts.append(f'curl -s -X POST {esc(RTSM_BASE)}/objects/merge \\\n')
        parts.append(f"     -H 'Content-Type: application/json' \\\n")
        parts.append(
            f'     -d \'{{"a_oid": "{esc(oid)}", "b_oid": "&lt;CANDIDATE_OID&gt;", '
            f'"winner_oid": "{esc(oid)}"}}\' | jq\n'
        )
        parts.append('  </div>\n')

    parts.append('</div>\n')

parts.append('</body></html>\n')

with open(OUTPUT, "w") as f:
    f.writelines(parts)

print(f"Wrote: {OUTPUT}")
PYEOF

echo
echo "Done. Open $OUTPUT in any browser — fully self-contained, no server needed."
echo "File size: $(du -h "$OUTPUT" | cut -f1)"

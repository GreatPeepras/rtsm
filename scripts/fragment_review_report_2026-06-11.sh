#!/usr/bin/env bash
# =============================================================================
# fragment_review_report_2026-06-11.sh
#
# Generates a single self-contained HTML report for visual review of
# find_fragments results. For each named OID with candidates above the
# cos threshold, shows the anchor snapshot + every candidate snapshot
# side-by-side with metadata. Open the HTML in a browser; scroll;
# eyeball; note the OIDs to merge.
#
# No interactivity — just visual presentation. Merge actions are POSTed
# separately by hand (or via the existing merge_review tooling), using
# the OIDs identified during review.
#
# Why: RTSM label_primary is known to be unreliable (CLIP noise),
# so cos+distance alone isn't enough to confirm duplicates. The
# anchor's reference snapshot vs each candidate's latest snapshot is
# the ground truth.
#
# Usage:
#   ./fragment_review_report_2026-06-11.sh [output.html]
#   ./fragment_review_report_2026-06-11.sh --cos 0.92 review.html
#   ./fragment_review_report_2026-06-11.sh --label "desk" desk_only.html
#
# Defaults: cos=0.95, output=fragment_review_<timestamp>.html
#
# Environment:
#   RTSM_BASE       Default http://192.168.0.53:8002
#   IMG_BASE_URL    URL prefix for <img src=...>. Default = same as
#                   RTSM_BASE. Set this if you want images to render
#                   against a different hostname (e.g. opening the
#                   HTML on a different machine over LAN: set to
#                   http://192.168.0.53:8002).
# =============================================================================

set -euo pipefail

RTSM_BASE="${RTSM_BASE:-http://192.168.0.53:8002}"
IMG_BASE_URL="${IMG_BASE_URL:-$RTSM_BASE}"
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
            if [ -z "$OUTPUT" ]; then
                OUTPUT="$1"; shift
            else
                echo "Unknown arg: $1" >&2; exit 2
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

# Fetch named OIDs (optionally filtered).
NAMED_JSON=$(curl -s "$RTSM_BASE/objects" \
    | jq -c '[.objects[] | select(.label_user != null) | {oid: .id, label: .label_user, mov: .movability_class}]')
if [ -n "$FILTER_LABEL" ]; then
    NAMED_JSON=$(echo "$NAMED_JSON" | jq -c --arg lbl "$FILTER_LABEL" \
                 '[.[] | select(.label == $lbl)]')
fi

if [ "$(echo "$NAMED_JSON" | jq 'length')" -eq 0 ]; then
    echo "No matching named OIDs." >&2; exit 0
fi

# -----------------------------------------------------------------------
# Build the HTML.
# -----------------------------------------------------------------------
{
cat <<EOF
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>RTSM Fragment Review — $(date '+%Y-%m-%d %H:%M')</title>
<style>
  body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", system-ui, sans-serif;
         background: #1a1a1a; color: #ddd; margin: 0; padding: 24px; }
  h1 { font-size: 18px; color: #fff; margin: 0 0 4px 0; }
  .meta { color: #888; font-size: 12px; margin-bottom: 24px; }
  .anchor { background: #252525; border: 1px solid #333; border-radius: 8px;
            padding: 16px; margin-bottom: 32px; }
  .anchor-header { display: flex; align-items: center; gap: 16px; margin-bottom: 12px; }
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
  .clean { color: #5fb878; font-style: italic; }
  .candidates-row { margin-top: 16px; }
  .copy-cmd { background: #1a1a1a; border: 1px solid #333; border-radius: 4px;
              padding: 8px 12px; font-family: ui-monospace, "SF Mono", Menlo, monospace;
              font-size: 11px; color: #aaa; margin-top: 8px; overflow-x: auto; }
  hr { border: none; border-top: 1px solid #333; margin: 24px 0; }
  .summary { background: #2a2a2a; padding: 12px 16px; border-radius: 6px;
             margin-bottom: 24px; font-size: 13px; }
</style>
</head>
<body>
<h1>RTSM Fragment Review</h1>
<div class="meta">
  Generated $(date '+%Y-%m-%d %H:%M:%S') &middot;
  cos &ge; $COS_THRESHOLD &middot;
  RTSM @ $RTSM_BASE
</div>
EOF

# Track counts for summary.
total_anchors=$(echo "$NAMED_JSON" | jq 'length')
anchors_with_candidates=0
total_candidates=0

# We do two passes: first collect data to a temp file (so we know counts
# for the summary), then build the body sections.
SECTIONS_TMP=$(mktemp /tmp/fragment_review.XXXXXX.html)
trap 'rm -f "$SECTIONS_TMP"' EXIT

echo "$NAMED_JSON" | jq -c '.[]' | while read -r row; do
    oid=$(echo "$row" | jq -r '.oid')
    label=$(echo "$row" | jq -r '.label')
    mov=$(echo "$row" | jq -r '.mov // "null"')

    response=$(curl -s -X POST "$RTSM_BASE/objects/$oid/find_fragments" \
               -H 'Content-Type: application/json' \
               --data "$REQ_BODY" 2>/dev/null || echo '{}')

    returned=$(echo "$response" | jq -r '.returned // 0')
    dist=$(echo "$response" | jq -r '.thresholds.dist_threshold_m // "?"')
    anchor_xyz=$(echo "$response" | jq -r '.anchor.xyz | tostring')

    # Always show the anchor; clean anchors get a "no fragments" note.
    {
        echo "<div class=\"anchor\">"
        echo "  <div class=\"anchor-header\">"
        # Use jq to safely escape the label for HTML.
        label_html=$(printf '%s' "$label" | jq -Rs '.' | sed 's/^"//; s/"$//')
        echo "    <h2>$label_html</h2>"
        echo "    <div class=\"meta-row\">$oid &middot; $mov &middot; cos&ge;$COS_THRESHOLD &middot; dist&le;${dist}m &middot; xyz=$anchor_xyz</div>"
        echo "  </div>"
        echo "  <div class=\"row\">"
        # Anchor card
        echo "    <div class=\"card anchor-card\">"
        echo "      <img src=\"$IMG_BASE_URL/objects/$oid/snapshots/0/image\" alt=\"anchor\" onerror=\"this.style.opacity=0.3\">"
        echo "      <div class=\"label\">$label_html <span style=\"color:#ffc857\">(anchor)</span></div>"
        echo "      <div class=\"oid\">$oid</div>"
        echo "      <div class=\"stats\"><span>$mov</span></div>"
        echo "    </div>"

        if [ "$returned" -eq 0 ]; then
            echo "    <div class=\"clean\" style=\"padding: 16px; align-self: center;\">No candidates above gate. Anchor appears clean.</div>"
        else
            # Iterate candidates from the response.
            echo "$response" | jq -c '.fragments[]' | while read -r frag; do
                f_oid=$(echo "$frag" | jq -r '.oid')
                f_cos=$(echo "$frag" | jq -r '.cosine')
                f_dist=$(echo "$frag" | jq -r '.distance_m')
                f_lab_p=$(echo "$frag" | jq -r '.label_primary // "?"')
                f_lab_u=$(echo "$frag" | jq -r '.label_user // ""')
                f_hits=$(echo "$frag" | jq -r '.hits')
                f_mov=$(echo "$frag" | jq -r '.movability_class // "null"')
                f_pose=$(echo "$frag" | jq -r '.pose_state_at_observation // "?"')
                f_has_ref=$(echo "$frag" | jq -r '.has_reference')
                ref_class="no-ref"
                ref_text="no ref"
                if [ "$f_has_ref" = "true" ]; then
                    ref_class="has-ref"; ref_text="has ref"
                fi
                # Escape candidate label for HTML safely
                f_lab_p_html=$(printf '%s' "$f_lab_p" | jq -Rs '.' | sed 's/^"//; s/"$//')

                echo "    <div class=\"card\">"
                echo "      <img src=\"$IMG_BASE_URL/objects/$f_oid/snapshots/0/image\" alt=\"candidate\" onerror=\"this.style.opacity=0.3\">"
                echo "      <div class=\"label\">$f_lab_p_html</div>"
                echo "      <div class=\"oid\">$f_oid</div>"
                echo "      <div class=\"stats\">"
                echo "        <span class=\"cosine\">cos=$f_cos</span>"
                echo "        <span>$f_dist&nbsp;m</span>"
                echo "        <br>"
                echo "        <span>$f_mov</span>"
                echo "        <span>$f_pose</span>"
                echo "        <span>hits=$f_hits</span>"
                echo "        <span class=\"$ref_class\">$ref_text</span>"
                echo "      </div>"
                echo "    </div>"
            done

            # Add per-anchor merge-command snippet.
            echo "  </div>"
            echo "  <div class=\"copy-cmd\">"
            echo "# Merge a candidate INTO this anchor (anchor wins, candidate dies):"
            echo "curl -s -X POST $RTSM_BASE/objects/merge -H 'Content-Type: application/json' \\\\"
            echo "     -d '{\"a_oid\": \"$oid\", \"b_oid\": \"&lt;CANDIDATE_OID&gt;\", \"winner_oid\": \"$oid\"}' | jq"
            echo "  </div>"
            echo "</div>"
            continue
        fi
        echo "  </div>"
        echo "</div>"
    } >> "$SECTIONS_TMP"
done

# Build a summary header now that we've collected data
anchors_with_candidates=$(grep -c "class=\"copy-cmd\"" "$SECTIONS_TMP" || true)

cat <<EOF
<div class="summary">
  <strong>$total_anchors named OIDs</strong> audited at cos &ge; $COS_THRESHOLD.
  <strong>$anchors_with_candidates</strong> have at least one candidate above gate.
  <br>
  Anchor snapshots have a <span style="color:#ffc857">yellow border</span>.
  Eyeball each candidate against the anchor; real duplicates get the merge curl below.
</div>
EOF

cat "$SECTIONS_TMP"

cat <<EOF
</body>
</html>
EOF
} > "$OUTPUT"

echo "Wrote: $OUTPUT"
echo
echo "Open in a browser. If the images don't render because localhost"
echo "isn't reachable from where you opened the HTML, set IMG_BASE_URL"
echo "to the LAN address and re-run:"
echo "   IMG_BASE_URL=http://192.168.0.53:8002 $0 $OUTPUT"

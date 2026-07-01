#!/usr/bin/env bash
# =============================================================================
# fragmentation_audit_2026-06-11_v2.sh
#
# v2 of the post-deploy fragmentation diagnostic.
#
# Changes from v1:
#  * Default cos_threshold raised 0.85 -> 0.95. Calibrated against the
#    2026-06-11 basketball probe: at 0.85 the corpus reported ~50%
#    cross-category CLIP noise (cup/nightstand/door all matching
#    "basketball"). At 0.95 only same-category-ish candidates remain.
#    Override with --cos 0.92 etc if you want to widen for exploration.
#  * --details now emits a single JSON array on stdout (no color headers),
#    so the output can be piped through jq cleanly:
#       ./fragmentation_audit_2026-06-11_v2.sh --details basketball | jq ...
#  * Label rendering no longer goes through bash double-quote expansion,
#    so labels containing backticks (dad`s chair, mom`s chair) don't
#    trigger command substitution. Truncation happens in jq.
#  * Summary footer uses awk count, not sum (sum was meaningless with
#    duplicate counts; "OIDs with fragments" is what we actually want).
#
# Usage:
#   ./fragmentation_audit_2026-06-11_v2.sh                          # summary
#   ./fragmentation_audit_2026-06-11_v2.sh --cos 0.92               # tighter
#   ./fragmentation_audit_2026-06-11_v2.sh --dist 5.0               # tighter dist
#   ./fragmentation_audit_2026-06-11_v2.sh --details                # JSON array
#   ./fragmentation_audit_2026-06-11_v2.sh --details basketball     # one anchor
#
# Multiple flags can be combined: --cos 0.92 --details basketball
#
# Environment:
#   RTSM_BASE  Default http://localhost:8002
# =============================================================================

set -euo pipefail

RTSM_BASE="${RTSM_BASE:-http://localhost:8002}"

# Defaults
COS_THRESHOLD="0.95"
DIST_THRESHOLD=""     # empty -> use server-side adaptive default
DETAILS_MODE=0
FILTER_LABEL=""

# Parse flags. Accept --cos, --dist, --details [label].
while [ $# -gt 0 ]; do
    case "$1" in
        --cos)
            COS_THRESHOLD="$2"; shift 2 ;;
        --dist)
            DIST_THRESHOLD="$2"; shift 2 ;;
        --details)
            DETAILS_MODE=1
            shift
            # Optional label argument
            if [ $# -gt 0 ] && [ "${1:0:2}" != "--" ]; then
                FILTER_LABEL="$1"; shift
            fi
            ;;
        --help|-h)
            sed -n '/^# Usage:/,/^# ===/p' "$0" | sed 's/^# //'
            exit 0 ;;
        *)
            echo "Unknown flag: $1" >&2
            echo "Use --help for usage." >&2
            exit 2 ;;
    esac
done

color_red()    { printf "\033[31m%s\033[0m\n" "$*" >&2; }
color_green()  { printf "\033[32m%s\033[0m\n" "$*" >&2; }
color_yellow() { printf "\033[33m%s\033[0m\n" "$*" >&2; }

# Build the request body once.
if [ -n "$DIST_THRESHOLD" ]; then
    REQ_BODY=$(jq -n --argjson c "$COS_THRESHOLD" --argjson d "$DIST_THRESHOLD" \
                   '{cos_threshold: $c, dist_threshold_m: $d, limit: 100}')
else
    REQ_BODY=$(jq -n --argjson c "$COS_THRESHOLD" \
                   '{cos_threshold: $c, limit: 100}')
fi

# Pre-flight: endpoint reachable and registered?
if ! curl -s -o /dev/null -f "$RTSM_BASE/objects?limit=1000&pose_state=any" 2>/dev/null; then
    color_red "FATAL: cannot reach RTSM at $RTSM_BASE/objects"
    exit 1
fi
if ! curl -s "$RTSM_BASE/openapi.json" \
        | jq -e '.paths["/objects/{oid}/find_fragments"]' >/dev/null 2>&1; then
    color_red "FATAL: /objects/{oid}/find_fragments not registered."
    color_yellow "Did you deploy the patch AND restart rtsm-dev?"
    exit 1
fi

# Fetch the named OIDs.
NAMED_JSON=$(curl -s "$RTSM_BASE/objects?limit=1000&pose_state=any" \
    | jq -c '[.objects[] | select(.label_user != null) | {oid: .id, label: .label_user, mov: .movability_class}]')

if [ "$(echo "$NAMED_JSON" | jq 'length')" -eq 0 ]; then
    color_yellow "No label_user-pinned OIDs found. Nothing to audit."
    exit 0
fi

# Optional filter by label (--details with a label arg).
if [ -n "$FILTER_LABEL" ]; then
    NAMED_JSON=$(echo "$NAMED_JSON" | jq -c --arg lbl "$FILTER_LABEL" \
                 '[.[] | select(.label == $lbl)]')
    if [ "$(echo "$NAMED_JSON" | jq 'length')" -eq 0 ]; then
        color_red "No named OID matches label_user=$FILTER_LABEL"
        exit 1
    fi
fi

# ---------------------------------------------------------------------------
# Per-anchor JSON details mode
# ---------------------------------------------------------------------------
if [ "$DETAILS_MODE" -eq 1 ]; then
    # Emit a single JSON array, one element per anchor, with the full
    # find_fragments response. Pipeable into jq.
    printf "["
    first=1
    echo "$NAMED_JSON" | jq -c '.[]' | while read -r row; do
        oid=$(echo "$row" | jq -r '.oid')
        response=$(curl -s -X POST "$RTSM_BASE/objects/$oid/find_fragments" \
                   -H 'Content-Type: application/json' \
                   --data "$REQ_BODY" 2>/dev/null || echo '{}')
        if [ $first -eq 1 ]; then
            first=0
        else
            printf ","
        fi
        # Wrap each anchor's response with the metadata row.
        echo "$response" | jq -c --argjson meta "$row" \
            '{label_user: $meta.label, anchor_oid: $meta.oid, movability: $meta.mov, response: .}'
    done
    printf "]\n"
    exit 0
fi

# ---------------------------------------------------------------------------
# Summary table mode (default)
# ---------------------------------------------------------------------------
TMP=$(mktemp /tmp/fragmentation_audit.XXXXXX)
trap 'rm -f "$TMP"' EXIT

# Emit a stable, parseable TSV first; pretty-print after sort.
echo "$NAMED_JSON" | jq -c '.[]' | while read -r row; do
    oid=$(echo "$row" | jq -r '.oid')

    response=$(curl -s -X POST "$RTSM_BASE/objects/$oid/find_fragments" \
               -H 'Content-Type: application/json' \
               --data "$REQ_BODY" 2>/dev/null || echo '{}')

    # jq does the per-row composition. No bash string manipulation on
    # untrusted label content -> no backtick interpretation.
    echo "$response" | jq -r --argjson meta "$row" '
        [
            ($meta.label[:22] // "?"),
            ($meta.mov // "null"),
            ($meta.oid[:18] // "?"),
            (.returned // 0 | tostring),
            (.total_above_thresholds // 0 | tostring)
        ] | @tsv' >> "$TMP"
done

# Pretty-print with header.
printf "%-22s %-12s %-18s %5s %5s\n" \
    "label_user" "movability" "anchor_oid" "frags" "above"
printf "%-22s %-12s %-18s %5s %5s\n" \
    "----------------------" "------------" "------------------" "-----" "-----"

# Sort by 'above' (column 5) descending — that's the un-truncated count,
# which is the true signal.
sort -t$'\t' -k5 -nr "$TMP" | while IFS=$'\t' read -r label mov oid frags above; do
    printf "%-22s %-12s %-18s %5s %5s\n" "$label" "$mov" "$oid" "$frags" "$above"
done

echo
total_named=$(echo "$NAMED_JSON" | jq 'length')
oids_with_fragments=$(awk -F'\t' '$5 > 0' "$TMP" | wc -l)

color_green "------------------------------------------------"
echo "Threshold:                 cos>=$COS_THRESHOLD${DIST_THRESHOLD:+, dist<=${DIST_THRESHOLD}m}"
echo "Total named OIDs audited:  $total_named"
echo "OIDs with >=1 above gate:  $oids_with_fragments"
echo
echo "For per-anchor details (JSON):"
echo "  $0 --details                   # all anchors"
echo "  $0 --details <label_user>      # one anchor"
echo "  $0 --cos 0.92 --details        # widen for exploration"

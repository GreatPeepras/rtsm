#!/usr/bin/env bash
# =============================================================================
# fragmentation_audit_2026-06-11.sh
#
# Post-deploy diagnostic. Sweeps every label_user-pinned OID through the
# new POST /objects/{oid}/find_fragments endpoint and prints a summary
# table sorted by fragment count.
#
# Use this to find which named objects have undiscovered duplicates.
#
# Requires: jq, find_fragments deployed (deploy_find_fragments_2026-06-11.sh
# --apply followed by docker compose restart rtsm-dev).
#
# Usage:
#   ./fragmentation_audit_2026-06-11.sh                # summary table
#   ./fragmentation_audit_2026-06-11.sh --details      # full JSON per anchor
#   ./fragmentation_audit_2026-06-11.sh --details <label_user>  # one anchor
#
# Environment:
#   RTSM_BASE  Default http://localhost:8002
# =============================================================================

set -euo pipefail

RTSM_BASE="${RTSM_BASE:-http://localhost:8002}"
MODE="${1:-summary}"
FILTER_LABEL="${2:-}"

color_red()    { printf "\033[31m%s\033[0m\n" "$*"; }
color_green()  { printf "\033[32m%s\033[0m\n" "$*"; }
color_yellow() { printf "\033[33m%s\033[0m\n" "$*"; }

# Pre-flight: endpoint reachable?
if ! curl -s -o /dev/null -f "$RTSM_BASE/objects" 2>/dev/null; then
    color_red "FATAL: cannot reach RTSM at $RTSM_BASE/objects"
    exit 1
fi

# Verify the endpoint exists (find_fragments deployed and rtsm-dev restarted).
if ! curl -s "$RTSM_BASE/openapi.json" | jq -e \
       '.paths["/objects/{oid}/find_fragments"]' >/dev/null 2>&1; then
    color_red "FATAL: /objects/{oid}/find_fragments not registered."
    color_yellow "Did you deploy the patch AND restart rtsm-dev?"
    echo "  cd ~/rtsm/docker && docker compose restart rtsm-dev"
    exit 1
fi

# Fetch the named OIDs.
NAMED_JSON=$(curl -s "$RTSM_BASE/objects" \
    | jq -c '[.objects[] | select(.label_user != null) | {oid: .id, label: .label_user, mov: .movability_class}]')

if [ "$(echo "$NAMED_JSON" | jq 'length')" -eq 0 ]; then
    color_yellow "No label_user-pinned OIDs found. Nothing to audit."
    exit 0
fi

# -----------------------------------------------------------------------
# Per-anchor mode
# -----------------------------------------------------------------------
if [ "$MODE" = "--details" ]; then
    if [ -n "$FILTER_LABEL" ]; then
        SELECTED=$(echo "$NAMED_JSON" \
            | jq -c "[.[] | select(.label == \"$FILTER_LABEL\")]")
        if [ "$(echo "$SELECTED" | jq 'length')" -eq 0 ]; then
            color_red "No named OID matches label_user=$FILTER_LABEL"
            exit 1
        fi
    else
        SELECTED="$NAMED_JSON"
    fi

    echo "$SELECTED" | jq -c '.[]' | while read -r row; do
        oid=$(echo "$row" | jq -r '.oid')
        label=$(echo "$row" | jq -r '.label')
        mov=$(echo "$row" | jq -r '.mov // "null"')
        echo
        color_green "=== $label  ($oid, $mov) ==="
        curl -s -X POST "$RTSM_BASE/objects/$oid/find_fragments" \
             -H 'Content-Type: application/json' -d '{}' | jq .
    done
    exit 0
fi

# -----------------------------------------------------------------------
# Summary table mode (default)
# -----------------------------------------------------------------------
printf "%-22s %-12s %-18s %5s %5s\n" \
    "label_user" "movability" "anchor_oid" "frags" "above"
printf "%-22s %-12s %-18s %5s %5s\n" \
    "----------------------" "------------" "------------------" "-----" "-----"

# Collect results into a tmpfile so we can sort.
TMP=$(mktemp /tmp/fragmentation_audit.XXXXXX)
trap 'rm -f "$TMP"' EXIT

echo "$NAMED_JSON" | jq -c '.[]' | while read -r row; do
    oid=$(echo "$row" | jq -r '.oid')
    label=$(echo "$row" | jq -r '.label')
    mov=$(echo "$row" | jq -r '.mov // "null"')

    response=$(curl -s -X POST "$RTSM_BASE/objects/$oid/find_fragments" \
               -H 'Content-Type: application/json' -d '{}' 2>/dev/null || echo '{}')
    returned=$(echo "$response" | jq -r '.returned // 0')
    total=$(echo "$response" | jq -r '.total_above_thresholds // 0')

    # Truncate long labels for tabular alignment.
    label_disp=$(printf "%.22s" "$label")
    oid_short=$(printf "%.18s" "$oid")

    printf "%-22s %-12s %-18s %5s %5s\n" \
        "$label_disp" "$mov" "$oid_short" "$returned" "$total" >> "$TMP"
done

# Sort by fragment count descending (column 4).
sort -k4 -nr "$TMP"

echo
total_named=$(echo "$NAMED_JSON" | jq 'length')
oids_with_fragments=$(awk '$4 > 0' "$TMP" | wc -l)
total_fragments=$(awk '{sum += $4} END {print sum+0}' "$TMP")

color_green "------------------------------------------------"
echo "Total named OIDs audited:  $total_named"
echo "OIDs with >=1 fragment:    $oids_with_fragments"
echo "Total fragments surfaced:  $total_fragments"
echo
echo "For per-anchor details:"
echo "  $0 --details                   # all anchors"
echo "  $0 --details <label_user>      # one anchor (label must match exactly)"

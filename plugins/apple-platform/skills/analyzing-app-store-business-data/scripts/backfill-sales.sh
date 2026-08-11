#!/usr/bin/env bash
# Backfill Sales & Trends reports into the skill cache via the asc CLI.
# Missing periods (404s) are skipped, existing cache files are not re-fetched.
#
# Usage:
#   backfill-sales.sh --vendor NUM --frequency DAILY|MONTHLY \
#     --from DATE --to DATE [--type SALES] [--subtype SUMMARY] [--version V] \
#     [--profile NAME]
#
# Reports are vendor-wide (all apps under the vendor number), so the cache is
# keyed by vendor, not app.
#
# DATE format matches the frequency: DAILY YYYY-MM-DD, MONTHLY YYYY-MM.

set -euo pipefail

TYPE="SALES"
SUBTYPE="SUMMARY"
FREQUENCY=""
VERSION=""
VENDOR="${ASC_VENDOR_NUMBER:-}"
FROM=""
TO=""
PROFILE=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --type) TYPE="$2"; shift 2 ;;
        --subtype) SUBTYPE="$2"; shift 2 ;;
        --frequency) FREQUENCY="$2"; shift 2 ;;
        --version) VERSION="$2"; shift 2 ;;
        --vendor) VENDOR="$2"; shift 2 ;;
        --from) FROM="$2"; shift 2 ;;
        --to) TO="$2"; shift 2 ;;
        --profile) PROFILE="$2"; shift 2 ;;
        *) echo "unknown flag: $1" >&2; exit 2 ;;
    esac
done

[[ -n "$VENDOR" && -n "$FREQUENCY" && -n "$FROM" && -n "$TO" ]] || {
    echo "required: --vendor (or ASC_VENDOR_NUMBER), --frequency, --from, --to" >&2
    exit 2
}

if [[ -z "$VERSION" ]]; then
    case "$TYPE" in
        SUBSCRIPTION|SUBSCRIPTION_EVENT|SUBSCRIBER) VERSION="1_3" ;;
        *) VERSION="1_0" ;;
    esac
fi

PROFILE_ARGS=()
[[ -n "$PROFILE" ]] && PROFILE_ARGS=(--profile "$PROFILE")

CACHE_DIR="${HOME}/.cache/app-store-business-analyst/vendor-${VENDOR}/sales"
mkdir -p "$CACHE_DIR"

next_period() {
    case "$FREQUENCY" in
        DAILY) date -j -v+1d -f "%Y-%m-%d" "$1" "+%Y-%m-%d" ;;
        MONTHLY) date -j -v+1m -f "%Y-%m" "${1}" "+%Y-%m" ;;
        WEEKLY) date -j -v+7d -f "%Y-%m-%d" "$1" "+%Y-%m-%d" ;;
        YEARLY) echo $(( $1 + 1 )) ;;
        *) echo "unsupported frequency: $FREQUENCY" >&2; exit 2 ;;
    esac
}

fetched=0
skipped=0
missing=0
current="$FROM"

while true; do
    file="${CACHE_DIR}/${TYPE}_${SUBTYPE}_${FREQUENCY}_${current}.tsv"
    if [[ -s "$file" ]]; then
        skipped=$((skipped + 1))
    elif asc "${PROFILE_ARGS[@]}" analytics sales \
            --vendor "$VENDOR" --type "$TYPE" --subtype "$SUBTYPE" \
            --frequency "$FREQUENCY" --version "$VERSION" \
            --date "$current" --decompress --output "$file" >/dev/null 2>&1; then
        fetched=$((fetched + 1))
    else
        rm -f "$file"
        missing=$((missing + 1))
        echo "no report: $current"
    fi

    [[ "$current" == "$TO" ]] && break
    current="$(next_period "$current")"
done

echo "fetched: $fetched, cached already: $skipped, missing: $missing"
echo "cache: $CACHE_DIR"

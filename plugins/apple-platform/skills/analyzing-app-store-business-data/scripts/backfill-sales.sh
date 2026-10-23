#!/usr/bin/env bash
# Backfill Sales & Trends reports into the skill cache via the asc CLI.
# Explicit HTTP 404 responses are skipped; ambiguous errors fail the run.
# Existing versioned cache files are not re-fetched. ASC_REPORT_CACHE_DIR may
# override the cache root; vendor/type/date/version still form the identity.
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
    if [[ "$1" == --help || "$1" == -h ]]; then
        sed -n '5,13p' "$0"
        exit 0
    fi
    [[ $# -ge 2 && "$2" != --* ]] || {
        echo "option requires a value: $1" >&2
        exit 2
    }
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

# Validate and enumerate before creating files or making requests. Calendar
# arithmetic starts on day one, so monthly advances cannot skip February.
PERIODS="$(python3 - "$FREQUENCY" "$FROM" "$TO" <<'PYDATES'
import datetime
import sys
frequency, start, end = sys.argv[1:]
formats = {"DAILY": "%Y-%m-%d", "WEEKLY": "%Y-%m-%d", "MONTHLY": "%Y-%m", "YEARLY": "%Y"}
try:
    pattern = formats[frequency]
    first = datetime.datetime.strptime(start, pattern).date()
    last = datetime.datetime.strptime(end, pattern).date()
    if first.strftime(pattern) != start or last.strftime(pattern) != end or first > last:
        raise ValueError("dates must use the documented format and from <= to")
    current = first
    periods = []
    while current <= last:
        periods.append(current.strftime(pattern))
        if current == last:
            break
        if frequency == "MONTHLY":
            current = datetime.date(current.year + (current.month == 12), current.month % 12 + 1, 1)
        elif frequency == "YEARLY":
            current = datetime.date(current.year + 1, 1, 1)
        else:
            current += datetime.timedelta(days=7 if frequency == "WEEKLY" else 1)
    if not periods or periods[-1] != end:
        raise ValueError("end date is not on the requested frequency sequence")
except (KeyError, ValueError, OverflowError) as error:
    sys.exit(f"invalid report range: {error}")
print("\n".join(periods))
PYDATES
)"

[[ "$VENDOR" =~ ^[0-9]+$ && "$TYPE" =~ ^[A-Z_]+$ && "$SUBTYPE" =~ ^[A-Z_]+$ && "$VERSION" =~ ^[0-9_]+$ ]] || {
    echo "invalid vendor, report type, subtype, or version" >&2
    exit 2
}
CACHE_DIR="${ASC_REPORT_CACHE_DIR:-${HOME}/.cache/app-store-business-analyst}/vendor-${VENDOR}/sales"
mkdir -p "$CACHE_DIR"
DOWNLOAD=""
ERROR_LOG=""
cleanup() {
    [[ -z "$DOWNLOAD" ]] || rm -f "$DOWNLOAD"
    [[ -z "$ERROR_LOG" ]] || rm -f "$ERROR_LOG"
}
trap cleanup EXIT

fetched=0
skipped=0
missing=0
while IFS= read -r current; do
    # Version belongs in the cache identity; never overwrite a different schema.
    file="${CACHE_DIR}/${TYPE}_${SUBTYPE}_${FREQUENCY}_${current}_v${VERSION}.tsv"
    if [[ -s "$file" ]]; then
        skipped=$((skipped + 1))
        continue
    fi
    DOWNLOAD="$(mktemp "${CACHE_DIR}/.download.XXXXXX")"
    ERROR_LOG="$(mktemp "${CACHE_DIR}/.error.XXXXXX")"
    if asc "${PROFILE_ARGS[@]}" analytics sales \
            --vendor "$VENDOR" --type "$TYPE" --subtype "$SUBTYPE" \
            --frequency "$FREQUENCY" --version "$VERSION" \
            --date "$current" --decompress --output "$DOWNLOAD" >"$ERROR_LOG" 2>&1; then
        [[ -s "$DOWNLOAD" ]] || { echo "empty report: $current" >&2; exit 1; }
        mv "$DOWNLOAD" "$file"
        fetched=$((fetched + 1))
    elif grep -Eq '(^|[[:space:]:])HTTP(/[0-9.]+)?[[:space:]:]+404([^0-9]|$)' "$ERROR_LOG"; then
        missing=$((missing + 1))
        echo "no report (404): $current"
    else
        echo "report request failed: $current" >&2
        cat "$ERROR_LOG" >&2
        exit 1
    fi
    cleanup
    DOWNLOAD=""
    ERROR_LOG=""
done <<< "$PERIODS"

echo "fetched: $fetched, cached already: $skipped, missing: $missing"
echo "cache: $CACHE_DIR"

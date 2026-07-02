#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SWIFTC="${SWIFTC:-$(command -v swiftc || true)}"

if [[ -z "$SWIFTC" ]]; then
  if [[ "${REQUIRE_SWIFTC:-0}" == "1" ]]; then
    echo "error: swiftc was not found" >&2
    exit 1
  fi
  echo "SKIP: swiftc was not found; markdown and metadata validation can still run."
  exit 0
fi

MIN_SWIFT_MAJOR=6
MIN_SWIFT_MINOR=3
VERSION_OUTPUT="$($SWIFTC --version 2>&1 | head -n 1)"
if [[ ! "$VERSION_OUTPUT" =~ Swift[[:space:]]version[[:space:]]([0-9]+)\.([0-9]+) ]]; then
  echo "error: could not parse swiftc version: $VERSION_OUTPUT" >&2
  exit 1
fi
SWIFT_MAJOR="${BASH_REMATCH[1]}"
SWIFT_MINOR="${BASH_REMATCH[2]}"
if (( SWIFT_MAJOR < MIN_SWIFT_MAJOR || (SWIFT_MAJOR == MIN_SWIFT_MAJOR && SWIFT_MINOR < MIN_SWIFT_MINOR) )); then
  echo "error: this skill requires the current Swift baseline (6.3 or newer) in Swift 6 language mode: $VERSION_OUTPUT" >&2
  exit 1
fi
printf 'TOOLCHAIN  %s\n' "$VERSION_OUTPUT"

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

COMMON_FLAGS=(
  -emit-module
  -parse-as-library
  -swift-version 6
  -strict-concurrency=complete
  -warnings-as-errors
)

module_name() {
  local base
  base="$(basename "$1" .swift)"
  printf 'Fixture_%s' "${base//[^A-Za-z0-9_]/_}"
}

check_positive() {
  local file="$1"
  local module
  module="$(module_name "$file")"
  echo "COMPILE    $(basename "$file")"
  "$SWIFTC" "${COMMON_FLAGS[@]}" \
    -module-name "$module" \
    -emit-module-path "$TMP/$module.swiftmodule" \
    "$file"
}

expected_fragments() {
  local file="$1"
  sed -n "s/^[[:space:]]*\/\/[[:space:]]*expected-error:[[:space:]]*//p" "$file"
}

check_negative() {
  local file="$1"
  local module diagnostic fragment_count=0
  module="$(module_name "$file")"
  diagnostic="$TMP/$(basename "$file").txt"
  echo "REJECT     $(basename "$file")"

  if "$SWIFTC" "${COMMON_FLAGS[@]}" \
      -module-name "$module" \
      -emit-module-path "$TMP/$module.swiftmodule" \
      "$file" >"$diagnostic" 2>&1; then
    echo "error: compile-fail fixture unexpectedly compiled: $file" >&2
    exit 1
  fi

  while IFS= read -r fragment; do
    [[ -z "$fragment" ]] && continue
    fragment_count=$((fragment_count + 1))
    if ! grep -Fq -- "$fragment" "$diagnostic"; then
      echo "error: expected diagnostic fragment was not emitted for $file: $fragment" >&2
      cat "$diagnostic" >&2
      exit 1
    fi
  done < <(expected_fragments "$file")

  if [[ "$fragment_count" -eq 0 ]]; then
    echo "error: compile-fail fixture has no // expected-error: marker: $file" >&2
    exit 1
  fi
}

check_runtime() {
  local executable="$TMP/CorePatternsRuntimeChecks"
  echo "RUN        CorePatternsRuntimeChecks.swift"
  "$SWIFTC" \
    -parse-as-library \
    -swift-version 6 \
    -strict-concurrency=complete \
    -warnings-as-errors \
    "$ROOT/examples/CorePatterns.swift" \
    "$ROOT/examples/CorePatternsRuntimeChecks.swift" \
    -o "$executable"
  "$executable"
}

check_positive "$ROOT/examples/CorePatterns.swift"
check_positive "$ROOT/examples/CurrentSwiftPatterns.swift"
check_runtime
check_negative "$ROOT/examples/CompileFailWrongID.swift"
check_negative "$ROOT/examples/CompileFailBypassValidation.swift"
check_negative "$ROOT/examples/CompileFailUseAfterConsume.swift"
check_negative "$ROOT/examples/CompileFailWrongTypestate.swift"
check_negative "$ROOT/examples/CompileFailWrongTrustState.swift"

echo "PASS: Swift 6 examples preserve their intended compile/pass, runtime, and compile/fail behavior under the selected compiler."

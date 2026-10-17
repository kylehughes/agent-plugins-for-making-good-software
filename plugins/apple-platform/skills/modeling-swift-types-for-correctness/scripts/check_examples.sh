#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

arguments=("$ROOT/scripts/swift_compile_checks.py" "$ROOT/examples/compile-checks.json")
if [[ "${REQUIRE_SWIFTC:-0}" != "1" ]]; then
  arguments+=(--allow-unavailable)
fi

python3 "${arguments[@]}"

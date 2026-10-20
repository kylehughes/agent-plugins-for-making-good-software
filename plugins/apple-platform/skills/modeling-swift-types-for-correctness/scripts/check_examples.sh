#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

arguments=("$ROOT/scripts/swift_compile_checks.py" "$ROOT/examples/compile-checks.json")
if [[ "${REQUIRE_SWIFTC:-0}" != "1" ]]; then
  arguments+=(--allow-unavailable)
fi

python3 "${arguments[@]}"

if [[ "${CHECK_SWIFT_COMPILER_CORPUS:-0}" == "1" ]]; then
  corpus_arguments=(
    "$ROOT/scripts/swift_compiler_corpus.py"
    "$ROOT/examples/compiler-corpus-map.json"
  )
  if [[ -n "${SWIFT_FRONTEND:-}" ]]; then
    corpus_arguments+=(--swiftc "$SWIFT_FRONTEND")
  fi
  python3 "${corpus_arguments[@]}"
fi

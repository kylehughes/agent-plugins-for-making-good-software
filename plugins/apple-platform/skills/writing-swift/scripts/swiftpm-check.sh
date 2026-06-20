#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage: swiftpm-check.sh [options] [package-directory]

Options:
  --configuration debug|release  Build configuration (default: debug)
  --target NAME                  Build only this target before tests
  --filter VALUE                 Pass a filter to swift test
  --skip-tests                   Skip swift test
  --scratch-path PATH            Use an explicit SwiftPM scratch path
  -h, --help                     Show this help

The script does not run `swift package update`.
USAGE
}

configuration=debug
target=""
filter=""
skip_tests=0
scratch_path=""
root="."

while (($#)); do
  case "$1" in
    --configuration)
      [[ $# -ge 2 ]] || { printf '%s\n' '--configuration requires a value' >&2; exit 2; }
      configuration="$2"; shift 2 ;;
    --target)
      [[ $# -ge 2 ]] || { printf '%s\n' '--target requires a name' >&2; exit 2; }
      target="$2"; shift 2 ;;
    --filter)
      [[ $# -ge 2 ]] || { printf '%s\n' '--filter requires a value' >&2; exit 2; }
      filter="$2"; shift 2 ;;
    --scratch-path)
      [[ $# -ge 2 ]] || { printf '%s\n' '--scratch-path requires a path' >&2; exit 2; }
      scratch_path="$2"; shift 2 ;;
    --skip-tests) skip_tests=1; shift ;;
    -h|--help) usage; exit 0 ;;
    -*) printf 'Unknown option: %s\n' "$1" >&2; usage >&2; exit 2 ;;
    *) root="$1"; shift ;;
  esac
done

case "$configuration" in
  debug|release) ;;
  *) printf 'Invalid configuration: %s\n' "$configuration" >&2; exit 2 ;;
esac

command -v swift >/dev/null 2>&1 || {
  printf '%s\n' 'swift is not installed or not on PATH.' >&2
  exit 127
}

root="$(cd "$root" && pwd -P)"
[[ -f "$root/Package.swift" ]] || {
  printf 'Package.swift not found in %s\n' "$root" >&2
  exit 2
}
cd "$root"

common=(--configuration "$configuration")
if [[ -n "$scratch_path" ]]; then
  common+=(--scratch-path "$scratch_path")
fi

printf '%s\n' '== Swift toolchain =='
swift --version

printf '%s\n' '== Validate manifest =='
swift package dump-package >/dev/null

printf '%s\n' '== Build =='
build=(swift build "${common[@]}")
if [[ -n "$target" ]]; then
  build+=(--target "$target")
fi
"${build[@]}"

if ((skip_tests == 0)); then
  printf '%s\n' '== Test =='
  test=(swift test "${common[@]}")
  if [[ -n "$filter" ]]; then
    test+=(--filter "$filter")
  fi
  "${test[@]}"
fi

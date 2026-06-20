#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage: lint-changed-swift.sh [--allow-defaults] [--base REV] [file.swift ...]

Runs a non-mutating swift-format lint over explicit files or changed Swift files.
By default it requires a checked-in .swift-format configuration at the Git root.
Relative explicit paths are resolved from the invocation directory.
USAGE
}

allow_defaults=0
base=""
raw_files=()
invocation_dir="$(pwd -P)"

while (($#)); do
  case "$1" in
    --allow-defaults) allow_defaults=1; shift ;;
    --base)
      [[ $# -ge 2 ]] || { printf '%s\n' '--base requires a revision' >&2; exit 2; }
      base="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    --) shift; raw_files+=("$@"); break ;;
    -*) printf 'Unknown option: %s\n' "$1" >&2; usage >&2; exit 2 ;;
    *) raw_files+=("$1"); shift ;;
  esac
done

command -v swift-format >/dev/null 2>&1 || {
  printf '%s\n' 'swift-format is not installed or not on PATH.' >&2
  exit 127
}

root="$(git rev-parse --show-toplevel 2>/dev/null || printf '%s\n' "$invocation_dir")"
root="$(cd "$root" && pwd -P)"
files=()

add_file() {
  local file="$1"
  local existing

  [[ "$file" == *.swift ]] || {
    printf 'Not a Swift source file: %s\n' "$file" >&2
    exit 2
  }
  [[ -f "$file" ]] || {
    printf 'Swift source file not found: %s\n' "$file" >&2
    exit 2
  }
  case "$file" in
    "$root"/.build/*|"$root"/DerivedData/*|"$root"/Pods/*|"$root"/Carthage/*|"$root"/.git/*) return 0 ;;
  esac
  for existing in "${files[@]}"; do
    [[ "$existing" == "$file" ]] && return 0
  done
  files+=("$file")
}

if ((${#raw_files[@]} > 0)); then
  for file in "${raw_files[@]}"; do
    if [[ "$file" != /* ]]; then
      file="$invocation_dir/$file"
    fi
    add_file "$file"
  done
else
  git -C "$root" rev-parse --is-inside-work-tree >/dev/null 2>&1 || {
    printf '%s\n' 'Changed-file discovery requires a Git worktree or explicit Swift file paths.' >&2
    exit 2
  }
  cd "$root"

  if [[ -n "$base" ]]; then
    while IFS= read -r -d '' file; do add_file "$root/$file"; done \
      < <(git diff --name-only --diff-filter=ACMR -z "$base" -- '*.swift')
    while IFS= read -r -d '' file; do add_file "$root/$file"; done \
      < <(git ls-files --others --exclude-standard -z -- '*.swift')
  else
    while IFS= read -r -d '' file; do add_file "$root/$file"; done \
      < <(git diff --name-only --diff-filter=ACMR -z -- '*.swift')
    while IFS= read -r -d '' file; do add_file "$root/$file"; done \
      < <(git diff --cached --name-only --diff-filter=ACMR -z -- '*.swift')
    while IFS= read -r -d '' file; do add_file "$root/$file"; done \
      < <(git ls-files --others --exclude-standard -z -- '*.swift')
  fi
fi

if ((${#files[@]} == 0)); then
  printf '%s\n' 'No Swift files to lint.'
  exit 0
fi

config=""
for candidate in "$root/.swift-format" "$root/.swift-format.json"; do
  if [[ -f "$candidate" ]]; then
    config="$candidate"
    break
  fi
done

args=(lint --strict --parallel)
if [[ -n "$config" ]]; then
  args+=(--configuration "$config")
elif ((allow_defaults == 0)); then
  printf '%s\n' 'No checked-in .swift-format configuration found at the Git root.' >&2
  printf '%s\n' 'Pass --allow-defaults only when default swift-format rules are intentional.' >&2
  exit 2
fi

printf 'Linting %d Swift file(s).\n' "${#files[@]}"
swift-format "${args[@]}" -- "${files[@]}"

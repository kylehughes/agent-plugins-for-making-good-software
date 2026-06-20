#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage: swift-project-context.sh [--deep] [repository]

Prints read-only Swift project context. --deep also asks SwiftPM/Xcode to inspect
manifests and schemes; those commands may load package plugins or manifest code.
USAGE
}

deep=0
root="."
while (($#)); do
  case "$1" in
    --deep) deep=1 ;;
    -h|--help) usage; exit 0 ;;
    -*) printf 'Unknown option: %s\n' "$1" >&2; usage >&2; exit 2 ;;
    *) root="$1" ;;
  esac
  shift
done

if [[ ! -d "$root" ]]; then
  printf 'Not a directory: %s\n' "$root" >&2
  exit 2
fi

root="$(cd "$root" && pwd -P)"
printf 'Repository: %s\n' "$root"

if git -C "$root" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  git_root="$(git -C "$root" rev-parse --show-toplevel)"
  printf 'Git root:   %s\n' "$git_root"
  printf 'Branch:     %s\n' "$(git -C "$root" branch --show-current 2>/dev/null || true)"
  printf 'Changes:    %s\n' "$(git -C "$root" status --short | wc -l | tr -d ' ')"
else
  git_root="$root"
  printf 'Git:        not detected\n'
fi

printf '\n== Toolchains ==\n'
if command -v swift >/dev/null 2>&1; then
  swift --version
else
  printf 'swift: not found\n'
fi
if command -v xcodebuild >/dev/null 2>&1; then
  xcodebuild -version
else
  printf 'xcodebuild: not found\n'
fi
if command -v xcrun >/dev/null 2>&1; then
  printf '%s\n' '-- Xcode-selected Swift --'
  xcrun swift --version || true
fi
if command -v xcode-select >/dev/null 2>&1; then
  printf 'Developer dir: %s\n' "$(xcode-select -p 2>/dev/null || printf unknown)"
fi

printf '\n== Repository instructions and configuration ==\n'
find "$git_root" -maxdepth 3 -type f \( \
  -name AGENTS.md -o -name CLAUDE.md -o -name GEMINI.md -o -name CONTRIBUTING.md -o \
  -name copilot-instructions.md -o -name .swift-format -o -name .swiftformat -o \
  -name .swiftlint.yml -o -name .swiftlint.yaml -o -name .periphery.yml -o \
  -name Package.swift -o -name Package.resolved -o -name '*.xctestplan' -o \
  -name project.yml -o -name Project.swift -o -name Tuist.swift -o \
  -name Makefile -o -name justfile -o -name Mintfile -o -name mise.toml -o \
  -name .swift-version -o -name .xcode-version \
\) -not -path '*/.build/*' -not -path '*/DerivedData/*' -print | sort

printf '\n== Xcode containers ==\n'
find "$git_root" -maxdepth 3 \( -name '*.xcodeproj' -o -name '*.xcworkspace' \) \
  -not -path '*/.build/*' -not -path '*/DerivedData/*' -print | sort

if [[ -f "$git_root/Package.swift" ]]; then
  printf '\n== Package manifest signals ==\n'
  sed -n '1,12p' "$git_root/Package.swift"
  grep -nE 'swiftLanguageModes|swiftLanguageVersions|defaultIsolation|enableUpcomingFeature|enableExperimentalFeature|swiftSettings|platforms:' \
    "$git_root/Package.swift" || true
fi

printf '\n== Swift source inventory ==\n'
source_count="$(find "$git_root" -type f -name '*.swift' \
  -not -path '*/.build/*' -not -path '*/DerivedData/*' -not -path '*/.git/*' \
  -not -path '*/Pods/*' -not -path '*/Carthage/*' -not -path '*/vendor/*' \
  | wc -l | tr -d ' ')"
test_count="$(find "$git_root" -type f -name '*.swift' \
  \( -path '*/Tests/*' -o -path '*Tests.swift' -o -path '*/UITests/*' \) \
  -not -path '*/.build/*' -not -path '*/DerivedData/*' -not -path '*/.git/*' \
  -not -path '*/Pods/*' -not -path '*/Carthage/*' -not -path '*/vendor/*' \
  | wc -l | tr -d ' ')"
printf 'Swift files: %s\n' "$source_count"
printf 'Likely test files: %s\n' "$test_count"

printf '\n== Test framework imports ==\n'
grep -RIl --include='*.swift' --exclude-dir=.build --exclude-dir=DerivedData --exclude-dir=.git \
  --exclude-dir=Pods --exclude-dir=Carthage --exclude-dir=vendor \
  -E '^import (Testing|XCTest)$' "$git_root" 2>/dev/null \
  | while IFS= read -r file; do
      imports="$(grep -E '^import (Testing|XCTest)$' "$file" | paste -sd ',' -)"
      printf '%s: %s\n' "${file#"$git_root"/}" "$imports"
    done | head -n 80 || true

if ((deep)); then
  if [[ -f "$git_root/Package.swift" ]] && command -v swift >/dev/null 2>&1; then
    printf '\n== swift package dump-package ==\n'
    (cd "$git_root" && swift package dump-package)
  fi

  if command -v xcodebuild >/dev/null 2>&1; then
    workspace="$(find "$git_root" -maxdepth 2 -name '*.xcworkspace' -not -path '*/project.xcworkspace' -print -quit)"
    project="$(find "$git_root" -maxdepth 2 -name '*.xcodeproj' -print -quit)"
    if [[ -n "$workspace" ]]; then
      printf '\n== xcodebuild -list (workspace) ==\n'
      xcodebuild -list -workspace "$workspace"
    elif [[ -n "$project" ]]; then
      printf '\n== xcodebuild -list (project) ==\n'
      xcodebuild -list -project "$project"
    fi
  fi
fi

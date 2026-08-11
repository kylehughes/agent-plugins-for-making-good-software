#!/bin/bash

#===============================================================================
#  record-xcuitest-video.sh - Record a focused XCUITest run as a simulator video
#
#  USAGE:
#    ./record-xcuitest-video.sh --name <artifact-name> \
#      --only-testing <Target/Suite/test> [--only-testing <...>] \
#      [--project <path> | --workspace <path>] --scheme <name> \
#      [--test-plan <name>] [--destination <spec>] \
#      [--derived-data-path <path>] [--env-script <path>] \
#      [--repo-root <path>] \
#      [record-ui-automation-video.sh options...]
#
#  DESCRIPTION:
#    Wraps record-ui-automation-video.sh with the reliable XCUITest recipe so
#    callers never assemble it by hand: runs xcodebuild build-for-testing in
#    --prepare and records xcodebuild test-without-building.
#
#    --project/--workspace, --scheme, --test-plan, --destination, and
#    --derived-data-path configure the xcodebuild invocation. When --project
#    and --workspace are both omitted, the script looks for a single
#    *.xcworkspace (preferred) or *.xcodeproj in the repo root. --scheme is
#    always required. --destination falls back to
#    "platform=iOS Simulator,id=$SIM_UDID" when SIM_UDID is set; otherwise
#    pass --destination explicitly. --repo-root defaults to
#    `git rev-parse --show-toplevel`, then the current directory.
#
#    --env-script, if given, is sourced before the test phase runs (for
#    example to load auth or environment secrets). It is skipped silently
#    when omitted.
#
#    Unrecognized options are forwarded to record-ui-automation-video.sh
#    (for example --keep-raw, --no-compress, --sim-udid, --output-dir).
#
#    See the skill's SKILL.md for the full rationale.
#
#  REQUIREMENTS:
#    bash >= 3.x
#    Xcode command-line tools
#
#  EXIT CODES:
#    0  success
#    1  usage error (bad flags, etc.)
#    >1 propagated from record-ui-automation-video.sh, xcodebuild, or the
#       recording pipeline
#
#  LICENSE:
#    Copyright (c) 2026 Kyle Hughes. All rights reserved.
#===============================================================================

set -Eeuo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SELF="$SCRIPT_DIR/$(basename "${BASH_SOURCE[0]}")"

usage() {
  cat <<'EOF'
Usage:
  record-xcuitest-video.sh --name <artifact-name> \
    --only-testing <Target/Suite/test> [--only-testing <...>] \
    [--project <path> | --workspace <path>] --scheme <name> \
    [--test-plan <name>] [--destination <spec>] \
    [--derived-data-path <path>] [--env-script <path>] \
    [--repo-root <path>] \
    [record-ui-automation-video.sh options...]

Options:
  --name <name>              Short scenario name used in artifact paths.
  --only-testing <spec>      XCTest identifier to run. Repeatable.
  --project <path>           Xcode project. Mutually exclusive with
                              --workspace.
  --workspace <path>         Xcode workspace. Mutually exclusive with
                              --project. When neither is given, the script
                              looks for a single .xcworkspace (preferred) or
                              .xcodeproj in the repo root.
  --scheme <name>            Xcode scheme. Required.
  --test-plan <name>         Test plan passed as -testPlan.
  --destination <spec>       xcodebuild -destination. Defaults to
                              "platform=iOS Simulator,id=$SIM_UDID" when
                              SIM_UDID is set.
  --derived-data-path <path> xcodebuild -derivedDataPath.
  --env-script <path>        Shell script sourced before the test phase runs.
  --repo-root <path>         Repo root used for project/workspace discovery.
                              Defaults to `git rev-parse --show-toplevel`,
                              then the current directory.
  --help                     Show this help.

Unrecognized options are forwarded to record-ui-automation-video.sh (for
example --keep-raw, --no-compress, --sim-udid, --output-dir).
EOF
}

# Resolves the repo root: --repo-root, else `git rev-parse --show-toplevel`,
# else the current directory.
resolve_repo_root() {
  local repo_root="$1"

  if [ -n "$repo_root" ]; then
    printf "%s" "$repo_root"
    return
  fi

  if repo_root="$(git rev-parse --show-toplevel 2>/dev/null)"; then
    printf "%s" "$repo_root"
    return
  fi

  pwd
}

# Finds exactly one *.xcworkspace (preferred) or *.xcodeproj in the repo root
# when neither --project nor --workspace was given.
discover_project_or_workspace() {
  local repo_root="$1"
  local workspaces=()
  local projects=()
  local entry=""

  while IFS= read -r entry; do
    [ -n "$entry" ] && workspaces+=("$entry")
  done < <(find "$repo_root" -maxdepth 1 -name "*.xcworkspace")

  if [ "${#workspaces[@]}" -eq 1 ]; then
    WORKSPACE="${workspaces[0]}"
    return
  fi

  if [ "${#workspaces[@]}" -gt 1 ]; then
    echo "Error: multiple .xcworkspace files found in $repo_root. Pass --project or --workspace." >&2
    exit 1
  fi

  while IFS= read -r entry; do
    [ -n "$entry" ] && projects+=("$entry")
  done < <(find "$repo_root" -maxdepth 1 -name "*.xcodeproj")

  if [ "${#projects[@]}" -eq 1 ]; then
    PROJECT="${projects[0]}"
    return
  fi

  echo "Error: could not find exactly one .xcworkspace or .xcodeproj in $repo_root. Pass --project or --workspace." >&2
  exit 1
}

# Fills XCODEBUILD_COMMON_ARGS with the fixed arguments both phases must
# pass, built from the resolved configuration.
build_xcodebuild_common_args() {
  XCODEBUILD_COMMON_ARGS=()

  if [ -n "$WORKSPACE" ]; then
    XCODEBUILD_COMMON_ARGS+=(-workspace "$WORKSPACE")
  else
    XCODEBUILD_COMMON_ARGS+=(-project "$PROJECT")
  fi

  XCODEBUILD_COMMON_ARGS+=(-scheme "$SCHEME")

  if [ -n "$TEST_PLAN" ]; then
    XCODEBUILD_COMMON_ARGS+=(-testPlan "$TEST_PLAN")
  fi

  XCODEBUILD_COMMON_ARGS+=(-destination "$DESTINATION")

  if [ -n "$DERIVED_DATA_PATH" ]; then
    XCODEBUILD_COMMON_ARGS+=(-derivedDataPath "$DERIVED_DATA_PATH")
  fi
}

run_prepare_phase() {
  build_xcodebuild_common_args

  cd "$REPO_ROOT"

  echo "Building for testing before recording starts..."
  xcodebuild build-for-testing "${XCODEBUILD_COMMON_ARGS[@]}"
}

run_test_phase() {
  build_xcodebuild_common_args

  cd "$REPO_ROOT"

  if [ -n "$ENV_SCRIPT" ]; then
    [ -f "$ENV_SCRIPT" ] || { echo "Error: --env-script not found: $ENV_SCRIPT" >&2; exit 1; }
    # shellcheck disable=SC1090
    source "$ENV_SCRIPT"
  fi

  xcodebuild test-without-building "${XCODEBUILD_COMMON_ARGS[@]}" "$@"
}

# Re-entrant invocations (__prepare/__test) receive the resolved configuration
# as explicit flags rather than relying on inherited environment state.
reentrant_config_args() {
  local args=()

  args+=(--repo-root "$REPO_ROOT")

  if [ -n "$WORKSPACE" ]; then
    args+=(--workspace "$WORKSPACE")
  else
    args+=(--project "$PROJECT")
  fi

  args+=(--scheme "$SCHEME")

  if [ -n "$TEST_PLAN" ]; then
    args+=(--test-plan "$TEST_PLAN")
  fi

  args+=(--destination "$DESTINATION")

  if [ -n "$DERIVED_DATA_PATH" ]; then
    args+=(--derived-data-path "$DERIVED_DATA_PATH")
  fi

  if [ -n "$ENV_SCRIPT" ]; then
    args+=(--env-script "$ENV_SCRIPT")
  fi

  printf "%s\n" "${args[@]}"
}

parse_config_args() {
  REPO_ROOT_OPTION=""
  PROJECT=""
  WORKSPACE=""
  SCHEME=""
  TEST_PLAN=""
  DESTINATION=""
  DERIVED_DATA_PATH=""
  ENV_SCRIPT=""
  REMAINING_ARGS=()

  while [ "$#" -gt 0 ]; do
    case "$1" in
      --repo-root)
        [ "$#" -ge 2 ] || { echo "Error: --repo-root requires a value" >&2; exit 1; }
        REPO_ROOT_OPTION="$2"
        shift 2
        ;;
      --project)
        [ "$#" -ge 2 ] || { echo "Error: --project requires a value" >&2; exit 1; }
        [ -z "$WORKSPACE" ] || { echo "Error: --project and --workspace are mutually exclusive" >&2; exit 1; }
        PROJECT="$2"
        shift 2
        ;;
      --workspace)
        [ "$#" -ge 2 ] || { echo "Error: --workspace requires a value" >&2; exit 1; }
        [ -z "$PROJECT" ] || { echo "Error: --project and --workspace are mutually exclusive" >&2; exit 1; }
        WORKSPACE="$2"
        shift 2
        ;;
      --scheme)
        [ "$#" -ge 2 ] || { echo "Error: --scheme requires a value" >&2; exit 1; }
        SCHEME="$2"
        shift 2
        ;;
      --test-plan)
        [ "$#" -ge 2 ] || { echo "Error: --test-plan requires a value" >&2; exit 1; }
        TEST_PLAN="$2"
        shift 2
        ;;
      --destination)
        [ "$#" -ge 2 ] || { echo "Error: --destination requires a value" >&2; exit 1; }
        DESTINATION="$2"
        shift 2
        ;;
      --derived-data-path)
        [ "$#" -ge 2 ] || { echo "Error: --derived-data-path requires a value" >&2; exit 1; }
        DERIVED_DATA_PATH="$2"
        shift 2
        ;;
      --env-script)
        [ "$#" -ge 2 ] || { echo "Error: --env-script requires a value" >&2; exit 1; }
        ENV_SCRIPT="$2"
        shift 2
        ;;
      *)
        REMAINING_ARGS+=("$1")
        shift
        ;;
    esac
  done

  REPO_ROOT="$(resolve_repo_root "$REPO_ROOT_OPTION")"

  if [ -z "$PROJECT" ] && [ -z "$WORKSPACE" ]; then
    discover_project_or_workspace "$REPO_ROOT"
  fi

  if [ -z "$SCHEME" ]; then
    echo "Error: no scheme configured. Pass --scheme <name>." >&2
    exit 1
  fi

  if [ -z "$DESTINATION" ]; then
    if [ -n "${SIM_UDID:-}" ]; then
      DESTINATION="platform=iOS Simulator,id=$SIM_UDID"
    else
      echo "Error: no destination configured. Pass --destination <spec> or set SIM_UDID." >&2
      exit 1
    fi
  fi
}

main() {
  local name=""
  local only_testing_args=()
  local record_args=()
  local config_args=()

  if [ "$#" -eq 0 ]; then
    usage >&2
    exit 1
  fi

  parse_config_args "$@"
  set -- "${REMAINING_ARGS[@]}"

  while [ "$#" -gt 0 ]; do
    case "$1" in
      --name)
        [ "$#" -ge 2 ] || { echo "Error: --name requires a value" >&2; exit 1; }
        name="$2"
        shift 2
        ;;
      --only-testing)
        [ "$#" -ge 2 ] || { echo "Error: --only-testing requires a value" >&2; exit 1; }
        only_testing_args+=("-only-testing:$2")
        shift 2
        ;;
      *)
        record_args+=("$1")
        shift
        ;;
    esac
  done

  if [ -z "$name" ]; then
    echo "Error: --name is required" >&2
    usage >&2
    exit 1
  fi

  if [ "${#only_testing_args[@]}" -eq 0 ]; then
    echo "Error: at least one --only-testing <Target/Suite/test> is required" >&2
    usage >&2
    exit 1
  fi

  while IFS= read -r arg; do
    config_args+=("$arg")
  done < <(reentrant_config_args)

  # The recorded command is passed as argv — no shell string splicing — and the
  # prepare phase re-enters this script, so quoting survives spaces in paths.
  # The resolved configuration is passed as explicit flags so re-entrant
  # invocations do not depend on inherited environment state.
  exec "$SCRIPT_DIR/record-ui-automation-video.sh" \
    run \
    --name "$name" \
    --prepare "bash $(printf '%q' "$SELF") __prepare $(quote_args "${config_args[@]}")" \
    ${record_args[@]+"${record_args[@]}"} \
    -- \
    bash "$SELF" __test "${config_args[@]}" "${only_testing_args[@]}"
}

quote_args() {
  local output=""
  local arg

  for arg in "$@"; do
    local quoted
    printf -v quoted "%q" "$arg"
    output="${output}${quoted} "
  done

  printf "%s" "${output% }"
}

case "${1:-}" in
  --help|-h)
    usage >&2
    exit 1
    ;;
  __prepare)
    shift
    parse_config_args "$@"
    run_prepare_phase
    ;;
  __test)
    shift
    parse_config_args "$@"
    set -- "${REMAINING_ARGS[@]}"
    run_test_phase "$@"
    ;;
  *)
    main "$@"
    ;;
esac

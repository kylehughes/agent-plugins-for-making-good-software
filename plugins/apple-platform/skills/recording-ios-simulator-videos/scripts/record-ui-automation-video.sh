#!/bin/bash

#===============================================================================
#  record-ui-automation-video.sh - Record simulator video around an automation run
#
#  USAGE:
#    record-ui-automation-video.sh run [options] -- <command> [args...]
#    record-ui-automation-video.sh run [options] --duration <seconds>
#    record-ui-automation-video.sh start [options]
#    record-ui-automation-video.sh stop [options]
#
#  REQUIREMENTS:
#    bash >= 3.x, xcrun
#    ffmpeg and ffprobe are optional and enable compressed handoff artifacts.
#
#  EXIT CODES:
#    0  success
#    1  usage error or recording failure
#    2  missing required dependency
#    Wrapped command status is returned as-is when using `run`
#
#  LICENSE:
#    Copyright (c) 2026 Kyle Hughes. All rights reserved.
#===============================================================================

set -Eeuo pipefail

usage() {
  cat <<'EOF'
Usage:
  record-ui-automation-video.sh run [options] -- <command> [args...]
  record-ui-automation-video.sh run [options] --duration <seconds>
  record-ui-automation-video.sh start [options]
  record-ui-automation-video.sh stop [options]

Options:
  --name <name>        Short scenario name used in artifact paths.
  --output-dir <path>  Artifact root. Defaults to UI_AUTOMATION_VIDEO_DIR,
                       DERIVED_DATA_PATH/UIAutomationVideos, or
                       DerivedData.noindex/UIAutomationVideos.
  --run-dir <path>     Existing run directory to stop.
  --sim-udid <udid>    Simulator UDID. Defaults to SIM_UDID.
  --duration <seconds> Record for a fixed duration. Only valid with run and no
                       command after --.
  --prepare <command>  Shell command to run before recording starts. Useful for
                       build, install, auth seeding, or other setup.
  --start-on-app [id]  With run, start recording only after a new app process
                       appears. Defaults to BUNDLE_ID. XCTest-like commands
                       record immediately because late-started recordings can
                       become stale during the app run.
                       Override with UI_AUTOMATION_VIDEO_ALLOW_XCTEST_START_ON_APP=1.
  --start-timeout <s>  Seconds to wait for --start-on-app. Default: 300.
  --post-start-duration <s>
                       Keep recording for at least this many seconds after
                       recording starts, even if the command exits first.
  --no-compress        Keep the raw recording and skip ffmpeg.
  --keep-raw           Keep the raw recording after successful compression.
  --help               Show this help.
EOF
}

fail() {
  echo "Error: $*" >&2
  exit 1
}

missing_dependency() {
  echo "Error: $* is required" >&2
  exit 2
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

sanitize_slug() {
  local raw="$1"
  local slug

  slug="$(
    printf "%s" "$raw" |
      tr "[:upper:]" "[:lower:]" |
      sed -E 's/[^a-z0-9._-]+/-/g; s/^-+//; s/-+$//; s/-+/-/g'
  )"

  if [ -z "$slug" ]; then
    slug="ui-automation-run"
  fi

  printf "%s" "$slug"
}

absolute_directory() {
  local directory="$1"

  mkdir -p "$directory"
  (cd "$directory" && pwd -P)
}

existing_directory() {
  local directory="$1"

  if [ ! -d "$directory" ]; then
    fail "Directory not found: $directory"
  fi

  (cd "$directory" && pwd -P)
}

default_artifact_root() {
  if [ -n "${UI_AUTOMATION_VIDEO_DIR:-}" ]; then
    printf "%s" "$UI_AUTOMATION_VIDEO_DIR"
  elif [ -n "${DERIVED_DATA_PATH:-}" ]; then
    printf "%s/UIAutomationVideos" "$DERIVED_DATA_PATH"
  else
    printf "DerivedData.noindex/UIAutomationVideos"
  fi
}

resolve_simulator_udid() {
  if [ -n "$SIMULATOR_UDID" ]; then
    printf "%s" "$SIMULATOR_UDID"
    return
  fi

  if [ -n "${SIM_UDID:-}" ]; then
    printf "%s" "$SIM_UDID"
    return
  fi

  fail "No simulator provided. Set SIM_UDID or pass --sim-udid."
}

default_app_bundle_id() {
  if [ -n "${BUNDLE_ID:-}" ]; then
    printf "%s" "$BUNDLE_ID"
    return
  fi

  fail "Cannot infer an app bundle ID. Set BUNDLE_ID or pass --start-on-app <bundle-id>."
}

state_key_for_simulator() {
  printf "%s" "$1" | tr -c "A-Za-z0-9._-" "_"
}

active_state_file() {
  local artifact_root="$1"
  local simulator_udid="$2"
  local state_key

  state_key="$(state_key_for_simulator "$simulator_udid")"
  printf "%s/.active-%s.state" "$artifact_root" "$state_key"
}

file_size() {
  if [ -f "$1" ]; then
    wc -c < "$1" | tr -d " "
  else
    printf "0"
  fi
}

reduction_percent() {
  local original_bytes="$1"
  local compressed_bytes="$2"

  if [ "$original_bytes" -eq 0 ] || [ "$compressed_bytes" -eq 0 ]; then
    printf "not-available"
    return
  fi

  awk -v original="$original_bytes" -v compressed="$compressed_bytes" \
    'BEGIN { printf "%.2f%%", (1 - compressed / original) * 100 }'
}

write_state_file() {
  local state_file="$1"

  {
    printf "RUN_DIR=%s\n" "$RUN_DIR"
    printf "ARTIFACT_ROOT=%s\n" "$ARTIFACT_ROOT"
    printf "SIMULATOR_UDID=%s\n" "$SIMULATOR_UDID"
    printf "STARTED_AT=%s\n" "$STARTED_AT"
    printf "STARTED_EPOCH=%s\n" "$STARTED_EPOCH"
    printf "RECORDER_PID=%s\n" "$RECORDER_PID"
    printf "RAW_VIDEO=%s\n" "$RAW_VIDEO"
    printf "COMPRESSED_VIDEO=%s\n" "$COMPRESSED_VIDEO"
    printf "METADATA_FILE=%s\n" "$METADATA_FILE"
    printf "RECORDER_LOG=%s\n" "$RECORDER_LOG"
    printf "COMMAND_LOG=%s\n" "$COMMAND_LOG"
    printf "COMPRESS=%s\n" "$COMPRESS"
    printf "KEEP_RAW=%s\n" "$KEEP_RAW"
  } > "$state_file"
}

write_active_state_file() {
  local state_file="$1"
  local active_state_file="$2"

  printf "RUN_STATE=%s\n" "$state_file" > "$active_state_file"
}

write_start_metadata() {
  {
    printf "Name: %s\n" "$NAME"
    printf "Started at: %s\n" "$STARTED_AT"
    printf "Simulator UDID: %s\n" "$SIMULATOR_UDID"
    printf "Run directory: %s\n" "$RUN_DIR"
    printf "Raw video: %s\n" "$RAW_VIDEO"
    printf "Compressed video: %s\n" "$COMPRESSED_VIDEO"
    printf "Recorder log: %s\n" "$RECORDER_LOG"
    printf "Start trigger: %s\n" "${START_TRIGGER:-immediate}"
    if [ -n "${START_TRIGGER_NOTE:-}" ]; then
      printf "Start trigger note: %s\n" "$START_TRIGGER_NOTE"
    fi
    if [ "${START_TRIGGER:-immediate}" = "app" ]; then
      printf "Start app bundle ID: %s\n" "$START_APP_BUNDLE_ID"
      printf "Start timeout: %s\n" "$START_TIMEOUT"
      printf "Trigger log: %s\n" "$TRIGGER_LOG"
    fi
    if [ -n "${POST_START_DURATION:-}" ] && [ "$POST_START_DURATION" -gt 0 ]; then
      printf "Post-start duration: %s\n" "$POST_START_DURATION"
    fi
    if [ -n "${PREPARE_COMMAND_TEXT:-}" ]; then
      printf "Prepare command: %s\n" "$PREPARE_COMMAND_TEXT"
      printf "Prepare log: %s\n" "$PREPARE_LOG"
      printf "Prepare status: %s\n" "${PREPARE_STATUS:-not-run}"
    fi
    if [ -n "${COMMAND_TEXT:-}" ]; then
      printf "Command: %s\n" "$COMMAND_TEXT"
      printf "Command log: %s\n" "$COMMAND_LOG"
    fi
  } > "$METADATA_FILE"
}

write_unrecorded_metadata() {
  local ended_at="$1"
  local command_status="$2"
  local recording_status="$3"
  local reason="$4"

  {
    printf "Name: %s\n" "$NAME"
    printf "Ended at: %s\n" "$ended_at"
    printf "Simulator UDID: %s\n" "$SIMULATOR_UDID"
    printf "Run directory: %s\n" "$RUN_DIR"
    printf "Start trigger: %s\n" "${START_TRIGGER:-immediate}"
    if [ -n "${START_TRIGGER_NOTE:-}" ]; then
      printf "Start trigger note: %s\n" "$START_TRIGGER_NOTE"
    fi
    if [ "${START_TRIGGER:-immediate}" = "app" ]; then
      printf "Start app bundle ID: %s\n" "$START_APP_BUNDLE_ID"
      printf "Start timeout: %s\n" "$START_TIMEOUT"
      printf "Trigger log: %s\n" "$TRIGGER_LOG"
    fi
    if [ -n "${PREPARE_COMMAND_TEXT:-}" ]; then
      printf "Prepare command: %s\n" "$PREPARE_COMMAND_TEXT"
      printf "Prepare log: %s\n" "$PREPARE_LOG"
      printf "Prepare status: %s\n" "${PREPARE_STATUS:-not-run}"
    fi
    if [ -n "${COMMAND_TEXT:-}" ]; then
      printf "Command: %s\n" "$COMMAND_TEXT"
      printf "Command log: %s\n" "$COMMAND_LOG"
    fi
    printf "Command status: %s\n" "$command_status"
    printf "Recording status: %s\n" "$recording_status"
    printf "Compression status: not-run\n"
    printf "Primary video: not-recorded\n"
    printf "Failure reason: %s\n" "$reason"
  } > "$METADATA_FILE"
}

append_stop_metadata() {
  local ended_at="$1"
  local expected_duration="$2"
  local command_status="$3"
  local recording_status="$4"
  local compression_status="$5"
  local primary_video="$6"
  local raw_video_bytes="$7"
  local compressed_video_bytes="$8"
  local compression_reduction="$9"

  {
    printf "Ended at: %s\n" "$ended_at"
    if [ -n "$expected_duration" ]; then
      printf "Expected recording duration: %s\n" "$expected_duration"
    fi
    printf "Command status: %s\n" "$command_status"
    printf "Recording status: %s\n" "$recording_status"
    printf "Compression status: %s\n" "$compression_status"
    printf "Raw video bytes: %s\n" "$raw_video_bytes"
    printf "Compressed video bytes: %s\n" "$compressed_video_bytes"
    printf "Compression reduction: %s\n" "$compression_reduction"
    printf "Primary video: %s\n" "$primary_video"
    printf "Primary video bytes: %s\n" "$(file_size "$primary_video")"
  } >> "$METADATA_FILE"
}

check_disk_space() {
  local available_kb

  available_kb="$(df -Pk "$ARTIFACT_ROOT" | awk 'NR == 2 { print $4 }')"
  if [ -n "$available_kb" ] && [ "$available_kb" -lt 1048576 ]; then
    echo "Warning: Less than 1 GiB is available for video artifacts in $ARTIFACT_ROOT." >&2
  fi
}

ensure_simulator_booted() {
  xcrun simctl boot "$SIMULATOR_UDID" >/dev/null 2>&1 || true
  xcrun simctl bootstatus "$SIMULATOR_UDID" -b >/dev/null
}

prepare_run_paths() {
  local timestamp

  NAME="${NAME:-ui-automation-run}"
  SLUG="$(sanitize_slug "$NAME")"
  ARTIFACT_ROOT="$(absolute_directory "${ARTIFACT_ROOT:-$(default_artifact_root)}")"
  check_disk_space

  if [ -n "$RUN_DIR" ]; then
    RUN_DIR="$(absolute_directory "$RUN_DIR")"
  else
    timestamp="$(date -u +"%Y%m%dT%H%M%SZ")"
    RUN_DIR="$(absolute_directory "$ARTIFACT_ROOT/${timestamp}-${SLUG}")"
  fi

  RAW_VIDEO="$RUN_DIR/${SLUG}.raw.mp4"
  COMPRESSED_VIDEO="$RUN_DIR/${SLUG}.mp4"
  METADATA_FILE="$RUN_DIR/metadata.txt"
  RECORDER_LOG="$RUN_DIR/recordVideo.log"
  COMMAND_LOG="$RUN_DIR/command.log"
  PREPARE_LOG="$RUN_DIR/prepare.log"
  TRIGGER_LOG="$RUN_DIR/trigger.log"
}

load_key_value_file() {
  local state_file="$1"
  local line=""
  local key=""
  local value=""

  if [ ! -f "$state_file" ]; then
    fail "Recording state not found: $state_file"
  fi

  while IFS= read -r line || [ -n "$line" ]; do
    key="${line%%=*}"
    value="${line#*=}"

    if [ "$line" = "$key" ] || [ -z "$key" ]; then
      fail "Malformed recording state line in $state_file: $line"
    fi

    case "$key" in
      ARTIFACT_ROOT)
        ARTIFACT_ROOT="$value"
        ;;
      COMMAND_LOG)
        COMMAND_LOG="$value"
        ;;
      COMPRESS)
        COMPRESS="$value"
        ;;
      COMPRESSED_VIDEO)
        COMPRESSED_VIDEO="$value"
        ;;
      KEEP_RAW)
        KEEP_RAW="$value"
        ;;
      METADATA_FILE)
        METADATA_FILE="$value"
        ;;
      RAW_VIDEO)
        RAW_VIDEO="$value"
        ;;
      RECORDER_LOG)
        RECORDER_LOG="$value"
        ;;
      RECORDER_PID)
        RECORDER_PID="$value"
        ;;
      RUN_DIR)
        RUN_DIR="$value"
        ;;
      RUN_STATE)
        RUN_STATE="$value"
        ;;
      SIMULATOR_UDID)
        SIMULATOR_UDID="$value"
        ;;
      STARTED_AT)
        STARTED_AT="$value"
        ;;
      STARTED_EPOCH)
        STARTED_EPOCH="$value"
        ;;
      *)
        fail "Unknown recording state key in $state_file: $key"
        ;;
    esac
  done < "$state_file"
}

load_recording_state_file() {
  local state_file="$1"

  ARTIFACT_ROOT=""
  COMMAND_LOG=""
  COMPRESS=""
  COMPRESSED_VIDEO=""
  KEEP_RAW=""
  METADATA_FILE=""
  RAW_VIDEO=""
  RECORDER_LOG=""
  RECORDER_PID=""
  RUN_DIR=""
  SIMULATOR_UDID=""
  STARTED_AT=""
  STARTED_EPOCH=""

  load_key_value_file "$state_file"

  case "$RECORDER_PID" in
    ""|*[!0-9]*)
      fail "Invalid RECORDER_PID in $state_file"
      ;;
  esac

  case "$COMPRESS" in
    0|1) ;;
    *)
      fail "Invalid COMPRESS in $state_file"
      ;;
  esac

  case "$KEEP_RAW" in
    0|1) ;;
    *)
      fail "Invalid KEEP_RAW in $state_file"
      ;;
  esac

  if [ -n "$STARTED_EPOCH" ] && ! is_nonnegative_integer "$STARTED_EPOCH"; then
    fail "Invalid STARTED_EPOCH in $state_file"
  fi
}

active_recording_state_file() {
  local active_state_file="$1"

  RUN_STATE=""
  load_key_value_file "$active_state_file"

  if [ -z "$RUN_STATE" ]; then
    fail "Active recording state is missing RUN_STATE: $active_state_file"
  fi

  printf "%s" "$RUN_STATE"
}

compress_video() {
  local input="$1"
  local output="$2"
  local expected_duration="${3:-}"
  local compress_log="$RUN_DIR/ffmpeg.log"
  local temp_output="${output}.tmp.mp4"
  local encoder=""
  local encoder_label=""
  local encode_fps="${UI_AUTOMATION_VIDEO_FPS:-30}"
  local hevc_crf="${UI_AUTOMATION_VIDEO_CRF:-28}"
  local hevc_preset="${UI_AUTOMATION_VIDEO_PRESET:-medium}"

  if ! command -v ffmpeg >/dev/null; then
    echo "Warning: ffmpeg not found. Raw video kept at $input." >&2
    COMPRESSION_STATUS="missing-ffmpeg"
    return 2
  fi

  if ! command -v ffprobe >/dev/null; then
    echo "Warning: ffprobe not found. Raw video kept at $input." >&2
    COMPRESSION_STATUS="failed-missing-ffprobe"
    return 1
  fi

  echo "Compressing recording with ffmpeg..."
  COMPRESSION_STATUS=""

  if ! is_positive_integer "$encode_fps"; then
    echo "Warning: UI_AUTOMATION_VIDEO_FPS must be a positive integer. Raw video kept at $input." >&2
    COMPRESSION_STATUS="failed-invalid-fps"
    return 1
  fi

  if ! is_number "$hevc_crf"; then
    echo "Warning: UI_AUTOMATION_VIDEO_CRF must be numeric. Raw video kept at $input." >&2
    COMPRESSION_STATUS="failed-invalid-crf"
    return 1
  fi

  if ffmpeg_has_encoder "libx265"; then
    encoder="libx265"
    encoder_label="hevc-libx265"
  elif ffmpeg_has_encoder "hevc_videotoolbox"; then
    encoder="hevc_videotoolbox"
    encoder_label="hevc-videotoolbox"
  else
    echo "Warning: ffmpeg has no supported HEVC encoder. Raw video kept at $input." >&2
    COMPRESSION_STATUS="failed-no-supported-encoder"
    return 1
  fi

  write_compression_log_header "$compress_log" "$input" "$output" "$encoder_label" "$encode_fps" "$expected_duration"

  rm -f "$temp_output" "$output"
  if encode_video "$input" "$temp_output" "$encoder" "$encode_fps" "$hevc_crf" "$hevc_preset" "$compress_log" "$expected_duration" &&
    compression_sanity_check "$input" "$temp_output" "$compress_log" "$encode_fps" "$expected_duration"; then
    mv -f "$temp_output" "$output"
    COMPRESSION_STATUS="$encoder_label"
    return 0
  fi

  echo "Warning: ffmpeg compression failed or produced an invalid video. See $compress_log. Raw video kept at $input." >&2
  rm -f "$temp_output" "$output"
  COMPRESSION_STATUS="${COMPRESSION_STATUS:-failed}"
  return 1
}

ffmpeg_has_encoder() {
  local encoder="$1"

  ffmpeg -hide_banner -encoders 2>/dev/null | awk -v encoder="$encoder" '$0 ~ encoder { found = 1 } END { exit !found }'
}

write_compression_log_header() {
  local compress_log="$1"
  local input="$2"
  local output="$3"
  local encoder_label="$4"
  local encode_fps="$5"
  local expected_duration="$6"

  {
    printf "Compression pipeline: internal ffmpeg\n"
    printf "Input: %s\n" "$input"
    printf "Output: %s\n" "$output"
    printf "Encoder: %s\n" "$encoder_label"
    printf "Normalized fps: %s\n" "$encode_fps"
    if is_number "$expected_duration"; then
      printf "Expected recording duration: %s\n" "$expected_duration"
    fi
    printf "Video filter: fps=%s, even-dimension scale, encoder-specific pixel format\n" "$encode_fps"
    printf "\nRaw probe:\n"
    ffprobe -v error \
      -select_streams v:0 \
      -show_entries stream=codec_name,width,height,avg_frame_rate,r_frame_rate,nb_frames,duration \
      -show_entries format=duration,size \
      -of default=noprint_wrappers=1 \
      "$input" 2>&1 || true
    printf "\nffmpeg output:\n"
  } > "$compress_log"
}

encode_video() {
  local input="$1"
  local output="$2"
  local encoder="$3"
  local encode_fps="$4"
  local hevc_crf="$5"
  local hevc_preset="$6"
  local compress_log="$7"
  local expected_duration="$8"
  local video_filter=""

  video_filter="$(compression_video_filter "$input" "$encode_fps" "$expected_duration" "yuv420p")"

  case "$encoder" in
    libx265)
      ffmpeg -hide_banner -y -nostdin \
        -fflags +genpts \
        -i "$input" \
        -vf "$video_filter" \
        -fps_mode cfr \
        -c:v libx265 -preset "$hevc_preset" -crf "$hevc_crf" -tag:v hvc1 \
        -c:a aac -b:a 128k \
        -movflags +faststart \
        "$output" >> "$compress_log" 2>&1
      ;;
    hevc_videotoolbox)
      ffmpeg -hide_banner -y -nostdin \
        -fflags +genpts \
        -i "$input" \
        -vf "$(compression_video_filter "$input" "$encode_fps" "$expected_duration" "nv12")" \
        -fps_mode cfr \
        -c:v hevc_videotoolbox -q:v 55 -tag:v hvc1 \
        -c:a aac -b:a 128k \
        -movflags +faststart \
        "$output" >> "$compress_log" 2>&1
      ;;
    *)
      return 1
      ;;
  esac
}

compression_video_filter() {
  local input="$1"
  local encode_fps="$2"
  local expected_duration="$3"
  local pixel_format="$4"
  local raw_duration=""
  local padding_duration=""
  local filter="fps=${encode_fps},scale=trunc(iw/2)*2:trunc(ih/2)*2,format=${pixel_format}"

  raw_duration="$(video_duration "$input")"

  if is_number "$expected_duration" && is_number "$raw_duration"; then
    padding_duration="$(awk -v expected="$expected_duration" -v raw="$raw_duration" \
      'BEGIN {
        padding = expected - raw
        if (padding > 0.25) printf "%.3f", padding
      }')"

    if [ -n "$padding_duration" ]; then
      filter="${filter},tpad=stop_mode=clone:stop_duration=${padding_duration}"
    fi
  fi

  printf "%s" "$filter"
}

is_number() {
  awk -v value="$1" 'BEGIN { exit !(value ~ /^[0-9]+([.][0-9]+)?$/) }'
}

number_max() {
  awk -v first="$1" -v second="$2" 'BEGIN { if (first > second) print first; else print second }'
}

absolute_difference() {
  awk -v first="$1" -v second="$2" 'BEGIN { diff = first - second; if (diff < 0) diff = -diff; print diff }'
}

video_duration() {
  local duration=""

  if ! duration="$(
    ffprobe -v error \
      -show_entries format=duration \
      -of default=noprint_wrappers=1:nokey=1 \
      "$1" 2>/dev/null |
      head -1
  )"; then
    duration=""
  fi

  printf "%s" "$duration"
}

video_frame_count() {
  local frame_count=""

  if ! frame_count="$(
    ffprobe -v error \
      -select_streams v:0 \
      -count_frames \
      -show_entries stream=nb_read_frames \
      -of default=noprint_wrappers=1:nokey=1 \
      "$1" 2>/dev/null |
      head -1
  )"; then
    frame_count=""
  fi

  printf "%s" "$frame_count"
}

video_decode_check() {
  local video="$1"
  local compress_log="$2"

  {
    printf "\nDecode check:\n"
    ffmpeg -hide_banner -v error -nostdin -i "$video" -f null -
  } >> "$compress_log" 2>&1
}

compression_sanity_check() {
  local raw_video="$1"
  local compressed_video="$2"
  local compress_log="$3"
  local target_fps="$4"
  local expected_duration="$5"
  local raw_duration=""
  local reference_duration=""
  local reference_source="raw"
  local compressed_duration=""
  local compressed_frames=""
  local duration_difference=""
  local duration_tolerance=""
  local minimum_frames=""
  local effective_fps=""

  if ! command -v ffprobe >/dev/null; then
    echo "Compression sanity check failed: ffprobe not found." >> "$compress_log"
    COMPRESSION_STATUS="failed-missing-ffprobe"
    return 1
  fi

  if [ ! -s "$compressed_video" ]; then
    echo "Compression sanity check failed: compressed video is missing or empty." >> "$compress_log"
    COMPRESSION_STATUS="failed-sanity-check"
    return 1
  fi

  raw_duration="$(video_duration "$raw_video")"
  compressed_duration="$(video_duration "$compressed_video")"
  compressed_frames="$(video_frame_count "$compressed_video")"
  reference_duration="$raw_duration"

  if is_number "$expected_duration"; then
    reference_duration="$expected_duration"
    reference_source="wall-clock"
  fi

  {
    printf "\nCompression sanity check:\n"
    printf "Raw duration: %s\n" "${raw_duration:-unknown}"
    printf "Reference duration: %s (%s)\n" "${reference_duration:-unknown}" "$reference_source"
    printf "Compressed duration: %s\n" "${compressed_duration:-unknown}"
    printf "Compressed frames: %s\n" "${compressed_frames:-unknown}"
  } >> "$compress_log"

  if ! is_number "$compressed_duration" ||
    awk -v duration="$compressed_duration" 'BEGIN { exit !(duration <= 0) }'; then
    echo "Compression sanity check failed: compressed duration is invalid." >> "$compress_log"
    COMPRESSION_STATUS="failed-sanity-check"
    return 1
  fi

  if is_number "$reference_duration"; then
    duration_difference="$(absolute_difference "$reference_duration" "$compressed_duration")"
    duration_tolerance="$(number_max 1 "$(awk -v reference="$reference_duration" 'BEGIN { print reference * 0.10 }')")"

    {
      printf "Duration difference: %s\n" "$duration_difference"
      printf "Duration tolerance: %s\n" "$duration_tolerance"
    } >> "$compress_log"

    if awk -v difference="$duration_difference" -v tolerance="$duration_tolerance" \
      'BEGIN { exit !(difference > tolerance) }'; then
      echo "Compression sanity check failed: compressed duration does not match raw duration." >> "$compress_log"
      COMPRESSION_STATUS="failed-sanity-check"
      return 1
    fi
  fi

  if ! is_number "$compressed_frames"; then
    echo "Compression sanity check failed: compressed frame count is unavailable." >> "$compress_log"
    COMPRESSION_STATUS="failed-sanity-check"
    return 1
  fi

  minimum_frames="$(awk -v duration="$compressed_duration" -v fps="$target_fps" \
    'BEGIN {
      frames = duration * fps * 0.75
      if (duration < 2 && frames < 1) frames = 1
      printf "%.0f", frames
    }')"
  effective_fps="$(awk -v frames="$compressed_frames" -v duration="$compressed_duration" \
    'BEGIN { if (duration > 0) printf "%.2f", frames / duration; else print "0" }')"

  {
    printf "Minimum expected frames: %s\n" "$minimum_frames"
    printf "Effective fps: %s\n" "$effective_fps"
  } >> "$compress_log"

  if awk -v frames="$compressed_frames" -v minimum="$minimum_frames" \
    'BEGIN { exit !(frames < minimum) }'; then
    echo "Compression sanity check failed: compressed video has too few frames for its duration." >> "$compress_log"
    COMPRESSION_STATUS="failed-sanity-check"
    return 1
  fi

  if ! video_decode_check "$compressed_video" "$compress_log"; then
    echo "Compression sanity check failed: compressed video does not decode cleanly." >> "$compress_log"
    COMPRESSION_STATUS="failed-sanity-check"
    return 1
  fi

  echo "Compression sanity check passed." >> "$compress_log"
  return 0
}

prepare_active_recording_state() {
  local active_state="$1"

  if [ -f "$active_state" ]; then
    local existing_state_file=""
    local existing_pid=""
    local existing_run_dir=""

    existing_state_file="$(active_recording_state_file "$active_state")"

    if [ -f "$existing_state_file" ]; then
      existing_pid="$(sed -nE 's/^RECORDER_PID=([0-9]+)$/\1/p' "$existing_state_file" | head -1)"
      existing_run_dir="$(sed -nE 's/^RUN_DIR=(.*)$/\1/p' "$existing_state_file" | head -1)"
    fi

    if [ -n "$existing_pid" ] && kill -0 "$existing_pid" 2>/dev/null; then
      fail "Recording already active for simulator $SIMULATOR_UDID. Stop it first. State: $active_state"
    fi

    echo "Warning: Removing stale active recording state for $existing_run_dir." >&2
    rm -f "$active_state"
  fi
}

start_recording() {
  local active_state="$1"
  local run_state="$RUN_DIR/recording.state"

  prepare_active_recording_state "$active_state"

  ensure_simulator_booted

  if [ -e "$RAW_VIDEO" ] || [ -e "$COMPRESSED_VIDEO" ]; then
    fail "Run directory already contains video output. Choose a new --run-dir or remove the existing files."
  fi

  STARTED_AT="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
  STARTED_EPOCH="$(date +%s)"
  RECORDING_STARTED_EPOCH="$STARTED_EPOCH"
  xcrun simctl io "$SIMULATOR_UDID" recordVideo --codec=h264 "$RAW_VIDEO" > "$RECORDER_LOG" 2>&1 &
  RECORDER_PID=$!

  sleep 1

  if ! kill -0 "$RECORDER_PID" 2>/dev/null; then
    echo "recordVideo failed to start. Log:" >&2
    sed -n '1,120p' "$RECORDER_LOG" >&2 || true
    exit 1
  fi

  write_state_file "$run_state"
  write_active_state_file "$run_state" "$active_state"
  write_start_metadata

  echo "Recording started."
  echo "  Run directory: $RUN_DIR"
  echo "  Raw video: $RAW_VIDEO"
  echo "  Stop command: $(printf "%q" "$0") stop --run-dir $(printf "%q" "$RUN_DIR")"
}

wait_for_recording_session() {
  echo "Recording remains active while this process is running."
  wait "$RECORDER_PID" || true
}

is_nonnegative_integer() {
  case "$1" in
    ""|*[!0-9]*)
      return 1
      ;;
    *)
      return 0
      ;;
  esac
}

is_positive_integer() {
  is_nonnegative_integer "$1" && [ "$1" -gt 0 ]
}

app_process_pids() {
  local bundle_id="$1"
  local appinfo=""
  local executable=""
  local path=""

  appinfo="$(xcrun simctl appinfo "$SIMULATOR_UDID" "$bundle_id" 2>/dev/null || true)"
  path="$(
    printf "%s\n" "$appinfo" |
      sed -nE 's/^[[:space:]]*Path = "?([^";]+)"?;$/\1/p' |
      head -1
  )"
  executable="$(
    printf "%s\n" "$appinfo" |
      sed -nE 's/^[[:space:]]*CFBundleExecutable = "?([^";]+)"?;$/\1/p' |
      head -1
  )"

  if [ -z "$path" ] || [ -z "$executable" ]; then
    return 0
  fi

  ps -axo pid=,command= |
    awk -v app_dir="$path" -v app_executable="$executable" -v device_path="/Devices/$SIMULATOR_UDID/" '
      BEGIN {
        executable_path = app_dir "/" app_executable
      }

      index($0, executable_path) && (index(executable_path, device_path) || index($0, device_path)) {
        print $1
      }
    '
}

pid_list_contains() {
  local list="$1"
  local candidate="$2"
  local pid=""

  for pid in $list; do
    if [ "$pid" = "$candidate" ]; then
      return 0
    fi
  done

  return 1
}

new_app_process_pid() {
  local baseline_pids="$1"
  local current_pids="$2"
  local pid=""

  for pid in $current_pids; do
    if ! pid_list_contains "$baseline_pids" "$pid"; then
      printf "%s" "$pid"
      return 0
    fi
  done

  return 1
}

wait_for_app_start_trigger() {
  local command_pid="$1"
  local bundle_id="$2"
  local attempts=$((START_TIMEOUT * 5))
  local baseline_pids="$3"
  local command_exit_attempts=0
  local current_pids=""
  local detected_pid=""
  local attempt=0

  {
    printf "Waiting for app launch trigger.\n"
    printf "Bundle ID: %s\n" "$bundle_id"
    printf "Simulator UDID: %s\n" "$SIMULATOR_UDID"
    printf "Timeout: %s seconds\n" "$START_TIMEOUT"
    printf "Baseline PIDs: %s\n" "${baseline_pids:-none}"
  } > "$TRIGGER_LOG"

  while [ "$attempt" -le "$attempts" ]; do
    current_pids="$(app_process_pids "$bundle_id")"

    if detected_pid="$(new_app_process_pid "$baseline_pids" "$current_pids")"; then
      printf "Detected app PID: %s\n" "$detected_pid" >> "$TRIGGER_LOG"
      return 0
    fi

    if ! kill -0 "$command_pid" 2>/dev/null; then
      command_exit_attempts=$((command_exit_attempts + 1))
      if [ "$command_exit_attempts" -ge 25 ]; then
        {
          printf "Command exited before a new app process was detected.\n"
          printf "Last observed PIDs: %s\n" "${current_pids:-none}"
        } >> "$TRIGGER_LOG"
        return 1
      fi
    fi

    sleep 0.2
    attempt=$((attempt + 1))
  done

  {
    printf "Timed out waiting for app launch trigger.\n"
    printf "Last observed PIDs: %s\n" "${current_pids:-none}"
  } >> "$TRIGGER_LOG"

  return 1
}

run_prepare_command() {
  PREPARE_STATUS="not-run"

  if [ -z "${PREPARE_COMMAND_TEXT:-}" ]; then
    return 0
  fi

  command -v zsh >/dev/null || missing_dependency "zsh"

  echo "Running prepare command before recording..."

  set +e
  zsh -lc "$PREPARE_COMMAND_TEXT" > >(tee "$PREPARE_LOG") 2>&1
  PREPARE_STATUS=$?
  set -e

  if [ "$PREPARE_STATUS" -ne 0 ]; then
    write_unrecorded_metadata \
      "$(date -u +"%Y-%m-%dT%H:%M:%SZ")" \
      "not-run" \
      1 \
      "prepare command failed"
    return "$PREPARE_STATUS"
  fi

  return 0
}

wait_for_command_status() {
  local command_pid="$1"
  WAITED_COMMAND_STATUS=0

  set +e
  wait "$command_pid"
  WAITED_COMMAND_STATUS=$?
  set -e
}

wait_for_post_start_duration() {
  local elapsed=0
  local remaining=0

  if [ "${POST_START_DURATION:-0}" -eq 0 ]; then
    return
  fi

  if [ -z "${RECORDING_STARTED_EPOCH:-}" ]; then
    return
  fi

  elapsed=$(($(date +%s) - RECORDING_STARTED_EPOCH))
  remaining=$((POST_START_DURATION - elapsed))

  if [ "$remaining" -gt 0 ]; then
    echo "Recording for ${remaining}s more to satisfy --post-start-duration..."
    sleep "$remaining"
  fi
}

command_looks_like_xctest() {
  local command_text="$*"

  case "$command_text" in
    *"UITests/"*|*"-only-testing:"*|*"ONLY_TESTING="*|*"xcodebuild"*' test'*)
      return 0
      ;;
    *)
      return 1
      ;;
  esac
}

normalize_start_trigger_for_command() {
  if [ "$START_TRIGGER" != "app" ]; then
    return
  fi

  if [ "${UI_AUTOMATION_VIDEO_ALLOW_XCTEST_START_ON_APP:-0}" = "1" ]; then
    return
  fi

  if ! command_looks_like_xctest "${COMMAND[@]}"; then
    return
  fi

  START_TRIGGER="immediate"
  START_TRIGGER_NOTE="requested --start-on-app ignored because starting recording after XCTest launches the app can make captured frames stale during the test"
  echo "Warning: $START_TRIGGER_NOTE. Set UI_AUTOMATION_VIDEO_ALLOW_XCTEST_START_ON_APP=1 to keep late-start behavior." >&2
}

stop_recording_from_state() {
  local state_file="$1"
  local command_status="${2:-not-run}"
  local active_state=""
  local recording_status=0
  local compression_status="not-run"
  local primary_video=""
  local ended_at=""
  local raw_video_bytes=0
  local compressed_video_bytes="not-run"
  local compression_reduction="not-run"
  local ended_epoch=0
  local expected_duration=""
  COMPRESSION_STATUS=""

  load_recording_state_file "$state_file"

  if [ -n "${ARTIFACT_ROOT:-}" ] && [ -n "${SIMULATOR_UDID:-}" ]; then
    active_state="$(active_state_file "$ARTIFACT_ROOT" "$SIMULATOR_UDID")"
  fi

  if [ -n "${RECORDER_PID:-}" ] && kill -0 "$RECORDER_PID" 2>/dev/null; then
    kill -INT "$RECORDER_PID" 2>/dev/null || true

    local attempts=0
    while kill -0 "$RECORDER_PID" 2>/dev/null && [ "$attempts" -lt 30 ]; do
      sleep 1
      attempts=$((attempts + 1))
    done

    if kill -0 "$RECORDER_PID" 2>/dev/null; then
      echo "Warning: recordVideo did not stop after SIGINT. Sending SIGTERM." >&2
      kill -TERM "$RECORDER_PID" 2>/dev/null || true
      recording_status=1
    fi
  else
    echo "Warning: recordVideo process is not running. Continuing with existing artifact." >&2
  fi

  ended_at="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
  ended_epoch="$(date +%s)"
  if [ -n "${STARTED_EPOCH:-}" ] && is_nonnegative_integer "$STARTED_EPOCH" && [ "$ended_epoch" -ge "$STARTED_EPOCH" ]; then
    expected_duration="$((ended_epoch - STARTED_EPOCH))"
  fi
  raw_video_bytes="$(file_size "$RAW_VIDEO")"

  if [ ! -s "$RAW_VIDEO" ]; then
    echo "Error: Raw recording is missing or empty: $RAW_VIDEO" >&2
    recording_status=1
    primary_video="$RAW_VIDEO"
  elif [ "$COMPRESS" -eq 0 ]; then
    echo "Skipping compression. Raw video: $RAW_VIDEO"
    compression_status="skipped"
    primary_video="$RAW_VIDEO"
  elif compress_video "$RAW_VIDEO" "$COMPRESSED_VIDEO" "$expected_duration"; then
    compression_status="$COMPRESSION_STATUS"
    compressed_video_bytes="$(file_size "$COMPRESSED_VIDEO")"
    compression_reduction="$(reduction_percent "$raw_video_bytes" "$compressed_video_bytes")"
    primary_video="$COMPRESSED_VIDEO"

    if [ "$COMPRESS" -eq 1 ] && [ "$KEEP_RAW" -eq 0 ]; then
      rm -f "$RAW_VIDEO"
    fi
  else
    compression_status="${COMPRESSION_STATUS:-failed}"
    primary_video="$RAW_VIDEO"
  fi

  append_stop_metadata \
    "$ended_at" \
    "$expected_duration" \
    "$command_status" \
    "$recording_status" \
    "$compression_status" \
    "$primary_video" \
    "$raw_video_bytes" \
    "$compressed_video_bytes" \
    "$compression_reduction"

  rm -f "$state_file"
  if [ -n "$active_state" ] && [ -f "$active_state" ]; then
    rm -f "$active_state"
  fi

  echo "Recording stopped."
  echo "  Run directory: $RUN_DIR"
  echo "  Primary video: $primary_video"
  echo "  Metadata: $METADATA_FILE"

  if [ "$recording_status" -ne 0 ]; then
    return "$recording_status"
  fi

  return 0
}

SUBCOMMAND="run"
if [ "${1:-}" = "run" ] || [ "${1:-}" = "start" ] || [ "${1:-}" = "stop" ]; then
  SUBCOMMAND="$1"
  shift
elif [ "${1:-}" = "help" ]; then
  usage
  exit 0
fi

NAME=""
ARTIFACT_ROOT=""
RUN_DIR=""
SIMULATOR_UDID=""
DURATION=""
PREPARE_COMMAND_TEXT=""
PREPARE_STATUS="not-run"
START_TRIGGER="immediate"
START_APP_BUNDLE_ID=""
START_TRIGGER_NOTE=""
START_TIMEOUT=300
POST_START_DURATION=0
COMMAND_PID=""
WAITED_COMMAND_STATUS=0
COMPRESS=1
KEEP_RAW=0
COMMAND=()

while [ "$#" -gt 0 ]; do
  case "$1" in
    --name)
      [ "$#" -ge 2 ] || fail "--name requires a value"
      NAME="$2"
      shift 2
      ;;
    --output-dir)
      [ "$#" -ge 2 ] || fail "--output-dir requires a value"
      ARTIFACT_ROOT="$2"
      shift 2
      ;;
    --run-dir)
      [ "$#" -ge 2 ] || fail "--run-dir requires a value"
      RUN_DIR="$2"
      shift 2
      ;;
    --sim-udid)
      [ "$#" -ge 2 ] || fail "--sim-udid requires a value"
      SIMULATOR_UDID="$2"
      shift 2
      ;;
    --duration)
      [ "$#" -ge 2 ] || fail "--duration requires a value"
      DURATION="$2"
      shift 2
      ;;
    --prepare)
      [ "$#" -ge 2 ] || fail "--prepare requires a value"
      PREPARE_COMMAND_TEXT="$2"
      shift 2
      ;;
    --start-on-app)
      START_TRIGGER="app"
      if [ "$#" -ge 2 ] && [ "${2#--}" = "$2" ]; then
        START_APP_BUNDLE_ID="$2"
        shift 2
      else
        shift
      fi
      ;;
    --start-timeout)
      [ "$#" -ge 2 ] || fail "--start-timeout requires a value"
      START_TIMEOUT="$2"
      shift 2
      ;;
    --post-start-duration)
      [ "$#" -ge 2 ] || fail "--post-start-duration requires a value"
      POST_START_DURATION="$2"
      shift 2
      ;;
    --no-compress)
      COMPRESS=0
      shift
      ;;
    --keep-raw)
      KEEP_RAW=1
      shift
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    --)
      shift
      COMMAND=("$@")
      break
      ;;
    *)
      fail "Unknown argument: $1"
      ;;
  esac
done

command -v xcrun >/dev/null || missing_dependency "xcrun"

if [ -n "$DURATION" ] && ! is_positive_integer "$DURATION"; then
  fail "--duration must be a positive integer"
fi

if ! is_positive_integer "$START_TIMEOUT"; then
  fail "--start-timeout must be a positive integer"
fi

if ! is_nonnegative_integer "$POST_START_DURATION"; then
  fail "--post-start-duration must be a non-negative integer"
fi

case "$SUBCOMMAND" in
  run)
    if [ "${#COMMAND[@]}" -eq 0 ]; then
      if [ -z "$DURATION" ]; then
        usage >&2
        fail "run requires a command after -- or --duration"
      fi

      COMMAND=(sleep "$DURATION")
    elif [ -n "$DURATION" ]; then
      fail "--duration cannot be combined with a command"
    fi

    if [ "$START_TRIGGER" = "app" ] && [ -n "$DURATION" ]; then
      fail "--start-on-app requires a command after --"
    fi

    SIMULATOR_UDID="$(resolve_simulator_udid)"
    if [ "$START_TRIGGER" = "app" ] && [ -z "$START_APP_BUNDLE_ID" ]; then
      START_APP_BUNDLE_ID="$(default_app_bundle_id)"
    fi

    prepare_run_paths
    COMMAND_TEXT="$(quote_args "${COMMAND[@]}")"
    normalize_start_trigger_for_command

    ACTIVE_STATE="$(active_state_file "$ARTIFACT_ROOT" "$SIMULATOR_UDID")"
    RUN_STATE="$RUN_DIR/recording.state"

    cleanup_after_signal() {
      echo "Signal received. Stopping recording..." >&2
      if [ -n "${COMMAND_PID:-}" ] && kill -0 "$COMMAND_PID" 2>/dev/null; then
        kill "$COMMAND_PID" 2>/dev/null || true
      fi
      if [ -f "$RUN_STATE" ]; then
        stop_recording_from_state "$RUN_STATE" "interrupted" >/dev/null 2>&1 || true
      fi
      exit 130
    }

    trap cleanup_after_signal INT TERM

    if [ "$START_TRIGGER" = "app" ]; then
      prepare_active_recording_state "$ACTIVE_STATE"
      ensure_simulator_booted
    fi

    run_prepare_command || exit "$PREPARE_STATUS"

    if [ "$START_TRIGGER" = "app" ]; then
      echo "Running command. Recording will start when $START_APP_BUNDLE_ID launches..."

      # Observe existing processes before launch; sampling afterward can mistake
      # a fast new process for the baseline and miss the launch entirely.
      BASELINE_APP_PIDS="$(app_process_pids "$START_APP_BUNDLE_ID")"
      set +e
      "${COMMAND[@]}" > >(tee "$COMMAND_LOG") 2>&1 &
      COMMAND_PID=$!
      set -e

      if wait_for_app_start_trigger "$COMMAND_PID" "$START_APP_BUNDLE_ID" "$BASELINE_APP_PIDS"; then
        start_recording "$ACTIVE_STATE"
        wait_for_command_status "$COMMAND_PID"
        COMMAND_STATUS="$WAITED_COMMAND_STATUS"
        wait_for_post_start_duration
      else
        if kill -0 "$COMMAND_PID" 2>/dev/null; then
          kill "$COMMAND_PID" 2>/dev/null || true
        fi

        wait_for_command_status "$COMMAND_PID"
        COMMAND_STATUS="$WAITED_COMMAND_STATUS"

        write_unrecorded_metadata \
          "$(date -u +"%Y-%m-%dT%H:%M:%SZ")" \
          "$COMMAND_STATUS" \
          1 \
          "app launch trigger did not fire"

        trap - INT TERM

        if [ "$COMMAND_STATUS" -ne 0 ]; then
          exit "$COMMAND_STATUS"
        fi

        exit 1
      fi
    else
      start_recording "$ACTIVE_STATE"

      set +e
      "${COMMAND[@]}" > >(tee "$COMMAND_LOG") 2>&1
      COMMAND_STATUS=$?
      set -e

      wait_for_post_start_duration
    fi

    trap - INT TERM

    if stop_recording_from_state "$RUN_STATE" "$COMMAND_STATUS"; then
      STOP_STATUS=0
    else
      STOP_STATUS=$?
    fi

    if [ "$COMMAND_STATUS" -ne 0 ]; then
      exit "$COMMAND_STATUS"
    fi

    exit "$STOP_STATUS"
    ;;
  start)
    if [ "${#COMMAND[@]}" -gt 0 ] || [ -n "$DURATION" ]; then
      fail "start does not accept a command or --duration"
    fi
    if [ -n "$PREPARE_COMMAND_TEXT" ] || [ "$START_TRIGGER" != "immediate" ] || [ "$POST_START_DURATION" -ne 0 ]; then
      fail "start does not accept --prepare, --start-on-app, or --post-start-duration"
    fi

    SIMULATOR_UDID="$(resolve_simulator_udid)"
    prepare_run_paths
    ACTIVE_STATE="$(active_state_file "$ARTIFACT_ROOT" "$SIMULATOR_UDID")"

    cleanup_after_signal() {
      echo "Signal received. Stopping recording..." >&2
      stop_recording_from_state "$RUN_DIR/recording.state" "interrupted" >/dev/null 2>&1 || true
      exit 130
    }

    trap cleanup_after_signal INT TERM

    start_recording "$ACTIVE_STATE"
    wait_for_recording_session
    ;;
  stop)
    if [ "${#COMMAND[@]}" -gt 0 ] || [ -n "$DURATION" ]; then
      fail "stop does not accept a command or --duration"
    fi
    if [ -n "$PREPARE_COMMAND_TEXT" ] || [ "$START_TRIGGER" != "immediate" ] || [ "$POST_START_DURATION" -ne 0 ]; then
      fail "stop does not accept --prepare, --start-on-app, or --post-start-duration"
    fi

    if [ -n "$RUN_DIR" ]; then
      RUN_DIR="$(existing_directory "$RUN_DIR")"
      STATE_FILE="$RUN_DIR/recording.state"
    else
      ARTIFACT_ROOT="$(absolute_directory "${ARTIFACT_ROOT:-$(default_artifact_root)}")"
      SIMULATOR_UDID="$(resolve_simulator_udid)"
      ACTIVE_STATE_FILE="$(active_state_file "$ARTIFACT_ROOT" "$SIMULATOR_UDID")"
      STATE_FILE="$(active_recording_state_file "$ACTIVE_STATE_FILE")"
    fi

    stop_recording_from_state "$STATE_FILE"
    ;;
esac

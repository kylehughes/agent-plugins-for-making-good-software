---
name: recording-ios-simulator-videos
description: "Record and compress iOS Simulator video for UI tests, bug reproductions, or PR demos. Use when a video artifact is needed; not screenshots or physical-device capture."
---

# Recording iOS Simulator Videos

Use this skill when an iOS task needs a simulator video artifact: UI automation runs, explicit XCTest/XCUITest filters, short manual reproductions, flaky visual states, or PR demo handoff.

The workflow is script-backed so agents do not have to coordinate `simctl recordVideo`, signal cleanup, artifact naming, and `ffmpeg` compression by hand. Resolve the script paths relative to this skill's `SKILL.md`, not the project working directory; the examples below abbreviate them as `scripts/…`.

## Artifact Contract

Recordings go under:

```sh
${UI_AUTOMATION_VIDEO_DIR:-${DERIVED_DATA_PATH:-DerivedData.noindex}/UIAutomationVideos}/<timestamp>-<name>/
```

`UI_AUTOMATION_VIDEO_DIR` is the explicit override; the derived-data fallbacks are last resorts relative to the working directory.

Each run contains:

- `metadata.txt`: simulator, command, status, timings, file sizes, compression savings, and primary video path.
- `recordVideo.log`: `simctl recordVideo` output.
- `prepare.log`: setup command output when `--prepare` is passed.
- `trigger.log`: delayed-start trigger details when `--start-on-app` is passed.
- `command.log`: wrapped command output when using `run`.
- `ffmpeg.log`: compression output when compression is attempted.
- `<name>.mp4`: compressed shareable video when `ffmpeg` succeeds.
- `<name>.raw.mp4`: raw simulator recording when compression is skipped, fails, or `--keep-raw` is passed.

`ffmpeg` and `ffprobe` are optional. Without both, the script keeps the raw recording and reports the missing dependency. When compression is available, the script owns the encoding path directly: it normalizes simulator recordings to a constant 30 fps, uses HEVC when an encoder is available, writes to a temporary file, and only replaces the compressed artifact after validation passes.

Compression is only accepted after `ffprobe` and decode sanity checks. The checks reject outputs with invalid duration, a large duration mismatch against the raw recording, too few frames for the normalized duration, or decode errors. The raw recording remains available until compression passes.

## Common Workflow

Prefer the wrapper for automation runs. For commands that build or install before launching the app and then leave the app open, use `--start-on-app` so recording begins when the target app process appears instead of capturing the simulator home screen during setup. `--post-start-duration` keeps a launched-app recording alive when the wrapped command exits immediately after launch.

```sh
scripts/record-ui-automation-video.sh \
  run \
  --name workspace-card-smoke \
  --start-on-app \
  --post-start-duration 45 \
  -- \
  zsh -lc 'xcrun simctl launch "$SIM_UDID" "$BUNDLE_ID"'
```

For an explicit XCUITest, use the dedicated wrapper:

```sh
scripts/record-xcuitest-video.sh \
  --name login-happy-path \
  --scheme App \
  --only-testing AppUITests/LoginTests/testHappyPath
```

`--only-testing` repeats for multi-test captures, and unrecognized options forward to `record-ui-automation-video.sh` (for example `--keep-raw` or `--sim-udid`). Keep the filter focused rather than recording a broader run. The wrapper encodes three rules a hand-assembled recording gets wrong:

- **Never wrap a test lane that shuts down or reboots the simulator around the test run.** Many projects' UI-test lanes do this to configure simulator state; a `simctl recordVideo` attached across that shutdown dies or freezes on stale frames. The wrapper instead records a raw `xcodebuild` invocation against the already-booted target simulator, passing the same test plan, destination, and derived-data arguments the lane would use — omitting those silently runs the wrong test plan or builds cold into the wrong `DerivedData`. Bypassing the lane also skips whatever simulator-state setup it performs (Password AutoFill suppression is a common one); a scenario that fills a password field may show the system save-password sheet on video.
- **Record XCUITest runs immediately — no `--start-on-app`.** Starting `simctl recordVideo` after XCTest has launched or attached to the app can produce stale captures that sit on the launch screen while the scenario runs, then resume after XCTest tears the app down.
- **Build in `--prepare`, record only the test.** A recorded `xcodebuild test` captures its build phase as dead air at the head of the video. The wrapper runs `xcodebuild build-for-testing` in `--prepare` and records `xcodebuild test-without-building`, so capture starts seconds before the app launches.

Use `--prepare` for setup that can be cleanly separated from the visual run. The prepare command runs through `zsh -lc`, writes `prepare.log`, and must succeed before recording or the wrapped command starts.

```sh
scripts/record-ui-automation-video.sh \
  run \
  --name already-built-launch \
  --prepare 'xcodebuild build -scheme App -destination "platform=iOS Simulator,id=$SIM_UDID"' \
  --start-on-app \
  --post-start-duration 30 \
  -- \
  zsh -lc 'xcrun simctl launch "$SIM_UDID" "$BUNDLE_ID"'
```

Prefer `run --duration` for timed captures. Use `start` and `stop` only when a manual reproduction cannot be expressed as a command or fixed-duration window. Keep the `start` command running in its shell while the recording is active; run `stop` from another shell or tool call.

```sh
scripts/record-ui-automation-video.sh start --name message-thread-scroll

# In another shell: run the focused command, drive the simulator manually, or use a UI-driving tool.

scripts/record-ui-automation-video.sh stop
```

For a fixed-duration capture, wrap `sleep`:

```sh
scripts/record-ui-automation-video.sh \
  run \
  --name manual-repro-window \
  --duration 45
```

## Operating Rules

- Target a specific simulator. The script resolves `--sim-udid`, then the `SIM_UDID` environment variable; it does not choose a booted simulator implicitly. Set `SIM_UDID` to the simulator your project's tooling targets.
- Use `--start-on-app` for launch captures where a new app process is the event you want to record. It defaults to the `BUNDLE_ID` environment variable; pass `--start-on-app <bundle-id>` explicitly otherwise.
- Do not use `--start-on-app` for XCUITest scenario recordings; see the XCUITest rules under Common Workflow.
- Pass `--post-start-duration` when the wrapped command only launches the app and exits; omit it for test commands that stay alive for the scenario.
- Pass `--prepare` for non-visual setup that should fail fast before recording starts.
- Leave compression defaults alone unless diagnosing encoder behavior. `UI_AUTOMATION_VIDEO_FPS`, `UI_AUTOMATION_VIDEO_CRF`, and `UI_AUTOMATION_VIDEO_PRESET` exist for controlled experiments.
- Pass `--output-dir` only when the artifact needs to live outside the derived-data directory.
- Pass `--keep-raw` when compression quality is under review or the compressed video can hide a rendering issue.
- Pass `--no-compress` only when speed matters more than handoff size.
- Keep names short and scenario-specific. Prefer `message-thread-send-failure` over `test-run`.
- If a command needs pipes, shell expansion, or sourced variables, wrap it with `zsh -lc '...'` after `--` — or `bash -lc '...'` when it sources bash-only helper scripts from your project.
- Verify the artifact before handoff: confirm the duration in `metadata.txt` is plausible for the scenario, then extract a few frames (`ffmpeg -ss <t> -i <video> -frames:v 1 <frame>.png`) at key moments and view them to confirm the capture shows the scenario — not a frozen launch screen, home screen, or dead air. A run that exited zero can still be visually wrong.
- When polling for completion, wait for `recording.state` to disappear from the run directory and the compression fields to land in `metadata.txt`. The run directory and `metadata.txt` appear when recording starts, not when it finishes.
- Include the final primary video path in PR notes, issue-tracker comments, or handoff summaries when the recording is part of the evidence.

## Failure Handling

- If the wrapped command fails, keep the video and command log; the script exits with the command's status.
- If the recorded simulator shuts down mid-capture (the signature of wrapping a lane that reboots the simulator), the video is invalid even when the tests pass; re-record through `record-xcuitest-video.sh`.
- If `--prepare` fails, no recording starts; inspect `prepare.log` and `metadata.txt`.
- If `--start-on-app` is passed for an XCTest-looking command, the script records immediately and notes the adjustment in `metadata.txt`; set `UI_AUTOMATION_VIDEO_ALLOW_XCTEST_START_ON_APP=1` to keep late-start behavior.
- If `--start-on-app` does not detect a new app process before the timeout, no recording is produced; inspect `trigger.log` and `command.log`.
- If recording fails, treat the run as invalid even when the wrapped command succeeds.
- If compression fails or the compressed file fails sanity checks, use the raw video as the primary artifact, report the compression status from `metadata.txt`, and keep the wrapper exit status tied to the recording and wrapped command.
- If an active recording is stale, run `stop --run-dir <artifact-directory>` when the directory is known; otherwise inspect `.active-*.state` under the artifact root to find the canonical `recording.state`.

## Reference Map

Load only what the task needs:

- `scripts/record-ui-automation-video.sh`: the full recorder — `run`/`start`/`stop`, delayed start, compression, and validation. Run it with `--help` for the option contract.
- `scripts/record-xcuitest-video.sh`: the XCUITest wrapper encoding the three rules above. Run it with `--help` for the option contract.

# Verification and Checklist

Run the narrowest appropriate Apple build/test/lint commands and confirm the Apple-specific cleanup checklist before finalizing.

## Tests and Verification for Apple Projects

Prefer the repository's documented commands. Discover schemes and destinations instead of inventing them.

### SwiftPM

For package-scoped changes, choose the command matching the required evidence. `swift test` already builds its test graph; do not run all three examples in sequence:

```sh
swift build
swift test
swift test --filter <TestName>
```

For packages with multiple platforms or conditional imports, verify affected platforms when practical. Inspect `Package.swift` platforms before assuming support.

### Xcode Build and Test

Discover first:

```sh
xcodebuild -list
xcodebuild -list -json
xcrun simctl list devices available
```

Then choose the narrowest valid command. Examples, only after replacing placeholders with discovered values:

```sh
xcodebuild -project <Project>.xcodeproj -scheme <Scheme> -destination 'generic/platform=iOS Simulator' build
xcodebuild -workspace <Workspace>.xcworkspace -scheme <Scheme> -destination 'generic/platform=iOS Simulator' build
xcodebuild -workspace <Workspace>.xcworkspace -scheme <Scheme> -destination 'platform=iOS Simulator,name=<Available Device>' test
```

For framework/package targets inside Xcode projects, prefer the smallest target/scheme that covers the touched files. For app-wide UI/lifecycle/availability changes, run an app build at minimum.

### Formatting and Linting

Run only if configured or requested:

```sh
swiftformat <changed files>
swiftlint lint --strict
```

If tools are installed through Mint, mise, Bundler, npm, Homebrew, or project scripts, use the repository's configured invocation rather than a global command.

### Availability Verification

When a change touches availability, build with the declared minimum deployment target and the current selected SDK. If practical, run or test on an older supported simulator/device as well as the newest target SDK path. If older simulators are unavailable, state that limitation.

### Concurrency Verification

When a change touches Swift concurrency, run the build configuration that surfaces strict concurrency warnings/errors. Do not claim concurrency safety solely because a non-strict local build passed if the repository has stricter CI settings.

## Apple-Specific Cleanup Checklist

Before finalizing Apple-platform work, confirm:

- Local Swift, Xcode, SDK, scheme, destination, package, and deployment-target facts were discovered rather than assumed.
- Runtime availability checks use `#available`/`@available`; compiler/module/platform checks use the correct conditional mechanism.
- Older-OS fallbacks remain for the declared minimum deployment targets.
- Swift concurrency isolation, sendability, task ownership, cancellation, and main-actor boundaries remain correct.
- SwiftUI state ownership, identity, lifecycle effects, navigation, focus, layout, animation, localization, and accessibility remain correct.
- UIKit/AppKit lifecycle, reuse, delegate ownership, constraints, responder behavior, and cleanup remain correct.
- Foundation formatting, calendrical logic, URL/path construction, coding strategies, networking, persistence, keychain, and file behavior preserve contracts.
- Project wrappers for design system, localization, analytics, logging, dependency injection, networking, persistence, feature flags, and compatibility were searched before keeping local code.
- Resources, entitlements, privacy manifests, target membership, and generated project files were not altered accidentally.
- The narrowest meaningful SwiftPM or Xcode build/test/lint command was run, or a concrete blocker was reported.

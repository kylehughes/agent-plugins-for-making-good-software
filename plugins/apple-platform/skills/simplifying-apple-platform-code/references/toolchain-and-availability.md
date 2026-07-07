# Toolchain and Availability

Detect the local Apple toolchain and project facts, then apply availability and backward-compatibility rules for code that spans deployment targets.

## Toolchain and Project Detection

Before judging Apple-platform code, inspect the relevant local facts. Use only commands appropriate for the repository.

Useful commands:

```sh
swiftc --version
xcode-select -p
xcodebuild -version
xcodebuild -showsdks
xcodebuild -list
xcodebuild -list -json
xcrun simctl list devices available
swift package dump-package
swift package describe --type json
```

For Xcode projects/workspaces, inspect build settings only after discovering valid schemes/workspaces/projects:

```sh
xcodebuild -showBuildSettings -scheme <Scheme>
xcodebuild -showBuildSettings -workspace <Workspace>.xcworkspace -scheme <Scheme>
xcodebuild -showBuildSettings -project <Project>.xcodeproj -scheme <Scheme>
```

Also inspect when present:

- `Package.swift`, `Package.resolved`, `.swift-version`, `.swiftpm`, `Package@swift-*.swift`.
- `.xcodeproj/project.pbxproj`, `.xcworkspace`, `.xcconfig`, `.xcscheme`, target membership, build phases, generated project inputs.
- Tuist, XcodeGen, Bazel, Buck, Fastlane, CocoaPods, Carthage, Mint, mise/asdf, Makefile, Justfile, CI config, and project README.
- Deployment settings such as `IPHONEOS_DEPLOYMENT_TARGET`, `MACOSX_DEPLOYMENT_TARGET`, `WATCHOS_DEPLOYMENT_TARGET`, `TVOS_DEPLOYMENT_TARGET`, supported destinations, extension settings, app groups, entitlements, privacy manifests, and bundle settings.
- Swift settings such as `SWIFT_VERSION`, strict concurrency flags, upcoming feature flags, warning-as-error settings, module stability, library evolution, whole-module optimization, and package tools version.

Do not invent scheme names, workspace names, simulator names, SDK versions, or build commands. Discover them or state the limitation.

## Availability and Backward Compatibility

For Apple apps spanning older deployment targets and newer SDKs, be exact:

- Use `if #available(...)` or `guard #available(...) else` for runtime OS API availability.
- Use `if #unavailable(...)` only when it clarifies the fallback and the repository's Swift version supports it.
- Use `@available` on declarations when an entire type, member, protocol conformance, overload, property wrapper, or extension is unavailable on older OS versions.
- Use `#if compiler(>=...)` or `#if swift(>=...)` only for compiler/language syntax differences, not runtime OS APIs.
- Use `#if canImport(...)` for module availability, not OS availability.
- Use `#if os(...)`, `#if targetEnvironment(...)`, and conditional target membership for platform families and environments, not API version checks.
- Do not expose newer-OS-only types in APIs that must be callable from older-OS code unless the declaration is itself availability-gated.
- Do not delete fallbacks for the declared minimum OS. Keep fallback behavior reachable and testable.
- Prefer a small compatibility wrapper when multiple call sites need the same version split.
- Avoid `ProcessInfo.operatingSystemVersion`, string parsing, selector checks, reflection, or manual framework probing when normal Swift availability checking works.
- Verify whether a new API is actually back-deployed before replacing older code with it. Back-deployed implementation, compiler support, SDK availability, and runtime OS support are separate facts.
- Treat beta APIs as unstable unless the repo has explicit beta branches or guards. Keep beta-only types out of stable public APIs.
- Watch for app-extension availability. APIs involving `UIApplication.shared`, process-wide app state, opening URLs, background modes, or shared containers may be unavailable or inappropriate in extensions.
- Watch for platform-specific behavior in shared code. iOS, iPadOS, macOS, Catalyst, visionOS, watchOS, tvOS, widgets, intents, and extensions often need different lifecycle and capability assumptions.

Availability fixes are correctness fixes, not style changes.

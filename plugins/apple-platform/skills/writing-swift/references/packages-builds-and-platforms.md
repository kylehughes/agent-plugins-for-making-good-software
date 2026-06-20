# Packages, Builds, and Platforms

## Contents

- Discover the build contract
- SwiftPM manifests and dependencies
- Package resources, plugins, macros, and traits
- SwiftPM validation
- Xcode projects and workspaces
- Availability and platform conditionals
- Cross-platform source design
- Embedded Swift
- Objective-C, C, and C++ interoperability
- Generated code
- CI and reproducibility

## Discover the Build Contract

Before editing build configuration, identify:

- Checked-in toolchain selectors such as `.swift-version`, `.xcode-version`, Mise, asdf, swiftly, Docker, or CI images.
- The SwiftPM tools version and language modes.
- Xcode project/workspace, shared schemes, test plans, configurations, and destinations.
- Minimum deployment versions and supported architectures.
- Binary dependencies, plugins, macros, generated sources, and package registries.
- Repository wrappers such as Make, just, Fastlane, Tuist, XcodeGen, Bazel, or custom scripts.

Use the repository's wrapper command when it encodes required environment, flags, code generation, or CI behavior.

## SwiftPM Manifests and Dependencies

Keep `Package.swift` declarative and readable. The tools-version directive controls available manifest APIs and the minimum
SwiftPM version that can load the package. Raise it only for a needed API or explicit support-policy change.

Specify platforms from product requirements. Do not infer them from the SDK installed on the current machine.

Use products to describe supported client entry points and targets to express module boundaries. Avoid cyclic or umbrella
target structures that exist only to hide dependency direction.

Dependency policy:

- Do not run `swift package update` during unrelated work.
- Preserve `Package.resolved` according to repository type and policy. Applications commonly commit it; reusable libraries
  may intentionally omit it.
- Prefer a compatible version range for source packages unless exact pinning is required by reproducibility or risk policy.
- Review transitive license, platform, toolchain, and binary-artifact implications before adding a package.
- Avoid adding a dependency for a small capability available in the standard library or existing project infrastructure.
- Verify checksum and origin for binary targets.

Use target dependencies and access control to prevent accidental layering violations. `package` access can expose shared
implementation across package targets without creating public API.

## Package Resources, Plugins, Macros, and Traits

Declare resources explicitly and access SwiftPM-managed resources through `Bundle.module`. Confirm deployment behavior in
all relevant products, especially tests and command-line tools.

Build-tool plugins and command plugins execute code during package workflows. Review sandbox permissions, generated output
locations, reproducibility, and CI support. Never edit plugin-generated files as the source of truth.

Macros add a compiler plugin and generated syntax boundary. Inspect expansion when debugging, keep diagnostics actionable,
and test both successful expansion and misuse. Do not introduce a macro for logic a function, generic, or property wrapper
expresses more transparently.

Swift 6.3 adds package trait inspection with:

```bash
swift package show-traits
```

Treat traits as part of the package's supported configuration matrix. Build meaningful combinations in CI and avoid a
combinatorial feature-flag design.

## SwiftPM Validation

Use the narrowest commands first:

```bash
swift --version
swift package dump-package
swift build --target TargetName
swift test --filter TestName
swift build -c release
swift test
```

`dump-package` catches manifest errors without intentionally updating dependencies. A normal build may still resolve
missing dependencies; inspect the diff afterward.

Useful diagnostics vary by toolchain:

```bash
swift package describe
swift package show-dependencies
swift package show-traits
swift test list
```

Do not assume every subcommand exists on older supported toolchains. Use `swift <command> --help` when scripting across
versions.

For a reusable library, test a small external consumer when public imports, resources, macros, or product composition
change. `@testable import` cannot catch every consumer-facing problem.

## Xcode Projects and Workspaces

Prefer the workspace when one exists and is used by CI. The `swift` executable on `PATH` may not be the compiler selected
by Xcode, so record both command-line and Xcode toolchains when diagnosing version-specific behavior:

```bash
swift --version
xcrun swift --version
xcodebuild -version
xcode-select -p
```

Discover shared schemes and destinations:

```bash
xcodebuild -list -workspace App.xcworkspace
xcodebuild -showdestinations -workspace App.xcworkspace -scheme App
```

Then build or test with an explicit configuration and destination. Use a generic destination for compilation-only checks
when appropriate; use a concrete simulator/device destination for tests that require runtime execution. Inspect effective
build settings rather than inferring them from one project file:

```bash
xcodebuild -showBuildSettings -workspace App.xcworkspace -scheme App -configuration Debug
```

Look specifically for the active Swift version, selected toolchain, deployment targets, compilation conditions, and
concurrency-related settings. Environment variables such as `DEVELOPER_DIR` and `TOOLCHAINS` can override global selection.

Avoid modifying `project.pbxproj` by hand when the project is generated. Change the generator input and regenerate through
the checked-in workflow. When direct project edits are required, keep them minimal and inspect UUID churn and target
membership.

Do not bypass code signing globally as a generic fix. Match CI's signing flags and distinguish simulator, macOS, package,
and archive requirements.

Do not begin diagnosis by deleting `.build` or Derived Data. Preserve the reproduction first; clean caches only when stale
artifacts are a supported hypothesis, then rerun the same command to prove the effect.

Use `-derivedDataPath` only when isolation or CI cleanup requires it. Do not commit derived data, result bundles, or build
products.

For test failures, preserve `.xcresult` bundles when they contain logs, attachments, screenshots, or performance metrics
needed for diagnosis.

## Availability and Platform Conditionals

Separate compile-time platform presence from runtime API availability:

```swift
#if canImport(UIKit)
import UIKit
#endif

@available(iOS 18, macOS 15, *)
func useNewAPI() { }

if #available(iOS 18, macOS 15, *) {
    useNewAPI()
} else {
    useFallback()
}
```

Annotate declarations when the entire API requires a newer runtime. Use runtime checks when one implementation can choose
between new and fallback paths.

Do not overuse `#if os(...)`. Prefer capability checks such as `canImport`, shared protocols, and small platform adapters.
Every conditional branch should compile in CI. Watch for `#if DEBUG` code that changes correctness rather than diagnostics.

Compiler and language gates serve different purposes; see `swift-6.3.2.md`.

## Cross-Platform Source Design

Keep platform-neutral domain logic in platform-neutral targets. Put Foundation/UI/network/file-system adapters behind
small boundaries. Avoid importing Apple-only frameworks into shared model targets. Some platforms still expose networking
APIs through a separate module:

```swift
#if canImport(FoundationNetworking)
import FoundationNetworking
#endif
```

Consider platform differences in:

- File paths, permissions, process and signal behavior.
- Networking stacks, TLS, proxies, and URL handling.
- Locale, calendars, time zones, and ICU behavior.
- Threading and event-loop integration.
- Dynamic libraries and linker flags.
- Objective-C runtime availability.
- XCTest/Swift Testing runner support.
- SDK-specific API annotations and deployment availability.

Swift 6.3 includes official Android SDK support, but “compiles on Android” is not guaranteed by pure Swift syntax. Audit
Foundation and system-module availability, build plugins, binary dependencies, JNI/platform bridges, and packaging.

For Linux, Windows, and WebAssembly targets, use each platform's official SDK/toolchain guidance and test there. Do not
claim portability based solely on `#if canImport(Foundation)`.

## Embedded Swift

Treat Embedded Swift as a distinct product configuration rather than a normal package with a smaller deployment target.
Audit the supported language/runtime subset, SDK, linker script, allocation strategy, interrupt or concurrency model, and
size constraints for the board or environment. Keep hardware access and unsafe memory behind narrow interfaces, validate
release optimization and whole-module behavior, and inspect binary size and linker output.

Do not assume Foundation, Objective-C interoperability, reflection, dynamic loading, process APIs, or ordinary test runners
exist. Use the repository's emulator, hardware-in-the-loop, or host-side test strategy. Swift 6.3 improves Embedded Swift,
but feature support remains target- and SDK-specific.

## Objective-C, C, and C++ Interoperability

Preserve the existing interoperability boundary unless the task explicitly changes it.

For Objective-C:

- Account for nullability, selector naming, reference semantics, KVO/KVC, exceptions, and main-thread framework contracts.
- Use `@objc` and `dynamic` only when runtime dispatch or exposure requires them.
- Keep Objective-C-compatible public surface intentional; many Swift types and concurrency constructs do not bridge.

For C:

- Validate ownership, nullability, buffer length, alignment, lifetime, and error conventions at the boundary.
- Encapsulate unsafe pointers and expose safe Swift values.
- Use module maps/system-library targets where appropriate.
- Swift 6.3 `@c` and `@c @implementation` can support direct C-facing declarations; adopt them only when all supported
  compilers understand the feature and the ABI/design has been reviewed.

For C++:

- Confirm the supported Swift/C++ interoperability mode and compiler pair.
- Review value/reference lifetime, templates, exceptions, move-only types, and generated module interfaces.
- Keep imported C++ types behind a narrow Swift facade when they would otherwise leak toolchain-sensitive details.
- Test both debug and optimized configurations; interop issues can be configuration-specific.

Swift 6.3 module selectors such as `ModuleA::Type` can resolve imported-name ambiguity. Prefer a stable module-qualified
reference over ad hoc typealiases when the distinction matters at the use site.

## Generated Code

Identify generated files through headers, build scripts, plugins, SourceGen, protobuf/OpenAPI tools, Swift macros, or project
generators. Change the schema/template/source and run the canonical generator.

Before regeneration:

- Confirm the tool version.
- Avoid overwriting local manual changes.
- Know whether generated output is committed.
- Expect broad diffs and separate them from manual logic where possible.

After regeneration, inspect for nondeterministic ordering, timestamps, absolute paths, tool-version churn, and accidental
API changes.

## CI and Reproducibility

Mirror supported toolchain/Xcode versions and platform matrices. A local newest-toolchain build is not sufficient when the
project promises older support.

Good CI separation includes:

- Manifest/dependency validation.
- Debug build and focused unit tests.
- Release build for optimizer-only diagnostics.
- Platform-specific tests and oldest-deployment smoke tests.
- Formatting/linting using checked-in configuration.
- Documentation, macro/plugin, generated-code, and public-consumer checks where relevant.
- Sanitizer or stress jobs for concurrency/memory-sensitive code.

Treat warnings as errors where the repository can control the toolchain and warning set. Be cautious about embedding
warnings-as-errors in reusable package targets because new compiler warnings can break downstream consumers.

Do not print secrets or signing material. Redact environment diagnostics before sharing logs.

Primary references:

- https://docs.swift.org/package-manager/
- https://docs.swift.org/package-manager/PackageDescription/PackageDescription.html
- https://developer.apple.com/documentation/xcode/building-and-running-an-app
- https://www.swift.org/platform-support/

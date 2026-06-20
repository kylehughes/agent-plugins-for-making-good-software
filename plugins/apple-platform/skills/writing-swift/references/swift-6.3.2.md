# Swift 6.3.2 and Compatibility

## Contents

- Version model
- Greenfield defaults
- Manifest examples
- Compile-time and runtime gates
- Swift 6.2 baseline
- Swift 6.3 additions
- Swift 6.3.2 patch release
- Upgrade checklist
- Primary sources

## Version Model

Do not collapse four independent compatibility decisions into “uses Swift 6.3.2.”

| Dimension | Example | Controls |
| --- | --- | --- |
| Toolchain | Swift 6.3.2 | Compiler, standard library shipped with the toolchain, SwiftPM, SourceKit-LSP |
| Language mode | Swift 6 | Source semantics and strict concurrency enforcement |
| SwiftPM tools version | `// swift-tools-version: 6.3` | Which `PackageDescription` APIs the manifest may use |
| Deployment target | `.macOS(.v15)` | Oldest runtime on which the built product may execute |

A Swift 6.3.2 compiler can compile a package in Swift 5 language mode. A package can use Swift 6 language mode while still
supporting older OS versions if every runtime API is availability-gated. The SwiftPM tools-version directive normally
uses the major and minor version; do not write `6.3.2` unless a repository has a specific reason.

Before changing any dimension, inspect CI, Xcode settings, package manifests, release policy, binary consumers, and the
oldest supported developer environment.

## Greenfield Defaults

For a new package explicitly targeting Swift 6.3.2:

- Use `// swift-tools-version: 6.3`.
- Use Swift 6 language mode.
- Choose deployment targets from product requirements, not from the compiler version.
- Keep library modules nonisolated by default unless the entire API is intentionally main-actor-bound.
- Consider default `MainActor` isolation for application/UI modules with predominantly main-thread state.
- Enable warnings-as-errors in CI rather than forcing it on every consumer of a library target.
- Add upcoming or experimental features only when they are not already part of the selected language mode and the
  repository accepts the compatibility cost.

In Swift 6 language mode, complete strict-concurrency checking is part of the language semantics. Flags such as
`-strict-concurrency=complete` and the corresponding Xcode build setting are primarily migration controls for Swift 5
language mode; do not treat them as a substitute for selecting Swift 6.

## Manifest Examples

A portable library package should normally keep the language's nonisolated default:

```swift
// swift-tools-version: 6.3

import PackageDescription

let package = Package(
    name: "ExampleLibrary",
    platforms: [
        .iOS(.v17),
        .macOS(.v14),
    ],
    products: [
        .library(name: "ExampleLibrary", targets: ["ExampleLibrary"]),
    ],
    targets: [
        .target(name: "ExampleLibrary"),
        .testTarget(name: "ExampleLibraryTests", dependencies: ["ExampleLibrary"]),
    ],
    swiftLanguageModes: [.v6]
)
```

An application-oriented module may intentionally default declarations to `MainActor`:

```swift
.target(
    name: "AppFeature",
    swiftSettings: [
        .defaultIsolation(MainActor.self),
    ]
)
```

Apply default actor isolation at the appropriate package or target scope supported by the manifest API. The
`defaultIsolation` manifest setting requires Swift tools 6.2 or newer. Confirm generated interfaces and cross-module call
sites after changing it; this is an API and migration decision, not formatting.

The `swiftLanguageModes` manifest spelling is available in modern tools-version manifests; older manifests use
`swiftLanguageVersions`. Do not rename or raise the tools version unless the repository's supported SwiftPM versions permit
it.

For codebases using the Swift 6.2 migration model before adopting full Swift 6 semantics, you may encounter:

```swift
.enableUpcomingFeature("NonisolatedNonsendingByDefault")
```

Do not copy an upcoming-feature flag blindly. Check whether the selected language mode already enables the behavior and
whether all supported toolchains understand the setting.

## Compile-Time and Runtime Gates

Use the gate that matches the dependency:

```swift
#if compiler(>=6.3)
// Syntax or compiler capability available only in a Swift 6.3+ compiler.
#endif

#if swift(>=6.0)
// Behavior dependent on the active Swift language mode.
#endif

#if canImport(UIKit)
import UIKit
#endif

if #available(iOS 18, macOS 15, *) {
    // Runtime API available on these OS versions.
} else {
    // Back-deployment path.
}
```

Prefer source-compatible designs over dense compiler-condition branches. Build every supported branch in CI where
possible. Remember that package-manifest conditionals run in the manifest compiler context, not the target source context.

## Swift 6.2 Baseline

Swift 6.2 introduced several capabilities that commonly affect modern code and migration decisions:

- Module-level default actor isolation, including default `MainActor` isolation for suitable targets.
- Caller-context execution for nonisolated async functions under the corresponding language behavior, plus `@concurrent`
  for work that must run independently of the caller's actor.
- `InlineArray` and `Span` for specialized storage and safe contiguous-memory access.
- Opt-in strict memory safety checking.
- Warning-control settings in SwiftPM.
- Named tasks for diagnostics and observability.
- Typed `NotificationCenter` messages and observation-related improvements on supported Apple platforms.
- Swift Testing exit tests, attachments, and raw-identifier test names.

Adopt these only when they solve a concrete problem and all supported platforms/toolchains permit them. In particular,
`Span`, ownership annotations, and strict memory-safety features are not routine replacements for ordinary collections.

## Swift 6.3 Additions

Swift 6.3 adds capabilities that may matter in specialized work:

- `@c` declarations and `@c @implementation` for direct C implementation/interoperability workflows.
- Module-qualified symbol selection with syntax such as `ModuleA::Type` when imported names collide.
- Additional optimization and implementation-only controls, including `@specialize`, `@inline(always)`, and
  `@export(implementation)`. Use such attributes only with measurements and compatibility review.
- Swift Build as a preview build engine surfaced through SwiftPM workflows.
- Prebuilt Swift Syntax support for shared macro implementation libraries and package traits inspection through
  `swift package show-traits`.
- Swift Testing warning-severity issues, explicit test cancellation, and image attachments.
- Experimental DocC Markdown output, per-page static HTML content, and code-block annotations such as `nocopy`, `highlight`,
  `showLineNumbers`, and `wrap`. Keep experimental flags confined to documentation pipelines that intentionally adopt them.
- Official Swift SDK support for Android and further Embedded Swift improvements.

Do not “modernize” existing code by introducing new syntax without a need. Newer constructs can raise the minimum compiler
version, complicate source compatibility, or obscure a simpler implementation.

## Swift 6.3.2 Patch Release

Swift 6.3.2 is a patch release published May 13, 2026. It includes targeted compiler, interoperability, SwiftPM,
Swift Testing, and SourceKit-LSP fixes. Xcode 26.5 contains Swift 6.3.2. On supported standalone installations, use the
repository's toolchain manager or `swiftly install 6.3.2` rather than replacing a shared toolchain ad hoc.

Notable fixes include C++23 header imports on Linux, `Bundle.module` access from outside `MainActor`, and Swift Testing exit
tests that produce no standard output or error. When one of these symptoms appears on an earlier 6.3 toolchain, verify it
under 6.3.2 before preserving a workaround in source.

Patch releases should be low-risk, but still run the full relevant build and test matrix. Compiler fixes can expose code
that previously compiled accidentally, and tooling fixes can alter diagnostics or indexing behavior.

## Upgrade Checklist

1. Record the current toolchain, language mode, tools version, deployment targets, CI images, and Xcode versions.
2. Read release notes for every crossed minor release, not only the destination patch release.
3. Upgrade the toolchain without changing language mode first when feasible.
4. Compile every product and test target, including release builds and generated code.
5. Address warnings and concurrency diagnostics by modeling intent, not by applying escape hatches globally.
6. Change the SwiftPM tools version only when the manifest needs newer APIs.
7. Change the language mode separately and review source/API effects.
8. Exercise oldest supported runtimes and every conditional-compilation branch.
9. Verify package consumers, plugins, macros, C-family interop, documentation, and IDE/source-service behavior.
10. Keep upgrade-only changes separate from feature work when the repository workflow allows it.

## Primary Sources

- Swift 6.3 release: https://www.swift.org/blog/swift-6.3-released/
- Swift 6.3.2 release: https://forums.swift.org/t/announcing-swift-6-3-2/86698
- Swift 6.2 release: https://www.swift.org/blog/swift-6.2-released/
- Swift language mode migration: https://www.swift.org/migration/documentation/swift-6-concurrency-migration-guide/
- Swift evolution proposals: https://github.com/swiftlang/swift-evolution/tree/main/proposals
- PackageDescription documentation: https://docs.swift.org/package-manager/PackageDescription/PackageDescription.html

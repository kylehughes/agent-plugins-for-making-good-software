# Swift Toolchains and Compatibility

Use this reference to choose toolchain, language-mode, package-manifest, and deployment settings independently. [Swift feature status](../../modeling-swift-types-for-correctness/references/swift-feature-status.md) owns the dated current Swift/Xcode snapshot and feature availability; [iOS versioning](../../modeling-swift-types-for-correctness/references/ios-versioning.md) owns the iOS baseline and adapter policy.

## Version Model

Do not collapse four independent compatibility decisions into “uses current Swift.”

| Dimension | Example | Controls |
| --- | --- | --- |
| Toolchain | Selected Xcode Swift or explicit Swift.org toolchain | Compiler, standard library shipped with the toolchain, SwiftPM, SourceKit-LSP |
| Language mode | Swift 6 | Source semantics and strict concurrency enforcement |
| SwiftPM tools version | `// swift-tools-version: 6.3` | Which `PackageDescription` APIs the manifest may use |
| Deployment target | `.macOS(.v15)` | Oldest runtime on which the built product may execute |

Compiler version and language mode are separate: a current compiler can support more than one mode. This skill defaults to Swift 6; assess another mode as migration work. A package can use Swift 6 language mode while still
supporting older OS versions if every runtime API is availability-gated. The SwiftPM tools-version directive normally
uses the major and minor version; pin a patch only for an identified manifest requirement.

Before changing any dimension, inspect CI, Xcode settings, package manifests, release policy, binary consumers, and the
oldest supported developer environment.

## Greenfield Defaults

For a new package targeting the selected current toolchain:

- Choose the minimum SwiftPM tools version that supports the manifest APIs the package needs; the example below uses 6.3 as an illustrative floor, not the current-release snapshot.
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

For codebases adopting caller-isolation semantics, you may encounter:

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

Use compiler or language-mode branches only for an intentionally supported build matrix; do not add an older-mode implementation by default. Prefer source-compatible designs over dense branches. Build each supported branch in CI where possible. Remember that package-manifest conditionals run in the manifest compiler context, not the target source context.

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

Read [the shared source index](../../modeling-swift-types-for-correctness/references/sources.md) for official release notes, language-mode migration, Swift Evolution, and PackageDescription links. Consult historical release notes when investigating a regression or removing a workaround; they do not define the current baseline.

# Current Swift with iOS 16–27 Runtime Availability

Use this reference whenever an app is compiled with the current Swift toolchain but must run from iOS 16 through current or preview OS releases.

## Policy

This skill supports one Swift source baseline:

- Swift 6 language mode.
- The project’s selected current Xcode/Swift toolchain.
- No compatibility implementation for another Swift language mode.
- iOS 16 as the default minimum deployment target unless the project states otherwise.
- Runtime and SDK availability handled independently from language syntax.

A lower deployment target does not require an earlier Swift language mode. Compile current Swift source, then isolate every API or standard-library symbol whose runtime availability starts after iOS 16.

## Verified Toolchain Snapshot

Verified on **2026-06-21**:

- Swift.org lists Swift 6.3.2 as the current stable downloadable compiler.
- Xcode 26.5 is the current generally released Xcode listed by Apple and carries Swift 6.3-era tooling and the iOS 26.5 SDK.
- Xcode 26.6 RC 2 is prerelease software, not the production baseline.
- Xcode 27 beta includes Swift 6.4 and the iOS 27 SDK.

For an Apple-platform build, `xcrun swift --version`, `xcodebuild -version`, and the selected Xcode path are authoritative. Do not substitute the separately installed Swift.org toolchain for the compiler that actually builds the Xcode target.

Version numbers in this document are a dated snapshot. Recheck [sources.md](sources.md) before making a time-sensitive recommendation.

## The Relevant Axes

### 1. Minimum deployment target

The oldest OS on which the binary promises to launch, such as iOS 16.0. This controls runtime availability, weak linking, and which fallback paths must exist.

### 2. SDK used to compile

The SDK determines which declarations the compiler can see. Building with a current SDK does not make a current API callable on iOS 16.

### 3. Selected current Swift toolchain

Use the compiler shipped by the project’s selected Xcode channel. Record its full version in CI and bug reports. The skill does not maintain a source-compatibility matrix across past compilers.

### 4. Swift 6 semantic settings

Swift 6 language mode is necessary but not sufficient to characterize semantics. Inspect:

- Strict concurrency.
- Default actor isolation.
- Approachable concurrency.
- Upcoming and experimental features.
- Strict memory safety.
- Per-target settings and package-level overrides.

Two modules built by the same compiler can behave differently when these settings differ.

### 5. ABI and distribution boundary

An app target, source package, source-stable framework, and binary framework have different constraints. `BUILD_LIBRARY_FOR_DISTRIBUTION`, public inlinable code, generated interfaces, and library evolution can make an otherwise local type change externally significant.

## Gate Selection

| Need | Mechanism | What it proves |
|---|---|---|
| A module may not exist in the selected SDK/build | `#if canImport(Module)` | Source/module presence only |
| An API starts on a later iOS release | `@available` plus `if #available` | Declaration and runtime availability |
| Stable and beta Xcode are intentionally tested from one branch | Narrow `#if compiler(...)` around preview-only source | Compiler capability only |
| Code is platform-specific | `#if os(iOS)` | Platform family, not OS version |

Do not create language-mode branches. Do not use a compiler conditional to stand in for a runtime availability check.

### Runtime availability pattern

```swift
protocol AccountEventStream: Sendable {
    func events() -> AsyncStream<AccountDidChange>
}

func makeAccountEventStream() -> any AccountEventStream {
    if #available(iOS 26, *) {
        TypedNotificationAccountEventStream()
    } else {
        LegacyAccountEventStream()
    }
}
```

Keep the newer framework type inside the available declaration or implementation. The domain-facing protocol remains valid on iOS 16.

### Declaration availability pattern

```swift
@available(iOS 26, *)
struct InlineStorage<Element: ~Copyable, let Count: Int>: ~Copyable {
    private var storage: InlineArray<Count, Element>
}
```

Any declaration that mentions an unavailable type in its signature or stored representation must itself carry compatible availability.

## Current-Swift Feature and Runtime Matrix

| Feature or API | Swift/toolchain status | iOS runtime floor | Guidance for an iOS 16 app |
|---|---|---:|---|
| Typed throws, ownership modifiers, noncopyable types, primary associated types, constrained existentials, parameter packs | Current Swift language features | No blanket higher floor | Use directly when the model benefits; check any APIs used alongside them |
| Strict concurrency and default actor isolation controls | Current build semantics/settings | No blanket higher floor | Configure per target; fix actual isolation boundaries |
| Strict memory safety | Opt-in compiler audit mode | Build-time only | Add a current-toolchain CI audit lane; marked unsafe code still needs a proof |
| `BitwiseCopyable` | Current Swift representation contract | No blanket higher floor | Never treat it as serialization, C layout, endianness, or arbitrary-byte validity |
| `Span` type | Current standard-library lifetime type | Specially back-deployed to iOS 12.2; producers vary | Verify each producer API and lifetime dependency |
| `InlineArray` | Current fixed-size standard-library type | iOS 26+ | Keep it out of iOS 16 signatures and storage unless the declaration is available-gated |
| `Synchronization.Mutex` | Current Synchronization API | iOS 18+ | Use an actor or an iOS 16 lock adapter below iOS 18 |
| `OSAllocatedUnfairLock` | Current OS synchronization API | iOS 16+ | Valid low-level baseline when synchronous locking is justified |
| Typed NotificationCenter messages | Current Foundation API | iOS 26+ | Hide behind a domain event adapter with an iOS 16 implementation |
| Observation framework / `@Observable` | Current observation API | iOS 17+ | Keep an iOS 16 `ObservableObject` or manual observation adapter when needed |
| SwiftData | Current persistence framework | iOS 17+ | Keep domain models independent from the persistence adapter |
| Swift 6.4 preview features such as `anyAppleOS` and `@diagnose` | Xcode 27 beta at verification | No inherent blanket floor | Preview lane only; referenced APIs still need their own availability checks |

The key distinction is not “old Swift versus new Swift.” It is current source semantics versus runtime symbols that may not exist on the minimum OS.

## Feature Notes

### Typed throws

Use `throws(E)` when callers benefit from a narrow, closed failure surface. Use ordinary `throws` for integration boundaries whose failures are intentionally open-ended. This is an API-design choice, not a deployment-target workaround.

Be explicit where closure or generic inference becomes difficult. A typed failure surface should remain small enough that adding a case is a deliberate source-level contract change.

### `InlineArray`

`InlineArray` is available on iOS 26 and later. Therefore:

- Do not place it in an unannotated stored property, parameter, return type, or generic constraint of an iOS 16 declaration.
- Put the entire declaration that mentions it behind `@available(iOS 26, *)`.
- Keep a domain-level fallback such as a tuple, named struct, or validated array.
- Use it for measured layout or allocation needs, not merely to express a business count.
- Recheck its current protocol conformances and iteration behavior in the selected compiler.

### `Span`

The `Span` type is specially back-deployed, but an API that vends a span may begin on a later OS. Check the producer, not merely the type.

A nonescapable spelling is not itself a lifetime proof. Confirm that the compiler can see the owner dependency and that foreign calls or hidden copies do not invalidate it.

### Synchronization

`Synchronization.Mutex` starts at iOS 18, while `OSAllocatedUnfairLock` is available from iOS 16. Keep the primitive behind a concrete internal adapter so domain APIs do not encode its availability.

Prefer an actor unless the operation must be synchronous or profiling demonstrates that a lock is justified. Never hold a lock across `await` or arbitrary callbacks.

### Typed notifications

Foundation’s typed notification messages start at iOS 26. Define one domain event and provide modern and legacy adapters. Consumers should not branch on OS version or receive two payload shapes.

### Default actor isolation

Default isolation is a target or package setting, not a universal fact about Swift 6 source. Inspect:

- `SWIFT_DEFAULT_ACTOR_ISOLATION`.
- Package `.defaultIsolation(...)`.
- Strict-concurrency level.
- Approachable-concurrency and upcoming-feature settings.
- Imported SDK annotations and protocol requirements.

Do not infer a declaration’s isolation solely from a nearby source file.

## Project Settings to Inventory

### Xcode

Search and then resolve per scheme/configuration:

```text
IPHONEOS_DEPLOYMENT_TARGET
SWIFT_VERSION
SWIFT_STRICT_CONCURRENCY
SWIFT_DEFAULT_ACTOR_ISOLATION
SWIFT_APPROACHABLE_CONCURRENCY
SWIFT_STRICT_MEMORY_SAFETY
SWIFT_UPCOMING_FEATURE_*
SWIFT_EXPERIMENTAL_FEATURE_*
BUILD_LIBRARY_FOR_DISTRIBUTION
SDKROOT
SUPPORTED_PLATFORMS
OTHER_SWIFT_FLAGS
```

Require Swift 6 language mode for every affected target. A textual search is only an inventory; use `xcodebuild -showBuildSettings` on the actual scheme and configuration.

### Swift Package Manager

Inspect:

- `// swift-tools-version:`.
- `platforms: [.iOS(...)]`.
- Package `swiftLanguageModes: [.v6]` and target `.swiftLanguageMode(.v6)` where specified.
- `.enableUpcomingFeature(...)`.
- `.enableExperimentalFeature(...)`.
- `.defaultIsolation(...)` and `.strictMemorySafety()` where supported.
- Conditional dependencies, compiler defines, and binary products.

The package tools version controls manifest APIs. The language mode controls source semantics. The iOS platform declaration controls runtime deployment.

## Baseline Architecture

```text
Domain module
  - current Swift 6 enums, structs, IDs, validation, protocols
  - no later-OS public signatures without availability
  - Sendable and isolation explicit where meaningful

Platform adapter module
  - iOS 16 implementation
  - iOS 17/18/26 implementations behind availability
  - one stable domain-facing façade

Application/UI module
  - selects adapters through availability or dependency injection
  - may use newer UI APIs locally
```

This architecture preserves current Swift source quality without allowing one modern framework type to raise the runtime floor of the entire domain layer.

## Preview Lane

Use Xcode 27 beta, Swift 6.4, and iOS 27 SDK behavior only when the repository explicitly opts in.

Requirements:

1. Record the exact Xcode build, compiler build, and SDK seed.
2. Isolate preview-only source in files or targets.
3. Do not expose preview-only types from stable public APIs.
4. Keep production CI on the current stable Xcode until the project deliberately promotes the preview toolchain.
5. Add a preview CI job for early diagnostics rather than silently redefining the production baseline.
6. Re-run compile-fail fixtures and inspect generated interfaces after every seed.
7. Remove temporary workarounds after the final release.

A preview compiler is “latest,” but it is not automatically the project’s production toolchain.

## CI Matrix

Use one Swift source/toolchain baseline per channel and vary runtime coverage:

| Job | Purpose |
|---|---|
| Current production Xcode, Swift 6 mode, iOS 16 deployment target | Main compilation and unit tests |
| Current production Xcode with intended strict-concurrency/default-isolation settings | Isolation and `Sendable` diagnostics |
| Current production Xcode with strict memory safety enabled for audited targets | Unsafe-code inventory |
| Minimum iOS 16 runtime or direct fallback-adapter tests | Oldest supported behavior |
| iOS 17 and iOS 18 runtime or direct adapter tests | Observation/persistence and synchronization boundaries |
| Current iOS 26 runtime | Modern production adapter path |
| Current production Xcode archive | Linkage, release configuration, and distribution surface |
| Xcode 27 beta optional job | Preview diagnostics and iOS 27 behavior only |

A current simulator alone does not exercise fallback branches. Test adapters directly when older simulator runtimes are unavailable.

## Review Checklist

- Is every affected target in Swift 6 language mode?
- Is the selected Xcode/Swift toolchain recorded from the actual build environment?
- Is the iOS deployment target analyzed separately from source-language capability?
- Does every new symbol have verified SDK and runtime availability?
- Are runtime checks expressed with `@available` and `if #available` rather than compiler conditionals?
- Does every iOS 26 declaration have an iOS 16 façade or an intentionally raised floor?
- Is `InlineArray` fully contained in iOS 26-available declarations?
- Are `Span` producer APIs checked separately from the type?
- Is `Synchronization.Mutex` avoided or gated below iOS 18?
- Is default actor isolation known per target?
- Are public ABI and library-evolution effects considered?
- Is preview tooling isolated from the production baseline?
- Are modern and fallback paths tested for semantic parity?

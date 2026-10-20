# Platform and Build Baseline

Use this reference before making broad concurrency changes or when a fix depends on Swift version, Xcode settings, SDK availability, or iOS deployment target.

## Baseline for this skill

The default target uses the project's selected current toolchain, Swift 6 language mode, and iOS 16+ runtime support. [Swift feature status](../../modeling-swift-types-for-correctness/references/swift-feature-status.md) owns the dated compiler/Xcode snapshot and API availability; [iOS versioning](../../modeling-swift-types-for-correctness/references/ios-versioning.md) owns deployment policy. Latest Swift syntax is allowed. Runtime framework APIs still obey deployment target availability.

Separate these concepts every time:

| Question | Meaning | Example |
|---|---|---|
| Can the compiler parse this? | Swift toolchain/language feature. | `sending`, `@concurrent`, isolated conformances, `Task.immediate`. |
| Can this symbol link and run on iOS 16? | SDK/runtime API availability. | `Observation`, `Synchronization.Mutex`, new Foundation typed notifications, beta frameworks. |
| Does this module infer isolation? | Per-target compiler setting. | `-default-isolation MainActor` versus `nonisolated`. |
| Does this API cross actor boundaries? | Concurrency contract. | `Sendable`, `@Sendable`, `sending`, `async`, isolated parameters. |

Do not gate Swift language syntax with `#available(iOS ...)`. Do gate framework APIs introduced after iOS 16.

## Recommended compiler posture

For app/UI targets:

- Swift Language Mode: Swift 6.
- Swift 6 enforces complete strict-concurrency checking; migration settings do not replace the language mode.
- Default Actor Isolation: `MainActor` when the target mostly contains UI and app orchestration.
- Adopt caller-isolation and isolated-conformance behavior deliberately. Check which upcoming features the selected language mode already enables before adding flags.

For reusable domain, networking, persistence, and algorithm packages:

- Swift Language Mode: Swift 6.
- Swift 6 enforces complete strict-concurrency checking; migration settings do not replace the language mode.
- Default Actor Isolation: usually `nonisolated` unless the package is explicitly UI-only.
- Enable `NonisolatedNonsendingByDefault` and `InferIsolatedConformances` deliberately; avoid accidental `@MainActor` inference in DTO/model packages.

For test targets:

- Match the production target’s language mode and upcoming concurrency features where practical.
- Be cautious with default `MainActor` isolation on XCTest subclasses and helper types. Prefer explicit `@MainActor` on UI tests/test methods that need it instead of main-actor-isolating every test utility.

## SwiftPM settings shape

The examples show explicit behavior choices for a tools-version manifest that supports them. Check the selected compiler and language mode before copying upcoming-feature settings; remove a setting that is already enabled or rejected as redundant. For a UI package or feature target that intentionally defaults to the main actor:

```swift
.target(
    name: "FeatureUI",
    swiftSettings: [
        .swiftLanguageMode(.v6),
        .defaultIsolation(MainActor.self),
        .enableUpcomingFeature("NonisolatedNonsendingByDefault"),
        .enableUpcomingFeature("InferIsolatedConformances")
    ]
)
```

For a domain package that should remain nonisolated by default:

```swift
.target(
    name: "Domain",
    swiftSettings: [
        .swiftLanguageMode(.v6),
        .defaultIsolation(nil),
        .enableUpcomingFeature("NonisolatedNonsendingByDefault"),
        .enableUpcomingFeature("InferIsolatedConformances")
    ]
)
```

`nil` means nonisolated default isolation. If the manifest tools version does not support a setting, do not invent unsafe flags unless the user explicitly wants low-level build configuration.

## iOS 16 deployment consequences

Many concurrency language features are compiler/runtime features and are usable in an iOS 16 app built with a modern toolchain. Many newer Apple frameworks are not.

Check [platform adapter availability](../../modeling-swift-types-for-correctness/references/swift-feature-status.md#platform-adapter-availability) for the documented floors. Common compatibility choices:

| Feature/API | Guidance for iOS 16-compatible code |
|---|---|
| `@Observable` / Observation framework | Use `ObservableObject`/`@Published` or gate Observation-backed models below its documented floor. |
| `Synchronization.Mutex` | Newer OS only. For iOS 16 Apple-only code, prefer `OSAllocatedUnfairLock` when a lock is required. |
| SwiftData | Keep Core Data or another persistence fallback below the documented floor. |
| New Foundation typed notification APIs | Gate with `#available` and keep string/name-based fallback if supporting iOS 16. |
| APIs introduced after the deployment baseline | Gate module presence and runtime availability separately; isolate preview code. |

When the stored type differs by OS version, do not try to switch stored-property types with `if #available` inside one type. Use an abstraction, a separate implementation type, or set a higher deployment target.

## Availability patterns

Prefer direct runtime availability checks for APIs:

```swift
if #available(iOS 18, *) {
    await useNewAPI()
} else {
    await useIOS16Fallback()
}
```

For entire types that require a newer framework:

```swift
@available(iOS 17, *)
@Observable
@MainActor
final class SearchModel {
    var results: [Result] = []
}
```

For beta SDK code, isolate it in a small adapter:

```swift
protocol IntelligenceClient: Sendable {
    func answer(_ prompt: String) async throws -> String
}

struct FallbackIntelligenceClient: IntelligenceClient {
    func answer(_ prompt: String) async throws -> String { "" }
}

#if canImport(SomeBetaFramework)
@available(iOS 27, *)
struct BetaIntelligenceClient: IntelligenceClient {
    func answer(_ prompt: String) async throws -> String {
        // Beta-only API here.
    }
}
#endif
```

Swift has no general, official `#if sdk(iOS >= ...)` condition. `#if compiler(...)` is not an SDK availability check. `#if canImport(...)` only proves a module exists in the build environment, not that the runtime device supports it. Pair compile-time gates with `#available` when runtime availability matters.

## Lock selection for iOS 16+

Use a lock only when synchronous access is required or when the state is extremely small and a custom actor would force awkward async APIs. Never hold a lock across `await`.

Apple-only iOS 16+:

```swift
import OS

final class Counter: @unchecked Sendable {
    private let state = OSAllocatedUnfairLock(initialState: 0)

    func increment() -> Int {
        state.withLock { value in
            value += 1
            return value
        }
    }
}
```

The `@unchecked Sendable` conformance is an audit point: all mutable state must be protected by the lock, the protected value must not escape unsafely, and no operation may suspend while holding the lock.

Use `Synchronization.Mutex` only when the minimum OS supports it or the code is explicitly gated/newer-only. Do not replace a simple actor with a lock for performance without measurement.

## `@preconcurrency` imports and legacy modules

`@preconcurrency import` is a migration boundary for modules that lack complete concurrency annotations. It is not proof of thread safety.

Use it when all are true:

1. The dependency cannot be updated or annotated now.
2. You understand the dependency’s callback/threading contract.
3. You contain the unsafely imported API behind a small adapter with explicit isolation.

Prefer this shape:

```swift
@preconcurrency import LegacySDK

@MainActor
final class LegacyAdapter {
    private let sdk: LegacyClient

    init(sdk: LegacyClient) {
        self.sdk = sdk
    }

    func refresh() async throws -> Snapshot {
        try await sdk.refreshSnapshot()
    }
}
```

Do not spread `@preconcurrency` imports across many files.

## Beta and future OS policy

For APIs available only in the selected preview SDK (determine release status from [feature status](../../modeling-swift-types-for-correctness/references/swift-feature-status.md), rather than an OS number):

- Keep beta-only code in its own adapter or file.
- Gate compilation with `#if canImport(...)` when the module may not exist in older SDKs.
- Gate runtime use with the API's declared availability; `#if canImport` alone does not establish deployment support.
- Do not change core protocol contracts to require beta-only types. Convert beta-specific values to stable app/domain types at the boundary.
- Expect signatures, names, isolation annotations, and Sendable conformances to change before GM.

## Review checklist

- Is the target UI, domain, service, test, or mixed? Are default isolation settings appropriate for that role?
- Are Swift language features separated from iOS runtime availability?
- Is any iOS 17+ or beta API used unconditionally in iOS 16-compatible code?
- Is `@preconcurrency` localized and documented?
- Are locks chosen with deployment target and synchronous-access needs in mind?
- Would the same source compile in a package target with nonisolated default isolation?

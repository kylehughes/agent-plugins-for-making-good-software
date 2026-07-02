---
name: simplifying-apple-platform-code
description: Apple-platform companion skill for simplifying and hardening Swift, SwiftUI, UIKit, AppKit, Foundation, Xcode, and SwiftPM code across iOS, iPadOS, macOS, watchOS, tvOS, and visionOS. Use with simplifying-code when code touches Apple SDKs, Swift concurrency, platform availability, UI lifecycle, Apple build settings, resources, or Apple deployment targets.
---

# Simplify Apple-Platform Code

Run this as the Apple-platform companion to the universal `simplifying-code` skill. It adds Swift, Xcode, SDK, availability, concurrency, UI lifecycle, resource, and Apple-framework checks. It does not replace the universal behavior-preservation and reuse/deletion workflow.

If both skills are available, apply `simplifying-code` first to establish the review surface and universal cleanup passes, then apply this skill before editing and verification. When this Apple-specific guidance conflicts with a generic simplification heuristic, this guidance wins for Apple-platform code.

## Scope

Use this skill for:

- Swift, Objective-C, Objective-C++, C/C++ bridged into Apple apps, Swift packages, Xcode projects, app extensions, widgets, intents, watch apps, visionOS apps, and shared Apple-platform modules.
- SwiftUI, UIKit, AppKit, Foundation, Combine, Observation, Core Data, SwiftData, URLSession, StoreKit, WidgetKit, App Intents, MapKit, AVFoundation, CoreLocation, CoreBluetooth, UserNotifications, CloudKit, XCTest, and other Apple SDK usage.
- Projects that compile with a modern Swift toolchain while deploying across older and newer Apple OS releases.

For projects intended to use modern Swift, prefer the latest local Swift toolchain and language capabilities unless the repository proves otherwise. Do not preserve compatibility with old Swift compilers merely out of habit. Still, the local project settings are authoritative: compiler version, Swift language mode, SDK, minimum deployment targets, package tools versions, and CI commands must be detected from the repository or toolchain. Avoid hard-coded claims about the latest Swift or latest Apple OS version; detect them locally.

## Apple-Specific Contract

1. Preserve declared deployment targets. Do not delete older-OS fallbacks because the current SDK is newer. For projects spanning a range such as iOS 16 through current or beta SDKs, treat the lower bound as a real runtime contract until project settings change.
2. Separate compiler, SDK, module, and runtime availability. New syntax support does not imply old OS runtime support.
3. Preserve Swift concurrency isolation, cancellation, lifetime, and actor boundaries. Do not silence warnings by weakening isolation.
4. Treat UI code as behavior. Layout, navigation, state identity, focus, scrolling, animation, Dynamic Type, accessibility, localization, keyboard behavior, safe areas, and lifecycle timing are observable.
5. Prefer project primitives: design system, localization wrappers, analytics/logging, error mapping, dependency injection, persistence wrappers, feature flags, compatibility shims, environment keys, and test helpers.
6. Avoid changing Xcode project settings, Swift language mode, signing, entitlements, bundle identifiers, deployment targets, package tools version, or target membership unless the user explicitly asked or the cleanup cannot build without it.
7. Keep beta SDK APIs isolated behind availability checks and do not make stable paths depend on beta-only behavior unless the project is explicitly beta-only.

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

## Swift Language Simplification

Prefer modern Swift when the repository supports it, but preserve semantics:

- Use strong domain types, enums, option sets, result types, and value types where they clarify state. Do not collapse meaningful models into strings, dictionaries, tuples, or `Any`.
- Prefer clear `guard` exits, optional chaining, nil coalescing, pattern matching, and standard-library collection APIs when they reduce branching without hiding failure behavior.
- Prefer `let` over `var`, narrower visibility, and immutable value flow where safe.
- Remove unused imports, unused accessors, unused state, empty extensions, redundant type annotations, redundant `self`, redundant closures, redundant `return`, and redundant access-control modifiers only when consistent with local style.
- Avoid unnecessary type erasure (`AnyView`, `AnyPublisher`, `AnySequence`, `AnyHashable`, existential `any`) unless it solves a real boundary, storage, ABI, or abstraction problem.
- Avoid over-generic helpers. A concrete function with domain names is usually clearer than a generic utility used once.
- Preserve `Equatable`, `Hashable`, `Identifiable`, `Codable`, `Sendable`, `Comparable`, and custom protocol semantics. Generated conformances are safe only when they preserve the same meaning and stored-property order/behavior where relevant.
- Preserve `Codable` keys, decoding defaults, lossy parsing behavior, unknown-field tolerance, date strategies, data strategies, and migration compatibility.
- Preserve error types and cancellation. Do not convert typed/domain errors into generic strings or `nil` if callers distinguish cases.
- Use force unwraps/casts only for true invariants. Prefer explicit failure paths in production code and targeted `XCTUnwrap`/test helpers in tests.
- Be careful with property wrappers, macros, result builders, and observation features. They can change initialization, identity, observation, threading, and availability.
- Do not change package tools version, Swift language mode, compiler flags, or upcoming feature flags as a side effect of cleanup.

## Swift Concurrency

Treat Swift concurrency warnings as correctness signals unless proven otherwise.

### Actor Isolation and Main Actor

- Preserve actor isolation. UI-facing state, view models, observable models, stores, coordinators, presenters, and controller logic are often `@MainActor`; do not remove that isolation to silence warnings.
- Prefer an isolated API boundary over scattered `DispatchQueue.main.async` calls.
- Use `MainActor.run` for narrow hops into UI isolation. Use `@MainActor` on declarations when the entire API is UI-bound.
- Do not move work off the main actor if the code touches UI state, SwiftUI state, UIKit/AppKit objects, Core Data main contexts, or other main-thread-bound resources.
- Do not mark methods `nonisolated` unless they only read immutable, thread-safe data or intentionally provide a cross-actor API.
- Avoid `MainActor.assumeIsolated` except for narrow, proven invariants.

### Sendability and Shared State

- Treat `Sendable`, `@Sendable`, `@unchecked Sendable`, `@preconcurrency`, and unsafe imports as boundaries. Use unchecked forms only when the invariant is true and worth documenting.
- Do not capture mutable reference types, UI objects, clients, delegates, contexts, or view models in concurrent closures unless the isolation and lifetime are correct.
- Prefer immutable value snapshots when crossing actor/task boundaries.
- Be careful with singletons, caches, clients, date/number formatters, decoders/encoders, database contexts, and notification centers across actors. Verify thread-safety or isolate access.
- Do not silence data-race warnings by making state global, optional, weak, or unchecked-sendable without addressing the race.

### Task Lifetime and Cancellation

- Prefer structured concurrency (`async`/`await`, `async let`, task groups, cancellation propagation) over callbacks, ad hoc queues, and detached work when the surrounding code already supports it.
- Avoid `Task.detached` unless isolation, priority, cancellation, lifetime, and error handling are explicitly intended.
- Avoid unowned fire-and-forget `Task {}` in models, views, and controllers unless there is a clear owner or it is intentionally one-shot.
- Store task handles when work must be cancelled on deinit, reuse, disappearance, or changed input.
- Preserve cancellation in `.task`, async loaders, streaming APIs, URL requests, observers, Combine bridges, and request pipelines.
- Prefer `.task(id:)` for SwiftUI work keyed to identity/input changes. Avoid repeated `.onAppear` launches without cancellation.
- Do not use sleep-based synchronization. Use clocks, dependency-injected schedulers/clocks, expectations, async sequences, or deterministic test hooks.
- Do not convert sequential code to concurrent code unless operations are independent and side effects, ordering, cancellation, and error behavior are understood.

### Bridging with Legacy APIs

- Prefer `withCheckedContinuation` or `withCheckedThrowingContinuation` over unsafe continuations unless a legacy API truly violates checked-continuation rules.
- Resume continuations exactly once on all paths, including cancellation and error paths.
- Keep delegate lifetimes alive for async wrappers.
- Preserve callback queue assumptions when bridging to async/await.
- For Combine-to-async bridges, preserve cancellation, buffering, completion, and threading semantics.

## SwiftUI

SwiftUI simplification must preserve identity, state, lifecycle, layout, and accessibility.

### State and Identity

- Use the right state owner: `@State` for view-owned value state, `@Binding` for parent-owned state, `@StateObject` for view-owned reference models, `@ObservedObject` for externally owned models, environment wrappers for injected app context, and focus/storage wrappers when appropriate.
- Do not replace a persistent model owner with a recreated model in `body` or an initializer that runs repeatedly.
- Remove mirrored state when it can be derived safely, but preserve state that intentionally captures user edits, in-flight input, focus, selection, scroll position, animation phase, or presentation state.
- Preserve stable identity in `ForEach`, lists, grids, navigation paths, matched geometry, scroll targets, and diffing. Do not use indices or random IDs unless identity is truly positional or ephemeral.
- Avoid `.id(...)` as a reset hammer unless reset semantics are intentional.
- Preserve `EquatableView`, `.equatable()`, and memoization only when they protect meaningful performance or behavior; remove them when they are obsolete and safe.

### Lifecycle and Effects

- Keep `body` pure and cheap. Do not start network requests, database writes, subscriptions, timers, task creation, or analytics events directly from `body`.
- Prefer `.task(id:)` for async effects tied to view identity/input. Preserve cancellation when the view disappears or input changes.
- Use `.onAppear`/`.onDisappear` carefully; they can run multiple times. Do not move one-time app logic there unless repeats are harmless or guarded.
- Preserve scene lifecycle, app lifecycle, deep links, handoff, restoration, notification routing, and background behavior.
- Keep presentation state coherent. Sheets, alerts, confirmation dialogs, popovers, navigation destinations, and full-screen covers should not be driven by duplicated boolean/item state that can conflict.

### Layout, Navigation, and Rendering

- Preserve Dynamic Type, layout direction, safe areas, keyboard avoidance, scroll behavior, focus, edit mode, selection, hover/pointer, split-view behavior, and platform idioms.
- Avoid `GeometryReader` for simple layout when stacks, grids, layout priorities, view-that-fits, container-relative frames, or custom layout primitives already fit.
- Avoid `AnyView` unless required for storage, ABI, or type erasure at a real boundary.
- Break very large views into named subviews only when it improves identity, state ownership, reuse, or readability. Do not fragment views into wrappers that add no behavior.
- Preserve navigation path types, deep-link restoration, destination availability, back behavior, and programmatic navigation semantics.
- Be cautious when replacing older navigation APIs with newer ones in apps that support older OS versions.
- Avoid expensive formatting, sorting, filtering, image work, or allocation inside `body`; move stable work into models, cached derived values, or local constants with clear invalidation.

### Accessibility and Localization in SwiftUI

- Preserve `accessibilityLabel`, `accessibilityValue`, `accessibilityHint`, `accessibilityIdentifier`, traits, sort priority, focus behavior, Dynamic Type, reduced motion, high contrast, color-blind safety, and VoiceOver grouping.
- Do not replace localized `Text` or `LocalizedStringKey` usage with raw `String` interpolation if it changes localization extraction, pluralization, formatting, or grammar.
- Use project localization wrappers and design-system text styles when present.

### Observation

- Use Observation or observable-object patterns according to the repository's deployment target and architecture. Do not migrate `ObservableObject` to newer observation mechanisms unless availability, architecture, and test coverage support the change.
- Preserve dependency injection and testability when simplifying observable models.
- Avoid broad `@MainActor` or observation annotations on pure data types if it creates unnecessary isolation; prefer the narrowest correct isolation.

## UIKit, AppKit, and Representables

### Lifecycle and Ownership

- Preserve view/controller lifecycle semantics. Do not move setup between `init`, `loadView`, `viewDidLoad`, `viewWillAppear`, `viewDidAppear`, `viewWillDisappear`, `deinit`, or SwiftUI representable hooks unless repeat behavior and timing are correct.
- UI work must stay on the main thread/actor.
- Avoid retain cycles in closures, delegates, display links, timers, notifications, Combine subscriptions, and async tasks. Use weak captures only when losing work is acceptable; otherwise create an explicit owner/cancellation path.
- Clean up observers, tasks, timers, gesture recognizers, display links, KVO, delegates, and data sources according to their ownership model.
- Preserve responder chain, target/action behavior, first responder, keyboard commands, menus, focus engine, undo manager, state restoration, and scene/window ownership.

### Reuse, Data Sources, and Layout

- Preserve cell/view reuse semantics. Cancel image/network/task work on reuse and avoid stale async updates.
- Preserve diffable data source identity, section/item IDs, snapshot ordering, animation choices, and reload/reconfigure semantics.
- Do not simplify Auto Layout constraints by removing priority, hugging/compression, safe area, readable content, or intrinsic-size behavior that protects real layouts.
- Avoid adding constraints repeatedly in lifecycle methods that can run multiple times.
- Preserve layout invalidation, preferred content size, trait collection handling, size class behavior, rotation behavior, and content inset adjustment.
- Avoid doing heavy work in scrolling, layout, drawing, or display callbacks.

### SwiftUI Bridges

For `UIViewRepresentable`, `UIViewControllerRepresentable`, `NSViewRepresentable`, and `NSViewControllerRepresentable`:

- Keep coordinator ownership and delegate lifetimes correct.
- Preserve `make*` versus `update*` responsibilities. Do not recreate platform views/controllers in update paths unless intentional.
- Preserve binding propagation, feedback-loop prevention, focus/first-responder behavior, intrinsic size, layout invalidation, and environment changes.
- Cancel or detach work when the represented view/controller is dismantled.

## Foundation, Data, Networking, and Persistence

### Formatting, Localization, and Calendrical Logic

- Use project formatting/localization wrappers when present.
- Prefer `URLComponents`, `URLQueryItem`, `URL`, and platform path APIs over string concatenation for URLs and paths.
- Preserve `Locale`, `Calendar`, `TimeZone`, numbering system, capitalization, measurement units, currency, pluralization, and grammar behavior.
- Be careful when caching formatters. Mutable `Formatter` subclasses and shared instances need thread/actor safety; value-style formatters may be safer when available and compatible.
- Preserve date parsing strategies, fractional seconds, timezone assumptions, default dates, server/client clock behavior, and user-visible formatting.

### Encoding, Decoding, and Models

- Preserve `CodingKeys`, optionality, default values, lossy decoding, unknown case handling, unknown-field tolerance, snake/camel-case strategies, date/data strategies, and backwards/forwards compatibility.
- Do not simplify models by removing seemingly unused fields that are required for decoding, persistence, analytics, debugging, equality, hashing, or future migrations.
- Preserve identity semantics for models used in SwiftUI, diffable data sources, caches, persistence, and network updates.

### Networking

- Preserve request construction, query encoding, headers, auth, content type, caching policy, timeout, retry policy, cancellation, redirect behavior, status-code handling, error mapping, rate limits, and background-session behavior.
- Do not log secrets, tokens, cookies, personal data, or full request/response bodies unless the project has a redaction policy.
- Prefer project clients and endpoint abstractions over local `URLSession` calls if the project has them.
- Preserve offline behavior, cache invalidation, pagination, ETags, idempotency keys, and duplicate-request suppression.

### Persistence

- Preserve migrations, schema versions, model identifiers, store locations, app-group containers, encryption, backups/exclusions, conflict policy, and data-retention behavior.
- For Core Data, preserve context confinement, merge policy, parent/child context behavior, batch operation side effects, faulting, fetch predicates, sort descriptors, fetch limits, relationship delete rules, and persistent history behavior.
- For SwiftData, verify deployment availability and model/migration implications before replacing Core Data or custom persistence. Do not use it in code paths that must run on unsupported OS versions without guards.
- For `UserDefaults`, preserve keys, suites, registration defaults, migration, reset behavior, and app-extension sharing.
- For Keychain and secure storage, use existing wrappers and preserve access groups, accessibility class, synchronizable behavior, and migration.
- For files, preserve atomic writes, file protection, coordination, security-scoped resource access, sandbox/container paths, temporary-file cleanup, and backup behavior.

## Apple Framework and Capability Pitfalls

When touched code uses these areas, apply extra caution:

- **App extensions/widgets/intents:** preserve extension-safe APIs, timeline reload policy, shared containers, privacy, performance budgets, and process lifetime assumptions.
- **StoreKit/subscriptions:** preserve transaction verification, entitlement refresh, restore behavior, product identifiers, subscription group logic, server notification assumptions, and idempotency.
- **Notifications/background work:** preserve authorization state, scheduling identifiers, background modes, expiration handlers, task identifiers, and main-thread handoff.
- **Location/Bluetooth/Health/Photos/Camera/Microphone/Contacts/Calendars:** preserve permissions, purpose strings, privacy prompts, background behavior, delegate lifetime, and restricted/denied states.
- **AVFoundation/media:** preserve session configuration ordering, interruption handling, audio session categories, thread usage, permissions, and cleanup.
- **CloudKit/iCloud:** preserve container identifiers, zones, subscriptions, conflict handling, account status, retries, and offline behavior.
- **MapKit/CoreLocation:** preserve authorization, accuracy, region monitoring limits, background modes, and user-location privacy.
- **SF Symbols/assets/colors/fonts:** verify symbol and asset availability across deployment targets; preserve rendering mode, dynamic color behavior, contrast, high contrast, and variable color semantics.
- **Entitlements/privacy manifests:** treat them as behavioral/security configuration. Do not remove or alter them as cleanup without a concrete reason.

## Localization, Accessibility, and Design System

Apple UI cleanup should actively protect user-visible behavior:

- Preserve localized keys and extraction behavior. Do not change keys casually; key changes can break translations.
- Preserve pluralization, formatted interpolation, grammatical agreement, bundle/table selection, comments for translators, and string-catalog compatibility.
- Prefer project text, spacing, color, typography, icon, haptics, animation, and component tokens over literal values.
- Preserve accessibility identifiers used by UI tests.
- Preserve VoiceOver order, grouping, headings, traits, values, actions, adjustable controls, focus restoration, Switch Control behavior, Dynamic Type, reduced motion, differentiate-without-color, high contrast, and content size categories.
- Do not simplify colors, images, labels, or gestures in a way that makes state available only by color, motion, or visual layout.

## Tests and Verification for Apple Projects

Prefer the repository's documented commands. Discover schemes and destinations instead of inventing them.

### SwiftPM

For package-scoped changes:

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

## Final Response Addendum

In addition to the universal final summary, include Apple-specific facts when relevant:

1. Detected toolchain/build surface: package or Xcode target/scheme, selected Xcode/Swift when checked, and relevant deployment target if checked.
2. Availability or deployment-target issues fixed or intentionally left unchanged.
3. Concurrency or UI-lifecycle issues fixed or intentionally deferred.
4. Exact Apple build/test/lint commands run and results, including simulator/destination when applicable.

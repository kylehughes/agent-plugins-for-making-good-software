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

## Reference Map

Load only the reference relevant to the code under review:

- [Toolchain and availability](references/toolchain-and-availability.md): Xcode/SwiftPM project detection and runtime/compiler availability rules.
- [Swift and concurrency](references/swift-and-concurrency.md): Swift language simplification and Swift concurrency isolation, sendability, and task lifetime.
- [UI frameworks](references/ui-frameworks.md): SwiftUI state/identity/lifecycle and UIKit/AppKit/representable ownership and layout.
- [Foundation frameworks and capabilities](references/foundation-frameworks-and-capabilities.md): Foundation, networking, persistence, Apple framework pitfalls, localization, and accessibility.
- [Verification and checklist](references/verification-and-checklist.md): Apple build/test/lint verification commands and the Apple-specific cleanup checklist.

Before finalizing, run the Apple-specific cleanup checklist in [verification-and-checklist](references/verification-and-checklist.md).

## Final Response Addendum

In addition to the universal final summary, include Apple-specific facts when relevant:

1. Detected toolchain/build surface: package or Xcode target/scheme, selected Xcode/Swift when checked, and relevant deployment target if checked.
2. Availability or deployment-target issues fixed or intentionally left unchanged.
3. Concurrency or UI-lifecycle issues fixed or intentionally deferred.
4. Exact Apple build/test/lint commands run and results, including simulator/destination when applicable.

# Primary Sources

This file records the primary specifications and official documentation used to verify time-sensitive or easily conflated guidance. Re-check availability in the actual SDK because documentation and beta behavior evolve.

Last verified: **2026-06-21**.

## Agent Skills

- OpenAI Codex Agent Skills: https://developers.openai.com/codex/skills
- Agent Skills specification: https://agentskills.io/specification
- Agent Skills best practices: https://agentskills.io/skill-creation/best-practices
- Agent Skills description guidance: https://agentskills.io/skill-creation/optimizing-descriptions
- OpenAI skill creator reference: https://github.com/openai/skills/tree/main/skills/.system/skill-creator

Key structural constraints reflected in this package:

- `name` is lowercase/hyphenated and matches the directory.
- `description` is below 1024 characters and includes activation cues.
- `SKILL.md` is below the recommended 500 lines.
- Detailed material is split into directly linked, focused references.
- Scripts are self-contained and provide actionable errors.
- Trigger and quality evals are included.

## Current Apple and Swift Releases

- Apple developer software releases: https://developer.apple.com/news/releases/
- Xcode 26.5 release notes: https://developer.apple.com/documentation/xcode-release-notes/xcode-26_5-release-notes
- Xcode 27 beta release notes: https://developer.apple.com/documentation/xcode-release-notes/xcode-27-release-notes
- Swift stable downloads: https://www.swift.org/install/
- Apple's “What's new in Swift”: https://developer.apple.com/swift/whats-new/
- Xcode build settings reference: https://developer.apple.com/documentation/xcode/build-settings-reference
- SwiftPM `SwiftSetting` reference: https://docs.swift.org/swiftpm/documentation/packagedescription/swiftsetting/
- SwiftPM changelog: https://github.com/swiftlang/swift-package-manager/blob/main/CHANGELOG.md

Snapshot used by this version:

- Xcode 26.5 (17F42): current generally released Apple toolchain, with Swift 6.3-era tooling and the iOS 26.5 SDK.
- Xcode 26.6 RC 2 (17F113): prerelease at the verification date.
- Swift.org current stable download: Swift 6.3.2.
- Xcode 27 beta (27A5194q): Swift 6.4 and iOS 27 SDK preview lane.

For Apple-platform builds, the compiler reported by the selected Xcode via `xcrun swift --version` is authoritative. This skill uses one current Swift 6 language baseline rather than preserving source compatibility with another language mode.

## Swift Evolution

- SE-0302 Sendable and `@Sendable`: https://github.com/swiftlang/swift-evolution/blob/main/proposals/0302-concurrent-value-and-concurrent-closures.md
- SE-0346 Primary associated types / lightweight same-type syntax: https://github.com/swiftlang/swift-evolution/blob/main/proposals/0346-light-weight-same-type-syntax.md
- SE-0352 Implicitly opened existentials: https://github.com/swiftlang/swift-evolution/blob/main/proposals/0352-implicit-open-existentials.md
- SE-0353 Constrained existential types: https://github.com/swiftlang/swift-evolution/blob/main/proposals/0353-constrained-existential-types.md
- SE-0377 Borrowing and consuming parameters: https://github.com/swiftlang/swift-evolution/blob/main/proposals/0377-parameter-ownership-modifiers.md
- SE-0389 Attached macros: https://github.com/swiftlang/swift-evolution/blob/main/proposals/0389-attached-macros.md
- SE-0390 Noncopyable structs and enums: https://github.com/swiftlang/swift-evolution/blob/main/proposals/0390-noncopyable-structs-and-enums.md
- SE-0393 Value and type parameter packs: https://github.com/swiftlang/swift-evolution/blob/main/proposals/0393-parameter-packs.md
- SE-0395 Observation: https://github.com/swiftlang/swift-evolution/blob/main/proposals/0395-observability.md
- SE-0413 Typed throws: https://github.com/swiftlang/swift-evolution/blob/main/proposals/0413-typed-throws.md
- SE-0426 `BitwiseCopyable`: https://github.com/swiftlang/swift-evolution/blob/main/proposals/0426-bitwise-copyable.md
- SE-0427 Noncopyable generics: https://github.com/swiftlang/swift-evolution/blob/main/proposals/0427-noncopyable-generics.md
- SE-0430 `sending` parameters and results: https://github.com/swiftlang/swift-evolution/blob/main/proposals/0430-transferring-parameters-and-results.md
- SE-0437 Noncopyable standard-library primitives: https://github.com/swiftlang/swift-evolution/blob/main/proposals/0437-noncopyable-stdlib-primitives.md
- SE-0446 Nonescapable types: https://github.com/swiftlang/swift-evolution/blob/main/proposals/0446-non-escapable.md
- SE-0452 Integer generic parameters: https://github.com/swiftlang/swift-evolution/blob/main/proposals/0452-integer-generic-parameters.md
- SE-0453 `InlineArray`: https://github.com/swiftlang/swift-evolution/blob/main/proposals/0453-vector.md
- SE-0456 `Span`-providing standard-library properties: https://github.com/swiftlang/swift-evolution/blob/main/proposals/0456-stdlib-span-properties.md
- SE-0458 Opt-in strict memory safety: https://github.com/swiftlang/swift-evolution/blob/main/proposals/0458-strict-memory-safety.md
- SE-0461 Async function isolation and `@concurrent`: https://github.com/swiftlang/swift-evolution/blob/main/proposals/0461-async-function-isolation.md
- SE-0465 Nonescapable standard-library primitives: https://github.com/swiftlang/swift-evolution/blob/main/proposals/0465-nonescapable-stdlib-primitives.md
- SE-0466 Default actor isolation controls: https://github.com/swiftlang/swift-evolution/blob/main/proposals/0466-control-default-actor-isolation.md
- SE-0522 Source-level warning control with `@diagnose`: https://github.com/swiftlang/swift-evolution/blob/main/proposals/0522-source-warning-control.md
- SE-0516 `Iterable` / borrowing iteration (active review at the verification date, not a stable commitment): https://github.com/swiftlang/swift-evolution/blob/main/proposals/0516-iterable.md
- Swift compiler documentation for `anyAppleOS`: https://docs.swift.org/compiler/documentation/diagnostics/use-any-apple-os-availability/

Important proposal details reflected in the skill:

- Primary associated types and constrained existentials preserve selected relationships but do not turn protocols into nominal generic types.
- Parameter packs should be adopted only where heterogeneous arity is natural and the current compiler's diagnostics remain understandable.
- Typed throws does not provide universally complete or ergonomic inference; prefer explicit signatures at brittle generic and closure boundaries.
- `BitwiseCopyable` is a permanent representation promise, not a serialization or C-layout guarantee.
- Integer generic parameters and new standard-library nominal types can have Apple-platform runtime availability independent of source syntax.
- `InlineArray` has an iOS 26 deployment requirement; recheck its current protocol conformances and iteration APIs in the selected toolchain.
- Strict memory safety is opt-in and inventories unsafe operations; it does not verify the programmer's proof inside `unsafe` expressions.
- Default actor isolation is a module-level setting, not a universal property of Swift 6 source.
- A nonescapable type requires valid lifetime dependencies; spelling `~Escapable` is not by itself an owner-lifetime proof.
- `anyAppleOS` and `@diagnose` are Swift 6.4 beta source features at the verification date; neither supplies runtime availability for APIs it references.
- SE-0516 was in active review at the verification date; do not describe its borrowing-iteration model or proposed conformances as shipped stable behavior until its status and implementation are rechecked.

## Apple API Availability

- `InlineArray`: https://developer.apple.com/documentation/swift/inlinearray
- `Span`: https://developer.apple.com/documentation/swift/span
- `RawSpan`: https://developer.apple.com/documentation/swift/rawspan
- `Synchronization.Mutex`: https://developer.apple.com/documentation/synchronization/mutex
- `OSAllocatedUnfairLock`: https://developer.apple.com/documentation/os/osallocatedunfairlock
- Foundation notification center messages: https://developer.apple.com/documentation/foundation/notification-center-messages
- `NotificationCenter.MainActorMessage`: https://developer.apple.com/documentation/foundation/notificationcenter/mainactormessage
- `NotificationCenter.AsyncMessage`: https://developer.apple.com/documentation/foundation/notificationcenter/asyncmessage
- Observation: https://developer.apple.com/documentation/observation
- `Observable`: https://developer.apple.com/documentation/observation/observable
- SwiftData: https://developer.apple.com/documentation/swiftdata
- URLComponents: https://developer.apple.com/documentation/foundation/urlcomponents
- Keychain Services: https://developer.apple.com/documentation/security/keychain-services
- CryptoKit: https://developer.apple.com/documentation/cryptokit
- File system programming guide: https://developer.apple.com/library/archive/documentation/FileManagement/Conceptual/FileSystemProgrammingGuide/
- Security-scoped bookmarks and resources: https://developer.apple.com/documentation/foundation/nsurl/bookmark_creation_options

Availability facts used by the compatibility guidance:

| Symbol/framework | Documented Apple-platform availability relevant to iOS |
|---|---:|
| `InlineArray` | iOS 26+ |
| `Span` type | iOS 12.2+ through special back deployment; producer APIs vary |
| `Synchronization.Mutex` | iOS 18+ |
| `OSAllocatedUnfairLock` | iOS 16+ |
| Typed NotificationCenter message APIs | iOS 26+ |
| Observation framework | iOS 17+ |
| SwiftData | iOS 17+ |

## Verification Policy

When this skill is updated:

1. Check Apple's releases page for stable, RC, and beta status.
2. Check the actual Xcode release notes for included Swift and SDK versions.
3. Check Swift.org for the current stable downloadable compiler.
4. Record `xcrun swift --version` from the Xcode that actually builds the Apple target.
5. Check Apple documentation for every runtime symbol's exact availability.
6. Check accepted Swift Evolution proposals for current semantics, limitations, and future directions.
7. Type-check fixtures in Swift 6 mode with the selected current compiler.
8. Run `python3 scripts/validate_skill.py .`.
9. Update `metadata.last-verified` and this file only after the checks pass.

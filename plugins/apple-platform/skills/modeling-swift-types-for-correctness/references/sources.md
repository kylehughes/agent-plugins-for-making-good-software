# Primary Sources

This file records the primary specifications and official documentation used to verify time-sensitive or easily conflated guidance. Re-check availability in the actual SDK because documentation and beta behavior evolve.

This is the primary-source index. [Swift feature status](swift-feature-status.md) owns dated verification scope, current release/channel facts, feature support, and Apple availability floors. The original index was reviewed on 2026-10-19; individual links are not a claim of fresh compiler execution.

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
- Xcode 27 release notes: https://developer.apple.com/documentation/xcode-release-notes/xcode-27-release-notes
- Swift stable downloads: https://www.swift.org/install/
- Swift 6.4 release: https://www.swift.org/blog/swift-6.4-released/
- Swift 6.4.1 announcement: https://forums.swift.org/t/announcing-swift-6-4-1/90029
- Apple's “What's new in Swift”: https://developer.apple.com/swift/whats-new/
- Xcode build settings reference: https://developer.apple.com/documentation/xcode/build-settings-reference
- SwiftPM `SwiftSetting` reference: https://docs.swift.org/swiftpm/documentation/packagedescription/swiftsetting/
- SwiftPM changelog: https://github.com/swiftlang/swift-package-manager/blob/main/CHANGELOG.md

For Apple-platform builds, record the compiler from the selected Xcode. A standalone Swift.org toolchain and an Xcode toolchain are separate selections. Read [iOS versioning](ios-versioning.md) for deployment and build-setting rules.

Historical release sources retained for upgrade and workaround investigations:

- Swift 6.2 release: https://www.swift.org/blog/swift-6.2-released/
- Swift 6.3 release: https://www.swift.org/blog/swift-6.3-released/
- Swift 6.3.2 announcement: https://forums.swift.org/t/announcing-swift-6-3-2/86698
- Swift language-mode migration: https://www.swift.org/migration/documentation/swift-6-concurrency-migration-guide/
- PackageDescription: https://docs.swift.org/package-manager/PackageDescription/PackageDescription.html

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
- SE-0474 Yielding accessors: https://github.com/swiftlang/swift-evolution/blob/main/proposals/0474-yielding-accessors.md
- SE-0493 Async `defer`: https://github.com/swiftlang/swift-evolution/blob/main/proposals/0493-defer-async.md
- SE-0504 Task cancellation shields: https://github.com/swiftlang/swift-evolution/blob/main/proposals/0504-task-cancellation-shields.md
- SE-0507 Borrow and mutate accessors: https://github.com/swiftlang/swift-evolution/blob/main/proposals/0507-borrow-accessors.md
- SE-0516 `Iterable` / borrowing iteration: https://github.com/swiftlang/swift-evolution/blob/main/proposals/0516-borrowing-sequence.md
- SE-0517 `UniqueBox`: https://github.com/swiftlang/swift-evolution/blob/main/proposals/0517-uniquebox.md
- SE-0518 Suppressing inferred `Sendable`: https://github.com/swiftlang/swift-evolution/blob/main/proposals/0518-tilde-sendable.md
- SE-0519 `Ref` and `MutableRef`: https://github.com/swiftlang/swift-evolution/blob/main/proposals/0519-ref-mutableref-types.md
- SE-0525 Safe raw-byte loading: https://github.com/swiftlang/swift-evolution/blob/main/proposals/0525-rawspan-safe-loading-api.md
- SE-0527 `UniqueArray` manuscript: https://github.com/swiftlang/swift-evolution/blob/main/proposals/0527-rigidarray-uniquearray.md
- SE-0528 Noncopyable `Continuation`: https://github.com/swiftlang/swift-evolution/blob/main/proposals/0528-noncopyable-continuation.md
- SE-0530 Async `Result`: https://github.com/swiftlang/swift-evolution/blob/main/proposals/0530-async-result-support.md
- SE-0531 Literal expressions: https://github.com/swiftlang/swift-evolution/blob/main/proposals/0531-literal-expressions.md
- SE-0532 Additional noncopyable `Optional` operations: https://github.com/swiftlang/swift-evolution/blob/main/proposals/0532-optional-noncopyable-improvements.md
- SE-0543 `InlineArray` equality and hashing: https://github.com/swiftlang/swift-evolution/blob/main/proposals/0543-inline-array-hashable.md
- SE-0544 Mutation and consumption in `deinit`: https://github.com/swiftlang/swift-evolution/blob/main/proposals/0544-mutate-or-consume-in-deinit.md
- SE-0551 Single-value span adapters: https://github.com/swiftlang/swift-evolution/blob/main/proposals/0551-span-of-one.md
- SE-0556 Interior-mutable cells: https://github.com/swiftlang/swift-evolution/blob/main/proposals/0556-cell.md
- Swift compiler documentation for `anyAppleOS`: https://docs.swift.org/compiler/documentation/diagnostics/use-any-apple-os-availability/

Important proposal details reflected in the skill:

- Primary associated types and constrained existentials preserve selected relationships but do not turn protocols into nominal generic types.
- Parameter packs should be adopted only where heterogeneous arity is natural and the current compiler's diagnostics remain understandable.
- Typed throws does not provide universally complete or ergonomic inference; prefer explicit signatures at brittle generic and closure boundaries.
- `BitwiseCopyable` is a permanent representation promise, not a serialization or C-layout guarantee.
- Integer generic parameters and new standard-library nominal types can have Apple-platform runtime availability independent of source syntax.
- `InlineArray` has runtime availability independent of integer-generic syntax; check the status matrix and selected SDK for its members and conformances.
- Strict memory safety is opt-in and inventories unsafe operations; it does not verify the programmer's proof inside `unsafe` expressions.
- Default actor isolation is a module-level setting, not a universal property of Swift 6 source.
- A nonescapable type requires valid lifetime dependencies; spelling `~Escapable` is not by itself an owner-lifetime proof.
- Swift 6.4 language support, experimental flags, unavailable forms, and Apple deployment floors are tracked in [Swift feature status](swift-feature-status.md). Accepted proposals and compiler probes do not establish Apple deployment support.
- Borrowing iteration does not promise stable borrows across iterator mutation; implementation status and deployment floors are recorded in the feature matrix.

## Apple API Availability

- `InlineArray`: https://developer.apple.com/documentation/swift/inlinearray
- `Span`: https://developer.apple.com/documentation/swift/span
- `RawSpan`: https://developer.apple.com/documentation/swift/rawspan
- `Ref`: https://developer.apple.com/documentation/swift/ref
- `UniqueBox`: https://developer.apple.com/documentation/swift/uniquebox
- `UniqueArray`: https://developer.apple.com/documentation/swift/uniquearray
- `Iterable`: https://developer.apple.com/documentation/swift/iterable
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

Use [the feature matrix](swift-feature-status.md) for the maintained availability facts. A symbol's documentation does not establish the availability of every producer or operation that mentions it.

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
9. Update the relevant dates and evidence scopes in [feature status](swift-feature-status.md) only for completed checks. Preserve earlier or supplied evidence labels for checks not repeated.

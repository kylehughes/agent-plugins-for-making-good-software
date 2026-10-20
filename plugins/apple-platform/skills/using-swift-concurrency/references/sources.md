# Sources and Maintenance Notes

This skill uses Swift 6 language-mode semantics with the project's selected current toolchain. Read [Swift feature status](../../modeling-swift-types-for-correctness/references/swift-feature-status.md) for dated release/channel facts and feature availability. Refresh this guidance when compiler defaults, isolation rules, or SDK annotations change.

Primary sources to re-check during maintenance:

- Historical Swift 6.3 release notes: https://www.swift.org/blog/swift-6.3-released/
- Swift 6.2 release notes and approachable concurrency overview: https://www.swift.org/blog/swift-6.2-released/
- Swift book concurrency chapter: https://docs.swift.org/swift-book/documentation/the-swift-programming-language/concurrency/
- Apple strict concurrency migration guide: https://developer.apple.com/documentation/swift/adoptingswift6
- SE-0430 `sending` parameter and result values: https://github.com/swiftlang/swift-evolution/blob/main/proposals/0430-transferring-parameters-and-results.md
- SE-0433 Mutex: https://github.com/swiftlang/swift-evolution/blob/main/proposals/0433-mutex.md
- SE-0434 global-actor-isolated type usability: https://github.com/swiftlang/swift-evolution/blob/main/proposals/0434-global-actor-isolated-types-usability.md
- SE-0449 `nonisolated` to prevent global actor inference: https://github.com/swiftlang/swift-evolution/blob/main/proposals/0449-nonisolated-for-global-actor-cutoff.md
- SE-0461 nonisolated async functions on caller actor by default: https://github.com/swiftlang/swift-evolution/blob/main/proposals/0461-async-function-isolation.md
- SE-0466 default actor isolation inference: https://github.com/swiftlang/swift-evolution/blob/main/proposals/0466-control-default-actor-isolation.md
- SE-0470 global-actor isolated conformances: https://github.com/swiftlang/swift-evolution/blob/main/proposals/0470-isolated-conformances.md
- SE-0472 immediate tasks: https://github.com/swiftlang/swift-evolution/blob/main/proposals/0472-task-start-synchronously-on-caller-context.md
- Apple `#available` guidance: https://developer.apple.com/documentation/xcode/running-code-on-a-specific-version
- Apple Swift Testing async/confirmation docs: https://developer.apple.com/documentation/testing/testing-asynchronous-code

High-signal secondary sources reflected in the heuristics:

- Matt Massicotte’s Swift Concurrency articles, especially actors, protocol design, conformances, stateful systems, and problematic patterns.
- Swift Forums discussions by Swift language/toolchain engineers around default isolation, testing confirmation semantics, and upcoming feature flags.

Maintenance checklist:

- Verify latest Swift toolchain version and Xcode mapping.
- Verify whether upcoming feature flags have become default and remove stale wording.
- Re-check availability of `Synchronization.Mutex`, Observation APIs, Foundation typed notification APIs, and any iOS beta APIs.
- Re-check syntax for SwiftPM settings and task APIs.
- Re-test examples in a Swift 6 language-mode package with iOS 16 deployment and a current Xcode.

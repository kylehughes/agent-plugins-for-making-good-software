---
name: using-swift-concurrency
description: "Design or debug Swift concurrency, isolation, Sendable, actors, tasks, and cancellation. Use proactively for async behavior, concurrency migrations, or compiler diagnostics."
---

# Using Swift Concurrency

Use this skill to produce Swift concurrency code that is correct under strict concurrency and practical for iOS applications with deployment targets as low as iOS 16. Treat concurrency as a design problem first and a diagnostic-silencing problem last.

## Scope and assumptions

- Preserve the project’s selected compiler and language mode; recommend Swift 6 migration only within the requested scope. [Feature status](../modeling-swift-types-for-correctness/references/swift-feature-status.md) owns dated support and availability facts; consult it when a mechanism depends on toolchain or SDK support.
- Inspect deployment targets before choosing APIs. The references illustrate an iOS 16 compatibility lane; it is not a default to impose on other projects. Gate framework APIs relative to the actual runtime minimum.
- Determine stable versus preview support from the selected SDK and official release evidence. Gate newer APIs by their declaration availability; compiler support alone does not establish iOS 16 deployment.
- Prefer portable Swift and Apple-platform APIs that are available on iOS 16+. If using a newer API such as Observation, Synchronization.Mutex, typed notifications, or beta frameworks, call out the availability implication.
- Remove older workarounds only after checking the project’s supported compiler and language modes.

For a claim about ownership, representable state, typed failure, or mandatory completion, first load the [type-modeling skill body](../modeling-swift-types-for-correctness/SKILL.md) and follow its composition and focused-reference requirements. Reading one of its recipes alone skips that assessment contract. This skill retains scheduling, isolation repair, and task-lifecycle guidance.

## First pass

1. Identify the module’s concurrency dialect: Swift language mode, strict concurrency level, default actor isolation, `NonisolatedNonsendingByDefault`, `InferIsolatedConformances`, deployment target, and whether this code lives in an app/UI target or reusable package.
2. Classify the task using the reference map below and read the narrowest matching reference first.
3. Draw the isolation map: which state is UI-bound, actor-bound, task-bound, locked, immutable, transferred, or intentionally non-Sendable.
4. Draw the lifetime map: who owns each task, how cancellation propagates, and what happens when a view/view-model/service deinitializes.
5. Fix the underlying model. Avoid mechanical fixes such as `@MainActor` everywhere, `Task.detached`, `@unchecked Sendable`, `@preconcurrency`, `MainActor.run`, or `assumeIsolated` unless the reference says they are the right semantic tool.
6. Validate API availability separately from concurrency correctness.

## Reference map

| Read | When |
|---|---|
| `references/platform-and-build-baseline.md` | Choosing build settings, Swift 6 semantic settings, iOS 16+ availability, SPM/Xcode settings, beta SDK boundaries, or deployment-target-safe primitives. |
| `references/concurrency-model.md` | Understanding `nonisolated(nonsending)`, `@concurrent`, `Task.immediate`, actor inheritance, region isolation, `sending`, isolated parameters, or where code runs. |
| `references/ui-and-mainactor.md` | SwiftUI/UIKit/AppKit-style UI state, view models, view lifecycle tasks, `@Observable`/`ObservableObject`, main-thread work, deinit cleanup, or UI callback isolation. |
| `references/task-lifecycle-and-cancellation.md` | Choosing between structured, unstructured, immediate, and detached tasks; cancellation; task handles; priorities; parent-child relationships; task groups. |
| `references/actor-decisions.md` | Choosing `actor`, `@MainActor`, `class` with lock, value type, custom global actor, or no isolation; reviewing a new custom actor. |
| `references/sendable-and-transfer.md` | Fixing `Sendable`, `@Sendable`, `sending`, non-Sendable captures, `@unchecked Sendable`, locks, global actor Sendability, or transfer diagnostics. |
| `references/protocol-design.md` | Designing protocols under default actor isolation, `Sendable`, async/sync requirements, closure isolation, service abstractions, or reusable packages. |
| `references/isolation-and-protocol-conformances.md` | Resolving `Equatable`, `Hashable`, `Codable`, `Identifiable`, `CustomStringConvertible`, `ObservableObject`, delegates, or other conformance isolation errors. |
| `references/logical-races-and-reentrancy.md` | Reviewing state machines, button taps, actor methods with `await`, request ordering, stale state after suspension, or completion-handler migrations. |
| `references/continuations-and-bridging.md` | Wrapping completion handlers, delegates, Objective-C APIs, Combine, GCD, callbacks, cancellation, and one-shot vs multi-shot async bridges. |
| `references/async-sequences-observation-and-notifications.md` | AsyncStream, AsyncThrowingStream, AsyncSequence consumers, NotificationCenter, observation, buffering, termination, and event pipelines. |
| `references/async-testing.md` | Writing deterministic async tests, Swift Testing/XCTest patterns, confirmations, timeouts, clocks, non-occurrence assertions, cancellation tests, or flaky test fixes. |
| `references/problematic-patterns.md` | Auditing common anti-patterns: split isolation, stateless actors, detached tasks, hidden unstructured tasks, blocking async work, overbroad MainActor, and unsafe escape hatches. |
| `references/review-playbooks.md` | Performing a systematic concurrency review, migration pass, availability pass, or PR review. |
| `references/terminology.md` | Looking up keywords, attributes, runtime concepts, build settings, proposal-era terms, and short definitions. |
| `references/sources.md` | Verifying guidance against primary sources and specifications, checking Swift Evolution proposal references, or refreshing the skill during maintenance. |

## Design defaults

- UI state, SwiftUI view models, UIKit controllers, coordinators, and presentation state should be `@MainActor` unless proven otherwise.
- Domain models, DTOs, persistence records, request/response values, and pure algorithms should usually be nonisolated `Sendable` value types.
- Reusable packages should not assume `@MainActor` default isolation unless the package is explicitly UI-only.
- Custom actors are for shared mutable state whose operations can be asynchronous and whose invariants benefit from actor serialization. They are not a background-thread annotation.
- Synchronous shared mutable state on iOS 16 is usually a lock problem, not an actor problem. Prefer `OSAllocatedUnfairLock` for Apple-only iOS 16+ code when a synchronous lock is genuinely needed; use `Synchronization.Mutex` only when the deployment target supports it or when gated.
- Use `@concurrent` only when a nonisolated async function must switch away from the caller’s actor to perform parallel or CPU-heavy work. Awaiting network I/O does not itself block the main actor.
- Use `Task.immediate` (iOS 26+/macOS 26+) only when immediate ordering before the first suspension is semantically required. It can overhang the caller executor.
- Use `Task.detached` only when losing actor inheritance, task-local values, and structured cancellation is intentional and all captured values are safe to send.
- Prefer `async let` and task groups for child work. Prefer returning task handles from unavoidable fire-and-forget APIs so tests and owners can observe completion.
- Add `Sendable`, `@Sendable`, `sending`, protocol isolation, and isolated conformances because they describe the real API contract, not because the compiler asked for a token.

## Output expectations

When changing code, include the smallest correct patch and a brief explanation of the isolation/lifetime decision. When diagnosing code, state the root cause, not just the compiler error. When availability matters, say whether the code compiles with the latest SDK, runs on iOS 16, or requires an availability-gated fallback.

## Validation checklist

- Does each mutable state owner have exactly one clear isolation strategy: value ownership, `@MainActor`, custom actor, lock, or immutable snapshot?
- Are all UI mutations statically main-actor isolated?
- Are all tasks either structured or explicitly owned and cancelled?
- Does every custom actor protect real shared mutable state and handle reentrancy across `await`?
- Are `Sendable` and `@Sendable` requirements semantic and auditably safe?
- Are non-Sendable values prevented from concurrent shared use or transferred with `sending`/region isolation intentionally?
- Are protocol requirements explicit about isolation, synchronicity, and transferability?
- Are async bridges cancellation-safe and exactly-once for continuations?
- Are async tests event-driven rather than sleep/yield driven?
- Are APIs newer than the deployment target gated or given compatible fallbacks?

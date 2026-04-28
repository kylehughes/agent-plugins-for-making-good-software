---
name: using-swift-concurrency
description: Writes, reviews, refactors, and debugs modern Swift Concurrency code for portable Swift and iOS projects. Use when working with async/await, actors, MainActor, Sendable, isolation, protocol design, protocol conformance isolation errors, Task or Task.detached, structured concurrency, logical races, actor reentrancy, continuation wrappers, Swift 6 concurrency diagnostics, or async Swift tests.
---

# Using Swift Concurrency

Use this skill to reason about Swift Concurrency as a design problem first and a compiler-diagnostic problem second. It is intentionally portable: do not assume local helper APIs, package names, build commands, or testing infrastructure. Prefer the narrowest reference that matches the task, then load more only when the code crosses topics.

## First Pass

1. Classify the work using the reference map below.
2. Read only the matching reference file before changing code.
3. When the code involves UI state, assume `@MainActor` is the default candidate unless a reference explicitly proves a custom actor is warranted.
4. Treat every `await` as a possible suspension point where previous state assumptions may become stale.
5. Prefer structured concurrency and explicit happens-before edges over sleeps, yield budgets, detached tasks, or runtime isolation assertions.

## Reference Map

| Read | When |
|---|---|
| `references/actor-decisions.md` | Choosing between `actor`, `class`, `struct`, `@MainActor`, locks, or synchronization; questioning a new custom actor. |
| `references/protocol-design.md` | Designing new protocols that interact with Swift Concurrency, default actor isolation, `Sendable`, synchronous versus asynchronous requirements, or protocols refined from other modules. |
| `references/isolation-and-protocol-conformances.md` | Resolving `Equatable`, `Hashable`, `Codable`, `Identifiable`, or other protocol conformance errors involving global actors or isolated declarations. |
| `references/logical-races-and-reentrancy.md` | Reviewing async state machines, actor methods with suspension points, button taps, notification handlers, completion-handler migrations, or unexpected out-of-order state. |
| `references/problematic-patterns.md` | Auditing or refactoring common anti-patterns: split isolation, `Task.detached`, stateless actors, `MainActor.run`, blocking async work, unstructured tasks, async wrappers over legacy APIs. |
| `references/async-testing.md` | Writing or fixing portable async tests, timing tests, observer lifecycle tests, cancellation tests, non-occurrence assertions, or flaky tests involving `Task.yield()`/`Task.sleep()`. |
| `references/terminology.md` | Looking up Swift Concurrency vocabulary, keywords, annotations, protocols, compiler settings, and proposal-era concepts. |

## Decision Defaults

- Use value types when callers should own independent state.
- Use a class when shared state needs synchronous access or explicit synchronization is enough.
- Use `@MainActor` classes for UI-connected state and view models.
- Use a custom actor only for non-Sendable mutable state requiring atomic mutation that cannot live on `MainActor`.
- Make protocol isolation and `Sendable` constraints explicit only when they are part of the protocol's true semantic contract.
- Keep types nonisolated and non-Sendable when safety can come from usage context instead of type-wide isolation.
- Use `Task` for a top-level async context and structured primitives (`async let`, `TaskGroup`) for child work.
- Use `Task.detached` only when losing priority, task-local values, cancellation context, and actor inheritance is intentional.

## Validation Checklist

- Does every custom actor protect real mutable non-Sendable state?
- Does each protocol requirement state the weakest correct isolation, synchronicity, and `Sendable` contract?
- Are state checks and state mutations that must be atomic completed before the first `await`?
- Are protocol conformances isolated, nonisolated, or `@preconcurrency` for a deliberate reason?
- Is there any synchronous blocking on async work?
- Do async tests wait on observable events instead of sleeps, yields, or time passing?

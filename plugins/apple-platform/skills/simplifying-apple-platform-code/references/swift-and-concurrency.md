# Swift and Concurrency

Simplify Swift language usage and Swift concurrency code while preserving semantics, isolation, and cancellation behavior.

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

# Concurrency

## Contents

- Establish the isolation model
- `Sendable` and transfer boundaries
- Structured and unstructured tasks
- Cancellation and lifetime
- Actors and reentrancy
- `MainActor` and UI code
- Async sequences and streams
- Continuations and callback bridges
- Synchronous synchronization
- Diagnostic repair patterns
- Escape-hatch audit

## Establish the Isolation Model

Before changing annotations, answer:

1. Which executor or actor owns the mutable state?
2. Which operations must be serialized?
3. Which values cross that boundary?
4. Which caller should own task lifetime and cancellation?
5. Is the module nonisolated by default or default-isolated to `MainActor`?

Use isolation to express the architecture. Do not add `@MainActor`, `nonisolated`, or `Sendable` merely until diagnostics
disappear.

Default `MainActor` isolation is often suitable for app-facing modules dominated by UI state. It is usually a poor default
for reusable model, networking, parsing, database, or server libraries. A declaration's inferred isolation is part of its
call contract and can affect protocol conformances and generated interfaces.

## `Sendable` and Transfer Boundaries

A value crossing actors or tasks must be safe to transfer.

Prefer:

- Immutable value types whose stored properties are `Sendable`.
- Actors that encapsulate non-sendable mutable state.
- Final classes with genuinely immutable, sendable state when reference identity is required.
- Explicit snapshots or identifiers instead of transferring framework objects with thread affinity.
- `@Sendable` closures whose captures are immutable or safely isolated.

Audit implicit captures carefully. Capturing one property can be safer than capturing `self`, but only when it preserves
lifetime and semantics.

`@unchecked Sendable` is a promise to the compiler, not synchronization. Use it only after documenting and testing the
invariant that makes every accessible mutation safe. Typical evidence includes immutable-after-initialization state,
internal locking around all access, or confinement guaranteed by a lower-level subsystem. A mutable reference type is not
safe merely because current call sites happen to use one queue.

When ownership-transfer features such as `sending` are available, use them to communicate one-way transfer only when that
matches the API. Do not use ownership syntax as a substitute for understanding aliasing.

## Structured and Unstructured Tasks

Prefer structured concurrency:

```swift
async let profile = loadProfile()
async let settings = loadSettings()
return try await Dashboard(profile: profile, settings: settings)
```

Use task groups for dynamic child work. Bound concurrency when input size is unbounded; a task per element can exhaust
memory, sockets, or service quotas.

An unstructured `Task` inherits useful context, but its lifetime is not automatically tied to the lexical scope. Use it at
synchronous entry points such as UI actions, delegate methods, and observation callbacks. Store its handle when cancellation
or deduplication matters:

```swift
@MainActor
final class SearchModel {
    private var searchTask: Task<Void, Never>?

    func search(for query: String) {
        searchTask?.cancel()
        searchTask = Task { [weak self] in
            guard let self else { return }
            await performSearch(for: query)
        }
    }

    deinit {
        searchTask?.cancel()
    }
}
```

Review capture and lifetime semantics rather than applying `[weak self]` mechanically. A task intentionally performing a
finite operation may need to retain its owner; an indefinitely running task often must not.

`Task.detached` does not inherit actor isolation, task-local values, or the same structured lifetime relationship. Use it
only when that separation is the requirement. Prefer `@concurrent` or a dedicated actor/API when expressing executor
behavior at a function boundary is clearer.

## Cancellation and Lifetime

Cancellation is cooperative. Define who cancels and when.

- Call `Task.checkCancellation()` where cancellation should throw.
- Read `Task.isCancelled` where graceful early return is appropriate.
- Check cancellation in long loops and before expensive follow-up work.
- Cancel child resources, streams, callbacks, and underlying I/O when bridging APIs.
- Do not convert `CancellationError` into a domain failure unless the API deliberately does so.
- Do not catch every error and continue after cancellation.

A timeout should race work against a clock using structured tasks and cancel the loser. Use injected clocks where supported
so tests do not wait on wall time.

## Actors and Reentrancy

Actors serialize isolated access, but an actor method can be reentered whenever it suspends. State read before `await` may
no longer be valid afterward:

```swift
actor TokenStore {
    private var generation = 0
    private var token: Token?

    func refresh(using client: Client) async throws -> Token {
        generation += 1
        let requestedGeneration = generation
        let refreshed = try await client.fetchToken()

        guard requestedGeneration == generation else {
            throw RefreshError.superseded
        }

        token = refreshed
        return refreshed
    }
}
```

Common strategies:

- Mutate state before suspension and revalidate afterward.
- Snapshot immutable inputs before `await`.
- Split a method into isolated state transitions and nonisolated computation.
- Deduplicate in-flight work by storing a task, while defining cancellation and failure cleanup.
- Avoid exposing actor internals through mutable reference values.

Do not assume two consecutive actor calls are atomic as a pair. Provide one actor method for compound invariants.

## `MainActor` and UI Code

Use `@MainActor` for UI-observable state and APIs with main-thread contracts. Prefer isolation annotations over scattered
`DispatchQueue.main.async` calls because the compiler can then verify call sites.

Do not assume every type imported from an Apple UI framework is correctly or completely annotated for every supported SDK.
When bridging a legacy delegate or callback:

- Capture only values that are safe to transfer.
- Enter the actor explicitly with `await MainActor.run` or an actor-isolated async method.
- Preserve ordering and cancellation semantics.
- Use `@preconcurrency import` only as a scoped migration measure after reviewing the imported API.

A default-`MainActor` target can make synchronous code straightforward, but it can also accidentally isolate CPU-heavy or
library-facing work. Mark intentionally concurrent operations accordingly and measure UI responsiveness.

## Async Sequences and Streams

For `AsyncSequence` and `AsyncStream`:

- Choose buffering behavior explicitly for potentially bursty producers.
- Finish streams on every terminal path, including errors where applicable.
- Use termination handlers to unregister callbacks and release resources.
- Avoid retaining the continuation and owner in a cycle.
- Define whether multiple consumers are supported.
- Propagate cancellation from the consumer to the producer.
- Do not treat an unbounded stream buffer as harmless.

Prefer adapting an existing async sequence over wrapping it in another task and stream without a semantic reason.

## Continuations and Callback Bridges

Use checked continuations while developing bridges:

```swift
func value() async throws -> Value {
    try await withCheckedThrowingContinuation { continuation in
        legacyAPI.load { result in
            continuation.resume(with: result)
        }
    }
}
```

The continuation must be resumed exactly once on every terminal path. Also review:

- Whether the callback can run synchronously before registration returns.
- Whether cancellation needs to stop the legacy operation. Use `withTaskCancellationHandler` when cancellation must be
  coordinated with registration, and account for cancellation racing with callback setup.
- Whether callback values are safe to cross the caller's isolation boundary.
- Whether the legacy API can emit multiple values, in which case an async sequence may be the correct model.
- Whether the callback has an executor or queue guarantee that must be preserved.

Do not suppress checked-continuation diagnostics by moving immediately to an unsafe continuation.

## Synchronous Synchronization

Use actors by default for state accessed from asynchronous workflows. Use `Synchronization.Mutex` when all protected work
is synchronous, the critical section is small, and supported deployment targets provide the API. Use atomics only for a
well-understood lock-free invariant or measured contention need.

Rules for locks:

- Never `await` while holding a lock.
- Keep user callbacks and arbitrary code outside the critical section.
- Do not recursively acquire a non-recursive lock.
- Protect every path to the state, including debugging and description code.
- Define lock ordering if more than one lock can be acquired.
- Do not expose mutable protected storage after unlocking.

For older deployment targets, follow the repository's established synchronization primitive and test under Thread
Sanitizer where practical.

## Diagnostic Repair Patterns

### “Main actor-isolated ... cannot be used to satisfy nonisolated requirement”

First determine the protocol's intended isolation. Possible fixes include making the protocol requirement actor-isolated,
using an isolated conformance where supported, moving non-UI behavior into a nonisolated value, or adding a synchronization
boundary. Do not mark the implementation `nonisolated` if it reads actor state.

### “Capture of non-Sendable type in a `@Sendable` closure”

Inspect the capture. Prefer a sendable snapshot, actor-owned operation, immutable value, or correctly isolated closure.
Do not add `@unchecked Sendable` to a broad owner just to satisfy one callback.

### “Task or actor-isolated value cannot be sent”

Look for aliasing across the boundary. Narrow the transferred value, consume it once when ownership semantics permit, or
perform the operation inside the owning actor.

### “Sending value risks causing data races”

Identify every alias that can access the value after transfer. A local `let` does not make the referenced object immutable.
Redesign ownership or isolate the reference.

### Legacy SDK callback warnings

Verify the framework's actual callback contract and SDK annotations. Prefer a narrow adapter module. Use `@preconcurrency`
only at the import or conformance boundary that needs it, with a tracking issue for removal.

## Escape-Hatch Audit

Before accepting `@unchecked Sendable`, `nonisolated(unsafe)`, `@preconcurrency`, an unsafe continuation, or manual executor
assumptions, record:

1. The exact compiler limitation or legacy contract being bridged.
2. The invariant that makes the code safe.
3. Every mutation path and synchronization mechanism.
4. Lifetime, cancellation, and deinitialization behavior.
5. A focused test or stress test where feasible.
6. The scope: keep the annotation on the narrowest declaration.
7. A removal condition when the escape hatch is temporary.

Primary references:

- https://docs.swift.org/swift-book/documentation/the-swift-programming-language/concurrency/
- https://www.swift.org/migration/documentation/swift-6-concurrency-migration-guide/
- https://github.com/swiftlang/swift-evolution/blob/main/proposals/0466-control-default-actor-isolation.md
- https://github.com/swiftlang/swift-evolution/blob/main/proposals/0433-mutex.md

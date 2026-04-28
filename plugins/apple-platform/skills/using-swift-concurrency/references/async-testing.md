# Async Testing

Use this reference when writing or reviewing tests for Swift Concurrency behavior in any Swift or iOS project. Keep tests event-driven: prove the specific happens-before edge the assertion depends on instead of hoping the scheduler has made progress.

## Contents

- [Core Principle](#core-principle)
- [Portable Synchronization Patterns](#portable-synchronization-patterns)
- [Timing Tests](#timing-tests)
- [AsyncSequence Tests](#asyncsequence-tests)
- [Cancellation Tests](#cancellation-tests)
- [Non-Occurrence Tests](#non-occurrence-tests)
- [Actor and Reentrancy Tests](#actor-and-reentrancy-tests)
- [Anti-Patterns](#anti-patterns)
- [Checklist](#checklist)

## Core Principle

Async tests should wait for observable events, not scheduler turns.

`Task.yield()`, `Task.sleep`, and wall-clock delays prove only that time passed or the scheduler had an opportunity to run. They do not prove that a task started, an observer subscribed, an `AsyncSequence` emitted, a cancellation handler ran, or an actor reached a stable state.

Prefer a test-controlled signal:

- Await a value from the system's `AsyncSequence`.
- Resume a continuation when the code under test reaches a milestone.
- Await a task's result.
- Poll a state predicate with a short real-time timeout only when the system has no event surface.
- Inject a clock when testing time-based behavior.

## Portable Synchronization Patterns

Use the strongest synchronization surface available:

| Need | Pattern |
|---|---|
| Know a task reached a point | `withCheckedContinuation` or `AsyncStream` milestone emitted by test instrumentation |
| Collect ordered values | Consume the `AsyncSequence` into a recorder task, then await counts or predicates |
| Test debouncing, throttling, retry, timeout | Inject a `Clock` or scheduler abstraction; advance virtual time when available |
| Test cancellation | Cancel the task, then await the task result or a cancellation milestone |
| Test non-occurrence | First prove subscription or task startup, then wait a short bounded interval for an unwanted event |
| Test actor reentrancy | Arrange concurrent callers, then assert the invariant after all tasks complete |

Keep timeouts as safety bounds. They should fail stuck tests, not be the mechanism that makes passing tests pass.

## Timing Tests

Prefer APIs that accept `Clock` or another scheduler abstraction:

```swift
func retry<C: Clock>(
    clock: C,
    operation: @escaping () async throws -> Void
) async throws where C.Duration == Duration {
    // production code sleeps through `clock`
}
```

In tests, pass a controllable clock if the project has one. If not, keep real-time sleeps short, isolated, and justified. Do not stack arbitrary sleeps to "settle" the system.

For time-based `AsyncSequence` operators, test through the sequence boundary when possible: feed deterministic input, advance time, and await emitted output. Avoid relying on hidden implementation tasks having observed input after a fixed number of yields.

## AsyncSequence Tests

When testing an `AsyncSequence`, record values from one consumer task and coordinate shutdown explicitly:

```swift
let stream = AsyncStream<Int> { continuation in
    continuation.yield(1)
    continuation.yield(2)
    continuation.finish()
}

let values = await stream.reduce(into: []) { result, value in
    result.append(value)
}

#expect(values == [1, 2])
```

For long-lived streams, build a small test recorder that:

- Starts consuming before the action under test.
- Stores events in order.
- Exposes async waits for a count or predicate.
- Cancels consumption during teardown.
- Awaits cancellation before treating the final transcript as stable.

The final point matters: after cancellation is requested, a recorder task may still process an already-enqueued value. Await recorder termination before asserting that no more values can appear.

## Cancellation Tests

Cancellation is cooperative. A passing cancellation test usually proves three things:

1. The task was actually cancelled.
2. The operation reached a cancellation-aware suspension point or checked `Task.isCancelled`.
3. The system performed the expected cleanup or stopped emitting values.

Prefer this shape:

```swift
let task = Task {
    await operation()
}

task.cancel()
await task.value

#expect(await system.isStopped)
```

If the operation should throw `CancellationError`, assert that exact result. If it intentionally swallows cancellation, assert the documented terminal state.

## Non-Occurrence Tests

Non-occurrence assertions are valid only after setup is proven.

Bad shape:

```swift
startObserving()
try await Task.sleep(for: .milliseconds(100))
#expect(events.isEmpty)
```

Better shape:

```swift
startObserving()
await recorder.waitUntilSubscribed()

performActionThatMustNotEmit()

let unexpected = await recorder.nextEvent(timeout: .milliseconds(100))
#expect(unexpected == nil)
```

The short timeout is a bounded observation window, not a progress driver. Keep it as small as the environment permits.

## Actor and Reentrancy Tests

Actors prevent data races, not logical races. Tests for actor-based state should include concurrent callers when invariants depend on interleaving:

```swift
await withTaskGroup(of: Void.self) { group in
    for _ in 0 ..< 10 {
        group.addTask {
            await store.loadIfNeeded()
        }
    }
}

let loadCount = await store.loadCount
#expect(loadCount == 1)
```

When a method reads state, awaits, then writes state, add tests where multiple calls overlap. The goal is to expose stale assumptions made before suspension points.

## Anti-Patterns

| Pattern | Problem | Prefer |
|---|---|---|
| Fixed `Task.yield()` loops | They guess at scheduler progress. | Await an explicit milestone or emitted value. |
| `Task.sleep` to settle work | Slow and still racy under load. | Event-driven waits with real-time timeout safety. |
| No timeout around waits | Stuck tests hang indefinitely. | Short, explicit timeouts around awaited test signals. |
| Timeout expiry as success | Passing depends on waiting long enough. | Prove setup, then use a bounded non-occurrence window. |
| Ignoring recorder shutdown | Late values can mutate the transcript after assertion. | Cancel and await recorder termination. |
| Assuming actor isolation prevents ordering bugs | Actors are reentrant at suspension points. | Test overlapping calls and post-`await` invariants. |

## Checklist

- Does the test prove the observer or task started before driving the behavior?
- Does each assertion wait on the exact event or state transition it needs?
- Are sleeps and yield loops absent except for tightly justified compatibility cases?
- Is every indefinite wait protected by a real-time timeout?
- Does teardown cancel long-lived tasks and await their termination?
- Do actor tests cover overlapping calls when state crosses an `await`?

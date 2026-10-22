# Primitive Contracts

The API contract each primitive must satisfy, with minimal reference implementations for the ones worth writing yourself. Use your project's existing primitives when they satisfy the contract; adopt the named ecosystem package when one exists; write from the sketch only when neither holds. Keep test primitives in a dedicated test-support module so production code cannot import them.

## Virtual Clock

Contract:

- Conforms to Swift's `Clock` protocol so production code can accept `some Clock` and never know it is under test.
- Time progresses only when the test calls `advance(by:)`; sleeps scheduled at or before the new deadline resume.
- Exposes enough state to prove a sleep was *armed* before advancing — a scheduled-sleep count with a bounded wait — so a test can distinguish "the operator scheduled its delay, then I advanced" from "I advanced before the operator got there." Use that wait only to sequence arm-then-advance, never as proof the operator observed a value.

[swift-clocks](https://github.com/pointfreeco/swift-clocks) `TestClock` satisfies the core contract, and its `advance(by:)` is `async` and awaits its sleepers, which subsumes the armed-sleep wait for most tests. A hand-rolled manual clock needs: a lock-protected schedule of `(deadline, continuation)` pairs, `sleep(until:tolerance:)` registering into it, `advance(by:)` snapshotting due entries atomically before resuming them, and an `Instant: InstantProtocol` measured as a `Duration` offset from zero.

## Event Recorder

Contract:

- `consuming(_ source: some AsyncSequence)` — spawn one collection task that appends every element, in order, to a transcript.
- `recording()` — no collection task; callback-shaped APIs call `await record(_:)` directly, avoiding a scheduler hop.
- `waitFor(_ predicate:since:timeout:)` — resume when a matching event lands at or after a transcript baseline index; throw on timeout.
- `waitForEventCount(_:timeout:)` — resume when the transcript reaches a count.
- `detach()` — cancel the collection task **and await its termination**. That task cannot append after `detach()` returns. Direct `record(_:)` callbacks require a separate producer stop barrier.
- `expectNoEvents(for:since:)` — observe the transcript from a baseline over a bounded window. Keep collection active to assess source non-occurrence; after detach, a stable transcript proves only recorder detachment.
- Every wait spends its deadline through the timeout budget below, not a single wall-clock sleep.

Reference sketch (actor; waits shown for one method, the rest follow the same shape):

```swift
actor EventRecorder<Event: Sendable> {
    private var transcript: [Event] = []
    private var collection: Task<Void, Never>?
    private var revision = 0

    static func consuming<S: AsyncSequence & Sendable>(
        _ source: S
    ) async -> EventRecorder<Event> where S.Element == Event {
        let recorder = EventRecorder<Event>()
        await recorder.beginCollecting(from: source)
        return recorder
    }

    var events: [Event] { transcript }

    func record(_ event: Event) {
        transcript.append(event)
        revision += 1
    }

    func detach() async {
        collection?.cancel()
        await collection?.value   // the barrier: awaits termination
        collection = nil
    }

    func waitFor(
        _ predicate: @Sendable (Event) -> Bool,
        since baseline: Int = 0,
        timeout: Duration = .seconds(2)
    ) async throws -> Event {
        let budget = TimeoutBudget(timeout: timeout)
        while true {
            if let match = transcript[min(baseline, transcript.count)...].first(where: predicate) {
                return match
            }
            guard await budget.spendSlice() else { throw RecorderFailure.waitTimedOut }
        }
    }

    private func beginCollecting<S: AsyncSequence & Sendable>(
        from source: S
    ) where S.Element == Event {
        collection = Task {
            do {
                for try await event in source { self.record(event) }
            } catch { /* record or surface upstream errors per project need */ }
        }
    }
}
```

A production-grade version replaces the polling loop with registered continuation waiters woken on every `record` (each waiter under a unique token; whoever wakes first — event, timeout, or cancellation — atomically removes the token so the continuation never double-resumes). The polling sketch illustrates the shared budget; it does not establish scheduler fairness or CI reliability. Check cancellation and upstream-error behavior before adopting it, and use registered waiters when wait latency matters.

## Timeout Budget

Contract: spend a nominal duration in short sleep slices and report exhaustion through `spendSlice()`. Delayed resumptions can extend elapsed wall-clock time. This heuristic does not guarantee fairness or completion before timeout, and it is not a strict wall-clock deadline.

```swift
final class TimeoutBudget: @unchecked Sendable {
    private let slice: Duration = .milliseconds(10)
    private var remaining: Duration
    private let lock = NSLock()

    init(timeout: Duration) { remaining = timeout }

    /// Sleeps one slice and debits it. Returns false once the budget is spent.
    func spendSlice() async -> Bool {
        let spent = lock.withLock {
            let spent = remaining <= .zero
            if !spent { remaining -= slice }
            return spent
        }
        guard !spent else { return false }
        try? await Task.sleep(for: slice)
        return true
    }
}
```

Choose the slice and budget from project evidence. Multiple suspensions expose the budget to scheduler delays, but they do not establish a fixed relationship to the system under test's scheduling.

## Awaited Cleanup

Contract: run an operation, then run async cleanup whether the operation returned or threw. The helper below supports compilers without async `defer` and centralizes cleanup. Compilers with [async `defer` support](../../modeling-swift-types-for-correctness/references/swift-feature-status.md#release-18) can await cleanup at scope exit. Neither form shields cleanup from cancellation automatically.

```swift
func withAsyncCleanup<T>(
    operation: () async throws -> T,
    cleanup: () async -> Void
) async throws -> T {
    do {
        let value = try await operation()
        await cleanup()
        return value
    } catch {
        await cleanup()
        throw error
    }
}
```

Add a `@MainActor` overload if suites are main-actor-isolated. Typical cleanup order in a test: open any gates the operation is blocked on, await outstanding tasks, stop the harness, `await recorder.detach()`.

## Serial Main Executor

Contract: redirect global task jobs to the main serial executor while the hook is installed. This improves scheduling predictability; it does not make `Task.yield()` proof that a particular task has run. The runtime hook also has no scoping guarantee if another caller changes it.

Do not write this one — the runtime hook is provided by [swift-concurrency-extras](https://github.com/pointfreeco/swift-concurrency-extras) (`withMainSerialExecutor`). What a project should add around it is a **scope guard**: the hook is process-global and parallel suites clobber each other, so expose it through a shared serializing wrapper or trait that leases the hook to one scope at a time, and keep scopes short. Serializing one suite alone does not exclude unrelated suites.

## Bounded Polling

For state that has no event surface at all (`waitUntil(_:)` / `waitForValue(_:)` helpers): poll a predicate through the timeout budget, sleeping one slice between checks. Polling is the last resort — prefer an event surface — but budgeted polling is sound where an unbudgeted spin or one-shot sleep is not.

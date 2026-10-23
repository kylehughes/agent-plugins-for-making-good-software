# Async Testing

Use this reference when writing or fixing tests for Swift Concurrency behavior. Prefer Swift Testing where the project uses it, but keep patterns portable to XCTest when needed.

## Core rule

Async tests should wait for observable events, not scheduler turns.

`Task.yield()` and `Task.sleep` do not prove a task started, a stream subscribed, a callback fired, cancellation propagated, or an actor reached a stable state. They prove only that the scheduler had an opportunity or time passed.

## Event-driven waits

Prefer one of these:

- Await the task’s `value`.
- Await a value from an `AsyncSequence`.
- Resume a continuation from test instrumentation.
- Use Swift Testing `confirmation` for events that happen before the confirmation closure returns.
- Poll a predicate with a short timeout only when there is no event surface.
- Inject a clock/scheduler for time-based behavior.

## Returning task handles for testability

If production code starts unstructured work, return the task handle when possible.

Production:

```swift
@discardableResult
func refresh() -> Task<Void, Never> {
    Task { await runRefresh() }
}
```

Test:

```swift
@Test
func refreshLoadsItems() async {
    let task = await model.refresh()
    await task.value
    #expect(await model.items.count == 3)
}
```

This is better than sleeping after `refresh()`.

## Swift Testing confirmations

Use `confirmation` to confirm events that occur during the operation passed to the confirmation closure. Do not treat it as an XCTest expectation that waits independently after the closure returns.

Good:

```swift
@Test
func notifiesDelegate() async {
    await confirmation("delegate called") { confirmed in
        delegate.onEvent = { confirmed() }
        await subject.performOperationThatCallsDelegateBeforeReturning()
    }
}
```

Bad:

```swift
await confirmation("called") { confirmed in
    subject.startFireAndForgetWork { confirmed() }
    // Closure returns before the task necessarily runs.
}
```

If the subject starts unstructured work, make it return the task and await it inside the confirmation closure.

## XCTest expectations

For existing XCTest suites, expectations remain useful for callback APIs, but still prefer direct async tests when the API is async.

```swift
func testCallback() async throws {
    let expectation = expectation(description: "callback")
    subject.start { value in
        XCTAssertEqual(value, expected)
        expectation.fulfill()
    }
    await fulfillment(of: [expectation], timeout: 1.0)
}
```

Keep timeouts as safety bounds, not as progress mechanisms.

## AsyncSequence recorder

For long-lived streams, build a recorder with explicit startup and shutdown.

```swift
actor Recorder<Element> {
    private var values: [Element] = []
    private var waiters: [(Int, CheckedContinuation<Void, Never>)] = []

    func append(_ value: Element) {
        values.append(value)
        let ready = waiters.filter { values.count >= $0.0 }
        waiters.removeAll { values.count >= $0.0 }
        for (_, continuation) in ready { continuation.resume() }
    }

    func waitForCount(_ count: Int) async {
        if values.count >= count { return }
        await withCheckedContinuation { continuation in
            waiters.append((count, continuation))
        }
    }

    func snapshot() -> [Element] { values }
}
```

Consumer task:

```swift
let recorder = Recorder<Int>()
let task = Task {
    for await value in stream {
        await recorder.append(value)
    }
}

await recorder.waitForCount(2)
#expect(await recorder.snapshot() == [1, 2])
task.cancel()
await task.value
```

In real tests, add timeouts around waits to prevent hangs.

## Timeouts

A timeout should fail stuck tests. It should not make passing tests pass.

Useful helper shape:

```swift
func withTimeout<T: Sendable>(
    _ duration: Duration,
    operation: @escaping @Sendable () async throws -> T
) async throws -> T {
    try await withThrowingTaskGroup(of: T.self) { group in
        group.addTask { try await operation() }
        group.addTask {
            try await Task.sleep(for: duration)
            throw TimeoutError()
        }

        let result = try await group.next()!
        group.cancelAll()
        return result
    }
}
```

This task-group race is a cooperative timeout: the group still waits for every child to terminate after cancellation. It cannot impose a hard deadline on an operation that ignores cancellation or is stuck on a continuation. Ensure the operation has cancellation-aware waits and cleanup; do not report this helper as a hard bound.

If `Task.sleep(for:)` availability is a concern in an older target, use the project’s existing timeout helper or nanosecond sleep wrapper. Do not duplicate unsafe helpers everywhere.

## Clocks and time-based code

Production code with delays should accept a `Clock` or scheduler abstraction when feasible.

```swift
func retry<C: Clock>(
    clock: C,
    operation: @Sendable () async throws -> Void
) async throws where C.Duration == Duration {
    for attempt in 0..<3 {
        do { return try await operation() }
        catch {
            if attempt == 2 { throw error }
            try await clock.sleep(for: .seconds(1))
        }
    }
}
```

Tests can pass a controllable clock if the project has one. If not, keep real-time sleeps short and isolated to timeout/safety behavior.

## Cancellation tests

A cancellation test should prove:

1. The task was cancelled.
2. The operation observed cancellation.
3. Cleanup occurred.

```swift
@Test
func cancellationStopsObservation() async {
    let task = Task { await subject.observe() }
    await subject.waitUntilSubscribed()

    task.cancel()
    await task.value

    #expect(await subject.isObserving == false)
}
```

If the operation throws, assert its documented cancellation result, such as `CancellationError` or a framework-specific cancellation error. Cancellation is cooperative; do not assume every API uses the same error type. See [Task cancellation](https://developer.apple.com/documentation/swift/task/cancel()).

## Non-occurrence tests

Non-occurrence assertions are valid only after setup is proven.

Bad:

```swift
subject.start()
try await Task.sleep(for: .milliseconds(100))
#expect(events.isEmpty)
```

Better:

```swift
subject.start()
await subject.waitUntilSubscribed()

subject.performActionThatMustNotEmit()
let event = await recorder.next(timeout: .milliseconds(100))
#expect(event == nil)
```

The timeout is the observation window, not a scheduler-progress hack.

## Actor reentrancy tests

If actor correctness depends on overlapping calls, test overlapping calls.

```swift
@Test
func loadIfNeededRunsOnce() async throws {
    let store = Store()

    await withTaskGroup(of: Void.self) { group in
        for _ in 0..<20 {
            group.addTask { await store.loadIfNeeded() }
        }
    }

    #expect(await store.loadCount == 1)
}
```

A single sequential call does not test actor reentrancy.

## MainActor tests

Use `@MainActor` on tests that inspect or mutate UI-isolated state.

```swift
@MainActor
@Test
func showsLoadedState() async {
    let model = Model(service: .mock)
    await model.load()
    #expect(model.state == .loaded)
}
```

Do not isolate every test helper to MainActor if helpers are DTOs, recorders, or background services. Test targets with default MainActor isolation can accidentally make non-UI test utilities harder to use.

## Anti-patterns

| Pattern | Problem | Prefer |
|---|---|---|
| `Task.yield()` loops | Guess scheduler progress. | Await event/task/continuation. |
| Sleep to settle | Slow and racy. | Observable event with timeout safety. |
| Unawaited fire-and-forget in subject | Test cannot know completion. | Return task handle or expose milestone. |
| Confirmation closure returns before event | Swift Testing confirmation fails/flakes. | Await the work inside the closure. |
| Ignoring stream teardown | Late events mutate transcript after assertion. | Cancel consumer and await termination. |
| Sequential-only actor tests | Miss reentrancy bugs. | Overlapping callers. |

## Checklist

- Does the test wait for the exact event needed by the assertion?
- Are all indefinite waits protected by a timeout?
- Are sleeps/yields absent except for bounded non-occurrence windows or timeout helpers?
- Can unstructured production tasks be observed or awaited in tests?
- Does teardown cancel and await long-lived tasks?
- Are MainActor tests isolated explicitly and narrowly?
- Do actor tests exercise overlap when invariants cross suspension points?

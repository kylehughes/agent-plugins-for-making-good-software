# Continuations and Bridging

Use this reference when converting completion handlers, delegates, Objective-C APIs, GCD, Combine, or callback systems into Swift Concurrency.

## First choose bridge shape

| Legacy shape | Swift shape |
|---|---|
| One callback exactly once | `withCheckedContinuation` / `withCheckedThrowingContinuation`. |
| One callback maybe never/cancelable | Continuation plus cancellation handler and timeout/cancel path. |
| Multiple values over time | `AsyncStream` / `AsyncThrowingStream`. |
| Delegate with lifecycle | Adapter object plus stream or actor/MainActor callbacks. |
| Synchronous blocking API | Prefer an async replacement; otherwise use a bounded queue/executor designed for blocking and bridge completion. `@concurrent` alone does not make blocking safe. |
| Combine publisher | Use `AsyncSequence` boundary carefully; maintain cancellation and subscriptions. |

## Continuation rules

A checked continuation must be resumed exactly once.

- Never resume twice.
- Never drop without resuming unless the task is intentionally leaked/stuck, which is a bug.
- Protect continuation state if callbacks and cancellation can race.
- Do not call `await` inside the continuation setup closure.
- Convert result values to Sendable snapshots if they cross isolation domains.

Simple one-shot bridge:

```swift
func loadImage(id: Image.ID) async throws -> Image {
    try await withCheckedThrowingContinuation { continuation in
        legacyLoadImage(id: id) { result in
            continuation.resume(with: result)
        }
    }
}
```

## Cancellation-safe one-shot bridge

If the underlying operation can be cancelled, wire task cancellation to it. Because cancellation and callback can race, guard resume with a lock.

```swift
final class OneShotBox<Success: Sendable>: @unchecked Sendable {
    private struct State {
        var continuation: CheckedContinuation<Success, Error>?
        var result: Result<Success, Error>?
    }

    private let state = OSAllocatedUnfairLock(initialState: State())

    func install(_ continuation: CheckedContinuation<Success, Error>) {
        let result = state.withLock { state -> Result<Success, Error>? in
            if let result = state.result {
                return result
            }
            state.continuation = continuation
            return nil
        }

        if let result {
            continuation.resume(with: result)
        }
    }

    func resume(_ result: Result<Success, Error>) {
        let continuation = state.withLock { state -> CheckedContinuation<Success, Error>? in
            guard state.result == nil else { return nil }
            state.result = result
            let continuation = state.continuation
            state.continuation = nil
            return continuation
        }
        continuation?.resume(with: result)
    }
}

func value(from client: LegacyClient) async throws -> Value {
    let box = OneShotBox<Value>()
    let token = client.makeToken()

    return try await withTaskCancellationHandler {
        try await withCheckedThrowingContinuation { continuation in
            box.install(continuation)

            guard !Task.isCancelled else {
                client.cancel(token: token)
                box.resume(.failure(CancellationError()))
                return
            }

            client.start(token: token) { result in
                box.resume(result)
            }
        }
    } onCancel: {
        client.cancel(token: token)
        box.resume(.failure(CancellationError()))
    }
}
```

This is intentionally more verbose than the simple bridge. Use it only when cancellation and multi-callback races are real.

## Callback isolation

Legacy callbacks may arrive on arbitrary queues. Decide the callback isolation explicitly.

If the result updates UI:

```swift
func start() {
    legacy.start { [weak self] value in
        Task { @MainActor [weak self] in
            self?.apply(value)
        }
    }
}

@MainActor
private func apply(_ value: Value) { }
```

If the result belongs to an actor:

```swift
legacy.start { [store] value in
    Task {
        await store.insert(value)
    }
}
```

Do not assume a callback is MainActor because it “usually” arrives on the main queue. Either document the legacy contract or hop explicitly.

## Delegates to AsyncStream

Use streams for multi-event delegates.

```swift
final class LocationDelegate: NSObject, CLLocationManagerDelegate {
    let stream: AsyncStream<CLLocation>
    private let continuation: AsyncStream<CLLocation>.Continuation

    override init() {
        var continuation: AsyncStream<CLLocation>.Continuation!
        self.stream = AsyncStream(bufferingPolicy: .bufferingNewest(1)) { cont in
            continuation = cont
        }
        self.continuation = continuation
        super.init()
    }

    func locationManager(_ manager: CLLocationManager, didUpdateLocations locations: [CLLocation]) {
        for location in locations {
            continuation.yield(location)
        }
    }

    func finish() {
        continuation.finish()
    }
}
```

Real adapters usually also need `onTermination` to stop the manager and break retain cycles. See the async sequence reference for stream lifetime details.

## Objective-C async imports

Compiler-imported async variants of Objective-C completion APIs can be convenient, but inspect semantics:

- Which queue invokes the completion?
- Does cancellation propagate?
- Are values Sendable or isolated?
- Does the original API call the completion more than once?
- Does the generated async API preserve error conventions correctly?

If semantics are unclear, write an explicit wrapper and document the threading/cancellation contract.

## GCD and blocking APIs

Never block Swift concurrency’s cooperative executor waiting for async work.

Bad:

```swift
let semaphore = DispatchSemaphore(value: 0)
Task {
    await work()
    semaphore.signal()
}
semaphore.wait()
```

Better:

```swift
await work()
```

Prefer an asynchronous API. If blocking legacy work is unavoidable, run it on an explicitly owned queue or executor designed for blocking and bridge completion asynchronously, with bounded concurrency and cancellation semantics. `@concurrent` and `Task.detached` still use Swift’s cooperative executor by default; they do not make blocking waits safe. See [Swift concurrency: Behind the scenes](https://developer.apple.com/videos/play/wwdc2021/10254/).

## Combine bridging

When consuming publisher values from async code:

- Own the task consuming values.
- Cancel the task to cancel observation.
- Avoid assuming a value has been observed after a fixed number of yields.
- Ensure downstream UI updates are MainActor-isolated.
- Beware backpressure and buffering differences.

```swift
@MainActor
func observePublisher() {
    observationTask?.cancel()
    observationTask = Task { [weak self] in
        for await value in publisher.values {
            self?.value = value
        }
    }
}
```

## Bridging from sync APIs into async

If a synchronous legacy method needs to kick off async work, prefer returning a task handle:

```swift
@discardableResult
func startRefresh() -> Task<Void, Never> {
    Task { await refresh() }
}
```

Use `Task.immediate` only when preserving immediate ordering before first suspension is required and overhang is acceptable.

## `@preconcurrency import`

Use `@preconcurrency import` to contain legacy modules with missing annotations, not to bless unsafe code.

```swift
@preconcurrency import LegacyFramework

struct LegacyClientAdapter: Sendable {
    func fetch() async throws -> Snapshot {
        try await explicitWrapperAroundLegacyFetch()
    }
}
```

Keep the imported API behind a small adapter whose public surface has modern isolation and Sendable annotations.

## Review checklist

- Is the legacy operation one-shot, multi-shot, or long-lived?
- Can the callback fire zero, one, many, or duplicate times?
- Is cancellation wired to the underlying operation?
- Can cancellation race with callback completion?
- Is callback queue/isolation documented or explicitly hopped?
- Are non-Sendable legacy values converted to snapshots before crossing actors?
- Is `@preconcurrency` localized?
- Are tests able to await completion without sleeps?

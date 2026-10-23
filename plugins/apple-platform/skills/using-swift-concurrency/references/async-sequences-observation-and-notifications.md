# Async Sequences, Observation, and Notifications

Use this reference for `AsyncSequence`, `AsyncStream`, stream consumers, notifications, Observation, buffering, termination, and long-lived event pipelines.

## AsyncSequence principles

An `AsyncSequence` is a pull-based asynchronous stream of values. Consumers suspend waiting for values. Producers and consumers may have different lifetimes.

Always answer:

- Who owns the producer?
- Who owns the consumer task?
- How does cancellation stop both sides?
- What is the buffering policy?
- What actor processes each value?
- What happens when the owner deinitializes?

## Consuming streams

A long-lived consumer should be task-owned and cancellable.

```swift
@MainActor
final class FeedModel: ObservableObject {
    @Published private(set) var items: [Item] = []
    private var task: Task<Void, Never>?

    func start<S: AsyncSequence>(feed: S) where S.Element == Item {
        task?.cancel()
        task = Task { [weak self] in
            do {
                for try await item in feed {
                    self?.append(item)
                }
            } catch is CancellationError { }
            catch { self?.show(error) }
        }
    }

    func stop() {
        task?.cancel()
        task = nil
    }

    @MainActor
    private func append(_ item: Item) {
        items.append(item)
    }
}
```

Do not start a stream consumer without a cancellation path.

## Creating AsyncStream

Use `AsyncStream` for nonthrowing multi-event sources and `AsyncThrowingStream` for sources that can terminate with an error.

```swift
func values() -> AsyncStream<Value> {
    AsyncStream(bufferingPolicy: .bufferingNewest(1)) { continuation in
        let token = source.observe { value in
            continuation.yield(value)
        }

        continuation.onTermination = { @Sendable _ in
            source.removeObserver(token)
        }
    }
}
```

Rules:

- Choose a buffering policy deliberately.
- Use `onTermination` to stop callbacks and release resources.
- Finish the stream when the source ends.
- Do not yield live mutable non-Sendable values across isolation domains; yield snapshots.
- If callbacks can arrive concurrently, ensure the legacy source and continuation use are thread-safe or serialize through an actor/lock.

## Buffering policy

| Policy | Use |
|---|---|
| `.unbounded` | Rare. Only when value volume is naturally bounded or lossless history is required. |
| `.bufferingNewest(1)` | UI state, latest progress, location, sensors, reachability. |
| `.bufferingNewest(n)` | Recent event window where latest values matter. |
| `.bufferingOldest(n)` | Preserve first events and drop newer overflow. |

Unbounded streams can become memory leaks when producers outpace consumers.

## NotificationCenter

Notifications are multi-event streams. Own the consuming task and cancel it.

```swift
@MainActor
final class KeyboardModel: ObservableObject {
    @Published private(set) var height: CGFloat = 0
    private var task: Task<Void, Never>?

    func start() {
        task?.cancel()
        task = Task { [weak self] in
            let notifications = NotificationCenter.default.notifications(
                named: UIResponder.keyboardWillChangeFrameNotification
            )

            for await notification in notifications {
                guard !Task.isCancelled else { break }
                await self?.applyKeyboard(notification)
            }
        }
    }

    deinit {
        task?.cancel()
    }
}
```

If using newer typed notification APIs, gate availability for iOS 16-compatible projects.

## Observation framework

Observation’s `@Observable` and `withObservationTracking` require iOS 17+/macOS 14+. The async `Observations` sequence requires iOS 26+/macOS 26+; gate it separately or provide a fallback. See [Apple’s `Observations` declaration](https://developer.apple.com/documentation/observation/observations).

For iOS 16-compatible view models, `ObservableObject` remains the safe default.

When using Observation:

- Isolate UI observable models to `@MainActor` unless they are explicitly not UI-bound.
- Do not assume all observation tools are durable multi-shot streams; understand whether tracking re-arms after each change.
- For async observation sequences, own and cancel the consumer task.
- Avoid mixing Observation and Combine without a clear boundary.

## Producer lifetime

A stream must not retain its owner forever unless that is intentional.

Potential retain cycle:

```swift
final class Source {
    func stream() -> AsyncStream<Value> {
        AsyncStream { continuation in
            self.onValue = { value in
                continuation.yield(value)
            }
        }
    }
}
```

Better:

```swift
func stream() -> AsyncStream<Value> {
    AsyncStream { [weak self] continuation in
        guard let self else {
            continuation.finish()
            return
        }

        let token = self.addObserver { value in
            continuation.yield(value)
        }

        continuation.onTermination = { @Sendable [weak self] _ in
            self?.removeObserver(token)
        }
    }
}
```

## AsyncSequence transformations

When mapping/filtering/merging streams:

- Keep transformations pure and Sendable when crossing tasks.
- Move UI mutations to MainActor.
- Propagate cancellation.
- Avoid hidden unstructured tasks inside operators unless the operator owns and cancels them.
- Prefer deterministic buffering and backpressure behavior.

## Termination and errors

For `AsyncThrowingStream`, finish with an error when the underlying source fails:

```swift
continuation.finish(throwing: error)
```

For cancellation, usually finish without error or let the consumer task observe `CancellationError` from its surrounding operation. Document which behavior callers should expect.

## Testing streams

Tests should prove:

- Subscription is active before driving events.
- Values are received in expected order.
- Cancellation terminates the consumer and unregisters legacy observers.
- Buffering policy drops or retains as designed.

Do not use sleeps to “let the stream start.” Provide an explicit subscription milestone in the test adapter.

## Review checklist

- Is buffering deliberate and bounded?
- Is `onTermination` implemented?
- Are producer and consumer lifetimes both owned?
- Does cancellation stop callbacks and release resources?
- Are values snapshots or safe to send?
- Are UI updates MainActor-isolated?
- Are iOS 17+ Observation or newer Notification APIs availability-gated for iOS 16?
- Can tests await subscription and termination events deterministically?

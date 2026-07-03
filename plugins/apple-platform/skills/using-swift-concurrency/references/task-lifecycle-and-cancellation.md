# Task Lifecycle and Cancellation

Use this reference when choosing task forms, owning task handles, handling cancellation, using task groups, setting priority, or fixing fire-and-forget work.

## Task taxonomy

| Form | Structured? | Inherits actor? | Cancellation relationship | Use |
|---|---:|---:|---|---|
| Direct `await` | Yes | Current context | Current task | Sequential async work. |
| `async let` | Yes | Child task rules | Parent-child | Fixed parallel child operations. |
| `withTaskGroup` | Yes | Child task closure boundary | Parent-child | Dynamic parallel child operations. |
| `Task {}` | No | Often yes | Must cancel manually | Boundary from sync code, UI action, lifecycle-owned work. |
| `Task.immediate {}` | No | Starts on caller context | Must cancel manually | Rare ordering-sensitive sync-to-async bridge. |
| `Task.detached {}` | No | No | Must cancel manually | Independent work with Sendable captures. |

Prefer the most structured form that fits.

## Direct await first

Inside an async function, do not create a task just to immediately await it.

Bad:

```swift
func refresh() async throws {
    let task = Task { try await service.fetch() }
    let value = try await task.value
    apply(value)
}
```

Good:

```swift
func refresh() async throws {
    let value = try await service.fetch()
    apply(value)
}
```

Creating the task adds scheduling, changes cancellation and priority behavior, and can widen race windows.

## `async let`

Use `async let` for a fixed number of independent child operations whose lifetime is the lexical scope.

```swift
func loadDashboard() async throws -> Dashboard {
    async let summary = api.summary()
    async let messages = api.messages()
    async let avatar = api.avatar()

    return try await Dashboard(
        summary: summary,
        messages: messages,
        avatar: avatar
    )
}
```

Rules:

- Await every `async let` before leaving scope, or let Swift cancel outstanding children on scope exit.
- Do not use `async let` for unbounded collections.
- Make captured values safe for child-task transfer.

## Task groups

Use task groups for dynamic child work.

```swift
func thumbnails(for assets: [Asset]) async throws -> [Thumbnail] {
    try await withThrowingTaskGroup(of: (Asset.ID, Thumbnail).self) { group in
        for asset in assets {
            group.addTask {
                try Task.checkCancellation()
                return (asset.id, try await render(asset))
            }
        }

        var result: [Asset.ID: Thumbnail] = [:]
        for try await (id, thumbnail) in group {
            result[id] = thumbnail
        }
        return assets.compactMap { result[$0.id] }
    }
}
```

Rules:

- Use throwing groups when failure should cancel siblings.
- Use `addTaskUnlessCancelled` when adding many tasks after cancellation should stop work.
- Avoid adding thousands of child tasks without bounding concurrency if each child is heavy.
- Do not mutate non-thread-safe shared state from child tasks. Return values and aggregate in the parent.

## Unstructured task ownership

Every unstructured task needs an owner and a cancellation point.

Bad:

```swift
func start() {
    Task {
        await observeForever()
    }
}
```

Better:

```swift
@MainActor
final class ObserverModel {
    private var observationTask: Task<Void, Never>?

    func start() {
        observationTask?.cancel()
        observationTask = Task { [weak self] in
            await self?.observeForever()
        }
    }

    func stop() {
        observationTask?.cancel()
        observationTask = nil
    }

    deinit {
        observationTask?.cancel()
    }
}
```

If a method starts unstructured work that tests must observe, return the task:

```swift
@discardableResult
func refresh() -> Task<Void, Never> {
    Task { await runRefresh() }
}
```

## Cancellation is cooperative

Calling `cancel()` sets cancellation state. It does not kill execution.

Cancellation-aware code should:

- Use throwing async APIs that react to cancellation when possible.
- Call `try Task.checkCancellation()` between chunks of synchronous work.
- Check `Task.isCancelled` in nonthrowing loops.
- Clean up in `defer` or `withTaskCancellationHandler`.
- Treat `CancellationError` as a normal terminal condition.

Example:

```swift
@concurrent
func transcode(_ input: Input) async throws -> Output {
    var state = Transcoder(input)
    while !state.isFinished {
        try Task.checkCancellation()
        state.processNextChunk()
    }
    return state.output
}
```

## Cancellation handlers

Use `withTaskCancellationHandler` to cancel underlying legacy work or resume a suspended bridge.

```swift
func data(for request: URLRequest) async throws -> Data {
    let handle = LegacyRequestHandle()

    return try await withTaskCancellationHandler {
        try await withCheckedThrowingContinuation { continuation in
            handle.start(request) { result in
                continuation.resume(with: result)
            }
        }
    } onCancel: {
        handle.cancel()
    }
}
```

The cancellation handler can run concurrently with the operation. Protect shared continuation/handle state if both paths can resume or mutate it.

## `Task.detached`

Detached tasks are independent. They do not inherit actor isolation. Captures must be safe to send.

Use detached only for work that should be independent of the current actor and task hierarchy:

```swift
func uploadAnalytics(_ event: AnalyticsEvent) {
    Task.detached(priority: .background) { [event] in
        await Analytics.shared.upload(event)
    }
}
```

Before using detached, ask:

- Why not a structured child task?
- Why not `@concurrent`?
- Why not a long-lived service actor/queue with its own task?
- How is cancellation handled?
- Are all captures Sendable or one-way transferred?
- Is losing task-local values acceptable?

## `Task.immediate`

Use immediate tasks only when initial synchronous execution order matters.

```swift
@MainActor
func begin() {
    Task.immediate { [weak self] in
        guard let self else { return }
        self.phase = .started // guaranteed before begin() returns if no suspension before it
        await self.load()
    }
}
```

Cautions:

- Immediate tasks can overhang the current executor before first suspension.
- They are still unstructured and need cancellation if long-lived.
- They are not a general replacement for actor methods or direct async APIs.

## Priority

Avoid explicit priority unless product behavior demands it. Swift usually propagates priority correctly through structured concurrency.

Good explicit priority:

```swift
Task(priority: .background) {
    await cache.warmNonUserVisibleEntries()
}
```

Bad explicit priority:

```swift
Task(priority: .high) {
    await everything()
}
```

Document the reason for non-default priority.

## Long-lived tasks

For tasks that consume streams, notifications, or delegates:

- Store the task handle.
- Cancel it when no longer needed.
- Ensure the sequence terminates or the task observes cancellation.
- Avoid retaining the owner forever through a strong `self` capture.
- Await termination in tests.

```swift
@MainActor
func observeNotifications() {
    notificationTask?.cancel()
    notificationTask = Task { [weak self] in
        for await notification in NotificationCenter.default.notifications(named: .didChange) {
            guard !Task.isCancelled else { break }
            await self?.handle(notification)
        }
    }
}
```

## Review checklist

- Could direct `await` replace a `Task`?
- Could `async let` or a task group replace multiple unstructured tasks?
- Who owns each unstructured/detached/immediate task?
- When is each long-lived task cancelled?
- Is cancellation checked in CPU loops and custom bridges?
- Is `CancellationError` handled as normal control flow?
- Are explicit priorities justified?
- Are detached captures safe and deliberate?

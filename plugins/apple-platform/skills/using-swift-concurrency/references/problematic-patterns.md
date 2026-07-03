# Problematic Patterns

Use this reference to audit Swift Concurrency code for patterns that compile but are fragile, misleading, unavailable on iOS 16, or semantically wrong.

## Quick reference

| Pattern | Problem | Better default |
|---|---|---|
| Actor as background queue | Actors are isolation domains, not background annotations. | `@concurrent`, structured tasks, or service design. |
| Stateless actor | Serializes nothing useful. | `struct`/`final class` service. |
| Split isolation | One type has mixed actor domains. | Type-level actor or separate types. |
| `Task.detached` for off-main work | Loses context and requires Sendable captures. | `@concurrent`, task group, or service. |
| Hidden unstructured tasks | No owner/cancellation/test handle. | Structured task or returned/stored handle. |
| `MainActor.run` everywhere | Dynamic boundary instead of static contract. | `@MainActor` declarations. |
| Blocking async work | Deadlocks/thread starvation. | Stay async; do not semaphore-wait. |
| `@unchecked Sendable` as fix-it | Manual proof missing. | Values, actors, locks, snapshots. |
| `@preconcurrency` spread everywhere | Silences diagnostics globally. | Adapter boundary. |
| New API without availability | Crashes/compile issues on iOS 16. | `#available`/fallback/adapter. |
| Sleep/yield tests | Flaky scheduler guesses. | Event-driven synchronization. |

## Split isolation

Problem:

```swift
final class ScreenModel {
    var id: UUID
    @MainActor var title: String
}
```

The type has no coherent isolation contract. It may become impossible to use safely across actors.

Better:

```swift
@MainActor
final class ScreenModel {
    nonisolated let id: UUID
    var title: String
}
```

Or separate DTO/state from UI model.

## Stateless actors

Problem:

```swift
actor APIClient {
    func user(id: User.ID) async throws -> User { ... }
}
```

No state is protected. The actor adds async boundaries and possible serialization without benefit.

Better:

```swift
struct APIClient: Sendable {
    func user(id: User.ID) async throws -> User { ... }
}
```

Use an actor only if protecting mutable state such as token refresh, cache, rate limits, in-flight de-duplication, or a non-thread-safe dependency.

## Actor chosen for synchronous state

Problem:

```swift
actor FeatureFlags {
    private var flags: [String: Bool]

    func isEnabled(_ key: String) -> Bool { flags[key] == true }
}
```

Every caller must `await` even when synchronous access is required throughout the app.

Better options:

- Immutable `Sendable` snapshot.
- `@MainActor` if flags are UI/configuration state only used on main.
- Lock-protected class if synchronous shared mutation is truly needed.
- Actor if async access is acceptable and serialization is valuable.

## `Task.detached` misuse

Problem:

```swift
@MainActor
func refresh() {
    Task.detached {
        let value = await service.fetch()
        await MainActor.run { self.value = value }
    }
}
```

Detached loses actor inheritance and structured cancellation, and capturing `self` is problematic.

Better:

```swift
@MainActor
func refresh() {
    task?.cancel()
    task = Task { [weak self] in
        guard let self else { return }
        let value = await self.service.fetch()
        self.value = value
    }
}
```

If CPU-heavy work should leave MainActor, put that work in an `@concurrent` function with Sendable inputs/outputs.

## Unstructured task inside async function

Problem:

```swift
func save() async {
    Task { await database.save(draft) }
}
```

The function returns before saving; cancellation/errors are lost.

Better:

```swift
func save() async throws {
    try await database.save(draft)
}
```

Only create unstructured tasks at synchronous boundaries or independent lifecycle boundaries.

## Fire-and-forget with no owner

Problem:

```swift
func startObserving() {
    Task {
        for await event in events { handle(event) }
    }
}
```

The task can leak forever and tests cannot await it.

Better:

```swift
private var observationTask: Task<Void, Never>?

func startObserving() {
    observationTask?.cancel()
    observationTask = Task { [weak self] in
        await self?.observe()
    }
}

func stopObserving() {
    observationTask?.cancel()
    observationTask = nil
}
```

## MainActor overreach

Problem:

```swift
@MainActor
struct APIResponse: Codable, Sendable {
    let id: UUID
}
```

A data value is accidentally UI-bound, causing Codable/Sendable/generic issues.

Better:

```swift
nonisolated struct APIResponse: Codable, Sendable {
    let id: UUID
}
```

Use `@MainActor` for UI state and imperative UI APIs, not for portable data.

## `MainActor.run` overuse

Problem:

```swift
await MainActor.run {
    model.title = title
}
```

This hides the reusable isolation contract.

Better:

```swift
@MainActor
func apply(title: String) {
    model.title = title
}

await apply(title: title)
```

Use `MainActor.run` at legacy/dynamic boundaries only.

## Blocking on async

Problem:

```swift
let group = DispatchGroup()
group.enter()
Task {
    await work()
    group.leave()
}
group.wait()
```

Can starve the cooperative executor and deadlock.

Better: make the caller async or redesign the boundary.

## Lock held across await

Problem:

```swift
lock.withLock {
    state.isLoading = true
    await service.load() // invalid design even if written through wrappers
}
```

Locks protect synchronous critical sections only.

Better:

```swift
lock.withLock { $0.isLoading = true }
let value = try await service.load()
lock.withLock { $0.value = value; $0.isLoading = false }
```

Re-check state after await if needed.

## `@unchecked Sendable` without invariant

Problem:

```swift
final class Store: @unchecked Sendable {
    var items: [Item] = []
}
```

No safety proof.

Better:

```swift
actor Store {
    private var items: [Item] = []
}
```

Or a lock-protected final class with documented invariant.

## Availability blind spots

Problem:

```swift
@Observable
final class Model { }
```

If the app supports iOS 16, this is not an unconditional baseline.

Better:

```swift
@MainActor
final class Model: ObservableObject { }

@available(iOS 17, *)
@Observable
@MainActor
final class ObservationModel { }
```

Do the same for newer synchronization and beta frameworks.

## Async wrapper over multi-shot callback

Problem:

```swift
func nextValue() async -> Value {
    await withCheckedContinuation { continuation in
        source.onValue = { continuation.resume(returning: $0) }
    }
}
```

If `onValue` fires more than once, the continuation resumes multiple times.

Better: use `AsyncStream`, or clear the callback after first value with synchronization.

## Ignoring actor reentrancy

Problem:

```swift
actor Store {
    private var loaded = false

    func loadIfNeeded() async {
        guard !loaded else { return }
        await load()
        loaded = true
    }
}
```

Multiple calls can pass the guard before `loaded` changes.

Better: set an in-progress flag/task before awaiting or re-check after await.

## Tests that guess scheduler progress

Problem:

```swift
subject.start()
await Task.yield()
#expect(subject.didStart)
```

Better:

```swift
subject.start()
await subject.waitUntilStarted()
#expect(subject.didStart)
```

## Checklist

- Is any actor stateless or used as a background queue?
- Does every unstructured task have an owner and cancellation?
- Is default MainActor isolation accidentally applied to data/protocols?
- Is any `@unchecked Sendable` missing a safety proof?
- Are locks purely synchronous?
- Are continuations exactly-once and cancellation-safe?
- Are iOS 17+ / iOS 18+ / beta APIs gated for iOS 16 projects?
- Are async tests event-driven?

# Logical Races and Reentrancy

Use this reference when async code produces out-of-order state, stale UI updates, duplicate work, actor reentrancy bugs, or behavior changes after converting completion handlers to async/await.

## Data race versus logical race

Swift’s strict concurrency can prevent many data races. It does not prove that your state machine is logically correct.

Logical races happen when:

- Multiple async operations overlap and complete out of order.
- State read before an `await` is stale after the `await`.
- An actor method is re-entered while suspended.
- A task starts later than code assumed.
- Migration from queues/completion handlers changes ordering.

## Critical rule

`await` ends your synchronous critical section.

Everything that must be checked and reserved atomically should happen before the first suspension point.

Bad:

```swift
@MainActor
func submit() {
    Task {
        await prepare()
        guard !isSubmitting else { return }
        isSubmitting = true
        await send()
        isSubmitting = false
    }
}
```

Better:

```swift
@MainActor
func submit() {
    guard !isSubmitting else { return }
    isSubmitting = true

    Task { [weak self] in
        guard let self else { return }
        defer { self.isSubmitting = false }
        await self.send()
    }
}
```

## Stale UI completions

Problem:

```swift
@MainActor
func load(userID: User.ID) {
    Task {
        profile = try await service.profile(id: userID)
    }
}
```

If `userID` changes or a second load starts, an older result may overwrite newer state.

Fix options:

### Cancel previous task

```swift
private var loadTask: Task<Void, Never>?

@MainActor
func load(userID: User.ID) {
    loadTask?.cancel()
    loadTask = Task { [weak self] in
        do {
            let profile = try await service.profile(id: userID)
            guard !Task.isCancelled else { return }
            self?.profile = profile
        } catch is CancellationError { }
        catch {
            guard !Task.isCancelled else { return }
            self?.error = error
        }
    }
}
```

### Version result

```swift
private var generation = 0

@MainActor
func load(userID: User.ID) async {
    generation += 1
    let currentGeneration = generation

    do {
        let profile = try await service.profile(id: userID)
        guard generation == currentGeneration else { return }
        self.profile = profile
    } catch {
        guard generation == currentGeneration else { return }
        self.error = error
    }
}
```

### Validate state after await

```swift
let requestedID = selectedID
let profile = try await service.profile(id: requestedID)
guard selectedID == requestedID else { return }
self.profile = profile
```

## Actor reentrancy

Actors serialize synchronous access, but actor methods are reentrant at suspension points.

Problem:

```swift
actor TokenProvider {
    private var token: Token?

    func validToken() async throws -> Token {
        if let token, token.isValid { return token }
        token = try await refreshToken()
        return token!
    }
}
```

Two callers can both pass the initial check and refresh.

Better with in-flight task:

```swift
actor TokenProvider {
    private var token: Token?
    private var refreshTask: Task<Token, Error>?

    func validToken() async throws -> Token {
        if let token, token.isValid { return token }
        if let refreshTask { return try await refreshTask.value }

        let task = Task { try await refreshToken() }
        refreshTask = task

        do {
            let token = try await task.value
            self.token = token
            self.refreshTask = nil
            return token
        } catch {
            self.refreshTask = nil
            throw error
        }
    }
}
```

## Re-check after await

Whenever an actor method uses pre-await state after suspension, re-check.

Bad:

```swift
actor Store {
    private var items: [Item.ID: Item] = [:]

    func update(id: Item.ID) async throws {
        guard var item = items[id] else { return }
        item.details = try await fetchDetails(id)
        items[id] = item // May resurrect deleted item or overwrite newer item.
    }
}
```

Better:

```swift
func update(id: Item.ID) async throws {
    guard items[id] != nil else { return }
    let details = try await fetchDetails(id)
    guard var current = items[id] else { return }
    current.details = details
    items[id] = current
}
```

## Ordering changes from completion handlers

Completion-handler code often synchronously enqueues work onto a specific queue. Async/await code introduces task scheduling and suspension, which can change ordering.

Before:

```swift
func toggle(completion: @escaping () -> Void) {
    queue.async {
        self.state.toggle()
        completion()
    }
}
```

After:

```swift
func toggle() async {
    state.toggle()
}

Task { await toggle() }
```

Creating the task does not execute the body immediately. If ordering matters from a synchronous caller, consider making the caller async, using `Task.immediate` sparingly, or preserving a serial executor/actor boundary.

## Button taps and idempotency

For user actions:

- Disable or guard synchronously before starting work.
- Decide whether repeated taps cancel previous work, queue work, coalesce work, or no-op.
- Reflect the policy in state names: `isLoading`, `currentRequestID`, `inFlight`, `pending`, `lastSubmittedVersion`.

Example coalescing:

```swift
@MainActor
func refresh() {
    if refreshTask != nil { return }
    refreshTask = Task { [weak self] in
        defer { self?.refreshTask = nil }
        await self?.runRefresh()
    }
}
```

Example latest-wins:

```swift
@MainActor
func search(_ query: String) {
    searchTask?.cancel()
    searchTask = Task { [weak self] in
        await self?.performSearch(query)
    }
}
```

## Artificial delay debugging

To expose races, insert randomized delays in debug-only code or tests around suspension boundaries.

```swift
#if DEBUG
func raceProbe() async {
    let delay = UInt64.random(in: 0...20_000_000)
    try? await Task.sleep(nanoseconds: delay)
}
#endif
```

Use probes to find bugs, not to fix tests. Production correctness must come from explicit happens-before edges, cancellation, versioning, or state reservations.

## Review checklist

- What state is read before each `await`?
- Can that state change during the suspension?
- Are user actions repeatable, cancelable, coalesced, or ignored?
- Can older results overwrite newer state?
- Do actor methods re-check invariants after suspension?
- Did converting from callbacks/queues to tasks change ordering?
- Are tests covering overlapped calls, not just one-at-a-time calls?

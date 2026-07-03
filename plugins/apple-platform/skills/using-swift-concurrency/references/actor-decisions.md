# Actor Decisions

Use this reference when deciding whether a type should be a value type, `@MainActor` class, custom actor, locked class, custom global actor, or plain nonisolated class.

## Correct mental model

Actors serialize access to actor-isolated mutable state. They are not “background objects,” not a replacement for every lock, and not a way to silence `Sendable` diagnostics.

An actor is appropriate when these conditions mostly hold:

1. The type owns shared mutable state.
2. That state has invariants requiring serialized access or atomic multi-step operations.
3. Asynchronous access from outside the actor is acceptable.
4. The state is not fundamentally UI-bound MainActor state.
5. Reentrancy across `await` has been designed deliberately.

The protected stored properties may themselves be `Sendable`. A `Dictionary` of `Sendable` values can still be shared mutable state that needs actor isolation. The question is shared mutation and invariants, not merely whether the stored property type is non-Sendable.

## Decision table

| Situation | Prefer |
|---|---|
| Independent values, DTOs, requests, responses, IDs | `struct`/`enum`, usually `Sendable`. |
| UI-bound state, view models, controllers, navigation, presentation | `@MainActor final class` or `@MainActor @Observable`/`ObservableObject` as availability permits. |
| Shared mutable state with async API acceptable | `actor`. |
| Shared mutable state requiring synchronous reads/writes | `final class` with a lock, or redesign to avoid sync access. |
| Stateless service with async functions | `struct` or `final class`; no actor. |
| CPU-heavy pure work | Nonisolated value/service function; `@concurrent` when called from actor-isolated code and off-actor execution is desired. |
| Serializing access to a subsystem with callback/delegate legacy API | Actor or `@MainActor` adapter depending on callback thread and state ownership. |
| Multiple types all confined to a non-main serial domain | Consider a custom global actor only if the domain is broad and stable. |

## Value type first

Use a value type when each consumer should own its own copy or when the value can be passed safely between isolation domains.

```swift
struct UserSnapshot: Sendable, Codable, Identifiable {
    let id: User.ID
    let displayName: String
}
```

Do not turn data records into actors. Actor identity and async access are expensive semantic commitments.

## MainActor for UI state

Most iOS UI state wants `@MainActor`:

```swift
@MainActor
final class ProfileViewModel: ObservableObject {
    @Published private(set) var state: State = .idle

    func refresh() {
        Task { [weak self] in
            guard let self else { return }
            self.state = .loading
            let snapshot = try await service.profile()
            self.state = .loaded(snapshot)
        }
    }
}
```

Use `@MainActor` at the type level when most members are UI-bound. Avoid split isolation such as a nonisolated type with one `@MainActor` property unless the split is intentional and documented.

## Custom actor examples

Appropriate actor:

```swift
actor ImageCache {
    private var storage: [URL: Image] = [:]

    func image(for url: URL, load: @Sendable () async throws -> Image) async throws -> Image {
        if let cached = storage[url] { return cached }
        let image = try await load()
        if let cached = storage[url] { return cached } // reentrancy-aware check
        storage[url] = image
        return image
    }
}
```

Why this actor is justified:

- There is shared mutable state.
- Mutations must be serialized.
- External access can be async.
- The state is not UI state.
- The post-`await` cache check handles actor reentrancy.

Stateless actor anti-pattern:

```swift
actor APIClient {
    func fetchUser(id: User.ID) async throws -> User { ... }
}
```

If the client has no mutable shared state, use a `struct` or `final class` instead. Add an actor only if it protects meaningful state such as token refresh coordination, request de-duplication, rate-limit state, or a mutable cache.

## Actor versus lock

Choose an actor when callers can `await` and the state’s operations are naturally asynchronous.

Choose a lock when the API must be synchronous and critical sections are small:

```swift
final class TokenStore: @unchecked Sendable {
    private let lock = OSAllocatedUnfairLock(initialState: Token?.none)

    var current: Token? {
        lock.withLock { $0 }
    }

    func update(_ token: Token?) {
        lock.withLock { $0 = token }
    }
}
```

Lock rules:

- Never call `await` while holding a lock.
- Never invoke arbitrary callbacks while holding a lock.
- Keep critical sections small.
- Audit `@unchecked Sendable` with comments or tests.
- Prefer a single protected state value over scattered locked properties.

Actor rules:

- Treat every `await` as releasing the actor to reentrant work.
- Keep critical state changes before suspension when possible.
- Re-check invariants after suspension.
- Avoid actor APIs that require many chatty awaits when a single isolated operation would be better.

## Custom global actors

A custom global actor can be useful for a broad serial domain, such as a database context or a non-thread-safe engine shared across many types:

```swift
@globalActor
enum DatabaseActor {
    actor ActorType { }
    static let shared = ActorType()
}

@DatabaseActor
final class DatabaseSession {
    func save(_ record: Record) throws { }
}
```

Use this only when the domain is durable and cross-cutting. Do not create a global actor for one class. Do not use a custom global actor to avoid understanding task ownership.

## Reentrancy test before choosing actor

For every actor method with an `await`, ask:

- What state was read before the `await`?
- Can another task change it during the suspension?
- Should the method re-check, reserve, or mark in-progress before suspending?
- Is a task memoization table needed?

Naive:

```swift
actor Loader {
    private var cache: [URL: Data] = [:]

    func data(for url: URL) async throws -> Data {
        if let data = cache[url] { return data }
        let data = try await fetch(url)
        cache[url] = data
        return data
    }
}
```

Better for duplicate suppression:

```swift
actor Loader {
    private var cache: [URL: Data] = [:]
    private var inFlight: [URL: Task<Data, Error>] = [:]

    func data(for url: URL) async throws -> Data {
        if let data = cache[url] { return data }
        if let task = inFlight[url] { return try await task.value }

        let task = Task { try await fetch(url) }
        inFlight[url] = task
        do {
            let data = try await task.value
            cache[url] = data
            inFlight[url] = nil
            return data
        } catch {
            inFlight[url] = nil
            throw error
        }
    }
}
```

## Red flags

- Actor has no mutable state.
- Actor exists only to make compiler errors disappear.
- Actor wraps URLSession but adds no serialized state.
- Actor exposes many small properties that callers fetch one by one.
- Actor method reads state, awaits, then writes based on stale assumptions.
- Actor is used because “actors are thread-safe” while the API still returns mutable non-Sendable references.
- Actor is selected even though callers require synchronous access.

## Checklist

- What state is being protected?
- What invariant must be serialized?
- Why is `@MainActor` not the right isolation?
- Can callers tolerate async access?
- Does the actor leak non-Sendable mutable state to callers?
- What happens if two calls overlap and interleave at every `await`?
- Would a value type, lock, or isolated closure be simpler?

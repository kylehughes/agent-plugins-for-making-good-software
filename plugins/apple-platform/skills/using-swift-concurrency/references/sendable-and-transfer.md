# Sendable and Transfer

Use this reference when fixing `Sendable`, `@Sendable`, `sending`, non-Sendable captures, transfer diagnostics, global actor Sendability, or `@unchecked Sendable`.

## Meanings

| Term | Means |
|---|---|
| `Sendable` | Values of this type can be safely used across isolation domains. |
| `@Sendable` | A function/closure value can be safely invoked across concurrency domains; captures are checked. |
| `sending` | This value is transferred across an isolation boundary; caller must not keep using the old region in a racing way. |
| non-Sendable | The type is not safe for concurrent shared use unless isolated, locked, immutable-by-convention, or transferred without aliases. |
| `@unchecked Sendable` | The compiler trusts a manual synchronization/immutability proof. The proof is your responsibility. |

## Prefer Sendable values

DTOs, IDs, snapshots, request payloads, errors, and state enums should usually be immutable value types with `Sendable` conformance.

```swift
struct ProfileSnapshot: Sendable, Codable, Identifiable, Equatable {
    let id: UUID
    let displayName: String
    let avatarURL: URL?
}
```

Avoid passing live mutable reference objects across actors. Pass snapshots.

## Classes and Sendable

A class can be `Sendable` only if its shared use is safe. Common safe shapes:

- Immutable `final class` with only `let` Sendable state.
- Internally synchronized class where all mutable state is protected by a lock or atomics.
- Global-actor-isolated class, with inheritance caveats.

Unsafe:

```swift
final class Session: Sendable {
    var token: String? // mutable unsynchronized reference state
}
```

Safer immutable:

```swift
final class Configuration: Sendable {
    let baseURL: URL
    let headers: [String: String]

    init(baseURL: URL, headers: [String: String]) {
        self.baseURL = baseURL
        self.headers = headers
    }
}
```

Safer synchronized:

```swift
final class SessionStore: @unchecked Sendable {
    private let state = OSAllocatedUnfairLock(initialState: State())

    func token() -> String? {
        state.withLock { $0.token }
    }

    func setToken(_ token: String?) {
        state.withLock { $0.token = token }
    }
}
```

## `@unchecked Sendable` audit rules

Only use `@unchecked Sendable` when all are true:

1. The type is `final`, or subclassing cannot break the invariant.
2. Every mutable stored property is protected by one synchronization mechanism or actor/global actor.
3. Protected mutable references do not escape unsafely.
4. No lock is held across `await` or arbitrary callbacks.
5. The invariant is documented at the conformance.
6. Tests or stress tests cover concurrent access when feasible.

Template:

```swift
/// SAFETY: `state` is the only mutable storage and is accessed only through
/// `stateLock.withLock`. The protected value never escapes the critical section.
final class CacheBox<Key: Hashable & Sendable, Value: Sendable>: @unchecked Sendable {
    private let stateLock = OSAllocatedUnfairLock(initialState: [Key: Value]())
}
```

## `@Sendable` closures

A closure should be `@Sendable` when it may execute concurrently, escape into a task, be stored by a concurrent type, or cross an actor boundary.

```swift
struct RetryPolicy: Sendable {
    let shouldRetry: @Sendable (Error, Int) -> Bool
}
```

Common capture fixes:

```swift
// Bad: captures mutable, non-Sendable self in a sendable closure.
group.addTask {
    await self.load(item)
}

// Better: capture immutable Sendable dependencies and values.
let service = self.service
let id = item.id
group.addTask {
    try await service.load(id: id)
}
```

If `self` is actor-isolated, prefer calling an actor method or extracting a Sendable snapshot rather than making the actor/class `@unchecked Sendable`.

## Global actor isolated types and Sendable

Global-actor-isolated types are usually safe to pass because use of their isolated state must hop to that actor. Swift has rules that infer Sendability for many such types and global-actor-isolated closures.

Caveat: a global-actor-isolated subclass of a nonisolated, non-Sendable superclass may not be Sendable. Do not assume every `@MainActor` class is freely Sendable in all inheritance designs.

Prefer this practical rule:

- A final `@MainActor` UI view model with no unsafe superclass is safe to share as a reference whose members are accessed on MainActor.
- Do not add explicit `Sendable` unless generic/API use actually needs it.
- Do not use Sendability of a UI object to justify doing work off MainActor with its mutable state.

## `sending`

`sending` is for transfer, not sharing.

```swift
func submit(_ payload: sending UploadPayload) async throws {
    try await uploader.submit(payload)
}
```

Use when:

- The callee consumes the value.
- The value may be non-Sendable but is safe to move because the caller will not use it afterward.
- The API represents ownership transfer.

Avoid when:

- Multiple owners will keep using the same reference.
- You are trying to silence a task-group capture warning without understanding aliases.
- The value is a UI object or live mutable model.

If a diagnostic says “sending value risks causing data races with later uses,” look for a use after transfer:

```swift
let payload = NonSendablePayload()
await submit(payload)
print(payload) // likely invalid after sending
```

## Non-Sendable first design

Keeping a reference type non-Sendable is often correct. It tells Swift not to allow concurrent shared use without an isolation proof.

```swift
nonisolated final class DraftEditor {
    var text: String = ""
}
```

This is useful for objects confined to one actor or one owner. It is not a synchronization mechanism by itself; it relies on the compiler and ownership model to prevent unsafe sharing. Region-based isolation may still allow one-way transfers when no aliases remain.

## Sendable protocols

Do not add `Sendable` to a protocol unless transfer across isolation domains is core to the protocol.

Too strong:

```swift
protocol ScreenModel: Sendable {
    var title: String { get }
}
```

Better if UI-bound:

```swift
@MainActor
protocol ScreenModel {
    var title: String { get }
}
```

Better if value/snapshot:

```swift
nonisolated protocol Snapshot: Sendable {
    var id: UUID { get }
}
```

Adding `Sendable` to a protocol makes every conformer prove cross-domain safety, which can force bad designs for UI, delegates, legacy objects, and actor-isolated types.

## Common diagnostics

### “Capture of non-Sendable type in @Sendable closure”

Fix order:

1. Capture immutable Sendable values instead of `self`.
2. Move work into an actor/global-actor method and call it with `await`.
3. Make the captured type a Sendable value/snapshot.
4. Add synchronization and `@unchecked Sendable` only if shared concurrent use is truly intended.

### “Task-isolated value passed as a strongly transferred parameter”

Fix order:

1. Do not use the value after transfer.
2. Make a Sendable snapshot for transfer.
3. Move object creation into the destination task/actor.
4. Change API from `sending` to borrowed/non-sending only if the callee does not actually consume or cross isolation.

### “Stored property of Sendable class is mutable”

Fix order:

1. Make the class immutable.
2. Convert to a value type.
3. Protect state with a lock/actor.
4. Remove `Sendable` if cross-domain use is not semantic.

## Review checklist

- Are values crossing actors/tasks immutable snapshots or truly Sendable?
- Are `@Sendable` closures capturing only safe values?
- Is `sending` a real ownership transfer?
- Is any `@unchecked Sendable` documented with a synchronization invariant?
- Is a protocol requiring `Sendable` for semantic reasons?
- Are UI objects kept on `MainActor` instead of made Sendable to satisfy background work?
- Are locks used without suspension or callback reentrancy?

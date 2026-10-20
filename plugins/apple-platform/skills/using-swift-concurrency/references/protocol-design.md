# Protocol Design

Use this reference when creating or revising Swift protocols that may interact with actors, MainActor, `Sendable`, default actor isolation, async requirements, or reusable packages.

## Protocols include concurrency contracts

A protocol requirement specifies more than shape. It can specify:

- Isolation: nonisolated, `@MainActor`, another global actor, or caller-inherited.
- Synchronicity: synchronous versus `async`.
- Transferability: `Sendable`, `@Sendable`, `sending`.
- Reentrancy/lifetime expectations: escaping closures, streams, cancellation.

Design protocols from both sides: call sites and ordinary conformers.

## First question: who should conform?

Before writing the protocol, name likely conformers:

- Immutable value snapshots?
- UI view models?
- Actors?
- Legacy Objective-C classes?
- Mock/test doubles?
- Reusable package implementations?

If a plain struct or mock cannot conform without ceremony, the protocol may be over-isolated or over-Sendable.

## Default actor isolation traps

In a target with `-default-isolation MainActor`, an unannotated protocol can become main-actor isolated. That is correct only for UI protocols.

For domain protocols, opt out explicitly:

```swift
nonisolated protocol UserRecord: Sendable, Identifiable {
    var id: UUID { get }
    var displayName: String { get }
}
```

For UI protocols, state isolation directly:

```swift
@MainActor
protocol ProfileScreenModel: AnyObject {
    var title: String { get }
    func refresh() async
}
```

Do not let a module default silently decide a reusable protocol’s public contract.

## Synchronous requirements are strong

A synchronous nonisolated requirement promises immediate access from any allowed context.

```swift
nonisolated protocol CacheKeyed {
    var cacheKey: String { get }
}
```

This excludes conformers whose value is actor-isolated unless they provide a safe nonisolated witness or isolated conformance.

Use synchronous requirements for:

- IDs and immutable values.
- Cheap pure properties.
- Protocols used in collections, hashing, equality, or decoding.

Avoid synchronous requirements for:

- Values that may need actor access.
- UI-derived state unless the protocol is `@MainActor`.
- Remote or persistent state.

## Async requirements are flexible

If callers can suspend, an async requirement can support actors, UI models, and plain values.

```swift
nonisolated protocol UserDisplaySource {
    var displayName: String { get async }
}
```

A synchronous implementation can satisfy many async requirements when isolation rules allow it. Use async requirements when the protocol represents a capability rather than a cheap stored value.

Do not make everything async. Async APIs add suspension points, reentrancy, and test complexity.

## `Sendable` on protocols

Add `Sendable` to a protocol only when conforming values are intended to cross isolation domains.

Correct:

```swift
nonisolated protocol RequestPayload: Sendable, Codable { }
```

Too broad:

```swift
protocol Coordinator: AnyObject, Sendable { }
```

A coordinator is usually UI-bound reference state; `@MainActor` is probably the real contract.

## Closure requirements

Escaping closures that may run from tasks or other isolation domains should declare both execution isolation and sendability.

Background/concurrent callback:

```swift
nonisolated protocol Downloader {
    func download(
        _ request: Request,
        progress: @escaping @Sendable (Progress) -> Void
    ) async throws -> Data
}
```

UI callback:

```swift
nonisolated protocol LoginCoordinator {
    func login(
        onEvent: @escaping @MainActor (LoginEvent) -> Void
    ) async
}
```

In Swift 6 language mode, a global-actor-isolated closure is normally inferred `@Sendable`. Still, include `@Sendable` if it clarifies an API boundary or if a generic/storage context requires it.

## Actors conforming to protocols

Actors cannot satisfy arbitrary synchronous nonisolated requirements with actor-isolated state.

Bad protocol for actors:

```swift
protocol CounterProtocol {
    var count: Int { get }
}
```

Actor-friendly:

```swift
protocol CounterProtocol {
    var count: Int { get async }
}
```

Or provide a safe nonisolated witness for immutable state:

```swift
actor UserStore: Identifiable {
    nonisolated let id: UUID
    private var users: [User.ID: User]
}
```

## Service protocols

Avoid `@MainActor` service protocols unless service calls must run on MainActor. UI consumers can call nonisolated async services from MainActor safely.

```swift
nonisolated protocol ProfileService: Sendable {
    func profile(id: User.ID) async throws -> ProfileSnapshot
}
```

If the implementation is a reference type with internal mutable state, make it safely `Sendable` or isolate it behind an actor. Do not force all services to be `@MainActor` because one view model uses them.

## Protocols refined from SDK protocols

A protocol that refines another protocol inherits its requirements and isolation expectations.

```swift
nonisolated protocol StoredEntity: Identifiable, Codable, Sendable {
    var displayName: String { get }
}
```

`Identifiable.id`, `Codable` machinery, and `Sendable` constraints all affect conformers. When diagnostics seem surprising, expand the inherited protocol requirements mentally.

## Associated types

Constrain associated types according to transfer semantics.

```swift
nonisolated protocol Repository: Sendable {
    associatedtype Entity: Sendable & Identifiable

    func entity(id: Entity.ID) async throws -> Entity
}
```

If `Entity` is a UI-bound model object, this protocol is wrong. Return a `Sendable` snapshot or make the protocol `@MainActor`.

## Conformance-side escape hatches are not protocol design

If every conformer needs one of these, redesign the protocol:

- `@preconcurrency` conformance.
- `@unchecked Sendable`.
- `nonisolated(unsafe)`.
- `assumeIsolated`.
- Dummy async wrappers around synchronous UI state.

Use isolated conformances for individual UI-bound types that conform to generic protocols, not as a substitute for clear protocol isolation.

## Design checklist

- Is the protocol UI-bound, domain-level, service-level, or low-level concurrency infrastructure?
- Is isolation explicit enough to survive different target default isolation settings?
- Can a simple struct conform?
- Can an actor conform if that is a target use case?
- Do synchronous requirements really need to be synchronous?
- Is `Sendable` required by semantics or just by one implementation?
- Are closure parameters correctly `@Sendable`, actor-isolated, or both?
- Are associated types constrained to Sendable only when returned/transferred across isolation?
- Are inherited protocol requirements compatible with expected conformers?

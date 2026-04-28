# Protocol Design

Use this reference when creating or revising Swift protocols that may be used across actor boundaries, under Swift 6 strict concurrency, or in codebases with default actor isolation settings.

Source: Matt Massicotte, "Concurrency Step-by-Step: Designing Protocols", <https://www.massicotte.org/step-by-step-designing-protocols/>, published 2026-04-26.

## Contents

- [Design From Both Sides](#design-from-both-sides)
- [Know the Active Dialect](#know-the-active-dialect)
- [Isolation Is a Contract](#isolation-is-a-contract)
- [Refined Protocols Carry Their Requirements](#refined-protocols-carry-their-requirements)
- [Synchronous Requirements Are Inflexible](#synchronous-requirements-are-inflexible)
- [Async Requirements Are More Flexible](#async-requirements-are-more-flexible)
- [`Sendable` Is a Severe Requirement](#sendable-is-a-severe-requirement)
- [Conformance-Side Escape Hatches](#conformance-side-escape-hatches)
- [Design Checklist](#design-checklist)

## Design From Both Sides

Protocols are contracts. In concurrent Swift, the contract includes isolation, suspension, and transferability.

When designing a protocol, evaluate two perspectives:

- How callers will use protocol values or generics.
- How ordinary conforming types will satisfy the requirements.

Create at least one plain conforming type while designing the protocol. Use it as feedback on whether the protocol is demanding unnecessary isolation, `Sendable`, or synchronous access.

## Know the Active Dialect

Protocol behavior can change substantially with these settings and features:

| Setting or feature | Why it matters |
|---|---|
| `DefaultActorIsolation` | A `MainActor` default can implicitly isolate protocols, types, and members. |
| `NonisolatedNonsendingByDefault` | Changes how nonisolated async requirements inherit isolation and avoid `Sendable` pressure. |
| `InferIsolatedConformances` | May infer actor-isolated conformances, but explicit conformance isolation is still useful when inference does not match intent. |

For portable protocols, avoid relying on a target's default actor isolation. Write the contract explicitly when isolation matters.

## Isolation Is a Contract

`@MainActor`, another global actor, and `nonisolated` are not implementation details on protocol requirements. They define where callers may use the requirement and what conforming types must provide.

Avoid letting a `MainActor` default silently become part of a reusable protocol unless the protocol is inherently UI-bound. A protocol used by model, storage, networking, or domain types is usually more flexible when it is explicitly `nonisolated` or when individual requirements carry the needed isolation.

```swift
nonisolated protocol CacheRecord {
    var key: String { get }
}
```

If the protocol is only meaningful on the main actor, state that directly:

```swift
@MainActor
protocol ViewStateModel {
    func refresh() async
}
```

## Refined Protocols Carry Their Requirements

A protocol that refines another protocol inherits that protocol's isolation contract. This matters most when refining SDK or third-party protocols defined under different defaults.

```swift
nonisolated protocol StoredEntity: Identifiable {
    var displayName: String { get }
}
```

If `Identifiable.id` is nonisolated, conformers must be able to provide `id` nonisolated unless they use an isolated conformance or another compatible design. Do not assume your protocol's default isolation overrides inherited requirements.

When a refined protocol causes surprising diagnostics, expand the inherited requirements mentally: ask what isolation each requirement actually demands.

## Synchronous Requirements Are Inflexible

A synchronous nonisolated requirement promises immediate access from any isolation domain:

```swift
nonisolated protocol UserRecord {
    var id: String { get }
}
```

That requirement excludes conformers whose `id` is actor-isolated unless they can provide a safe nonisolated implementation or use an isolated conformance. Before requiring synchronous access, ask whether callers truly need it.

## Async Requirements Are More Flexible

If callers can suspend, an async requirement can accept more conforming implementations:

```swift
nonisolated protocol UserRecord {
    var id: String { get async }
}
```

The requirement means access is allowed to suspend, not that every implementation must suspend. A synchronous stored property can satisfy an async requirement when the isolation rules allow it.

This flexibility is especially useful when conformers may be actors, `@MainActor` types, or plain value types. Verify behavior under the Swift language mode and feature flags used by the target; `NonisolatedNonsendingByDefault` is a major part of this model.

## `Sendable` Is a Severe Requirement

Requiring `Sendable` says conforming values can be used safely across isolation domains:

```swift
nonisolated protocol TransferableRecord: Sendable, Identifiable {
}
```

This can be exactly right for immutable values passed between actors. It can also make conformers much harder to write, especially if the protocol has synchronous requirements that may be called from multiple isolation domains.

Use this rule of thumb:

- Add `Sendable` when cross-actor transfer is core to the protocol's purpose.
- Do not add `Sendable` just to work around default `MainActor` diagnostics.
- Remember that `Sendable` can disable default `MainActor` inference for conforming types because the protocol has declared concurrency as part of its contract.

## Conformance-Side Escape Hatches

When an existing protocol design collides with a conforming type's isolation, choose the least surprising fix:

| Fix | Use when |
|---|---|
| Make the conforming member `nonisolated` | The member is immutable or otherwise safe to access from any isolation. |
| Use an isolated conformance | The protocol can be satisfied only from a specific global actor context. |
| Change a requirement to `async` | Callers do not need synchronous access and conformers may be isolated. |
| Add `Sendable` | Transferability is truly part of the protocol contract. |
| Relax protocol isolation | The protocol was accidentally isolated by default settings. |

Do not use these as mechanical compiler fixes. Each option changes what callers may do and what conformers must guarantee.

## Design Checklist

- Is this protocol inherently actor-isolated, or did a default setting add isolation accidentally?
- Does every refined protocol bring requirements with compatible isolation?
- Do callers truly need synchronous access, or would `async` make the contract more correct?
- Is `Sendable` a semantic requirement or just a workaround?
- Can a regular value type conform without ceremony?
- Can an actor or `@MainActor` type conform if that should be supported?
- Are isolation choices explicit enough to survive different target settings?

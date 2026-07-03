# Isolation and Protocol Conformances

Use this reference to resolve protocol conformance errors involving actor isolation, `@MainActor`, default actor isolation, `Equatable`, `Hashable`, `Codable`, `Identifiable`, delegates, and other synchronous protocols.

If you control the protocol, read `protocol-design.md` first.

## Core mismatch

Many standard protocols have synchronous nonisolated requirements. A `@MainActor` type or a type in a MainActor-default target may not be able to satisfy those requirements with isolated state.

Typical diagnostic shape:

```text
Main actor-isolated ... cannot satisfy nonisolated protocol requirement
```

Do not fix this by reflexively adding `nonisolated(unsafe)`, `@unchecked Sendable`, or `MainActor.assumeIsolated`. Choose the conformance model that matches the API.

## Solution order

1. **Make the data nonisolated** if it is pure data and should not be UI-bound.
2. **Make specific witnesses nonisolated** if they are immutable, Sendable, and safe from any isolation domain.
3. **Use an isolated conformance** when the type is genuinely global-actor isolated and the conformance should only be used on that actor.
4. **Use a DTO/snapshot** when encoding, equality, hashing, or identity should not depend on live actor-isolated UI state.
5. **Use `@preconcurrency`** only for legacy protocols/modules where modern isolation cannot be expressed cleanly.
6. **Use `assumeIsolated` or `nonisolated(unsafe)`** only as a last resort with a runtime/threading proof.

## Nonisolated data types

In a MainActor-default UI target, DTOs and state enums often need explicit `nonisolated`.

```swift
nonisolated struct ProfileDTO: Sendable, Codable, Equatable, Identifiable {
    let id: UUID
    let name: String
}
```

If many such declarations appear, move them to a nonisolated domain module.

## Nonisolated witnesses

Immutable identity can often be safely nonisolated:

```swift
@MainActor
final class RowViewModel: Identifiable {
    nonisolated let id: UUID

    var title: String

    init(id: UUID, title: String) {
        self.id = id
        self.title = title
    }
}
```

Use this for stable, immutable, Sendable values. Do not mark mutable UI state nonisolated.

## Isolated conformances

Use isolated conformances when a global-actor-isolated type should conform only from that actor.

```swift
@MainActor
final class ImageModel {
    var name: String = ""
}

extension ImageModel: @MainActor Equatable {
    static func == (lhs: ImageModel, rhs: ImageModel) -> Bool {
        lhs.name == rhs.name
    }
}
```

This says the conformance is usable on MainActor. It does not mean generic code from arbitrary isolation domains can freely use the conformance.

## `Equatable`

Good for immutable identity:

```swift
@MainActor
final class ItemViewModel: Identifiable, Equatable {
    nonisolated let id: UUID
    var title: String

    nonisolated static func == (lhs: ItemViewModel, rhs: ItemViewModel) -> Bool {
        lhs.id == rhs.id
    }
}
```

Good for UI-state equality only on MainActor:

```swift
extension ItemViewModel: @MainActor Equatable {
    static func == (lhs: ItemViewModel, rhs: ItemViewModel) -> Bool {
        lhs.title == rhs.title
    }
}
```

Bad: using `assumeIsolated` for equality that can be called by sets, diffing, tests, or background generic algorithms.

## `Hashable`

Hashing must be stable while a value is stored in a set or dictionary. Do not hash mutable UI state.

Prefer immutable IDs:

```swift
@MainActor
final class RowModel: Identifiable, Hashable {
    nonisolated let id: UUID

    nonisolated func hash(into hasher: inout Hasher) {
        hasher.combine(id)
    }

    nonisolated static func == (lhs: RowModel, rhs: RowModel) -> Bool {
        lhs.id == rhs.id
    }
}
```

If equality/hash truly depend on isolated mutable state, reconsider the type’s use as a hash key.

## `Codable`

Do not usually make live UI objects `Codable`. Encode/decode DTOs.

Better:

```swift
nonisolated struct DraftDocumentDTO: Sendable, Codable {
    var title: String
    var body: String
}

@MainActor
final class DraftDocumentModel: ObservableObject {
    @Published var title: String = ""
    @Published var body: String = ""

    var snapshot: DraftDocumentDTO {
        DraftDocumentDTO(title: title, body: body)
    }
}
```

For value types in a MainActor-default target, nested coding keys may need explicit `nonisolated`:

```swift
nonisolated struct Payload: Codable, Sendable {
    let id: UUID

    nonisolated private enum CodingKeys: String, CodingKey {
        case id
    }
}
```

If a type is intentionally `@MainActor Codable`, verify every generated/synthesized requirement and nested type has compatible isolation. Synthesis can create surprising diagnostics under default MainActor isolation.

## `Identifiable`

Use stable immutable IDs. Mark them nonisolated when the type is actor-isolated but the identity is safe:

```swift
actor Download: Identifiable {
    nonisolated let id: UUID
    private var progress: Double = 0
}
```

Do not compute `id` from mutable isolated state for a nonisolated requirement.

## `CustomStringConvertible` and logging protocols

`description` is synchronous and often called from arbitrary contexts. Avoid reading actor-isolated mutable state.

Prefer a snapshot:

```swift
struct JobSnapshot: Sendable, CustomStringConvertible {
    let id: UUID
    let state: State

    var description: String { "Job(\(id), \(state))" }
}
```

Or provide isolated debug helpers instead of conforming:

```swift
@MainActor
func debugDescription() -> String { ... }
```

## Delegates and Objective-C protocols

Legacy delegate requirements are often nonisolated because the framework predates Swift concurrency annotations.

Options:

- Use an isolated conformance if the protocol and compiler support it.
- Use a small nonisolated adapter that forwards into an actor/MainActor task.
- Use `@preconcurrency import` for the legacy framework boundary, not everywhere.
- Keep callback threading documented.

Example adapter:

```swift
final class LegacyDelegateAdapter: NSObject, LegacyDelegate {
    weak var owner: (any LegacyEventHandling)?

    func legacyDidUpdate(_ value: LegacyValue) {
        Task { @MainActor [weak owner] in
            await owner?.handle(value)
        }
    }
}

@MainActor
protocol LegacyEventHandling: AnyObject {
    func handle(_ value: LegacyValue)
}
```

## `@preconcurrency` conformance

Use only for compatibility with old protocols whose requirements are not annotated accurately and where isolated conformances cannot model the behavior.

```swift
@MainActor
final class Model { }

extension Model: @preconcurrency LegacyProtocol { }
```

This is a migration escape hatch. It does not make the legacy protocol thread-safe.

## `assumeIsolated`

Last resort:

```swift
extension Model: LegacyProtocol {
    nonisolated func callback() {
        MainActor.assumeIsolated {
            self.handleCallback()
        }
    }
}
```

Use only when an external invariant guarantees the current executor. It can trap at runtime when the invariant is false. Prefer static isolation or an adapter.

## Decision flow

```text
Is the type accidentally isolated by default settings?
├─ Yes → mark data type/protocol/extension `nonisolated` or move modules.
└─ No
   Does the requirement only need immutable Sendable state?
   ├─ Yes → provide a `nonisolated` witness.
   └─ No
      Is the conformance only meaningful on a global actor?
      ├─ Yes → isolated conformance.
      └─ No
         Can the protocol become async or isolated?
         ├─ Yes → redesign protocol.
         └─ No → DTO, adapter, @preconcurrency, or assumeIsolated with proof.
```

## Checklist

- Is the conformance error caused by accidental default MainActor isolation?
- Is the protocol requirement synchronous/nonisolated by design?
- Can immutable identity satisfy the requirement safely?
- Would a DTO be cleaner than conforming a live UI object?
- Is an isolated conformance valid and sufficient?
- Is any `@preconcurrency`, `nonisolated(unsafe)`, or `assumeIsolated` localized and justified?
- Are synthesized `Codable`, `Hashable`, and nested types checked under the target’s default isolation?

# Extensions and Nested Types

Reference for when extensions are legitimate and how to organize nested types.

## Legitimate Extensions

Extensions are allowed only when they express something that cannot be cleanly represented in the primary declaration.

Allowed extension categories:

1. Custom protocol conformances, one protocol per extension.
2. Nested types, one nested type per extension.
3. Constrained generic extensions.
4. Extensions of external types.
5. Static constants that are true type API.
6. Protocol default implementations, when the extension provides real default behavior rather than visual grouping.

Everything else should be treated as suspicious and moved into the primary declaration.

### Constrained Generic Extensions

Use constrained extensions when the constraint is the reason the members exist.

```swift
// ✅ GOOD
extension Array where Element: Identifiable {
    var ids: [Element.ID] {
        map(\.id)
    }
}

// ❌ BAD: unconstrained extension used as a bucket
extension UserStore {
    func refresh() async throws { }
}
```

### External Type Extensions

Extensions on types from other modules are allowed when they add real, project-relevant functionality.

Rules:

- Prefer a dedicated file named for the external type and capability.
- Keep access as narrow as possible.
- Avoid broad public/internal conveniences on foundational types unless they are deliberate module API.
- Use `fileprivate` for file-local primitive constants.
- Do not add retroactive conformances unless unavoidable.

```swift
// ✅ GOOD: local helper in a dedicated file or tightly scoped implementation file
extension UIEdgeInsets {
    fileprivate static let avatarInsets = UIEdgeInsets(top: 8, left: 12, bottom: 8, right: 12)
}
```

### Protocol Default Implementations

Protocol extensions are legitimate when they implement default behavior.

```swift
protocol RetryableRequest {
    var retryLimit: Int { get }
    func perform() async throws
}

extension RetryableRequest {
    var retryLimit: Int { 3 }
}
```

Do not use protocol extensions as section buckets for requirements that belong in the protocol declaration.

## Nested Types

Nested types belong in dedicated extensions, one nested type per extension. Sort sibling nested types lexicographically by nested type name.

```swift
struct Message: Equatable, Hashable, Identifiable, Sendable {
    let body: String
    let id: UUID
}

extension Message {
    enum Priority: Comparable, Sendable {
        case high
        case low
        case normal
    }
}

extension Message {
    struct Receipt: Equatable, Sendable {
        let readAt: Date?
    }
}
```

This pattern is fractal. Complete a nested type's subtree before moving to the next sibling.

```swift
extension Message {
    struct Metadata: Codable, Equatable, Sendable {
        let createdAt: Date
    }
}

extension Message.Metadata {
    struct Author: Codable, Equatable, Sendable {
        let name: String
    }
}

extension Message.Metadata.Author: CustomStringConvertible {
    var description: String {
        name
    }
}

extension Message {
    enum Priority: Comparable, Sendable {
        case high
        case low
        case normal
    }
}
```

In the example above, `Metadata` and its `Author` subtree are completed before moving to sibling `Priority`.

Rules:

- Use one nested type per extension.
- Do not combine multiple sibling nested types in one extension.
- Do not put ordinary members in a nested-type extension.
- Do not create fake namespaces when a real owning type exists.
- Apply the same primary declaration, conformance, nested type, constants, and preview rules recursively to nested types.

```swift
// ❌ BAD
extension Message {
    enum Priority { }
    struct Metadata { }

    func send() { }
}
```

# Primary Declaration and Conformances

Reference for what belongs in a type's primary declaration and how to organize protocol conformances.

## Primary Type Declaration

The primary type declaration owns the type's actual interface. Do not fragment it.

Put these in the primary declaration:

- Stored properties.
- Computed properties that are not protocol requirements implemented in a custom conformance extension.
- Initializers and deinitializers.
- Lifecycle overrides.
- Ordinary methods.
- Private helpers.
- Actions and selectors.
- Synthesized, marker, or empty conformances in the inheritance clause.

```swift
// ✅ GOOD
struct User: Codable, Equatable, Hashable, Identifiable, Sendable {
    let id: UUID
    let name: String
}

// ✅ GOOD: empty/default conformance belongs on the type declaration
struct ImportFailure: Equatable, Error, Sendable {
    let message: String
}
```

Do not place nested types in the primary declaration unless the compiler requires it. Prefer dedicated nested-type extensions.

## Protocol Conformances

### Synthesized, Marker, and Empty Conformances

When the compiler provides the implementation, or no implementation is needed, declare the conformance on the primary type definition.

Common examples:

- `CaseIterable` when synthesized.
- `Codable`, `Encodable`, or `Decodable` when synthesized.
- `Equatable` and `Hashable` when synthesized.
- `Identifiable` when `id` is already present and no custom implementation is needed.
- `Sendable` when synthesized or marker-only.
- `Error` when no custom behavior is needed.

Sort conformances lexicographically unless another skill gives a stronger ordering rule.

```swift
// ✅ GOOD
struct Message: Codable, Equatable, Hashable, Identifiable, Sendable {
    let body: String
    let id: UUID
}

// ❌ BAD: synthesized conformance split into an empty extension
struct Message {
    let body: String
    let id: UUID
}

extension Message: Equatable { }
extension Message: Hashable { }
```

### Custom Conformances

When implementing protocol requirements yourself, use one protocol per extension.

```swift
// ✅ GOOD
extension User: Comparable {
    static func < (lhs: User, rhs: User) -> Bool {
        lhs.name < rhs.name
    }
}

extension User: CustomStringConvertible {
    var description: String {
        name
    }
}
```

Rules:

- One custom conformance protocol per extension.
- Sort custom conformance extensions by protocol name.
- Do not combine delegate/data source protocols in one extension.
- Do not add non-requirement helper methods to a protocol conformance extension unless they are private implementation details used only by that conformance and placing them in the primary type would reduce clarity. Keep that exception rare.
- If a custom conformance needs nested helper types, those helper types still belong in dedicated nested-type extensions, not inside the conformance extension, unless the compiler requires otherwise.

For `Codable`, use `Codable` on the primary declaration only when both `Encodable` and `Decodable` are synthesized. If encoding or decoding is custom, split custom implementations by actual protocol:

```swift
// ✅ GOOD
struct Event: Equatable, Sendable {
    let date: Date
    let title: String
}

extension Event: Decodable {
    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        date = try container.decode(Date.self, forKey: .date)
        title = try container.decode(String.self, forKey: .title)
    }
}

extension Event: Encodable {
    func encode(to encoder: Encoder) throws {
        var container = encoder.container(keyedBy: CodingKeys.self)
        try container.encode(date, forKey: .date)
        try container.encode(title, forKey: .title)
    }
}

extension Event {
    private enum CodingKeys: String, CodingKey {
        case date
        case title
    }
}
```

### Retroactive Conformances

Avoid conforming an external type to an external protocol. Prefer a wrapper type or a protocol/type owned by the current module.

If a retroactive conformance is unavoidable:

- Put it in a dedicated extension.
- Keep it out of arbitrary primary-type files.
- Use Swift 6's explicit retroactive-conformance syntax when the compiler requires it.
- Keep the conformance as narrow and local to the module as possible.

```swift
// Prefer avoiding this shape when both Date and Identifiable are external.
extension Date: @retroactive Identifiable {
    public var id: TimeInterval { timeIntervalSinceReferenceDate }
}
```

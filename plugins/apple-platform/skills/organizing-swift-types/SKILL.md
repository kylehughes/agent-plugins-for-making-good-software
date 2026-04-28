---
name: organizing-swift-types
description: Defines Swift conventions for structuring type declarations, access control, extension usage, file layout, and prohibited patterns like MARK comments and organizational extensions. Use when writing new Swift types, deciding whether to use an extension, structuring protocol conformances, organizing nested types, choosing access modifiers, placing file-scoped constants, or determining Swift file layout order.
---

# Swift Type Conventions

## Access Control

- Omit `internal` — it's the default; explicit declaration is noise
- Prefer the most restrictive access level possible
- Use `final` on classes unless designed for inheritance

## Declaration Modifiers

Apply modifiers in this order:

```swift
[access] [static|class] let|var name: Type
[access] [static|class] func name(params) -> ReturnType
```

Favor `let` over `var` for immutability.

## Prohibited Patterns

These patterns add noise without adding value when the other conventions in this skill are followed:

- **No MARK comments** — Deterministic symbol ordering (see the `ordering-symbols` skill) makes navigational markers redundant; they become stale signposts that drift from the code they describe
- **No organizational extensions** — Extensions exist for necessity (protocol conformance, nested types, generic constraints), not for grouping related members within the same module; using them for organization fragments the type's interface and hides members from the primary declaration
- **No unnecessary `self`** — Only use `self` when required (e.g., to disambiguate from a parameter); gratuitous `self` adds visual noise and obscures the cases where it actually matters

```swift
// ❌ BAD
init(name: String) {
    self.name = name
    self.isActive = true
    self.configureDefaults()
}

// ✅ GOOD
init(name: String) {
    self.name = name  // Required: disambiguates from parameter
    isActive = true   // No parameter named isActive, so no self
    configureDefaults()
}

// ❌ BAD
extension MyViewController {
    private func setupUI() { }
}
```

## Extensions

Use extensions only for:

1. **Protocol conformance with custom implementation** — One protocol per extension
2. **Nested types** — One nested type per extension
3. **Constrained generics** — `extension Array where Element: Identifiable`
4. **External types** — Adding functionality to types from other modules
5. **Constants** — Static constants on types

### Protocol Conformance

**Synthesized conformances** — When the compiler provides the implementation (e.g., `Equatable`, `Hashable`, `Sendable`, `Identifiable`, `Codable` for simple types), declare them on the type definition:

```swift
// ✅ GOOD: Synthesized conformances on type definition
struct User: Equatable, Hashable, Identifiable, Sendable {
    let id: UUID
    let name: String
}
```

**Custom implementations** — When you provide the implementation, use one protocol per extension:

```swift
// ✅ GOOD: Custom implementations in separate extensions
extension User: CustomStringConvertible {
    var description: String {
        "User(\(name))"
    }
}

extension User: Comparable {
    static func < (lhs: User, rhs: User) -> Bool {
        lhs.name < rhs.name
    }
}
```

### Nested Types

Define nested types in dedicated extensions, in lexicographic order:

```swift
struct Message: Equatable, Hashable, Sendable {
    let content: String
    let id: UUID
}

extension Message {
    enum Priority {
        case high
        case low
        case normal
    }
}

extension Message {
    struct Metadata: Codable, Equatable, Sendable {
        let timestamp: Date
    }
}
```

This pattern is fractal—nested types follow the same structure, and each nested type's extensions appear before moving to the next sibling:

```swift
extension Message.Metadata {
    struct Author: Sendable {
        let name: String
    }
}

extension Message.Metadata.Author: CustomStringConvertible {
    var description: String {
        name
    }
}
```

### File-Scoped Constants

For file-local constants, extend primitive types with `fileprivate`. This keeps magic numbers out of the type's member list and enables clean dot-syntax at call sites:

```swift
// ❌ BAD: Constants pollute type namespace
final class TypingDotsView: UIView {
    private static let dotDiameter: CGFloat = 4
    private static let numberOfDots = 3
}

// ✅ GOOD: Constants on primitive types
final class TypingDotsView: UIView {
    override var intrinsicContentSize: CGSize {
        CGSize(width: .dotDiameter * CGFloat(.numberOfDots), height: .dotDiameter)
    }
}

extension CGFloat {
    fileprivate static let dotDiameter: CGFloat = 4
}

extension Int {
    fileprivate static let numberOfDots = 3
}
```

## File Structure

Organize files in this order:

1. Type definition (with synthesized protocol conformances)
2. Protocol conformance extensions with custom implementations (lexicographic)
3. Nested type extensions (lexicographic)
4. File-scoped constant extensions
5. `#if DEBUG` previews

Previews are development aids, not implementation—they always come last.

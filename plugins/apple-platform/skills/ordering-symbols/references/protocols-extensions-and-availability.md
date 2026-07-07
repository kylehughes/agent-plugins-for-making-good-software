# Protocols Extensions and Availability

This reference covers ordering inside protocol declarations, ordering of file-level extensions, and the safety boundaries around conditional compilation and availability.

## Protocol Declaration Order

Inside a `protocol`, use the same preference adapted to protocol requirements:

1. Associated types and type aliases, alphabetical by name.
2. Property requirements, static/type before instance, alphabetical by name.
3. Initializer requirements, alphabetical by canonical initializer signature.
4. Subscript requirements, alphabetical by signature.
5. Method requirements, static/type before instance, alphabetical by base name and then full signature.

Access level is normally inherited from the protocol. `optional` in `@objc` protocols is not a sorting key.

Do not reorder associated types or requirements when later declarations depend on earlier names, documentation intentionally explains them in sequence, Objective-C optional requirements are grouped for a reason, or the protocol is public API whose displayed order is part of generated documentation expectations.

## File-Level Extension Order

At file scope, order extensions for the same extended type in this sequence:

1. Protocol conformance extensions, alphabetical by protocol name.
2. Extensions whose primary purpose is nested types, alphabetical by the first nested type name.
3. Plain implementation extensions, if the file already uses them.

### Protocol Conformance Extensions

Sort conformance extensions by conformed protocol name.

```swift
// ✅ Correct: protocol names are alphabetical.
extension User: Codable {
    init(from decoder: Decoder) throws {
        // ...
    }
}

extension User: Equatable {
    static func == (lhs: User, rhs: User) -> Bool {
        lhs.id == rhs.id
    }
}

extension User: Hashable {
    func hash(into hasher: inout Hasher) {
        hasher.combine(id)
    }
}
```

Rules:

- If an extension conforms to multiple protocols, alphabetize the protocol list and sort the extension by the first protocol in that sorted list.
- Do not split a multi-protocol conformance extension unless explicitly requested and safe.
- For otherwise identical protocol names, use the `where` clause string as a tie-breaker.
- Keep conformance-required members inside the relevant conformance extension unless project code already uses a different convention.
- Each extension body follows the type-level ordering rules.

### Extensions With Nested Types

Sort nested-type extensions by the nested type name. If an extension contains multiple nested types, sort by the first nested type after sorting the nested types inside the extension.

### Plain Implementation Extensions

Do not create plain implementation extensions solely to satisfy ordering. If plain implementation extensions already exist, place them after conformance and nested-type extensions, then sort their contents using the implementation-detail rules.

If multiple plain implementation extensions exist for the same type and same access level, either merge them when safe or sort them by the first contained member name. Preserve separate extensions when they are separated by conditional compilation, availability, comments, generated-code boundaries, or build configuration.

## Conditional Compilation and Availability

Availability and conditional compilation are not sort keys. They are safety boundaries.

Rules:

- A declaration annotated with `@available(...)` is sorted by its normal category/access/name when moving it is safe.
- Do not reorder declarations across `#if`, `#elseif`, `#else`, or `#endif` boundaries unless the entire conditional region moves intact and remains correct.
- Do not reorder runtime availability branches such as `if #available(iOS 26.0, *) { ... } else { ... }` merely for lexicographic order.
- Preserve fallback paths required by the deployment target. In an iOS 16+ codebase, newer iOS 17–27 APIs must remain guarded when used in code that can run on older supported OS versions.
- Do not assume beta APIs are stable. Keep beta-only declarations and fallbacks guarded exactly as needed by the project.

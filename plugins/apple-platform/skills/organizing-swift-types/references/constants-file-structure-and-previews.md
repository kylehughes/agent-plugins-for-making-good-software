# Constants, File Structure, and Previews

Reference for file-scoped constants, overall file ordering, and preview placement.

## File-Scoped Constants

For file-local implementation constants, extend primitive or value types with `fileprivate static let`. This keeps magic values out of the primary type's member list and enables contextual dot syntax at call sites.

Use this pattern for constants that are implementation details of the file, not part of the type's conceptual API.

```swift
// ❌ BAD: constants pollute the primary type
final class TypingDotsView: UIView {
    private static let dotDiameter: CGFloat = 4
    private static let numberOfDots = 3
}

// ❌ BAD: namespace bucket
private enum Constants {
    static let dotDiameter: CGFloat = 4
    static let numberOfDots = 3
}

// ✅ GOOD
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

Rules:

- Use `fileprivate static let`; do not use `static var` for constants.
- Extend the value type used at the call site: `CGFloat` for dimensions, `Double` for floating-point values, `Int` for counts, `TimeInterval` or `Duration` for time, `String` for local keys or identifiers, `CGSize`/`CGPoint`/`UIEdgeInsets` for geometry values when contextual dot syntax is useful.
- Keep these constants file-private. Do not make primitive constants internal or public.
- Use semantic names that will not collide inside the file.
- Sort primitive constant extensions by type name, then constants by constant name.
- Do not extract meaningless literals such as `0`, `1`, `true`, `false`, `nil`, or empty collections unless the value has domain meaning or is repeated.
- If a constant is true API of a domain type, put it in a static constants extension on that domain type instead of a primitive extension.

```swift
// ✅ GOOD: true type API, not merely a file-local magic number
extension Avatar.Size {
    static let compact = Avatar.Size(points: 32)
    static let regular = Avatar.Size(points: 44)
}
```

## File Structure

A normal type file should use this order:

```swift
import Foundation
import UIKit

[primary type declaration]

[custom protocol conformance extensions for the primary type]

[constrained generic extensions for the primary type]

[nested type extension subtree]

[static constants extensions for non-primitive/domain types]

[file-scoped primitive constant extensions]

#if DEBUG
[previews]
#endif
```

Detailed rules:

- Prefer one primary production type per file.
- Name the file after the primary type.
- Additional top-level production types usually deserve their own files. If a helper is owned by the primary type, make it nested.
- Keep same-type implementation members in the primary declaration, not extensions.
- Keep external-type extensions in dedicated files unless they are file-local constants or tightly coupled local helpers.
- Do not add MARK comments between sections.
- Conditional compilation should be as narrow as possible. Do not wrap an entire file in `#if` when one declaration can be gated.
- Availability-gated declarations stay in their structural location; do not move them to an availability section.

## Previews

Previews are development aids, not implementation. They always come last.

```swift
#if DEBUG
#Preview {
    ProfileViewController()
}
#endif
```

Rules:

- Wrap previews in `#if DEBUG`.
- Put previews after all implementation, nested types, conformances, and constants.
- Do not add MARK comments before previews.
- If `#Preview` is incompatible with the target's iOS 16 deployment configuration, use the project's established preview fallback or an availability-isolated preview shim. Do not raise the deployment target to satisfy previews.

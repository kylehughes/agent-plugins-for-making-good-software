# Access Control and Modifiers

Reference for choosing access levels and ordering declaration modifiers.

## Access Control

Use the most restrictive access level that compiles and accurately represents the API boundary.

- Omit `internal`. It is the default and explicit `internal` is noise.
- Use `private` for implementation details that do not need same-file cross-type access.
- Use `fileprivate` only when same-file cross-type access is genuinely required, and for file-scoped primitive constants required by this skill.
- Use `package` only for Swift package internals that must cross target/module boundaries inside the same package.
- Use `public` only for API exposed outside the module.
- Use `open` only when external modules are meant to subclass or override. `open` is a design promise, not a convenience.
- Prefer `private(set)` over a wider setter.
- Do not widen access to make organization easier. Move code instead.
- Do not widen access just because tests want to reach an implementation detail. Prefer testing through public behavior or module test mechanisms already used by the project.

Classes are `final` by default.

```swift
// ✅ GOOD
final class SettingsViewController: UIViewController {
    private(set) var selectedUserID: User.ID?
}

// ✅ GOOD: public API, still not subclassable
public final class ImagePipeline: Sendable {
    public init() { }
}

// ❌ BAD: internal is redundant, class is subclassable by accident
internal class ImagePipeline {
    internal init() { }
}
```

Omit `final` only when the class is intentionally designed for inheritance or a framework/runtime requirement prevents finalization. UIKit, SwiftUI, Foundation, XCTest, and Objective-C interop do not by themselves justify omitting `final`.

## Declaration Modifiers

Attributes come first. Access control comes first among declaration modifiers. Omit `internal`.

Preferred forms:

```swift
@MainActor
public final class ProfileViewController: UIViewController { }

@available(iOS 17.0, *)
private struct NewRenderer { }

public private(set) var state: State
private static let reuseIdentifier = "Cell"
override func viewDidLoad()
public override func layoutSubviews()
mutating func reset()
```

Use these modifier orders unless the compiler requires otherwise:

```swift
[attributes]
[access] final class Name
[attributes]
[access] struct|enum|actor|protocol Name
[attributes]
[access] [setter access] [override] [static|class] let|var name: Type
[attributes]
[access] [override] [static|class] [mutating|nonmutating] func name(...)
[attributes]
[access] convenience|required init(...)
```

Favor `let` over `var`. Use `var` only for actual mutation, computed properties, property wrappers that require it, or framework overrides that must be mutable.

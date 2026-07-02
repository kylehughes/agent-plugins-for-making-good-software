---
name: organizing-swift-types
description: Defines Swift 6.3 conventions for organizing iOS Swift types across iOS 16 through the latest stable iOS 26 SDKs, with iOS 27 treated as beta. Use when writing or editing Swift type declarations, choosing access control, ordering modifiers, deciding whether an extension is legitimate, placing protocol conformances, organizing nested types, handling file-scoped constants, applying availability guards, placing previews, or removing prohibited organizational patterns such as MARK comments, organizational extensions, unnecessary self, global constants, and Constants namespaces.
---

# Swift Type Organization Conventions

## Scope and Assumptions

These conventions apply to Swift source for iOS projects.

- Target Swift 6.3. Do not write compatibility branches for older Swift compilers or older Swift language syntax.
- Assume Swift 6 language mode unless project settings explicitly prove otherwise. Do not optimize style for Swift 5-era limitations.
- Target iOS 16 as the minimum runtime unless a file or target explicitly states a higher minimum.
- Support the latest stable iOS 26 SDKs. Treat iOS 27 as beta: do not use iOS 27-only APIs, beta SDK behavior, or Swift 6.4+ syntax unless the user explicitly asks for beta code.
- A newer compiler or SDK does not make newer OS APIs available on iOS 16. Guard every post-iOS-16 API at runtime or isolate it behind an available declaration.
- This skill governs organization. For detailed symbol ordering inside a declaration, apply the `ordering-symbols` skill when available. If that skill is unavailable, use deterministic ordering: compiler-required declarations first, then lexicographic order by symbol name. Never compensate for missing ordering rules with MARK comments.

When a rule here conflicts with compiler correctness, compiler correctness wins. Make the smallest possible exception and preserve the rest of the structure.

## Required Outcome

Every generated or edited Swift file should converge toward this shape:

1. Imports.
2. Primary type declaration, including synthesized conformances.
3. Custom protocol conformance extensions, one protocol per extension, sorted lexicographically by protocol name.
4. Legitimate constrained extensions for the primary type, sorted lexicographically by constraint text.
5. Nested type extensions, one nested type per extension, sorted lexicographically by nested type name, with each nested type's subtree completed before moving to the next sibling.
6. Static constants extensions for non-primitive types, when the constants are true type API.
7. File-scoped primitive constant extensions using `fileprivate static let`.
8. `#if DEBUG` previews last.

The file should not contain MARK comments, organizational extensions, unnecessary `self`, global implementation constants, `private enum Constants`, `private struct Constants`, `private enum Metrics`, or equivalent namespace buckets.

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

## Availability and Version Spanning

The default deployment span is iOS 16 through stable iOS 26. Availability handling is mandatory for APIs introduced after iOS 16.

- Use `if #available(iOS X.Y, *)` for runtime behavior branches.
- Use `@available(iOS X.Y, *)` when an entire declaration is unusable before that OS.
- Prefer the narrowest viable availability boundary. Do not wrap an entire file when one method or helper can be isolated.
- Always provide an iOS 16-compatible path unless the enclosing declaration is explicitly unavailable before a newer OS.
- Do not use `UIDevice.current.systemVersion`, string comparisons, build numbers, or beta OS checks for API availability.
- Use `#if canImport(...)` for optional modules only, not for OS-version gating.
- Do not add `#if swift(...)` or `#if compiler(...)` branches for old Swift versions. Swift 6.3 is the target.
- Do not introduce iOS 27 beta APIs unless explicitly requested. When requested, isolate beta usage with `@available(iOS 27.0, *)` or `if #available(iOS 27.0, *)`, and keep a stable iOS 16-26 path.
- SDK-provided macros and property wrappers still obey framework availability. A Swift 6.3 compiler does not make an iOS 17+ framework API deployable to iOS 16.

Stored properties need special care. If a stored property has a type that is only available on iOS 17+, the containing type effectively cannot be used on iOS 16. Isolate the newer type in an available helper or erase the storage behind an iOS-16-safe abstraction.

```swift
// ❌ BAD: newer API used with no iOS 16 path
func configure() {
    useFeatureIntroducedAfterIOS16()
}

// ✅ GOOD: newer API is guarded and the fallback remains explicit
func configure() {
    if #available(iOS 17.0, *) {
        useFeatureIntroducedAfterIOS16()
    } else {
        useIOS16Fallback()
    }
}
```

## Prohibited Patterns

### No MARK Comments

Do not add `// MARK:`, `// MARK: -`, section headers, lifecycle banners, protocol banners, or visual separators.

```swift
// ❌ BAD
// MARK: - UICollectionViewDataSource

// ❌ BAD
// MARK: Private Helpers
```

Deterministic file layout and symbol ordering replace navigational comments. MARK comments become stale and encourage organizational extensions.

Explanatory comments and documentation comments are still allowed when they explain non-obvious behavior, public API, workarounds, or availability fallbacks. Do not use comments as structure.

### No Organizational Extensions

An extension is organizational when it exists only to group members that could be written in the primary declaration. Organizational extensions are prohibited.

```swift
// ❌ BAD
extension ProfileViewController {
    private func configureView() { }
}

// ❌ BAD
private extension ProfileViewController {
    func bind() { }
}

// ❌ BAD
extension ProfileViewController {
    @objc private func didTapSaveButton() { }
}
```

Move ordinary properties, initializers, lifecycle overrides, actions, and helper methods into the primary declaration.

```swift
// ✅ GOOD
final class ProfileViewController: UIViewController {
    override func viewDidLoad() {
        super.viewDidLoad()
        configureView()
        bind()
    }

    @objc private func didTapSaveButton() { }

    private func bind() { }

    private func configureView() { }
}
```

### No Unnecessary `self`

Use `self` only when required by Swift or when it materially changes capture semantics.

Required or appropriate cases include:

- Disambiguating an instance member from a parameter or local variable with the same name.
- Satisfying Swift's explicit-self requirement in escaping closures.
- Working with weak/unowned captures where `self` must be explicit before rebinding.
- Referring to `Self`/`self` as a value or type where the language requires it.

```swift
// ❌ BAD
init(name: String) {
    self.name = name
    self.isActive = true
    self.configureDefaults()
}

// ✅ GOOD
init(name: String) {
    self.name = name
    isActive = true
    configureDefaults()
}
```

In closures, be explicit only as long as necessary.

```swift
// ✅ GOOD
loader.load { [weak self] result in
    guard let self else { return }
    handle(result)
}
```

Do not use `self.` for symmetry, style, or visual scanning.

### No Constants Namespaces

Do not introduce local namespace buckets for constants.

```swift
// ❌ BAD
private enum Constants {
    static let dotDiameter: CGFloat = 4
    static let numberOfDots = 3
}

// ❌ BAD
private enum Metrics {
    static let avatarSize: CGFloat = 40
}
```

Use file-scoped primitive constant extensions instead, as described below.

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

## Editing Procedure for Agents

When editing Swift under this skill:

1. Identify the primary type and minimum deployment target.
2. Collapse organizational extensions into the primary declaration.
3. Keep synthesized, marker, and empty conformances on the primary declaration.
4. Move custom conformance implementations into one-protocol extensions.
5. Move nested types into one-nested-type extensions and complete each nested subtree before moving to siblings.
6. Replace `private enum Constants`, `private struct Constants`, global implementation constants, and type-polluting private static constants with `fileprivate static let` primitive extensions unless the constant is true type API.
7. Remove MARK comments and visual section comments.
8. Remove unnecessary `self` while preserving required disambiguation and capture semantics.
9. Add or preserve iOS availability guards for every post-iOS-16 API.
10. Place previews last inside `#if DEBUG`.

Do not create churn outside the touched file unless moving a legitimate external-type extension or top-level production type into its own file is necessary for correctness or explicitly requested.

## Complete Shape Example

```swift
import UIKit

@MainActor
final class TypingDotsView: UIView {
    private let firstDotView = UIView()
    private let secondDotView = UIView()
    private let thirdDotView = UIView()

    override var intrinsicContentSize: CGSize {
        CGSize(width: .dotDiameter * CGFloat(.numberOfDots), height: .dotDiameter)
    }

    override init(frame: CGRect) {
        super.init(frame: frame)
        configureView()
    }

    required init?(coder: NSCoder) {
        super.init(coder: coder)
        configureView()
    }

    private func configureView() {
        [firstDotView, secondDotView, thirdDotView].forEach(addSubview)
    }
}

extension TypingDotsView: CAAnimationDelegate {
    func animationDidStop(_ anim: CAAnimation, finished flag: Bool) {
        guard flag else { return }
        invalidateIntrinsicContentSize()
    }
}

extension TypingDotsView {
    enum AnimationPhase: CaseIterable, Sendable {
        case appearing
        case disappearing
        case idle
    }
}

extension CGFloat {
    fileprivate static let dotDiameter: CGFloat = 4
}

extension Int {
    fileprivate static let numberOfDots = 3
}

#if DEBUG
#Preview {
    TypingDotsView()
}
#endif
```

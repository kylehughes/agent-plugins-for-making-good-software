---
name: ordering-symbols
description: Defines the canonical order for Swift 6.3 symbols in iOS projects — type aliases, nested types, enum cases, stored properties, initializers, lazy/computed properties, subscripts, and methods — using access-level grouping and lexicographic sorting wherever reordering is semantics-preserving. Use when writing new Swift types, adding members to existing structs/classes/actors/enums/protocols/extensions, reorganizing or refactoring Swift code, deciding where to place a new property or method, or reviewing member ordering in pull requests.
---

# Swift Lexicographic Symbol Ordering

## Objective

Maintain deterministic, lexicographic ordering of Swift declarations wherever reordering is semantics-preserving. Consistent member ordering removes subjective placement decisions and makes types scannable: readers should know where to find a symbol without knowing its implementation.

This skill enforces the existing preference: order by declaration category, access level, static-vs-instance, and name. It does not introduce semantic grouping as an alternative to lexicographic ordering.

## Version and Platform Assumptions

- Use current Swift syntax and language behavior. Swift 6.3 is the relevant language version.
- iOS projects commonly span iOS 16 through the latest stable SDKs, with newer/beta APIs guarded as needed. Availability gates are safety boundaries, not sorting keys.
- Do not preserve old Swift-era conventions for compatibility with versions below the stated deployment target.
- Do not remove, weaken, or reorder availability fallbacks merely to improve symbol ordering.

## Non-Negotiable Safety Rule

Only reorder sibling declarations or sibling statements when it is safe to do so. Never reorder if the change could affect compilation, overload resolution, initialization order, synthesized API shape, runtime behavior, UI order, availability behavior, reflection, serialization, generated code, or tests.

When editing existing code, move a declaration together with all directly attached documentation comments, attributes, property wrappers, macros, conditional-compilation directives that guard only that declaration, and inline comments that describe that declaration.

If safety is uncertain, preserve the current order rather than guessing.

## Canonical Sort Keys

When a declaration is safe to reorder, compare it using these keys in order:

1. Major declaration category.
2. Access level, where applicable.
3. Static/type member before instance member, where applicable.
4. Declaration kind, where applicable.
5. Lexicographic name/signature.
6. Original order as a stable tie-breaker.

### Access-Level Order

Use this access order, from broadest to narrowest:

1. `open`
2. `public`
3. `package`
4. `internal` / omitted access modifier
5. `fileprivate`
6. `private`

Rules:

- Omitted access is `internal`, unless inherited from an enclosing `private`, `fileprivate`, `package`, `public`, or `open` declaration/extension.
- Sort a declaration by its getter/access level, not by setter-only access. For example, `public private(set) var title` belongs in the `public` bucket, and `private(set) var count` belongs in the `internal` bucket.
- Access modifiers on extensions affect unannotated members inside the extension.
- Access level is primary only where the ordering rules below say it is primary. Do not globally sort every declaration by access before category.

### Name Comparison

Use deterministic code-point lexicographic ordering for the comparison string.

- For properties and enum cases, compare the declared identifier.
- For type aliases, associated types, nested types, classes, structs, actors, enums, and protocols, compare the declared type name.
- For methods, compare the base name first. Use the full signature only as a tie-breaker among overloads.
- For initializers, compare the canonical initializer signature, such as `init()`, `init(coder:)`, `init(from:)`, `init(id:name:)`.
- For subscripts, compare `subscript` signatures after named computed properties and before methods.
- For operator functions, compare the operator token as the method base name.
- Ignore backticks around escaped identifiers for comparison, but otherwise treat every character literally. `_`, `$`, digits, and capitalization participate in the sort.
- Attributes and modifiers are not sort keys unless they change access level or static/type-member status. Ignore `@MainActor`, `@objc`, `@IBAction`, `@IBOutlet`, `@Published`, `@State`, `@Environment`, `@Observable`, `@discardableResult`, `final`, `override`, `required`, `convenience`, `mutating`, `nonmutating`, `async`, `throws`, `rethrows`, `isolated`, `nonisolated`, and similar annotations for ordering.

## Type Declaration Order

Apply these rules inside `class`, `struct`, `actor`, `enum`, and concrete extension bodies. Apply the protocol-specific variant below inside protocol declarations.

### 1. Type-Level Declarations

Place type-level declarations before value-level members.

Order:

1. `typealias` declarations, alphabetical by alias name.
2. Nested types (`struct`, `class`, `actor`, `enum`, `protocol`), alphabetical by nested type name.

Each nested type internally follows this skill.

Do not move a nested type if doing so would break access to file-private helpers, conditional-compilation boundaries, macro expansion expectations, or local documentation structure.

### 2. Enum Cases

Enum cases belong after type-level declarations and before stored properties.

Sort enum cases alphabetically only when safe. Reordering enum cases is often not safe because it can change synthesized `CaseIterable.allCases` order, implicit raw values, UI ordering, persistence expectations, tests, analytics values, switch readability, and human-facing semantics.

Treat enum case reordering as safe only when all of these are true:

- Cases have explicit raw values if raw values exist.
- The enum does not rely on synthesized case order, or all dependent call sites/tests are updated.
- The case order is not user-facing, serialized, persisted, reflected, or part of a protocol/API contract.
- No comments or sectioning indicate deliberate semantic ordering.

If any condition is unclear, preserve case order.

When safe to sort:

```swift
// ✅ Safe only if case order is not semantically observed.
enum SortDirection: String {
    case ascending = "ascending"
    case descending = "descending"
}
```

### 3. Stored Properties

Stored properties come after type-level declarations and enum cases, and before initializers.

Group order:

1. `static let`
2. `static var`
3. instance `let`
4. instance `var`

Within each group:

1. Access level: `open` → `public` → `package` → `internal` → `fileprivate` → `private`
2. Alphabetical by identifier

Important classification rules:

- Lazy properties are not part of this stored-property section. They are implementation details.
- Property-wrapper declarations such as `@State`, `@Binding`, `@Environment`, `@Published`, `@FocusState`, `@AppStorage`, and `@NSManaged` are sorted by the declared property identifier, not by the wrapper or generated backing storage.
- Stored properties with observers (`willSet` / `didSet`) remain stored properties unless they use an explicit `get` or `set` accessor.
- A property with `get`, `set`, `_read`, `_modify`, or a computed body is a computed property, not a stored property.
- Static stored properties are sorted as stored properties even though their initialization is lazy.

Stored property reordering is high-risk. Preserve order when declaration order affects synthesized memberwise initializer parameter order, default-value side effects, property-wrapper initialization order, reflection, memory/layout assumptions, persistence, generated code, or snapshot tests.

### 4. Initializers and Deinitializers

Initializers come after stored properties and before implementation details.

Order initializers by:

1. Access level: `open` → `public` → `package` → `internal` → `fileprivate` → `private`
2. Canonical initializer signature

Rules:

- `required`, `convenience`, `override`, `@MainActor`, `async`, `throws`, and failable spelling (`init?`, `init!`) are not primary sort keys. Use them only as tie-breakers when signatures are otherwise identical.
- `deinit` has no access level. Place `deinit` after all initializers and before implementation details.
- Never reorder statements inside an initializer in a way that changes initialization requirements. Required `super.init(...)`, `self.init(...)`, stored-property assignments, actor isolation rules, and early returns must stay valid.

### 5. Implementation Details

Implementation details come after initializers/deinitializers.

Access level is the primary sort key across all implementation details:

1. `open`
2. `public`
3. `package`
4. `internal`
5. `fileprivate`
6. `private`

Within each access level, order by kind:

1. Lazy properties
2. Computed properties
3. Subscripts
4. Methods

Within each kind:

1. Static/type members (`static` and `class`) before instance members.
2. Alphabetical by identifier or signature.

This means a `public` computed property comes before a `private` lazy property, and an `internal` method comes before a `private` lazy property. Do not sort all lazy properties before all computed properties globally; sort by access level first in the implementation-details section.

Classification examples:

- `lazy var imageLoader = ImageLoader()` → lazy property.
- `var body: some View { ... }` → computed property.
- `static var previewValue: Self { ... }` → static computed property.
- `class var supportsSecureCoding: Bool { ... }` → type computed property.
- `subscript(id: ID) -> Value { ... }` → subscript.
- `@IBAction func didTapSave(_ sender: UIButton)` → method.
- `static func == (...) -> Bool` → static method, sorted by operator token.

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

## Function and Initializer Parameters

Do not apply lexicographic ordering to function parameters, initializer parameters, closure parameters, tuple elements used as API shape, or result-builder child order.

Parameters should be ordered semantically based on role and relationships:

1. Identity: `id` and identifiers typically come first.
2. Related groups: keep conceptually related parameters together, such as `firstName`, `lastName`, `fullName`.
3. Primary data: the main subject/content being operated on.
4. Configuration: settings that modify behavior.
5. Dependencies: required collaborators and services.
6. Optionals/defaulted parameters: values with sensible defaults.
7. Closures: completion handlers, callbacks, and builder closures go last.

When parameters have no clear semantic relationship, use lexicographic ordering only as a tiebreaker.

```swift
// ✅ Good: semantic parameter ordering.
init(
    id: UUID,
    firstName: String,
    lastName: String,
    fullName: String,
    profilePhotoURL: URL?,
    completion: @escaping () -> Void
)

func send(
    _ content: String,
    with attachments: [Attachment],
    isImportant: Bool,
    completion: @escaping (Result) -> Void
) async

// ❌ Bad: lexicographic parameter ordering overrides semantics.
init(
    completion: @escaping () -> Void,
    firstName: String,
    fullName: String,
    id: UUID,
    lastName: String,
    profilePhotoURL: URL?
)
```

## Ordering Inside Function, Initializer, and Closure Bodies

Inside executable bodies, sort only contiguous independent statements.

Safe targets for sorting:

- Independent `let` / `var` declarations, alphabetical by declared identifier.
- Independent assignment/configuration statements, first by receiver name, then by property/method name.
- Independent array or dictionary literal elements when order is not semantically observed.
- Constraint lists such as `NSLayoutConstraint.activate([...])`, sorted by primary item/receiver, then anchor/attribute, then relation.
- Test fixture declarations when no setup sequence is required.

Never sort across:

- Data dependencies or first-use dependencies.
- Side effects, `await`, `try`, `defer`, locking, transactions, animations, notifications, logging, metrics, or lifecycle calls unless independence is obvious.
- `guard`, `if`/`else`, `switch`, `catch`, `defer`, loops, task groups, or cancellation handlers.
- Result builders, SwiftUI `body` child views, `VStack`/`HStack`/`ZStack` contents, menus, table/collection sections, navigation routes, toolbar items, accessibility order, or any UI sequence.
- Arrays used as displayed data, ordered commands, ordered validation steps, ordered middleware, ordered tests, or ordered fallback chains.

```swift
// ✅ Correct: independent declarations and independent assignments are sorted.
func setupUI() {
    let backButton = UIButton()
    let headerLabel = UILabel()
    let subtitleLabel = UILabel()

    backButton.setTitle("Back", for: .normal)
    headerLabel.text = "Welcome"
    subtitleLabel.text = "Please sign in"
}

// ✅ Correct: dependencies preserve original order.
func processUser() {
    let user = fetchUser()
    let name = user.name
    let validated = validate(name)

    updateUI(with: validated)
}
```

## Formatting Enforcement

Always use multi-line formatting for braced constructs. Do not use single-line braced forms.

Use this:

```swift
var isValid: Bool {
    !email.isEmpty
}

guard isValid else {
    return
}

let handler = {
    refresh()
}
```

Do not use this:

```swift
var isValid: Bool { !email.isEmpty }

guard isValid else { return }

let handler = { refresh() }
```

Single-statement bodies are acceptable only when the braces remain multi-line.

## Comments, MARKs, and Documentation

- Move documentation comments and attached comments with the declaration they document.
- Do not let `// MARK:` sections override the canonical ordering rules.
- Remove or update stale `// MARK:` headings if reordering makes them inaccurate.
- Do not add new `// MARK:` sections merely to justify a noncanonical order.
- Preserve generated-code comments, copyright headers, lint directives, formatter directives, and warning-suppression comments exactly unless explicitly asked to edit them.

## Complete Type Example

```swift
struct UserViewModel {
    typealias Identifier = UUID

    enum Mode {
        case compact
        case expanded
    }

    static let defaultName = "Guest"
    static var registrationCount = 0

    public let id: Identifier

    let name: String

    private let apiClient: APIClient

    var email: String
    var isActive: Bool

    public init(id: Identifier, name: String, email: String, isActive: Bool, apiClient: APIClient) {
        self.id = id
        self.name = name
        self.apiClient = apiClient
        self.email = email
        self.isActive = isActive
    }

    init(name: String, apiClient: APIClient) {
        self.id = UUID()
        self.name = name
        self.apiClient = apiClient
        self.email = ""
        self.isActive = true
    }

    public var displayName: String {
        name.isEmpty ? Self.defaultName : name
    }

    public func refresh() async throws {
        try await load()
    }

    var isValid: Bool {
        !email.isEmpty && isActive
    }

    func activate() {
        isActive = true
    }

    func deactivate() {
        isActive = false
    }

    private lazy var cache = UserCache()

    private var hasCachedValue: Bool {
        cache.contains(id)
    }

    private func load() async throws {
        // ...
    }
}
```

Notes about the example:

- Stored properties use storage kind first, then access level.
- Implementation details use access level first, then lazy/computed/method kind.
- The `private lazy var cache` appears after internal methods because access level is primary inside implementation details.

## Application Strategy

When writing or editing Swift code:

1. Identify the smallest declaration scope or statement block that can be safely reordered.
2. Classify each sibling declaration by category.
3. Apply the relevant access-level, static-vs-instance, kind, and name keys.
4. Preserve comments, attributes, wrappers, macros, and conditional guards with their declarations.
5. Check safety boundaries: initialization, enum order, property-wrapper order, availability, generated code, UI/result-builder order, and side effects.
6. Apply multi-line braced formatting.
7. Preserve original order for anything not proven safe.

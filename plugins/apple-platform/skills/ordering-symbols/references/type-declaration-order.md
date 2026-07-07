# Type Declaration Order

This reference covers the ordering rules for declarations inside `class`, `struct`, `actor`, `enum`, and concrete extension bodies.

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

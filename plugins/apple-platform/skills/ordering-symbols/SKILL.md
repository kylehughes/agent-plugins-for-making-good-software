---
name: ordering-symbols
description: Defines the canonical order for members within Swift types — properties, initializers, computed properties, and methods — using access-level grouping and lexicographic sorting. Use when writing new Swift types, adding members to existing structs/classes/enums, reorganizing or refactoring Swift code, deciding where to place a new property or method, or reviewing member ordering in pull requests.
---

# Swift Lexicographic Symbol Ordering

## Overview

Maintain deterministic, lexicographic ordering of members within Swift types wherever reordering is semantics-preserving. Consistent member ordering eliminates subjective decisions about "where does this go?" and makes types scannable — readers always know where to find a given member.

## When to Apply

Apply lexicographic ordering when:
- Writing new Swift types (classes, structs, enums, extensions)
- Refactoring or reorganizing existing Swift code
- Reviewing code to ensure consistent organization
- Adding new members to existing types

**Critical:** Only reorder when it's safe to do so. Never reorder if it would break compilation, change runtime behavior, or violate required ordering (e.g., `super.init()` must remain in its required position).

## When NOT to Apply

### Function and Initializer Parameters

**DO NOT apply lexicographic ordering to function parameters or initializer parameters.**

Parameters should be ordered semantically based on their role and relationships:

1. **Identity** — `id` and identifiers typically come first
2. **Related groups** — Keep conceptually related parameters together (e.g., `firstName`, `lastName`, `fullName`)
3. **Primary data** — The main subject or content being operated on
4. **Configuration** — Settings that modify behavior
5. **Dependencies** — Required collaborators and services
6. **Optionals with defaults** — Parameters that have sensible defaults
7. **Closures** — Completion handlers and callbacks go last

When parameters have no clear semantic relationship, fall back to lexicographic ordering as a tiebreaker.

```swift
// ✅ GOOD: Semantic parameter ordering
init(
    id: UUID,                                 // Identity first
    firstName: String,                        // Related name components
    lastName: String,                         //   grouped together
    fullName: String,
    profilePhotoURL: URL?,                    // Other properties
    completion: @escaping () -> Void          // Closures last
)

func send(
    _ content: String,                        // Primary data
    with attachments: [Attachment],           // Associated data
    isImportant: Bool,                        // Configuration
    completion: @escaping (Result) -> Void    // Closure last
) async

// ❌ BAD: Lexicographic parameter ordering
init(
    completion: @escaping () -> Void,         // Closure should be last
    firstName: String,
    fullName: String,
    id: UUID,                                 // Identity buried in middle
    lastName: String,                         // Name components scattered
    profilePhotoURL: URL?
)
```

## Ordering Rules

### 1. Within Type Declarations (class / struct / enum)

Order members in this sequence:

1. **typealiases** – alphabetical by name

2. **stored properties**
   - Group order: static let → static var → instance let → instance var
   - Within each group: public → internal → fileprivate → private
   - Within each access level: alphabetical by identifier
   - Importantly: NOT LAZY PROPERTIES.

3. **initializers** (`init` and `deinit`)
   - Order by access level first: public → internal → fileprivate → private
   - Within each access level: alphabetical (e.g., `init()` before `init(coder:)`)

4. **implementation details** (lazy properties, computed properties, methods)

   **Access level is the primary sort key** across all implementation details:
   - public → internal → fileprivate → private

   **Within each access level**, order by member kind:
   - Lazy properties → computed properties → methods
   - Static before instance within each kind
   - Alphabetical within each kind

   This means a `public` computed property comes before a `private` lazy property, and an `internal` method comes before a `private` lazy property.

### 2. File-Level Extensions

Order extensions at file scope:

1. **Protocol conformance extensions** – alphabetical by protocol name
   - Each extension internally follows the type-level ordering rules above

2. **Extensions with nested types** – alphabetical by the inner type name

### 3. Inside Function/Initializer Bodies

When statements are independent (no data or side-effect dependencies):
- Sort constant/variable declarations (`let`/`var`) lexicographically
- Sort array/dictionary literal elements (e.g., in `NSLayoutConstraint.activate([...])`)
  - Sort first by variable/receiver name
  - Then by called method/selector

**Never reorder** when there are dependencies that would change behavior.

### 4. General Notes

- Use standard ASCII/Unicode code-point ordering for "alphabetical"
- Correctness takes precedence: preserve original order if reordering would break the code
- When uncertain about safety, ask for confirmation rather than risking incorrect reordering
- **Always use multi-line formatting** for braced constructs (computed properties, closures, guard/if statements, methods). Never use single-line forms like `var x: Int { 0 }` or `guard condition else { return }`

## Examples

### Type Declaration

```swift
// ✅ CORRECT
struct User {
    // 1. typealiases (alphabetical)
    typealias Identifier = UUID

    // 2. stored properties (static let → static var → instance let → instance var)
    static let defaultName = "Guest"
    static var registrationCount = 0

    let id: UUID
    let name: String

    var email: String
    var isActive: Bool

    // 3. initializers (access level, then alphabetical)
    init(id: UUID, name: String, email: String, isActive: Bool) {
        self.id = id
        self.name = name
        self.email = email
        self.isActive = isActive
    }

    init(name: String) {
        self.id = UUID()
        self.name = name
        self.email = ""
        self.isActive = true
    }

    // 4a. computed properties (before methods)
    var displayName: String {
        name.isEmpty ? Self.defaultName : name
    }

    var isValid: Bool {
        !email.isEmpty && isActive
    }

    // 4b. methods (alphabetical)
    mutating func activate() {
        isActive = true
    }

    mutating func deactivate() {
        isActive = false
    }
}
```

### Access Level Ordering

```swift
// ✅ CORRECT
class ViewModel {
    // Stored properties: public → internal → private, alphabetical within each
    public let title: String

    let subtitle: String

    private let apiClient: APIClient

    // Implementation details: access level is primary sort key
    // public lazy → public computed → public methods
    public lazy var formattedTitle: String = title.uppercased()

    public var isLoading: Bool {
        state == .loading
    }

    public func load() {
        // ...
    }

    public func refresh() {
        // ...
    }

    // internal lazy → internal computed → internal methods
    lazy var cache: Cache = Cache()

    var hasContent: Bool {
        !items.isEmpty
    }

    func handleError(_ error: Error) {
        // ...
    }

    func validateInput() {
        // ...
    }

    // private lazy → private computed → private methods
    private lazy var items: [Item] = []

    private var state: State {
        .idle
    }

    private func fetchData() {
        // ...
    }

    private func parseResponse() {
        // ...
    }
}
```

### Protocol Conformances

```swift
// ✅ CORRECT - Alphabetical by protocol name
extension User: Codable {
    // Codable implementation following internal ordering rules
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

Note: The `Equatable` and `Hashable` implementations above are single-statement bodies, which is acceptable. The multi-line rule applies to the braces being on separate lines, not to requiring multiple statements.

### Function Body - Safe Reordering

```swift
// ✅ CORRECT - Independent statements sorted alphabetically
func setupUI() {
    let backButton = UIButton()
    let headerLabel = UILabel()
    let subtitleLabel = UILabel()

    backButton.setTitle("Back", for: .normal)
    headerLabel.text = "Welcome"
    subtitleLabel.text = "Please sign in"
}
```

### Function Body - Preserve Dependencies

```swift
// ✅ CORRECT - Dependent statements NOT reordered
func processUser() {
    let user = fetchUser()      // Must come first
    let name = user.name        // Depends on user
    let validated = validate(name)  // Depends on name
    updateUI(with: validated)   // Depends on validated
}
```

## Application Strategy

When writing or editing Swift code:

1. **Start with the structure** - Place members in the correct category order (typealiases → properties → initializers → computed properties → methods)

2. **Apply access level ordering** - Within each category, group by access level (public → internal → fileprivate → private)

3. **Sort alphabetically** - Within each access level group, sort members alphabetically by name

4. **Verify safety** - Before reordering, confirm that the change won't affect behavior or break dependencies

5. **When unsure** - Ask for confirmation rather than making potentially unsafe changes

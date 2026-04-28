---
name: writing-swift
description: >-
  Swift 6 coding standards covering strict concurrency, immutability, optional handling, error patterns,
  protocol design, Swift Testing (not XCTest), documentation style, inline comments, and file organization.
  Use when writing, generating, or reviewing any Swift source code — including new types, extensions,
  protocol conformances, tests, or API documentation. Also use when the user asks about Swift style,
  formatting, naming, file layout, or how to structure Swift declarations.
---

# Swift Coding Standards

These standards target Swift 6 language mode with strict concurrency checking. They prioritize compile-time safety, readability, and consistency.

## Foundational Principles

- Use Swift 6 language mode with strict concurrency checking — this catches data-race bugs at compile time.
- Prefer immutability: declare with `let` unless mutation is genuinely required, because immutable bindings are easier to reason about and safer in concurrent code.
- Never force unwrap optionals (`!`), force try (`try!`), or force cast (`as!`) — these crash at runtime instead of surfacing errors at compile time.
- Never use `// MARK:` sections — file organization and type structure make them unnecessary.
- Document all `public` declarations so that consumers understand intent without reading implementation.
- Maximum line length: 120 characters.
- Indentation: 4 spaces.
- Use Swift Testing for all new tests; never use XCTest.

## Optionals

- Use optional binding (`if let`, `guard let`) to unwrap safely.
- Use `guard let` for early exits that reduce nesting — it keeps the happy path left-aligned.
- Prefer nil-coalescing (`??`) when a sensible default exists.
- Redesign APIs to eliminate the need for forced unwrapping; if a value truly cannot be nil at a given point, restructure so the type system reflects that.

## Error Handling

- Prefer throwing functions over returning optionals or sentinel values — thrown errors carry context about what went wrong, while `nil` is ambiguous.
- Define specific error types (typically an `enum` conforming to `Error`) so callers can handle failures precisely.
- Document error conditions and which errors a function throws.

## Protocol Usage

- Favor protocol composition over class inheritance — composition is more flexible and avoids fragile base class problems.
- Use protocol extensions for default implementations rather than duplicating logic across conforming types.
- Keep protocol requirements minimal and purposeful; a protocol with many requirements is hard to conform to and often indicates it should be split.
- Name capability protocols with `-able` or `-ing` when it improves clarity (e.g., `Sendable`, `Identifiable`).

## Concurrency

- Use structured concurrency (`async`/`await`, task groups, `AsyncSequence`) under Swift 6 strict checking.
- Mark types as `Sendable` when they are safe to pass across concurrency boundaries; prefer value types which get `Sendable` conformance automatically.
- Use actors to protect mutable shared state instead of locks or dispatch queues.
- If applying `@unchecked Sendable`, document the rationale with `/// - Important:` explaining why the compiler cannot verify safety.

## Modern Swift Patterns

- Leverage the type system to make invalid states unrepresentable (e.g., an enum with associated values instead of parallel booleans and optionals).
- Adopt property wrappers where appropriate.
- Use result builders for DSLs when it improves clarity.
- Minimize casting and manual type checks; redesign so the compiler enforces correctness.
- Prefer `isEmpty` over `count == 0` for collections — `isEmpty` is O(1) for all `Collection` types while `count` may not be.
- Avoid magic numbers and strings; use named constants or enums.
- Omit `self.` unless required by the compiler for clarity in closures or to disambiguate.

## Naming Conventions

Follow Apple's Swift API Design Guidelines:

- Use `camelCase` for functions, properties, and variables; `UpperCamelCase` for types, protocols, and enum cases.
- Name methods and functions based on their side effects: phrases without side effects read as noun phrases (`x.distance(to: y)`), phrases with side effects read as imperative verbs (`x.sort()`).
- Name boolean properties as assertions about the receiver: `isEmpty`, `isValid`, `hasChildren`.
- Name protocols describing capabilities with `-able`, `-ible`, or `-ing` suffixes (e.g., `Equatable`, `ProgressReporting`). Name protocols describing what something is with nouns (e.g., `Collection`).

## Access Control

- Default to the most restrictive access level that works. Start `private` and widen only when needed.
- Use `package` access for symbols shared across modules within a Swift package but not intended for external consumers.
- Mark types and members `public` only when they are part of the intended API surface.
- Prefer `private` over `fileprivate` unless the declaration genuinely needs file-wide visibility (e.g., extensions in the same file).

## Testing

- Name test types with a `Tests` suffix (e.g., `DebouncerTests`).
- Use Swift Testing (`import Testing`); never use XCTest.
- Do not prefix test function names with `test` — the `@Test` macro identifies them.
- Use `#expect(...)` for assertions, not XCTest's `XCTAssert` family.
- Use parameterized tests (`@Test(arguments:)`) when testing the same logic across multiple inputs.

### Test Descriptions

The `@Test("...")` description string should assert what the test proves — not merely name the functionality. This makes test output readable as a specification.

- **Describe the assertion**, not the feature.
- **Use declarative sentences** that state what should be true.
- **Function names can be shorter** — the description carries the meaning.

```swift
// ✅ GOOD: Description asserts what the test proves
@Test("Coalescing rapid values delivers only the final value")
func coalescesRapidValues() async throws { }

@Test("Debouncer restarts delivery after being stopped and started")
func restartResumesDelivery() async throws { }

// ❌ BAD: Description just names the feature
@Test("Addition")
func addition() { }

// ❌ BAD: Description repeats the function name
@Test("coalescesRapidValues")
func coalescesRapidValues() { }
```

## Documentation

### Format

- Use `///` for documentation comments (not `/** */` block style).
- Place documentation immediately above the declaration with no blank line between.
- Use backticks around code and symbol references in documentation text.

### Tense and Style

Follow Apple's Swift API Design Guidelines for documentation:

- **Use third-person declarative**: "Creates a...", "Returns a...", "Indicates whether..."
- **Begin with a verb** describing what the symbol does.
- **For properties**: Describe what the property represents, not how to use it.

```swift
// ✅ GOOD: Third person declarative
/// Creates a new user with the specified name and email.
init(name: String, email: String)

/// Returns the formatted display name for the user.
var displayName: String { get }

/// Indicates whether the user has verified their email address.
var isEmailVerified: Bool { get }

// ❌ BAD: Imperative mood
/// Create a new user with the specified name and email.
init(name: String, email: String)
```

### Content

- Document all `public` declarations.
- Document complex `internal` declarations.
- Include parameter and return value documentation.
- Use single‑line parameter docs: `/// - Parameter <name>: <description>`.
- Add usage examples only for exceptionally complex cases unless specified.
- Note threading/concurrency requirements.
- Document error conditions and `throws` clauses.
- If using `@unchecked Sendable`, add `/// - Important:` with rationale.

## Comments

### Inline Comments

Use inline comments sparingly—only to explain non-obvious logic:

- Prefer self-documenting code over comments.
- Use inline comments for complex algorithms, non-obvious business logic, or workarounds.
- Write complete sentences with proper grammar.
- Place comments on the line above the code they describe.

```swift
// ✅ GOOD: Explains non-obvious logic
// URLSession's delegate callbacks are not correctly annotated for strict
// concurrency, so we must capture properties explicitly rather than passing self.
session.dataTask(with: request) { [logger, configuration] data, response, error in

// ❌ BAD: States the obvious
// Create a new user
let user = User(name: name)
```

### Prohibited

- NEVER use `// MARK:` sections.
- NEVER use comments to disable code (delete it instead).
- NEVER use comments to explain what code does when the code is self-explanatory.

## Layout and Spacing

### Line Breaks

- One declaration per line.
- Break before operators.
- Align wrapped parameter lists.
- Maximum line length 120 characters.

### Vertical Spacing

- Single blank line between declarations.
- Blank line before and after type/extension declarations.
- No blank line after opening brace or before closing brace.

### Indentation

- Use 4 spaces for indentation.
- Indent wrapped lines to align with the opening delimiter.

## File Organization

Consistent file organization makes it easy to find declarations without searching — readers can predict where things are.

### Headers

- Files begin with standard header format:

```swift
//
//  Copyright © <YYYY> Kyle Hughes. All rights reserved.
//
```

### Type Organization

- Define each type or extension in its own file unless types are tightly coupled.
- Place nested type definitions in separate extensions in their own files.
- Organize members by kind first, then by access level within each kind. This grouping means the public API is always at the top of each section:
    - **Properties:**
        - `public` properties
        - `package` properties
        - `internal` properties
        - `fileprivate` properties
        - `private` properties
    - **Initializers:**
        - `public` initializers
        - `package` initializers
        - `internal` initializers
        - `fileprivate` initializers
        - `private` initializers
    - **Interface (Methods & Computed Properties):**
        - `public` interface (`static/class` > `instance`)
        - `package` interface (`static/class` > `instance`)
        - `internal` interface (`static/class` > `instance`)
        - `fileprivate` interface (`static/class` > `instance`)
        - `private` interface (`static/class` > `instance`)
- Within each group, order lexicographically by identifier when reordering is semantics-preserving. Lexicographic ordering removes subjective judgment about "what goes first" and makes diffs predictable.

### Lexicographic Ordering

When semantics allow, sort independent declarations and statements lexicographically by identifier. This applies to enum cases, switch cases over those enums, independent variable declarations, and similar constructs where order has no runtime effect.

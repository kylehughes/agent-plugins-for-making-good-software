---
name: modeling-swift-types-for-correctness
description: >-
  Designs Swift types that make invalid states unrepresentable at compile time. Use when choosing between
  booleans and enums, replacing parallel arrays or optional-laden structs, applying phantom types, newtypes,
  ~Copyable move semantics, typed throws, or any pattern that shifts runtime checks into the type system.
  Trigger this skill whenever the task involves modeling state machines, eliminating impossible states,
  designing sum or product types, wrapping raw values for type safety, enforcing ownership or linear
  consumption, or refactoring code that has fatalError("impossible") branches, sentinel values, or
  stringly-typed identifiers. (swift, types, correctness, compile-time, state modeling, enum, struct,
  phantom type, newtype, validated value, ~Copyable, typed throws, state machine)
---

# Type-Driven State Modeling in Swift

## Philosophy

Tenet 3: "Push logic into types." The compiler is the most reliable reviewer — every runtime check it can replace is a bug it prevents for free. The goal is not clever types but **obvious** types: if it compiles, it is correct.

This skill covers *how to shape types* for correctness. Adjacent skills cover complementary concerns:

- `organizing-swift-types` — *where* to put types (access control, extensions, file structure)
- `designing-swift-apis` — *how to name* types (clarity at the point of use)
- `writing-swift` — coding standards that apply to all Swift code
- `using-swift-concurrency` — state correctness under concurrency

## When to Apply

Apply these patterns when you encounter:

- Mutually exclusive booleans (`isLoading` + `isError` + `isSuccess`)
- Booleans paired with correlated optionals (`isLoaded` + `data: T?`)
- Parallel arrays that must stay synchronized
- Dictionaries used as ad-hoc structs
- Optional fields that are always present in certain states
- Stringly-typed identifiers or configuration values
- Runtime assertions that guard invalid states
- `switch` statements with `fatalError("impossible")` branches
- Sentinel values (`-1`, `""`, `.zero`) representing absence
- Resources that must be consumed exactly once

## Quick Reference: Smell to Pattern

| Code Smell | Pattern | Section |
|---|---|---|
| Mutually exclusive booleans | Enum with associated values | 1 |
| Boolean + correlated optional | Enum with associated values | 1 |
| Parallel arrays | Single array of richer struct | 2 |
| Dictionary-as-struct | Named struct | 2 |
| Loose tuples passed around | Named struct | 2 |
| Optionals always present in some state | Enum with state-dependent data | 3 |
| Stringly-typed identifiers | Generic wrapper with tag type | 4 |
| Type-safe IDs across domains | Phantom-typed ID | 4 |
| Resources consumed exactly once | `~Copyable` + consuming methods | 5 |
| State machines with irreversible transitions | `~Copyable` + consuming methods | 5 |
| Untyped `throws` erasing error info | `throws(E)` | 6 |
| Scattered runtime validation of semantic constraints | Failable init newtype or property wrapper | 7 |
| Sentinel values representing absence | Optional or dedicated empty case | 7 |

## 1: Sum Types Over Boolean Flags

### Problem

Booleans are the most common source of invalid state. Two independent booleans create four combinations — if only two or three are valid, the type permits states the program must never enter.

```swift
// 8 representable states (2×2×2), but only 3 are valid
var isLoading: Bool
var error: Error?
var data: [Item]?
```

A boolean paired with a correlated optional is the same problem in disguise: `isLoaded = false` with `data != nil` is incoherent.

### Pattern

Replace with an enum whose cases enumerate *exactly* the valid states.

```swift
// Exactly 3 states — no invalid combinations possible
enum LoadState<T: Sendable>: Sendable {
    case idle
    case loading
    case completed(Result<T, any Error>)
}
```

### When Overkill

A single, truly independent boolean is fine. `isEnabled` on a toggle, `isEmpty` on a collection — these have no correlated state. The test: if the boolean has no dependent optionals or sibling booleans, leave it.

## 2: Product Type Consolidation

### Problem

Parallel arrays require synchronized indices. Dictionaries used as structs lose compile-time key checking. Loose tuples lose names across call sites.

```swift
// Parallel arrays — out-of-sync indices cause silent bugs
var names: [String]
var ages: [Int]
var emails: [String]

// Dictionary-as-struct — typo in key compiles fine
let config: [String: Any] = ["timout": 30] // "timeout" typo
```

### Pattern

Introduce a named type that binds related values together.

```swift
struct Person: Sendable {
    let age: Int
    let email: String
    let name: String
}

var people: [Person]
```

### When Overkill

Tuples are fine for local scope — returning `(min: Int, max: Int)` from a private helper doesn't need a struct. The test: does this tuple cross a module boundary or get stored in a collection? If yes, use a struct.

## 3: Optionality Refinement

### Problem

Optionals that are always present in certain states force `guard let` / `if let` chains that can never fail. The code compiles, but the type model is imprecise — it permits states the domain does not.

```swift
struct UserProfile {
    let avatarURL: URL?
    let displayName: String?
    let isComplete: Bool // true means both fields are non-nil
}
```

### Pattern

Embed state-dependent data in enum associated values so the compiler enforces presence.

```swift
enum UserProfile {
    case incomplete
    case complete(avatarURL: URL, displayName: String)
}
```

Or use separate types for each state when the data diverges significantly:

```swift
struct IncompleteProfile: Sendable { /* partial fields */ }
struct CompleteProfile: Sendable { let avatarURL: URL; let displayName: String }

enum UserProfile: Sendable {
    case complete(CompleteProfile)
    case incomplete(IncompleteProfile)
}
```

### When Overkill

When fields are genuinely independently optional — a user might have an avatar but no display name, or vice versa. The test: can each combination of nil/non-nil actually occur in the domain?

## 4: Phantom Types

### Problem

Identifiers, tokens, and keys that are all `String` at the type level can be confused at call sites. The compiler cannot distinguish a user ID from a workspace ID.

```swift
func fetchUser(id: String, workspaceID: String) -> User
// Easy to swap arguments — compiles fine
fetchUser(id: workspaceSlug, workspaceID: userID)
```

### Pattern

Use a generic wrapper with an uninhabited tag type parameter:

```swift
struct Identifier<Tag>: Hashable, RawRepresentable, Sendable {
    let rawValue: String
}

// RawRepresentable enables automatic Codable conformance and easy conversion.

enum UserTag {}
enum WorkspaceTag {}

typealias UserID = Identifier<UserTag>
typealias WorkspaceID = Identifier<WorkspaceTag>

func fetchUser(id: UserID, workspaceID: WorkspaceID) -> User
// Compiler rejects: fetchUser(id: workspaceID, workspaceID: userID)
```

The tag type is never instantiated — it exists only at the type level to differentiate wrappers.

### When Overkill

A single ID type used within a narrow module where confusion is impossible. The test: are there two or more identifiers of the same underlying type that could plausibly be swapped at a call site?

For detailed treatment including state-tagged phantom types and builder patterns, see [REFERENCE.md](REFERENCE.md#phantom-types).

## 5: ~Copyable and Move Semantics

### Problem

Resources that must be consumed exactly once — file handles, tokens, state machine transitions — are modeled as regular values that can be copied, used twice, or silently dropped.

### Pattern

Mark the type `~Copyable` so the compiler tracks ownership. Use `consuming` methods for irreversible transitions.

```swift
struct OneTimeToken: ~Copyable {
    private let value: String

    consuming func redeem() -> String {
        value
    }
}

let token = OneTimeToken(value: "abc")
let result = token.redeem()
// token.redeem() // Compiler error: 'token' consumed by previous call
```

For state machines, consuming the current state and returning the next prevents illegal transitions:

```swift
struct Draft: ~Copyable {
    consuming func submit() -> Submitted { Submitted() }
}

struct Submitted: ~Copyable {
    consuming func approve() -> Approved { Approved() }
}
```

### When Overkill

Most values are naturally copyable. Reserve `~Copyable` for resources with linear consumption semantics — tokens, handles, one-shot continuations, state machine states. The test: does copying this value create a logical error?

For complete treatment including `borrowing`, `consuming`, `~Escapable`, and state machine patterns, see [REFERENCE.md](REFERENCE.md#noncopyable-and-move-semantics).

## 6: Typed Throws

### Problem

Untyped `throws` erases the error type to `any Error`, forcing callers to pattern-match or use broad `catch` blocks. The compiler cannot enforce exhaustive error handling.

### Pattern

Use `throws(E)` to preserve the concrete error type through the call chain.

```swift
enum ValidationError: Error {
    case empty
    case tooLong(max: Int)
}

func validate(_ input: String) throws(ValidationError) -> String {
    guard !input.isEmpty else { throw .empty }
    guard input.count <= 100 else { throw .tooLong(max: 100) }
    return input
}

// Caller gets exhaustive switching
do {
    let result = try validate(input)
} catch .empty {
    // handle
} catch .tooLong(let max) {
    // handle
}
```

### When Overkill

When the caller doesn't benefit from knowing the specific error type — top-level UI error presentation that shows a generic message regardless. The test: will the caller switch on the error type? If not, untyped `throws` is simpler.

For complete treatment including generic typed throws, protocol requirements, and scoped errors, see [REFERENCE.md](REFERENCE.md#typed-throws).

## 7: Validated Values

### Problem

Semantic constraints (non-empty strings, positive integers, bounded ranges) enforced by scattered runtime checks throughout the codebase. Each call site must remember to validate, and forgetting is silent.

### Pattern

**Failable-init newtypes** — validate once at construction, carry the guarantee in the type:

```swift
struct NonEmptyString: Sendable {
    let value: String

    init?(_ value: String) {
        guard !value.isEmpty else { return nil }
        self.value = value
    }
}
```

**Property wrappers** — embed validation into storage:

```swift
@propertyWrapper
struct Clamped<Value: Comparable & Sendable>: Sendable {
    let range: ClosedRange<Value>
    var wrappedValue: Value {
        get { storage }
        set { storage = min(max(newValue, range.lowerBound), range.upperBound) }
    }

    private var storage: Value

    init(wrappedValue: Value, _ range: ClosedRange<Value>) {
        self.range = range
        self.storage = min(max(wrappedValue, range.lowerBound), range.upperBound)
    }
}
```

### When Overkill

When a constraint is checked at a single call site and the value doesn't propagate further. The test: does this validated value cross a function boundary? If it stays local, inline validation is fine.

## 8: Advanced Patterns

Brief orientation — see [REFERENCE.md](REFERENCE.md#advanced-patterns) for full treatment.

### Protocol Witnesses vs Runtime Polymorphism

Replace dynamic dispatch with static types when the set of behaviors is known at compile time. A protocol witness struct (a concrete type conforming to a protocol, configured via closures or stored functions) avoids existential overhead and enables generic specialization.

### Generic Constraints and Conditional Conformance

Use `where` clauses to express type relationships at compile time. Conditional conformance (`extension Array: Equatable where Element: Equatable`) extends capabilities precisely when the constituent types support them.

### `some` vs `any` (Opaque vs Existential)

Prefer `some` (opaque types) when the concrete type is fixed but hidden — enables compiler optimization and generic specialization. Use `any` (existential) when heterogeneous storage is required. The compiler enforces the distinction.

### Result Builders for Domain Validation

Result builders (`@resultBuilder`) can enforce structural constraints at compile time — ensuring a configuration has required fields, a form has at least one section, etc.

### `InlineArray` for Fixed-Size Collections

When size is known at compile time, `InlineArray<Count, Element>` (Swift 6.2) stores elements inline without heap allocation, enforcing the size constraint in the type.

### Marker Protocols for Type-Level Properties

Empty protocols (`protocol Validated {}`) serve as compile-time tags — generic constraints on `where T: Validated` restrict APIs to types that have been through validation, without runtime overhead.

## 9: Pragmatism Guardrails

Tenet 1: "Be pragmatic, not dogmatic." Type-driven design adds value only when the complexity it introduces is less than the runtime errors it prevents.

**When type modeling adds cost without value:**

- **One consumer**: If a value is created and consumed in the same function, inline validation is clearer than a newtype.
- **Stable domain**: If the set of states hasn't changed in a year and no bugs have occurred, adding an enum is churn.
- **Prototype code**: Exploratory code should optimize for iteration speed, not compile-time guarantees.
- **Negligible risk**: A boolean `isAnimating` that, if wrong, causes a visual glitch (not data corruption) doesn't warrant an enum.

**The "one reader" test**: If the person reading this code would find the type heavier than the problem it solves, the type is over-engineered. Optimize for the reader.

**Tenet 5 check**: "Invent empathetically." Every custom type you create is a type someone else must learn. If the learning cost exceeds the safety benefit, simplify.

## Cross-References

| Skill | Relationship |
|---|---|
| `organizing-swift-types` | WHERE to put types you create |
| `designing-swift-apis` | HOW to name the types and their members |
| `writing-swift` | Coding standards applying to all Swift code |
| `using-swift-concurrency` | State correctness under concurrency |

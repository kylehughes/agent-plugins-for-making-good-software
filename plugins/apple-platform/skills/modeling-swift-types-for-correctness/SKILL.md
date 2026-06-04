---
name: modeling-swift-types-for-correctness
description: >-
  Designs Swift types that make invalid states unrepresentable at compile time. Use when choosing between
  booleans and enums, replacing parallel arrays or optional-laden structs, applying phantom types, newtypes,
  typestate APIs, capability tokens, validated values, typed keys, ownership/lifetime types, ~Copyable move
  semantics, typed throws, Sendable/isolation constraints, or any pattern that shifts runtime checks into
  the type system. Trigger this skill whenever the task involves modeling state machines, eliminating
  impossible states, designing sum or product types, wrapping raw values for type safety, enforcing ownership
  or linear consumption, modeling trust/sanitization, replacing stringly typed identifiers, reducing
  fatalError("impossible") branches, or deciding whether a Swift type model is too weak or too heavy.
  (swift, types, correctness, compile-time, state modeling, enum, struct, phantom type, newtype, validated
  value, capability token, ~Copyable, ~Escapable, typed throws, Sendable, state machine)
---

# Type-Driven State Modeling in Swift

## Philosophy

Tenet 3: "Push logic into types." Use Swift's compiler as a reviewer by making invalid states difficult or impossible to construct.

The goal is not clever types. The goal is obvious APIs where misuse fails at the call site, validation happens once at a boundary, and the rest of the code can operate on refined values without repeated defensive checks.

Swift is not dependently typed. Do not claim compile-time enforcement for arbitrary runtime values. Swift can prove finite cases, nominal distinctions, ownership/lifetime constraints, generic relationships, literal integer parameters, literal macros, actor isolation, `Sendable`, and controlled construction. Runtime-derived facts still need validation that produces a refined value.

## Workflow

1. **Name the invariant.** Decide whether the problem is exclusivity, co-presence, absence reason, identity/domain, cardinality, ordering, bounds, units, phase/state, capability, trust, isolation, ownership/lifetime, failure surface, layout, or boundary refinement.
2. **Choose the lightest proof.** Prefer the smallest type change that makes the invalid operation fail to compile or impossible to express.
3. **Control construction.** A type proves an invariant only when all relevant initializers, stored properties, conformances, decoding paths, and escape hatches preserve it.
4. **Refine at boundaries.** Keep DTOs, database rows, Objective-C shapes, C buffers, analytics dictionaries, user defaults, and server strings raw at the edge; convert into domain types before core logic.
5. **Let compiler errors drive migration.** Introduce the refined type, change core functions first, follow type errors to callers, then remove raw overloads.
6. **Test the proof.** Add constructor tests for boundary values and compile-fail examples for misuse when the invariant is important.

## Invariant Taxonomy

| Invariant | Typical Swift Tools |
|---|---|
| Exactly one state/variant | `enum`, nested enums, `Never`, `Result<Success, Never>` |
| Correlated fields or co-presence | Enum associated values, separate state structs, product type consolidation |
| Absence with reason | Optional, enum, `Result`, typed throws |
| Identity/domain separation | Newtype, phantom-typed ID, typed key |
| Cardinality and bounds | `NonEmpty`, bounded newtype, `OptionSet`, `InlineArray`, integer generic parameter |
| Ordering and canonical form | Validating initializer, canonicalizing initializer, domain interval type |
| Units and dimensions | `Quantity<Unit, Value>`, phantom tags, constrained conversions |
| Phase/state transition | Enum, typestate generic, constrained extension, `~Copyable` consuming transition |
| Capability/authority | Unforgeable token with private initializer, actor- or module-issued proof |
| Trust/sanitization | Raw/sanitized/escaped/parameterized wrapper states |
| Isolation/concurrency | `Sendable`, `@Sendable`, actor/global-actor isolation, `sending`, immutable snapshot |
| Ownership/lifetime | `~Copyable`, `borrowing`, `consuming`, `inout`, `~Escapable`, `Span` |
| Failure surface | `throws(E)`, `Result<Value, Failure>`, `Failure == Never`, accumulated validation |
| Layout/performance | `InlineArray`, `BitwiseCopyable`, fixed-size wrappers, safe unsafe-interop wrapper |
| Source boundary | DTO-to-domain refinement, custom `Decodable`, typed NotificationCenter message |

## Smell to Pattern Matrix

| Smell | Invariant | Lightest Adequate Construct | Heavier Alternatives | Avoid |
|---|---|---|---|---|
| `isLoading`, `data?`, `error?` | Exclusive phase + co-presence | Enum with associated values | Generic `LoadState<Value, Failure>` | Stored derived booleans |
| One of several optionals must exist | Exclusive payload | Enum | Separate state structs | `guard let` maze plus `fatalError` |
| Parallel arrays | Element co-presence | Array of struct | Domain collection wrapper | Shared index discipline |
| `[String: Any]` with fixed keys | Named fields | Struct or typed key map | DTO plus domain model | Force casts in core code |
| Raw `String` IDs | Identity/domain | Newtype | Phantom `Identifier<Tag>` | `typealias` as safety |
| Status string or mode integer | Finite variant | Enum with unknown case if external | Resilient public enum | Sentinel values |
| Public validated wrapper with public storage | Bounds/trust | Private storage + validating init | Factory + unsafe internal escape hatch | Public memberwise bypass |
| `isAdmin` parameter | Capability | Unforgeable capability token | Session typestate | Boolean authorization |
| Raw HTML/SQL/shell text | Trust boundary | `HTML<Sanitized>`, `SQL<Parameterized>` | Macro/literal validation | Escaping by convention |
| Resource used once | Ownership | `~Copyable` + `consuming` | Closure-scoped access | Copyable wrapper with comments |
| Actor-owned mutable model crossing tasks | Isolation | Immutable `Sendable` snapshot | Transfer with `sending` | Leaking non-Sendable references |
| Untyped domain failure | Failure surface | `throws(E)` or `Result<Value, E>` | Layered error mapping | Giant global `AppError` |
| Required builder fields | Construction order | Staged builder or phantom state | Macro-generated builder | Plain result builder alone |
| Heterogeneous `[any P]` loses relationships | Type relationship | Generic or constrained existential | Type eraser preserving axes | Erasing `Self`/associated types too early |

## Proof-Strength Ladder

Use stronger tools only when the weaker tool does not prove the invariant.

1. Comment: documents intent; proves nothing.
2. `typealias`: improves readability; proves nothing because the raw type is still accepted.
3. Named parameter: reduces call-site confusion; does not prevent same-type swaps.
4. Nominal newtype: prevents accidental mixing; proof depends on access control and validation.
5. Failable or throwing initializer: validates construction; can be bypassed by public stored properties, memberwise init, or synthesized decoding.
6. Private init plus factory: centralizes proof production; still audit internal unsafe paths.
7. Enum with payloads: encodes finite valid states; use no `default` for owned enums.
8. Generic or phantom state: removes invalid operations from the API; watch generic explosion.
9. Constrained extension or same-type constraint: exposes operations only when relationships hold.
10. Ownership/lifetime type: compiler enforces use-after-consume and nonescaping borrowed views.
11. Macro or literal validation: proves static input; runtime input still needs validation.
12. Compiler mode: strict concurrency, strict memory safety, warnings-as-errors, and compile-fail fixtures keep the model from regressing.

## Closed-World vs Open-World

- Use an `enum` when the variants are finite and owned by this module.
- Use a protocol or existential when third parties can add variants.
- Use a generic parameter when the caller chooses one concrete type.
- Use `some P` when the callee returns one fixed concrete type but hides it.
- Use `any P` only for heterogeneous runtime storage or dynamic dispatch.
- Use a witness struct when behavior is data or configuration rather than subtype identity.
- Use a type eraser when you need storage while preserving associated-type axes such as `Input`, `Output`, and `Failure`.

Public library enums need a resilience decision. Internal closed domains should avoid `default` so new cases produce compiler errors. External string domains often need `case unknown(String)` instead of failing decode.

## Core Patterns

### Sum Types Over Boolean Flags

Replace mutually exclusive booleans and correlated optionals with an enum that has exactly the valid cases.

```swift
enum LoadState<Value: Sendable, Failure: Error & Sendable>: Sendable {
    case idle
    case loading(previous: Value?)
    case loaded(Value)
    case failed(Failure, previous: Value?)
}

extension LoadState {
    var isLoading: Bool {
        if case .loading = self { true } else { false }
    }
}
```

Derived booleans are fine. Stored booleans that duplicate enum state are not.

### Product Type Consolidation

Bind values that must move together into a named struct or domain collection.

```swift
struct Contact: Sendable {
    let email: EmailAddress
    let name: NonEmptyString
    let phoneNumber: PhoneNumber?
}
```

Avoid storing facts that can drift out of sync, such as `count` beside an array, `duration` beside `start` and `end`, or `isValid` beside raw fields.

### Validated Values and Newtypes

Validate once at a trust boundary and pass the refined type inward.

```swift
struct EmailAddress: Hashable, Sendable {
    private let rawValue: String

    init(_ rawValue: String) throws(ValidationError) {
        let canonical = rawValue.trimmingCharacters(in: .whitespacesAndNewlines).lowercased()
        guard canonical.contains("@") else { throw .missingAtSign }
        self.rawValue = canonical
    }
}
```

Control the memberwise initializer. `ExpressibleByStringLiteral` cannot fail, and `RawRepresentable` is only safe when `init(rawValue:)` validates or construction is otherwise sealed.

### Phantom Types, Typestate, and Capability Tokens

Use phantom parameters when the same runtime representation has different compile-time roles.

```swift
struct Identifier<Tag>: Hashable, RawRepresentable, Sendable {
    let rawValue: String
}

enum UserTag {}
enum WorkspaceTag {}

typealias UserID = Identifier<UserTag>
typealias WorkspaceID = Identifier<WorkspaceTag>
```

For state-dependent APIs, put operations in constrained extensions.

```swift
enum Unvalidated {}
enum Validated {}

struct Form<State>: Sendable {
    private let fields: [String: String]
}

extension Form where State == Unvalidated {
    func validate() throws(ValidationError) -> Form<Validated> { /* ... */ }
}

func submit(_ form: Form<Validated>) async throws(SubmitError) { /* ... */ }
```

Public marker protocols are forgeable by public conformance. They prove something only when construction or conformance is controlled through access control, private requirements, sealed wrappers, or capability tokens.

### Ownership and Lifetime

Use ownership when copying or escaping is the bug.

```swift
struct Transaction<State>: ~Copyable {
    private let handle: DatabaseHandle
}

extension Transaction where State == Active {
    consuming func commit() throws(TransactionError) -> Transaction<Committed> { /* ... */ }
    consuming func rollback() -> Transaction<RolledBack> { /* ... */ }
}
```

Use `borrowing` to inspect, `consuming` to take ownership exactly once, `inout` for exclusive mutation, `~Escapable` and `Span` for borrowed views that must not outlive their owner.

### Modeling Failures Honestly

Use `Optional` for absence without diagnostics, `Result` for stored or composable outcomes, `throws` for control-flow failure, typed throws when callers benefit from the exact failure type, and accumulated validation when forms or batches need all errors.

Typed throws gives a `catch` block a precise error type. It does not make a chain of `catch .case` clauses generally exhaustive. Use an unconditional `catch` and switch inside when exhaustive case handling matters.

```swift
do {
    _ = try validate(input)
} catch {
    switch error {
    case .empty:
        break
    case .tooLong(let max):
        print(max)
    }
}
```

Use `throws(Never)` or `Result<Value, Never>` when failure is impossible. Keep `Never`-based APIs honest; do not invent unreachable failure paths to satisfy a generic abstraction.

### Generics, Protocols, and Existentials

Use associated types, same-type constraints, and conditional conformances to model relationships.

```swift
protocol Endpoint {
    associatedtype Request: Sendable
    associatedtype Response: Sendable
    associatedtype Failure: Error & Sendable

    func decode(_ data: Data) throws(Failure) -> Response
}

func send<E: Endpoint>(_ endpoint: E, request: E.Request) async throws(E.Failure) -> E.Response { /* ... */ }
```

Put constraints on methods or extensions when only those operations require them. Do not constrain the whole type to `Codable`, `Sendable`, or `Equatable` if most operations do not need that capability.

### Builders, Macros, and Reflection

A result builder alone does not prove a required field exists. Pair builders with staged overloads, phantom state, validating output types, or macros that generate sealed construction paths.

Use macros to remove repetitive proof plumbing, such as newtypes, typed IDs, case paths, or literal validation. Do not hide core domain logic in generated code. Literal validation only proves literal/static input; runtime strings still need validated constructors.

Use `KeyPath<Root, Value>` or typed keys instead of string field names for forms, sorting, predicates, analytics, user defaults, feature flags, and localization keys.

### Concurrency and Boundaries

Model isolation in signatures. Prefer immutable `Sendable` structs for values that cross actors, `@MainActor` view models for UI-owned state, `@Sendable` closures for concurrent execution, and immutable snapshots for actor-owned mutable models.

At app boundaries, convert raw shapes into domain types:

- JSON/database rows -> DTO -> validated domain model
- Objective-C dictionaries/nullability -> Swift nominal values
- C/C++ handles and buffers -> ownership/lifetime wrappers
- Notification names/userInfo -> typed notification messages
- server routes -> typed endpoints, cursors, freshness, and error types
- secrets/PII/raw HTML/SQL/shell fragments -> redacted or safe-state wrappers

## Escape Hatches

Unsafe or unchecked construction is sometimes necessary for performance, decoding, tests, or interop. Keep it narrow.

- Prefer `internal` or `private` escape hatches.
- Name them loudly: `unsafeAssumingValid`, `unchecked`, `trusted`.
- Document the precondition in one sentence.
- Centralize uses at the boundary.
- Add tests or compile-fail fixtures that prove ordinary construction cannot bypass validation.

## When to Stop

Type modeling adds value only when the safety benefit exceeds the learning and maintenance cost.

Skip or simplify when:

- The value is created and consumed in one function.
- The invariant is obvious, stable, and low risk.
- The generic axes are multiplying faster than the domain states.
- Type-checking slows down or diagnostics become unreadable.
- A plain enum or struct would express the model more clearly than a phantom hierarchy.
- The proof has already been established inside a module and type erasure at the boundary would reduce noise.

When a design is overmodeled, collapse phantom axes into an enum, replace generic state with separate structs, erase behavior behind a preserving type eraser, or move validation back to the boundary.

## References

Read only the reference needed for the task:

- [REFERENCE.md](REFERENCE.md) - core taxonomy, proof rules, feature availability, migration, and worked refactors.
- [references/algebraic-and-value-modeling.md](references/algebraic-and-value-modeling.md) - enums, product/value modeling, Codable, non-empty/bounded values, routes, forms, money, units, dates, typed keys.
- [references/generics-phantom-and-protocols.md](references/generics-phantom-and-protocols.md) - phantom state, capability tokens, trust types, associated types, same-type constraints, `some`/`any`, type erasure, builders, macros.
- [references/ownership-concurrency-boundaries.md](references/ownership-concurrency-boundaries.md) - `~Copyable`, `~Escapable`, `Span`, typed throws, validation, Sendable/isolation, networking, persistence, interop, security.


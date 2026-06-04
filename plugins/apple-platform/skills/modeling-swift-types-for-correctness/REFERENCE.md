# Type-Driven State Modeling - Core Reference

This file is the entry reference for `modeling-swift-types-for-correctness`. It covers how to choose a modeling strategy, how strong each proof is, where Swift's type system stops, and how to migrate code without overmodeling it.

For detailed pattern catalogs, load only the focused reference needed for the task:

- [references/algebraic-and-value-modeling.md](references/algebraic-and-value-modeling.md)
- [references/generics-phantom-and-protocols.md](references/generics-phantom-and-protocols.md)
- [references/ownership-concurrency-boundaries.md](references/ownership-concurrency-boundaries.md)

## What Kind of Invariant Is This?

Classify the invariant before choosing a construct.

| Invariant class | Question | Good first tools |
|---|---|---|
| Exclusivity | Can exactly one variant be true? | `enum`, `Result`, `Optional` |
| Co-presence | Do fields become valid together? | Enum associated values, richer struct |
| Absence reason | Is missing data meaningful? | Optional, enum, typed error |
| Identity/domain | Can two same-shaped values be swapped? | Newtype, phantom tag |
| Cardinality | Is zero, one, at least one, or fixed size required? | `NonEmpty`, `OptionSet`, `InlineArray`, integer generics |
| Ordering | Must values be sorted or normalized? | Canonicalizing initializer |
| Bounds | Must values be positive, finite, or within a range? | Bounded newtype, property wrapper |
| Units/dimensions | Can units be mixed accidentally? | `Quantity<Unit, Value>`, phantom unit tags |
| Phase/state | Are only some operations legal now? | Enum, typestate, constrained extension |
| Capability/authority | Should possession of a value grant permission? | Token with private initializer |
| Trust/sanitization | Has untrusted data been checked or escaped? | Raw/safe state wrapper |
| Isolation | Which executor owns this value? | Actor isolation, global actor, `Sendable`, snapshot |
| Ownership/lifetime | Can the value be copied or escape? | `~Copyable`, `~Escapable`, `borrowing`, `consuming`, `Span` |
| Failure surface | What failures can occur? | `throws(E)`, `Result<Value, Failure>`, `Never` |
| Layout/performance | Is representation part of correctness? | `InlineArray`, `BitwiseCopyable`, fixed wrappers |
| Source boundary | Where does raw external data enter? | DTO -> domain refinement |

## Invariant-to-Tool Matrix

| Tool | Proves | Does Not Prove |
|---|---|---|
| `enum` | Finite variants and case-specific payloads | External string validity unless decoded carefully |
| Struct/newtype | Nominal distinction and encapsulated validation | Safety if public storage or memberwise init bypass validation |
| Optional | Absence allowed | Why absence happened |
| `Result` | Stored success/failure outcome | Exhaustive control flow unless switched |
| Generic wrapper | Relationship carried in type signature | Runtime-derived value constraints |
| Phantom tag | Same representation, different domain/state | Unforgeability without controlled construction |
| Constrained extension | Operation exists only when constraints hold | Simplicity when states are highly dynamic |
| Associated type | Families of related types | Heterogeneous storage without erasure |
| Same-type constraint | Two axes are identical | Arbitrary value-level equality |
| `Sendable` | Safe transfer across concurrency domains | Thread safety of `@unchecked Sendable` without audited synchronization |
| Actor/global actor | Executor ownership | Value validity outside that isolation unless snapshot/refined |
| `~Copyable` | No implicit copies; consumed values cannot be reused | Collection/storage ergonomics of ordinary values |
| `~Escapable` | Borrowed value cannot escape its lifetime | General dependent lifetime logic |
| `Span` | Borrowed contiguous-memory view with compiler-checked lifetime | Ownership of the backing storage |
| `InlineArray` | Fixed element count in the type | Dynamic size validation |
| Integer generic parameter | Literal integer carried in a type | Arbitrary runtime integer as a type parameter |
| Property wrapper | Repeated storage-level policy | Cross-field invariants by itself |
| Macro | Generated proof plumbing; literal/static validation | Runtime input validity |
| Result builder | DSL grammar shape | Required fields unless paired with staged/validated output |
| Key path | Typed field reference | Dynamic field names from untrusted input |
| Protocol witness | Behavior as a value | Free static specialization in every context |
| Type eraser | Storage while preserving chosen axes | Axes you erase from the wrapper |

## Proof-Strength Ladder

Prefer the weakest construct that actually prevents misuse.

| Strength | Construct | What It Buys |
|---|---|---|
| 1 | Comment | Human reminder only |
| 2 | `typealias UserID = String` | Better vocabulary, no type safety |
| 3 | External parameter label | Reduces call-site confusion |
| 4 | Newtype | Prevents same-raw-type swaps |
| 5 | Failable/throwing initializer | Validates before construction |
| 6 | Private init + factory | Centralizes proof creation |
| 7 | Enum with payloads | Invalid state combinations disappear |
| 8 | Phantom/generic state | Invalid operations are absent |
| 9 | Constrained extension/where clause | Relationships become compile-time requirements |
| 10 | Ownership/lifetime type | Compiler enforces use-after-consume and nonescape rules |
| 11 | Macro/literal validation | Static input checked before runtime |
| 12 | Compiler mode/test harness | Regression pressure across the project |

Type modeling is only a proof when all construction routes preserve the invariant. Audit these bypasses:

- public stored properties
- public or internal memberwise initializers
- synthesized `Decodable`
- public `init(rawValue:)`
- public marker-protocol conformance
- `unsafeBitCast`, force casts, unchecked bridging
- `@unchecked Sendable`
- `unsafeAssumingValid` helpers
- test-only factories that leak into production modules

## State-Count Arithmetic

Count representable states, then count valid states. A type is suspicious when the gap is large.

```swift
struct LoadingModel {
    var data: [Item]?
    var error: Error?
    var isLoading: Bool
}
```

This has `2 * 2 * 2 = 8` representable nil/error/loading combinations before considering the actual array contents. If the domain allows only idle, loading, loaded, and failed, use an enum.

```swift
enum LoadingModel {
    case idle
    case loading
    case loaded([Item])
    case failed(Error)
}
```

The same arithmetic catches optional product explosions:

```swift
struct LoginResult {
    var token: String?
    var mfaChallenge: Challenge?
    var error: Error?
}
```

If exactly one field should be present, the struct permits seven invalid combinations. Use an enum.

## Closed-World and Open-World Decisions

Use the construct that matches who owns the variant set.

| Situation | Prefer |
|---|---|
| Finite cases owned by this module | `enum` |
| Finite cases from an external resilient framework | `switch` with `@unknown default` |
| External server strings with forward compatibility | `enum Known { case knownA; case unknown(String) }` |
| Third parties add conformers | Protocol or existential |
| Caller picks one concrete type | Generic function/type |
| Callee hides one fixed concrete type | `some P` |
| Heterogeneous runtime storage | `any P` or type eraser |
| Behavior is configuration | Witness struct |

For owned enums, do not use `default` in internal switches. Let a new case break compilation. For public libraries, decide whether adding a case is a source-breaking change. If clients must remain forward compatible, expose an unknown case or document `@unknown default` handling.

## Boundary-First Modeling

Keep raw shapes at the edge and refined types in the core.

```swift
struct UserDTO: Decodable {
    let email: String
    let id: String
    let plan: String
}

struct User: Sendable {
    let email: EmailAddress
    let id: UserID
    let plan: Plan

    init(dto: UserDTO) throws(UserMappingError) {
        do {
            email = try EmailAddress(dto.email)
        } catch {
            throw .invalidEmail(error)
        }

        guard let id = UserID(rawValue: dto.id) else {
            throw .invalidID(dto.id)
        }

        self.id = id
        plan = Plan(rawValue: dto.plan) ?? .unknown(dto.plan)
    }
}
```

Do not let `NSDictionary`, `Any`, `String` status values, raw SQL fragments, Objective-C nullability, untyped notification payloads, or decoded DTOs leak into domain logic.

## Compiler Limits

Do not overstate what Swift can express.

Swift does not cleanly express:

- negative constraints, such as `T` is not `String`
- arbitrary value-dependent types, such as "array length equals this runtime count"
- disjunctive constraints, such as `T == A || T == B`
- runtime string validity without validation
- cross-object membership, such as "this ID belongs to this exact collection instance"
- sortedness of a mutable array unless mutation is controlled
- uniqueness of a nonce across all time without stateful coordination
- exact actor executor behavior hidden behind erased closures unless the type says so

When the compiler cannot prove the invariant, choose an honest boundary: validating initializer, macro for literals, runtime assertion in one place, or a domain service that owns the state.

## Feature Availability

Use current Swift features deliberately and version-gate advice when needed.

| Area | Availability Framing | Modeling Relevance |
|---|---|---|
| Typed throws | Swift 6.0 language mode area | Preserves concrete failure type; use unconditional `catch` + `switch error` for exhaustive case handling. |
| `throws(Never)` | Swift 6 typed throws model | Represents infallible generic failure; equivalent in practice to nonthrowing APIs when no error can be thrown. |
| Noncopyable types and generics | Swift 6.0 language mode area, still evolving in libraries | Models linear resources and irreversible transitions. |
| `BitwiseCopyable` | Swift 6.0 low-level layout marker area | Public conformance is a library promise about representation and destruction. |
| Integer generic parameters | Documented in Swift 6.3 language reference | Carries literal integer values, such as dimensions or fixed sizes, in generic signatures. |
| `InlineArray` | Swift 6.2 | Fixed-size inline storage; count is in the type. |
| `Span` / `RawSpan` | Swift 6.2 safe systems programming | Borrowed memory views with compiler-checked lifetime constraints. |
| Opt-in strict memory safety | Swift 6.2 | Compiler pressure against unsafe constructs in security-critical projects. |
| Typed NotificationCenter messages | Swift 6.2 Foundation | Replaces string names and untyped dictionaries with concrete message types and concurrency semantics. |
| Default actor isolation / `@concurrent` | Swift 6.2 concurrency options | Makes isolation choices visible in signatures and project settings. |
| Macro build improvements | Swift 6.3 package/build tooling | Reduces some macro cost; macros still add debugging and build indirection. |
| `@c` and module selectors | Swift 6.3 | Useful at interop/API boundaries, not central to most domain models. |

Sources for current feature framing: [Swift 6.2 Released](https://www.swift.org/blog/swift-6.2-released), [Swift 6.3 Released](https://www.swift.org/blog/swift-6.3-released), [Swift Language Reference: Generic Parameters and Arguments](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/genericparametersandarguments/), and [Swift compiler typed throws diagnostic](https://docs.swift.org/compiler/documentation/diagnostics/untyped-throws/).

## Migration Recipe

1. Pick one boundary or workflow, not the whole app.
2. Introduce the new type with explicit construction.
3. Add conversion from the legacy shape.
4. Change core functions to accept the refined type.
5. Let compiler errors identify callers.
6. Convert callers nearest the boundary first.
7. Deprecate raw overloads after call sites move.
8. Remove bypasses such as public raw initializers.
9. Add boundary tests and compile-fail misuse examples.
10. Stop when remaining code is clearer with the old shape.

## Unsafe Escape Hatch Policy

Use escape hatches sparingly and make them auditable.

```swift
struct EmailAddress: Sendable {
    private let rawValue: String

    init(_ rawValue: String) throws(ValidationError) { /* validate */ }

    internal static func unsafeAssumingValid(_ rawValue: String) -> EmailAddress {
        // Precondition: caller has already canonicalized and validated this address.
        EmailAddress(rawValue: rawValue)
    }

    private init(rawValue: String) {
        self.rawValue = rawValue
    }
}
```

Keep unchecked construction `internal` or `private` where possible. If it must be public, document the precondition and make the name impossible to miss.

## Worked Refactor: Raw JSON to UI Snapshot

### Before

```swift
struct UserResponse: Decodable {
    var id: String
    var email: String
    var subscription: String
}

@MainActor
final class ProfileViewModel: ObservableObject {
    @Published var error: Error?
    @Published var isLoading = false
    @Published var user: UserResponse?

    func load(id: String) async {
        isLoading = true
        defer { isLoading = false }

        do {
            user = try await api.get("/users/\(id)")
        } catch {
            self.error = error
        }
    }
}
```

Problems:

- `id`, `email`, and `subscription` are unvalidated strings.
- Loading state permits `isLoading == true` with stale `error`.
- The endpoint path is stringly typed.
- The UI stores transport DTOs.
- The error surface is erased.

### After

```swift
struct UserDTO: Decodable, Sendable {
    let email: String
    let id: String
    let subscription: String
}

struct User: Sendable {
    let email: EmailAddress
    let id: UserID
    let subscription: Subscription

    init(dto: UserDTO) throws(UserMappingError) {
        do {
            email = try EmailAddress(dto.email)
        } catch {
            throw .invalidEmail(error)
        }

        guard let id = UserID(rawValue: dto.id) else {
            throw .invalidID
        }

        self.id = id
        subscription = Subscription(rawValue: dto.subscription)
    }
}

enum Subscription: Sendable {
    case free
    case pro
    case unknown(String)
}

enum UserMappingError: Error, Sendable {
    case invalidEmail(EmailAddress.ValidationError)
    case invalidID
}

struct Endpoint<Request: Sendable, Response: Sendable, Failure: Error & Sendable>: Sendable {
    let path: @Sendable (Request) -> Path<Absolute>
    let decode: @Sendable (Data) throws(Failure) -> Response
}

enum ProfileState: Sendable {
    case idle
    case loading(previous: UserSnapshot?)
    case loaded(UserSnapshot)
    case failed(ProfileError, previous: UserSnapshot?)
}

struct UserSnapshot: Sendable {
    let displayEmail: String
    let id: UserID
    let subscriptionLabel: String
}

@MainActor
final class ProfileViewModel: ObservableObject {
    @Published private(set) var state: ProfileState = .idle

    func load(id: UserID) async {
        let previous = state.snapshot
        state = .loading(previous: previous)

        do {
            let user = try await userClient.load(id: id)
            state = .loaded(UserSnapshot(user))
        } catch {
            state = .failed(error, previous: previous)
        }
    }
}
```

The core now receives refined IDs, validated emails, typed endpoint responses, typed errors, and an immutable `Sendable` UI snapshot. The raw JSON still exists, but only at the decoding boundary.

## Overmodeled Rollback

Phantom axes are useful until they hide the domain.

```swift
struct Request<Auth, Body, Response, Retry, Cache, Metrics> {
    /* ... */
}
```

If most call sites spell five or six generic arguments and only one operation depends on each axis, collapse the model.

```swift
struct Endpoint<Request, Response, Failure: Error> {
    let auth: AuthRequirement
    let body: BodyPolicy
    let retry: RetryPolicy<Failure>
    let cache: CachePolicy
}

enum AuthRequirement {
    case none
    case user
    case admin
}
```

Keep a generic axis only when it makes an invalid call fail to compile. Use ordinary stored policy values for configuration that is inspected at runtime anyway.

## Testing and Enforcement

Type modeling moves bugs from call sites into constructors, conversions, and escape hatches. Test those places.

- Add property or table tests for boundary constructors.
- Keep compile-fail fixtures for major guarantees.
- Prefer no `default` in owned enum switches.
- Turn on strict concurrency and warnings-as-errors where the project can support them.
- Use targeted warning controls when a project needs a ratchet: enable the diagnostic group for new code, acknowledge existing violations narrowly, and remove acknowledgements as wrappers replace unsafe or untyped shapes.
- Consider strict memory safety for security-critical modules.
- Add lint rules for recurring smells: `[String: Any]` in core code, raw string IDs in public APIs, multiple correlated booleans, `fatalError("impossible")`, force casts, and broad `@unchecked Sendable`.

Compile-fail examples should show the intended misuse:

```swift
let userID: UserID = UserID(rawValue: "u_1")
let workspaceID: WorkspaceID = WorkspaceID(rawValue: "w_1")

fetchUser(id: workspaceID, in: userID)
// expected-error: cannot convert value of type 'WorkspaceID' to expected argument type 'UserID'
```

A compile-fail harness can be small. Keep snippets under `Tests/CompileFail/`, run `swiftc -typecheck` or `swift test` with a custom script, and assert that each file fails for the expected reason. These fixtures are useful for public APIs where accidental broadening would otherwise compile silently.

## API Boundary and Resilience

Type modeling changes API shape. Treat public and module-boundary changes as design work, not cleanup.

- Public validated wrappers need a stable construction story. Adding validation later can be source-breaking if callers already use raw initializers.
- Public enums need a resilience decision: closed and exhaustively switched, or forward-compatible with unknown cases.
- Public marker protocols are open-world extension points unless conformance is controlled. Do not use them as proof.
- Public `RawRepresentable` types should validate in `init(rawValue:)` or keep raw construction unavailable.
- Public type erasers should preserve the axes that encode correctness, such as `Input`, `Output`, `Failure`, `Auth`, or `State`.
- Public `Sendable`, `BitwiseCopyable`, and ownership conformances are promises. Adding reference storage, locks, destructors, or actor isolation later can change that promise.
- Boundary DTOs can remain flexible while the domain model is strict. This is often the right compatibility split.

## Review Checklist

Ask these questions in code review:

- What invariant is this type trying to prove?
- Where does raw data become refined data?
- Can invalid construction happen through an initializer, stored property, decoding path, conformance, or test helper?
- Does the chosen type remove an invalid operation, or only document intent?
- Is a public marker protocol, public raw value, or public `init(rawValue:)` undermining the proof?
- Are `some`, `any`, generics, and type erasure preserving the relationships that matter?
- Does the model still work across actors and tasks without `@unchecked Sendable` hand-waving?
- What is the escape hatch, and where is it used?
- What compiler error proves misuse?
- Is the type model simpler than the bugs it prevents?

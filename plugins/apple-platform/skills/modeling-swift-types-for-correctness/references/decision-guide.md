# Decision Guide

Use this reference when the correct construct is unclear, when a proposed design feels too clever, or when reviewing whether an invariant is actually enforced.

## Start With the Failure You Want

A useful type change should cause a specific bad operation to fail in one of three places:

1. **At compile time:** the operation is absent or the arguments have incompatible types.
2. **At a single runtime boundary:** raw data cannot become a domain value without validation.
3. **At an explicit unsafe boundary:** a narrowly named unchecked operation documents and centralizes the remaining precondition.

If misuse still compiles throughout the core and each caller must remember a check, the model has not moved the invariant into the type system.

## Invariant Taxonomy

| Invariant | Typical symptom | First choice | Common escalation |
|---|---|---|---|
| Exclusive variant | Boolean flags can conflict | Enum | State-specific concrete types |
| Correlated payload | Optional fields require nested guards | Enum associated values or struct | Domain collection |
| Absence semantics | `nil` means several things | Enum or `Result` | Typed error at operation boundary |
| Nominal identity | IDs or parameters can be swapped | Wrapper struct | Phantom-tagged generic wrapper |
| Validated scalar | Repeated range/format guards | Private-storage newtype | Accumulating validator |
| Canonical form | Equivalent values compare differently | Canonicalizing initializer | Locale/policy-specific wrapper |
| Cardinality | Empty or oversized collection is invalid | Collection wrapper | Fixed-size storage when measured |
| Ordering | Start may exceed end | Interval/range domain type | State-dependent construction |
| Units | Same numeric representation has different dimensions | Quantity wrapper | Dimensional algebra only when needed |
| Phase | Operations are legal only in some states | Separate state structs | Generic typestate |
| Capability | A boolean or role name grants authority | Private-initializer token | Actor-issued revocable authority |
| Trust | Raw and sanitized text share one type | Distinct wrappers | Generic trust-state wrapper |
| Ownership | Copy or reuse after transition is invalid | Private owner with fixed operations | `~Copyable` and consuming methods |
| Lifetime | View must not outlive storage | Closure-scoped borrow | `~Escapable` with a real lifetime dependency |
| Isolation | Mutable reference crosses tasks | Actor or immutable snapshot | Lock for measured synchronous paths |
| Effect identity | Old async result overwrites newer UI state | Request ID or revision in state/action | Explicit command/effect system when feature scale warrants it |
| Failure surface | Callers downcast `Error` | Small local error type | Typed throws for closed surfaces |
| Generic relation | Associated input/output types drift or are erased | Generic parameter or same-type constraint | Primary associated type, constrained existential, or explicit eraser |
| Layout | Heap allocation or variable size is measured cost | Domain struct/tuple | `InlineArray` or low-level wrapper |
| Resource | Handle, bookmark, or scoped access may leak or double-close | Closure-scoped operation | Noncopyable owner with complete cleanup story |
| Security context | URL/path/text/proof is accepted in the wrong sink or authority context | Context-specific wrapper plus checked boundary | Trusted service transaction or OS/server enforcement |
| Boundary | Raw external values leak inward | DTO-to-domain mapping | Custom decoder/adapter |

## Smell Matrix

| Smell | Better model | Why |
|---|---|---|
| `isLoading`, `value?`, `error?` | `enum LoadState` | Invalid combinations disappear |
| `isAuthenticated` plus `user?` | `.anonymous` / `.authenticated(User)` | Authentication and identity cannot drift |
| `start`, `end`, `duration` stored together | Store interval or two independent facts; derive the third | Removes redundant state |
| Parallel arrays | Array of one element struct | Co-presence follows element construction |
| `[String: Any]` in domain code | Struct or typed-key adapter | Removes unchecked key and cast combinations |
| Several raw `String` identifiers | Nominal or phantom IDs | Prevents accidental substitution |
| Sentinel values such as `-1` or `"unknown"` | Optional or enum | Separates absence/unknown from valid values |
| Public `var rawValue` on a validated type | Private `let` plus checked init | Prevents post-construction invalidation |
| `isAdmin: Bool` argument | Capability token or authority service | A call site cannot grant itself authority |
| Raw HTML, SQL, shell, or regex fragments | Trust-state wrapper or parameterized builder | Makes unsafe composition visible |
| `fatalError("impossible")` in normal domain flow | Enum or construction proof | Makes the branch genuinely unrepresentable |
| `@unchecked Sendable` added to silence build | Actor, immutable snapshot, or synchronized wrapper | Replaces assertion with a real concurrency story |
| Generic state parameters on every model | Enum or separate concrete types | Reduces type-system ceremony |
| `InlineArray` for a business rule such as “exactly 3” | Three-field domain struct or validating collection | Keeps layout optimization separate from semantics |
| A cancelled task assumed unable to respond | Request identity plus stale-response rejection | Cancellation is cooperative and side effects may already exist |
| `URL.absoluteString.hasPrefix(allowedBase)` | Parsed-component policy and trusted-root resolution | String prefixes do not establish URL or path authority |
| Protocol-extension helper expected to dispatch dynamically | Declare it as a protocol requirement or avoid existential erasure | Extension-only members are statically selected through an existential |

## Proof-Strength Ladder

Each step carries more enforcement and usually more complexity.

1. **Comment or documentation:** no compiler enforcement.
2. **Name or argument label:** improves readability; same-type swaps remain possible.
3. **`typealias`:** vocabulary only; no nominal distinction.
4. **Nominal wrapper:** prevents substitution if raw overloads are not retained.
5. **Checked initializer:** validates construction through that initializer.
6. **Sealed construction:** private storage/init plus checked factories closes ordinary bypasses.
7. **Algebraic state:** enum cases make invalid combinations absent.
8. **Operation restriction:** constrained extension or distinct state type removes illegal methods.
9. **Capability restriction:** ordinary clients inside the intended access-control boundary cannot produce the argument needed for an operation; only the trusted issuer path can.
10. **Ownership restriction:** consuming and noncopyable APIs prevent reuse or copying.
11. **Lifetime restriction:** nonescapable values plus lifetime dependencies prevent escape beyond the owner.
12. **Compiler mode and fixtures:** strict concurrency, warnings, and compile-fail tests preserve the proof over time.

Do not jump to a stronger rung merely because it is available. Stronger proofs are useful when the prevented failure is likely or costly and the API remains understandable.

## State-Space Arithmetic

Estimate invalid combinations before refactoring.

Three independent booleans represent eight combinations. If the domain has four legitimate phases, an enum cuts the representable state space in half and gives every valid combination a name.

Optionals multiply similarly. A struct with three independent optional payloads represents eight presence combinations before considering payload values. If only three combinations are legal, an enum with three payload-bearing cases is usually clearer.

Use this arithmetic as a diagnostic, not a demand to encode every relation statically. Runtime-dependent facts still need validation.

## Choosing Between Enum, Separate Types, and Typestate

### Use an enum when

- The states are data that must be inspected or switched over.
- A value can move among states repeatedly.
- Storage varies naturally by case.
- The set is finite and owned by the module.
- Serializing the state is useful.

### Use separate concrete types when

- Each phase exposes meaningfully different operations.
- Storage differs substantially between phases.
- Transitions are one-way or infrequent.
- Call sites benefit from simple names more than generic machinery.

Example: `RegistrationDraft -> ValidRegistration -> SubmittedRegistration`.

### Use generic typestate when

- Runtime representation is mostly shared.
- The same generic algorithms operate across states.
- Constrained extensions express a small, stable transition graph.
- State parameters do not leak through most application layers.

Avoid typestate when it creates many generic axes, requires type erasure immediately, or makes ordinary collections and UI state awkward.

## Choosing Between Wrapper and Phantom Tag

### Use distinct wrappers

```swift
struct UserID: Hashable, Sendable { let rawValue: UUID }
struct WorkspaceID: Hashable, Sendable { let rawValue: UUID }
```

This is clearest when domains have different validation, behavior, visibility, or serialization.

### Use a phantom-tagged implementation

```swift
struct Identifier<Domain>: Hashable, Sendable {
    let rawValue: UUID
}
```

This reduces repetition when representation and behavior are genuinely identical. Phantom tags create nominal separation; they do not grant authority or restrict construction of the wrapper. Internal APIs can keep tag types nonpublic. Public APIs may need visible marker types, for which an uninhabited enum is often suitable. If raw construction must be restricted, seal the wrapper initializer or expose a checked factory separately. Never make conformance to a public marker protocol sufficient to grant permission.

## Choosing an Error Model

| Need | Prefer |
|---|---|
| Absence without diagnostics | `Optional` |
| Immediate control-flow failure | `throws` |
| Exact, closed local failure set | `throws(E)` or `Result<Value, E>` |
| Stored, transformed, or combined outcome | `Result` |
| All form or batch errors | Accumulating validation result |
| Open integration boundary | Untyped `throws`, preserving underlying errors as needed |
| Truly infallible generic branch | `Never` |

Typed throws is not automatically “more correct.” It is a source-compatibility commitment and can encourage giant umbrella enums when applied across layers. Use it where exhaustive handling is stable and valuable.

## Choosing Actor, Lock, or Immutable Value

1. Prefer an immutable `Sendable` value when mutation need not be shared.
2. Prefer an actor for logically owned mutable state and asynchronous access.
3. Prefer a lock only when access must remain synchronous or profiling shows actor hops are material.
4. Prefer `OSAllocatedUnfairLock` for an iOS 16 baseline; use `Synchronization.Mutex` only where iOS 18+ is acceptable or availability is isolated.
5. Never hold a lock across `await`, callbacks that can re-enter, or unknown client code.

## Choosing Resource-Lifetime Enforcement

1. Prefer a fixed operation that keeps the handle or pointer private.
2. Use `defer` and cancellation handlers to centralize runtime cleanup on every exit path.
3. Treat an ordinary closure-scoped API as lifetime documentation and cleanup structure, not proof that a copyable value cannot escape.
4. Use noncopyable/nonescapable types only when copies or escape are genuinely invalid and the compiler can see the owner dependency.
5. Specify close failure, partial transition, callback, suspension, and asynchronous cleanup behavior before claiming ownership safety.

## Proof-Closure Checklist

A claimed invariant is closed only when all answers are satisfactory:

- Can a memberwise initializer be synthesized or called?
- Can public stored properties be modified after construction?
- Does `Decodable` invoke validation?
- Does a macro synthesize a bypassing initializer or setter?
- Can test helpers or previews create invalid values and escape into production code?
- Can Objective-C/KVC mutate the representation?
- Can persistence hydrate an object without the checked path?
- Can an external module conform to a marker protocol and forge a state or capability?
- Does an unchecked initializer have more callers than the boundary that justifies it?
- Does a reference-semantic field mutate behind an apparently immutable value?
- Does `@unchecked Sendable` rely on a lock or actor that is actually used for every access?
- Can availability fallback and modern implementations diverge semantically?

## Security Boundary Warning

Types improve API discipline but do not replace authorization, cryptographic verification, server enforcement, sandboxing, or input validation. A capability token is useful only when:

- Construction is controlled.
- The issuer performs the real authorization check.
- The token cannot be replayed beyond its intended scope or lifetime when that matters.
- The protected operation still validates server-side or system-side authority.

Do not advertise a client-side Swift type as a security boundary against a hostile client.

## Overmodeling Signals

Simplify when any of these appear:

- More generic state types than domain states.
- Most functions become generic solely to carry phantom parameters.
- Types are immediately erased into `Any` or `any Protocol` to fit storage.
- A state transition requires several force casts or `unsafeBitCast`.
- Diagnostics no longer identify the domain mistake.
- Compile times materially regress.
- Callers need helper aliases for every combination.
- The invariant is local, low-risk, and already checked once in a short function.
- A three-case enum would communicate more directly.

## Rollback Strategies

- Collapse multiple booleans into one enum without introducing typestate.
- Replace generic state parameters with separate concrete structs.
- Replace phantom unit algebra with explicit conversion functions.
- Keep a nominal ID but remove generic protocol abstractions around it.
- Erase behavior at an outer boundary while preserving typed internals.
- Move a low-value invariant back to a checked boundary and document it.
- Keep the domain model and remove layout-oriented types until profiling justifies them.

The best model is not the one with the strongest theoretical proof. It is the simplest design that reliably prevents the failures the project actually cares about.

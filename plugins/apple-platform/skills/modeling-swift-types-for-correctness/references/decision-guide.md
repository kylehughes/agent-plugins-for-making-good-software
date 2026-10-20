# Decision Guide

Use this reference when the correct construct is unclear, when a proposed design feels too clever, or when reviewing whether an invariant is actually enforced.

## Find the authoritative treatment

Select the problem first, then read only its implementation section. The domain recipes own compound model decisions and contracts; the focused references own the underlying construction rules.

| Problem | Start here |
|---|---|
| Exclusive variants, correlated fields, absence, or cardinality | [Algebraic values](algebraic-and-refined-values.md#sum-types-model-alternatives-directly) |
| Scalar validation or canonicalization | [Validated newtypes](algebraic-and-refined-values.md#validated-newtypes) |
| Validation of saved or network values | [Codable construction](algebraic-and-refined-values.md#codable-and-refined-types) |
| Same-representation IDs or basic staged APIs | [Nominal identity](identity-typestate-capabilities.md#nominal-identity) or [typestate](identity-typestate-capabilities.md#typestate) |
| Issuer-created permission | [Capability construction](identity-typestate-capabilities.md#capability-tokens) |
| Subject-bound evidence, policy indices, or transform composition | [Compound relationships](domain-modeling-recipes.md#rel) |
| Recoverable state transition | [Workflow outcomes](domain-modeling-recipes.md#flow) |
| Typed caches, endpoints, queries, or import pipelines | [Applied model decisions](domain-modeling-recipes.md#app) |
| Public proof boundary, conformance laws, or evolution | [Public contracts](domain-modeling-recipes.md#api) |
| Generic type equations, static dimensions, or typed languages | [Correlated types](generic-proof-recipes.md#gen), [dimensions](generic-proof-recipes.md#sizes-packs), or [expression proofs](generic-proof-recipes.md#adv) |
| Borrowed storage or changing facts across suspension | [Complete ownership section](ownership-effect-recipes.md#ownership) or [reservation and settlement](ownership-effect-recipes.md#isolation) |
| Failure transport or required completion | [Typed errors](ownership-effect-recipes.md#effects) or [completion obligations](ownership-effect-recipes.md#resources) |

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

## Swift Representation Strength

This sequence compares how strongly common Swift representations restrict ordinary callers. It is not an evidence-confidence ladder: tests and compiler fixtures verify a representation against a recorded boundary, but do not make the representation itself stronger.

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

Do not jump to a stronger representation merely because it is available. Stronger restrictions are useful when the prevented failure is likely or costly and the API remains understandable.

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

Choose distinct wrappers when domains differ in validation, behavior, visibility, or serialization. Choose a phantom-tagged implementation when the representation and behavior are genuinely shared. Use [nominal identity and tag sealing](identity-typestate-capabilities.md#nominal-identity) for the examples and construction rules. A tag prevents substitution; [capability construction](identity-typestate-capabilities.md#capability-tokens) is a separate authority decision.

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

Prefer an immutable `Sendable` value when shared mutation is unnecessary, an actor for asynchronous ownership, and a lock for required synchronous access or measured cost. Use [ownership of mutable state](ownership-concurrency-errors.md#concurrency-invariants-begin-with-ownership-of-mutable-state) for construction, availability, reentrancy, and lock rules. For an operation that validates facts before suspension, use [reservation and settlement](ownership-effect-recipes.md#isolation).

## Choosing Resource-Lifetime Enforcement

Start with a fixed operation that keeps its handle private. Escalate to ownership or lifetime types only when copying or escape is itself invalid. Use [resource modeling](security-and-resource-modeling.md#native-and-file-handles-need-one-ownership-story) for cleanup, failure, and cancellation, or [borrowed projections](ownership-effect-recipes.md#ownership) when a client must temporarily access storage.

## Construction-Closure Checklist

Audit every path that constructs, mutates, restores, or bridges the value with the [Swift construction checklist](../SKILL.md#close-swift-construction-and-mutation). Go directly to [validated decoding](algebraic-and-refined-values.md#codable-and-refined-types) for synthesized-decoder claims; private storage alone does not close that route.

## Security Boundary Warning

A type constrains ordinary API callers within an inspected access boundary. Use [security enforcement limits](security-and-resource-modeling.md#types-narrow-misuse-they-do-not-replace-enforcement) when the claim includes authorization, hostile clients, revocation, cryptography, or replay.

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

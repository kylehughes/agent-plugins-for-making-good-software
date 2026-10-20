# Domain modeling recipes

Use this guide when several type mechanisms must cooperate around a domain
boundary. Start with the relevant family, then follow its focused implementation
link. Examples are design sketches, not a new compiler acceptance corpus.
[Feature status](swift-feature-status.md) separates supplied compiler observations
from fresh release evidence. Source correspondence lives in the repository's
integration ledger; the catalog is not a prerequisite for using these recipes.

<a id="alg"></a>
## Algebraic structure: represent the actual alternatives

Use products for facts that coexist, sums for exclusive alternatives, and a
required prefix plus a collection for a minimum cardinality. The invariant is
structural: a value contains precisely the payload required by its selected case.
See [sum and product construction](algebraic-and-refined-values.md#sum-types-model-alternatives-directly)
for the baseline implementation rules.

```swift
enum Patch<Value> {
    case unchanged
    case remove
    case set(Value)
}

struct NonEmpty<Element> {
    let head: Element
    let tail: [Element]

    func map<Output>(_ transform: (Element) -> Output) -> NonEmpty<Output> {
        NonEmpty<Output>(head: transform(head), tail: tail.map(transform))
    }

    func filter(_ keep: (Element) -> Bool) -> [Element] {
        ([head] + tail).filter(keep)
    }
}
```

Construction supplies the head; mapping preserves it; filtering deliberately
forgets nonemptiness. Serialization must distinguish all three patch cases.
Erasing a patch into `Value?` loses a state; exposing an array setter loses the
nonempty invariant. Refining the payload is separate from choosing the case.

For exactly two positions, a named pair is usually clearer than a counted array.
For a small finite key domain, use one property per key or an exhaustive switch;
this establishes coverage, not that evaluation terminates. Compute counts and
flags from authoritative data instead of storing contradictory copies. Recursive
`indirect` enums describe tree grammar, not bounded depth, reference-graph
acyclicity, or terminating interpreters.

`Result` excludes simultaneous success and failure; an outcome enum can also
represent partial completion or cancellation. `Never` removes a normally
constructible payload, but a function returning it can trap or diverge. `Void`
and empty structs carry presence, not authority; caseless tags distinguish types
without supplying values. Decide public enum resilience deliberately and keep
owned switches exhaustive; see [public evolution](algebraic-and-refined-values.md#public-api-resilience).
The cost is more named cases and explicit adapters. Prefer `Optional` when there
really are only two meanings. Test serialization, case selection, and traversal
limits rather than claiming the enum proves business semantics.

<a id="val"></a>
## Refined values: make successful construction carry the input

Use a nominal refined value when callers repeatedly depend on a runtime
predicate. Its invariant is that every admitted instance satisfies the predicate;
the trusted constructor establishes that fact, and the API preserves it. A
boolean validation result loses the connection to the checked input.

```swift
struct NonblankLabel {
    let text: String

    init?(_ text: String) {
        guard text.contains(where: { !$0.isWhitespace }) else { return nil }
        self.text = text
    }
}

// Editable input remains a legitimate separate representation.
struct LabelDraft { var text: String }
```

Keep all constructing paths in the audit, including generated initializers,
fixtures, property-wrapper projections, database hydration, and decoding.
For persisted refinements, use the existing [keyed decoding recipe](algebraic-and-refined-values.md#codable-and-refined-types)
and its historical-payload, predicate-reaching-invalid-input, and round-trip
controls. Do not replace the wire format while repairing validation. A read-only
primitive projection can discard evidence for downstream calls, but does not
mutate the wrapper; a referenced class or writable projection can reopen it.

For cross-field predicates, construct and update one aggregate. A sorted list
must control both comparator policy and element mutation; a unique list must
control equality and hashing. Numeric closure needs scrutiny: dividing positive
integers can yield zero, overflow can trap, and floating values admit NaN,
infinity, and underflow. Return a weaker type or revalidate when an operation is
not closed over the predicate. See [collection invariants](algebraic-and-refined-values.md#collection-invariants)
and [numeric limits](algebraic-and-refined-values.md#numeric-bounds-and-floating-point-traps).

Canonicalization is a domain policy: Unicode normalization, locale casing, path
resolution, and unit conversion are not interchangeable. Record losses and
version dependencies. Generic `Validated<Value, Rule>` wrappers help when several
operations share a stable predicate vocabulary, but a public `Rule` protocol is
open to dishonest witnesses. Seal evidence-producing policies; do not infer
logical implication between distinct rule types. A concrete wrapper is cheaper
when there is only one useful predicate.

Property wrappers mediate local writes; they do not automatically make the
unwrapped primitive an invariant-bearing value. Literal macros can diagnose
constant syntax and emit a refined value; runtime strings still need a checked
constructor. Secret, escaped-HTML, SQL-parameter, and path-component wrappers
belong to their exact sinks: see [trust boundaries](security-and-resource-modeling.md#trust-types-are-interpreter-specific).
Residual obligations are predicate correctness, normalization policy, external
freshness, and every bypass. Costs include adapters, rejection handling, and
migration of stored values; avoid blanket primitive wrapping.

<a id="rel"></a>
## Relationships: bind evidence to the right subject

Use tags and associated-type equations when two individually valid values must
belong together. The invariant is static category or composition compatibility;
runtime identity requires additional data. Start with [nominal IDs](identity-typestate-capabilities.md#nominal-identity),
then preserve relationships through [generic composition](generic-proof-recipes.md#gen).

```swift
struct Point<Space> { let x: Double; let y: Double }
struct Transform<From, To> {
    let apply: (Point<From>) -> Point<To>

    func followed<Next>(by next: Transform<To, Next>) -> Transform<From, Next> {
        Transform<From, Next> { next.apply(apply($0)) }
    }
}
```

The intermediate space must match. The closure remains trusted: it can implement
the wrong matrix, handedness, point/vector convention, or unit conversion. Keep
its constructor inside the trusted geometry layer if arbitrary client witnesses
would invalidate the claim. Erasing both transforms separately loses the shared
axis. A two-space conversion function is simpler when composition is rare.

Apply the same distinction to `Money<Currency>`, exchange-rate direction,
coordinate systems, clock epochs, graph ports, and encoding stages. Type tags do
not establish rounding laws, rate freshness, a future deadline, acyclic graphs,
correct cryptography, or authentic ciphertext. See [units](algebraic-and-refined-values.md#units-and-dimensions),
[money](algebraic-and-refined-values.md#money), and [trust states](identity-typestate-capabilities.md#trust-and-taint-states).

A tenant tag distinguishes declared tenant *types*, not every tenant instance.
An opaque return type likewise does not create a fresh brand per runtime call.
For object-bound permission, privately store the subject, authority, revision,
and permitted operation together, or return a closure bound to the checked
subject. Settlement compares identity/version atomically at the authority.
Never accept an unrelated resource beside a `Permission<Resource>` and assume
the generic parameter binds their runtime identities.

`ObjectIdentifier`, stable database keys, and `Identifiable` answer different
identity questions. A mutable or recomputed ID can type-check while breaking
cache or UI assumptions. Policy-indexed data also depends on the actual
comparator, codec, locale, or schema instance; freeze or version that policy.
Construction binds those values, mutation revalidates them, and erasure retains
the axes needed later. Costs are propagating tags through APIs and maintaining
conversions; add only relationships that reject a plausible mix-up.

<a id="flow"></a>
## Workflows: preserve ownership on failure

Use separate state types when available operations change after a transition.
Use a phantom state parameter only when multiple stages share meaningful storage.
The invariant is which local operations are callable, not that a workflow ever
finishes. Existing [typestate and builders](identity-typestate-capabilities.md#typestate)
cover the basic choice.

```swift
enum Attempt<Success: ~Copyable, Recovery: ~Copyable, Failure: Error>: ~Copyable {
    case success(Success)
    case failure(Failure, Recovery)
}

// Signature sketch: the failure branch retains the still-valid draft.
// consuming func validate()
//   -> Attempt<Submission<Ready>, Submission<Draft>, ValidationFailure>
```

A consuming transition transfers the resource into exactly one outcome. Its
private constructors and validation implementation establish the next state.
Return the old resource on a recoverable failure; an optional result instead
permits it to be lost. A thrown error is not a general transport for a noncopyable
recovery handle. Copyable snapshots may retain an earlier stage; choose
noncopyability only when reuse of that handle would itself violate the contract.

Returning a recovery handle makes retry possible; the caller may still drop it.
Every consuming-workflow assessment must distinguish local reuse prevention,
recovery availability, and eventual completion. Noncopyability does not require
submission, retry, or success. Server deduplication can prevent duplicate effects,
but it does not establish that any request eventually succeeds.

Show the complete transition result, including its terminal success payload.
Intermediate verified or ready states are not a substitute for the receipt or
owned result returned after the effect succeeds. Name what callers receive on
success, recoverable failure, and any uncertain outcome; do not leave the final
outcome type undefined while claiming the recovery contract is complete.

A required-field builder is useful for staged discovery, but a normal initializer
is simpler when the required data is already available. Keep correlated phases
in a sum with state-specific payloads; independent capability axes are appropriate
only when their cross product is valid. A generic shell full of irrelevant
optionals can still contain inconsistent internal storage.

Privately minted capabilities can attenuate read/write or account authority.
Do not expose the broader handle through unwraps or captured closures. Consume
one-shot local permits, and recheck revocation at the authoritative operation.
Progressive information enrichment produces richer snapshots, not perpetually
fresh facts. A closed event/reducer algebra makes branches inspectable; a general
`reduce(State, Event)` still admits every pair unless its input types restrict it.

Session-style send/receive/choose/close APIs can constrain a local sequence and
carry typed branches. They do not inherit research proofs of duality, fairness,
progress, or deadlock freedom. Resource identity, retries, abandonment, peer
behavior, and cancellation remain runtime obligations. See [resource protocols](ownership-effect-recipes.md#resources).
Erasure should happen after related stages are packaged; otherwise it discards
the phase evidence. Costs are state proliferation and recovery plumbing; keep a
plain enum when operations need dynamic switching rather than static exclusion.

Make the evidence plan concrete even when the API is only a sketch. Name a valid
transition and a misuse the chosen types reject; for a consuming handle, pair
the accepted transition with reuse of that handle under the same ownership-checking
phase and flags. Specify a runtime scenario that forces a recoverable failure,
checks that the returned resource remains usable, then cancels an in-flight
operation and observes its outcome and retained state. Mark unrun checks pending.
These checks do not establish remote idempotency or recovery after a process crash;
those require service and persistence evidence.

<a id="app"></a>
## Applied architecture: keep shape and domain evidence separate

Use typed endpoints, caches, queries, commands, and pipelines when adapters are
where relationships get lost. The invariant is that the operation's declared
input, output, failure, and policy remain correlated across a seam. It is not a
claim that the remote system obeys the local model.

```swift
protocol Request {
    associatedtype Output
    func decode(_ bytes: [UInt8]) throws -> Output
}

struct CacheKey<Value> { let namespace: String; let name: String }
// A heterogeneous cache's implementation must maintain the key/value relation.
// Public get<Value>(for: CacheKey<Value>) -> Value? preserves that relation.
```

Generated DTOs establish schema shape. Decode them, validate domain constraints,
then produce the request's refined output. Keep HTTP status, authentication,
server drift, unknown variants, and nullable fields explicit. Typed SQL adds
row/value and projection relationships; nullable joins and aggregate phases
need their own representations. Transactions, uniqueness, authorization, query
meaning, and execution cost still belong to the database and interpreter.

Use these task-specific owners rather than copying their implementation rules:

| Task | Recipe and retained obligation |
|---|---|
| Forms and submission | [Draft then validated command](ui-state-navigation-and-effects.md#forms-need-raw-editing-state-and-validated-submission-state); recheck inventory or identity at submission. |
| Navigation and restoration | [Routes](ui-state-navigation-and-effects.md#navigation-is-a-closed-domain-when-the-app-owns-it); validate deep links, saved payloads, and legal route sequences. |
| Loading and refresh | [UI phases](ui-state-navigation-and-effects.md#model-ui-phases-as-data); preserve valid stale-content-plus-error combinations and request identity. |
| Dependency injection | [Operation witnesses](advanced-generics-and-protocols.md#witness-structs-versus-protocols); require dependencies at construction, then test their behavior. |
| Configuration | Use separate static configuration types only for static facts; runtime flags need a checked capability or an enum of configurations. |
| Caches and events | [Typed keys](identity-typestate-capabilities.md#typed-keys); heterogeneous storage casts, key collisions, schema versions, expiration, handler registration, delivery, and idempotency remain trusted. |
| Import pipelines | Raw → parsed → normalized → validated → deduplicated → committed; merging unique batches can reintroduce duplicates, so revalidate the combined result. |
| Image/media work | [Relationship tags](#rel) connect dimensions, color space, orientation, format, and alpha convention; validate actual layout and conversion math. |
| Stateful connections | [Recovering transitions](#flow); reconcile remote disconnects and revocation with the local state. |
| Queries and render plans | [Typed languages](generic-proof-recipes.md#dsl); keep the interpreter small and test generated meaning. |

Construct cache keys and codec descriptors together under a trusted namespace;
mutation must preserve that pairing. Erasure can support heterogeneous storage
inside one audited adapter, but repeated casts throughout clients lose the
benefit. Costs are adapter code, schema migration, and larger signatures. A
concrete service with named methods is simpler when there are few operations.

<a id="api"></a>
## Public boundaries: preserve the claim clients actually need

Use this family when publishing an invariant-bearing type or changing its public
surface. The invariant is a named set of forbidden client operations under a
recorded access and build boundary. It applies only while all constructors and
mutation paths preserve the representation.

```swift
struct DraftDocument { var title: String }
struct ReadyDocument {
    let title: String
    init?(draft: DraftDocument) {
        guard !draft.title.isEmpty else { return nil }
        title = draft.title
    }
}
// A publishing API accepts ReadyDocument; the editor accepts DraftDocument.
```

Keep unchecked construction and external adaptation in a small trusted core.
Choose structs, final classes, or non-open interfaces when client overrides would
break the invariant. A public protocol still allows independent conformers.
Use constrained extensions for conditional operations, and omit impossible
operations instead of implementing traps. An unavailable overload with a clear
migration message can help existing clients; it does not validate its replacement.

Avoid convenient conformances that promise unsupported operations or laws:
`Numeric`, mutable collection protocols, literals, and raw-value APIs can reopen
construction. Audit setters, writable key paths, `inout` callbacks, property
wrappers, dynamic member forwarding, and mutable references at the aggregate
boundary. Exclusive access protects access, not cross-field predicates. Package
correlated values before erasure and preserve the minimal evidence clients need.

Use the [existing verification contract](../SKILL.md#verify-swift-claims) for
positive and negative compiler controls, phase selection, runtime checks, and
explicit limits. Record language mode, isolation defaults, imports, warning
policy, experimental flags, SDK, and deployment independently. Warnings-as-errors
is build policy, not a new type guarantee. Inventory unchecked sendability,
unsafe memory, raw constructors, force casts, and legacy bridges as trusted edges.

Test semantic laws separately from signatures: equality/hash consistency,
normalization, codec round trips, optic laws, and interpreter meaning. A generated
finite model can support stronger checks only for its faithful restricted
specification; code generation does not prove the generator. See [verification
and migration](testing-migration-and-review.md).

Measure diagnostics, clean/incremental builds, specialization size, and the
number of generic axes callers must carry. A concrete representation or runtime
check is the simpler alternative when proof machinery adds no useful rejection.
Public ABI and source evolution remain review obligations even when all local
clients compile. Compilation establishes neither arbitrary correctness nor
liveness.

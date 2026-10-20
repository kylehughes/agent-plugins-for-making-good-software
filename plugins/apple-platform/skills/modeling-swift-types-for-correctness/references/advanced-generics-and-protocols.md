# Advanced Generics and Protocol Relationships

Use this reference when the invariant is a relationship among types, associated values, implementations, arity, or generated API—not merely a property of one stored value.

This guide owns language mechanisms and API choices. For an applied invariant assessment, read the relevant recipe section as well:

- [Preserved correlations](generic-proof-recipes.md#gen) and [abstraction boundaries](generic-proof-recipes.md#abs) when related inputs, outputs, or implementations cross an API.
- [Static sizes and packs](generic-proof-recipes.md#sizes-packs) when shape is the claimed proof; the section separates dimensions from numerical results, runtime index bounds, and layout.
- [Typed DSLs](generic-proof-recipes.md#dsl) for generated languages and updates; [explicit proof evidence](generic-proof-recipes.md#adv) for recursive result sorts, equality witnesses, and indexed structures.
- [Specialized encodings](generic-proof-recipes.md#gap) for typed reconstruction, labels, information flow, or resource budgets.

## Start With Closed Versus Open World

Use an enum when the module owns a finite set of alternatives and consumers should switch over them. Use a protocol when third parties or independent modules must add implementations and behavior is the abstraction.

A protocol is not automatically more extensible in a useful way. It also introduces witness selection, existential erasure, conformance visibility, resilience, and type-erasure costs. Do not replace a four-case owned enum with four empty marker conformances.

Use a struct of closures when behavior is the only relationship and nominal conformance adds no value.

## Generic Parameters Preserve Relationships

A generic parameter says all uses refer to one concrete type chosen at the call site:

```swift
func render<R: Renderer>(_ renderer: R, model: R.Model) -> R.Output {
    renderer.render(model)
}
```

The compiler knows the model and output correspond to the same renderer. Replacing parameters with unrelated existentials may erase that relation.

Prefer generic parameters for algorithms. Prefer existentials for heterogeneous storage, plugin boundaries, and dynamic dispatch. Prefer opaque `some` results when the implementation chooses one hidden concrete type.

## Same-Type Requirements

Use same-type constraints to express equality among associated types or generic parameters:

```swift
func concatenate<L: Sequence, R: Sequence>(
    _ lhs: L,
    _ rhs: R
) -> [L.Element]
where L.Element == R.Element {
    Array(lhs) + Array(rhs)
}
```

Constrain only the operation that needs the relation. Moving every constraint to the enclosing type reduces reuse and worsens diagnostics.

A same-type requirement is static equality, not conversion. When conversion is legitimate, model it explicitly rather than forcing unrelated representations to share a type.

## Primary Associated Types

Primary associated types make important caller-supplied relationships visible in protocol spelling:

```swift
protocol Store<Element> {
    associatedtype Element
    func load() -> Element
}

struct UserStore: Store {
    func load() -> User { User() }
}
```

The angle-bracket list does not make the protocol itself a nominal generic type. It identifies associated types that clients commonly bind.

Use a primary associated type when:

- Callers frequently constrain that associated type.
- The relation is central to the protocol's identity.
- The spelling improves generic, opaque, or existential APIs.

Do not mark every associated type primary. Implementation-selected helper types generally remain ordinary associated types.

## Constrained Existentials

A constrained existential preserves selected associated-type information while erasing the concrete conformer:

```swift
func readUser(from store: any Store<User>) -> User {
    store.load()
}
```

This is useful for heterogeneous storage or dynamic injection when the preserved axis is enough for clients.

It does not recover all static relationships. If two operations must refer to the same hidden conforming type, a generic parameter or explicit type eraser may still be required.

Generic and existential syntax is available in the current Swift 6 baseline, but public ABI, library-evolution, and runtime support can still constrain a design. Verify the iOS 16 deployment target and binary-client boundary independently from source syntax.

## `some` Versus `any`

Use `some P` when:

- The callee chooses one concrete type.
- Static specialization and associated-type relationships should remain available.
- The concrete identity should be hidden from source clients.

Use `any P` when:

- Values of different conforming types share storage or flow.
- Dynamic replacement is an actual requirement.
- The erased protocol requirements are sufficient.

Use a generic parameter when the caller chooses the type or multiple arguments/results must stay related.

Do not treat `some` as a spelling for “any conformer.” One opaque declaration returns one underlying type on every path, unless the language construct explicitly provides a type-erasing builder.

Do not treat `any` as free. It may allocate, inhibit specialization, hide conformances such as `Equatable`, and lose associated-type relationships.

## Implicitly Opened Existentials

Modern Swift can temporarily open many existential values when passing them to generic functions. This improves ergonomics but does not turn an existential into a named concrete type that can freely escape.

Design public APIs around the relationship you need, not around whether one compiler happens to open a particular expression. If the result must preserve the input's hidden type across storage or another call, keep the operation generic or provide an explicit eraser/witness.

Compile representative call sites with the project's selected current compiler, because existential opening can still produce surprising diagnostics or inference at API boundaries.

## Type Erasure Should Name What Remains

Erase only the axes callers do not need. Keep important input, output, failure, identity, or isolation types explicit.

```swift
struct AnyTransformer<Input, Output>: Sendable
where Input: Sendable, Output: Sendable {
    private let transform: @Sendable (Input) async throws -> Output

    init(
        _ transform: @escaping @Sendable (Input) async throws -> Output
    ) {
        self.transform = transform
    }

    func callAsFunction(_ input: Input) async throws -> Output {
        try await transform(input)
    }
}
```

An eraser must have a complete implementation path. Never hide an impossible generic relationship behind `fatalError`, force casts, or a placeholder closure.

Check captures for `Sendable` and lifetime safety. A `@Sendable` closure field does not make captured mutable reference state safe by itself.

## Witness Structs Versus Protocols

A witness struct stores the operations that matter:

```swift
struct Clock: Sendable {
    let now: @Sendable () -> ContinuousClock.Instant
    let sleep: @Sendable (Duration) async throws -> Void
}
```

Use this pattern when:

- Behavior is injected as data.
- There is no meaningful public conformance ecosystem.
- Associated types would be erased immediately.
- Tests need small, local substitutions.

Use a protocol when nominal conformance, generic algorithms, or independent conformers are important. Avoid forcing every dependency into either style dogmatically.

## Protocol Extension Dispatch Hazard

A method declared only in a protocol extension is statically selected when the expression's static type is the protocol or a protocol constraint; it is not a dynamically dispatched requirement.

```swift
protocol Renderer {}

extension Renderer {
    func name() -> String { "default" }
}

struct HTMLRenderer: Renderer {
    func name() -> String { "html" }
}

let renderer: any Renderer = HTMLRenderer()
renderer.name() // "default"
```

If polymorphic behavior is required, declare the member in the protocol:

```swift
protocol Renderer {
    func name() -> String
}
```

Default implementations are then witnesses that conformers may replace. Audit extension-only members before erasing to `any Protocol`.

## Conditional Conformance

Conform only when the stored representation supports the promise:

```swift
struct Tagged<Tag, RawValue> {
    let rawValue: RawValue
}

extension Tagged: Equatable where RawValue: Equatable {}
extension Tagged: Hashable where RawValue: Hashable {}
extension Tagged: Sendable where RawValue: Sendable {}
```

Do not add unconditional manual `Hashable`, `Codable`, `Sendable`, or `Comparable` implementations to avoid generic constraints. That often hides lossy behavior or an unsound concurrency claim.

Be careful with public conditional conformances: adding another conformance later can affect overload resolution and client behavior.

## Constrained Methods Versus Constrained Types

Prefer a broadly useful type and narrow operations:

```swift
struct Pair<First, Second> {
    let first: First
    let second: Second
}

extension Pair where First == Second {
    func homogeneousArray() -> [First] {
        [first, second]
    }
}
```

Do not constrain `Pair` itself to equal element types unless heterogeneous pairs are invalid by definition.

This keeps invariant constraints distinct from convenience-algorithm constraints.

## `Self` Requirements and F-Bounded Relationships

Use `Self` when an operation fundamentally returns or consumes the same conforming type:

```swift
protocol Mergeable {
    func merged(with other: Self) -> Self
}
```

Such requirements preserve a strong relationship in generic code but limit existential use. That is not automatically a defect; it may accurately describe the operation.

Do not weaken a correct `Self` relationship to `any Protocol` merely to make heterogeneous storage compile. Add a separate erased operation if the domain actually supports cross-type merging.

## Parameter Packs

Parameter packs abstract over heterogeneous arity. Use them when one algorithm genuinely relates an arbitrary number of distinct types, such as zipping heterogeneous inputs, dependency aggregation, or typed argument forwarding.

Do not use packs to encode a small finite set of feature phases or required form fields. Concrete overloads, a tuple/domain struct, or a runtime collection is usually clearer.

Before publishing a pack-based API:

- Verify the selected current compiler and realistic call sites.
- Verify runtime availability and ABI constraints independently.
- Inspect diagnostics at realistic call sites.
- Measure compile time and code size.
- Provide a concrete façade when most clients use one or two shapes.

Pack syntax and capabilities continue to evolve; isolate sophisticated use from business-domain APIs unless it creates a material correctness or maintenance gain.

Swift 6.4 supports ordinary copyable parameter-pack elements. It does not establish noncopyable tuples or `each T: ~Copyable`; use a nominal noncopyable aggregate for that ownership boundary. See [Swift feature status](swift-feature-status.md#release-14).

## Integer Generic Parameters and Fixed Size

Integer generic parameters and `InlineArray` can express compile-time cardinality and fixed inline storage, but the standard-library type has Apple-platform runtime availability beginning at iOS 26.

Swift 6.4 does not provide general symbolic arithmetic or refinement constraints. The accepted literal-expressions design remains experimental and the supplied 6.4.x probes do not establish a usable implementation even with its flag. Keep runtime validation for bounds and use [Swift feature status](swift-feature-status.md#release-12) before adopting preview syntax.

Do not use an integer generic parameter merely to model a runtime business bound. `Maximum<20>` does not validate an array loaded from JSON; construction still needs a runtime check.

Use fixed-size generic machinery when:

- Algorithms are naturally generic over a compile-time literal size.
- Layout or allocation is measured and relevant.
- Deployment and ABI constraints are acceptable.
- Diagnostics remain understandable.

For an iOS 16 public domain API, prefer a nominal struct, tuple hidden behind a wrapper, or validated collection unless the modern type is isolated behind availability.

## Key Paths and Typed Access

A key path preserves a `Root`/`Value` relationship:

```swift
struct Field<Root, Value> {
    let keyPath: WritableKeyPath<Root, Value>
}
```

This is useful for local form bindings, projections, sort descriptors, and typed configuration. It does not automatically make access thread-safe, persistable, or stable across schema changes.

Audit key paths that cross isolation. Sendability rules for key-path literals and captures depend on compiler/language settings. Prefer performing mutation on the owning actor rather than sending writable key paths and mutable roots across tasks.

Foundation predicates and persistence query macros add separate availability and expression-subset constraints. A Swift key path that compiles in memory may not be representable by a database query engine.

## Macros and Generated Invariants

Macros can generate wrappers, memberwise APIs, conformances, case accessors, builders, and validation code. Treat generated declarations as ordinary public surface during review.

Audit:

- Every initializer and setter.
- Access levels.
- Synthesized `Codable` and persistence behavior.
- Generic constraints and conditional conformances.
- `Sendable` and actor isolation.
- Availability on generated declarations and referenced symbols.
- Public names, symbol graphs, ABI, and diagnostics.
- Expansion changes when the macro dependency is upgraded.

A macro can validate a source literal at compile time. It cannot prove an arbitrary runtime string is valid; keep the checked runtime constructor.

Prefer peer/member macros that produce inspectable, unsurprising API. Avoid a macro when the generated type-system machinery is harder to review than the repeated code it replaces.

## Public Protocol Evolution

For source and binary libraries, protocol changes are commitments. Consider:

- Adding a requirement may break existing conformers unless a compatible default and resilience model applies.
- Adding an associated type can affect conformances and existential use.
- Changing actor isolation or `Sendable` constraints changes source behavior under Swift 6.
- Primary-associated-type order is API spelling.
- Exposing concrete generic implementation types can lock in layout and specialization choices.
- Extension-only helpers do not become dynamic requirements.

Prefer a small semantic requirement set. Add convenience algorithms in extensions only when their dispatch semantics are intentional.

## Diagnostic and Build-Cost Budget

A generic proof is not successful if ordinary misuse produces incomprehensible diagnostics or every feature boundary requires erasure.

Measure:

- Number of generic axes carried through call sites.
- Error quality for likely mistakes.
- Incremental and clean build time.
- Binary specialization/code size.
- Need for `Any...` wrappers.
- Public signature complexity.

Collapse axes that no longer remove a callable invalid operation. Separate concrete state types often outperform a universal generic shell in clarity.

## Review Checklist

- Is the domain closed enough for an enum instead of a protocol?
- Which relationships must remain statically equal?
- Does a generic parameter, opaque result, existential, or witness struct fit who chooses the implementation?
- Are primary associated types limited to caller-important axes?
- Does existential erasure lose a relation later recovered by a cast?
- Are protocol-extension-only methods expected to dispatch dynamically?
- Are conformances conditional on the stored representation's real capabilities?
- Are constraints placed on the narrowest operation that needs them?
- Does a `Self` requirement accurately prevent heterogeneous use?
- Are parameter packs or integer generic parameters solving a natural generic problem rather than showing sophistication?
- Are macro expansions audited as API?
- Have deployment, compiler, runtime, ABI, diagnostics, and build cost all been checked?

# Generic Proof Recipes

Use these recipes when a domain rule relates types, arity, syntax, or proof evidence rather than one validated scalar. Start with the smallest ordinary Swift model that rejects the named misuse. Move to an encoding here only when an enum, nominal wrapper, checked initializer, or concrete state type cannot carry the relationship without casts or repeated runtime checks.

This reference describes proof shapes and their trust boundaries. Check [Swift feature status](swift-feature-status.md) before using syntax that depends on a particular toolchain or runtime. For the baseline rules on generic parameters, protocols, existentials, type erasure, and diagnostics, use [Advanced generics and protocol relationships](advanced-generics-and-protocols.md).

Code snippets show the relevant type shape and omit surrounding domain declarations. They are design sketches, not compiler evidence. Compile the exact production form with its selected toolchain and settings.

For every recipe, record four things:

1. The invalid construction or operation the compiler should reject.
2. Which constructors, mutations, decoders, and generated declarations may issue the required types or evidence.
3. Which relationships must survive an existential, closure, persistence, or foreign boundary.
4. Which semantic laws remain runtime tests, external checks, or trusted implementation obligations.

| Problem | Start here | Prefer the simpler alternative when |
|---|---|---|
| Inputs, outputs, or implementations must share types | [Generic relationships](#gen) | A concrete function or owned enum has the whole relationship |
| Runtime heterogeneity must retain selected relationships | [Abstraction and erasure](#abs) | One generic call can keep the concrete type visible |
| Shape or heterogeneous arity belongs in the interface | [Static sizes and packs](#sizes-packs) | The shape comes from runtime data or has only a few fixed cases |
| Users construct a constrained language or schema | [Typed DSLs](#dsl) | A validating initializer or ordinary parser already closes the boundary |
| Evidence must travel as data or syntax must carry a result sort | [Advanced proof encodings](#adv) | A closed enum, associated family, or concrete interpreter suffices |
| The problem needs a specialized proof pattern | [Additional encodings](#gap) | A domain-specific struct, enum, fold, or generated API is clearer |

<a id="gen"></a>
## Preserve Generic Relationships

Use a generic relationship when correctness depends on two or more positions choosing compatible types. The invariant is an equation or capability requirement in the generic signature: for example, a producer's output equals a consumer's input, a repository's identifier equals its entity's identifier, or an operation is available only when its payload is decodable.

Read the baseline sections on [generic parameters](advanced-generics-and-protocols.md#generic-parameters-preserve-relationships), [same-type requirements](advanced-generics-and-protocols.md#same-type-requirements), [primary associated types](advanced-generics-and-protocols.md#primary-associated-types), [conditional conformance](advanced-generics-and-protocols.md#conditional-conformance), [constrained methods](advanced-generics-and-protocols.md#constrained-methods-versus-constrained-types), and [`Self` requirements](advanced-generics-and-protocols.md#self-requirements-and-f-bounded-relationships). Those sections own the language rules; the recipes below show how to apply them.

### Connect a pipeline at its joints

Name the shared type once and place the equation at the narrowest composition point:

```swift
protocol Stage<Input, Output> {
    associatedtype Input
    associatedtype Output
    func run(_ input: Input) -> Output
}

struct Then<First: Stage, Second: Stage>: Stage
where First.Output == Second.Input {
    let first: First
    let second: Second

    func run(_ input: First.Input) -> Second.Output {
        second.run(first.run(input))
    }
}
```

This rejects a connection with the wrong intermediate type. It does not prove that either stage computes the intended value. Keep constraints on `Then` rather than constraining every `Stage`, and use a primary associated type only for an axis callers regularly bind.

Recursive associated-type constraints work when a family member must itself support a related interface. Stop before the signature becomes a type-level program: named intermediate protocols or concrete adapters usually produce better diagnostics.

### Ask for the smallest capability

Use a protocol refinement or composition for the operations the algorithm needs. Put behavior that must dispatch by conformer in a protocol requirement; an extension-only overload is not a substitute. See [Protocol extension dispatch hazard](advanced-generics-and-protocols.md#protocol-extension-dispatch-hazard).

Use constrained members for conditional operations and conditional conformances for promises inherited from stored types. A policy with different semantics should be a nominal wrapper or policy parameter rather than a competing conformance. A metatype can connect a request for `T.self` to a `T` result, but it cannot turn runtime data into a fresh static type.

### Pass an interpretation as data

An operation dictionary is useful when the same value type needs several local interpretations and nominal conformance would be global:

```swift
struct Ordering<Value> {
    let precedes: (Value, Value) -> Bool
}
```

The type parameter connects the operation to `Value`; private construction can also bind an issued witness to a policy. The function may still violate transitivity or disagree with another function in the dictionary. Test those laws or issue the witness from a checked kernel when callers rely on them.

**Boundaries and cost.** Keep constructors for policy tags and evidence restricted. Mutation must not replace a related component with a value whose type or policy no longer agrees. Erasing related members separately loses the equation; package them first or use the [abstraction recipes](#abs). Generic signatures establish declared type relationships, not value equality, object identity, authorization, purity, termination, or semantic laws. Count generic axes, inspect misuse diagnostics, and measure build time and specialization before making a relationship public. A concrete adapter is the rollback when the proof surface costs more than the misuse it removes.

<a id="abs"></a>
## Abstract Without Erasing the Proof

Use abstraction when implementations vary or should remain hidden, but callers still need part of their type relationship. The invariant is that every operation crossing the abstraction boundary retains the axes needed for later composition.

Start with the baseline choice among [generic parameters, opaque results, and existentials](advanced-generics-and-protocols.md#some-versus-any), then choose the smallest erasure boundary:

- Return `some P` when the implementation chooses one hidden concrete type and callers need its stable identity.
- Use a named generic parameter when the caller chooses the type or multiple positions must share it. Two independent `some P` parameters do not express equality.
- Use `any P<Axis>` when runtime heterogeneity is required and the preserved primary associated types are sufficient.
- Let an [implicitly opened existential](advanced-generics-and-protocols.md#implicitly-opened-existentials) do local generic work only when the hidden type does not need to escape.
- Use a closed enum when all legitimate alternatives are owned and finite.

### Package before erasing

Suppose an import job has a source, decoder, and sink that must agree on `Record`. Keep the equality inside one package and erase the package's operation:

```swift
struct ImportJob<Record> {
    let next: () throws -> Data?
    let decode: (Data) throws -> Record
    let save: (Record) throws -> Void

    func runOne() throws {
        if let data = try next() { try save(decode(data)) }
    }
}

struct AnyImportJob {
    private let run: () throws -> Void

    init<Record>(_ job: ImportJob<Record>) {
        run = job.runOne
    }

    func runOne() throws { try run() }
}
```

The erased API retains the coherent operation while hiding `Record`. Exporting the three closures independently would let clients recombine unrelated jobs. A custom eraser should likewise keep every semantic axis callers still need, such as input, output, failure, isolation, ownership, or mutation authority. Follow [Type erasure should name what remains](advanced-generics-and-protocols.md#type-erasure-should-name-what-remains).

### Eliminate instead of exposing

A visitor, fold, or generic method can let clients compute a public result without extracting the hidden representation. This is useful for a heterogeneous store whose keys each select a `Value`, or for a closed witness issued behind an open read interface. If the alternatives are finite, an enum and exhaustive switch are usually easier to inspect than a visitor.

**Boundaries and cost.** Restrict witness issuance if possession claims validation or authority; a publicly conformable proof protocol is forgeable. Audit captured state, `Sendable`, isolation, ownership, error precision, and invocation count in closure-based erasers. A type-indexed dictionary still has a private cast and key-identity boundary, and lookup remains optional unless completeness is separately established. Erasure does not restore a relation already discarded, prove two hidden types equal, or prove the erased operations agree semantically. Prefer one generic operation until storage or dynamic replacement makes erasure necessary.

<a id="sizes-packs"></a>
## Model Static Sizes and Heterogeneous Packs

Use a static size when a literal dimension is part of the API contract. Use a parameter pack when one operation must preserve an arbitrary number of positionally related, differently typed values. Check [Swift feature status](swift-feature-status.md) before adopting either spelling, and follow the baseline [parameter-pack](advanced-generics-and-protocols.md#parameter-packs) and [fixed-size](advanced-generics-and-protocols.md#integer-generic-parameters-and-fixed-size) decisions.

The invariant is equality of declared dimensions or positional pack shapes. It is not arithmetic correctness, bounds safety for arbitrary runtime indexes, or proof that runtime input has the advertised shape.

In a shape-based design assessment, name the remaining checks separately: numerical results, dynamic-index bounds, storage layout or strides, and validation of decoded dimensions. Matching dimensions and element counts do not establish an indexing formula or memory-layout convention. Give a concrete numerical-result test alongside the compatible and incompatible shape controls.

A valid `Rows × Columns` shape still admits an invalid runtime row such as `-1` or `Rows`. State how subscripts and kernel loops establish each index bound; a shape precondition alone does not prove that every access is in bounds. Keep this obligation visible even when indexing remains inside a private implementation.

### Carry a shape equation

The following is illustrative syntax; compile it under the selected toolchain before treating it as production code:

```swift
struct Matrix<let Rows: Int, let Columns: Int> {
    // Fixed-size storage selected for the supported toolchain and runtime.
}

func multiplied<let R: Int, let K: Int, let C: Int>(
    _ lhs: Matrix<R, K>,
    _ rhs: Matrix<K, C>
) -> Matrix<R, C> {
    // Audited numerical implementation.
}
```

Sharing `K` rejects incompatible inner dimensions. The body can still return wrong numbers. A constrained operation such as `where Rows == Columns` can expose only square-matrix behavior, but arbitrary inequalities and arithmetic propositions need runtime validation or a different proof system.

For a runtime index, validate once into an immutable `BoundedIndex<N>` with a restricted initializer, then accept that branded index with storage carrying the same `N`. The trusted subscript still owes memory safety. The brand proves a bound, not membership in one mutable collection instance; resizing or reordering needs generation or identity evidence.

### Preserve positional correlation

A heterogeneous product can store `(repeat each Field)`. Repeating a pack of transformations together with `(each Transform).Input` and `(each Transform).Output` preserves per-position input and output types. Statement-level pack iteration can then run an operation valid for every element under the declared constraints.

Packs are compile-time shapes, not runtime collections. They do not provide runtime indexing into an arbitrary position, sorting or filtering of types, label matching, or a type shape invented from decoded data. For a small fixed arity, use overloads or a domain struct. For dynamic input, validate into a runtime collection. A recursive `HCons<Head, Tail>` or nominal `Zero`/`Successor<N>` witness can express inductive positions, but use it only when recursive proof structure pays for its boilerplate and compiler cost.

**Boundaries and cost.** Validate runtime sizes before construction, keep fixed storage and branded indices immutable or centrally mutated, and preserve pack shape across every erasure. Reifying a static size as `Int` prevents duplicated constants but does not promote runtime arithmetic back into a type. Verify layout and availability separately from type checking. Measure diagnostics, compile time, code size, and public signature readability; tuple wrappers, hidden fixed storage, and checked arrays are the usual simpler alternatives.

<a id="dsl"></a>
## Build a Typed DSL Around Its Boundary

Use a typed DSL when many callers construct the same constrained language: a parser, route, query, document, schema operation, patch, or staged command program. The invariant is that only the grammar and context combinations represented by constructors can produce the finished language value.

### Separate syntax, refinement, and interpretation

Treat the pipeline as four different obligations:

```text
untrusted text or schema
    -> recognized syntax
    -> refined domain values
    -> typed program or update
    -> interpreted effect
```

A result builder can restrict admitted expressions; state-indexed partial results can restrict ordering and require completion. Branch and loop support needs deliberate combination rules. A broad `buildExpression` or early `Any` erasure reopens the grammar.

Typed parser combinators connect recognized structure to result types. Require complete consumption when the contract is a whole document. A typed regex capture removes capture-index casts but does not prove that the regex recognizes the intended language. Parser-printers and codecs share structure in both directions; round-trip, canonicalization, ambiguity, and losslessness remain laws to test.

### Keep the domain boundary after generation

Schema-generated network or database types reflect the generator's input, not necessarily the deployed system or the app's stronger rules. Convert generated primitives into checked domain values. A refined aggregate should decode through its validating constructor or through a raw DTO followed by conversion; synthesized decoding does not discover an unrelated smart initializer.

A typed SQL DSL can track table scopes, columns, nullability, and projections. A typed route enum can connect each destination to its parameters and printer. Both still receive untrusted runtime input, and neither establishes authorization, deployed-schema agreement, transaction behavior, or server semantics.

### Restrict updates and encoding contexts

Use `KeyPath<Root, Value>` for a read projection and expose a writable key path only when arbitrary field mutation preserves the aggregate invariant. Case paths and prisms retain an enum case's payload type but are partial. Lenses and type-changing optics preserve source/focus relationships; their laws and refinement preservation remain implementation obligations.

Model patches as case-specific commands or a three-way `Field<Value>` (`unchanged`, `remove`, `set(Value)`):

```swift
enum ProfileUpdate {
    case rename(DisplayName)
    case setBio(Bio)
    case removeBio
}

extension Profile {
    func applying(_ update: ProfileUpdate) throws -> Profile {
        // Re-enter the aggregate's validating constructor.
    }
}
```

The enum rejects a raw `String` and makes deletion distinct from no change. The application method still must preserve cross-field rules. For rendering, distinguish HTML text, attributes, URL segments, query components, and bound SQL parameters. A generic `Sanitized` wrapper erases the encoding context that makes the value safe to place.

Macros and generators may emit constructors, mappings, or witnesses, but generated declarations are part of the construction surface. Audit inputs, expansion, access control, setters, decoding, raw escape hatches, and version binding.

**Residual obligations and cost.** The compiler checks the grammar encoded by builder methods, combinators, constructors, and generated declarations. It does not prove complete parsing, deployed-system truth, codec or optic laws, authorization, correct escaping implementations, interpreter behavior, or accessibility and semantic validity of rendered documents. Prefer an enum plus parser, an ordinary checked initializer, or generated nominal types when they reject the same errors with less machinery.

<a id="adv"></a>
## Carry Explicit Proof Evidence

Use advanced encodings when a relationship must travel as a value, a closed language must retain each expression's result sort, or several interpreters must share one typed program. These are ordinary Swift encodings with a trusted kernel. They do not turn Swift into a total proof calculus.

### Equality Witnesses and Finite GADT Style

A first-class equality witness should have no public arbitrary constructor. Build reflexive evidence under `A == B`, then derive reversal and transitivity from that kernel. Transport remains explicit because inspecting a witness value does not add a same-type requirement to the surrounding generic context.

```swift
struct Equal<A, B> {
    private let transportValue: (A) -> B

    private init(_ transport: @escaping (A) -> B) {
        transportValue = transport
    }

    func transport(_ value: A) -> B { transportValue(value) }
}

extension Equal where A == B {
    static var reflexive: Self { Self { $0 } }
}

enum Expression<Output> {
    case text(String, Equal<String, Output>)
    case flag(Bool, Equal<Bool, Output>)
}
```

The case payload prevents constructing text as `Expression<Bool>` through the safe API. Evaluation still needs an explicit transport, and the evaluator still owns the meaning of each case. Keep both directions if clients need symmetric transport; the one-way excerpt only illustrates the construction seal.

For a finite language, separate associated syntax families are often simpler: `TextSyntax` evaluates to `String`, `FlagSyntax` evaluates to `Bool`, and cross-sort cases mention the other family directly. Use an equality-carrying enum when one uniform indexed representation matters. Use associated families when inspectable closed syntax and ordinary switches matter more.

Apply that choice to the whole expression, including operator operands and its evaluation result. A scalar value enum plus a checked kind tag only closes literal construction; it does not establish the recursive expression's result relationship. Runtime parsing can validate into a closed syntax family, so dynamic input alone is not a reason to discard typed construction. State why the simpler family suffices and what requirement would justify a uniform indexed form; reserve equality witnesses for that requirement rather than ruling them out categorically.

Pair a rejected ill-typed expression with a concrete well-typed expression and its expected evaluator result. A valid compilation control establishes construction and type relationships; evaluating the example checks a separate semantic claim. Even a read-only recommendation should specify both examples and mark their execution status.

Typed environments extend the same idea: a heterogeneous product stores values, while `Here` and `There<Rest>` witnesses select a position and its element type. This can reject unbound variables, wrong stack transitions, or reconstruction into a hole of the wrong sort. Dynamic environments require validation and existential packaging.

Indexed inductive structures go further by making each derivation rule a constructor whose premises carry the indices needed for its conclusion. This can exclude malformed proof trees or incompatible child sorts. Keep constructors closed, and inspect the recursive storage: declaring a height, color, scope, or result index does not show that the payload has that property.

### Choose a Language Representation

| Representation | Use when | What remains unproved |
|---|---|---|
| Tagless-final or object algebra | Programs should be generic over evaluation, printing, analysis, or generation | Interpreter agreement, purity, and optimization correctness |
| Initial typed AST | Programs must be inspected, stored, transformed, or interpreted later | Interpreter semantics and transformation preservation |
| Free or freer instruction form | An operation vocabulary and sequencing must be explicit | General encodings may require GADT, HKT, or erasure assumptions |
| Church, Scott, or continuation encoding | The permitted eliminations are the abstraction boundary | Branch count, single invocation, termination, and algebraic laws |

Higher-rank behavior can be represented by a function object or protocol requirement whose method is generic. Swift does not thereby provide a first-class polymorphic closure. Higher-kinded emulation uses a constructor tag plus `Kind<F, A>`-like representation and operation witnesses; any force cast that connects the tag to a concrete type belongs in the trusted kernel. Prefer direct associated families or domain-specific wrappers unless many algorithms truly need the shared constructor abstraction.

### Bind Evidence to the Thing Proved

Phantom proof names can require evidence for membership, sorting, or a validated transformation, but a tag alone does not establish runtime instance identity. Restrict issuance and bind evidence to the exact artifact, version, generation, or authority scope. Phase-specific IR types can prevent connecting parsed, resolved, typed, and lowered phases incorrectly; they do not prove semantic preservation across a pass.

Products, sums, functions, and uninhabited types can model conjunction, alternatives, implication-shaped interfaces, and falsehood. Because Swift functions can trap, diverge, and perform effects, treat proof terms as application evidence rather than mathematical proof unless a restricted external system supplies that theorem. A law-bearing witness should be minted by a small checker and tied to the exact implementation and data it certifies.

**Boundaries and cost.** Audit every evidence constructor, conversion, cast, decoder, mutation, and eraser. Check that recursive storage actually matches its advertised index. Keep semantic laws, termination, effect behavior, and external-certificate validation separate from type checking. Equality transports, mutually recursive families, HKT emulation, and higher-rank protocol objects raise diagnostic and maintenance cost quickly. Replace them with a closed enum, direct associated family, concrete command tree, or ordinary runtime validation when those alternatives reject the same misuse.

<a id="gap"></a>
## Use Specialized Encodings Deliberately

These recipes fill narrower gaps. They are useful when a concrete domain has the matching shape; they should not become a general framework by default.

### Keep Generic Requirements Solvable

Treat a generic signature as a system of conformance and same-type requirements. Name intermediate types and split protocols when recursive requirements become difficult to explain or compile. A successful signature proves only those interface equations. It does not prove the body satisfies a mathematical specification.

Separate producers from consumers when adapting subtypes or related abstractions. Supported function conversions and explicit `map` or `contramap` adapters can preserve direction; writable user-defined storage remains invariant unless the language explicitly says otherwise. Do not infer business implications from subtyping.

### Replace Opaque Control Flow With Data

Defunctionalize a finite callback family into an enum whose cases store captured environments:

```swift
enum Continuation {
    case save(record: RecordID)
    case retry(request: Request, remaining: Int)
}

func resume(_ continuation: Continuation, with result: Response) {
    switch continuation {
    case let .save(record): save(result, for: record)
    case let .retry(request, remaining): retry(request, remaining: remaining)
    }
}
```

This makes the callback vocabulary and stored state inspectable. Separate frame families when continuations consume different result sorts. The dispatcher still owns scheduling, replay, termination, and semantic correctness.

An indexed zipper stores a focused subtree plus a reconstruction context parameterized by the replacement and root types. It rejects plugging the wrong sort into the hole. A domain-specific fold, unfold, or generate-and-fold operation can centralize recursion without a general higher-kinded recursion-scheme framework. The traversal may still diverge, perform effects, or rebuild the wrong semantics.

### Carry Membership, Labels, and Budgets

Row-like records combine nominal labels, heterogeneous products or sums, and membership or removal witnesses. They preserve a selected field's payload while leaving a typed remainder. Swift does not supply a general unordered-row solver, automatic absence proof, or effect-row subtraction; use generated witnesses or a fixed domain when uniqueness and permutation matter.

Information-flow wrappers may index values and sinks by confidentiality or integrity and require explicit declassification authority. They can reject direct incompatible API calls. Ordinary Swift control flow does not track branch sensitivity, exceptions, timing, logs, globals, or raw projections, so the wrapper does not prove noninterference or constant-time execution.

Fuel or budget indices can require one modeled credit per interpreter step. Consuming tokens can prevent reuse of a credit. The trusted executor and cost assignment still determine whether a modeled step corresponds to time, memory, energy, or another real resource; the encoding does not infer asymptotic or deadline bounds.

Compiler diagnostics for allocation, locking, or effects belong to a pinned verification workflow, not to the public proof vocabulary. Consult [Swift feature status](swift-feature-status.md) before using any underscored or experimental annotation. Treat optimizer assertions as trusted assumptions unless a supported checker rejects violations in the exact build phase used.

**Boundaries and cost.** Restrict witness, declassification, and fuel construction; preserve indices through mutation and erasure; and inventory every raw projection or unchecked interpreter. Verify reconstruction, traversal, dispatch, labels, and cost correspondence separately. Specialized encodings add cases, witnesses, recursive constraints, and generated code. A plain enum machine, domain-specific fold, nominal record, runtime authorization check, or measured resource limit is usually cheaper and often more accurate.

## Review Checklist

- Name the misuse rejected by each generic axis, index, witness, or constructor.
- Prefer the baseline generic or protocol rule before an advanced encoding.
- Trace construction, decoding, mutation, generation, persistence, and erasure.
- Keep runtime identity and value predicates separate from static type equality.
- Keep syntax well-formedness separate from interpreter semantics and external-system truth.
- Treat casts, proof issuance, generated witnesses, and certificate checking as trusted code.
- Pair compiler rejection with a valid control under the same toolchain and arguments.
- Test semantic laws and runtime validation independently of compile-time fixtures.
- Record availability, ABI, diagnostics, build time, code size, and migration cost.
- Collapse any axis that no longer removes a callable invalid operation.

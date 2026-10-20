# Ownership, effects, and representation recipes

Use this guide when a model's guarantee depends on who owns storage, who may
access it, how errors travel, or who must finish work. These are different
obligations. Load only the matching family; use [feature status](swift-feature-status.md)
for version-sensitive syntax and library APIs before adopting a supplied example.
The snippets illustrate boundaries, not newly executed compiler acceptance.

<a id="ownership"></a>
## Ownership: lend access without surrendering the invariant

Use noncopyable ownership for a handle whose duplication would violate a local
lifecycle rule. Use borrowing for temporary inspection and consuming operations
for transfer. The invariant is at most one consuming use of a noncopyable value
within the checked Swift boundary. It does not establish unique ownership of
external storage or mandatory use. See [ownership fundamentals](ownership-concurrency-errors.md)
for the established resource patterns.

```swift
struct ResourceSlot<Resource: ~Copyable>: ~Copyable {
    private var resource: Resource?

    init(_ resource: consuming Resource) { self.resource = resource }

    mutating func take() -> Resource? {
        resource.take()
    }
}
```

Construction transfers the handle into one optional slot. Taking it leaves nil;
repeat calls therefore have a runtime absence result. A private raw handle and
an audited destructor establish release behavior. Noncopyability cannot fix a
second wrapper around the same file descriptor or an aliased class inside it.
Erasing into an ordinary copyable box must not recreate an ownership capability.

When generalizing, suppress `Copyable` on the wrapper, payload, protocol, caller,
and applicable extension where needed. `~Copyable` permits copyable *and*
noncopyable arguments. Associated-type capabilities are independent of `Self`;
primary associated-type defaults can reappear at use sites. Ownership-preserving
existentials must preserve suppressed capabilities and required relationships.
A `Hashable` conformance proves neither semantic laws nor compatibility with
every container. Review [status and generalized protocols](swift-feature-status.md#release-08)
before adopting newer ownership-polymorphic APIs.

Choose the operation by what its caller retains:

| Operation | What to inspect |
|---|---|
| Borrow a parameter or enum payload | No ownership transfer; referenced objects can still mutate through their allowed API. A borrowing switch and optional binding need not have identical ownership behavior. |
| `consume` a binding or switch payload | Ends that binding's current lifetime; earlier copies/aliases survive. A consumed `inout` slot must be reinitialized. |
| `copy` a borrowed copyable value | Explicitly creates ownership; does not promise deep cloning or low cost. |
| Split an aggregate | Partial consumption depends on layout visibility and destructor restrictions; do not dismantle a destructor-bearing wrapper as an arbitrary record. |
| Destroy a resource | Audit release and cycles; destruction is not a lexical deadline, external success guarantee, or recovery from process termination. |

For borrowed storage, distinguish using a supplied `Span` from defining custom
lifetime-dependent returns. `MutableSpan` and mutable raw spans protect scoped
access, not valid indices, business invariants, or foreign aliases. `Ref` lends
shared access without ownership; `MutableRef` lends exclusive access. Neither
makes a class deeply immutable or authorizes extending the storage lifetime.
Custom projections and returns need their separately recorded lifetime support.

A `borrow` accessor projects existing storage; a `mutate` accessor admits all
writes permitted by the component type. Expose mutation only when that component
can preserve the containing aggregate's predicate on its own. Yielding coroutine
accessors are a separate feature track. `UniqueBox` selects unique heap placement;
`UniqueArray` stores dynamically many owned elements. Neither proves no allocation,
constant-time growth, mathematical element uniqueness, or fixed capacity.

Borrowing iteration can lend a batch only until the iterator changes. Do work
inside that borrow; a generic `first(where:)`, retained element, or cross-batch
comparison needs an owned result or independently valid lifetime. Propagate the
iterator's failure type, but do not infer termination. The supplied projection
and `Iterable` examples are discussed in [release rows 5–10](swift-feature-status.md#release-05).
Costs include lifetime constraints, recovery plumbing, ABI restrictions, and
less familiar diagnostics. A scoped `withResource` operation or immutable value
is usually simpler when ownership does not itself prevent a real misuse.

<a id="isolation"></a>
## Isolation: reserve changing facts before suspension

Use actor ownership for an asynchronous consistency domain, or a lock for a
required synchronous operation. The invariant is exclusive authorized access to
isolated storage, not an atomic workflow across suspension. The concurrency
skill owns execution and migration rules; consult its [reentrancy guide](../../using-swift-concurrency/references/logical-races-and-reentrancy.md)
when changing scheduling behavior.

```swift
actor Inventory {
    private var remaining: Int
    init(count: Int) { precondition(count >= 0); remaining = count }

    func reserve() -> Bool {
        guard remaining > 0 else { return false }
        remaining -= 1
        return true
    }
}
```

The check and decrement run without suspension. A real API can return a private
reservation bound to item, quantity, revision, and authority; settlement consumes
it or atomically verifies its identity. Construct isolated state in one owner,
mutate through complete operations, and never expose an unrestricted reference
or writable projection that bypasses that owner. Erasing an actor reference does
not erase the need to await its isolated operations.

Keep the axes separate:

| Axis | Retained meaning and boundary |
|---|---|
| Sharing | `Sendable` and `@Sendable` describe safe cross-domain use. They do not imply purity, copying, serialization, or once-only invocation; unchecked conformances are trusted assertions. |
| Transfer | Region isolation and `sending` permit disconnected graphs to move. This is flow-sensitive and distinct from consuming ownership; aliases can merge regions. `inout sending` adds a transfer contract beyond ordinary exclusive `inout`. |
| Actor access | An `isolated` actor parameter grants access to that instance. It does not acquire two independent actors as one transaction. |
| Execution inheritance | `#isolation`, `@isolated(any)`, and `nonisolated(nonsending)` preserve particular isolation relationships, not no-suspension or a scheduling deadline. An isolated callback is not automatically Sendable. |
| Leaving isolation | `@concurrent` changes where async work executes; it does not create a task, guarantee a thread, or prove parallelism. |
| Conformance | Global-actor-isolated conformances are limited to that isolation. `SendableMetatype` requirements affect usable conformances, so add them only when metatypes cross domains. |
| Defaults | Module default isolation, language mode, strict checking, and upcoming features are separate settings; inspect the actual target. |

Nonisolated public facets should expose only operations safe without actor
privilege. Nonisolated does not mean pure or background execution. Concrete
`~Sendable` suppression does not provide a general negative generic constraint;
see [release row 21](swift-feature-status.md#release-21). An immutable weak
relationship can still become nil; capture syntax and feature settings require
the selected compiler's documentation.

Keep mutex-protected check/update in one critical section and never suspend
inside it. Typed atomic orderings reject some invalid operation/order pairs but
do not prove publication protocols, ABA freedom, lock freedom, or larger
invariants. Legacy executor adapters and `assumeIsolated` assert an execution
context; they do not hop to it. Distributed actors add transport, serialization,
identity, and remote failure obligations rather than local transaction proofs.

Test interleavings, stale revisions, rollback, cancellation, and external authority.
Costs include executor hops, lock contention, testing histories, and public
isolation constraints. An immutable snapshot with a checked version on write is
a simpler alternative when live shared mutation is unnecessary.

<a id="effects"></a>
## Effects: carry a useful error vocabulary through adapters

Use typed errors when callers need a closed domain failure vocabulary or a
generic wrapper must preserve its callback's error type. The invariant restricts
the throwable type; it does not establish error provenance, which input causes
which case, or whether an operation completes. See [typed errors](ownership-concurrency-errors.md)
for the basic signature choices.

```swift
enum ReadFailure: Error { case missing, invalid }

func readLabel(_ text: String?) throws(ReadFailure) -> String {
    guard let text else { throw .missing }
    guard !text.isEmpty else { throw .invalid }
    return text
}

func explain(_ text: String?) -> String {
    do { return try readLabel(text) }
    catch {
        switch error {
        case .missing: return "No label"
        case .invalid: return "Empty label"
        }
    }
}
```

Use an unconditional catch with an exhaustive inner switch when case-pattern
catch clauses do not establish exhaustiveness for the selected compiler. For
higher-order code, write explicit `throws(Failure)` closure or receiving-function
types rather than assuming inference preserves the narrow type everywhere.
`rethrows` tracks dependence on throwing callbacks; it is not a general
first-class effect variable. See [typed-error seams](swift-feature-status.md#release-20).

Store outcomes in `Result` when delayed observation is intended. Constructing
`.success` is trusted implementation, not proof that external work occurred.
`Never` removes the throwable channel specifically; a nonthrowing function can
still trap, loop, ignore cancellation, or perform wrong effects. A sum of error
families needs explicit cases and mappings; Swift does not infer arbitrary error
unions or treat every enum containing `Never` as a nonthrowing effect.

An operation protocol can correlate `Output` and `Failure`. Async sequences can
retain element and failure axes, but bridges may erase them and library
availability matters. A sequence type proves neither ordering, backpressure,
finite length, nor eventual yield. Translate infrastructure failures at one
boundary and decide how cancellation remains visible.

Where direct `Task` or `async let` throwing paths erase the error, materialize
`Result<Output, Failure>` inside the work and unwrap after awaiting it. A
`Task<Result<Output, Failure>, Never>` retains the failure axis while still needing
an owner for cancellation and observation. Async `Result(catching:)` itself does
not create work; check its independent availability. Keep release/probe evidence
qualified rather than treating proposal intent as implemented behavior.

A synchronous signature forbids suspension in its body, not blocking or hidden
unstructured tasks. Swift's typed throws is not a general effect-row or purity
system. Typed commands and restricted interpreters can make permitted operations
inspectable; arbitrary stored closures can hide effects. `@TaskLocal` carries
scoped context but a default does not prove injection. `noasync` restricts direct
async calls, not synchronous wrappers or transitive thread affinity.

Construction and mutation of stored outcomes must preserve the declared family;
erasure to `any Error` loses precision and must be intentional. Residual work is
error mapping, cancellation policy, callback multiplicity, and interpreter laws.
Costs include wrapping errors and evolving public cases. Untyped `throws` or a
small result enum is simpler when consumers do not use a closed failure contract.

<a id="resources"></a>
## Completion: account for abandonment and recovery

Use a structured scope when child work or resource cleanup belongs to one
operation. Use a consuming permit when reusing local authority is the invalid
operation. These enforce different facts: scoped child lifetime, at-most-once
consumption, and runtime completion must not be conflated.

```swift
func withHandle<Value>(
    acquire: () throws -> Int32,
    release: (Int32) -> Void,
    body: (Int32) throws -> Value
) rethrows -> Value {
    let handle = try acquire()
    defer { release(handle) }
    return try body(handle)
}
```

This deliberately exposes a copyable integer: the callback can retain it. The
scope arranges release on ordinary unwinding but does not prove that no handle
escapes. A stronger API hides the raw handle and lends an appropriate ownership-
or lifetime-restricted view. The acquisition/release implementation still owns
external correctness, and fatal termination bypasses normal unwinding.

Use `async let` or task groups for children, and explicit handles for unavoidable
unstructured work. A cancelled child can ignore cancellation and hold a parent
scope open. A discarded-task warning is useful build policy, not a mandatory
observation proof. See [task lifecycle](../../using-swift-concurrency/references/task-lifecycle-and-cancellation.md).

A consuming continuation can reject a second resumption statically while still
allowing omission. Destruction checks and indefinitely retained continuations
have different runtime consequences. When callbacks race cancellation or repeat,
an actor or lock must atomically take the continuation from a slot before resume;
registration, precedence, and later callbacks remain runtime design. A one-shot
handle cannot change the foreign callback's multiplicity. See [continuation status](swift-feature-status.md#release-19)
and [bridging](../../using-swift-concurrency/references/continuations-and-bridging.md).

Async cleanup in `defer` may suspend or fail. Cancellation shields can protect
particular cleanup work from inherited cancellation without imposing a timeout
or making a remote release succeed. Isolated synchronous destruction is not
`async deinit`, and scheduled destruction or reference cycles can delay release.
Check [cleanup support](swift-feature-status.md#release-18) before selecting APIs.

For transactions and session protocols, return an outcome retaining either the
next authority or recoverable prior authority: [consuming transitions](domain-modeling-recipes.md#flow).
Do not reconstruct permissions from freely writable state tags. Construction
binds authority to the resource; mutation follows the legal transition; erasure
must retain consumption and identity. Reserve changing facts synchronously before
awaiting, and settle or roll back under the authority that owns them.

Residual obligations include deadlines, termination, cleanup errors, crash
recovery, idempotency, peer duality, and distributed durability. A session-like
API does not prove fairness or deadlock freedom. Costs include cancellation and
recovery state machines; a scoped operation is simpler than public stage types
when callers need only one complete action.

<a id="representation"></a>
## Bytes: validate memory shape before domain meaning

Use representation constraints for binary parsers and borrowed buffers when they
remove unsafe operations. Keep four questions separate: can this value's bits be
copied, can all its bytes be observed, can arbitrary bytes construct it, and can
raw mutation preserve it? The invariant concerns representation, not wire format
or business meaning. See [safe byte API status](swift-feature-status.md#release-17).

```swift
enum PacketError: Error { case truncated, unsupportedVersion }

func packetVersion(_ bytes: [UInt8]) throws -> UInt16 {
    guard bytes.count >= 2 else { throw PacketError.truncated }
    let version = UInt16(bytes[0]) << 8 | UInt16(bytes[1])
    guard version == 1 else { throw PacketError.unsupportedVersion }
    return version
}
```

This small parser uses explicit big-endian layout and separate bounds/domain
checks. A supported safe `RawSpan` load can replace scalar assembly; it cannot
remove those obligations. Do not serialize an arbitrary Swift struct's memory
layout as a stable packet format.

`BitwiseCopyable` alone permits neither arbitrary-bit construction nor reading
uninitialized padding. `ConvertibleToBytes` concerns fully initialized observable
storage; `ConvertibleFromBytes` concerns valid construction for every bit pattern.
Their `FullyInhabited` intersection supports bidirectional raw access under its
contract. Compiler-supplied versus unchecked custom conformances differ in trust;
review actual availability and conformance restrictions. A refined range, pointer,
enum discriminant, or Unicode scalar is not automatically arbitrary-bit-safe.

Mutable raw views still require alignment, size divisibility, bounds, and domain
checks. `OutputSpan`/`OutputRawSpan` track initialized portions of capacity at
runtime; consuming or initializing elements must maintain that count. Scoped
temporary allocation can arrange lifetime and cleanup without guaranteeing stack
allocation, bounded latency, or allocation success.

For foreign interfaces, bounds and lifetime annotations are trusted inputs.
C/C++ storage and external writers must honor exclusivity and lifetime promises;
a Swift wrapper cannot prove they do. Keep unsafe casts, pointers, unchecked
conformances, and optimizer assumptions within the audited adapter. Consult
[interop](boundaries-and-interop.md) and [unsafe-code review](security-and-resource-modeling.md#strict-memory-safety-as-an-audit-tool).

`UTF8Span` can carry validated UTF-8 for borrowed processing. Construct it through
a validating or independently trusted route; UTF-8 validity still does not prove
normalization, application grapheme policy, or a permitted identifier. Erasing a
validated view to bytes loses this evidence. Costs include alignment/lifetime
constraints and a larger trusted adapter. Ordinary array decoding or copying to
a small nominal domain value is simpler when zero-copy work is not measured.

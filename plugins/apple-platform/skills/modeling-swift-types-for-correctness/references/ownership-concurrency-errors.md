# Ownership, Concurrency, and Error Modeling

Use this reference when copying, lifetime, task isolation, synchronization, cancellation, or failure typing is part of the invariant.

## Concurrency Invariants Begin With Ownership of Mutable State

Ask three questions:

1. Which isolation domain owns each mutable value?
2. What representation may cross to another task or actor?
3. What operation, if any, transfers ownership rather than shares it?

Prefer this order:

1. Immutable `Sendable` values.
2. Actor-owned mutable state with immutable snapshots.
3. A lock-backed synchronous abstraction for measured or API-required cases.
4. `@unchecked Sendable` only when the synchronization proof cannot be expressed and is documented in the type.

## `Sendable` Is a Cross-Isolation Contract

A `Sendable` value may safely cross concurrency domains. For structs and enums, immutable stored values that are themselves `Sendable` are the easiest proof.

```swift
struct AccountSnapshot: Sendable {
    let id: AccountID
    let displayName: String
    let revision: Int
}
```

A class's reference identity and mutable storage require more care. Prefer actor isolation, immutability, or a lock-backed final class with all access synchronized.

### `@unchecked Sendable`

`@unchecked Sendable` is a promise made by the programmer, not compiler verification. Before using it, document:

- The exact mutable state.
- The synchronization primitive or immutability rule protecting it.
- Why every read and write follows that rule.
- Whether callbacks can re-enter while the invariant is partially updated.
- Whether subclasses can introduce unsynchronized state; usually make the class `final`.
- Whether deinitialization and foreign APIs obey the same rule.

A comment such as “thread-safe” is insufficient.

## Actors

Use an actor when a logical component owns mutable state and asynchronous access is acceptable.

```swift
actor SessionStore {
    private var session: UserSession?
    private var revision = 0

    func replace(with session: UserSession?) -> SessionSnapshot {
        self.session = session
        revision += 1
        return SessionSnapshot(session: session, revision: revision)
    }

    func snapshot() -> SessionSnapshot {
        SessionSnapshot(session: session, revision: revision)
    }
}
```

Return immutable snapshots rather than leaking actor-owned mutable references.

### Reentrancy

An actor-isolated function may be re-entered at an `await`. Invariants that span asynchronous work need an explicit design:

```swift
actor Inventory {
    private var reserved: Set<ItemID> = []

    func purchase(_ id: ItemID, client: StoreClient) async throws {
        guard reserved.insert(id).inserted else { throw PurchaseError.alreadyReserved }
        defer { reserved.remove(id) }

        try await client.purchase(id)
    }
}
```

The reservation records in-flight state before suspension. Decide whether cancellation or failure releases, retains, or compensates the reservation.

Do not hold a logical invariant only in local variables across `await` while other actor calls may observe partially completed state.

## Global Actors and Default Actor Isolation

Use `@MainActor` for UI-owned mutable state and APIs that must run on the main actor.

Current Swift provides module-level default isolation controls. Treat default actor isolation as a build setting that changes the meaning of unannotated declarations. Inspect `SWIFT_DEFAULT_ACTOR_ISOLATION`, package `.defaultIsolation(...)`, and upcoming concurrency features before interpreting a diagnostic or proposing annotations.

Do not blanket-add `@MainActor` to domain models merely to quiet warnings. It can make value construction and protocol conformances unnecessarily asynchronous. Conversely, do not strip main-actor isolation from UI state that is genuinely main-owned.

Use explicit `nonisolated` or `@concurrent` behavior only after understanding the compiler and language-mode semantics in the project's toolchain. Keep concurrency annotations part of the API contract, not diagnostic decoration.

## `@Sendable` Closures

A closure that may execute concurrently should be `@Sendable` and capture only safe values.

```swift
struct WorkItem: Sendable {
    let run: @Sendable () async -> Void
}
```

Capturing a mutable local or non-Sendable reference is a design signal. Prefer capturing an immutable snapshot, actor reference, identifier, or value-semantic configuration.

Be careful with callback APIs imported from Objective-C: the imported closure annotation and execution queue may not fully express runtime behavior. Wrap the callback at a boundary and resume into an actor or checked continuation deliberately.

## Transferring Values

Use `sending` and related transfer semantics only when the operation truly transfers a value into another isolation domain. The current Swift 6 baseline supplies the language support; a transfer is stronger than merely passing a `Sendable` shared value.

Do not add transfer annotations speculatively. Validate callers and test under strict concurrency because region-based isolation diagnostics can change as the compiler evolves.

## Locks

Use a lock for synchronous mutation that cannot conveniently be actor-isolated or where profiling demonstrates actor overhead matters.

For an iOS 16 baseline:

- `OSAllocatedUnfairLock` is available from iOS 16.
- `Synchronization.Mutex` is available from iOS 18.
- Actors remain available and are usually the higher-level default.

A lock-backed type should:

- Own the lock and protected state together.
- Never expose the protected mutable reference.
- Keep critical sections small.
- Avoid `await` while locked.
- Avoid calling arbitrary client closures while the invariant is partially updated.
- Establish a lock ordering when multiple locks can be acquired.
- Be `final` if class invariants rely on complete synchronization.

Prefer domain operations over a public “run arbitrary code while locked” API:

```swift
import os

struct InventorySnapshot: Sendable {
    let reservedIDs: Set<Int>
}

final class LockedInventory: @unchecked Sendable {
    private struct State: Sendable {
        var reservedIDs: Set<Int> = []
    }

    private let storage = OSAllocatedUnfairLock(initialState: State())

    func reserve(_ id: Int) -> Bool {
        storage.withLock { state in
            state.reservedIDs.insert(id).inserted
        }
    }

    func snapshot() -> InventorySnapshot {
        storage.withLock { state in
            InventorySnapshot(reservedIDs: state.reservedIDs)
        }
    }
}
```

The concrete methods keep partial state and lock reentrancy out of client code. A generic `withValue` helper can still be useful as a private implementation detail, but exposing it publicly lets callers block, re-enter, or observe an invariant mid-update. Verify the exact initializer and closure signatures against the SDK in use, and keep platform-specific lock code behind an adapter.

## Atomic Values

An atomic primitive protects individual operations, not arbitrary multi-field invariants. If correctness requires “read A, update B, then publish C” as one transaction, use one lock or actor around the whole state.

Choose memory ordering based on a written synchronization argument. Defaulting to the weakest ordering for speed without that argument is unsafe; defaulting every operation to sequential consistency may be correct but still obscure the higher-level protocol.

## Cancellation Is Part of State Modeling

Swift task cancellation is cooperative. Model which states and side effects are legal when cancellation arrives:

- Before work begins.
- During a suspension.
- After a remote side effect succeeds but before local state records it.
- During cleanup.

Use `defer` for synchronous cleanup and cancellation handlers for asynchronous resources where appropriate. Preserve `CancellationError` or map it intentionally; do not convert cancellation into a generic business failure without reason.

A state machine may need explicit cases such as `.cancelling`, `.cancelled`, or `.completedAfterCancellationRequest` only when those distinctions matter to users or recovery. Do not add them automatically.

## Weak and Unowned References

`weak` and `unowned` model object-lifetime relationships; they are not concurrency mechanisms.

- A `weak` reference is optional and automatically becomes `nil` after the object deallocates. Use it when absence is a valid outcome and the reference must not keep the object alive.
- An `unowned` reference encodes the runtime precondition that the referenced object outlives every access. Violating that precondition traps. Use it only when the ownership graph establishes the lifetime, not merely to avoid optional handling.
- `unowned(unsafe)` omits the runtime check and can become a dangling reference. Treat it as an explicit unsafe boundary requiring the same level of proof as a raw pointer.
- Actor isolation does not repair a dangling `unowned` reference, and weak-reference reads can still race with surrounding mutable state unless that state has one isolation domain.
- A closure should capture `[weak self]` when allowing the owner to deallocate changes the intended operation semantics. Strong capture is often correct for finite work that must keep its owner alive; choose deliberately rather than applying a universal capture-list rule.

Review cycles separately from task cancellation, observer lifetime, and callback escape. Breaking a retain cycle can expose a use-after-lifetime bug if a foreign callback still retains an unsafe context pointer.

## Ownership: Use It When Copying Is the Bug

Ordinary Swift value semantics are a feature. Reach for noncopyable types only when copies would violate a resource or state transition.

Typical cases:

- Lock guards or leases.
- File descriptors or native handles with unique ownership.
- Transactions that must commit or roll back once.
- Builders that consume backing storage.
- Security-sensitive tokens that should not be duplicated in-process.

### Noncopyable type

```swift
struct Lease: ~Copyable {
    private let handle: NativeHandle

    init(handle: consuming NativeHandle) {
        self.handle = handle
    }

    borrowing func inspect() -> LeaseInfo {
        handle.info
    }

    consuming func release() {
        handle.release()
    }
}
```

This establishes unique Swift ownership only if `NativeHandle` is itself a verified unique-owning, noncopyable wrapper. Applying `consuming` to a copyable integer, pointer, or reference does not prove unique ownership of the underlying native resource. This syntax also requires a supporting compiler. The native wrapper and deinitialization policy must still be correct; `~Copyable` does not automatically close a handle.

### Ownership modifiers

- `borrowing`: temporary read access without taking ownership.
- `consuming`: takes ownership; the caller cannot use a noncopyable argument afterward.
- `inout`: exclusive mutable access for the duration of a call.

Use modifiers to communicate semantics, not as performance folklore. Measure copies and ARC traffic before complicating ordinary value APIs.

### Destruction and partial transitions

A noncopyable resource type needs a complete terminal-state story:

- What happens on ordinary scope exit?
- Can `deinit` perform the required cleanup?
- Is cleanup allowed to fail?
- What happens if a consuming transition throws after partially acting?
- Is rollback automatic, explicit, or impossible?

Swift destructors cannot provide asynchronous cleanup. Async resources often need an explicit `close()`/`finish()` operation plus a defensive synchronous `deinit` fallback where possible.

## Nonescapable Values and Lifetimes

`~Escapable` and `Span` can model borrowed views that must not outlive storage. They are advanced tools and require compiler support plus correct lifetime relationships.

A custom nonescapable wrapper alone does not prove that its pointer or view remains valid. The compiler must know the value's lifetime depends on a valid owner, or the value must remain inside a closure whose owner is alive.

For broad deployment, closure-scoped access keeps the owner visibly alive and makes the intended use interval easy to review:

```swift
func withBytes<Result>(
    of data: Data,
    _ body: (UnsafeRawBufferPointer) throws -> Result
) rethrows -> Result {
    try data.withUnsafeBytes(body)
}
```

This remains a documented unsafe-buffer contract, not a complete compile-time nonescape proof: `UnsafeRawBufferPointer` is copyable, and generic result or captured storage can carry it beyond the closure. The pointer must not be used after the underlying API's documented access interval. Prefer fixed operations that consume the bytes inside the closure when practical.

Use the `Span` family when APIs can safely expose nonescapable views: `Span<Element>` for initialized elements and `RawSpan` for bytes, with mutable/output variants only when their initialization and exclusivity rules fit. These types do not prove semantic validity, element binding, or foreign-buffer correctness by themselves. `Span` itself is specially back-deployed on Apple platforms, but methods that vend spans may begin at iOS 26. Check each symbol.

Do not store a span, raw pointer, or buffer view in an escaping closure or ordinary escapable property. Do not manufacture a lifetime dependency with unsafe casts.

## Strict Memory Safety Checking

Current Swift provides opt-in strict memory safety checking. The compiler flag `-strict-memory-safety` diagnoses unsafe constructs and APIs in the `StrictMemorySafety` diagnostic group. The mode also enables `#if hasFeature(StrictMemorySafety)` and the `@safe`, `@unsafe`, and `unsafe` spellings.

Use it as an audit lane, not as a claim that marked code is correct:

- Enable it in CI for modules that contain pointer operations, C/C++ interop, codecs, cryptography, or custom allocation.
- Keep `unsafe` expressions as small as possible and adjacent to written lifetime, bounds, initialization, type, and isolation preconditions.
- Wrap unsafe implementation behind a safe signature only when the wrapper discharges every caller precondition.
- Treat `@safe` as a serious API assertion, not a diagnostic suppression.
- Avoid release settings such as `-Ounchecked`, disabled exclusivity, or incomplete strict concurrency when memory safety is part of the requirement.

Strict checking identifies operations the compiler cannot prove safe. It does not verify the human proof inside an `unsafe` expression, and it does not replace fuzzing, sanitizers, or review of foreign libraries.

## `BitwiseCopyable`

`BitwiseCopyable` states that values may be copied with direct memory operations and need no special destroy operation. It is a low-level representation/performance contract, not a domain-correctness marker and not the same as ordinary `Copyable`.

Use it only for generic memory operations that genuinely require this representation property. The compiler can infer conformance for many non-exported structs and enums whose stored members qualify. Public/package/`@usableFromInline` types generally need an explicit long-term commitment unless frozen; removing a published conformance is source-breaking.

Important limits:

- Developers cannot retroactively conform a type from another module.
- Generic aggregate conditional conformances may need to be written explicitly.
- Conformance says the promise remains true as the type evolves; transient internal layout is not enough.
- It does not prove C ABI layout, byte ordering, absence of padding, stable serialization, or that arbitrary bytes form a valid value.
- `memcpy` safety still requires correct bounds, initialization, alignment where applicable, lifetime, and exclusivity.

Do not serialize a `BitwiseCopyable` value by dumping its memory. Define an explicit wire format.

## Fixed-Size and Noncopyable Containers

`InlineArray` combines integer generic parameters, inline storage, and conditional copyability. On Apple platforms it is iOS 26+. It is not a general replacement for `Array` or tuples in iOS 16 code.

Use it only when:

- Count is a compile-time literal or supported integer generic parameter.
- Fixed layout/allocation is material and measured.
- Deployment availability is acceptable or isolated.
- Its iteration and protocol conformances in the selected Swift version fit the algorithm.

`InlineArray` is not interchangeable with `Array`, and borrowing iteration continues to evolve through Swift Evolution work that may still be under review in a beta toolchain. Verify the selected compiler and proposal status rather than assuming every `Array` API or proposed conformance exists.

## Error Modeling

### Keep error domains local

Prefer small layer-specific errors:

```swift
enum ValidationFailure: Error, Equatable, Sendable {
    case empty
    case tooLong(maximum: Int)
}

enum AccountServiceFailure: Error, Sendable {
    case unauthorized
    case unavailable
    case rejected(code: String)
    case cancelled
}
```

Avoid a global `AppError` that accumulates unrelated cases. It couples layers and makes exhaustive handling unstable.

### Untyped throws remains a strong default

Untyped `throws` is appropriate when:

- Errors are normally propagated or logged rather than exhaustively handled.
- The underlying integration can evolve.
- Several dependencies contribute failures.
- A public API should not expose every implementation error as a source contract.

### Typed throws

Use `throws(E)` when the failure surface is narrow, closed, and useful to callers.

```swift
enum ParseFailure: Error, Equatable, Sendable {
    case empty
    case notAnInteger
}

func parseCount(_ text: String) throws(ParseFailure) -> Int {
    guard !text.isEmpty else { throw .empty }
    guard let value = Int(text) else { throw .notAnInteger }
    return value
}
```

Typed throws is part of the current Swift 6 baseline, but inference is not universally ergonomic. Be explicit where inference is brittle, and compile representative callers with the selected current compiler.

### Exhaustive handling

A typed catch variable has the concrete error type when the `do` body remains within that typed failure surface. Use one unconditional `catch` and switch when exhaustive case handling matters:

```swift
do {
    let count = try parseCount(input)
    use(count)
} catch {
    switch error {
    case .empty:
        showEmptyMessage()
    case .notAnInteger:
        showIntegerMessage()
    }
}
```

Do not assume a chain of pattern-specific `catch` clauses is treated as exhaustive in every context.

### Error translation

Translate errors at architectural boundaries:

```swift
func loadAccount() async throws(AccountServiceFailure) -> Account {
    do {
        return try await transport.fetchAccount()
    } catch is CancellationError {
        throw .cancelled
    } catch let error as HTTPFailure {
        throw mapHTTPFailure(error)
    } catch {
        throw .unavailable
    }
}
```

This example deliberately makes cancellation part of the service contract. When callers should continue to observe the standard `CancellationError`, prefer untyped `throws`, rethrow cancellation unchanged, and map only the domain failures you own. Do not disguise cancellation as `.unavailable` merely to keep a closed error enum.

Preserve useful underlying context for diagnostics without exposing unstable implementation types as public cases. Options include structured codes, an internal underlying error, logging at the boundary, or an opaque public error with diagnostic metadata.

## `Never`

`Never` expresses an impossible value or failure branch.

- `Result<Value, Never>` is an infallible stored result.
- A generic `Failure == Never` specialization can remove failure handling.
- A nonthrowing function is conceptually `throws(Never)` for subtyping purposes.

Do not add fake impossible branches to satisfy an abstraction. Simplify the abstraction or specialize it.

## Accumulating Validation

Throwing initializers usually stop at the first failure. Forms and imports often need all issues:

```swift
struct FieldIssue: Equatable, Sendable {
    let field: FieldID
    let message: String
}

enum Validation<Value> {
    case valid(Value)
    case invalid([FieldIssue])
}
```

Keep the resulting valid type refined. Do not return the raw model plus an `isValid` flag.

## Public Error Resilience

A public typed error enum makes its cases part of source-level client behavior. Consider:

- Can new failure cases be added without breaking exhaustive client switches?
- Should the enum be nonfrozen across a resilient library boundary?
- Is an `unknown` or opaque case appropriate?
- Would an error code plus structured metadata evolve better?
- Does the API need typed throws at all?

Typed errors are strongest inside modules and stable domain seams. They are often weaker at broad framework or network boundaries.

## Review Checklist

- Who owns each mutable value?
- What crosses isolation, and is it immutable or `Sendable`?
- Can an actor be re-entered while an invariant is partial?
- Is default actor isolation known?
- Does any `@unchecked Sendable` have a complete synchronization proof?
- Is a lock necessary, available on the deployment target, and never held across `await`?
- Is cancellation preserved intentionally?
- Is copying actually invalid before introducing `~Copyable`?
- Are consuming transitions failure-safe?
- Does a nonescapable view have a real owner lifetime dependency?
- Is `InlineArray` availability and protocol behavior verified?
- Is typed throws local, closed, and useful rather than a global taxonomy?
- Can public error cases evolve safely?

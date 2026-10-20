# Swift Feature Status and Frontier

Use this reference before recommending a recent Swift type-system feature. It separates language/compiler support from standard-library deployment availability and records what the supplied Swift 6.4 research archive can and cannot establish.

This file owns dated Swift/Xcode release facts and feature availability for the Apple Platform plugin. Compatibility references link here rather than maintaining their own snapshots.

Release/channel snapshot rechecked against primary sources: **2026-10-20**. Feature rows retain the **2026-10-19** primary-source review unless a row says otherwise; this consolidation does not claim every proposal or API was rechecked.

## Evidence vocabulary

- **Shipped** means the Swift Evolution proposal says `Implemented` for a released Swift version, or an official release announcement documents the released behavior. No experimental flag is required for the scoped form unless the row says otherwise.
- **Experimental** means the feature requires the exact frontend flag shown. An accepted proposal is not enough to call a feature shipped.
- **Unavailable** means the scoped form is absent, rejected, returned for revision, or deliberately declined. A nearby feature may still be usable.
- **Fresh** evidence was checked directly in an official release page, Swift Evolution proposal, Apple documentation page, or tagged Swift source on the recorded review date. It is source inspection, not compiler execution.
- **Supplied** evidence comes from the companion archive's saved Ubuntu compiler reports. It is useful corroboration, not a fresh compiler run.
- **Local compiler evidence** means the separately recorded Apple Swift corpus run; it does not relabel supplied Linux reports as fresh runs.
- **Unknown** means the available primary evidence does not establish the claim. Do not turn `unknown` into a deployment promise.

Swift Evolution acceptance establishes a design decision. It does not establish implementation in a released toolchain or Apple deployment support. A Linux `swift-frontend -emit-sil -swift-version 6` probe establishes only the recorded source/compiler/arguments outcome. Compilation does not prove arbitrary correctness, semantic protocol laws, resource cleanup, exactly-once completion, progress, or liveness.

## Swift 6.4 release matrix

The current stable Swift.org download is Swift 6.4.1, announced on 2026-10-13. Apple lists Xcode 27.1 (27A9275), released 2026-10-15, and Xcode 27.2 RC (27B48), dated 2026-10-19. The RC remains a preview lane until a project deliberately promotes it. Xcode 27 (27A266a) includes Swift 6.4 and the iOS 27 SDK. These release/channel facts were rechecked on 2026-10-20 against [Apple releases](https://developer.apple.com/news/releases/), [Xcode 27 notes](https://developer.apple.com/documentation/xcode-release-notes/xcode-27-release-notes), [Swift macOS downloads](https://www.swift.org/install/macos/), and the [6.4.1 announcement](https://forums.swift.org/t/announcing-swift-6-4-1/90029).

Record `xcodebuild -version`, the selected developer directory, and `xcrun swift --version` for the actual build. A Swift.org download version does not identify Xcode's bundled compiler. The archive also names official Swift 6.4.0 and 6.4.1 Ubuntu toolchains, but those binaries were not run for this integration. “No flag” below means no experimental feature flag for the scoped released form; ordinary `-swift-version 6` and the selected compilation phase still matter.

<a id="release-01"></a>
### 1. Compiler and language baseline

- **Support:** Shipped — Swift 6.4 and 6.4.1 are official releases.
- **Flag:** None.
- **Apple availability:** Xcode 27 and 27.1 are released Apple toolchains; inspect the selected Xcode with `xcrun swift --version` because the separately downloadable 6.4.1 toolchain is a different selection axis.
- **Evidence:** Fresh — [Swift 6.4 release](https://www.swift.org/blog/swift-6.4-released/), [Swift 6.4.1 announcement](https://forums.swift.org/t/announcing-swift-6-4-1/90029), and [Apple releases](https://developer.apple.com/news/releases/). Supplied SIL reports corroborate two Linux labels but do not establish Apple behavior.

<a id="release-02"></a>
### 2. Noncopyable ownership and generalized generics

- **Support:** Shipped — noncopyable structs/enums predate Swift 6; generalized noncopyable generics ship in Swift 6.
- **Flag:** None for the released forms.
- **Apple availability:** Language feature; no blanket OS floor. Referenced library types can have one.
- **Evidence:** Fresh — [SE-0390](https://github.com/swiftlang/swift-evolution/blob/main/proposals/0390-noncopyable-structs-and-enums.md) and [SE-0427](https://github.com/swiftlang/swift-evolution/blob/main/proposals/0427-noncopyable-generics.md). Supplied probes show borrow/consume checks. Affine ownership still permits dropping and does not prove unique ownership of a foreign resource.

<a id="release-03"></a>
### 3. Nonescapable inputs and supplied `Span` views

- **Support:** Shipped — nonescapable types and `Span` in Swift 6.2.
- **Flag:** None for use of released forms.
- **Apple availability:** `Span` is iOS 12.2+, macOS 10.14.4+, and corresponding platform versions; individual producers and operations vary.
- **Evidence:** Fresh — [SE-0446](https://github.com/swiftlang/swift-evolution/blob/main/proposals/0446-non-escapable.md), [SE-0447](https://github.com/swiftlang/swift-evolution/blob/main/proposals/0447-span-access-shared-contiguous-storage.md), and [Apple `Span`](https://developer.apple.com/documentation/swift/span). Supplied probes corroborate access rejection. A `~Escapable` spelling does not create an owner dependency.

<a id="release-04"></a>
### 4. Custom lifetime-dependent returns and projections

- **Support:** Experimental.
- **Flag:** `-enable-experimental-feature Lifetimes`.
- **Apple availability:** Unknown; experimental compiler support has no deployable API commitment.
- **Evidence:** Fresh — the [lifetime-dependency proposal PR](https://github.com/swiftlang/swift-evolution/pull/3145) is not an accepted implemented proposal. Supplied probes accept selected underscored `@_lifetime` forms only with the flag. Released standard-library lifetime APIs do not stabilize arbitrary custom lifetime annotations.

<a id="release-05"></a>
### 5. `Ref` and `MutableRef`

- **Support:** Shipped in Swift 6.4.
- **Flag:** None.
- **Apple availability:** iOS 27+, macOS 27+, and corresponding platform versions.
- **Evidence:** Fresh — [SE-0519](https://github.com/swiftlang/swift-evolution/blob/main/proposals/0519-ref-mutableref-types.md) and [Apple `Ref`](https://developer.apple.com/documentation/swift/ref). A reference neither owns its target nor confers deep immutability; its lifetime and exclusivity obligations remain.

<a id="release-06"></a>
### 6. Borrow and mutate accessors

- **Support:** Shipped in Swift 6.4.
- **Flag:** None.
- **Apple availability:** Language feature; no blanket OS floor.
- **Evidence:** Fresh — [SE-0507](https://github.com/swiftlang/swift-evolution/blob/main/proposals/0507-borrow-accessors.md). Supplied probes corroborate stored projection and temporary rejection. Exposing `mutate` can still bypass an enclosing aggregate invariant.

<a id="release-07"></a>
### 7. Yielding coroutine accessors

- **Support:** Experimental; the design is accepted but only partially implemented behind a flag.
- **Flag:** `-enable-experimental-feature CoroutineAccessors`.
- **Apple availability:** Unknown.
- **Evidence:** Fresh — [SE-0474](https://github.com/swiftlang/swift-evolution/blob/main/proposals/0474-yielding-accessors.md). Supplied probes reject representative syntax by default and accept it with the flag. Do not conflate these accessors with shipped `borrow` and `mutate` accessors.

<a id="release-08"></a>
### 8. Suppressed associated types and generalized simple protocols

- **Support:** Shipped in Swift 6.4 for the scoped forms in SE-0499 and SE-0503.
- **Flag:** None in the supplied official 6.4 probes. SE-0503's manuscript still mentions the development flag `-enable-experimental-feature SuppressedAssociatedTypesWithDefaults`; treat that line as stale implementation metadata for released 6.4 behavior.
- **Apple availability:** Unknown for SE-0499's standard-library protocol changes; verify the selected SDK interface and deployment target. SE-0503 is a language feature.
- **Evidence:** Fresh proposal status — [SE-0499](https://github.com/swiftlang/swift-evolution/blob/main/proposals/0499-support-non-copyable-simple-protocols.md) and [SE-0503](https://github.com/swiftlang/swift-evolution/blob/main/proposals/0503-suppressed-associated-types.md). Supplied no-flag probes resolve the metadata conflict for those exact examples. Conformance still does not prove semantic protocol laws.

<a id="release-09"></a>
### 9. `UniqueBox` and `UniqueArray`

- **Support:** Shipped in Swift 6.4.
- **Flag:** None.
- **Apple availability:** iOS 27+, macOS 27+, and corresponding platform versions.
- **Evidence:** Fresh — [SE-0517](https://github.com/swiftlang/swift-evolution/blob/main/proposals/0517-uniquebox.md), the [SE-0527 acceptance decision](https://forums.swift.org/t/accepted-with-modifications-se-0527-uniquearray/87282), [Apple `UniqueBox`](https://developer.apple.com/documentation/swift/uniquebox), and [Apple `UniqueArray`](https://developer.apple.com/documentation/swift/uniquearray). Unique ownership is not element uniqueness, fixed capacity, or a no-allocation guarantee.

<a id="release-10"></a>
### 10. `Iterable` and borrowing iteration

- **Support:** Shipped in Swift 6.4.
- **Flag:** None.
- **Apple availability:** iOS 27+, macOS 27+, and corresponding platform versions.
- **Evidence:** Fresh — [SE-0516](https://github.com/swiftlang/swift-evolution/blob/main/proposals/0516-borrowing-sequence.md) and [Apple `Iterable`](https://developer.apple.com/documentation/swift/iterable). A borrowed element can depend on iterator state; the protocol does not prove finiteness, ordering, or progress.

<a id="release-11"></a>
### 11. Integer dimensions and `InlineArray`

- **Support:** Shipped in Swift 6.2.
- **Flag:** None.
- **Apple availability:** `InlineArray` is iOS 26+, macOS 26+, and corresponding platform versions. Integer generic syntax itself has no blanket OS floor.
- **Evidence:** Fresh — [SE-0452](https://github.com/swiftlang/swift-evolution/blob/main/proposals/0452-integer-generic-parameters.md), [SE-0453](https://github.com/swiftlang/swift-evolution/blob/main/proposals/0453-vector.md), and [Apple `InlineArray`](https://developer.apple.com/documentation/swift/inlinearray). Static length does not prove an arbitrary index or runtime allocation request valid.

<a id="release-12"></a>
### 12. Literal arithmetic and symbolic integer constraints

- **Support:** Experimental only for the proposal's bounded literal expressions; general symbolic arithmetic and refinement constraints are unavailable.
- **Flag:** `-enable-experimental-feature LiteralExpressions`.
- **Apple availability:** Language experiment; no deployment commitment.
- **Evidence:** Fresh — [SE-0531](https://github.com/swiftlang/swift-evolution/blob/main/proposals/0531-literal-expressions.md) is accepted and names the flag. Supplied 6.4.x probes still reject `Sized<(2 + 3)>` and symbolic `N + 1`/`N > 0`; therefore the archive does not establish a usable 6.4 implementation even with the flag.

<a id="release-13"></a>
### 13. Tuple and `InlineArray` protocol conformances

- **Support:** Unavailable in Swift 6.4 for tuple `Hashable` conformance and the later `InlineArray` `Equatable`/`Hashable` additions.
- **Flag:** None that makes these released 6.4 features.
- **Apple availability:** Not applicable for the unavailable 6.4 forms; nominal wrappers remain deployable according to their own contents.
- **Evidence:** Fresh — [SE-0283](https://github.com/swiftlang/swift-evolution/blob/main/proposals/0283-tuples-are-equatable-comparable-hashable.md) was returned for revision and [SE-0543](https://github.com/swiftlang/swift-evolution/blob/main/proposals/0543-inline-array-hashable.md) targets Swift Next. Supplied probes reject both scoped generic requirements.

<a id="release-14"></a>
### 14. Noncopyable tuples and parameter-pack elements

- **Support:** Unavailable in the scoped Swift 6.4 forms.
- **Flag:** None established.
- **Apple availability:** Not applicable.
- **Evidence:** Fresh — [SE-0390](https://github.com/swiftlang/swift-evolution/blob/main/proposals/0390-noncopyable-structs-and-enums.md) retains noncopyable tuples as a future direction; [SE-0393](https://github.com/swiftlang/swift-evolution/blob/main/proposals/0393-parameter-packs.md) does not establish `each T: ~Copyable`. Supplied probes reject both. Use a nominal noncopyable aggregate when ownership is the invariant.

<a id="release-15"></a>
### 15. Additional noncopyable `Optional` operations

- **Support:** Accepted, but unavailable in the supplied official Swift 6.4.0 and 6.4.1 results.
- **Flag:** None established.
- **Apple availability:** Unknown because the APIs are not established as shipped.
- **Evidence:** Fresh — [SE-0532](https://github.com/swiftlang/swift-evolution/blob/main/proposals/0532-optional-noncopyable-improvements.md) says accepted rather than implemented. The [implementation-status report](https://forums.swift.org/t/implementation-status-update-for-recent-language-and-library-proposals/89295) and supplied probes agree that `ref`, `mutableRef`, `put`, and noncopyable `map` are absent. The Swift 6.4 release-blog mention does not override the implementation evidence.

<a id="release-16"></a>
### 16. `RigidArray`

- **Support:** Unavailable as public standard-library API; the steering group accepted `UniqueArray` and declined `RigidArray`.
- **Flag:** None.
- **Apple availability:** Not applicable.
- **Evidence:** Fresh — use the [acceptance decision](https://forums.swift.org/t/accepted-in-principle-se-0527-uniquearray/86943) over retained sections of [SE-0527](https://github.com/swiftlang/swift-evolution/blob/main/proposals/0527-rigidarray-uniquearray.md) and over Apple prose that still mentions `RigidArray`. Supplied probes reject the public name. The proposed capacity policy was runtime checked, not a static size proof.

<a id="release-17"></a>
### 17. Safe raw-byte conversion and loading

- **Support:** Shipped in Swift 6.4.
- **Flag:** None.
- **Apple availability:** `ConvertibleToBytes`, `ConvertibleFromBytes`, and `FullyInhabited` are documented from iOS 8+; verify each concrete `RawSpan` operation separately.
- **Evidence:** Fresh — [SE-0525](https://github.com/swiftlang/swift-evolution/blob/main/proposals/0525-rawspan-safe-loading-api.md), [SE-0426](https://github.com/swiftlang/swift-evolution/blob/main/proposals/0426-bitwise-copyable.md), and Apple documentation for [`ConvertibleToBytes`](https://developer.apple.com/documentation/swift/convertibletobytes). These contracts do not establish wire-format portability, domain validity, or correct custom unchecked conformances.

<a id="release-18"></a>
### 18. Async `defer` and cancellation shields

- **Support:** Shipped in Swift 6.4.
- **Flag:** None.
- **Apple availability:** Unknown from the checked primary evidence; inspect the selected SDK declarations.
- **Evidence:** Fresh — [SE-0493](https://github.com/swiftlang/swift-evolution/blob/main/proposals/0493-defer-async.md) and [SE-0504](https://github.com/swiftlang/swift-evolution/blob/main/proposals/0504-task-cancellation-shields.md). Compilation does not prove cleanup finishes, deadlines, atomicity, or liveness.

<a id="release-19"></a>
### 19. Noncopyable `Continuation`

- **Support:** Shipped in Swift 6.4.
- **Flag:** None.
- **Apple availability:** iOS 27+, macOS 27+, and corresponding platform versions.
- **Evidence:** Fresh — [SE-0528](https://github.com/swiftlang/swift-evolution/blob/main/proposals/0528-noncopyable-continuation.md) and [Apple `Continuation`](https://developer.apple.com/documentation/swift/continuation). The type gives static at-most-once consumption. Omitting resume still compiles; runtime checks and operational design carry exactly-once completion and liveness.

<a id="release-20"></a>
### 20. Async `Result` and typed-error transport

- **Support:** Async `Result` support shipped in Swift 6.4; full typed-throws transport through every concurrency construct is not established.
- **Flag:** None for shipped `Result` additions.
- **Apple availability:** Unknown from the checked primary evidence; inspect the selected SDK declarations.
- **Evidence:** Fresh — [SE-0530](https://github.com/swiftlang/swift-evolution/blob/main/proposals/0530-async-result-support.md) and [SE-0413](https://github.com/swiftlang/swift-evolution/blob/main/proposals/0413-typed-throws.md). Supplied probes reject selected `Task<Output, DomainError>` and `async let` forms while accepting `Result` carriers. Storing a result does not ensure observation or handling.

<a id="release-21"></a>
### 21. Explicit suppression of inferred `Sendable`

- **Support:** Shipped in Swift 6.4 for the concrete-type form.
- **Flag:** None in the supplied official 6.4 probe. SE-0518 retains the development flag name `TildeSendable`; its implemented Swift 6.4 status and the no-flag release probe govern this scoped use.
- **Apple availability:** Language feature; no blanket OS floor.
- **Evidence:** Fresh proposal status — [SE-0518](https://github.com/swiftlang/swift-evolution/blob/main/proposals/0518-tilde-sendable.md). The feature suppresses inferred unconditional conformance. It is neither a negative generic constraint nor a substitute for region-transfer and isolation analysis.

## Platform adapter availability

These deployment floors retain the 2026-10-19 documentation review. Check the selected SDK declarations, including individual members and producers, before changing deployment promises. The [source index](sources.md#apple-api-availability) links the official symbol documentation.

| Symbol/framework | iOS floor | Compatibility obligation |
|---|---:|---|
| `Synchronization.Mutex` | 18+ | Gate the declaration or use a baseline adapter |
| `OSAllocatedUnfairLock` | 16+ | Keep synchronous locking behind an audited adapter |
| Typed NotificationCenter messages | 26+ | Provide a legacy notification adapter when needed |
| Observation / `@Observable` | 17+ | Provide a baseline observation adapter when needed |
| SwiftData | 17+ | Keep persistence adapters separate from domain types |

Language syntax has no blanket OS floor; library types and their individual operations can have one. The release rows above own the floors for `Span`, `InlineArray`, `Ref`, `UniqueBox`, `UniqueArray`, and `Iterable`.

<a id="frontier"></a>
## Frontier family rubric

Retain frontier concepts as design vocabulary even when Swift cannot express them. Every entry states when to use the idea, the invariant sought, boundaries that must be traced, one concrete fallback or probe, residual obligations, and complexity cost.

### FUT01 — Custom lifetime dependency annotations

- **Use when:** A domain view must safely escape a helper while remaining tied to owner storage.
- **Invariant:** No view use after the declared owner lifetime.
- **Boundaries:** Construction, forwarding accessors, owner mutation, erasure to pointers or closures, and foreign calls.
- **Example:** Keep `withBytes { ... }` closure-scoped in production; isolate a flagged `@_lifetime`/`Span` prototype in a preview target.
- **Residual obligations:** Correct dependency declaration, pointee initialization, bounds, exclusivity, and foreign lifetime behavior.
- **Cost:** Experimental syntax and diagnostics, compiler churn, and poor deployability; prefer closure scope until the dependency removes a material misuse.

### FUT02 — Yielding coroutine accessors

- **Use when:** A projection needs setup/cleanup or temporary materialization around caller access.
- **Invariant:** The yielded access ends before coroutine cleanup and cannot escape its valid scope.
- **Boundaries:** Accessor entry/exit, reentrancy, mutation, nested projections, protocol witnesses, and erasure.
- **Example:** A `yielding mutate` dictionary-style projection behind `-enable-experimental-feature CoroutineAccessors`.
- **Residual obligations:** Cleanup success, exclusivity, actor isolation, and behavior if the caller throws or cancels.
- **Cost:** Experimental flag, coroutine overhead, narrower escape behavior, and harder protocol/API evolution.

### FUT03 — Additional noncopyable `Optional` operations

- **Use when:** Optional storage must expose or insert a noncopyable payload without transferring the whole container.
- **Invariant:** Borrowed/exclusive payload access preserves the `Optional` owner and initialized state.
- **Boundaries:** `ref`, `mutableRef`, `put`, mapping, switching, replacement, and erasure through copyable abstractions.
- **Example:** Today, use borrowing `switch` or `take()`-style explicit transitions instead of assuming SE-0532 APIs exist.
- **Residual obligations:** Nil handling, mutation scope, error rollback, and payload cleanup.
- **Cost:** Fallbacks are more verbose; adopting manuscript APIs early creates source churn.

### FUT04 — Compile-time literal expressions

- **Use when:** Repeated literal dimensions or bit patterns need one statically reduced expression.
- **Invariant:** The supported expression reduces to the same concrete literal at every type use.
- **Boundaries:** Constant declaration, generic argument, operator subset, overflow, visibility, and macro generation.
- **Example:** Keep `InlineArray<5, Byte>` today rather than relying on `InlineArray<(2 + 3), Byte>`.
- **Residual obligations:** Runtime indices, allocation feasibility, algorithm semantics, and unsupported expression forms.
- **Cost:** Experimental/absent implementation, constrained evaluator, and diagnostics that may expose compiler internals.

### FUT05 — General arithmetic and refinement constraints

- **Use when:** An API would materially benefit from relations such as `N > 0` or output length `N + M`.
- **Invariant:** Values and dimensions satisfy the stated predicate throughout construction and mutation.
- **Boundaries:** Raw input, arithmetic overflow, generic composition, decoding, mutation, and erasure to ordinary integers/collections.
- **Example:** Use a validated `NonEmptyArray` or a private-initializer `BoundedCount` plus runtime checks.
- **Residual obligations:** Validator correctness, persistence repair, arithmetic semantics, and external data changes.
- **Cost:** Wrapper and witness proliferation; Swift has no general refinement solver, so do not simulate one with unreadable generics.

### FUT06 — User-defined tuple conformances

- **Use when:** A heterogeneous structural product needs protocol participation without a wrapper.
- **Invariant:** Each element meets the protocol constraint and the derived operation preserves element order/semantics.
- **Boundaries:** Tuple construction, labels, arity, element conformance, erasure, and evolution of structural shape.
- **Example:** Define `struct Coordinate: Hashable { var x: Int; var y: Int }` instead of requiring `(Int, Int): Hashable`.
- **Residual obligations:** Semantic equality/hashing laws and domain meaning of the product.
- **Cost:** Nominal wrappers add declarations but improve diagnostics and API ownership; unavailable tuple conformances cannot be promised.

### FUT07 — Noncopyable tuple and pack elements

- **Use when:** A heterogeneous aggregate must contain multiple uniquely owned resources with statically related types.
- **Invariant:** No resource element is implicitly copied and each consumption invalidates only legal ownership paths.
- **Boundaries:** Tuple/pack construction, destructuring, partial consumption, iteration, generic forwarding, and existential erasure.
- **Example:** Use a nominal `struct SessionResources: ~Copyable` with explicit fields and transitions.
- **Residual obligations:** Dropped resources, partial failure, cleanup ordering, and foreign-handle uniqueness.
- **Cost:** Nominal aggregates do not generalize arbitrary arity; unavailable variadic ownership syntax should not drive public API design.

### FUT08 — `InlineArray` equality and hashing conformances

- **Use when:** A fixed-length block needs generic equality or hash-based collection membership.
- **Invariant:** Equality and hashing cover the same ordered elements and satisfy protocol laws.
- **Boundaries:** Element conformance, count, mutation while keyed, protocol erasure, and deployment availability.
- **Example:** Wrap the array in a domain type with explicit `==`/`hash(into:)` on Swift 6.4.
- **Residual obligations:** Hash stability policy, semantic equivalence, and mutation discipline.
- **Cost:** Wrapper code and possible element traversal; waiting for Swift Next avoids claiming a nonexistent 6.4 conformance.

### FUT09 — Rigid fixed-capacity heap containers

- **Use when:** Heap storage is needed but implicit capacity growth is operationally unacceptable.
- **Invariant:** Growth happens only through named capacity-changing operations; ordinary insertion respects available capacity.
- **Boundaries:** Initialization, append/insert, reserve/resize, copying/ownership, decoding, and foreign allocation.
- **Example:** Use a private-storage bounded container that checks `count < capacity` before insertion.
- **Residual obligations:** Runtime capacity choice, allocation failure, element cleanup, and thread safety.
- **Cost:** Runtime checks and a custom container surface; the declined `RigidArray` design never supplied static capacity proof.

### FUT10 — Interior-mutable cells and externally aliased memory

- **Use when:** Foreign, volatile, atomic, or synchronized storage can change through aliases outside ordinary exclusivity.
- **Invariant:** The type distinguishes lifetime/bounds safety from the separate synchronization and volatility contract.
- **Boundaries:** Cell creation, shared access, synchronization primitive, FFI, pointer escape, and destruction.
- **Example:** Keep MMIO or shared-memory access behind a narrowly audited unsafe adapter while SE-0556 remains under review.
- **Residual obligations:** Data-race freedom, memory ordering, volatile semantics, device rules, and foreign lifetime.
- **Cost:** Unsafe and platform-specific reasoning remains; a cell abstraction can make aliasing explicit but cannot make unsynchronized access safe.

### FUT11 — Single-value `Span` adapters

- **Use when:** A scalar must temporarily satisfy a bulk-processing API without allocating or copying.
- **Invariant:** The one-element view shares the scalar's lifetime and, for mutation, its exclusive access.
- **Boundaries:** Scalar borrow, span construction, callee escape, mutation, raw-byte conversion, and closure capture.
- **Example:** Use `Ref`/`MutableRef` or a closure-scoped pointer adapter until the proposed `Span` initializer ships.
- **Residual obligations:** Callee nonescape, alignment, initialization, byte interpretation, and actor isolation.
- **Cost:** Adapter ceremony today; premature proposal use creates compiler-version coupling.

### FUT12 — Field mutation and consumption inside destructors

- **Use when:** Noncopyable teardown must transfer, mutate, or conditionally dispose of an owned field.
- **Invariant:** Fields are consumed or finalized without resurrecting the destroyed whole value.
- **Boundaries:** Construction, partial consumption, `deinit`, throwing transitions, fallback cleanup, and foreign release.
- **Example:** Move fallible or async shutdown into explicit `close()`/`finish()` and keep `deinit` as a synchronous defensive fallback.
- **Residual obligations:** Cleanup failure, async work, ordering, idempotence, and leak behavior.
- **Cost:** Explicit lifecycle states and callers; accepted SE-0544 does not make the behavior available in Swift 6.4.

### FUT13 — Value parameters beyond `Swift.Int`

- **Use when:** Types must vary over a finite compile-time boolean, enum, string, identifier, or richer value.
- **Invariant:** Different parameter values denote distinct static types and only legal values construct them.
- **Boundaries:** Literal parsing, generic substitution, serialization, erasure, public ABI, and generated code.
- **Example:** Use nominal marker types such as `Encrypted`/`Plaintext` or validated value wrappers instead of boolean value generics.
- **Residual obligations:** Runtime refinement, schema evolution, marker authenticity, and bridge behavior.
- **Cost:** More nominal declarations and generic axes; current Swift supports only `Swift.Int` value parameters.

## Conflict decisions and evidence limits

- SE-0532's release-blog mention does not override its accepted-but-unimplemented status and the scoped compiler rejections; see [release row 15](#release-15).
- SE-0527's retained manuscript and Apple prose do not override the steering group's decision to decline public `RigidArray`; see [release row 16](#release-16).
- Duplicate supplied core reports count as one result set with unknown toolchain provenance. The supplied performance report also lacks compiler/target identity. Neither establishes independent release coverage or measured allocation, locking, latency, purity, or constant-time behavior.
- Accepted proposals and Linux SIL probes do not establish Apple deployment support. Use Apple symbol documentation or the selected SDK interface; otherwise mark the floor unknown.
- Compilation proves only the checked rule for the exact source, phase, arguments, and toolchain. Validation, semantic laws, cleanup, progress, and exactly-once behavior need separate evidence.

The original source review inspected the archive without running its corpus. Later Apple corpus verification established the recorded 89 compiler outcomes and 15 controls under Apple Swift 6.4, with a macOS 27.0 compile-only target; two runtime sources separately built and ran with the host-compatible target. These are distinct evidence sets. Neither result proves older deployment support or execution of macOS 27 APIs on the verification host. Use [the corpus runner contract](compile-check-runner.md) and a new target-specific report for a new deployment claim.

For performance annotations, the [Swift underscored-attribute reference](https://github.com/swiftlang/swift/blob/main/docs/ReferenceGuides/UnderscoredAttributes.md#_effectseffectname) describes optimizer assumptions whose violation can cause undefined behavior. The [performance-annotation pitch](https://forums.swift.org/t/performance-annotations/54441) concerns compiler diagnostics, not stable general effect types. Unsupported compile-only probes remain outside performance evidence.

# Quality Evaluation Scenarios

Use these scenarios to evaluate the content of a response after the skill triggers. A strong response does not merely name a pattern; it establishes the compatibility envelope, states the invariant, identifies bypasses, proposes the lightest proof, and supplies a migration and validation strategy.


The matching discovery cases are in `trigger-evals.json`. These local scenarios are editable coverage checks, not the frozen native acceptance suite. Repository maintainers use `evals/swift-type-integration/cases.json` for the frozen prompt/rubric identities and `docs/swift-type-integration-verification.md` for executed attempts, accepted selections, and evidence limits. Those repository paths are maintainer pointers; the installed plugin remains usable without them. Editing or passing a local scenario neither changes a frozen criterion nor establishes native-suite acceptance.

Scenarios 15 and 16 split relationship preservation and expression-result modeling into focused local checks. They use the frozen `swift-type-generic-correlation-combined` case as a coverage guide. Scenario 17 sharpens the storage obligation covered by `swift-type-ownership-lifetime-combined`. The prompts are independent natural-user requests; the obligations below are evaluation criteria, not text to send with the prompt.

## 1. iOS 16 Through iOS 26 Notification Adapter

**Prompt**

> The app deploys to iOS 16, uses Xcode 26.5, and has a dozen stringly typed `NotificationCenter` events. Convert one account-change event to the modern typed API without duplicating domain logic.

**Must include**

- Separates iOS deployment availability from compiler and SDK capability.
- Keeps one deployment-neutral domain event type.
- Hides iOS 26 typed messages and the iOS 16–25 `Notification.Name` path behind an adapter.
- Annotates declarations that mention the iOS 26 types; it does not rely only on a runtime branch around an unavailable signature.
- Specifies equivalent delivery isolation, ordering, filtering, buffering, and observation lifetime for both paths.
- Tests the adapter contract independently from Foundation transport.

**Must not include**

- An unconditional iOS 26 type in a public signature available on iOS 16.
- Raw `userInfo` dictionaries in feature code.
- A claim that typed broadcast is automatically better architecture than a direct dependency or stream.

## 2. `InlineArray` Suggested for a Business Count

**Prompt**

> A `ColorStop` always has exactly three channels. The package deploys to iOS 16. Should the model store `InlineArray<3, UInt8>`?

**Must include**

- Says `InlineArray` is iOS 26+ and therefore not a baseline signature for this package.
- Distinguishes a semantic cardinality rule from a layout/performance requirement.
- Prefers a three-field domain struct, tuple hidden behind a nominal type, or checked collection unless profiling establishes a layout need.
- Notes that a new compiler feature and a new runtime standard-library type have different compatibility properties.

**Must not include**

- “It compiles in current Swift, so the referenced runtime symbol is available on iOS 16.”
- A source-only `#if compiler` gate presented as sufficient runtime availability handling.

## 3. Refined `Codable` Value

**Prompt**

> Implement `Percentage` in the closed interval 0...100. It must be Codable and safe against malformed persisted data.

**Must include**

- Private storage and a checked initializer.
- A custom decoder that invokes the same checked path.
- Boundary tests for -1, 0, 100, and 101 plus malformed decoded input.
- An explicit encoding representation.
- An audit of `RawRepresentable`, literal conformance, memberwise initialization, mutable storage, and test-only escape hatches.

**Must not include**

- Synthesized `Decodable` that writes private storage directly.
- A public `rawValue` initializer that accepts out-of-range values.
- Floating-point exactness assumptions if the chosen representation is `Double`.

## 4. Phantom IDs During Migration

**Prompt**

> Replace UUID parameters with `UserID` and `WorkspaceID` in a large app, while preserving a temporary Objective-C caller.

**Must include**

- Nominal or sealed phantom wrappers that are not interchangeable.
- Core APIs changed before outer call sites, allowing compiler errors to reveal migration work.
- Conversion at parsing, persistence, and Objective-C boundaries.
- A narrow compatibility shim that is deprecated or isolated, rather than raw overloads throughout the codebase.
- A compile-fail fixture or equivalent compile-time assertion for the swapped-ID misuse.

**Must not include**

- `typealias UserID = UUID` as the safety mechanism.
- Public marker conformance that lets clients forge domains.

## 5. Mutable Cache and Strict Concurrency

**Prompt**

> A class wraps an `NSMutableDictionary` and is marked `@unchecked Sendable`. It is shared by tasks and sometimes crashes.

**Must include**

- Rejects `@unchecked Sendable` as a proof by itself.
- Defines one owner for the complete mutable invariant: normally an actor; a lock only with a synchronous, measured need.
- Avoids returning the mutable reference or pointers into protected state.
- Uses immutable `Sendable` snapshots across isolation.
- For an iOS 16 lock implementation, can use an `OSAllocatedUnfairLock`-backed adapter; it does not expose `Synchronization.Mutex` below iOS 18.
- Includes stress or concurrency tests and reentrancy review if actor methods suspend.

**Must not include**

- One lock per property when the invariant spans multiple properties.
- Holding a lock across `await`.
- An assertion that `Sendable` makes mutations atomic.

## 6. Typed Throws and Cancellation

**Prompt**

> Make a service method use typed throws so UI code can exhaustively switch over failures. The transport also throws cancellation and evolving HTTP errors.

**Must include**

- Questions whether a closed typed surface is genuinely stable and useful at this layer.
- Keeps untyped `throws` as a valid default for an evolving transport boundary.
- If mapping to a closed service error, treats cancellation intentionally, either as a modeled case or by preserving `CancellationError` through an untyped surface.
- Explains public resilience implications of adding future enum cases.
- Uses an unconditional typed catch plus a switch when exhaustive handling matters.

**Must not include**

- Mapping cancellation to a generic network outage without an explicit product policy.
- A giant application-wide error enum.

## 7. Single-Use Native Handle

**Prompt**

> Wrap a C handle that must be released once, can be inspected while alive, and cannot escape borrowed buffers.

**Must include**

- Starts with the simplest safe ownership shape; closure-scoped access may centralize cleanup but is not called a static nonescape or single-use proof for copyable values.
- Uses `~Copyable`, `borrowing`, and `consuming` only when supported by the actual toolchain and when copies are the bug.
- Defines cleanup on normal scope exit, explicit close, partial initialization, and error paths.
- Ties any nonescapable view to the owner with a valid lifetime relationship; a bare `~Escapable` declaration is not called a proof.
- Keeps unsafe pointer operations inside a small audited wrapper.

**Must not include**

- A reachable `fatalError` placeholder.
- A claim that `~Copyable` automatically releases the C resource.
- A borrowed view stored beyond the closure or owner lifetime.

## 8. Capability Versus Current Authorization

**Prompt**

> Create a token proving that an account can be deleted, but permissions can be revoked remotely at any time.

**Must include**

- Distinguishes a point-in-time proof from continuously valid authority.
- Uses a private-initializer capability only if its lifetime and revocation semantics are acceptable.
- Otherwise keeps the authoritative check and mutation in one actor/service transaction.
- Binds the capability to the relevant account and, where needed, expiry, session, revision, or nonce.
- Prevents public construction or public marker conformance from forging the proof.

**Must not include**

- A bare `isAdmin: Bool` parameter.
- A timeless token presented as proof after revocation.

## 9. Public Framework State Model

**Prompt**

> A binary-distributed SDK exposes a public enum for server job status and a public typed error. New server cases are expected.

**Must include**

- Separates the external open string domain from an internal closed semantic model.
- Discusses nonfrozen public enums, unknown-value preservation, and client exhaustive switches.
- Avoids making every transport failure a permanent source-level error case.
- Accounts for `BUILD_LIBRARY_FOR_DISTRIBUTION`, ABI, and minimum deployment target.
- Tests unknown future values and old-client behavior.

**Must not include**

- Silently mapping all unknown server states to an existing state.
- Treating an internal exhaustive enum and a resilient public enum as the same design problem.

## 10. Detect and Remove Overmodeling

**Prompt**

> A checkout form uses generic states for name, address, payment, coupon, inventory, and consent. Most functions are generic over all six axes.

**Must include**

- Identifies which axes actually remove callable invalid operations.
- Recommends collapsing dynamic or combinatorial facts into a validated value or a finite enum.
- Considers separate concrete phase structs, a runtime validation report, or a simple staged boundary.
- Sets rollback criteria based on diagnostics, build time, API leakage, and maintenance cost.
- Preserves the high-value invariant while reducing generic surface area.

**Must not include**

- More phantom axes by default.
- “The compiler accepts it” as evidence that the architecture is maintainable.

## 11. Stale SwiftUI Effects Across iOS 16 and 17

**Prompt**

> A search screen starts a task on every query change. Cancellation is attempted, but an older response can still overwrite newer results. The app deploys to iOS 16 and uses Observation on iOS 17+.

**Must include**

- Keeps the domain state/action/effect model independent of `ObservableObject` and `@Observable`.
- Gives each request an identity and accepts a completion only when it matches the currently active request.
- Treats cancellation as resource control, not proof that no callback or remote side effect can arrive.
- Uses main-actor ownership for presentation mutation and immutable/sendable values across isolation.
- Provides an iOS 16 observation adapter and an availability-gated iOS 17+ adapter that share transition logic.
- Tests stale completion, cancellation before and after suspension, account/query changes, and semantic parity between adapters.

**Must not include**

- A task handle or closure stored in persistent/restorable state.
- A claim that `Task.cancel()` alone prevents stale mutation.
- `@Observable` in an unguarded declaration that must load on iOS 16.

## 12. Protocol-Extension Dispatch and Existential Relationships

**Prompt**

> A conforming type defines `serialize()`, but a generic function constrained to the protocol calls the extension's default implementation. The API also needs heterogeneous serializers for one output type.

**Must include**

- Identifies whether `serialize()` is a protocol requirement or merely an extension member and explains the resulting dispatch.
- Makes dynamically selected behavior a protocol requirement, or uses a witness struct/closure when an open protocol hierarchy is unnecessary.
- Preserves the associated input/output relationship with a generic parameter, primary associated type, or constrained existential.
- Uses type erasure only after naming which relationship is intentionally erased and implements every path without force casts or placeholders.
- Notes compiler/toolchain requirements separately from the iOS 16 deployment target.
- Adds compile-time or behavioral tests through concrete, generic, and existential call paths.

**Must not include**

- A same-named extension method presented as an override.
- `any Protocol` used where losing associated-type relationships makes the API less safe.
- A reachable `fatalError` to complete an eraser.

## 13. Security-Sensitive URL and File Destination

**Prompt**

> Validate an OAuth callback URL and a server-provided file name before writing under the app's import directory.

**Must include**

- States that `URL` parsing and nominal wrappers do not themselves prove authorization or safety.
- Validates URL components structurally: exact scheme/host/port/path/query policy, with explicit canonicalization decisions.
- Rejects string-prefix host checks and raw path concatenation.
- Resolves a constrained relative name against a trusted root and addresses symlinks plus check/use races where the threat model requires it.
- Keeps server-side OAuth state/nonce, redirect registration, and authorization checks authoritative.
- Models any security-scoped access as a balanced runtime lifetime rather than a timeless URL capability.

**Must not include**

- `absoluteString.hasPrefix(...)` as host validation.
- A “sanitized string” type shared across URL, HTML, SQL, and shell contexts.
- A claim that lexical path standardization defeats adversarial filesystem races.

## 14. Strict Memory Safety and `BitwiseCopyable`

**Prompt**

> A current-Swift module wraps a C packet buffer, uses pointer arithmetic, and constrains packet headers to `BitwiseCopyable`. Harden the design for an iOS 16 product.

**Must include**

- Treats strict memory safety as an opt-in compiler/CI diagnostic lane, not a runtime OS feature or proof that unsafe code is correct.
- Shrinks `unsafe` regions and writes the bounds, alignment, initialization, lifetime, exclusivity, and isolation preconditions beside them.
- Exposes a safe wrapper only when it discharges every caller precondition; otherwise keeps unsafety visible in the API.
- Explains that `BitwiseCopyable` permits direct memory copying but does not guarantee C layout, stable serialization, byte order, no padding, or validity of arbitrary bytes.
- Defines an explicit wire format and validates lengths before binding or loading typed values.
- Uses sanitizers, fuzzing, malformed-input tests, and the selected current compiler plus runtime matrix in addition to strict-memory diagnostics.

**Must not include**

- Raw memory dumping as serialization.
- `@safe` or `BitwiseCopyable` used as diagnostic suppression.
- An iOS 26 availability requirement inferred solely from using a current Swift language feature.

## 15. Correlated Readers and Processors

Matching trigger ID: `generic-correlation`.

**Prompt**

> A Swift import pipeline lets callers pair any file reader with any processor. We have accidentally sent decoded images to a processor that expects account records. Recommend a small API that prevents this mix-up while still letting us choose among different readers at runtime. Explain what remains to check; keep this assessment read-only.

**Must include**

- Loads the relevant generic-proof recipe and states the relationship: a processor must accept the selected reader's decoded type.
- Uses the lightest adequate generic, associated-type, or closed-family model. Runtime selection preserves that relation rather than independently erasing both halves.
- Shows one valid reader/processor pairing and the concrete rejected image-reader/account-processor pairing.
- Audits construction, registry lookup, type erasure, and any public witness issuance; dynamic data still requires validation at the decoding boundary.
- Proposes paired valid-use and misuse compilation controls with shared compiler settings, plus a runtime valid-processing check. Reports each as run or pending and limits any conclusion to the inspected boundary.
- Explains the source/API migration and the complexity tradeoff; leaves the workspace unchanged.

**Must not include**

- An uncorrelated pair of erased objects repaired with force casts, unchecked downcasts, or a reachable placeholder.
- Equality witnesses or higher-rank machinery without a concrete need that simpler associated-family modeling cannot meet.
- A claim that the static type relationship validates file contents or proves processor semantics.

## 16. Expression Result Sorts

Matching trigger ID: `typed-expression-sorts`.

**Prompt**

> Our Swift rules editor builds expressions for text, numbers, and yes-or-no results. A text literal can currently be attached to a condition and crash evaluation later. Suggest the smallest model that prevents these mismatches and show how a valid condition would be evaluated. Keep the assessment read-only.

**Must include**

- Loads the focused generic-proof recipe and keeps each expression's payload and evaluator result sort correlated.
- Selects a closed associated-family or separate typed expression forms when adequate; reserves equality-witness/GADT-style machinery for a materially necessary shared indexed representation.
- Shows a concrete valid condition with its evaluation result, and the rejected attempt to use a text literal where a boolean result is required.
- Audits constructors, public witness issuance, decoding, and erasure. Does not let an unrestricted initializer or cast restore the forbidden pairing.
- Proposes a positive evaluator test and a paired compile-fail misuse control when the chosen API supports it; names compiler settings and marks unrun checks pending.
- Separates the static result-sort guarantee from evaluator semantics, termination, optimizer correctness, and external-data validity; leaves the workspace unchanged.

**Must not include**

- A universal untyped payload with a promised result type enforced only by a later runtime cast.
- A phantom result marker described as enforcement when payload construction remains unrestricted.
- Fabricated compiler acceptance or rejection.

## 17. Borrowed Views and Live, Stable Storage

Matching trigger ID: `borrowed-view-storage`.

**Prompt**

> Our Swift media decoder lends a view into a reusable buffer during a callback. A caller queues that view for later work, and native code can refill or replace the buffer. Would changing the decoder handle to prevent copying make this safe? Recommend a small boundary and checks; keep the review read-only.

**Must include**

- Loads the complete focused ownership/lending section and distinguishes callback-scoped borrowing from ownership transfer. Chooses scoped use, an owned copy, or a supported lifetime-dependent projection according to what must survive.
- Names the concrete misuse: queued work using the borrowed view after its storage is no longer valid.
- States the implementation obligation to keep the actual owner alive, the storage initialized and stable, and foreign aliases from invalidating it throughout each permitted access. A live Swift handle alone does not establish those facts.
- Audits buffer refill, replacement, reallocation, destruction, escaping closures, raw handles/pointers, erasure, foreign aliases, and actor/exclusivity boundaries.
- Uses noncopyability only when duplicating decoder authority is itself invalid; it does not prove deep immutability, unique foreign ownership, or borrowed storage validity.
- Separates supported compile-time escape/use-after-consume controls from runtime tests for buffer replacement, queued work, and cleanup. Records compiler/feature/deployment settings and marks checks run or pending with their limits.
- Bounds generation or epoch checks to accesses routed through the checked facade; extracted raw pointers remain outside that guard. Leaves the workspace unchanged.

**Must not include**

- A claim that a noncopyable handle, actor isolation, or a bare nonescapable declaration proves the borrowed buffer remains live and stable.
- A generation check presented as protection for arbitrary previously extracted pointers.
- Deferred borrowed access without a demonstrated lifetime relationship or ownership transfer.

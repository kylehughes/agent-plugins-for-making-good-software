# Testing, Migration, and Review

Use this reference when implementing a refactor, proving an invariant remains closed, or reviewing whether stronger types justify their cost.

## Test the Boundary, Not Just the Happy Path

A type-level model removes some runtime states, but constructors, decoding, persistence, interop, availability, and concurrency remain runtime concerns.

For every refined value, test:

- Smallest valid value.
- Largest valid value.
- Values immediately outside each bound.
- Empty and whitespace-only input where applicable.
- Unicode, locale, normalization, and case behavior.
- `NaN`, infinity, signed zero, overflow, and rounding for numerics.
- Canonicalization idempotence.
- Equality and hash behavior after canonicalization.
- Malformed wire and persisted forms.
- Unknown external enum cases.

Prefer table-driven tests for policy-heavy constructors.

## Property Tests

Property-based testing is useful when the invariant is algebraic or the input space is broad.

Candidate properties:

- Every successfully constructed bounded value satisfies the bound.
- Canonicalizing twice equals canonicalizing once.
- Encoding then decoding preserves identity.
- Sorting wrapper output is always ordered.
- Nonempty collection operations never produce an empty internal state.
- Unit conversion round-trips within documented tolerance.
- A valid transition sequence never exposes an illegal operation.

Do not replace example tests with random tests. Keep named regression cases for failures that matter.

## Compile-Fail Fixtures

Use compile-fail tests for high-value guarantees that ordinary runtime tests cannot observe:

- `WorkspaceID` cannot be passed as `UserID`.
- A private validated initializer cannot be bypassed.
- A method is absent in the wrong typestate.
- A noncopyable value cannot be used after consumption.
- A borrowed view cannot escape when nonescapability and its owner dependency are compiler-visible.
- A non-Sendable value cannot cross an isolation boundary under strict concurrency.

Do not expect compile-fail coverage from pointer closures alone: copyable unsafe pointers may escape unless the type system expresses the lifetime relationship. A basic harness invokes a compiler pipeline that performs ownership and concurrency checking, then expects a nonzero exit status. `swiftc -typecheck` alone may omit some ownership-flow diagnostics; `scripts/check_examples.sh` uses `-emit-module -parse-as-library` for that reason. Use Swift 6 mode and the same strictness settings as the selected current build.

Give every fixture one intended error and verify a stable diagnostic fragment from an `expected-error` marker. Avoid matching the entire diagnostic string because compiler wording changes. Keep fixtures small and self-contained so an unrelated diagnostic cannot satisfy the test accidentally.

## API Surface Tests

For public packages or frameworks, add checks for generated interfaces and compatibility:

- `swift-symbolgraph-extract` or API digester where available.
- Generated `.swiftinterface` inspection for binary frameworks.
- Availability annotations in public signatures.
- Accidental public initializers or setters.
- `@frozen`, `@inlinable`, and generic constraints.
- Actor isolation and `Sendable` changes.
- Typed error and enum case changes.

A source package and a binary framework need different baselines. Record which one the project promises.

## Serialization and Persistence Tests

For `Codable` and persistence:

1. Valid round trip.
2. Malformed raw field.
3. Missing required field.
4. Unknown enum value.
5. Historical schema fixture.
6. Canonicalization change fixture.
7. Corrupt cache or partial record.
8. Downgrade/rollback behavior when releases can move backward.

Fixtures should represent bytes or records from actual prior versions, not only values produced by the current encoder.

## Availability Tests

Test the domain-facing behavior of both implementations directly even when CI cannot launch every old OS simulator.

```text
Legacy adapter contract tests
Modern adapter contract tests
Shared semantic test suite
Runtime selection smoke test
```

Verify:

- Ordering.
- Actor/queue delivery.
- Cancellation and observation lifetime.
- Buffering/backpressure.
- Error mapping.
- Subject or object filtering.
- Duplicate suppression.

Compilation alone does not prove an iOS 16 fallback behaves like its iOS 26 counterpart.

## Concurrency Tests

Use strict concurrency diagnostics as a static test and targeted runtime tests for behavior.

For actor-backed state:

- Concurrent calls preserve invariants.
- Reentrancy at `await` does not duplicate work or lose updates.
- Cancellation leaves a valid state.
- Snapshots do not expose mutable references.

For lock-backed state:

- All access goes through the lock.
- Stress concurrent reads/writes.
- Test reentrant callback scenarios if callbacks are permitted.
- Use Thread Sanitizer where practical.
- Confirm no lock is held across `await`.
- Establish and test lock ordering for multi-lock operations.

Runtime stress tests cannot prove absence of races, but they can expose violations of the documented synchronization design.

## Performance Validation

Type modeling should not be justified by assumed performance.

Measure before adopting:

- `InlineArray` for allocation/layout.
- `~Copyable` to remove copies or ARC traffic.
- Locks instead of actors.
- Custom type erasure.
- Large generic state graphs.
- Canonicalization on hot paths.

Use representative release builds. Check code size, compile time, specialization, ARC, allocation count, and latency as relevant.

A nominal wrapper around a primitive is generally optimized well, but verify hot public generic APIs and cross-module optimization when performance is critical.

## Compiler-Driven Migration

A reliable migration sequence:

### 1. Add the new type without changing callers

Implement validation, access control, conformances, and tests. Do not expose unchecked conveniences merely to reduce initial compiler errors.

### 2. Change the innermost domain operation

```swift
// Before
func loadUser(id: UUID) async throws -> User

// After
func loadUser(id: UserID) async throws -> User
```

This creates a focused set of compiler errors.

### 3. Follow errors outward

At each caller, decide whether it already has a `UserID` or is a raw boundary that must construct one. Do not immediately add `UserID(rawValue:)` everywhere without asking whether the value's domain is known.

### 4. Move construction to sources

Convert at:

- JSON mapping.
- Database fetch.
- Route parsing.
- UI submission.
- Notification adapter.
- Objective-C/C bridge.

Core functions should stop accepting raw values.

### 5. Remove bypasses

Delete or deprecate raw overloads, public storage, duplicate flags, and old helper initializers. A migration is incomplete while the old unsafe path remains the easiest path.

### 6. Update persistence and external APIs

Add schema migration, custom decoding, Objective-C façade changes, and availability adapters.

### 7. Add negative fixtures

Lock in the compiler error that motivated the refactor.

### 8. Measure and simplify

Check diagnostics, call-site readability, generic growth, compile time, and performance. Roll back unnecessary type axes.

## Incremental Adoption Patterns

### Adapter-first

Introduce a typed façade around a legacy subsystem while leaving internals unchanged. Useful for large Objective-C or notification-heavy codebases.

### Core-first

Change pure domain and service APIs, then migrate outer layers. Usually best when raw values are already localized.

### Read-path before write-path

Decode/map into refined values first, then update creation and persistence. Useful when historical data risk is high.

### Shadow validation

Temporarily validate and log without rejecting, to measure existing invalid data before enforcing a tighter invariant. Do not leave shadow mode indefinitely; define an exit criterion.

### Dual representation

Maintain old and new wire/schema representations behind one domain type during rollout. Keep conversion centralized and remove the old path after compatibility windows close.

## Source Compatibility and Deprecation

When changing a public API:

- Add a typed overload and deprecate the raw overload with a migration message.
- Avoid ambiguous overloads where literals can match both.
- Preserve wire format when only static identity is changing.
- Use unavailable renames for mechanical symbol moves where appropriate.
- Document canonicalization or validation changes as behavior changes.
- Give clients a way to handle historical invalid values.

Do not keep deprecated raw overloads forever if they undermine the core proof. Set a removal version.

## Code Review Rubric

Classify each proposal on five dimensions.

### 1. Correctness gain

- Which invalid state or operation disappears?
- Is the failure moved to compile time or one controlled boundary?
- Can the claim be demonstrated with a negative fixture?

### 2. Proof closure

- Are all constructors, mutations, decoders, persistence paths, macros, and interop paths audited?
- Are unchecked paths narrow and justified?
- Can external clients forge a state, conformance, or capability?

### 3. Compatibility

- Deployment target, selected current Xcode/Swift toolchain, SDK, settings, and ABI known?
- Runtime availability gates correct?
- iOS 16 fallback present when needed?
- Beta-only dependencies excluded by default?

### 4. Usability

- Does the compiler diagnostic explain the domain mistake?
- Are call sites clearer?
- Is construction ergonomic at legitimate boundaries?
- Can values be logged, persisted, and presented without leaking raw escape hatches?

### 5. Cost

- Generic and conceptual complexity.
- Migration size.
- Compile time and code size.
- Runtime overhead.
- Public compatibility commitment.
- Team familiarity and maintenance.

A high-cost model needs a high-value invariant.

## Review Finding Vocabulary

Use precise labels:

- **Proven:** ordinary Swift APIs cannot represent the invalid state or operation.
- **Boundary-checked:** raw input is validated at one controlled entry point.
- **Convention-only:** names, comments, or call-site discipline carry the rule.
- **Bypassable:** an initializer, decoder, mutation, bridge, or unchecked API violates the claimed proof.
- **Availability-unsafe:** code compiles in one environment but leaks a later runtime symbol into the baseline.
- **Concurrency-asserted:** safety relies on `@unchecked Sendable` without a complete synchronization design.
- **Overmodeled:** complexity exceeds the prevented risk and a simpler enum/struct/check would be clearer.

## Red Flags

- “Private storage means Codable is safe” without inspecting synthesis.
- “It compiles with iOS 16 target” used as the only availability evidence.
- A compiler conditional used instead of `if #available` for a runtime symbol.
- Public raw initializer retained next to a validated initializer.
- A public marker protocol described as an authorization capability.
- `@unchecked Sendable` plus mutable state and no lock/actor.
- Lock held while awaiting or calling arbitrary code.
- `InlineArray` selected solely to encode a small count.
- Typestate values erased immediately into `Any`.
- One error enum spanning validation, networking, persistence, UI, and cancellation.
- Force casts or `unsafeBitCast` used to implement state transitions.
- Beta syntax appearing in baseline production code without a stable branch.

## Completion Checklist

Before declaring the change complete:

- Invariant and invalid states documented.
- Environment and compatibility lane recorded.
- Construction and mutation sealed.
- Raw boundary mapping implemented.
- Persistence and historical data handled.
- Availability fallback implemented and contract-tested.
- Positive, negative, and round-trip tests added.
- Compile-fail fixture added for valuable static guarantees.
- Strict concurrency build passes at intended settings.
- Public API/ABI changes reviewed.
- Performance claims measured.
- Old bypasses removed or have a dated deprecation plan.
- Complexity reassessed after migration.

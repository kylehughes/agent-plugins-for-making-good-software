---
name: modeling-swift-types-for-correctness
description: >-
  Design or refactor Swift models so invalid states, swapped identifiers, unchecked boundary values,
  illegal transitions, unsafe ownership, and concurrency misuse are difficult or impossible to express.
  Use for SwiftUI feature state, forms, navigation and effect identity; boolean or optional state
  explosions; enums with associated values; validated newtypes; phantom IDs; units or trust states;
  typestate and staged builders; capability tokens; generic/protocol relationships; typed errors;
  Sendable or actor isolation; ~Copyable or ~Escapable; security/resource boundaries; Codable,
  persistence, Objective-C or C interop; and version-aware APIs that deploy to iOS 16 with newer SDKs.
  Also use to audit whether a type invariant is bypassable or a design is overengineered. Do not use for
  cosmetic naming-only refactors with no meaningful invariant.
---

# Model Swift Types for Correctness

## Mission

Use Swift's type system to remove invalid operations and invalid state combinations from ordinary code paths. Prefer the lightest model that creates a useful compiler error at the misuse site.

Do not claim that a type proves an invariant merely because its intended initializer validates. The proof is only as strong as every construction route, mutation path, synthesized conformance, decoder, macro, Objective-C or C bridge, and unchecked escape hatch.

Swift cannot prove arbitrary facts about runtime input before validation. Refine untrusted input at a boundary, then pass the refined value inward.

## Operating Procedure

### 1. Establish the compatibility envelope before proposing syntax

Inspect the project rather than inferring capability from the deployment target. Determine all of these independently:

1. Minimum deployment versions, especially `IPHONEOS_DEPLOYMENT_TARGET` or SwiftPM `platforms`.
2. The selected Xcode channel and the actual compiler reported by `xcrun swift --version`.
3. That every affected target uses Swift 6 language mode (`SWIFT_VERSION = 6.0` or `.v6`).
4. The SDK used to compile.
5. Strict-concurrency, default-actor-isolation, upcoming-feature, experimental-feature, and strict-memory-safety settings.
6. Whether the affected target is an app, package, binary framework, or library-evolution boundary.

Run `python3 scripts/audit_project.py <project-root>` for a heuristic inventory, then verify target-specific Xcode settings. Treat any non-Swift-6 target as migration work, not as a compatibility lane. Current Swift language features can often deploy to iOS 16; SDK and standard-library symbols still require their documented runtime availability.

Use the right gate:

- `#if canImport(Module)` for optional module presence.
- `@available(iOS 26, *)` on declarations and `if #available(iOS 26, *)` at runtime for OS-gated APIs.
- A narrowly isolated `#if compiler(...)` only when the repository deliberately tests both current stable and current beta Xcode; never as a runtime check.
- Do not add language-mode conditional branches. This skill assumes one Swift 6 language mode.
- Never use `#if os(iOS)` as an OS-version check.

Read [references/ios-versioning.md](references/ios-versioning.md) whenever deployment spans iOS 16 through current or beta SDKs.

### 2. State the invariant before choosing a pattern

Write one sentence in domain language:

> A submitted registration has a validated email and accepted terms, and it cannot return to draft state.

Then list the currently representable invalid cases. Include malformed external data, not just in-memory callers.

Classify the invariant:

| Axis | Typical question |
|---|---|
| Variant | Must exactly one case be active? |
| Correlation | Must values appear or change together? |
| Identity | Can same-representation values be accidentally swapped? |
| Refinement | Must raw input satisfy bounds, format, ordering, or canonical form? |
| Phase | Are operations valid only before or after a transition? |
| Authority | Must an operation require a permission value only a trusted issuer can construct? |
| Trust | Has text or data been validated, sanitized, escaped, or parameterized? |
| Ownership | Is copying, reuse after consumption, or escaping a borrow the bug? |
| Isolation | Which executor owns mutable state, and what may cross isolation? |
| Failure | Does the caller benefit from a closed, precise failure surface? |
| Layout | Is fixed size or memory representation actually required and measured? |
| Boundary | Where does raw or foreign representation become trusted domain state? |

### 3. Choose the lightest adequate proof

Use this default order unless the domain contradicts it:

| Problem | Default | Escalate when |
|---|---|---|
| Mutually exclusive flags or correlated optionals | Enum with associated values | Different states need materially different APIs or storage |
| Values that must move together | Struct | The collection itself needs non-empty, sorted, keyed, or bounded semantics |
| Swappable IDs or same-typed parameters | Nominal wrapper | Many domains share one implementation; then use a module-owned phantom tag |
| Runtime validation | Private storage plus throwing or failable initializer | Callers need accumulated errors, canonicalization policy, or staged validation |
| State-dependent operations | Separate state structs | Representation is shared and transitions compose; then consider typestate |
| Authorization | Private-initializer capability value | Authority is dynamic or revocable; keep the decision in an actor/service |
| Cross-task mutable state | Actor | A measured synchronous hot path requires a lock |
| Precise local failures | Small error enum or typed throws | The layer is an open integration boundary; preserve or erase errors deliberately |
| Resource lifetime | Scoped operation plus `defer`/cancellation cleanup | Copies or escape must be statically rejected; then use verified ownership/lifetime features |
| Fixed-size storage | Tuple or small domain struct | Profiling proves layout/allocation matters and availability permits `InlineArray` |

A comment, `typealias`, naming convention, or boolean authorization flag is documentation, not a proof.

Read [references/decision-guide.md](references/decision-guide.md) for the full selection matrix and rollback criteria.

### 4. Close every bypass

Audit all routes into and through the type:

- Public, internal, synthesized, memberwise, convenience, literal, and `RawRepresentable` initializers.
- Mutable stored properties, writable subscripts, reference-semantic storage, and collection mutation.
- `Decodable`, database hydration, model macros, reflection, and test fixtures.
- Objective-C initializers, KVC/KVO, `NSCoding`, `NSCopying`, C/C++ imports, unsafe pointers, and raw handles.
- `@unchecked Sendable`, unchecked or `unsafe` factories, `unsafeBitCast`, force casts, force unwraps, and unchecked indexes.
- Public protocol conformances or marker types that outside modules can forge.

Prefer one obvious checked constructor and a narrowly scoped, loudly named unchecked path when one is unavoidable. Document its precondition and keep its callers at a trusted boundary.

### 5. Separate raw, validated, and presented representations

Use a boundary pipeline:

```text
JSON / database / Objective-C / user input
        -> raw DTO or foreign shape
        -> validation and canonicalization
        -> domain type
        -> view or transport projection
```

Do not make malformed wire data impossible to decode by pretending it is already a domain model. Decode raw values, map errors with context, and construct the domain type explicitly. Custom `Decodable` is appropriate when the wire and domain shapes truly coincide, but it must call the same invariant-preserving constructor.

### 6. Select a runtime lane

Use one lane per changed API and state it in the answer or code review:

- **iOS 16 baseline:** Uses the current Swift 6 compiler while avoiding symbols unavailable on iOS 16. This is the default for shared domain code.
- **Availability lane:** Uses a newer SDK API or standard-library type behind declaration and runtime availability, with an iOS 16 fallback.
- **Preview lane:** Uses the current beta Xcode/Swift/iOS SDK only when the repository explicitly opts in. Isolate preview-only source and do not leak preview types into stable domain APIs.

Do not infer runtime support from the fact that syntax compiles. In particular, `InlineArray` is iOS 26+, Foundation's typed notification messages are iOS 26+, `Synchronization.Mutex` is iOS 18+, and `OSAllocatedUnfairLock` is available from iOS 16. `Span` is unusually back-deployed, but APIs that produce spans can have later availability.

### 7. Implement the smallest coherent migration

When editing code:

1. Introduce the domain type and its tests.
2. Change the innermost business operation to require it.
3. Follow compiler errors outward to callers.
4. Convert raw values at source boundaries.
5. Remove or deprecate raw overloads after migration.
6. Keep adapter shims at module or availability boundaries, not throughout core logic.
7. Avoid unrelated architecture cleanup unless it is required to close the invariant.

The compiler should reveal migration sites; tests must still cover runtime validation, serialization, availability fallbacks, cancellation, and interop.

### 8. Validate the proof

At minimum:

- Positive constructor tests for valid and canonicalized values.
- Boundary and adjacent-value tests for every numeric or cardinality constraint.
- Negative tests for malformed decoded or persisted data.
- Round-trip tests when `Codable`, persistence, or Objective-C bridging is involved.
- Concurrency tests or stress tests for actor/lock-backed invariants.
- Compile-fail fixtures for high-value misuse such as swapped IDs or inaccessible construction.
- Builds with the minimum deployment target and the selected current SDK.
- Builds once in Swift 6 language mode with the project’s selected current compiler; test runtime fallback branches separately.

Run `python3 scripts/validate_skill.py .` when modifying this skill. See [references/testing-migration-and-review.md](references/testing-migration-and-review.md) for project-level validation and review checklists.

## Non-Negotiable Rules

1. Never describe a runtime-validated value as compile-time validated before construction succeeds.
2. Never use `typealias` as evidence that two raw-value domains cannot be mixed.
3. Never store derived flags beside their source enum or value unless there is a measured denormalization need and one mutation authority.
4. Never expose public writable storage that can invalidate a validated wrapper.
5. Never synthesize `Decodable` for a refined type without verifying that decoding cannot bypass validation.
6. Do not use `ExpressibleByStringLiteral` for validation that can fail unless literals are guaranteed by construction, checked by a validating macro, or governed by an explicit trap policy.
7. Never treat `RawRepresentable` as validation by itself.
8. Never use a public, freely conformable marker protocol as a trusted-issued capability proof.
9. Never use `@unchecked Sendable` as a fix for diagnostics without a written synchronization or immutability proof.
10. Never choose a lock merely to avoid actor isolation; choose it only for synchronous semantics or measured performance, and keep the critical section small.
11. Never make typed throws the default for an error surface expected to evolve openly across layers.
12. Never expose ownership or nonescapable machinery unless copying or escaping is the actual invariant being defended.
13. Never add compatibility branches for a non-current Swift language mode.
14. Never introduce beta-only syntax or APIs into the baseline lane without an explicit project decision.
15. Never preserve a generic typestate design after it makes call sites, diagnostics, or build times worse than separate concrete types.
16. Never describe a nominal wrapper as security enforcement: authorization, cryptographic verification, revocation, sandbox access, and unsafe-memory proofs remain runtime responsibilities.

## Output Contract

For design, review, or implementation work, provide these results in proportion to the task:

1. **Invariant:** one sentence, plus invalid states removed.
2. **Environment:** deployment target, selected current Xcode/Swift toolchain, SDK, and relevant build settings; mark unknowns.
3. **Chosen model:** why it is the lightest adequate construct.
4. **Proof boundary:** exactly which constructors, decoders, mutations, and interop paths preserve it.
5. **Code:** complete enough to compile in the stated lane; include fallback or gate when needed.
6. **Migration:** compiler-driven sequence and compatibility impact.
7. **Validation:** tests, compile-fail cases, and minimum/current OS coverage.
8. **Tradeoffs:** escape hatches, resilience, performance, and signs the model should be simplified.

When reviewing an existing design, distinguish:

- **Proven:** misuse is unavailable through ordinary APIs.
- **Checked:** misuse is detected at runtime at a controlled boundary.
- **Documented:** convention or comments only.
- **Bypassable:** at least one construction or mutation path violates the claimed proof.

## Reference Map

Load only what the task needs:

- [references/decision-guide.md](references/decision-guide.md): invariant taxonomy, smell matrix, proof ladder, and overmodeling rollback.
- [references/algebraic-and-refined-values.md](references/algebraic-and-refined-values.md): enums, product types, validated values, bounds, units, money, intervals, collections, and `Codable` traps.
- [references/identity-typestate-capabilities.md](references/identity-typestate-capabilities.md): nominal and phantom IDs, typestate, staged builders, capabilities, trust states, and generic-complexity rollback.
- [references/ui-state-navigation-and-effects.md](references/ui-state-navigation-and-effects.md): SwiftUI/UI state, forms, request identity, effects, cancellation, routes, restoration, `OptionSet`, and iOS 16 observation adapters.
- [references/advanced-generics-and-protocols.md](references/advanced-generics-and-protocols.md): same-type relationships, primary associated types, constrained existentials, `some`/`any`, witness structs, dispatch hazards, packs, key paths, and macros.
- [references/ownership-concurrency-errors.md](references/ownership-concurrency-errors.md): `Sendable`, actors, locks, `~Copyable`, borrowing/consuming, nonescapable values, strict memory safety, `BitwiseCopyable`, typed throws, and cancellation.
- [references/boundaries-and-interop.md](references/boundaries-and-interop.md): networking, persistence, notifications, Objective-C/C, analytics, and public API resilience.
- [references/security-and-resource-modeling.md](references/security-and-resource-modeling.md): authentication, revocable authority, secrets, interpreter-specific trust, URLs/paths, filesystem races, handles, cryptographic states, and unsafe-code audits.
- [references/ios-versioning.md](references/ios-versioning.md): one-current-toolchain policy, iOS 16–27 runtime availability, stable versus preview Xcode, and feature availability.
- [references/testing-migration-and-review.md](references/testing-migration-and-review.md): tests, compile-fail fixtures, migration sequencing, performance checks, and review rubric.
- [references/sources.md](references/sources.md): primary specifications and official release documentation used to verify time-sensitive guidance.

## Included Utilities and Fixtures

- `scripts/audit_project.py`: inventories the selected Swift/Xcode toolchain, Swift 6 mode, deployment, availability, and build settings without modifying the project.
- `scripts/validate_skill.py`: validates metadata, links, eval data, and Swift fixtures.
- `scripts/check_examples.sh`: type-checks positive examples and confirms negative fixtures fail.
- `examples/CorePatterns.swift`: deployment-neutral domain modeling examples.
- `examples/CorePatternsRuntimeChecks.swift`: executable validation and `Codable` boundary checks for the core fixtures.
- `examples/CurrentSwiftPatterns.swift`: current Swift 6 typed-errors, ownership, and concurrency examples.
- `examples/CompileFail*.swift`: negative fixtures for identity, sealed construction, typestate, and ownership misuse.
- `evals/trigger-evals.json`: positive and negative activation prompts.
- `evals/quality-evals.md`: scenario-based expectations for skill behavior.

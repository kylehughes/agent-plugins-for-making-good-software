---
name: modeling-swift-types-for-correctness
description: "Model and verify Swift invariants so invalid states are hard to express. Use for state models, typed IDs, validated values, decoding, mutation, legal transitions, ownership, concurrency boundaries, and compiler checks; not cosmetic naming changes."
---

# Model Swift Types for Correctness

Use Swift’s type system to remove invalid operations and state combinations from ordinary code paths. Prefer the lightest representation that produces a useful diagnostic at the misuse site.

This skill owns Swift representation, construction closure, decoding, interop, ownership, isolation, availability, and compiler evidence. For an explicit request to verify or prove an invariant, invoke `universal:verifying-invariants` when available before the assessment, then supply the Swift rules here. Also compose when an enforcement change needs boundary mapping or evidence selection. A narrow implementation with a settled invariant and check does not need that extra workflow. When Universal is absent, use this skill's Swift checklist and report the limits of the assessment.

Swift cannot prove arbitrary facts about runtime input before validation. Refine untrusted input at a boundary, then pass the refined value inward. A validating initializer proves nothing if another initializer, decoder, mutation, or bridge bypasses it.

## Establish the Swift environment

Inspect the project instead of inferring language features from the deployment target:

1. Record minimum deployment versions and SDK.
2. Record the selected Xcode channel and `xcrun swift --version`.
3. Confirm Swift 6 language mode for every affected target.
4. Record strict concurrency, default isolation, upcoming features, experimental features, strict memory safety, and library evolution.
5. Identify app, package, binary framework, and Objective-C or C boundaries.

Run `python3 scripts/audit_project.py <project-root>` for a heuristic inventory, then verify target-specific Xcode settings. Only one current Swift toolchain is in scope. Treat a target outside Swift 6 language mode as migration work rather than a compatibility lane.

Choose one runtime lane:

- **iOS 16 baseline:** current Swift compiler, with no symbols unavailable on iOS 16.
- **Availability lane:** newer SDK or standard-library API behind declaration and runtime availability, with an iOS 16 fallback.
- **Preview lane:** beta Xcode and SDK only after an explicit project decision; isolate preview-only source.

Use `#if canImport(Module)` for module presence, `@available` and `if #available` for runtime APIs, and `#if compiler(...)` only when the repository deliberately tests two current compiler channels. Never use `#if os(iOS)` as a version check or add branches for an older language mode. Read [iOS versioning](references/ios-versioning.md) when deployment spans iOS 16 through current or beta SDKs.

## Choose the Swift representation

Apply the settled invariant to Swift with these defaults:

| Invalid operation or state | Swift representation |
|---|---|
| Mutually exclusive flags or correlated optionals | Enum with associated values |
| Values that must change together | Struct with one mutation authority |
| Swappable same-representation IDs | Nominal wrapper; use a module-owned phantom tag only when several domains share behavior |
| Runtime-refined input | Immutable private storage plus a throwing or failable initializer |
| State-dependent operations | Separate state structs; use typestate when shared representation and transitions justify it |
| Trusted-issued permission | Private-initializer capability value backed by a service or actor when authority is dynamic |
| Cross-task mutable state | Actor; choose a lock only for required synchronous semantics or measured performance |
| Closed local failure surface | Small error enum or typed throws |
| Copying or reuse after consumption | Scoped operation first; verified ownership types only when lifetime is the invariant |
| Fixed-size storage | Tuple or small domain struct until measurement and availability justify a specialized layout |

A comment, `typealias`, naming convention, boolean permission, `RawRepresentable`, or freely conformable marker protocol documents intent without enforcing it.

Use [the decision guide](references/decision-guide.md) for the Swift pattern matrix and rollback criteria. Read only the focused representation reference needed by the change:

- [Algebraic and refined values](references/algebraic-and-refined-values.md) for enums, validated values, bounds, units, money, intervals, and collections.
- [Identity, typestate, and capabilities](references/identity-typestate-capabilities.md) for typed IDs, staged transitions, trust states, and authority tokens.
- [UI state, navigation, and effects](references/ui-state-navigation-and-effects.md) for SwiftUI state, forms, routes, request identity, cancellation, and restoration.
- [Advanced generics and protocols](references/advanced-generics-and-protocols.md) for same-type constraints, existentials, witnesses, packs, key paths, and macros.
- [Ownership, concurrency, and errors](references/ownership-concurrency-errors.md) for `Sendable`, actors, locks, noncopyable values, borrowing, typed throws, and cancellation.
- [Security and resource modeling](references/security-and-resource-modeling.md) for revocable authority, secrets, paths, handles, cryptographic state, and unsafe code.

## Close Swift construction and mutation

Keep validated values immutable. Expose one obvious checked constructor and keep any unavoidable unchecked path narrowly scoped, loudly named, and documented with its precondition.

Audit every route that can create or invalidate the value:

- Public, internal, synthesized, memberwise, convenience, literal, and `RawRepresentable` initializers.
- Writable properties and subscripts, reference-semantic storage, collection mutation, and derived flags.
- `Decodable`, persistence hydration, macros, reflection, and fixtures.
- Objective-C initializers, KVC/KVO, `NSCoding`, `NSCopying`, C/C++ imports, raw handles, and unsafe pointers.
- `@unchecked Sendable`, unchecked factories, `unsafeBitCast`, force casts, force unwraps, and unchecked indexes.
- Public conformances or marker types that clients can forge.

Do not use `ExpressibleByStringLiteral` when validation can fail unless a macro checks literals or an explicit trap policy governs them. Do not describe a nominal wrapper as authorization or security enforcement.

## Decode at the boundary

Keep raw, validated, and presented representations distinct:

```text
JSON / database / Objective-C / user input
        -> raw DTO or foreign shape
        -> validation and canonicalization
        -> domain type
        -> view or transport projection
```

Decode malformed external data into a raw shape, attach boundary context to failures, then call the same checked constructor used by in-memory callers. Custom `Decodable` is appropriate when wire and domain shapes coincide, but its implementation must reuse that constructor. Verify synthesized decoding before relying on private storage as a seal.

Preserve the existing keyed, unkeyed, or single-value wire shape when adding validation. A struct with synthesized keyed encoding needs a matching keyed decoder; being a one-property wrapper does not authorize switching to a scalar. Check historical payloads and round trips. Negative fixtures must be syntactically valid and reach the intended validation, rather than fail earlier in JSON parsing.

Read [boundaries and interop](references/boundaries-and-interop.md) for networking, persistence, notifications, Objective-C, C, analytics, and public resilience.

## Migrate through compiler errors

Introduce the domain type and runtime tests, then change the innermost operation to require it. Follow compiler errors outward, constructing the value at raw input boundaries. Remove or deprecate raw overloads once callers migrate. Keep compatibility and availability adapters at module boundaries rather than spreading them through core logic.

Avoid generic typestate when separate concrete types produce clearer call sites and diagnostics. Remove a type axis when it worsens build time or developer understanding without preventing a meaningful misuse.

## Verify Swift claims

Compiler checks complement runtime tests; they do not replace them. A compile-fail fixture establishes only that the recorded source snapshot, compiler, phase, and arguments reject the listed misuse with the expected diagnostic. It does not prove runtime validation, decoding behavior, availability, synchronization, interop, security, or all possible construction routes.

For valuable static guarantees, compile the real production module or the shared production sources plus a small misuse fixture. Pair every negative fixture with a valid control compiled under identical arguments. Use an emit-module pipeline when ownership checking matters; a type-check-only invocation can miss ownership-flow diagnostics. Reject an unexpected acceptance, missing or unrelated diagnostic, broken positive control, compiler crash, and timeout.

This skill includes a reusable standard-library runner:

```sh
python3 scripts/swift_compile_checks.py examples/compile-checks.json
python3 scripts/swift_compile_checks.py examples/compile-checks.json --json
```

The manifest records minimum compiler version, compiler arguments, shared support sources, paired positive controls, negative fixtures, and diagnostic markers. The report records the resolved toolchain, manifest digest, inputs, results, and limitations. A missing, unparseable, or too-old compiler is `unavailable`, never a successful proof. `scripts/check_examples.sh` retains the optional legacy skip; set `REQUIRE_SWIFTC=1` to make unavailability fail. Read [the compile-check runner contract](references/compile-check-runner.md) before creating or integrating another manifest.

Use the existing Swift testing skills for test structure and deterministic synchronization. They own runtime assertions, async readiness, completion signals, bounded waits, cancellation, and cleanup. Read [testing, migration, and review](references/testing-migration-and-review.md) for Swift-specific fixture design, serialization, availability, performance, migration, and review guidance.

## Output contract

Report, in proportion to the task:

1. The invariant and invalid Swift operations removed.
2. The compiler, language mode, SDK, deployment target, and relevant settings; mark unknowns.
3. The selected Swift representation and why it is the lightest adequate model.
4. The constructors, mutations, decoders, persistence paths, and interop routes that preserve or bypass it.
5. The migration and compatibility impact.
6. Runtime tests and compiler checks, with their exact limits.

Classify conclusions precisely:

- **Enforced:** ordinary Swift APIs cannot express the misuse within the inspected boundary.
- **Boundary-checked:** controlled runtime validation rejects it.
- **Evidence only:** tests or analysis support the claim without making the state unrepresentable.
- **Convention-only:** names, comments, or caller discipline carry the rule.
- **Bypassable:** a construction, mutation, decoding, or interop path breaks the claim.

## Checklist

- Environment and runtime lane are recorded.
- The representation removes a named invalid operation or state.
- Stored values are immutable or have one mutation authority.
- All constructors, decoders, persistence paths, macros, and bridges are audited.
- Raw input becomes trusted domain state at an explicit boundary.
- Availability gates protect later runtime symbols.
- Positive controls compile with the same settings as negative fixtures.
- Negative fixtures use production sources and reject only for declared diagnostics.
- Runtime tests cover validation, round trips, cancellation, and fallback behavior as applicable.
- Compiler and runtime evidence are reported with their limitations.
- Public compatibility, ABI, performance, and complexity costs are reviewed.

## Reference Map

Load only the reference that answers the changed Swift concern:

- [Decision guide](references/decision-guide.md): Swift pattern selection, representation strength, smells, and rollback.
- [Algebraic and refined values](references/algebraic-and-refined-values.md): enums, products, validation, bounds, units, intervals, collections, and `Codable` traps.
- [Identity, typestate, and capabilities](references/identity-typestate-capabilities.md): nominal and phantom IDs, legal transitions, builders, capability values, and trust states.
- [UI state, navigation, and effects](references/ui-state-navigation-and-effects.md): UI state, forms, effects, cancellation, routes, restoration, and observation adapters.
- [Advanced generics and protocols](references/advanced-generics-and-protocols.md): constraints, associated types, existentials, witnesses, packs, key paths, and macros.
- [Ownership, concurrency, and errors](references/ownership-concurrency-errors.md): isolation, locks, ownership, nonescapable values, strict memory safety, typed throws, and cancellation.
- [Boundaries and interop](references/boundaries-and-interop.md): networking, persistence, notifications, Objective-C/C, analytics, and resilience.
- [Security and resource modeling](references/security-and-resource-modeling.md): authority, secrets, paths, handles, cryptography, and unsafe-code audits.
- [iOS versioning](references/ios-versioning.md): current-toolchain policy, runtime availability, stable versus preview Xcode, and feature availability.
- [Testing, migration, and review](references/testing-migration-and-review.md): Swift runtime tests, compile checks, migration, performance, and review.
- [Compile-check runner](references/compile-check-runner.md): manifest schema, CLI, paths, module linkage, reports, exit statuses, and evidence limits.
- [Sources](references/sources.md): primary specifications and official release documentation for time-sensitive guidance.

## Included utilities and fixtures

- `scripts/audit_project.py`: inventories Swift/Xcode compatibility settings.
- `scripts/swift_compile_checks.py`: runs manifest-defined positive, negative, and runtime checks with human or JSON reporting.
- `examples/compile-checks.json`: declares the Swift 6.3 fixture snapshot and compiler inputs.
- `scripts/check_examples.sh`: compatibility entry point with optional skip and `REQUIRE_SWIFTC=1` behavior.
- `scripts/validate_skill.py`: validates metadata, links, evals, manifest wiring, and fixtures.
- `examples/CorePatterns.swift`, `CurrentSwiftPatterns.swift`, and `TrustStatePatterns.swift`: shared sources used by controls and misuse fixtures.
- `examples/CorePatternsRuntimeChecks.swift`: executable validation and `Codable` checks.
- `examples/CompilePass*.swift` and `CompileFail*.swift`: paired valid and invalid uses of the shared sources.
- `evals/trigger-evals.json` and `evals/quality-evals.md`: activation and response-quality scenarios.

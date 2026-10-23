---
name: modeling-swift-types-for-correctness
description: "Model Swift invariants, validated decoding, legal transitions, ownership, and generic relationships. Load before assessing or changing enforcement boundaries; not ordinary output tests or naming."
---

# Modeling Swift Types for Correctness

Use Swift’s type system to remove invalid operations and state combinations from ordinary code paths. Prefer the lightest representation that produces a useful diagnostic at the misuse site.

This skill owns Swift representation and its enforcement: construction, decoding, interop, ownership, and compiler evidence. The concurrency skill owns scheduling, isolation repair, and task lifecycle; the shared feature-status reference owns dated support and availability facts. First distinguish a representation or enforcement claim from ordinary function behavior: testing a function's outputs, even with negative or boundary inputs, does not itself call for type modeling or invariant verification. Keep that work with the testing or defect-review skill.

For a representation claim or a change to an enforcement boundary, invoke `verifying-invariants` if installed and not already active. Apply its procedure alongside the Swift rules here, including for a small initializer or decoding fix with a settled predicate. When Universal is absent, use this skill's Swift checklist and report the assessment's limits.

Swift cannot prove arbitrary facts about runtime input before validation. Refine untrusted input at a boundary, then pass the refined value inward. A validating initializer proves nothing if another initializer, decoder, mutation, or bridge bypasses it.

## Establish the Swift environment

Inspect the environment when compiler behavior, availability, isolation, or ownership affects the claim. For a supplied snippet without a project, state unknown settings briefly and assess its shown boundaries. Do not infer language features from the deployment target:

1. Record minimum deployment versions and SDK.
2. Record the selected Xcode channel and `xcrun swift --version`.
3. Record the actual Swift language mode for every affected target; do not silently migrate it.
4. Record strict concurrency, default isolation, upcoming features, experimental features, strict memory safety, and library evolution.
5. Identify app, package, binary framework, and Objective-C or C boundaries.

Resolve all bundled script, fixture, and reference paths relative to this skill directory; run project commands from the consumer repository.

Run `python3 scripts/audit_project.py <project-root>` for a heuristic inventory, then verify target-specific Xcode settings. The bundled compiler fixtures use Swift 6 language mode. Assess production code under its actual supported settings; a different language mode is a verification limit, not permission to migrate.

Preserve the project’s actual runtime lane. The following iOS 16 examples illustrate compatibility choices, not a mandatory deployment minimum:

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

Before assessing or recommending a representation, read the focused reference for the claim, even for a read-only design sketch. The skill body does not replace these construction rules and proof limits:

- Validated decoding: [algebraic and refined values](references/algebraic-and-refined-values.md#codable-and-refined-types).
- Recoverable state transitions: [domain modeling recipes](references/domain-modeling-recipes.md#flow).
- Correlated types: [preserve generic relationships](references/generic-proof-recipes.md#gen).
- Typed expression results: [explicit proof evidence](references/generic-proof-recipes.md#adv).
- Static dimensions: [sizes and packs](references/generic-proof-recipes.md#sizes-packs).
- Borrowed views and lifetimes: read the complete [ownership section](references/ownership-effect-recipes.md#ownership).
- Typed failures across concurrency: [error transport](references/ownership-effect-recipes.md#effects).
- Required completion or cleanup: [abandonment and recovery](references/ownership-effect-recipes.md#resources).

For other concerns, use the Reference Map; use [the decision guide](references/decision-guide.md) when pattern selection remains open. Load only relevant sections and consult feature status only for mechanisms that depend on recent support.

## Close Swift construction and mutation

Keep validated values immutable. Expose one obvious checked constructor and keep any unavoidable unchecked path narrowly scoped, loudly named, and documented with its precondition.

Audit every route that can create or invalidate the value:

- Public, internal, synthesized, memberwise, convenience, literal, and `RawRepresentable` initializers.
- Writable properties and subscripts, reference-semantic storage, collection mutation, and derived flags.
- `Decodable`, persistence hydration, macros, reflection, and fixtures.
- Objective-C initializers, KVC/KVO, `NSCoding`, `NSCopying`, C/C++ imports, raw handles, and unsafe pointers.
- `@unchecked Sendable`, unchecked factories, `unsafeBitCast`, force casts, force unwraps, and unchecked indexes.
- Public conformances or marker types that clients can forge.

Confirm synthesis before alleging a bypass: a struct's custom initializer in its primary body suppresses memberwise synthesis; one in an extension does not. Visible `let` storage is still immutable. Neither fact seals synthesized decoding. Synthesized `Encodable` does not rerun the validating initializer; an invalid decoded instance can therefore be encoded again. Check saving claims against values admitted by every construction path.

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

Before suggesting or changing a decoder, read [the keyed decoding example](references/algebraic-and-refined-values.md#codable-and-refined-types) and establish the existing wire contract:

- Inspect the encoder or a historical payload for its container kind and keys. Preserve that keyed, unkeyed, or single-value shape. For synthesized encoding of `value: Int`, decode through `decoder.container(keyedBy: CodingKeys.self)` and `decode(Int.self, forKey: .value)`. A `singleValueContainer()` would change that wire contract.
- Decode a fixed valid historical payload independently of the current encoder. This establishes compatibility with already saved data.
- Test syntactically valid invalid payloads that reach the predicate, and a valid encode/decode round trip. The round trip checks agreement between the current encoder and decoder; it cannot replace the historical control.

Run the checks when execution is in scope. Keep one record for each of the three controls, with its observed evidence and result or its pending status, including in a read-only assessment. Derive any summary of what ran from those records. A round trip can pass while the defect exists and still belongs in the repair's regression checks: it guards encoder/decoder agreement. Keep it distinct from the historical payload control.

Describe a decoder repair with its container and keys as well as its validation path. If showing concrete decoder code, compile that exact proposal with the unchanged encoder and run the three controls when execution is available. Use the applicable project checks, or isolated scratch code for read-only work; existing equivalent checks suffice. This catches incompatible container APIs as well as schema changes. If execution is unavailable, distinguish the proposed implementation from a checked repair.

For scratch compiler checks, keep allocation, cleanup registration, compilation, and execution in one tool command, outside the project. Use a scoped temporary-directory API or register an exit trap immediately after allocation; see [scratch compiler checks](references/compile-check-runner.md#scratch-compiler-checks). Cleanup must cover failure too. Report runs, changes, and cleanup only when completed tool results confirm them.

Read [boundaries and interop](references/boundaries-and-interop.md) for networking, persistence, notifications, Objective-C, C, analytics, and public resilience.

## Migrate through compiler errors

Introduce the domain type and runtime tests, then change the innermost operation to require it. Follow compiler errors outward, constructing the value at raw input boundaries. Remove or deprecate raw overloads once callers migrate. Keep compatibility and availability adapters at module boundaries rather than spreading them through core logic.

Avoid generic typestate when separate concrete types produce clearer call sites and diagnostics. Remove a type axis when it worsens build time or developer understanding without preventing a meaningful misuse.

## Verify Swift claims

Compiler checks complement runtime tests; they do not replace them. A compile-fail fixture establishes only that the recorded source snapshot, compiler, phase, and arguments reject the listed misuse with the expected diagnostic. It does not prove runtime validation, decoding behavior, availability, synchronization, interop, security, or all possible construction routes.

For valuable static guarantees, compile the real production module or the shared production sources plus a small misuse fixture. Pair every negative fixture with a valid control using the same compiler phase and shared compiler arguments; fixture sources and output paths may differ. Record each side’s effective phase and arguments, and derive the report from those records. After changing the phase or shared arguments, rerun the positive control. If the controls differ, report the difference and the missing pairing instead of describing the invocations as identical. Use an emit-module pipeline when ownership checking matters; a type-check-only invocation can miss ownership-flow diagnostics. Reject an unexpected acceptance, missing or unrelated diagnostic, broken positive control, compiler crash, and timeout.

This skill includes a reusable standard-library runner:

```sh
python3 scripts/swift_compile_checks.py examples/compile-checks.json
python3 scripts/swift_compile_checks.py examples/compile-checks.json --json
```

The manifest records minimum compiler version, compiler arguments, shared support sources, paired positive controls, negative fixtures, and diagnostic markers. The report records the resolved toolchain, manifest digest, inputs, results, and limitations. A missing, unparseable, or too-old compiler is `unavailable`, never a successful proof. `scripts/check_examples.sh` retains the optional legacy skip; set `REQUIRE_SWIFTC=1` to make unavailability fail. Read [the compile-check runner contract](references/compile-check-runner.md) before creating or integrating another manifest.

Use the existing Swift testing skills for test structure and deterministic synchronization. They own runtime assertions, async readiness, completion signals, bounded waits, cancellation, and cleanup. Read [testing, migration, and review](references/testing-migration-and-review.md) for Swift-specific fixture design, serialization, availability, performance, migration, and review guidance.

## Output contract

For a verification-only request, report the boundaries, counterexamples, checks, and limits. Include replacement code or a migration design only when the user asks for repair or implementation advice.

Report, in proportion to the task:

1. The invariant and invalid Swift operations removed.
2. The compiler, language mode, SDK, deployment target, and relevant settings; mark unknowns.
3. The selected Swift representation and why it is the lightest adequate model.
4. The constructors, mutations, decoders, persistence paths, and interop routes that preserve or bypass it.
5. The migration and compatibility impact.
6. Concrete valid-use, misuse, and runtime scenarios for the selected guarantee, including recovery or cancellation where relevant. Mark each check run or pending and state its limit; a list of obligations alone is not an evidence plan.

Classify conclusions precisely:

- **Enforced:** ordinary Swift APIs cannot express the misuse within the inspected boundary.
- **Boundary-checked:** controlled runtime validation rejects it.
- **Evidence only:** tests or analysis support the claim without making the state unrepresentable.
- **Convention-only:** names, comments, or caller discipline carry the rule.
- **Bypassable:** a construction, mutation, decoding, or interop path breaks the claim.

## Checklist

Before returning an invariant assessment or enforcement-boundary change, confirm that `verifying-invariants` has been loaded when installed. If it was skipped, load it and reconcile the evidence and conclusion before finishing. Use the standalone checklist below when it is unavailable.

- Environment and runtime lane are recorded.
- The representation removes a named invalid operation or state.
- Stored values are immutable or have one mutation authority.
- Each claimed constructor, decoder, persistence path, macro, or bridge is tied to its inspected implementation; a synthesized-`Decodable` result transfers only to paths shown to invoke that decoder. Uninspected paths remain explicit limits.
- Raw input becomes trusted domain state at an explicit boundary.
- Availability gates protect later runtime symbols.
- Positive controls compile with the same settings as negative fixtures.
- Negative fixtures use production sources and reject only for declared diagnostics.
- Runtime tests cover validation, round trips, cancellation, and fallback behavior as applicable.
- For persisted values, the report accounts separately for fixed historical payloads, predicate-reaching invalid payloads, and current round trips, including relevant checks run during the assessment.
- Compiler and runtime evidence are reported with their limitations.
- Public compatibility, ABI, performance, and complexity costs are reviewed.

## Reference Map

Load the owner of the changed concern. Mechanism guides explain construction and language rules; recipes apply those rules to compound invariants. Follow their conditional links only when that supporting detail is needed:

- [Decision guide](references/decision-guide.md): Swift pattern selection, representation strength, smells, and rollback.
- [Algebraic and refined values](references/algebraic-and-refined-values.md): construction mechanics for sums, products, validated values, structural collections, and compatible decoding.
- [Identity, typestate, and capabilities](references/identity-typestate-capabilities.md): nominal and phantom IDs, legal transitions, builders, capability values, and trust states.
- [UI state, navigation, and effects](references/ui-state-navigation-and-effects.md): UI state, forms, effects, cancellation, routes, restoration, and observation adapters.
- [Advanced generics and protocols](references/advanced-generics-and-protocols.md): language mechanics for constraints, protocols, abstraction, packs, key paths, and generated APIs.
- [Ownership, concurrency, and errors](references/ownership-concurrency-errors.md): language mechanics for ownership operations, isolation boundaries, strict memory safety, and typed throws.
- [Boundaries and interop](references/boundaries-and-interop.md): networking, persistence, notifications, Objective-C/C, analytics, and resilience.
- [Security and resource modeling](references/security-and-resource-modeling.md): authority, secrets, paths, handles, cryptography, and unsafe-code audits.
- [iOS versioning](references/ios-versioning.md): deployment policy, availability gates, adapters, and stable versus preview build lanes.
- [Testing, migration, and review](references/testing-migration-and-review.md): Swift runtime tests, compile checks, migration, performance, and review.
- [Compile-check runner](references/compile-check-runner.md): manifest schema, CLI, paths, module linkage, reports, exit statuses, and evidence limits.
- [Domain modeling recipes](references/domain-modeling-recipes.md): compound domain policy, relationships, recovering workflows, applied boundaries, and public contracts.
- [Generic proof recipes](references/generic-proof-recipes.md): preserving correlations, static sizes, typed DSLs, equality witnesses, higher-rank encodings, and restricted proof structures.
- [Ownership and effect recipes](references/ownership-effect-recipes.md): borrowed projections, isolation, error transport, completion obligations, and binary representations.
- [Feature status and frontier](references/swift-feature-status.md): the dated support and availability authority, experiment flags, evidence limits, and unavailable encodings.
- [Sources](references/sources.md): primary specifications and official release documentation for time-sensitive guidance.

For bundled scripts, fixture sources, and activation/quality evals, see the [utility inventory](references/compile-check-runner.md#included-utilities-and-fixtures).

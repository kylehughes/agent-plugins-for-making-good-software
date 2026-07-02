---
name: simplifying-code
description: Universally reviews and simplifies existing code while preserving behavior. Use when the user asks to simplify, clean up, harden, reduce, reuse, recycle, de-duplicate, refactor locally, or review a code diff in any language or platform. This skill is platform-neutral; when a platform-specific companion skill is available for the target stack, compose with it rather than embedding platform rules here.
---

# Simplify Code

Run this skill as a disciplined, behavior-preserving cleanup and hardening pass over code that already exists or has just been written. The goal is smaller, clearer, safer, more idiomatic, more reusable, and more maintainable code.

This is not a rewrite license. Prefer deletion, reuse, narrower boundaries, and targeted fixes over new architecture. Expand scope only when the current change cannot be simplified safely without touching adjacent code.

## Non-Negotiable Contract

1. Preserve intended behavior, public API, persistence formats, wire formats, analytics names, localization keys, accessibility semantics, migrations, deployment targets, security boundaries, and observable UI behavior unless the user explicitly asked to change them.
2. Treat repository conventions and project configuration as the source of truth. Read nearby code and manifests before changing style, architecture, formatting, tests, or build settings.
3. Use the local toolchain and declared project settings. Do not hard-code assumptions about language versions, SDKs, frameworks, package managers, runtime versions, or CI commands.
4. Search before adding or keeping code. A simplification pass should not leave a duplicate helper, component, formatter, wrapper, service, mock, fixture, utility, compatibility shim, or mini-framework when an existing primitive fits.
5. Keep fixes local and reviewable. Avoid mass formatting, broad renames, dependency churn, file moves, generated-file edits, and architectural migrations unless they remove concrete duplication or fix a concrete defect in the reviewed surface.
6. Never discard user work with destructive git or filesystem operations. Do not run `git reset`, `git checkout --`, `git clean`, force pushes, recursive deletes, or equivalent operations unless the user specifically requested that operation.
7. Verify with the cheapest relevant command that proves the touched code still builds or behaves correctly. If verification cannot be run, report the exact blocker.
8. Be honest about uncertainty. Do not claim tests passed, commands ran, files changed, or behavior was preserved unless that is grounded in actual inspection or execution.

## Platform-Specific Companion Skills

This skill is deliberately universal. It should not contain detailed rules for any single platform or framework.

At the start of the task, infer the target stack from file extensions, manifests, project files, imports, package managers, test files, and the user's wording. If a more specific skill is available for that stack, compose with it:

1. Use this skill to establish the review surface, behavior-preservation contract, reuse/deletion pass, and verification discipline.
2. Use the platform-specific skill as an additional checklist for availability, lifecycle, concurrency, UI, framework, build-system, and compatibility hazards.
3. If the universal checklist and the platform-specific checklist conflict, the more specific rule wins for that platform.
4. Do not copy platform-specific rules into this skill. Keep this skill neutral so it remains valid across languages and ecosystems.
5. If no platform-specific skill is available, infer the analogous checks from the language, runtime, dependency manager, concurrency model, test runner, framework lifecycle, and compatibility mechanism.

Examples of companion-skill areas include mobile platforms, web frameworks, backend runtimes, data systems, game engines, embedded systems, infrastructure-as-code, and security-sensitive domains.

## Workflow

### 1. Identify and Freeze the Review Surface

Start by identifying the code that should be reviewed. Use the same baseline surface for all review passes so findings are not biased by later edits.

Run when available:

```sh
git status --short
git diff --stat
git diff --name-status
```

Then choose the surface:

- If staged or unstaged tracked changes exist, review `git diff HEAD` so staged and unstaged edits are considered together.
- If only unstaged tracked changes exist, `git diff` is acceptable, but still note the changed file list from `git status --short`.
- If untracked source files exist, inspect them explicitly with `git ls-files --others --exclude-standard`; ordinary diffs will not show them.
- If the repository is not a git repository, review the files the user mentioned, files you edited earlier, and the most recently modified relevant source files.
- If there are merge conflicts, stop broad cleanup and only simplify conflict-resolution code unless the user explicitly asked for a larger pass.
- If a file is generated, vendored, minified, binary, huge, or build output, do not hand-edit it. Inspect only enough to identify the relevant hand-written source.

Freeze the initial file list before editing. Expand the surface only for a concrete reason: deleting a duplicated helper, updating necessary call sites, moving a fallback into an existing compatibility layer, or fixing a compile/test error introduced by the cleanup.

### 2. Recon the Repository Before Judging the Diff

Inspect enough context to avoid cargo-cult fixes:

- Project manifests, workspace/project files, package files, lockfiles, module manifests, build settings, language settings, runtime/deployment targets, lint/format configs, test configs, CI scripts, and code-generation config.
- Nearby code: adjacent types, helpers, services, components, reducers/stores, data adapters, fixtures, mock builders, design tokens, environment/dependency wrappers, compatibility shims, and error/logging primitives.
- Ownership boundaries: package/module visibility, public/internal/private API, generated-code boundaries, vendored dependencies, test-only support code, and platform-specific directories.
- Existing commands: README, CONTRIBUTING, Makefile, Justfile, Taskfile, package scripts, CI config, or project-specific docs.

Do not apply a rule merely because it is common elsewhere. Match the host codebase unless the local convention is actively causing the problem being fixed.

### 3. Build an Intent Map

Before editing, identify the contracts the changed code appears to rely on:

- Inputs, outputs, errors, fallback behavior, validation, retries, cancellation, cleanup, resource lifetime, ordering, timing, identity, equality, hashing, pagination, precision, rounding, locale, timezone, encoding, caching, and persistence behavior.
- Public API, ABI, serialization, schema, migration, feature-flag, analytics, logging, accessibility, localization, and configuration boundaries.
- Runtime compatibility: declared minimum runtime, supported platforms, package version ranges, framework availability, database versions, browser/runtime support, or deployment environments.

Use this map to distinguish safe simplification from behavior change.

### 4. Run Independent Review Passes

Run these passes independently. If the environment supports parallel reviewers or subagents, give each the full frozen surface and ask for separate findings. Otherwise, perform the passes yourself and keep findings separated until all passes are complete.

#### Pass A: Behavior, Compatibility, and Correctness

Find changes that simplify incorrectly or silently alter contracts:

1. Removed branches, fallbacks, nil/null handling, error handling, default values, retries, cancellation, cleanup, validation, permission checks, or guardrails.
2. Changed ordering, identity, equality, hashing, sorting, stable IDs, pagination, locale, timezone, encoding, precision, rounding, caching, idempotency, transaction, persistence, or request semantics.
3. Public API changes, serialization changes, migration changes, feature-flag changes, analytics/event-name changes, localization-key changes, accessibility-identifier changes, test fixture changes, or configuration changes that affect callers.
4. Compatibility hazards: new APIs used without required guards, compile-time checks confused with runtime checks, framework/module checks confused with version checks, removed support for declared minimum versions, or beta/experimental APIs used without isolation.
5. Error handling that became too broad, too narrow, swallowed, double-reported, retried unsafely, or lost useful diagnostics.
6. Data-integrity issues: partial writes, missing transactions, non-atomic updates, lost deduplication, unstable sort orders, race-prone existence checks, or changed conflict resolution.

Fix correctness and compatibility defects before aesthetic cleanup.

#### Pass B: Reuse, Deletion, and Consolidation

Look for code that should not exist because the project already has a better primitive:

1. New utilities, helpers, formatters, validators, adapters, clients, wrappers, extensions, components, hooks, reducers, stores, mocks, fixtures, or test builders that duplicate existing functionality.
2. Inline logic that should use existing abstractions: URL/path handling, date/time formatting, currency/number formatting, localization, logging, analytics, error mapping, networking, decoding, persistence, dependency injection, feature flags, environment checks, styles, permissions, or compatibility wrappers.
3. Copy-paste with small variations. Extract a helper only when the shared concept is real and the resulting call sites are clearer.
4. Dead code, unused parameters, unused imports, unused state, unused tests, unreachable branches, redundant adapters, and wrappers that add no behavior, lifecycle, identity, layout, styling, test seam, or accessibility value.
5. Custom code that can be replaced by a standard-library, framework, or already-approved project API without losing clarity, behavior, or compatibility.

Delete more than you add. Do not create a new abstraction just to satisfy DRY when two explicit call sites are clearer.

#### Pass C: Shape, Boundaries, and Cognitive Load

Find code that makes the system harder to reason about:

1. Redundant state: stored values that duplicate derived state, cached values without invalidation, observers/effects where a direct call or derived property is enough, or model mirrors that can drift.
2. Parameter sprawl: long parameter lists, boolean flags that encode multiple modes, optional clusters, weakly related arguments, or new parameters added where an existing domain type, configuration, command, or result type already exists.
3. Leaky abstractions: UI knowing service internals, services knowing UI concerns, packages exposing internals, tests depending on private implementation details, persistence/networking concepts bleeding into domain models without purpose, or domain logic hidden in view/render code.
4. Stringly typed code: raw strings, magic numbers, ad hoc identifiers, untyped dictionaries/maps, or implicit conventions where existing constants, enums, typed identifiers, option sets, value types, or design tokens should be used.
5. Control-flow noise: deeply nested branches, negative condition pyramids, unnecessary temporary variables, avoidable callbacks, over-eager genericity, unnecessary type erasure, and comments explaining obvious code.
6. Naming drift: names that describe implementation instead of intent, names inconsistent with adjacent code, and names that obscure units, ownership, lifetime, isolation, side effects, or failure behavior.

Prefer code that makes invalid states unrepresentable, but do not broaden scope just to model every theoretical state.

#### Pass D: Concurrency, Lifecycle, and Resource Ownership

Find simplifications that create leaks, races, stuck work, or lifetime bugs:

1. Work launched without ownership, cancellation, timeout, parent scope, or lifecycle binding.
2. Shared mutable state accessed from multiple threads, actors, event loops, tasks, goroutines, fibers, workers, callbacks, or request contexts without the project's normal isolation mechanism.
3. Subscriptions, observers, streams, file handles, sockets, timers, processes, tasks, locks, transactions, database sessions, or temporary resources that are not cleaned up.
4. UI lifecycle effects moved into render/body paths, constructors, or callbacks that can run repeatedly.
5. Background work that captures UI, request, session, transaction, or context objects beyond their valid lifetime.
6. Fire-and-forget work that hides errors or keeps running after callers are gone.
7. Blocking operations moved onto latency-sensitive threads, event loops, UI threads, request handlers, or hot render paths.
8. Locking or synchronization that can deadlock, invert priority, block cancellation, or violate actor/event-loop confinement.

Do not silence concurrency warnings by erasing isolation, broadening mutability, or adding unsafe annotations unless the invariant is actually true and documented.

#### Pass E: Security, Privacy, and Trust Boundaries

Find changes that weaken safety:

1. Secrets, tokens, credentials, session IDs, authorization headers, personally identifiable data, health/financial data, user content, or internal identifiers logged or exposed.
2. Authorization, authentication, permission, entitlement, rate-limit, CSRF, validation, escaping, sanitization, or origin checks weakened or removed.
3. Paths, URLs, SQL, shell commands, regular expressions, HTML, XML, JSON, templates, or file names assembled unsafely from untrusted input.
4. Cryptography, hashing, token generation, randomness, key storage, certificate validation, or signature checks replaced with simpler but weaker logic.
5. Dependencies, plugins, build scripts, generated code, or external tools introduced without need.
6. Error responses or logs that disclose internals not previously disclosed.

Prefer existing security wrappers and policy gates. Do not invent local security mechanisms during a cleanup pass.

#### Pass F: Performance, Memory, and Scalability

Find obvious waste without premature optimization:

1. Repeated expensive computation, parsing, reflection, serialization, database queries, network requests, filesystem scans, regular expression compilation, image/media work, or excessive logging.
2. Hot-path bloat in startup, request handling, per-render paths, scrolling, layout, animation, reducers, serialization, validation, parsing, or frequently repeated callbacks.
3. Full collection/file loads where a targeted query, stream, lazy sequence, pagination, index, cache, or early exit is enough.
4. Unnecessary existence checks before resource operations when direct operation plus error handling avoids time-of-check/time-of-use races.
5. Unbounded collections, caches, queues, task groups, retry loops, recursion, listeners, or memory growth.
6. Avoidable allocation churn: recreating formatters, regexes, encoders/decoders, clients, observers, attributed strings, images, layout objects, style objects, or heavyweight services in hot paths.
7. N+1 query patterns, nested loops over large collections, repeated sorting/filtering, or conversions back and forth between equivalent representations.

Measure when the performance tradeoff is non-obvious. For obvious waste, fix locally.

#### Pass G: Tests, Observability, and Failure Modes

Check whether simplified code remains testable and diagnosable:

1. Tests that overfit implementation details or duplicate production logic instead of asserting behavior.
2. Missing targeted regression tests for bug fixes, compatibility fallbacks, parsing/formatting edge cases, concurrency races, cancellation, permissions, migrations, and boundary cases.
3. Test helpers or mocks duplicated across files instead of using existing fixtures/builders.
4. Debug prints, temporary logs, screenshots, sleeps, arbitrary timeouts, disabled assertions, skipped tests, fragile snapshots, and brittle wall-clock assumptions.
5. Errors that lose context needed for support, logging, telemetry, or debugging.
6. Observability changes that alter event names, cardinality, privacy level, sampling, or support workflows.

Do not add a large test suite during a cleanup pass unless the change is risky or the bug is subtle. Prefer one targeted regression test over broad snapshot churn.

### 5. Classify Findings Before Editing

Classify findings before changing code:

- **Must fix:** compile errors, behavior regressions, compatibility defects, data races, leaks, security/privacy issues, broken tests, invalid migrations, and clear duplicate code that can be removed safely.
- **Should fix:** redundant state, unnecessary wrappers, parameter sprawl, obvious inefficiencies, unclear names, avoidable branching, duplicated fixtures/helpers, and local boundary leaks.
- **May skip:** subjective style differences, churn-heavy refactors, speculative abstractions, low-risk duplication that is clearer as-is, changes requiring product decisions, and improvements outside the frozen surface.

For each skipped real finding, keep a short note explaining why it was not changed. Do not mention speculative findings that proved false unless the user needs to know.

### 6. Apply Safe Fixes

When editing:

1. Work in small patches. After each meaningful patch, reassess whether the code got smaller and clearer.
2. Preserve the smallest stable API. Tighten visibility where safe, but do not break public, cross-module, serialized, persisted, reflected, plugin, or external callers.
3. Remove unused code, imports, dependencies, mocks, fixtures, test data, and configuration after consolidation.
4. Keep comments only for non-obvious why: invariants, constraints, compatibility traps, security decisions, performance tradeoffs, and workarounds with a reason. Delete comments that narrate the task or restate the code.
5. Do not introduce dependencies, global mutable state, build settings, formatters, linters, macros, code generation, architectural layers, or background services unless the repository already uses them and the change has a concrete payoff.
6. Avoid mass formatting. Format only touched code unless the user asked for a formatting pass or the repo's formatter can target the changed files.
7. Keep generated files generated. If generated output must change, update the source generator or state that regeneration is required.
8. Re-run `git diff --check` or the repository equivalent before final verification when practical.

### 7. Verify

Choose verification based on the touched files and repository conventions. Prefer documented commands over guesses.

General order:

1. Fast static checks for the touched language or package.
2. Targeted unit tests for changed behavior.
3. Package/module build.
4. App/integration build or CI-equivalent command when the change crosses module boundaries or platform availability.
5. Formatter/linter only when configured by the repository or requested by the user.

If no command is obvious, inspect project files to discover one. If discovery is expensive or ambiguous, run the narrowest safe build/test command and report the limitation.

Include the command and result in the final response. If a command fails for an unrelated pre-existing reason, report that separately from issues introduced by the cleanup.

## Universal Adaptation Rules

Apply the same simplification principles in every language:

- Prefer language idioms and existing project patterns over personal taste.
- Prefer standard data structures, standard libraries, and approved framework primitives over custom helpers.
- Preserve type safety. Do not simplify by erasing types, weakening nullability, broadening exceptions/errors, using dynamic casts unnecessarily, or collapsing domain models into dictionaries/maps.
- Preserve resource ownership. Use the language's normal lifecycle primitives: RAII, `defer`, context managers, `using` blocks, scopes, cancellation tokens, subscriptions, disposables, or destructors as appropriate.
- Preserve concurrency semantics. Do not move work between threads, actors, event loops, queues, executors, request contexts, or processes without a reason and a verification path.
- Preserve compatibility with the declared runtime, SDK, language mode, ABI, database schema, browser/runtime support, package constraints, and deployment target.
- Prefer targeted compatibility shims over scattered version checks.
- Treat UI code as behavior. Layout, focus, animation, accessibility, localization, dynamic type, keyboard behavior, gesture priority, identity, state restoration, scroll position, and rendering performance are observable behavior.
- Treat tests as product code. Simplify them by improving fixtures, reducing duplication, and asserting behavior, not by weakening coverage.
- Treat configuration as code. Build files, manifests, feature flags, environment variables, deployment settings, policy files, and generated-code inputs can carry behavior and compatibility contracts.

## Common Anti-Simplifications

Reject changes that look simpler but are weaker:

- Replacing a domain type with a primitive because there is only one field today.
- Removing a fallback because the current development machine or SDK does not need it.
- Flattening an error type into a string and losing retry/support/telemetry semantics.
- Replacing project-specific localization, logging, analytics, networking, persistence, or dependency wrappers with direct framework calls that bypass policy.
- Moving work into constructors, render methods, global initializers, module load, or static initialization where lifetime and failure become harder to control.
- Converting structured async work into fire-and-forget work.
- Silencing type, nullability, lint, or concurrency warnings by weakening the type system.
- Deleting tests because they are verbose instead of simplifying their fixtures.
- Adding a broad abstraction because two call sites share a few lines.
- Mass-formatting or renaming files as part of a behavior cleanup.

## File-Type-Specific Attention

Use these prompts when the review surface contains the corresponding files:

- **Public interfaces:** preserve source/binary compatibility, documented behavior, defaults, error contracts, nullability, availability, visibility, annotations, and overload resolution.
- **Serialization and schemas:** preserve field names, optionality, defaulting, migrations, ordering guarantees, version tolerance, and backwards compatibility.
- **Persistence/data access:** preserve transactions, indexes, predicates, sort order, pagination, isolation, conflict behavior, nullability, and migration paths.
- **UI components:** preserve state identity, accessibility, localization, focus, input behavior, animation, layout, sizing, scrolling, theming, and lifecycle side effects.
- **Network/API clients:** preserve URL construction, query encoding, headers, auth, status handling, retries, cancellation, timeouts, caching, pagination, and error mapping.
- **Background jobs/workers:** preserve idempotency, retry policy, locking, scheduling, deduplication, rate limits, timeout, and cancellation.
- **Configuration/build files:** preserve environment behavior, package resolution, generated-code inputs, target membership, deployment settings, feature flags, and CI parity.
- **Tests:** preserve behavioral assertions, fixture intent, regression coverage, and determinism while deleting duplicate setup and brittle implementation coupling.

## Final Response Format

Finish with a concise summary:

1. What changed, grouped by behavior/reuse/quality/performance when useful.
2. Verification commands run and their results.
3. Any real findings intentionally skipped or deferred, with a brief reason.
4. Any verification not run, with the concrete blocker.

If no fixes were needed, say the reviewed surface was already clean and list the verification performed. Do not invent changes, tests, or results.

## Compact Checklist

Before finalizing, confirm:

- The review surface included staged, unstaged, and relevant untracked files.
- Existing utilities and adjacent patterns were searched before keeping new code.
- Behavior, compatibility, public API, persistence, localization, accessibility, analytics, and security semantics were preserved.
- Redundant state, duplicate logic, wrapper code, unused imports, dead code, no-op updates, and hot-path waste were removed where safe.
- Concurrency, lifecycle, cancellation, resource ownership, and cleanup remain correct.
- Platform compatibility checks are precise and fallbacks remain for declared minimum versions.
- Generated/vendor/build artifacts were not hand-edited.
- The cheapest relevant verification was run or a specific blocker was reported.

# Review Passes

Apply the passes selected in the skill’s workflow to the same frozen surface. These prompts guide investigation; they do not presume defects or authorize edits outside scope.

## Pass A: Behavior, Compatibility, and Correctness

Find changes that simplify incorrectly or silently alter contracts:

1. Removed branches, fallbacks, nil/null handling, error handling, default values, retries, cancellation, cleanup, validation, permission checks, or guardrails.
2. Changed ordering, identity, equality, hashing, sorting, stable IDs, pagination, locale, timezone, encoding, precision, rounding, caching, idempotency, transaction, persistence, or request semantics.
3. Public API changes, serialization changes, migration changes, feature-flag changes, analytics/event-name changes, localization-key changes, accessibility-identifier changes, test fixture changes, or configuration changes that affect callers.
4. Compatibility hazards: new APIs used without required guards, compile-time checks confused with runtime checks, framework/module checks confused with version checks, removed support for declared minimum versions, or beta/experimental APIs used without isolation.
5. Error handling that became too broad, too narrow, swallowed, double-reported, retried unsafely, or lost useful diagnostics.
6. Data-integrity issues: partial writes, missing transactions, non-atomic updates, lost deduplication, unstable sort orders, race-prone existence checks, or changed conflict resolution.

Fix correctness and compatibility defects before aesthetic cleanup.

## Pass B: Reuse, Deletion, and Consolidation

Look for code that should not exist because the project already has a better primitive:

1. New utilities, helpers, formatters, validators, adapters, clients, wrappers, extensions, components, hooks, reducers, stores, mocks, fixtures, or test builders that duplicate existing functionality.
2. Inline logic that should use existing abstractions: URL/path handling, date/time formatting, currency/number formatting, localization, logging, analytics, error mapping, networking, decoding, persistence, dependency injection, feature flags, environment checks, styles, permissions, or compatibility wrappers.
3. Copy-paste with small variations. Extract a helper only when the shared concept is real and the resulting call sites are clearer.
4. Dead code, unused parameters, unused imports, unused state, unused tests, unreachable branches, redundant adapters, and wrappers that add no behavior, lifecycle, identity, layout, styling, test seam, or accessibility value.
5. Custom code that can be replaced by a standard-library, framework, or already-approved project API without losing clarity, behavior, or compatibility.

Delete more than you add. Do not create a new abstraction just to satisfy DRY when two explicit call sites are clearer.

## Pass C: Shape, Boundaries, and Cognitive Load

Find code that makes the system harder to reason about:

1. Redundant state: stored values that duplicate derived state, cached values without invalidation, observers/effects where a direct call or derived property is enough, or model mirrors that can drift.
2. Parameter sprawl: long parameter lists, boolean flags that encode multiple modes, optional clusters, weakly related arguments, or new parameters added where an existing domain type, configuration, command, or result type already exists.
3. Leaky abstractions: UI knowing service internals, services knowing UI concerns, packages exposing internals, tests depending on private implementation details, persistence/networking concepts bleeding into domain models without purpose, or domain logic hidden in view/render code.
4. Stringly typed code: raw strings, magic numbers, ad hoc identifiers, untyped dictionaries/maps, or implicit conventions where existing constants, enums, typed identifiers, option sets, value types, or design tokens should be used.
5. Control-flow noise: deeply nested branches, negative condition pyramids, unnecessary temporary variables, avoidable callbacks, over-eager genericity, unnecessary type erasure, and comments explaining obvious code.
6. Naming drift: names that describe implementation instead of intent, names inconsistent with adjacent code, and names that obscure units, ownership, lifetime, isolation, side effects, or failure behavior.

Prefer code that makes invalid states unrepresentable, but do not broaden scope just to model every theoretical state.

## Pass D: Concurrency, Lifecycle, and Resource Ownership

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

## Pass E: Security, Privacy, and Trust Boundaries

Find changes that weaken safety:

1. Secrets, tokens, credentials, session IDs, authorization headers, personally identifiable data, health/financial data, user content, or internal identifiers logged or exposed.
2. Authorization, authentication, permission, entitlement, rate-limit, CSRF, validation, escaping, sanitization, or origin checks weakened or removed.
3. Paths, URLs, SQL, shell commands, regular expressions, HTML, XML, JSON, templates, or file names assembled unsafely from untrusted input.
4. Cryptography, hashing, token generation, randomness, key storage, certificate validation, or signature checks replaced with simpler but weaker logic.
5. Dependencies, plugins, build scripts, generated code, or external tools introduced without need.
6. Error responses or logs that disclose internals not previously disclosed.

Prefer existing security wrappers and policy gates. Do not invent local security mechanisms during a cleanup pass.

## Pass F: Performance, Memory, and Scalability

Find obvious waste without premature optimization:

1. Repeated expensive computation, parsing, reflection, serialization, database queries, network requests, filesystem scans, regular expression compilation, image/media work, or excessive logging.
2. Hot-path bloat in startup, request handling, per-render paths, scrolling, layout, animation, reducers, serialization, validation, parsing, or frequently repeated callbacks.
3. Full collection/file loads where a targeted query, stream, lazy sequence, pagination, index, cache, or early exit is enough.
4. Unnecessary existence checks before resource operations when direct operation plus error handling avoids time-of-check/time-of-use races.
5. Unbounded collections, caches, queues, task groups, retry loops, recursion, listeners, or memory growth.
6. Avoidable allocation churn: recreating formatters, regexes, encoders/decoders, clients, observers, attributed strings, images, layout objects, style objects, or heavyweight services in hot paths.
7. N+1 query patterns, nested loops over large collections, repeated sorting/filtering, or conversions back and forth between equivalent representations.

Measure when the performance tradeoff is non-obvious. For obvious waste, fix locally.

## Pass G: Tests, Observability, and Failure Modes

Check whether simplified code remains testable and diagnosable:

1. Tests that overfit implementation details or duplicate production logic instead of asserting behavior.
2. Missing targeted regression tests for bug fixes, compatibility fallbacks, parsing/formatting edge cases, concurrency races, cancellation, permissions, migrations, and boundary cases.
3. Test helpers or mocks duplicated across files instead of using existing fixtures/builders.
4. Debug prints, temporary logs, screenshots, sleeps, arbitrary timeouts, disabled assertions, skipped tests, fragile snapshots, and brittle wall-clock assumptions.
5. Errors that lose context needed for support, logging, telemetry, or debugging.
6. Observability changes that alter event names, cardinality, privacy level, sampling, or support workflows.

Do not add a large test suite during a cleanup pass unless the change is risky or the bug is subtle. Prefer one targeted regression test over broad snapshot churn.

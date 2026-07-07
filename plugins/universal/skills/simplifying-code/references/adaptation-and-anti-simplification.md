# Adaptation and Anti-Simplification

Apply these language-agnostic rules, anti-patterns, and file-type prompts during review and cleanup.

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

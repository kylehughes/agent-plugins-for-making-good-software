# Review Lenses

## Contents

- Correctness and contracts
- State, concurrency, and distributed behavior
- Security and privacy
- Data, storage, and migrations
- API and compatibility
- Errors, lifecycle, and resources
- Performance and scalability
- Tests and observability
- Build, configuration, dependencies, and release
- UI, client, and mobile behavior
- Design and maintainability
- Runtime-specific prompts

Use only the sections relevant to the change. These are prompts for investigation, not automatic findings.

## Correctness and Contracts

- Does the implementation satisfy the stated requirement, existing tests, public behavior, and caller assumptions?
- Compare old and new behavior for every changed branch, default, order, side effect, and error.
- Check boundary values: empty, null/missing, zero, negative, maximum, overflow, duplicate, stale, malformed, reordered, and partially initialized inputs.
- Check numeric precision, units, rounding, time zones, calendars, clocks, durations, locale, encoding, and normalization.
- Check ordering, stable sorting, pagination, cursor semantics, deduplication, equality, hashing, and identity.
- Look for partial updates, torn state, stale caches, incorrect memoization, and hidden mutation.
- Verify default values and fallback behavior do not silently turn failure into apparent success.
- Confirm feature flags and configuration select the intended path in all supported environments.
- Check whether types encode the invariant or merely assert it at runtime.

## State, Concurrency, and Distributed Behavior

- Identify who owns mutable state and which thread, actor, event loop, lock, transaction, or process protects it.
- Check read-then-act and read-await-write sequences for interleaving.
- Check lock scope, lock order, reentrancy, atomicity, memory visibility, and unsafe publication.
- Check task/goroutine/thread lifetime, detached work, structured cancellation, and stale completion handlers.
- Check whether cancellation can leave state half-updated or resources unreleased.
- Check retries for idempotency, duplicate side effects, stable request identity, and retry storms.
- Check timeout ownership, backoff, jitter, backpressure, queue bounds, and overload behavior.
- Check event ordering, duplicate delivery, at-least-once semantics, stale messages, and out-of-order updates.
- Check transactions and distributed operations for partial success, compensation, and exactly-once assumptions.
- For every concurrency finding, describe the specific interleaving; “could race” is insufficient.

## Security and Privacy

- Locate trust boundaries and distinguish authentication from authorization.
- Verify object-, tenant-, role-, and action-level authorization on every sensitive path, including alternate endpoints and background jobs.
- Trace untrusted input to SQL, shell, templates, HTML, URLs, file paths, deserializers, interpreters, redirects, and dynamic code loading.
- Check SSRF, path traversal, injection, unsafe deserialization, cross-site scripting, request forgery, open redirect, and confused-deputy paths where applicable.
- Check secrets, credentials, tokens, personal data, and security metadata in source, logs, errors, analytics, caches, URLs, and client storage.
- Check cryptographic use for safe primitives, nonce/key reuse, comparison behavior, key storage, and verified authenticity. Do not invent custom cryptography fixes.
- Check session, cookie, CORS, origin, permission, sandbox, and least-privilege behavior where relevant.
- Check upload/download validation, content type, archive extraction, decompression limits, and parser resource limits.
- Check dependency provenance, integrity, install scripts, and newly expanded permissions.
- Prove the source-to-sink path and attacker capability before labeling a vulnerability.

## Data, Storage, and Migrations

- Check schema changes for old/new reader and writer compatibility during rolling deploys.
- Check nullability, defaults, constraints, indexes, uniqueness, collation, and data type width.
- Check whether backfills are bounded, resumable, observable, and safe to rerun.
- Check migration ordering, lock duration, table rewrites, transaction boundaries, and production data volume.
- Check rollback after new-format data has been written; reversible syntax does not guarantee reversible data.
- Check serialization and persisted formats for renamed fields, enum values, unknown fields, versioning, and precision loss.
- Check transactions for isolation assumptions, lost updates, duplicate inserts, partial commits, and retry behavior.
- Check deletion, retention, cascade behavior, soft-delete filtering, and restoration.
- Check cache invalidation and consistency between primary storage, replicas, indexes, and derived data.

## API and Compatibility

- Identify every consumer of changed public symbols, endpoints, events, files, schemas, environment variables, and command-line behavior.
- Check source, binary, wire, storage, semantic, and behavioral compatibility as applicable.
- Check required versus optional fields, default changes, enum expansion, error codes, status codes, and response ordering.
- Check mixed-version operation: old client/new server, new client/old server, old worker/new producer, and rollback.
- Check deprecation and migration paths; avoid flag-day assumptions unless deployment is truly atomic.
- Check feature negotiation and capability detection instead of version guessing.
- Check CLI exit codes, stdout/stderr contracts, machine-readable output, and script compatibility.
- Check configuration renames and default changes for existing deployments.

## Errors, Lifecycle, and Resources

- Check every exit path for correct propagation, translation, logging, cleanup, and user-visible state.
- Look for swallowed errors, catch-all handlers, success returned after partial failure, and retry of non-retryable errors.
- Check files, sockets, streams, database handles, transactions, locks, subscriptions, observers, timers, processes, and temporary files.
- Check initialization and teardown ordering, including failure during initialization.
- Check callback, listener, task, and subscription removal; confirm lifetime matches ownership.
- Check cancellation and timeout paths for cleanup and state restoration.
- Check memory ownership, reference cycles, use-after-free, double release, and retained closures/callbacks as relevant to the runtime.
- Check process termination, signal handling, shutdown deadlines, and draining behavior for services and tools.

## Performance and Scalability

- Focus on plausible hot paths and input sizes; do not report micro-optimizations without evidence.
- Check asymptotic complexity, nested scans, repeated parsing, repeated serialization, and accidental quadratic behavior.
- Check N+1 queries, per-item network calls, missing batching, and unbounded concurrency.
- Check unbounded collections, queues, caches, logs, retries, recursion, and buffered streams.
- Check large copies, retained graphs, allocation churn, blocking I/O on latency-sensitive threads, and expensive work on UI/main threads.
- Check cache key correctness, invalidation, stampedes, and cardinality.
- Check database query plans or indexes when the change materially alters query shape.
- Prefer benchmarks or profiles when performance is the claim; distinguish measurement flaws from implementation flaws.

## Tests and Observability

- Verify the test fails for the old/broken behavior and passes for the intended fix when feasible.
- Check assertions for vacuity, wrong object, wrong phase, missing await, swallowed failure, and over-broad snapshots.
- Check positive, negative, boundary, error, cancellation, retry, and concurrency paths relevant to the change.
- Check test isolation, deterministic clocks/randomness/order, cleanup, and hidden dependence on machine state or network.
- Check mocks and fakes against the real contract; overly permissive doubles can hide integration defects.
- Check whether disabled, deleted, or weakened tests remove the only coverage for a contract.
- Check logs, metrics, traces, audit records, and alerts for enough context to diagnose failure without exposing secrets.
- Check that failure signals remain visible; silent fallback and catch-and-log can convert outages into corrupted success.

## Build, Configuration, Dependencies, and Release

- Check behavior across supported operating systems, architectures, toolchains, build modes, and CI matrix entries.
- Check environment-specific defaults, relative paths, shell assumptions, case sensitivity, line endings, and locale.
- Check reproducibility: manifests and lockfiles agree, generated artifacts are current, and build steps do not depend on untracked state.
- Check dependency changes for API/runtime compatibility, transitive removals, duplicate versions, supply-chain risk, and expanded privileges.
- Check build scripts and CI for secret exposure, command injection, untrusted pull-request execution, and unsafe caches/artifacts.
- Check infrastructure changes for blast radius, least privilege, replacement/destruction, state drift, ordering, and rollback.
- Check release flags, phased rollout, migrations, and observability are sequenced safely.
- Check that documentation and examples match actual commands and supported versions when they are part of the shipped interface.

## UI, Client, and Mobile Behavior

- Check state restoration, lifecycle transitions, background/foreground behavior, cancellation, navigation, and stale async results.
- Check loading, empty, error, offline, retry, and partial-data states.
- Check main/UI-thread requirements and avoid blocking work on latency-sensitive paths.
- Check accessibility semantics, focus order, keyboard operation, contrast, dynamic text, reduced motion, and screen-reader output when UI changes.
- Check localization, pluralization, layout expansion, bidirectional text, locale-sensitive formatting, and hard-coded user-visible strings.
- Check permissions, privacy disclosures, deep links, universal/app links, notifications, and platform entitlements where applicable.
- Check supported OS/browser/device versions, feature availability, responsive layout, and resource constraints.
- Check local persistence and synchronization for schema migration, conflict resolution, and offline replay.

## Design and Maintainability

- Check that responsibility and state ownership have one clear home.
- Check dependency direction, layering, module boundaries, and whether the change creates cycles or bypasses established policy enforcement.
- Check duplicated business rules that can diverge, not merely duplicated syntax.
- Check whether an abstraction has a real invariant or variation point; avoid both speculative abstraction and copy-pasted policy.
- Check whether callers can misuse the API and whether types can make invalid states unrepresentable.
- Check complexity that obscures correctness, rollback, testing, or ownership.
- Check comments and documentation for contract-level information that cannot be expressed in code; do not demand narration of obvious implementation.
- Do not report design taste as a defect. Tie the concern to a concrete maintenance, correctness, compatibility, or operational consequence.

## Runtime-Specific Prompts

Verify the actual language, runtime, and platform versions. Compose with an available companion covering their semantics; its rules win for that platform. Reuse the existing review scope and evidence rather than starting another review. If no companion is available, inspect authoritative documentation and state any unresolved semantics that limit the review.

Use these platform-neutral questions to select the relevant guidance:

- Which guarantees are enforced statically, and which inputs or runtime shapes still require validation?
- How do isolation, suspension, blocking, cancellation, and resource lifetime interact at the changed boundary?
- Can aliasing, shared defaults, reflection, serialization, or foreign interfaces bypass the intended ownership or validation rules?
- Do imports, package lifecycle scripts, build tools, or dependency lifetimes introduce side effects?
- Which availability, persistence, ABI, layout, or allocation/release contracts must remain compatible?

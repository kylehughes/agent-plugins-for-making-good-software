# Change-Type Playbooks

## Contents

- Bug fixes
- New features
- Refactors
- API, schema, and storage migrations
- Dependency and toolchain updates
- Concurrency changes
- Performance changes
- Test-only changes
- Build, configuration, CI, and infrastructure
- Generated and vendored code
- Deletions and cleanup

Use the relevant playbook in addition to the general workflow. These checks are prompts, not presumed defects.

## Bug Fixes

- Reconstruct the original failure and verify the patch addresses its root cause rather than one symptom.
- Check that the regression test would fail before the fix and meaningfully exercises the reported path.
- Look for sibling paths with the same root cause and for broadened behavior that breaks valid cases.
- Check whether the fix changes errors, ordering, retries, or compatibility beyond the bug's scope.
- Check rollback and data already produced by the buggy version when applicable.

## New Features

- Map requirements to code paths, defaults, permissions, failure states, and tests.
- Check disabled/off/default behavior and interaction with existing users or stored data.
- Check authorization, abuse limits, privacy, observability, and operational ownership from the start.
- Check incomplete integration: UI without backend support, producer without consumer, flag without cleanup, or API without migration.
- Check whether unsupported states fail explicitly rather than silently degrading.

## Refactors

- Treat behavior preservation as the primary contract unless behavior change is explicit.
- Compare side effects, ordering, exceptions/errors, logging, synchronization, serialization, and timing—not only return values.
- Search for reflection, registration, dependency injection, annotations, selectors, string-based lookup, generated bindings, and external callers.
- Check that moved ownership does not duplicate state or bypass enforcement.
- Be especially skeptical of deleted tests or broad mechanical edits that hide one semantic change.

## API, Schema, and Storage Migrations

- Model old and new readers/writers and every mixed-version deployment order.
- Check additive-first or expand/migrate/contract sequencing when deployment is not atomic.
- Check backfill safety, retryability, progress visibility, and impact at production scale.
- Check defaults, nullability, constraints, enum/field renames, data conversion, and precision.
- Check rollback after new code has written new-format data.
- Check all consumers, jobs, analytics, caches, and external integrations—not just the primary application.

## Dependency and Toolchain Updates

- Inspect the actual version delta, manifest and lockfile changes, release notes, and migration requirements when available.
- Check runtime, compiler, OS, architecture, and transitive dependency compatibility.
- Check changed defaults, removed APIs, peer constraints, plugin compatibility, and duplicate major versions.
- Check install/build scripts, source provenance, integrity, licenses or policy constraints, and newly requested permissions.
- Run the most relevant build and tests; dependency updates often compile while changing runtime behavior.
- Do not object to a dependency merely because an internal implementation is possible. Identify a concrete cost or risk.

## Concurrency Changes

- Enumerate shared state, owners, synchronization, and task lifetime before judging syntax.
- Write down at least one adversarial interleaving for each candidate race.
- Check reentrancy across suspension points, atomicity across I/O, lock order, and cancellation.
- Check duplicate work and effects under retries, concurrent calls, process restarts, and message redelivery.
- Prefer stress, race-detector, or deterministic scheduler tests when the project supports them, but do not treat a clean run as proof.

## Performance Changes

- Confirm the metric and workload the change intends to improve.
- Check benchmark representativeness, warmup, variance, caches, release mode, and comparison baseline.
- Look for traded costs: latency versus throughput, memory versus CPU, client versus server, or average versus tail latency.
- Check correctness under batching, caching, parallelism, lazy loading, and approximation.
- Reject performance findings based only on aesthetics or tiny constant factors outside a hot path.

## Test-Only Changes

- Determine which production contract the test is meant to protect.
- Check that assertions observe the outcome rather than setup, mocks, or implementation details.
- Check missing await/join, caught assertion errors, permissive stubs, skipped cases, snapshots accepted blindly, and false-positive retries.
- Check determinism, isolation, cleanup, clocks, randomness, order, and environment dependence.
- Check whether deleted or weakened tests were compensating for a real regression.
- Do not demand tests for trivial code without identifying a likely escaped defect.

## Build, Configuration, CI, and Infrastructure

- Evaluate the exact execution environment: shell, permissions, event type, fork trust, secrets, paths, matrices, and caches.
- Check quoting, injection, globbing, failure propagation, exit codes, and conditional expressions.
- Check environment-specific defaults and whether local, CI, staging, and production behavior diverge.
- Check destructive infrastructure replacement, privilege expansion, public exposure, state moves, and rollback.
- Check cache/artifact keys for poisoning, staleness, cross-branch leakage, and reproducibility.
- Check that migration or deployment steps are sequenced and observable.

## Generated and Vendored Code

- Find the source of truth and regeneration command before commenting on generated output.
- Check whether generated changes are complete, reproducible, and version-aligned with the generator.
- Review hand-written adapters and generator configuration more deeply than mechanical output.
- Report generated-output defects when the output is shipped and broken, but direct the fix to the source of truth.
- Treat unexplained edits to vendored code as high-risk; check provenance and whether updates will overwrite them.

## Deletions and Cleanup

- Search for dynamic, string-based, configuration-based, and external references before declaring code unused.
- Check registration, reflection, plugins, routes, migrations, cron jobs, feature flags, scripts, and documentation.
- Check whether deletion removes fallback, compatibility, telemetry, cleanup, or rollback behavior.
- Check persisted data and external consumers that outlive the code.
- Distinguish dead code from rarely executed disaster-recovery code.

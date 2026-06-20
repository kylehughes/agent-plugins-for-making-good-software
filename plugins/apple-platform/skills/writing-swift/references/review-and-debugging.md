# Review and Debugging

## Contents

- Investigation workflow
- Read compiler diagnostics structurally
- Swift 6 concurrency diagnosis
- Correctness and lifetime review
- API and compatibility review
- Performance investigation
- Security and privacy review
- Diff hygiene
- Reporting templates

## Investigation Workflow

Use an evidence loop:

1. Reproduce the exact failure with the smallest relevant command.
2. Record toolchain, configuration, target, destination, platform, and input.
3. Reduce the failing path without changing semantics.
4. Form one falsifiable hypothesis.
5. Add instrumentation or a focused test that distinguishes that hypothesis.
6. Make the smallest fix consistent with the architecture.
7. Run the focused reproduction, then neighboring and broad regression checks.
8. Remove temporary instrumentation and inspect the diff.

Do not redesign a subsystem from a stack trace alone. Check logs, generated interfaces, macro expansion, package resolution,
compiler invocations, and runtime environment as appropriate.

When a failure appears only in CI, compare toolchain, SDK, architecture, locale, time zone, filesystem case sensitivity,
parallelism, environment variables, signing, sandbox, and dependency cache. Do not assume “CI flake” until a race or external
cause is demonstrated.

## Read Compiler Diagnostics Structurally

Swift diagnostics often report the symptom at a use site while the design issue originates in a declaration. Inspect the
full diagnostic chain, notes, inferred generic types, protocol requirements, and isolation annotations.

Useful tactics:

- Reduce a generic expression into named intermediate values to expose inferred types.
- Use `type(of:)`, generated interfaces, `swiftc -typecheck`, or IDE quick help to confirm imported signatures.
- Replace shorthand closure syntax temporarily when overload resolution is unclear.
- Inspect availability and conditional compilation for the active SDK.
- Expand macros when generated declarations affect lookup or conformance.
- Verify whether a manifest, plugin, or build setting selects a different language mode than expected.

Do not keep diagnostic-only decomposition if it harms the final design, but prefer readable named steps when they clarify
complex inference.

## Swift 6 Concurrency Diagnosis

For each isolation error, draw the transfer:

```text
owner/executor A -- value or closure --> owner/executor B
```

Then identify:

- Mutable aliases that remain on both sides.
- Whether the value is actually `Sendable`.
- Whether a closure captures actor-isolated state.
- Whether the caller or callee should own isolation.
- Whether an `await` creates a reentrancy window.
- Whether an unstructured task outlives its owner.
- Whether cancellation reaches the underlying work.

Common bad fixes:

- Applying `@MainActor` to a whole type whose work should be concurrent.
- Adding `@unchecked Sendable` to a mutable class without synchronization.
- Wrapping code in `Task {}` to make an `await` compile while losing ordering and errors.
- Using `Task.detached` to escape inherited isolation.
- Marking actor state `nonisolated(unsafe)`.
- Adding `@preconcurrency` broadly enough to hide unrelated imported API problems.
- Capturing `self` weakly and silently dropping required work.

Prefer changing ownership and API boundaries over annotations that merely suppress the checker.

## Correctness and Lifetime Review

Review observable behavior before style:

- Optional and collection boundaries: empty input, missing value, invalid index, duplicate key.
- Integer overflow, units, precision, date/calendar/time-zone behavior, and locale-sensitive parsing.
- State-machine transitions, retries, idempotency, and partial failure.
- Resource lifetime: tasks, observations, continuations, file handles, sockets, delegates, timers, streams.
- Retain cycles and premature deallocation in escaping closures.
- Exactly-once callback or continuation completion.
- Cancellation and cleanup on success, error, timeout, and deinitialization.
- Actor reentrancy and compound invariants split across calls.
- UI updates performed on the correct actor and stale async results discarded.
- Codable compatibility, unknown enum cases, defaults, and migration of persisted data.

A weak capture is not automatically correct. Ask whether dropping the operation is allowed. Conversely, a strong capture by
an unbounded task can retain an object forever.

## API and Compatibility Review

For a public or package-facing change, compare generated interfaces and representative clients.

Check:

- Source-breaking renames, label changes, overload ambiguities, and generic inference changes.
- ABI or resilience effects for distributed binary libraries.
- New protocol requirements that break conformers.
- Enum exhaustiveness and `@frozen` implications.
- Changed isolation, `Sendable`, global-actor, or throwing contracts.
- Deployment and SDK availability.
- Objective-C selectors and bridging.
- Codable/wire/storage representation.
- Behavioral compatibility, including ordering and cancellation.

An additive overload can still be source-breaking through ambiguity. A defaulted parameter can alter overload selection. A
new actor annotation can require `await` at every consumer. Treat these as compatibility changes even if the declaration
looks additive.

## Performance Investigation

Define the metric and workload before optimizing. Use release builds.

- Time Profiler for CPU paths.
- Allocations, leaks, and memory graph tools for lifetime/allocation issues.
- Signposts and points of interest for async workflows.
- Instruments or package benchmarks for repeatable measurements.
- Network and filesystem tracing for I/O latency.
- Concurrency visualizations, task names, and sanitizer/stress runs for scheduling behavior.

Compare distributions, not one timing sample. Control warm-up, cache state, input, device thermal conditions, simulator vs.
device, and background load.

Review algorithmic complexity and task fan-out before adding inlining, specialization, unsafe buffers, atomics, or custom
allocators. Preserve a benchmark that proves the regression and improvement where the project supports it.

## Security and Privacy Review

Inspect Swift code for:

- Unsafe pointer bounds, lifetime, alignment, and integer conversion.
- Untrusted decoding, decompression, archive extraction, and path traversal.
- Command construction and process arguments.
- TLS validation, certificate handling, and insecure fallback.
- Authentication state races, token persistence, keychain access groups, and logout cleanup.
- Sensitive values in logs, errors, analytics, crash metadata, tests, and fixtures.
- Clipboard, pasteboard, photos, contacts, location, microphone, camera, and other permission-bound data.
- File protection, backup eligibility, temporary-file permissions, and app-group boundaries.
- Web view message handlers and URL scheme validation.

Use platform security APIs rather than hand-rolled cryptography. Do not include real secrets in source or tests. Treat
privacy manifests, entitlements, and usage descriptions as part of the implementation when relevant.

## Diff Hygiene

Before finalizing:

```bash
git status --short
git diff --check
git diff --stat
git diff
```

Look for:

- Unrelated reformatting or member reordering.
- Accidental `Package.resolved`, project, lockfile, or generated-output changes.
- Raised tools/language/deployment versions.
- Debug prints, breakpoints, disabled tests, focused tests, and temporary flags.
- Added force operations or concurrency escape hatches.
- New public API without docs or tests.
- Secrets, absolute local paths, timestamps, and binary artifacts.
- Tests that pass only because assertions were weakened.

## Reporting Templates

### Implementation summary

```text
Changed:
- <behavior and owning component>

Validated:
- `<exact command>` — passed
- `<exact command>` — passed

Not run / residual risk:
- <specific check and reason>
```

### Review finding

```text
[severity] path/to/File.swift:line — concise failure mode

<Why this is observable or risky, including the triggering path.>

Suggested fix: <smallest sound change, with test recommendation when useful.>
```

Use severity based on impact and likelihood, not tone:

- **Critical:** likely data loss, exploitable security fault, or systemic crash in normal use.
- **High:** incorrect behavior, race, crash, or compatibility break on a plausible path.
- **Medium:** defect under a narrower condition or design issue likely to cause future failures.
- **Low:** localized maintainability or rule violation with limited behavioral risk.

If no actionable findings exist, say that directly and list validation gaps rather than inventing stylistic objections.

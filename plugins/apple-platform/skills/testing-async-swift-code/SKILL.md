---
name: testing-async-swift-code
description: "Make Swift async tests deterministic. Use for flaky tests, clocks, observer attachment, completion, cancellation, cleanup, and proving non-occurrence; not general test organization or production concurrency design."
---

# Testing Async Swift Code

Recurring async-test flakes share one shape: the test infers progress from scheduler behavior instead of awaiting an explicit happens-before edge. `advance(by:)`, `Task.yield()`, `Task.sleep()`, and `stop()` prove only that time passed or the scheduler turned — not that an observer saw a value, a task detached, or the system quiesced. This skill codifies the four primitives that prove those edges, the category-to-primitive decision table, canonical idioms, and anti-patterns to remove.

This skill assumes the base doctrine — event-driven waits over scheduler guesses, timeouts as safety bounds rather than progress mechanisms, Swift Testing confirmations, cancellation proof — covered by a general Swift Concurrency skill when one is installed (`using-swift-concurrency` here). It adds the primitive layer that doctrine stops short of.

When the behavior under test is synchronous, don't add async machinery just to observe it; assert it synchronously and keep the recorder for real async boundaries.

For an explicit invariant or proof request, or when changed async code alters an enforcement model or transition, use `verifying-invariants` when available to scope the claim and select the lightest adequate evidence. This skill remains independently useful for deterministic async-test design.

## The Four Primitives

Each primitive owns one synchronization problem. No two overlap. These are contracts: use your project's implementations when it has them, adopt the named ecosystem implementations when it doesn't, or write the small ones from [the contracts reference](references/primitive-contracts.md).

### 1. Virtual clock — deterministic time

Owns: "advance time deterministically for code that sleeps on a `Clock`." Nothing else.

Production code that debounces, throttles, retries, or times out should accept a `Clock`; tests then inject a controllable clock and advance it explicitly. Point-Free's [swift-clocks](https://github.com/pointfreeco/swift-clocks) `TestClock` is the ecosystem-standard implementation; a minimal manual clock is also about a page of code (contract in the reference).

If the clock's `advance` is synchronous, it only schedules resumed continuations — always pair an advance with an explicit handshake, usually a recorder wait, to observe whatever emission the sleep drove. Never probe the clock ("is something sleeping for at least N?") to prove an operator observed a value; the operator doesn't expose that, and the probe can't prove what it claims.

### 2. Event recorder — ordered transcript with an awaited-detach barrier

Owns: "record every emission from an `AsyncSequence`, in order, with a real-time-bounded wait API."

The **detach barrier** cancels the collection task *and awaits its termination*, so that task cannot append later. This proves recorder detachment and makes its final collected transcript stable. It does not prove the production source stopped emitting: a detached collector cannot see later source events. For a source-stop assertion, keep independent live observation or await producer-owned completion evidence. Direct `record(_:)` callbacks need their own stop barrier.

Two more properties worth having: transcript **baselines** (`waitFor(_:since:)` — wait for a match after index N without a bespoke loop) and a `recording()` factory for callback-shaped APIs whose callback can `await record(_:)` directly. Do not wrap synchronous `@MainActor` callbacks in `AsyncStream` plus a recorder; that adds a collector-task hop the test did not need.

### 3. Serial main executor — controlled Swift task scheduling

Owns: "make Swift task scheduling more predictable within a guarded test scope."

Point-Free's [swift-concurrency-extras](https://github.com/pointfreeco/swift-concurrency-extras) provides `withMainSerialExecutor`, which redirects global task jobs to the main serial executor to make tests more predictable. Its runtime hook has no scoping guarantee if another caller changes the global state. [`Task.yield()`](https://developer.apple.com/documentation/swift/task/yield()) permits other work to run but does not itself guarantee that a particular task runs next.

Use a single yield only for a test-controlled handoff whose ordering is established by the harness and has no stronger observable barrier. This does not prove readiness inside an opaque framework API, including `NotificationCenter` async-sequence observer registration. Use its readiness seam or the bounded observation idiom instead; awaiting a listener after one possibly missed post can hang before cleanup runs.

The hook is **process-global**, and Swift Testing can run unrelated suites concurrently. Guard all hook users with a shared serializing helper or trait and keep the scope short. A suite's `.serialized` trait alone does not exclude unrelated suites. Use it only for tests whose assertions depend on Swift task ordering.

The hook captures only Swift Concurrency task scheduling. `DispatchQueue` work (cache-observer callbacks, Combine `schedule(after:)`, `URLSession` completions) is unaffected — those races need observable completion and cleanup barriers — and it doesn't fully constrain AsyncAlgorithms operators' internal `TaskGroup` hops.

### 4. Sliced timeout budgets — the failure policy

Owns: the timeout policy around every wait.

A shared timeout budget can spend a nominal duration in short sleep slices. Delayed resumptions can make its elapsed wall-clock duration longer, which may reduce failures caused by contention. This is a scheduling heuristic, not a guarantee that progressing work will finish before the timeout. Prove progress with observable synchronization edges; diagnose a timeout from the missing event and the CI evidence.

Timeouts catch bugs; they don't drive progress. If a test only passes because the timeout expired, the test is wrong. Keep the default budget unless measured work or CI evidence justifies a longer one, and explain the reason locally. Never hand-roll a wall-clock deadline (`ContinuousClock().now.advanced(by:)` loops, yield spins bounded by a real clock) in a test or helper.

## Preflight for Async Test Changes

When creating or editing an async test, make the determinism contract explicit before committing:

- **Attachment edge**: what proves the observer, listener, task, or stream is attached before the trigger?
- **Completion edge**: what event proves the behavior under test happened?
- **Cleanup edge**: what awaits task release, provider stop, stream detach, or harness teardown if an assertion throws?
- **Isolation edge**: does the test use process-global hooks, shared singleton/coordinator state, reused IDs, or cache state that requires `.serialized`, unique IDs, or a reset seam?
- **Timeout edge**: is every non-default timeout justified by real work or CI evidence?

Make the answer visible in code structure, a short local comment where needed, or the PR/commit notes. If the answer is "the scheduler will probably run it," the test is not ready.

## Category → Primitive Decision Table

| Category | Virtual clock | Recorder | Serial executor | Timeouts |
|---|:---:|:---:|:---:|:---:|
| Timing logic (debounce / throttle / retry) | ✓ | ✓ | ✓ | net |
| Observer lifecycle (provider stop/detach) | | ✓ | | net |
| Refresh / refetch observation | | ✓ | | net |
| Sequence / event ordering | | ✓ | ✓ | net |
| State-transition | | ✓ (on published state) | ✓ | net |
| Synchronous callback effects | | | | |
| Non-occurrence ("after stop, no more X") | | ✓ (live observation or producer completion) | | net |
| Cancellation correctness | | ✓ | ✓ | net |
| Concurrency correctness (actor races, reentrancy) | | ✓ | ✓ | net |

"net" means a real-time timeout is always the outer failure bound, never a load-bearing signal.

For synchronous callback effects, assert synchronously on local `@MainActor` state. The empty row is deliberate: using a primitive there usually creates the race.

Apply the category through [the canonical idioms](references/idioms.md) — timing-operator marble tests, observer lifecycle, state transitions, refresh handles, NotificationCenter handshakes, non-occurrence, and cancellation each have one.

## Anti-Patterns

| Pattern | Why it's wrong | What to use instead |
|---|---|---|
| `for _ in 0 ..< N { await Task.yield() }` in a test body | Fixed-count yield budgets hide the actual happens-before edge. | A recorder wait; a marble harness for timing operators. Controlled single-hop handoff follows the serial executor's narrow scope above. |
| `Task.sleep` to "let the system settle" | Wall-clock sleeps are slow and still race under CI load. | Virtual clock + recorder handshake. |
| Custom inline "recorder" / "collector" classes per test file | Re-invents the recorder without the detach barrier. | One shared recorder with `detach()`. |
| Wrapping a synchronous `@MainActor` callback in `AsyncStream` + recorder | Adds a collector-task hop and can time out even though the callback ran. | Append to local main-actor state; assert after the awaited operation returns. |
| Clock probes ("waitUntilSleeping", "deadline at least N") | They try to prove "the operator observed my value," which the operator doesn't expose. | Explicit recorder wait after the advance. |
| Mutating the backing store or cache directly when testing subscription refresh | Proves a cache mutation happened, not that the subscriber consumed the requested refresh. | Drive through the production awaitable refresh handle or a test seam that delegates to it. |
| Implementing an awaitable refresh by spawning a task or forwarding through fire-and-forget `refresh()` | Decouples the waiter from the requested operation: unrelated emissions satisfy it, coalesced refreshes get dropped. | Await the active inner refresh handle directly. |
| Re-waiting for an inner refresh handle after caller cancellation | Cancelled teardown tasks spin readiness loops or start stale work. | Check cancellation before each wait, after each wake, and before forwarding. |
| Treating store-change callbacks as proof a refresh completed | Framework callbacks are scheduler-driven; they lag and coalesce under CI load. | Force a read/emission on the observed subscription, then wait on the subscription event. |
| Posting one `NotificationCenter` notification after `Task.sleep` | The listener may not have attached; the test misses the only post and hangs. | Await a readiness seam, or repeatedly post under a bounded wait until the state transition is observed. |
| Non-occurrence via "sleep X ms then check empty" | Sleeping without proven setup is not proof. | Prove attachment, then observe over a bounded window; use producer completion when available. Detach only after observation. |
| Raising a timeout because a test flaked in CI | A timeout alone does not distinguish a lost event from slow work or scheduler contention; a bigger constant can hide the cause. | Trace the emission path: stale read, attach-after-emit, dropped one-shot. |
| Hand-rolled `ContinuousClock` deadlines or yield-spin waits | Duplicates timeout policy; yield spins can worsen contention and neither form proves progress. | Budgeted waits on the recorder or polling helpers. |
| Production observers spawning one task per change notification, re-reading state in each | Actor reentrancy resumes reads out of order; downstream last-value latching freezes on a stale snapshot. Microseconds locally, seconds on CI. | Coalesce notifications into a pending set drained by one serial loop. |
| Calling a process-global hook from parallel suites without a scope guard | Concurrent sibling calls clobber each other. | A suite trait or serializing wrapper around the hook. |
| Reusing entity IDs in tests backed by shared singleton/coordinator state | Prior dirty state leaks across tests; assertions become order-dependent. | Unique IDs per test, or an explicit reset seam. |
| Declaring a CI-only flake fixed after local stress runs | Local 100× loops apply useful pressure but do not prove behavior on the CI runner where the flake reproduces. | Run the CI workflow serially on the final SHA for an agreed proof count; restart the count after any code change. |

## Checklist for New Async Tests

1. Identify the category from the table; load the matching idiom from [the idioms reference](references/idioms.md).
2. Synchronous callback on the current actor → record into local state, assert synchronously, stop here.
3. Timing-operator semantics → marble harness. Wrapper lifecycle is a separate test with a zero interval.
4. Apply the serial executor to the smallest suite or region that needs Swift task ordering.
5. Use a virtual clock for timing; real clocks only for the timeout safety net.
6. Attach a recorder to whatever `AsyncSequence` the system publishes.
7. Drive the system, then block on the specific wait that proves the behavior — never a sleep, never a yield budget.
8. Keep observation live while checking source non-occurrence, or use producer-owned completion evidence. Await `detach()` before reading a final collected transcript; detachment alone proves only collector termination.
9. Every wait has a real-time timeout; longer than default only with a justifying comment.
10. Centralize awaited cleanup in a cleanup helper rather than duplicating success/failure paths. On compilers supporting [async `defer`](../modeling-swift-types-for-correctness/references/swift-feature-status.md#release-18), it can provide scope-bound cleanup; account for cancellation in either form.
11. Shared singleton or coordinator state → unique IDs per test or an explicit reset.
12. CI-only flakes are proven fixed in CI, serially, on the final SHA.

## Reference Map

Load only what the task needs:

- [Primitive contracts](references/primitive-contracts.md): the API contract for each primitive, with minimal reference implementations — recorder with detach barrier and baselines, timeout budget, awaited-cleanup helper, manual clock. Read when the project lacks a primitive.
- [Canonical idioms](references/idioms.md): the worked test shapes per category — marble-diagram timing tests, wrapper lifecycle, observer lifecycle, state transition, synchronous callbacks, refresh handles, NotificationCenter handshakes, non-occurrence, cancellation. Read when writing or migrating a test.

Before finishing, confirm the five preflight edges are answered, no anti-pattern row matches the new test, and every wait routes through a budgeted primitive.

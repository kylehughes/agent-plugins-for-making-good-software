---
name: testing-async-swift-code
description: "Make Swift async tests deterministic. Use for flaky tests, clocks, observer attachment, completion, cancellation, cleanup, and proving non-occurrence; not general test organization or production concurrency design."
---

# Testing Async Swift Code

Recurring async-test flakes share one shape: the test infers progress from scheduler behavior instead of awaiting an explicit happens-before edge. `advance(by:)`, `Task.yield()`, `Task.sleep()`, and `stop()` prove only that time passed or the scheduler turned — not that an observer saw a value, a task detached, or the system quiesced. This skill codifies the four primitives that prove those edges, the category-to-primitive decision table, canonical idioms, and anti-patterns to remove.

This skill assumes the base doctrine — event-driven waits over scheduler guesses, timeouts as safety bounds rather than progress mechanisms, Swift Testing confirmations, cancellation proof — covered by a general Swift Concurrency skill when one is installed (`using-swift-concurrency` here). It adds the primitive layer that doctrine stops short of.

When the behavior under test is synchronous, don't add async machinery just to observe it; assert it synchronously and keep the recorder for real async boundaries.

## The Four Primitives

Each primitive owns one synchronization problem. No two overlap. These are contracts: use your project's implementations when it has them, adopt the named ecosystem implementations when it doesn't, or write the small ones from [the contracts reference](references/primitive-contracts.md).

### 1. Virtual clock — deterministic time

Owns: "advance time deterministically for code that sleeps on a `Clock`." Nothing else.

Production code that debounces, throttles, retries, or times out should accept a `Clock`; tests then inject a controllable clock and advance it explicitly. Point-Free's [swift-clocks](https://github.com/pointfreeco/swift-clocks) `TestClock` is the ecosystem-standard implementation; a minimal manual clock is also about a page of code (contract in the reference).

If the clock's `advance` is synchronous, it only schedules resumed continuations — always pair an advance with an explicit handshake, usually a recorder wait, to observe whatever emission the sleep drove. Never probe the clock ("is something sleeping for at least N?") to prove an operator observed a value; the operator doesn't expose that, and the probe can't prove what it claims.

### 2. Event recorder — ordered transcript with an awaited-detach barrier

Owns: "record every emission from an `AsyncSequence`, in order, with a real-time-bounded wait API."

The load-bearing property is the **detach barrier**: `detach()` cancels the collection task *and awaits its termination*, so no element can land in the transcript after it returns. That is what makes non-occurrence tests sound: detach, snapshot the baseline count, provoke the potentially-racy event, then assert the count stayed stable over a bounded window. A recorder without the awaited barrier is a race with extra steps.

Two more properties worth having: transcript **baselines** (`waitFor(_:since:)` — wait for a match after index N without a bespoke loop) and a `recording()` factory for callback-shaped APIs whose callback can `await record(_:)` directly. Do not wrap synchronous `@MainActor` callbacks in `AsyncStream` plus a recorder; that adds a collector-task hop the test did not need.

### 3. Serial main executor — deterministic Swift task scheduling

Owns: "make Swift Concurrency scheduling deterministic for the duration of a test."

Point-Free's [swift-concurrency-extras](https://github.com/pointfreeco/swift-concurrency-extras) provides `withMainSerialExecutor`: with the hook installed, `await Task.yield()` hands control to the next scheduled task on `MainActor`'s queue in FIFO order, making ordering-dependent tests deterministic for the portions of the system Swift Concurrency controls.

The hook is **process-global**, and Swift Testing can run unrelated suites concurrently. Guard the scope — wrap it in a serializing helper or apply a suite trait rather than calling the raw hook from parallel suites — and keep it short. Use it only for tests whose assertions depend on Swift task ordering.

The hook captures only Swift Concurrency task scheduling. `DispatchQueue` work (cache-observer callbacks, Combine `schedule(after:)`, `URLSession` completions) is unaffected — those races need the recorder's awaited detach barrier — and it doesn't fully constrain AsyncAlgorithms operators' internal `TaskGroup` hops.

### 4. Contention-scaled timeout budgets — the outer failure bound

Owns: the real-time safety net around every wait.

Pay a deadline out in short sleep slices instead of one wall-clock sleep: each slice resumption pays the same per-suspension scheduling debt the awaited emission chain pays, so on a healthy scheduler the budget elapses in roughly the nominal timeout while on a starved CI runner the effective deadline stretches proportionally. A legitimately progressing emission always beats its timeout; a true non-occurrence still fails. A single wall-clock deadline cannot provide this — it races one sleep against a many-hop emission chain, and under CI load the chain loses no matter how large the constant is.

Timeouts catch bugs; they don't drive progress. If a test only passes because the timeout expired, the test is wrong. Because budgets scale with contention, raising a timeout above the default is rarely justified — reserve longer timeouts for waits that do legitimately long work even on a healthy machine, with a comment explaining why. Never hand-roll a wall-clock deadline (`ContinuousClock().now.advanced(by:)` loops, yield spins bounded by a real clock) in a test or helper.

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
| Non-occurrence ("after stop, no more X") | | ✓ (detach + assert count stable) | | net |
| Cancellation correctness | | ✓ | ✓ | net |
| Concurrency correctness (actor races, reentrancy) | | ✓ | ✓ | net |

"net" means a real-time timeout is always the outer failure bound, never a load-bearing signal.

For synchronous callback effects, assert synchronously on local `@MainActor` state. The empty row is deliberate: using a primitive there usually creates the race.

Apply the category through [the canonical idioms](references/idioms.md) — timing-operator marble tests, observer lifecycle, state transitions, refresh handles, NotificationCenter handshakes, non-occurrence, and cancellation each have one.

## Anti-Patterns

| Pattern | Why it's wrong | What to use instead |
|---|---|---|
| `for _ in 0 ..< N { await Task.yield() }` in a test body | Fixed-count yield budgets hide the actual happens-before edge. | A recorder wait; a marble harness for timing operators. A single `Task.yield()` under the serial executor is acceptable only when deliberately handing off one known Swift-task hop with no stronger observable barrier. |
| `Task.sleep` to "let the system settle" | Wall-clock sleeps are slow and still race under CI load. | Virtual clock + recorder handshake. |
| Custom inline "recorder" / "collector" classes per test file | Re-invents the recorder without the detach barrier. | One shared recorder with `detach()`. |
| Wrapping a synchronous `@MainActor` callback in `AsyncStream` + recorder | Adds a collector-task hop and can time out even though the callback ran. | Append to local main-actor state; assert after the awaited operation returns. |
| Clock probes ("waitUntilSleeping", "deadline at least N") | They try to prove "the operator observed my value," which the operator doesn't expose. | Explicit recorder wait after the advance. |
| Mutating the backing store or cache directly when testing subscription refresh | Proves a cache mutation happened, not that the subscriber consumed the requested refresh. | Drive through the production awaitable refresh handle or a test seam that delegates to it. |
| Implementing an awaitable refresh by spawning a task or forwarding through fire-and-forget `refresh()` | Decouples the waiter from the requested operation: unrelated emissions satisfy it, coalesced refreshes get dropped. | Await the active inner refresh handle directly. |
| Re-waiting for an inner refresh handle after caller cancellation | Cancelled teardown tasks spin readiness loops or start stale work. | Check cancellation before each wait, after each wake, and before forwarding. |
| Treating store-change callbacks as proof a refresh completed | Framework callbacks are scheduler-driven; they lag and coalesce under CI load. | Force a read/emission on the observed subscription, then wait on the subscription event. |
| Posting one `NotificationCenter` notification after `Task.sleep` | The listener may not have attached; the test misses the only post and hangs. | Await a readiness seam, or repeatedly post under a bounded wait until the state transition is observed. |
| Non-occurrence via "sleep X ms then check empty" | Sleeping and hoping is not proof. | Detach first, then assert no events over a bounded window from a baseline. |
| Raising a timeout because a test flaked in CI | With contention-scaled budgets, a timeout still expiring means the event is genuinely not arriving; a bigger constant hides the lost signal. | Trace the emission path: stale read, attach-after-emit, dropped one-shot. |
| Hand-rolled `ContinuousClock` deadlines or yield-spin waits | Re-creates the wall-clock-vs-scheduling-debt race the budget removes; spinning worsens the contention it loses to. | Budgeted waits on the recorder or polling helpers. |
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
8. Always `await detach()` before reading a "final" transcript snapshot or asserting non-occurrence.
9. Every wait has a real-time timeout; longer than default only with a justifying comment.
10. Awaited cleanup goes through a cleanup helper (`defer` cannot `await`), not duplicated success/failure paths.
11. Shared singleton or coordinator state → unique IDs per test or an explicit reset.
12. CI-only flakes are proven fixed in CI, serially, on the final SHA.

## Reference Map

Load only what the task needs:

- [Primitive contracts](references/primitive-contracts.md): the API contract for each primitive, with minimal reference implementations — recorder with detach barrier and baselines, timeout budget, awaited-cleanup helper, manual clock. Read when the project lacks a primitive.
- [Canonical idioms](references/idioms.md): the worked test shapes per category — marble-diagram timing tests, wrapper lifecycle, observer lifecycle, state transition, synchronous callbacks, refresh handles, NotificationCenter handshakes, non-occurrence, cancellation. Read when writing or migrating a test.

Before finishing, confirm the five preflight edges are answered, no anti-pattern row matches the new test, and every wait routes through a budgeted primitive.

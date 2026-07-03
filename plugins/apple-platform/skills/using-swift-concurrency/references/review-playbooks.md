# Review Playbooks

Use this reference to run a systematic Swift Concurrency review or migration pass.

## Fast PR review

1. Identify changed isolation domains: new `@MainActor`, actors, `nonisolated`, `@concurrent`, `Sendable`, `@unchecked Sendable`, `@preconcurrency`, task creation.
2. For each new task, identify owner, cancellation, priority, and test observability.
3. For each `await`, check whether pre-await state is used afterward.
4. For each protocol change, check call-site and conformer consequences.
5. For each new framework API, check iOS 16 availability.
6. For each escape hatch, demand a written invariant.

## Migration pass from warnings to Swift 6.3 correctness

Order matters:

1. Enable strict checking/build settings in the smallest target first.
2. Separate UI code from DTO/domain code. Move or mark DTOs `nonisolated`.
3. Add type-level `@MainActor` to UI models/controllers, not individual random properties.
4. Make value snapshots `Sendable`.
5. Fix protocols: isolation, async requirements, `Sendable` constraints.
6. Replace hidden unstructured tasks with direct `await`, structured tasks, or owned task handles.
7. Audit actors for real state and reentrancy.
8. Localize legacy imports/bridges behind adapters.
9. Use `@unchecked Sendable`, `@preconcurrency`, `assumeIsolated`, and `nonisolated(unsafe)` only for remaining cases with proof.
10. Add race/reentrancy/cancellation tests.

## Isolation map template

For a type under review, fill this out mentally or in comments:

```text
Type:
Role: UI / domain / service / persistence / adapter / test
Default isolation in module:
Explicit isolation:
Mutable state owner:
Synchronization strategy:
Sendable status:
Task ownership:
Cancellation path:
Availability constraints:
Legacy/beta dependencies:
```

If any field is unclear, the design is probably not ready.

## Task review template

For each `Task`, `Task.immediate`, or `Task.detached`:

```text
Why is a new task needed?
Why not direct await / async let / task group?
Who owns the handle?
When is it cancelled?
What actor does the body run on?
What values are captured?
Are captures Sendable or actor-isolated safely?
Can tests await completion?
What happens on error/cancellation?
```

## Actor review template

For each actor:

```text
What mutable state is protected?
What invariants require serialization?
Which methods contain await?
For each await, what state was read before it?
Can reentrancy violate the invariant?
Does the actor expose mutable references?
Could a lock or value snapshot be simpler?
Could @MainActor be the right actor instead?
```

## Protocol review template

For each protocol:

```text
Expected conformers:
Expected callers:
Should the protocol be UI-bound?
Should requirements be sync or async?
Should conforming values be Sendable?
Are closure parameters @Sendable / actor-isolated?
Do associated types need Sendable?
Does default actor isolation accidentally change the contract?
Can a mock conform easily?
Can an actor conform if desired?
```

## Availability review template

For every new API or framework:

```text
Is this Swift syntax or runtime API?
Minimum OS availability?
Does the project support iOS 16?
Is there a #available fallback?
Does old SDK compilation need #if canImport?
Does beta API leak into stable protocols or data models?
```

## Common fixes by symptom

| Symptom | First fixes |
|---|---|
| MainActor conformance error on DTO | Mark DTO/protocol/nested types `nonisolated`; move to domain module. |
| UI update from background callback | Add `@MainActor` apply method; bridge with `Task { @MainActor in }` at boundary. |
| Non-Sendable capture in task group | Capture Sendable snapshot/dependency; move work into actor; avoid capturing `self`. |
| Stateless actor | Convert to `struct`/`final class`; add actor only for real mutable state. |
| Main thread overhang | Move CPU work to `@concurrent` function with Sendable inputs/outputs. |
| Flaky async test | Replace sleep/yield with continuation, task handle, sequence recorder, or confirmation. |
| Continuation crash | Ensure exactly-once resume; use stream for multi-shot; guard callback/cancel races. |
| Duplicate actor work | Store in-flight task or reserve state before await. |
| iOS 16 compile/runtime issue | Gate newer API or use iOS 16 fallback. |

## Final response checklist for code reviews

When returning a review, include:

- The root issue in one sentence.
- The isolation/lifetime decision.
- The smallest safe patch or precise guidance.
- Any availability caveat for iOS 16.
- Any remaining risk that tests should cover.

# Goal-contract design reference

Use this reference when source material is long, ambiguous, multi-milestone, or likely to produce a non-terminating loop.

## 1. Why large-spec pointers fail

A pointer-only goal delegates closure back to a document that was usually written for humans, not a completion evaluator. Large specs commonly mix:

- required behavior;
- implementation ideas;
- rationale and examples;
- quality aspirations;
- unresolved decisions;
- future work;
- optional refinements;
- broad repository standards;
- phrases such as “including,” “as needed,” and “production-ready.”

A persistent worker can always reinterpret one of these as unfinished. The more capable the model, the more possible improvements it can discover. The fix is not a better summary of the spec. The fix is a separate, finite closure contract.

The goal may still reference the full spec for intent. It must also state that the fixed acceptance criteria in the goal—not every sentence in the spec—govern termination.

## 2. The closure equation

Treat a goal as this contract:

```text
SUCCESS = one outcome
          AND every fixed acceptance criterion passes
          AND required invariants hold
          AND decisive evidence is surfaced
          AND no in-scope regression remains
```

`BLOCKED` is a separate terminal state, not a weaker form of success:

```text
BLOCKED = required external dependency unavailable
          OR bounded no-progress threshold reached
          OR absolute turn cap reached
```

Anything not represented in one of these terms is context, method, or follow-up—not closure.

## 3. Source triage

Classify every material statement before deciding whether it belongs in the goal.

### Required outcome

Include when the statement names behavior, an artifact, a migration state, or a user-visible result that must exist.

Examples:

- “All call sites use the new API.”
- “The generated schema contains fields X and Y.”
- “Landscape rotation remains supported on iPhone.”

### Invariant

Include when a property must remain true while the outcome changes.

Examples:

- source compatibility for public API consumers;
- no data loss during migration;
- unchanged accessibility labels;
- no new warnings in touched targets.

### Validation

Include or strengthen when the source already names a test, command, measurement, fixture, screenshot, or review method.

### Implementation guidance

Include only when violating it would make the result unacceptable. Otherwise leave it in the referenced source.

“Use actor isolation because this API must be concurrency-safe” may be a constraint. “Consider using an actor” is guidance.

### Decision prerequisite

Use when an unresolved product, policy, security, or rollout choice changes what would count as an acceptable result. Do not let the worker silently choose among materially different outcomes. Resolve it before activation or make unavailable guidance a BLOCKED condition. Ordinary technical implementation choices may remain flexible when every option satisfies the same acceptance criteria.

### Non-goal

Include when adjacent work is likely to tempt the worker or expand the loop.

Examples:

- no unrelated formatter churn;
- no dependency upgrades;
- no redesign of adjacent screens;
- no cleanup of pre-existing warnings outside touched files.

### Follow-up

Exclude from closure when marked optional, future, recommended, stretch, nice-to-have, investigation, or possible enhancement. The worker may record it after satisfying the goal.

## 4. Acceptance-criterion design

### Stable identity

Assign `AC1`, `AC2`, and so on. Stable IDs let the worker report state without rewriting the goal and make progress legible after context compaction.

### Binary outcome

A criterion should describe an end state, not a process.

Weak:

> AC1: Review the networking layer and improve error handling.

Strong:

> AC1: Requests that receive 401, 429, and transport failures return the three specified typed errors, covered by named tests.

### Bounded quantifier

Prefer named sets over open quantifiers.

Weak:

> Handle all edge cases.

Strong:

> Handle empty input, malformed UTF-8, duplicate identifiers, and a 10 MB payload as specified in fixtures A–D.

### Observable proof

Every criterion needs evidence available to the worker and understandable to a separate evaluator. A command name alone is not enough when its output could be ambiguous. Require exit status plus the decisive result, count, threshold, or artifact.

### Independent necessity

Remove criteria that merely restate another criterion or prescribe a step that is not itself an outcome. Too many criteria make the closure set noisy and fragile. Three to seven criteria usually preserve the important distinctions; more than eight usually signals a need to split.

### No mutable tail

Do not end with clauses such as:

- “and anything else required”;
- “and all issues discovered along the way”;
- “until no improvements remain”;
- “plus any necessary cleanup.”

Those phrases erase the boundary you just created.

Mutable queues need the same treatment. Freeze issue, PR, record, warning, or migration membership by explicit IDs, a timestamped snapshot, or an immutable query result. A condition such as “the open queue is empty” can move forever as new items arrive.

## 5. Evidence design

Build a small evidence matrix before drafting:

| Criterion type | Preferred evidence | Avoid |
|---|---|---|
| Bug behavior | named reproduction failing before and passing after, when practical | only a post-fix assertion |
| Behavior | named automated test plus result | “works as expected” |
| Build/integration | exact build command, exit status, relevant target | “project compiles” without command |
| Migration | query/count/invariant before and after | manual confidence |
| Performance | fixed workload, warmup, repeated runs, statistic, threshold | one noisy run |
| Visual/UI | fixed states, viewport/device, screenshots or bounded inspection, accessibility check | “looks polished” |
| API compatibility | compiler fixture, symbol/API diff, consumer build | broad intuition |
| Generated artifact | exact path, schema/content check, reproducibility command | file existence alone |
| Scope | diff summary, changed-file allowlist, no unrelated generated churn | unbounded review |

### Evaluator-visible final evidence

Require the final worker turn to include, at minimum:

- each AC ID and `PASS` or `FAIL`;
- exact validation command or inspection performed;
- exit status or decisive measurement;
- concise output summary;
- artifact paths where relevant;
- remaining blocker if any.

The transcript should contain enough evidence for a small evaluator to make the stop decision without independently inspecting the repository.

### Subjective quality

Convert subjective criteria into a bounded rubric. For example:

```text
AC4: The empty, loading, success, and error states match the supplied design at
390×844 and 1024×768. Proof: capture four named screenshots per viewport; verify
text truncation, focus order, and zero overlap against the listed rubric.
```

For generative or probabilistic systems, combine deterministic gates with a fixed evaluation set and a threshold. State sample size, judge rubric, scoring scale, aggregation, and maximum tolerated regressions.

## 6. Baseline-aware closure

A goal can become impossible when it inherits every failure in a mature repository.

Use this decision order:

1. Run the narrow authoritative checks before changes when practical.
2. Record the baseline result and relevant failure signatures.
3. Run the same checks after changes.
4. Treat new or worsened failures as blockers.
5. Treat unchanged, unrelated baseline failures as non-blocking and surface them.
6. Add broader checks only when they are authoritative for the touched scope.

Do not use baseline policy to excuse failures in changed code or failures that undermine an acceptance criterion.

When baseline capture is expensive or impossible, name a bounded substitute: changed-target tests, a consumer fixture, a migration dry run, or a diff-scoped static check.

## 7. Terminal-state design

### SUCCESS

Write SUCCESS as a conjunction. Do not use “substantially complete,” “good enough,” or “ready for review.” Require all ACs and evidence, then tell the worker to stop immediately. This prevents post-success polishing from keeping the loop alive.

### BLOCKED

A useful blocked clause is specific enough to halt thrashing but not so broad that the worker quits at the first difficulty.

Good blockers:

- inaccessible credential or service that cannot be replaced with a local fixture;
- missing product decision with materially different valid implementations;
- environment failure outside repository control;
- repeated attempts that produce no new evidence or material AC progress;
- absolute loop cap.

A blocked report should make continuation cheap:

```text
BLOCKED
Passed: AC1, AC2
Remaining: AC3
Evidence: [commands/results]
Blocker: [specific fact]
Smallest next action: [one decision, permission, credential, or environment fix]
```

Do not allow “blocked” merely because the first approach failed. The worker should try reasonable alternatives within scope before invoking it.

Native goal states differ by runtime. The worker's final transcript must say `BLOCKED`, not `SUCCESS`, and enumerate the incomplete criteria. Follow the runtime's authority and timing rules for any native status transition; the contract's report outcome does not authorize marking an incomplete objective complete.

## 8. Character-budget strategy

The hard goal-body limit for current Claude Code and Codex goal commands is 4,000 characters. The 3,000-character target is this skill's conservative clarity/headroom heuristic, not a platform limit.

Compress in this order:

1. Delete rationale already present in the source.
2. Delete implementation narration that does not constrain the result.
3. Merge scope statements without weakening them.
4. Put proof inline with each AC.
5. Replace prose with exact paths, commands, IDs, and thresholds.
6. Split into a goal pack before deleting evidence, baseline policy, or terminal clauses.

Never save characters by replacing the acceptance criteria with a pointer to the spec.

## 9. Decomposing a large spec

Split when the source contains multiple independently valuable outcomes, distinct validation regimes, risky migrations, or more closure terms than fit cleanly.

Prefer vertical, proof-carrying milestones:

1. a safe foundation or compatibility seam;
2. one end-to-end behavior slice;
3. bounded remaining variants or migration;
4. integration and release checks.

Avoid horizontal splits such as “write all models,” then “write all views,” when neither milestone can be meaningfully validated.

Each goal should state prerequisites, but its success must be demonstrable without reopening prior goals. The final integration goal checks seams and release invariants; it does not repeat every earlier criterion.

## 10. Anti-pattern rewrites

### Pointer-only completion

Bad:

```text
/goal Implement docs/architecture-v2.md completely. Keep going until every item is done.
```

Rewrite:

```text
Objective: Migrate the three named consumers to Architecture V2.
Inputs: Read docs/architecture-v2.md for intent; only AC1–AC4 define completion.
Done when:
- AC1: Consumer A uses V2 and its named tests pass. Proof: `...`.
- AC2: Consumer B uses V2 and its named tests pass. Proof: `...`.
- AC3: Consumer C uses V2 and its named tests pass. Proof: `...`.
- AC4: No V1 imports remain in the named directories. Proof: `rg ...` returns none.
...
```

### Aspirational quality

Bad:

> Make the feature production-ready, robust, clean, and well tested.

Rewrite “production-ready” into the exact release gates that matter: error cases, compatibility, test commands, telemetry, migration behavior, performance threshold, and explicit exclusions.

### Repository-wide purity

Bad:

> Finish when all tests, warnings, and TODOs in the repository are gone.

Rewrite against a captured baseline and touched scope. Put unrelated debt outside the goal.

### Activity checklist

Bad:

> Read the code, make a plan, implement it, test it, review it, and document it.

Those are execution phases. Replace them with the artifact or behavior that must exist and the evidence that proves it.

### Unbounded optimization

Bad:

> Keep optimizing the prompt until results stop improving.

Rewrite:

```text
AC1: On eval set v3, pass rate is at least 92% across 3 fixed-seed runs and no
protected category drops by more than 1 percentage point from baseline.
Proof: `python eval.py --set v3 --seeds 1,2,3 --json out.json`; surface aggregate
and per-category deltas.
```

### Success-or-blocked ambiguity

Bad:

> The goal is complete when the feature works or you cannot continue.

Rewrite with separately labeled terminal outcomes and require a blocked report that does not claim success.

## 11. Compact example

```text
/goal
Objective: Replace the legacy token cache in AuthKit with the new actor-backed cache without changing its public API.

Inputs: Read `docs/token-cache-migration.md` and `Sources/AuthKit`; they provide implementation context. Only AC1–AC4 below define completion.

Scope: In: AuthKit cache implementation, its tests, and migration notes. Out: authentication-flow redesign, dependency upgrades, and unrelated warning cleanup.

Done when:
- AC1: Existing AuthKit public source compatibility is preserved. Proof: `swift test --package-path Fixtures/AuthKitConsumer` exits 0.
- AC2: Concurrent read/write/expiry behavior passes the named cache tests under Thread Sanitizer. Proof: `xcodebuild ... -enableThreadSanitizer YES test` exits 0 with those tests passing.
- AC3: No production reference to `LegacyTokenCache` remains. Proof: `rg 'LegacyTokenCache' Sources/AuthKit` returns no matches.
- AC4: Migration notes name behavior changes, rollback, and known non-goals. Proof: surface the path and its three headings.

Baseline: Run the two test commands before edits when practical. New or worsened failures block; evidenced unrelated baseline failures do not.

Rules: Keep the public API and scope fixed. Do not add ACs; record optional findings as follow-ups. Surface commands, exit status, concise results, and artifact paths in the final turn.

Terminal outcomes:
- SUCCESS: AC1–AC4 pass with surfaced evidence; stop immediately.
- BLOCKED: Stop without claiming success after unavailable external input, 3 consecutive no-progress turns, or 20 turns. Report passed/remaining ACs, evidence, blocker, and smallest next action.
```

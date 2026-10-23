---
name: compiling-agent-goals
description: "Compile specs, plans, or issues into bounded agent goal contracts with acceptance evidence and stopping conditions. Use proactively when preparing a persistent-agent handoff; this authors the contract, not the implementation."
---

# Compiling Agent Goals

Compile source material into a finite completion contract for a persistent coding-agent loop.

A goal is **not** a compressed spec, implementation plan, backlog, aspiration, or pointer to a large document. A goal defines the smallest stable set of observable facts that lets the harness stop.

## Scope

Use this skill to author, audit, shorten, or split the goal contract itself. Doing the underlying implementation work is a separate request.

A task is usually not goal-shaped when it is:

- a tiny one-turn edit;
- an open-ended backlog, cleanup, research program, or "make it better" request;
- periodic or event-driven work that belongs in a scheduled loop;
- missing the information needed to define observable success;
- primarily a planning exercise whose deliverable is the plan itself.

When explicitly asked for a goal anyway, state the limitation and compile the narrowest honest contract rather than pretending the work is finite.

## Non-Negotiable Model

Use this distinction throughout:

- **Source material** explains intent, constraints, and implementation context.
- **The goal contract** alone defines closure.
- The worker may discover more work; discovery must not silently expand closure.
- Completion requires evidence, not the worker's assertion that the work is done.
- The loop has two honest terminal outcomes: `SUCCESS` and `BLOCKED`.

When a goal points to a spec, include this meaning explicitly:

> Read the referenced material as implementation context. For deciding when to stop, only the finite acceptance criteria in this goal define completion.

Never produce a pointer-only goal such as "Implement everything in SPEC.md."

## Workflow

### 1. Read the Actual Source

Read all user-supplied specs, plans, issues, design documents, repository instructions, and relevant code before drafting. In a repository, inspect the smallest set needed to identify:

- the concrete artifact or behavior to change;
- existing test, build, lint, typecheck, benchmark, migration, or inspection commands;
- compatibility and non-regression constraints;
- known baseline failures or likely unrelated repository debt;
- requirements marked optional, future, recommended, illustrative, or out of scope;
- unresolved product, policy, or rollout decisions that materially change the acceptable result.

Do not invent repository-specific commands when they can be discovered. Do not turn every sentence in a spec into a completion criterion. A technical choice may remain agent-discretion when several implementations satisfy the same contract; a product or policy choice that changes success must become an explicit prerequisite or BLOCKED condition.

If a literal command is unknown but a named authoritative source exists, require the worker to discover the command from that source and surface the exact command it ran. If a decisive validator, threshold, path, or decision remains indeterminate after inspecting available context, do not fabricate it and do not emit a paste-ready `/goal`. Return `Assessment: goal definition blocked` with the smallest missing inputs and, when useful, a clearly labeled non-executable draft.

### 2. Decide Whether This Should Be One Goal

Use one goal only when all of these are true:

1. There is one coherent outcome.
2. Closure can be expressed with at most 8 stable acceptance criteria; 3–7 is preferred.
3. Each criterion has observable proof.
4. The complete contract fits under the hard character limit without deleting closure information.
5. A competent worker can plausibly finish within 30 evaluated goal turns.

Otherwise produce an ordered **goal pack**. Split by independently verifiable milestones, not by arbitrary document sections. Each goal must be useful, safe, and closed on its own. Do not activate multiple goals at once.

### 3. Extract the Frozen Closure Set

Classify source statements before drafting:

- **Required outcome:** observable product, code, data, or behavior that must exist.
- **Invariant:** behavior or compatibility that must remain unchanged.
- **Validation:** command, measurement, artifact, or inspection that proves an outcome.
- **Implementation guidance:** preferred approach; include only when it is a real constraint.
- **Decision prerequisite:** unresolved product, policy, security, or rollout choice whose answer changes the acceptable outcome.
- **Non-goal:** explicitly excluded work.
- **Follow-up:** optional, future, exploratory, or newly discovered work that must not block this goal.

Create stable IDs `AC1`, `AC2`, and so on. Each acceptance criterion must be binary enough that a reviewer can answer pass or fail from surfaced evidence. Prefer outcomes over activities.

Bad criterion:

> AC2: Refactor the parser and investigate edge cases.

Better criterion:

> AC2: Inputs A, B, and C produce outputs X, Y, and Z, covered by the named regression tests.

Do not add, broaden, or reinterpret acceptance criteria after the loop starts. A newly discovered requirement may block the goal only when it is necessary to satisfy an existing criterion, preserve an explicit invariant, or repair a regression caused by the work. Put all other discoveries in follow-ups.

Freeze mutable work queues too. For issues, PRs, warnings, or records, snapshot the IDs or define membership as of a timestamp or immutable query result. "Process all open issues until the queue is empty" is not finite when new items can arrive.

### 4. Bind Every Criterion to Evidence

For each acceptance criterion, name the proof the worker must surface in the conversation transcript. Use one or more of:

- an exact command and its exit status plus concise result summary;
- a named test, test count, benchmark, threshold, or before/after measurement;
- a generated artifact at an exact path plus structural checks;
- a bounded manual or visual inspection with specified cases;
- a diff or repository-state check demonstrating scope and non-regression;
- a deterministic checker plus an explicit qualitative review rubric when judgment is unavoidable.

Do not rely on an evaluator to open files or run commands. Require the worker to expose the decisive evidence in its final turn. For bug fixes, prefer a named reproduction that fails before the change and passes afterward when practical.

For an explicit invariant or proof criterion, use [verifying-invariants](../verifying-invariants/SKILL.md) to scope the boundary and choose the lightest adequate evidence. Name the claim accurately: compiler restrictions, checked constructors, sampled tests, exhaustive finite exploration, and formal proof differ; repeatability does not imply completeness. Use a durable registry only when the user requests a lasting contract or CI needs it; ordinary goals carry a scoped report instead.

For stochastic or performance work, specify the dataset or workload, number of runs, aggregation method, threshold, and failure tolerance. "Looks better" and "performance improves" are not closure conditions.

### 5. Set Baseline and Regression Policy

Unknown repository debt commonly creates infinite goals. Add a baseline rule whenever broad checks may already fail:

- Run relevant checks before editing when practical.
- Failures demonstrably introduced or worsened by this work block success.
- Unrelated pre-existing failures do not block success when they are identified with evidence.
- If a baseline cannot be captured, use the narrowest authoritative checks and state why.

Never require "all tests in the repository pass" unless the baseline is known clean and that breadth is intentional.

### 6. Add Terminal Outcomes and an Escape Hatch

Every goal must say exactly when to stop.

`SUCCESS` requires all acceptance criteria to pass and all decisive evidence to be surfaced. The worker must stop immediately even when additional improvements are possible.

`BLOCKED` ends the loop without claiming success when any of these applies:

- required access, credentials, environment, external service, or user decision is unavailable;
- no new evidence or material progress toward any acceptance criterion occurs for 3 consecutive goal turns;
- the absolute turn cap is reached.

Choose a cap proportional to the milestone: about 10 turns for a localized change, 20 by default, and no more than 30 for one goal. Split the work instead of assigning a larger cap. A blocked report must include completed criteria, remaining criteria, evidence, the blocker, and the smallest external action needed.

`SUCCESS` and `BLOCKED` are report outcomes in this contract, not portable native status names. Include the blocked branch in the terminal contract and label it `BLOCKED` in the transcript so termination is not mistaken for success. Follow the runtime's authority and timing rules for native status transitions; a report label does not authorize marking incomplete work complete.

### 7. Draft the Compact Contract

Start from [assets/goal-template.md](assets/goal-template.md). Keep the goal body at or below 3,000 characters when practical and never above 4,000 characters. The leading `/goal`, surrounding code fence, character-count line, and commentary are not part of the goal body.

Keep only information that changes execution or closure. Prefer literal file paths, commands, thresholds, and criterion IDs over explanation.

For a multi-turn goal, optionally require a short progress file such as `.agent/goal-status.md`. It may record fixed criterion states, evidence, decisions, and follow-ups, but it must never create new acceptance criteria or become an additional completion requirement.

### 8. Lint and Revise

Save only the goal body to a temporary file. Resolve the linter path relative to this skill's `SKILL.md`, not the project working directory, then run it with Python 3.9 or newer:

```bash
python3 /absolute/path/to/compiling-agent-goals/scripts/lint_goal.py /path/to/goal.txt
```

The linter is heuristic. Fix all errors, review every warning, then perform a semantic check:

- Can a separate evaluator determine completion from the transcript alone?
- Is there exactly one outcome?
- Is the closure set finite and frozen?
- Does every criterion have proof?
- Can unrelated baseline debt keep the loop alive?
- Does the worker know when to stop successfully and when to stop blocked?
- Would deleting the source document still leave a comprehensible closure contract?

Run the linter again after edits.

## Goal Packs

When source material is too large, produce an ordered pack with these rules:

1. Each goal has one demonstrable milestone and its own SUCCESS/BLOCKED exits.
2. Later goals may depend on artifacts from earlier goals but must not reopen their scope absent a regression.
3. Acceptance criteria do not overlap across goals except for explicit integration checks.
4. Put migration, rollout, and cleanup in separate goals when they have distinct risk or evidence.
5. Make the final goal an integration or release-readiness contract, not "review everything again."
6. State prerequisites outside each paste-ready body unless the worker needs them to execute correctly.

When the user asks for a single goal but the source cannot close safely as one, produce the pack and explain the split in one sentence.

## Output Contract

Unless the user requests another format, return:

1. `Assessment: single goal`, `Assessment: goal pack (N)`, `Assessment: not goal-shaped`, or `Assessment: goal definition blocked`.
2. One paste-ready fenced block per goal, beginning with `/goal` followed by the complete inline contract.
3. `Characters: N / 4000` for each goal body, using the linter's count.
4. At most a short assumptions or split-rationale note outside the goal blocks.

Do not bury required closure information in commentary outside the block. Do not tell the user to run `/goal Complete GOAL.md`; a saved goal document is for editing or copying, not a substitute for putting the finite contract into the harness.

When auditing an existing goal, return the revised paste-ready goal first, followed by only the material changes and remaining warnings.

## Reference Map

Load only what the current step needs:

- [Goal contract](references/goal-contract.md): the compilation model, evidence design, decomposition rules, and anti-pattern rewrites. Read it when source material is long, ambiguous, multi-milestone, or likely to produce a non-terminating loop.
- [Platform notes](references/platform-notes.md): documented Claude Code and Codex goal behavior, limits, and packaging. Read it when targeting one harness specifically.
- [Single-goal template](assets/goal-template.md): the paste-ready body for one goal.
- [Goal-pack template](assets/goal-pack-template.md): the ordered body set when decomposition is required.
- `scripts/lint_goal.py`: deterministic structural checks and character counting.

Before returning a goal, confirm the linter reports no errors, every acceptance criterion carries proof, and both terminal outcomes are labeled.

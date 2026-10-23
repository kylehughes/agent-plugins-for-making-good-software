# Substantive workflow

Use this reference only after the entry point selects the substantive path. Continue with its frozen scope and auditor set.

Run the five phases below: audit, decide, fix, compile checkpoint, and re-audit. Obtain completed findings before fixing.

For a changed construction boundary, invariant claim, enforcement gap, legal transition, or explicit proof request, load [verifying-invariants](../../verifying-invariants/SKILL.md). Complete its semantics-owner selection before boundary judgments or edits: record the selected companion and its successful or reused activation, or confirmed absence after checking available skill descriptions. This activation record is a prerequisite for boundary work, not a final-report reminder. Reuse active guidance within this workflow.

Before editing, allocate a fresh temporary directory outside the repository using a temporary-directory allocator (`mktemp -d` where available, or the runtime's equivalent). Use the allocator's returned path for every capture; never invent a supposedly unique name, reuse an existing directory, or use `mkdir -p` for this evidence. Capture the initial owned-work diff and pre-edit contents of owned dirty or untracked files there; include only artifacts created for this task. Give compatibility reviewers the exact retained contents needed for their comparison as inline task context. The scratch path identifies provenance; it does not grant the reviewer file access. If more initial context is needed, supply it from the capture in the same review. Do not ask a reviewer to work around a denied read through another tool. Conversation memory alone does not supply a child reviewer with overwritten contents. Capture any newly affected path before its first edit. The clean base identifies ownership. The initial working tree supplies pre-hardening behavior for comparison, including work not yet committed. It is evidence of prior behavior, not authority to preserve defects; authoritative requirements decide which behavior must remain. Keep this scoped evidence for the task, not as a maintained registry.

Surfaces the branch does not implicate stay untouched. Defer owned work that requires app-wide rearchitecture or a product decision only the user can make.

**By default, this path runs one compile checkpoint, not a verification pass.** Apply the entry point's project-companion requirements: explicit checks required during hardening run in this pass; checks assigned to the later ship gate remain there.

## Dispositions

Every finding gets one. Do not dismiss a finding because it seems low priority, and do not treat every finding as permission to rewrite the branch.

| Disposition | Meaning | Action |
|---|---|---|
| Mechanical fix | A codified rule determines exactly one correct outcome. | Fix automatically. |
| Judgment fix | The branch owns the thread and project evidence supports a best answer among several valid ones. | Resolve from evidence, fix, record in the decision ledger. |
| Defer | Completing the thread would tear up floorboards across the whole app, or needs a product decision only the user can make. | Record with full context for the handoff. |
| Drop | Vague, speculative, or grooming of code the branch does not own. | Record the exclusion and rationale in the internal ledger. |
| Blocker | Cannot be safely prepared without resolving a correctness, build, or architecture issue that exceeds this loop. | Attended: stop and ask. Unattended: report in the handoff. |

Mechanical fixes are never optional. Judgment fixes are not put to the user mid-loop — pick the strongest-evidence option, apply it, and report the call in the handoff where it can be audited. Effort is not a defer criterion: large but branch-owned work is still fix-now work.

## Finding Classification

Walk this in order:

1. **Ledger check.** Does the decision ledger already hold this file path and underlying concern? On a match the finding is settled: keep the prior disposition. Override only on concrete new evidence — a build failure, a demonstrated defect in an applied fix — never on an alternative preference.
2. **Ownership test.** Does the branch own the thread? It does when its changes introduce, extend, or destabilize the state the finding names. Pre-existing drift in untouched code is not owned: **Drop**.
3. **Concreteness test.** Can the finding name a concrete problem, affected code, and next action? If not: **Drop**.
4. **Floorboards test.** Would completing it rearchitect a pattern across many unrelated features or packages, or require a product decision? PR safe to merge without it: **Defer**. PR unsafe or misleading without it: **Blocker**.
5. **Fix now.** Exactly one codified outcome: **Mechanical fix**. Multiple valid outcomes: **Judgment fix**.

When in doubt between mechanical and judgment, choose judgment. When in doubt between fix-now and defer, fix now.

Mechanical fixes include symbol and import ordering, formatting, documentation voice, naming-pattern and localization-pattern fixes codified by the project, access control corrections, and file structure ordering.

Deferrals need the handoff fields recorded while context is fresh: **Title** (3-8 words), **Why** (the concrete risk), **Scope** (why it exceeds this PR), **Work** (first step and affected modules), **Effort** (`S` <1h, `M` half day, `L` 1-2 days, `XL` larger), **Evidence** (auditor plus file, symbol, or rule).

## Run Modes

Resolve everything resolvable from project evidence before stopping. An attended run interacts at exactly two points: a blocker, and the exit offer to file deferred work in the project's issue tracker, when one is configured. An unattended run makes neither stop — it reports blockers in the handoff with `Status: Blocked` and records deferred work without offering to file it.

When hardening is one stage of an enclosing workflow, the filing offer belongs at that workflow's final handoff. Return the stage result and continue the enclosing workflow's remaining checks before making the offer.

Translate the workflow onto the current runtime rather than treating tool names literally. The finding ledger lives in orchestrator state. Auditors return findings as text in their final report — subagents receive a reduced tool set and cannot be relied on to create tasks or invoke skills by name, so the orchestrator collects and records. Use the runtime's native subagent mechanism for auditors; if it does not expose the named agents, pass the matching agent definition as prompt context.

Where the runtime provides cheaper delegated workers, bounded mechanical slices can go to them once the orchestrator fixes file scope and acceptance criteria. Workers do not build or run the project; every worker prompt names its working directory explicitly and quotes space-containing paths.

## Workflow

### Phase 1: Audit

Use the mode and frozen surface from the initial inspection. Display the surface, including file lists for untracked directories, so auditors can inspect new files.

Launch the implicated auditors in parallel against the surface. The roster is a set of concerns, not a fixed list of names. This plugin supplies four:

| Agent | Question |
|---|---|
| `code-reviewer` | Does this fit the architecture? |
| `code-simplifier` | Could this reuse what exists, and does it waste work? |
| `correctness-reviewer` | Does this behave correctly on real paths? |
| `technical-writing-auditor` | Does this match the human voice? |

Platform plugins and projects commonly add reviewers for concerns such as codified standards compliance, type-system enforcement, complexity and cognitive load, and async-test determinism. Launch every installed reviewer agent whose concern the surface implicates; record the concerns you had no reviewer for.

Apply the opening scope, companion requirements, and activation rules to the auditor contracts. Investigate domain values and legal transitions introduced, altered, or newly exposed by substantive changes. Consider a stronger representation when it prevents concrete misuse at a justified complexity cost. This adds no reviewer or verification loop: Phase 4 owns the default compile checkpoint, and project instructions determine when their additional checks run.

Pass this contract to every auditor, filling the compatibility input for any reviewer assessing changed behavior:

```text
Audit the changed meaning within the chosen surface. Check a new or strengthened behavioral claim against relevant implementation evidence; a wording-only edit does not authorize tracing the surrounding model for pre-existing defects. Report only issues introduced, extended, or destabilized by the owned change. In branch mode, use the base-branch diff plus any uncommitted working-tree edits. In working-tree mode, use git status --short, git diff HEAD --find-renames=20%, and direct reads of untracked files. If this launch names an explicit scoped file list, audit only those files.

Compatibility evidence: [exact retained initial-work contents needed for this comparison, with capture path for provenance and authoritative preservation requirements; none when this reviewer does not assess changed behavior]. The base diff establishes ownership; compare pre-hardening behavior using this supplied evidence, including uncommitted work. Do not infer the initial working tree from the final diff or treat prior defects as requirements. Request missing captured contents from the caller; do not read its scratch directory.

Remain read-only. Do not modify files and do not build, test, or run the project. Recommend the narrowest relevant verification command to the orchestrator instead.

For each finding, include: file:line, concern, proposed fix, expected disposition, patch boundary, and the skill, project rule, or architectural pattern that supports it.

Return scoped findings in one list. Each finding must identify the owned change that gives rise to it. You may suggest a disposition; the orchestrator owns final classification.
```

Auditors do not propose Drop — an auditor that believes a finding is not worth reporting omits it. All launched auditors must complete; re-launch any that fails rather than proceeding with missing results.

Collect the scoped findings into the ledger. If a reviewer submits an excluded observation, record its rejection internally without investigating a repair. Deduplicate by underlying failure, including findings across files or concern labels: an invariant bypass and a type-based way to prevent it share one finding and disposition. Correctness owns the failure evidence and impact; the type specialist supplies representation choices and tradeoffs; the orchestrator decides the fix. Preserve distinct failures as distinct findings. Close completed auditor sessions if the runtime keeps them active.

### Phase 2: Decide

Classify each finding through the procedure above. Record ledger entries for deferrals, drops, and blockers, and mark them resolved so they do not count as open work. For each judgment fix, write a ledger entry naming the choice, the strongest alternative, and the rationale — this anchors the decision so re-audits do not flip between valid designs.

Print a short summary of the fix-now work. This is informational, not a checkpoint.

### Phase 3: Fix

Fix every mechanical and judgment finding, grouped by file, each patch inside its stated boundary. Low-ambiguity slices can go to delegated workers once files and acceptance criteria are fixed. Mark each finding complete as it lands, and confirm zero open actionable findings before continuing.

### Phase 4: Compile Checkpoint

Run the default compile checkpoint **once**, after the first substantive fix batch, and only if the fixes touched source code, package manifests, or project files. Hardening can introduce failures that static analysis cannot see — public API changes, access control, concurrency isolation, package boundaries — and this is where they surface. Explicit project requirements may also require commands when no fixes were needed or at another point in this pass; follow their timing.

Use the narrowest command that compiles the full dependent graph of the touched modules — a whole-app or whole-workspace build, or the unit-test build when test targets changed. **Not an incremental, changed-module-only build**: it does not compile the changed module's dependents, which is precisely where the failures this checkpoint exists to catch appear. The incremental build is the iteration loop; the checkpoint needs the graph.

Purely mechanical iterations — formatting, ordering, whitespace — skip the default compile checkpoint. A project-required check that already compiles the required dependent graph on the same artifacts satisfies it; do not add a duplicate build. Once the checkpoint passes, later audit fixes do not restart it except for the compiler-caused repair below. Carry other verification obligations, including invariant rechecks, to the project ship gate unless explicit project requirements call for them during hardening. Keep required hardening-check results current under the entry point's reuse and rerun rules.

On default compile-checkpoint failure:

- **Clearly caused by a just-applied fix**: make the smallest repair inside the accepted patch boundary, re-run that command once, and give the repair a **scoped re-audit** through the owning auditor. A compiler-driven repair is still a change; it does not bypass audit.
- **Ambiguous, unrelated, or in a package the branch did not touch**: stop and report it as a blocker. Do not start editing packages the branch does not own to make a build pass.

For a failed project-required hardening step, classify an owned defect through the existing dispositions, repair it in the same loop, and rerun the affected check. An environmental obstacle, unavailable command, or failure outside the owned thread is a blocker; do not silently move a required hardening step to the later ship gate or repair unrelated code to make it pass.

Also run the cheap deterministic checks the surface requires:

- Always: `git diff --check HEAD --find-renames=20% -- <owned-paths>`, applying the entry point's scope guard to unrelated edits within those files. Do not run an unrestricted check when no tracked paths are owned.
- Agent configuration changed (skills, agents, runtime settings) → run the project's validation script for that configuration, when it ships one.
- Scripts or tooling changed → run the project's tooling tests, when it has them; nothing else runs them, so a tooling-only branch is otherwise unverified.
- Working-tree mode → enumerate untracked files with `git ls-files --others --exclude-standard -z`, filter to the owned surface, then scan owned text files for trailing whitespace and missing final newlines.

If the diff fires a maintenance trigger the repository declares for an architecture or design document, confirm that document updated on this branch; a missing update is a fix-now judgment finding, not a defer.

### Phase 5: Re-Audit

Include owned outputs of companion preparation and generation in this review, using their retained pre-command contents. Inspect the output changes for correctness without expanding the frozen surface to unrelated parts of their files. Finish required hardening checks before preparing the final handoff; later fixes that invalidate those results require the affected checks again within this workflow.

Include the retained initial compatibility evidence in every applicable re-audit's contract, alongside the final artifacts. If `verifying-invariants` was loaded, write the complete intended final response to a draft file in the allocated scratch directory after fixes and checkpoint evidence are stable. Read [Manager handoff](manager-handoff.md) now and copy its final review request, inserting the draft file's exact contents inline along with the retained initial comparison contents, final artifact locations, and actual check evidence. The reviewer receives the complete text without needing access to the caller's scratch directory. Do not substitute selected claims or an earlier conversational draft. One completed review covers both the changes and the handoff. An **Incomplete final claim review** requires supplying the named missing input to the same reviewer; it is not a completed review. If findings cause further changes, update the draft and evidence before the final review; a stale draft does not cover the final handoff.

Return to Phase 1, scoped by what changed:

- Surface materially unchanged since the last completed audit → reuse that scoped code-audit result rather than rerunning auditors.
- Fixes introduced new abstractions, touched package boundaries, or spanned multiple concern areas → full pass.
- Otherwise → only the files changed since the last audit, through only the owning auditors.
- Exclusively trivial mechanical fixes → exit without re-auditing.
- An auditor returning no findings is a valid result. Do not invent work to justify the audit.

If `verifying-invariants` was loaded in this workflow, the final handoff claim check is mandatory even after mechanical fixes. Reuse satisfies that check only if the completed review covered the same final artifacts, evidence, and complete response draft; an earlier code audit normally did not.

## Termination

**Convergence is the exit condition.** The loop ends when the most recent audit returns zero actionable findings after classification. Iteration count is not an exit condition: if actionable findings persist after several passes, present the disposition table for all findings across all iterations and **stop without declaring completion** — attended, the user decides whether to continue, broaden scope, or accept; unattended, render the table with `Status: Needs decision`.

### Final Manager Handoff

Complete [Manager handoff](manager-handoff.md) at convergence. If `verifying-invariants` was loaded in this workflow, resolve the records from the completed correctness review and emit the final handoff under the invariant skill's correction rules. Otherwise prepare the scoped handoff directly.

## Decision Ledger

A running record in conversational state, not a file. Three entry types — **Deferred** (surface, concern, rationale, handoff fields), **Dropped** (surface, concern, one-line rationale), and **Judgment call** (surface, choice, strongest alternative, rationale).

The ledger accumulates across iterations and settles decisions: a re-audit finding that matches an entry keeps its prior disposition, so the loop neither re-litigates a deferral nor flips an applied judgment call between valid designs. The only escape is concrete new evidence. Mechanical findings never enter the ledger; codified rules cannot be deferred or dropped.

Before finishing, apply the [Manager handoff completion checklist](manager-handoff.md#completion-checklist) to the handoff and retained evidence.

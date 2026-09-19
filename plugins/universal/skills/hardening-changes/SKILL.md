---
name: hardening-changes
description: "Harden an owned branch or working tree for a PR through an audit-and-fix loop. Use for PR preparation or requested change-set hardening, not a read-only review of someone else's work."
---

# Hardening Changes

Run an audit-fix loop before pull request creation: make the work safer, simpler, and more correct, and leave every subsystem it touches whole. The size of the result is bounded by the thread the branch owns, not by a review budget; where the project has reviewers, the handoff carries every judgment call so review effort lands on decisions rather than mechanics.

Two boundaries hold:

- Surfaces the branch does not implicate stay untouched. Completeness never means consistency grooming of unrelated working code.
- Work that would tear up floorboards across the whole app, or that needs a product decision only the user can make, is deferred — not attempted.

**This skill runs one compile checkpoint, not a verification pass.** The project's own ship gate — its full build, test, and release checks — runs after this skill and is the project's responsibility; this skill does not substitute for it.

## Dispositions

Every finding gets one. Do not dismiss a finding because it seems low priority, and do not treat every finding as permission to rewrite the branch.

| Disposition | Meaning | Action |
|---|---|---|
| Mechanical fix | A codified rule determines exactly one correct outcome. | Fix automatically. |
| Judgment fix | The branch owns the thread and project evidence supports a best answer among several valid ones. | Resolve from evidence, fix, record in the decision ledger. |
| Defer | Completing the thread would tear up floorboards across the whole app, or needs a product decision only the user can make. | Record with full context for the handoff. |
| Drop | Vague, speculative, or grooming of code the branch does not own. | Record the drop and its rationale. |
| Blocker | Cannot be safely prepared without resolving a correctness, build, or architecture issue that exceeds this loop. | Attended: stop and ask. Unattended: report in the handoff. |

Mechanical fixes are never optional. Judgment fixes are not put to the user mid-loop — pick the strongest-evidence option, apply it, and report the call in the handoff where it can be audited. Effort is not a defer criterion: large but branch-owned work is still fix-now work.

## Scope Guard

- **Branch mode**: working tree clean → audit the diff from the base branch (usually `main`; confirm from repository context) to `HEAD`.
- **Working-tree mode**: uncommitted or untracked changes exist → audit the working tree via `git status --short`, `git diff HEAD --find-renames=20%`, and direct reads of untracked files.

If the committed diff against the base branch is empty but the tree is dirty, working-tree mode is required. Never report a clean branch from an empty committed diff while uncommitted work exists.

The audit surface determines where findings come from, not where fixes stop. A fix extends as far as the thread the branch owns requires, including files outside the surface — updating a generated registration file after adding a test target, adopting a type the branch introduced in the sibling subsystems the work implicates. The boundary is ownership, not size.

**The surface is frozen at Phase 1 and does not ratchet.** A completion edit outside it is audited for the correctness of that edit; the file it landed in does not become newly owned territory to mine for unrelated findings. Without this, each iteration enlarges what the next one audits — a fix reaches into a neighboring package, that package enters the next surface, its own drift produces fresh findings — and the loop cannot converge. Adopting the type you introduced in a sibling subsystem is in scope. Auditing that sibling's test suite because you touched a file near it is not.

Also freeze the auditor set to the surface's content. A diff with no code gives the language-specific auditors nothing to answer; launching them costs a subagent context for a guaranteed-empty result. Launch the auditors whose concerns the surface actually implicates and record which you skipped and why.

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

Translate the workflow onto the current runtime rather than treating tool names literally. The finding ledger lives in orchestrator state. Auditors return findings as text in their final report — subagents receive a reduced tool set and cannot be relied on to create tasks or invoke skills by name, so the orchestrator collects and records. Use the runtime's native subagent mechanism for auditors; if it does not expose the named agents, pass the matching agent definition as prompt context.

Where the runtime provides cheaper delegated workers, bounded mechanical slices can go to them once the orchestrator fixes file scope and acceptance criteria. Workers do not build or run the project; every worker prompt names its working directory explicitly and quotes space-containing paths.

## Workflow

### Phase 1: Audit

Run `git status --short` and `git diff --name-only <base>...HEAD`, choose the mode, and display the surface. For untracked directories include the file list so auditors can inspect new files.

Launch the implicated auditors in parallel against the surface. The roster is a set of concerns, not a fixed list of names. This plugin supplies four:

| Agent | Question |
|---|---|
| `code-reviewer` | Does this fit the architecture? |
| `code-simplifier` | Could this reuse what exists, and does it waste work? |
| `correctness-reviewer` | Does this behave correctly on real paths? |
| `technical-writing-auditor` | Does this match the human voice? |

Platform plugins and projects commonly add reviewers for concerns such as codified standards compliance, type-system enforcement, complexity and cognitive load, and async-test determinism. Launch every installed reviewer agent whose concern the surface implicates; record the concerns you had no reviewer for.

Pass this contract to every auditor:

```text
Audit the chosen surface. In branch mode, use the base-branch diff plus any uncommitted working-tree edits. In working-tree mode, use git status --short, git diff HEAD --find-renames=20%, and direct reads of untracked files. If this launch names an explicit scoped file list, audit only those files.

Remain read-only. Do not modify files and do not build, test, or run the project. Recommend the narrowest relevant verification command to the orchestrator instead.

For each finding, include: file:line, concern, proposed fix, expected disposition, patch boundary, and the skill, project rule, or architectural pattern that supports it.

You may suggest a disposition, but the orchestrator owns final classification. Put app-wide rearchitecting and product decisions in a "Deferral Candidates" section.
```

Auditors do not propose Drop — an auditor that believes a finding is not worth reporting omits it. All launched auditors must complete; re-launch any that fails rather than proceeding with missing results.

Collect every finding, including Deferral Candidates, into the ledger. Deduplicate: if two auditors flagged the same file and concern, keep the finding from the auditor that owns that concern and remove the duplicate. Close completed auditor sessions if the runtime keeps them active.

### Phase 2: Decide

Classify each finding through the procedure above. Record ledger entries for deferrals, drops, and blockers, and mark them resolved so they do not count as open work. For each judgment fix, write a ledger entry naming the choice, the strongest alternative, and the rationale — this anchors the decision so re-audits do not flip between valid designs.

Print a short summary of the fix-now work. This is informational, not a checkpoint.

### Phase 3: Fix

Fix every mechanical and judgment finding, grouped by file, each patch inside its stated boundary. Low-ambiguity slices can go to delegated workers once files and acceptance criteria are fixed. Mark each finding complete as it lands, and confirm zero open actionable findings before continuing.

### Phase 4: Compile Checkpoint

Run this **once**, after the first substantive fix batch, and only if the fixes touched source code, package manifests, or project files. Hardening can introduce failures that static analysis cannot see — public API changes, access control, concurrency isolation, package boundaries — and this is where they surface.

Use the narrowest command that compiles the full dependent graph of the touched modules — a whole-app or whole-workspace build, or the unit-test build when test targets changed. **Not an incremental, changed-module-only build**: it does not compile the changed module's dependents, which is precisely where the failures this checkpoint exists to catch appear. The incremental build is the iteration loop; the checkpoint needs the graph.

Purely mechanical iterations — formatting, ordering, whitespace — skip this phase.

On failure:

- **Clearly caused by a just-applied fix**: make the smallest repair inside the accepted patch boundary, re-run that command once, and give the repair a **scoped re-audit** through the owning auditor. A compiler-driven repair is still a change; it does not bypass audit.
- **Ambiguous, unrelated, or in a package the branch did not touch**: stop and report it as a blocker. Do not start editing packages the branch does not own to make a build pass.

Also run the cheap deterministic checks the surface requires:

- Always: `git diff --check HEAD --find-renames=20%`.
- Agent configuration changed (skills, agents, runtime settings) → run the project's validation script for that configuration, when it ships one.
- Scripts or tooling changed → run the project's tooling tests, when it has them; nothing else runs them, so a tooling-only branch is otherwise unverified.
- Working-tree mode → scan untracked text files for trailing whitespace and missing final newlines:

```bash
git ls-files --others --exclude-standard -z | xargs -0 grep -nIE '[ \t]+$' -- || true
git ls-files --others --exclude-standard | while IFS= read -r f; do
  [ -s "$f" ] && [ -n "$(tail -c 1 "$f")" ] && echo "$f: missing final newline"
done
```

If the diff fires a maintenance trigger the repository declares for an architecture or design document, confirm that document updated on this branch; a missing update is a fix-now judgment finding, not a defer.

### Phase 5: Re-Audit

Return to Phase 1, scoped by what changed:

- Surface materially unchanged since the last completed audit → reuse that result rather than rerunning auditors.
- Fixes introduced new abstractions, touched package boundaries, or spanned multiple concern areas → full pass.
- Otherwise → only the files changed since the last audit, through only the owning auditors.
- Exclusively trivial mechanical fixes → exit without re-auditing.
- An auditor returning no findings is a valid result. Do not invent work to justify the audit.

## Termination

**Convergence is the exit condition.** The loop ends when the most recent audit returns zero actionable findings after classification. Iteration count is not an exit condition: if actionable findings persist after several passes, present the disposition table for all findings across all iterations and **stop without declaring completion** — attended, the user decides whether to continue, broaden scope, or accept; unattended, render the table with `Status: Needs decision`.

### Final Manager Handoff

Optimize for someone who did not watch the implementation — a reviewer or the author later — reading on a phone, deciding the next action in under a minute. Use file paths, symbols, and package names rather than abstract labels.

Open with the status block. These four fields really are one line each:

```text
Status: [Ready | Needs decision | Blocked].
Next: [continue with X | track deferred work in the issue tracker | no action needed | blocked on Z].
Changed: [one line, 1-3 short bullets, or "No code changes were needed."]
Proof: [compile checkpoint result, or "none needed — mechanical only"].
```

**Everything after the status block is prose. Write complete sentences.** Terse means no padding, not no grammar. A decision that needs two sentences gets two sentences. Compressing one into a dense line with em dashes standing in for verbs produces something nobody can read, which defeats the entire point of the handoff.

Do not chain slots with em dashes, write label-colon fragments where a sentence belongs, use semicolon lists, or restate the section heading in the line beneath it.

The difference, on a real decision:

> **Good.** I changed how the audit surface grows. Before, a fix could reach into a file outside the audited set, and the next round then audited that file for new problems, so every round enlarged the area under audit. Fixes can still reach outside the set, but those files no longer become fair game for new findings.

> **Bad.** `hardening-changes` surface — froze at Phase 1 over letting fixes ratchet the next iteration's territory.

Same decision. The second one is unreadable.

Use these sections only when they have content:

**Judgment Calls.** Every judgment fix, so the reviewer or author can audit the call after the fact. Say what you changed and why. Name the alternative only where a reader would otherwise assume you never considered it.

**Must Fix or Decide Before Merge.** Blockers and anything the project's ship gate still has to prove. Give the risk, the specific next action, and the evidence behind it. While this section has content, do not imply the PR is ready.

**Deferred Work.** Only work that passed the floorboards test — most runs have none, and at most 6 appear. Each item needs its impact, why it exceeds this PR, the first implementation step and the modules it touches, rough effort (`S`/`M`/`L`/`XL`), and the finding it came from. Write that as a short paragraph rather than a field list. Omit any item that cannot supply all of it.

**Not Carried Forward.** Optional. What an auditor raised that you fixed, dropped, or judged not worth tracking, and why.

In attended runs, when the project has an issue tracker configured, offer to file the deferred work once — at most 6 options, each with a 1-5 word label and a description naming problem, impact, effort, and scope reason.

## Decision Ledger

A running record in conversational state, not a file. Three entry types — **Deferred** (surface, concern, rationale, handoff fields), **Dropped** (surface, concern, one-line rationale), and **Judgment call** (surface, choice, strongest alternative, rationale).

The ledger accumulates across iterations and settles decisions: a re-audit finding that matches an entry keeps its prior disposition, so the loop neither re-litigates a deferral nor flips an applied judgment call between valid designs. The only escape is concrete new evidence. Mechanical findings never enter the ledger; codified rules cannot be deferred or dropped.

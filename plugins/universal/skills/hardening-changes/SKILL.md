---
name: hardening-changes
description: "Harden an owned branch or working tree for a PR through an audit-and-fix loop. Use for PR preparation or requested change-set hardening, not a read-only review of someone else's work."
---

# Hardening Changes

Prepare the owned changes through one of the two paths below. The orchestrator owns fixes and dispositions; installed reviewers supply completed audits. Do not replace available reviewers with self-review because the patch is small. If delegation is unavailable, record that limit and perform the same scoped review directly.

## Scope Guard

Inspect `git status --short` first, then select the scope:

- **Branch mode**: working tree clean → audit the diff from the base branch (usually `main`; confirm from repository context) to `HEAD`.
- **Working-tree mode**: uncommitted or untracked changes exist → audit the working tree via `git status --short`, `git diff HEAD --find-renames=20%`, and direct reads of untracked files.

If the committed diff against the base branch is empty but the tree is dirty, working-tree mode is required. Never report a clean branch from an empty committed diff while uncommitted work exists.

The audit surface determines where findings come from, not where fixes stop. A fix extends as far as the thread the branch owns requires, including files outside the surface — updating a generated registration file after adding a test target, adopting a type the branch introduced in the sibling subsystems the work implicates. The boundary is ownership, not size.

**The surface is frozen at the initial inspection and does not ratchet.** A completion edit outside it is audited for the correctness of that edit; the file it landed in does not become newly owned territory to mine for unrelated findings. Without this, each iteration enlarges what the next one audits — a fix reaches into a neighboring package, that package enters the next surface, its own drift produces fresh findings — and the loop cannot converge. Adopting the type you introduced in a sibling subsystem is in scope. Auditing that sibling's test suite because you touched a file near it is not.

Also freeze the auditor set to the surface's content. A diff with no code gives the language-specific auditors nothing to answer; launching them costs a subagent context for a guaranteed-empty result. Launch the auditors whose concerns the surface actually implicates and record which you skipped and why.

## Choose the Path

Route from the request and the changed hunks before choosing reviewers or reading implementation details. Determine whether the user wants to preserve meaning or change an asserted fact or contract.

- **Wording-only:** Every changed hunk is prose or comments, and the request is for wording, clarity, or cleanup. Preserve the old meaning while improving its expression. An accidental new or stronger claim is a prose defect to correct, not authority to investigate or change implementation. Follow the wording-only path and finish there.
- **Substantive:** Code, configuration, or an intended contract changes; the request says the prose records a factual or behavioral change; or the user requests a truth audit or invariant assessment. Check the scoped claims against authoritative requirements and implementation evidence. An explicitly requested whole-document truth audit includes existing claims in that document and takes precedence over wording-only routing.

If a mixed request includes a stated factual or contract change in any hunk, take the substantive path. If the request gives no editing intent, use the changed meaning to select the path. A reviewer's interpretation of wording alone does not change a selected meaning-preservation task into a truth audit. The surrounding unchanged model does not activate a broader audit; claims behaviorally affected by substantive changes remain within the owned thread.

Use only these `Status` values: **Hardening complete** means this scoped stage converged and required reviews finished; **Needs decision** names an unresolved disposition; **Blocked** names an obstacle preventing completion. Pending project checks belong in `Next`.

## Wording-only Path

1. Identify the requested editing improvement, then fill and send the reviewer request below to the technical-writing reviewer. Copy its contract rather than summarizing it; supply old and new text, locations, and only necessary prose context. The caller owns delivering the improvement; the reviewer assesses meaning preservation. Do not read implementation or launch code/type reviewers for this path.
2. Obtain the completed review and apply justified edits to the **new** text, changing only the words responsible for each material difference. Retain other improvements even within the same phrase. If a replacement removes wording its rationale does not address, ask the same reviewer once to localize the correction. A whole-text row is valid when it corrects one inseparable meaning difference. Resolve editorial judgment within the task; reject unrelated implementation observations and follow-ups internally.
3. Check delivery separately from resolving findings: does the corrected text still achieve the requested improvement? A result identical to the old text has delivered no cleanup. If the corrected text no longer achieves the editing intent and the original still admits a useful meaning-preserving improvement, draft one fresh formulation from the old meaning that achieves the editing goal and avoids the reviewer's stated difference. Send it to the same reviewer under the same contract, including the prior finding as prose context, then apply justified corrections. Allow one fresh-formulation review, not repeated attempts. If no accepted improvement remains, retain the meaning-preserving text and report the undelivered cleanup; do not invent a change merely to leave a diff. A one-word factual label, for example, may appropriately return to its original form.
4. Run `git diff --check HEAD --find-renames=20%` and any project-required document/configuration validation. Inspect untracked text when present. A comment edit remains wording-only regardless of its file extension: skip compilation and project execution.
5. Finish with `Status`, `Next`, `Changed`, and `Proof`, followed by one sentence on the scoped prose-review result. Explain corrections and any fresh formulation in `Changed`. If the bounded attempt leaves the requested improvement undelivered, use **Needs decision** and name the editing objective and reviewer's stated difference in `Next`. Report observed results; include setup details only when they affect the next action. State that compilation was unnecessary and name any ordinary project gate still pending. Do not describe or speculate about code outside the changed text. Stop here. Do not load the substantive workflow or manager handoff; their loop, ledger, deferral sections, and invariant handoff do not apply.

### Reviewer request

```text
Perform a read-only meaning-preservation review. The new text is the editing base; the old text constrains meaning. Judge the claim as a reasonable reader would understand it in context. A merely possible implication is not a stronger guarantee, and preference for the old style is not a finding. Accept ordinary paraphrases.

Return Accepted with a brief rationale, or a list of minimal edits with these fields:
Location | Current words in the new text | Replacement words | Material difference corrected

For each edit, identify the shortest span responsible for the difference and change only those words. Preserve independent improvements, including other changed words in the same phrase. Do not return an unlocalized whole-passage rewrite or replace unaffected wording with the old style. A row may cover the entire supplied text when it is one atomic meaning difference and no independent improvement survives. If every change must be undone, account for each independently in the edit list.

Keep untouched text unchanged. Do not assess whether either version is true, inspect implementation, add severity labels, or propose implementation follow-ups. Return only the acceptance or edit list with its rationale.

Location and necessary prose context: [fill]
Requested editing improvement: [fill]
Old text: [fill]
New text: [fill]
```

## Substantive Path

Read [Substantive workflow](references/substantive-workflow.md) and [Manager handoff](references/manager-handoff.md) after selecting this path. Continue with the frozen surface and auditor set through audit, decide, fix, compile checkpoint, and re-audit, then complete the handoff.

## Reference Map

Read the two references only for the substantive path:

- [Substantive workflow](references/substantive-workflow.md): load after code, configuration, contracts, changed behavioral claims, or an explicit truth/invariant assessment selects the substantive path. Contains dispositions, auditor contracts, phases, ledger, and termination.
- [Manager handoff](references/manager-handoff.md): load with the substantive workflow so its evidence requirements are available before editing and its complete draft is available for final claim review. The wording-only path does not load it.

Before finishing the wording-only path, check its five steps above. Before finishing the substantive path, apply the [Manager handoff completion checklist](references/manager-handoff.md#completion-checklist).

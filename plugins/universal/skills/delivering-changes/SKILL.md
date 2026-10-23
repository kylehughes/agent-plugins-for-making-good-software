---
name: delivering-changes
description: "Carry a requested change from a ticket or brief to a PR-ready handoff. Use when the user delegates the full implementation, simplification, and hardening workflow, with project-defined manual verification checkpoints."
---

# Delivering Changes

Take ownership of a requested change through its PR-ready handoff. Continue from implementation through simplification, hardening, and the remaining checks without requiring a separate prompt for each stage.

## Scope and Completion Contract

Use this workflow when the user delegates a change from the initial request through preparation for review. A ticket is optional; dictated commentary, a brief, or an existing conversation can supply the request. A request for only planning, implementation, simplification, or read-only review keeps that narrower scope.

The endpoint is a reviewable change with its required pre-PR checks complete. Creating a PR, committing, pushing, merging, releasing, and updating tickets follow the user's existing authorization and project workflow; this skill does not grant those permissions itself. Carry out authorized follow-on work without asking for the same permission again.

Keep one task scope, decision record, and account of verification. Stage summaries are intermediate evidence, not reasons to return control to the user. Continue until the handoff is ready or a required human check, unresolved decision, or concrete blocker prevents progress. Do not add a plan document, registry, or persistent goal merely to run this workflow.

## Workflow

### 1. Establish the Request and Project Rules

Read the referenced ticket or brief through an available connector or project tool, the user's commentary, and applicable project instructions. Treat explicit user corrections as updates to the source request. Ask only when an unresolved ambiguity changes the intended outcome or cannot be resolved from available context.

Identify the acceptance criteria, compatibility constraints, owned work, and required checks. Discover project guidance for manual verification and the timing of preparation, generation, review, and final checks. Follow relevant skill references and available descriptions; do not depend on a project-specific naming convention or search undisclosed skill directories.

Inspect the branch and working tree, including staged, unstaged, and untracked files. Separate the requested change from unrelated existing work. Preserve that boundary through every stage, including when other work shares a file. A new file needed to complete the requested change can join the task; touching it does not authorize a broader cleanup.

Retain the task-entry comparison needed to preserve existing work. Use a fresh allocated temporary directory outside the repository for scoped snapshots, and capture a newly affected path before its first edit. Keep the source request authoritative: an existing defect is not a requirement to preserve it.

### 2. Implement and Verify the Requested Behavior

Implement the change using the project's patterns and relevant language or platform guidance. Resolve routine technical choices from evidence. Run the applicable automated checks and fix owned failures; do not stop merely because the initial implementation is finished.

Apply required human checkpoints at the time specified by the project. If a human check is required but its timing is unspecified, pause after implementation and its automated checks, before simplification and hardening. Follow [Manual Verification and Resumption](#manual-verification-and-resumption).

Before cleanup, retain the implemented state needed for behavior comparison, including owned dirty and untracked contents. Distinguish this baseline from the task-entry baseline: one establishes the requested behavior to preserve during cleanup; the other identifies existing work and the change the task owns. Supply reviewers the relevant retained contents, not just a scratch path they may be unable to read.

### 3. Simplify the Owned Change

Apply [simplifying-code](../simplifying-code/SKILL.md) to the implemented change. Compose with available platform-specific guidance under that skill's rules, reusing guidance already active. Keep its behavior-preservation contract and review passes; do not substitute a quick cosmetic pass.

Pass the owned surface, authoritative requirements, implemented baseline, and completed verification into this stage. Preserve unrelated work. Retain completed review results with their scope and artifact state so hardening can reuse evidence that still applies. Do not manufacture edits when the implementation is already simple.

For a change containing no code to simplify, record that the code-simplification stage does not apply and continue to hardening's appropriate path. Do not expand a prose task into implementation review to populate this stage.

### 4. Harden Without Restarting the Task

Apply [hardening-changes](../hardening-changes/SKILL.md). Let it select the appropriate review path, discover project hardening companions, and own its audit-and-fix loop. Pass the task's owned surface and exclusions, baselines, decisions, completed reviews, and check evidence into that workflow.

Reuse an earlier audit only when it satisfies the required review contract for the same concern and materially unchanged artifacts. A simplification summary is not evidence that every required hardening reviewer has completed its work. Use the available reviewer mechanisms and the skill's documented fallback.

Treat the hardening handoff as a stage result. Resolve routine next actions within the task rather than forwarding them as another assignment for the user. Preserve genuine blockers and unresolved decisions; do not rename them completion. Continue after **Hardening complete** to finish the delivery checks below.

### 5. Complete the Applicable Delivery Checks

Inspect hardening's pending proof and the project's remaining requirements. Run checks assigned after hardening that are executable and required before the PR handoff. Ordinary test, build, generation, or inspection commands are work for the coordinator when authorized and available, not automatic human checkpoints.

Preserve checks explicitly assigned to PR CI, merge, or release at their required stage. Name those later gates and their owners in the handoff; do not perform an unauthorized external action to satisfy them early. Missing pre-PR evidence prevents a PR-ready status. Evidence assigned to a later stage does not justify a claim of merge or release readiness.

Reuse a passing check when it covers the same requirements and final artifacts, unless project instructions require a rerun. Later edits that invalidate evidence require the affected checks again. Review any owned generated changes or repairs through the relevant existing reviewers. Reapply simplification only to affected code that needs it; do not restart the whole sequence after every fix.

Keep the hardening handoff's reviewed explanations and limits. Update completion metadata from actual later results. If later changes alter substantive claims or the final explanation, give the revised complete draft and evidence to the same applicable reviewer under the existing claim-review contract; do not add an independent audit loop.

### 6. Hand Off the Change

Return one concise handoff for someone who did not watch the work:

- **Status:** Ready for PR, Awaiting manual verification, Needs decision, or Blocked.
- **Changed:** The delivered behavior and material decisions.
- **Proof:** Completed checks, relevant review outcomes, and user-reported manual verification, with their limits.
- **Next:** The PR handoff or authorized follow-on action; otherwise the exact missing verification, decision, or unblock step. Include later project gates and material deferred work when present.

Report **Ready for PR** only when implementation, applicable simplification, hardening, and required pre-PR verification are complete on the final artifacts. Do not report user verification as an agent-executed test or hide pending requirements behind a completed stage. Use the applicable reviewed response when a final claim review was required.

## Manual Verification and Resumption

Human verification requirements come from the task and project. A UI change alone does not establish a mandatory human checkpoint. Use available tools for checks they can perform; ask for human judgment when required evidence genuinely needs it.

When pausing, provide a concrete, reviewable result and state what the user should check, how to reach it, the expected behavior, and which later stages remain. Preserve the current stage, owned scope, artifact state, decisions, completed evidence, and exact pending check in the conversation or the project's existing task mechanism. Do not invent a new tracking system for this purpose.

Resume from that checkpoint after the user provides the result. Silence, elapsed time, or an unrelated reply does not satisfy verification. Fix reported defects within scope, then repeat the affected checks. If later edits invalidate a verified interaction or result, request only the affected manual recheck at the appropriate checkpoint. Otherwise carry the verification forward and continue automatically.

## Reference Map

Load each stage's existing instructions when that stage begins:

- [Simplifying code](../simplifying-code/SKILL.md): behavior-preserving cleanup of the implemented change and applicable platform composition.
- [Hardening changes](../hardening-changes/SKILL.md): scoped review, project companions, fixes, convergence, and the stage handoff.

Before the final handoff, confirm the request is delivered, required stages finished, evidence covers the final artifacts, and every remaining action is accurately assigned to its required stage.

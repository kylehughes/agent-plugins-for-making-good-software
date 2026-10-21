---
name: verifying-invariants
description: "Assess whether invalid domain values or states can be constructed, decoded, mutated into, or reached, and verify changes to those enforcement boundaries. Select checks and bound conclusions. Excludes ordinary function-output tests, defect review, naming, and async-test flakiness."
---

# Verifying Invariants

Determine which incorrect states a scoped implementation excludes and what evidence supports that conclusion. Begin with an authoritative domain contract; turn requests for perfect correctness into a bounded inventory with uncovered obligations.

Use this skill for an explicit invariant or proof request, or a change to invariant representation, enforcement, or legal transitions. Ordinary defect review, output testing, naming, test organization, and async-test flakiness stay with their owners unless they expose a separate invariant claim. This skill grants no permission to refactor, install dependencies, create infrastructure or reviewer roles, or broaden scope. Keep read-only requests read-only; reviewing a check does not authorize executing it, and inspect commands before running them. Verification-only work reports counterexamples, checks, and limits without supplying an unrequested replacement design.

## Choose the Mode and Stopping Condition

Select the mode before doing task work:

- **Assessment:** Perform the requested assessment and authorized checks directly, then report. The implementation and completion-review steps below do not apply.
- **Implementation:** Before editing, record one claim-check method in the evidence ledger. Use an exposed, permitted reviewer focused on correctness while preserving caller model policy. Use direct inspection only when review is unavailable, denied, or fails, and record why.

Implementation is complete only after this sequence finishes:

> requested change → final project checks → one bounded claim check → resolve claim records and existing review findings → report

Reuse a correctness review only when it covers the same final artifacts, evidence, and complete response draft. During hardening, attach this concern to its existing correctness review; never add a reviewer or audit loop.

An enclosing workflow may hand off full project verification to a later stage. Respect that boundary: finish its authorized checks and bounded claim review, then name pending obligations, their owner, and next actions in the handoff. That completes the enclosing stage, not the invariant implementation sequence above; a compile checkpoint alone does not discharge runtime or transition obligations.

## Workflow

### 1. State the Obligation and Load Its Semantics

State each obligation as a falsifiable proposition with its authority, assumptions, inputs, entry points, access context, configuration, and transitions. Record uncertainty.

For a refined-value boundary, separate these implications:

1. successful result → predicate holds;
2. specified input class → no successful result;
3. specified input class → named error or result.

The first two do not imply the third. A named-error policy needs authority or task authorization plus evidence for its path and conditions. Preserve previously accepted inputs satisfying the authoritative predicate; treat stricter rejection separately.

“Unrepresentable” needs a named representation and access boundary. “Unreachable” needs initial states and allowed transitions. External facts usually need runtime validation and recovery; a past check does not make them permanent.

If the claim depends on language-specific construction, decoding, access control, ownership, or isolation, resolve its semantics owner before assessment or edits:

- Match the claim to an installed type-correctness companion using the available skill descriptions. It owns those language semantics.
- Invoke that guide and record its name and successful load, or reuse an already loaded guide and identify it. Knowing the language does not replace loading its available guidance.
- Only after checking the available descriptions may you record that no companion is installed. In that case, inspect implementation and available language documentation, state uncertainty, and continue within scope. A failed read of an available guide is an unresolved prerequisite, not evidence of absence.

### 2. Trace the Boundary and Select Evidence

Trace scoped construction, decoding, mutation, transition, and external paths, including aliases and escape hatches. Reconcile downstream claims with upstream bypasses. Read [construction boundaries](references/construction-boundaries.md) for value claims and [transition exploration](references/transition-exploration.md) for reachability or interleavings.

Keep enforcement separate from evidence and select the lightest fitting method: compiler rejection with a valid control, boundary tests plus path inspection, transition tests, completed finite traversal, discharged proof obligations, or integration checks with recovery. Read [evidence and reporting](references/evidence-and-reporting.md) for mixed evidence or proof claims.

Compiler results establish only checked rules and settings. Seeds, coverage, and mutation scores do not establish completeness. Exploration is exhaustive only for a faithful finite model finishing without sampling or truncation. For serialized values, separately check fixed historical restoration, predicate-reaching invalid input, and valid round trip; a round trip can hide paired incompatible changes.

Use production modules or shared sources for production claims. Pair negative fixtures with valid controls under the same settings. Existing testing skills own assertion syntax, synchronization, and organization.

For each counterexample, identify a same-boundary regression and valid control. Reapply demonstrated bypasses to a repair and name remaining paths. Establish uncertain language mechanisms through the companion, primary documentation, or an executable misuse check; otherwise leave the mechanism open.

When warranted, select one isolated [targeted mutation](references/targeted-mutations.md) in the evidence plan. A survivor shows the check missed that change, not necessarily an implementation defect. Mutation is evidence, never a completion step.

### 3. Implement, Check, and Account

Keep a temporary ledger of obligation, provenance, artifact or command, result, supported conclusion, and limits. Mark requester assertions **supplied**, inspected artifacts and completed results **observed**, and unperformed checks **proposed**. Include the claim-check method.

Run only authorized checks. Record the exact working snapshot, toolchain, configuration, command or artifact, result, and limits. A missing tool, malformed fixture, unrelated diagnostic, crash, or timeout is failed or unavailable evidence, never successful rejection.

For implementation, make the scoped change and run appropriate final checks, including any preselected mutation. Once artifacts and results are stable, preserve unavailable checks as limits; do not acquire tools during completion unless separately authorized. Then prepare the complete final response draft and execute the already selected claim check.

### 4. Execute the Claim Check

Check changed or behaviorally affected maintained claims and every behavioral claim in the complete final response draft.

Give the reviewer the complete response draft rather than a selected claim list. **Claims in project text (maintained claims)** are verbatim statements from the final scoped artifacts, including unchanged statements whose behavior the change affects. Start each record with the quotation and its path and line; do not substitute an implementation summary or draft sentence. **Claims in final response (report claims)** come from the draft and cite its sections. Group equivalent statements with every quotation and location; separate different conditions, domains, or conclusions. Test names and implementation labels are evidence unless they independently assert a contract. Do not audit unchanged artifacts outside that scope.

For every derived maintained claim and report claim, produce a record and disposition of **supported**, **contradicted**, or **unestablished**:

> authority and logical form → boundary and input domain → final outcome and evidence → baseline outcome and evidence for compatibility → supported wording

Classify authority for each claim before correction. Its source location says where the statement appears, not what authorizes its behavior. Introduced implementation or draft text cannot authorize itself: narrow or remove it unless an independent task or contract obligation requires the behavior, then assess that behavior over the obligation's domain.

Respect a claim's stated conditions and exclusions. If its domain is ambiguous, mark the domain uncertainty rather than silently choosing a broader reading. Tested examples and evidence limits do not silently narrow a maintained claim's domain: if only narrower wording is supported, disposition the exact claim accordingly. A counterexample inside the established domain contradicts the claim without separate evidence that current callers exercise that case.

For independent review, give the existing correctness reviewer the complete intended response, obligations, exact changed paths and final contents, results, limits, and baseline evidence for compatibility. Require three response sections: **Claims in project text (maintained claims)**, **Claims in final response (report claims)**, and **Reviewed response**. The first two contain separate claim records and dispositions, using columns `Verbatim claim and location | Independent authority or introduced text | Disposition and evidence | Supported wording or pending obligation`. The last returns the complete supplied draft with only the records' supported wording corrections; preserve its sections, next actions, limits, and pending obligations. Do not invent completed work or add behavioral assurances. Missing or incomplete inputs or an unresolved contradiction mean the review is incomplete, not approved; identify the gap rather than reconstructing missing content.

A violated independently authoritative obligation is a claim record with its counterexample and required caller work, not a repair proposal. Preserve unestablished required obligations as pending in the reviewed response. A claim-only focused review returns the three sections without the ordinary defect workflow or optional repair alternatives; keep its records inline without task items. Combine this work with the final scoped correctness audit when applicable, retaining that review's authorized ordinary findings separately. The claim-only reviewer remains read-only and must not build, test, edit, delegate, create tasks, add infrastructure, or audit unrelated concerns. Require a completed result, not merely a tool call.

For fallback, record why review was unavailable, denied, or failed, then perform the same bounded check:

1. Read the changed inventory and final diff, then any changed behavior-bearing file whose full content was omitted, truncated, or untracked. Derive maintained claims from changed or behaviorally affected statements in those scoped final artifacts, and report claims from the complete response draft.
2. Keep successful-result, non-success, and named-error obligations separate. Document a named error only when authorized and only for its established path and conditions. Leave incidental outcomes in the ledger or report.
3. Assess every derived maintained and report claim from the scoped evidence using the same record shape. Produce the same three sections, including the complete corrected response, and identify any input gap or unresolved contradiction that leaves the check incomplete.

The caller owns corrections. Correct, narrow, or remove unsupported assertions about present behavior. Do not change production behavior or add tests solely to preserve introduced text. Do not erase an authoritative required obligation merely because it is unestablished; retain it as a normative obligation and mark its verification or implementation pending.

Post-review edits to behavior-bearing final artifacts must use the record's minimal supported wording. If an edit adds or materially broadens a behavioral statement, derive and disposition that affected maintained claim against the same evidence before completion; this does not start another review cycle.

A behavior-changing correction requires independent task or contract authority, affected applicable checks to run again, and affected records and draft wording to use their actual results; it does not require another reviewer or audit cycle.

Resolve the records and apply any remaining supported corrections to the returned **Reviewed response**, then reconcile affected records against the same evidence without another review. Emit that response instead of rebuilding it from the claim records. After review, add only formatting or completion metadata copied from the completed review receipt or required follow-up check results; omit any new or materially broadened behavioral claim.

Completion requires these resolutions and explicit pending obligations. Do not add tests for optional prose, audit unchanged files, expand the invariant inventory, or restart implementation except for an in-scope contradiction.

### 5. Report and Persist Proportionally

Report only after the claim check and corrections complete. Use the ledger and tool trace to resolve records and retain pending obligations in the returned reviewed response.

Before claiming preservation or change, pair baseline and final outcomes for the same representation and boundary. Claim only the exact respect that matches or differs; if either side is unavailable, omit the temporal claim or mark it unestablished.

Account for each obligation as observed, supplied, or pending. Put counterexamples first and separate conclusions from assumptions, limits, and unavailable checks. Actions need completed results; content identity needs byte or digest comparison. Do not collapse compiler restrictions, runtime validation, samples, finite exploration, and proof into “verified.”

Normally keep the inventory in the task report. Create or update a registry only when the project already uses one or the user requests durable CI or a lasting contract. Missing evidence does not authorize a registry, CI change, or extra implementation.

For an authorized durable contract, use the [manifest template](assets/invariants.template.json), [manifest format](references/manifest-format.md), and [execution-report requirements](references/evidence-and-reporting.md#execution-report). Keep results separate. CI must obtain its checker reproducibly and run its exact command. Validate metadata with:

```sh
python3 <skill-dir>/scripts/validate_invariants.py <manifest.json> --root <project> --json
```

This checks schema and references only; it does not run commands or prove an invariant. Invalidate evidence when implementation, configuration, assumptions, or toolchain changes.

## Reference Map

Read only what the current obligation needs:

- [Construction boundaries](references/construction-boundaries.md): value paths, logical forms, and enforcement.
- [Transition exploration](references/transition-exploration.md): interleavings, traversal, exhaustion, and bounds.
- [Evidence and reporting](references/evidence-and-reporting.md): evidence, ledger, reports, persistence, and checklist.
- [Targeted mutations](references/targeted-mutations.md): sensitivity to a reopened path.
- [Manifest format](references/manifest-format.md): durable obligation metadata.

Use the [completion checklist](references/evidence-and-reporting.md#completion-checklist) before finishing.

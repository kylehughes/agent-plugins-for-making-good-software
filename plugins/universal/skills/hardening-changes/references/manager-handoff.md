# Manager handoff

For the substantive path, prepare a concise handoff for someone who did not watch the implementation. Name concrete files, symbols, changes, and the next action. Report scoped findings and obligations; rejected observations stay in the internal ledger. Use only sections with content. The wording-only path finishes in the skill entry point without this reference.

## Status and proof

Open with four one-line fields:

```text
Status: [Hardening complete | Needs decision | Blocked].
Next: [the next project check, required decision, or blocking action].
Changed: [what changed, or no code changes needed].
Proof: [actual compile checkpoint and other completed checks, including project-required hardening steps, or none required].
```

- **Hardening complete** means the scoped audit-and-fix loop converged, its required reviews finished, and applicable checks required during hardening passed on the final artifacts. It does not mean the change is merge-ready or its invariants are verified. A project check assigned to a later ship gate belongs in Next and Must Fix or Decide Before Merge; a failed or unavailable check required during hardening prevents this status.
- **Needs decision** means an unresolved finding or tradeoff needs the caller's disposition. Name that decision; pending routine checks alone do not require a human decision.
- **Blocked** means a concrete obstacle prevents completion of this stage. Name the obstacle and what would unblock it.

Never count a compile checkpoint as a passing runtime test. List pending proof obligations with the responsible project role or agent and the next command or action. Do not imply merge or release readiness while required project checks remain outstanding.

## Sections

Write complete sentences after the status block; avoid compressed label-colon fragments and chains of unrelated clauses.

**Findings and Changes.** Explain each fix-now problem, the owned change that introduced or exposed it, and the repair. Briefly identify applied project companions, including reused guidance, and report their command results in Proof. Include any setup notes or completed reviewer outcomes you intend to report. If the status block already says everything useful, omit this section; otherwise include the full explanation in the draft before review.

**Judgment Calls.** Explain each judgment fix and why the evidence supports it. Name the strongest alternative when needed to understand the choice.

**Must Fix or Decide Before Merge.** Include blockers, unresolved dispositions, and anything the project ship gate still has to prove. For each, name the evidence or gap, owner, and next action. Keep pending invariant checks here even when hardening is complete.

**Deferred Work.** Include owned findings whose completion would require app-wide rearchitecture or a product decision. Give the owned change that gives rise to the finding, impact, reason for deferral, first implementation step, affected modules, rough effort (`S`/`M`/`L`/`XL`), and originating finding. Most runs have none; include at most six.

In attended runs with a configured issue tracker, offer once to file deferred work, with at most six concise options. When hardening is one stage of an enclosing workflow, carry the offer into that workflow's final handoff instead of pausing here. Do not file issues without authorization.

## When invariant verification applies

The existing correctness reviewer owns the final review response; the orchestrator owns resolving its findings. The claim contract and correction rules come from [verifying-invariants](../../verifying-invariants/SKILL.md).

1. Once final fixes and checkpoint evidence are stable, write every word intended for the user to a draft file in the workflow's allocated scratch directory, including explanations of the original defect, fix, tradeoffs, and compatibility. A short status block is not the draft if you intend to add narrative later. Fill and send the review request below to the existing correctness reviewer, copying the draft file's exact contents inline. Keep the file as the caller's stable draft; do not require reviewer access to the scratch directory. Combine this with an applicable final scoped correctness re-audit rather than scheduling a separate claim audit.
2. Obtain its completed **Claims in project text (maintained claims)**, **Claims in final response (report claims)**, and **Reviewed response**. Source quotations belong in the first section; sentences from your draft belong in the second. The third contains the entire supplied handoff with only supported wording corrections. Selected claim bullets or a verdict without the reviewed response do not complete this transfer.
3. Resolve the records and any ordinary findings under the invariant skill's correction rules. An **Incomplete final claim review** requires supplying its named missing input to the same reviewer. An unavailable required input or unresolved contradiction prevents declaring hardening complete. Project proof assigned to a later stage may remain pending when accurately handed off; required hardening checks may not.
4. Emit the returned **Reviewed response**, with only the permitted supported corrections and completion metadata. Do not compose another handoff from the verdicts. This completes the hardening stage, not the pending project proof.

When independent review is unavailable, use the invariant skill's direct-check fallback on the same complete draft and retain that corrected response. No additional reviewer, registry, audit cycle, or project verification gate is introduced.

### Final review request

Copy this contract into the final correctness-review request and fill its inputs. Do not pass just the section names: the reviewer needs the stage definition and claim sources even if earlier reviewers already saw them.

```text
Complete the scoped correctness re-audit and final claim check below. Remain read-only; do not build, test, edit, or delegate.

Stage: Hardening complete means the owned audit/fix loop converged, its required reviews finished, and applicable checks required during hardening passed on the final artifacts. It does not mean all runtime proof passed or merge readiness. Project proof explicitly assigned to a later stage may remain pending; an unresolved review finding or required hardening check prevents completion. Use Needs decision for an unresolved disposition and Blocked for an obstacle preventing this stage; do not invent another status.

Scope and authority: [owned paths, final contents or readable locations, authoritative requirements]
Ownership comparison: [base branch/HEAD and initial changed surface]
Compatibility comparison: [exact retained initial-work contents needed for comparison and any other required baseline, including uncommitted behavior; capture paths identify provenance only; distinguish observed behavior from preservation requirements and label missing evidence unavailable]
Completed reviews and checks: [actual results and their limits]
Pending project proof: [obligations, required stage, owner, next command/action]

Derive Claims in project text (maintained claims) from verbatim statements in the scoped final artifacts, including unchanged statements whose behavior this change affects. Cite path and line. Do not substitute implementation summaries or sentences from the draft. Group equivalent statements with every quotation and location. Test names and implementation labels are evidence unless they independently assert a contract.

Read the complete draft supplied below. Derive Claims in final response (report claims) separately from that draft, citing its sections. For each record distinguish where the statement appears from what independently authorizes it: introduced implementation or draft text does not authorize its own behavior. Mark it supported, contradicted, or unestablished, with its scoped evidence or gap. Narrow or remove unsupported introduced assertions; retain independently required obligations as pending when unestablished. Follow the invariant skill's remaining correction rules. Return these columns in both sections:
Verbatim claim and location | Independent authority or introduced text | Disposition and evidence | Supported wording or pending obligation

Return Reviewed response containing the entire supplied draft with only supported wording corrections. Preserve its sections, next actions, limits, and pending authoritative obligations. Do not invent completed work or add assurances. Identify missing inputs or unresolved contradictions as incomplete; request missing captured contents from the caller rather than reading its scratch directory or retrying denied access through another tool. Return ordinary correctness findings separately when applicable.

Complete intended final response:
[copy every word from the caller's draft file here, not its path or selected claims]
```

After resolving the returned records, use its **Reviewed response** as the completed hardening handoff. Send it as the final message for a standalone invocation; otherwise return it to the enclosing workflow so remaining stages can continue. An explanation omitted from the draft stays omitted; do not append a fresh summary of the work.

## Completion checklist

- All required auditors finished, and every finding has a disposition.
- Status describes this stage; applied companions, required hardening-check outcomes, and later project checks are explicit.
- Observed commands and results support each proof claim.
- When applicable, the complete handoff received the bounded claim check and the final response is its corrected draft.
- No unperformed check is reported as passed and no outstanding project proof is hidden by a completion label.

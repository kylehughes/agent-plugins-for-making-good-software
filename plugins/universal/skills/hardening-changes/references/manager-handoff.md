# Manager handoff

For the substantive path, prepare a concise handoff for someone who did not watch the implementation. Name concrete files, symbols, changes, and the next action. Report scoped findings and obligations; rejected observations stay in the internal ledger. Use only sections with content. The wording-only path finishes in the skill entry point without this reference.

## Status and proof

Open with four one-line fields:

```text
Status: [Hardening complete | Needs decision | Blocked].
Next: [the next project check, required decision, or blocking action].
Changed: [what changed, or no code changes needed].
Proof: [actual compile checkpoint and other completed checks, or none needed for mechanical work].
```

- **Hardening complete** means the scoped audit-and-fix loop converged and its required reviews finished. It does not mean the change is merge-ready or its invariants are verified. A normal pending project ship gate belongs in Next and Must Fix or Decide Before Merge.
- **Needs decision** means an unresolved finding or tradeoff needs the caller's disposition. Name that decision; pending routine checks alone do not require a human decision.
- **Blocked** means a concrete obstacle prevents completion of this stage. Name the obstacle and what would unblock it.

Never count a compile checkpoint as a passing runtime test. List pending proof obligations with the responsible project role or agent and the next command or action. Do not imply merge or release readiness while required project checks remain outstanding.

## Sections

Write complete sentences after the status block; avoid compressed label-colon fragments and chains of unrelated clauses.

**Judgment Calls.** Explain each judgment fix and why the evidence supports it. Name the strongest alternative when needed to understand the choice.

**Must Fix or Decide Before Merge.** Include blockers, unresolved dispositions, and anything the project ship gate still has to prove. For each, name the evidence or gap, owner, and next action. Keep pending invariant checks here even when hardening is complete.

**Deferred Work.** Include owned findings whose completion would require app-wide rearchitecture or a product decision. Give the owned change that gives rise to the finding, impact, reason for deferral, first implementation step, affected modules, rough effort (`S`/`M`/`L`/`XL`), and originating finding. Most runs have none; include at most six.

In attended runs with a configured issue tracker, offer once to file deferred work, with at most six concise options. Do not file issues without authorization.

## When invariant verification applies

The existing correctness reviewer owns the final review response; the orchestrator owns resolving its findings. The claim contract and correction rules come from [verifying-invariants](../../verifying-invariants/SKILL.md).

1. Once final fixes and checkpoint evidence are stable, write the complete intended handoff with every section, pending obligation, and next action. Supply that full text, final scoped artifacts, baseline evidence, actual results, and limits to the existing correctness reviewer. Combine this with an applicable final scoped correctness re-audit rather than scheduling a separate claim audit.
2. Obtain its completed **Maintained claims**, **Report claims**, and **Reviewed response**. The first two contain the derived dispositions; the third contains the entire supplied handoff with only supported wording corrections. Selected claim bullets or a verdict without the reviewed response do not complete this transfer.
3. Resolve the records and any ordinary findings under the invariant skill's correction rules. An incomplete review or unresolved contradiction prevents declaring hardening complete. Required project proof may remain pending when accurately handed off.
4. Emit the returned **Reviewed response**, with only the permitted supported corrections and completion metadata. Do not compose another handoff from the verdicts. This completes the hardening stage, not the pending project proof.

When independent review is unavailable, use the invariant skill's direct-check fallback on the same complete draft and retain that corrected response. No additional reviewer, registry, audit cycle, or project verification gate is introduced.

## Completion checklist

- All required auditors finished, and every finding has a disposition.
- Status describes this stage; the next action and pending project checks are explicit.
- Observed commands and results support each proof claim.
- When applicable, the complete handoff received the bounded claim check and the final response is its corrected draft.
- No unperformed check is reported as passed and no outstanding project proof is hidden by a completion label.

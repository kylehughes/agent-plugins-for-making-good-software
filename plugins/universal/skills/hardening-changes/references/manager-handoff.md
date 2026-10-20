# Manager handoff

Prepare a concise handoff for someone who did not watch the implementation. Name concrete files, symbols, changes, and the next action. Use only sections with content.

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

**Deferred Work.** Include only work that exceeds the branch's ownership or requires a product decision. Give its impact, scope reason, first implementation step, affected modules, rough effort (`S`/`M`/`L`/`XL`), and originating finding. Most runs have none; include at most six.

**Not Carried Forward.** Optionally explain findings that were fixed, dropped, or not worth tracking, including their rationale.

In attended runs with a configured issue tracker, offer once to file deferred work, with at most six concise options. Do not file issues without authorization.

## When invariant verification applies

Use the existing correctness reviewer for the bounded claim check defined by [verifying-invariants](../../verifying-invariants/SKILL.md). Keep it inside the current workflow:

1. Write every section you intend to emit in its final wording, including pending obligations and the next action. The four-line status block or selected claim bullets alone are not the complete draft.
2. Give the reviewer that entire draft, final artifacts, actual checkpoint results, and verification limits. Require explicit supported, contradicted, or unestablished verdicts for maintained claims and report claims. Reuse a prior review only when it covered these same inputs.
3. Wait for the completed verdicts and resolve the records. Apply their supported corrections to the same draft. After review, add only formatting or completion metadata from the review receipt or required follow-up results; do not add new or broader behavioral claims.
4. Emit that corrected draft. Completing this stage does not discharge pending project proof or complete invariant implementation.

The invariant skill owns claim semantics and correction rules. This handoff adds no reviewer, registry, audit cycle, or project verification gate.

## Completion checklist

- All required auditors finished, and every finding has a disposition.
- Status describes this stage; the next action and pending project checks are explicit.
- Observed commands and results support each proof claim.
- When applicable, the complete handoff received the bounded claim check and the final response is its corrected draft.
- No unperformed check is reported as passed and no outstanding project proof is hidden by a completion label.

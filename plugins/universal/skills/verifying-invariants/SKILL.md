---
name: verifying-invariants
description: "Verify invariants and interpret compiler, test, exploration, or mutation evidence. Use for explicit correctness proofs or changes to state models, construction boundaries, and legal transitions; not routine test organization, naming cleanup, or ordinary defect review."
---

# Verifying Invariants

Determine which incorrect states a scoped implementation excludes, how it excludes them, and what evidence supports that conclusion. Start from the domain contract: a tool cannot decide what “incorrect” means without one.

Use this skill for an explicit invariant or proof request, or when a change affects the representation or enforcement of an invariant. Select only the obligations affected by the change. A request for “perfect correctness” calls for a bounded inventory and honest limits, not an unfinishable promise.

Ordinary defect review, naming cleanup, test organization, and async-test flakiness stay with their existing owners unless they expose a separate invariant claim. This skill does not authorize refactoring, new infrastructure, dependency installation, or broader review scope. Keep read-only requests read-only; distinguish reviewing a check from executing it, and inspect commands before running them.

## Contract

- Separate **enforcement** from **evidence**. A private constructor can enforce a boundary; a test supplies evidence about it. A validator for an evidence manifest validates metadata only.
- State the universe of the claim: inputs, entry points, access context, supported configuration, and transitions. “Unrepresentable” needs a named representation and boundary; “unreachable” needs initial states and allowed transitions.
- Repeatability is not completeness. Seeded tests, coverage, and mutation scores cannot establish that all incorrect states are excluded.
- “All explored states passed” does not establish that exploration was exhaustive, even within stated bounds. Require evidence that the frontier was exhausted without sampling or truncation before making that claim.
- Treat compiler acceptance or rejection as evidence under that compiler's rules and settings. It does not prove business intent, external facts, or behavior outside the checked boundary.
- Prefer the lightest method that answers the actual obligation. Escalate to finite exploration or formal verification only when the risk and contract justify their maintenance cost.

## Workflow

### 1. State the obligations

Read the requested scope and authoritative contracts before selecting checks. Write each invariant as a falsifiable statement, with its authority and assumptions. Distinguish:

| Kind | Example obligation |
| --- | --- |
| Structural | A loaded state always carries its value; unrelated identities cannot be interchanged. |
| Refined value | Every constructed quantity is positive, including values entering through decoding. |
| Transition | Completion of an older operation cannot overwrite the current operation's result. |
| External | A remote resource is still accessible when a consumer uses it. |

Record uncertainty in the contract instead of choosing a convenient interpretation. External facts often require runtime validation and failure handling; representing evidence of a past check does not make the fact permanent.

### 2. Trace the boundaries

Find constructors, factories, decoders, deserializers, mutations, aliases, copies, transitions, persistence, and external adapters within scope. Check whether the alleged enforcement covers every reachable entry and update path. Include nested mutable state and asynchronous completion paths where relevant.

Use [construction boundaries](references/construction-boundaries.md) for value and representation claims. When the conclusion depends on language or platform semantics, load the available companion for type correctness before judging the claim. It owns access control, synthesized construction and decoding, ownership, compiler phases, and idiomatic representations. If no companion is installed, inspect the implementation and available language documentation, state uncertainty, and continue the scoped assessment. Do not duplicate those rules here.

### 3. Select evidence per obligation

| Obligation | Suitable starting evidence | What remains to establish |
| --- | --- | --- |
| Forbidden construction or API use | Compiler rejection paired with a valid control | The production API, relevant access contexts, settings, and bypasses are covered. |
| Validated input | Boundary tests and inspection of all construction paths | The predicate matches the contract and every path enforces it. |
| Transition preservation | Tests of legal and rejected transitions | Initial states and interleavings match the actual implementation. |
| Finite state space | Exhaustive traversal of the declared model and bounds | Model fidelity, completeness within bounds, and any excluded environment behavior. |
| Mathematical property | Proof obligations discharged by an appropriate tool | Assumptions, trusted components, and linkage to the implementation. |
| External condition | Integration checks and explicit recovery behavior | The environment may change after the observation. |

Read [transition exploration](references/transition-exploration.md) when reachability or interleavings matter, and [evidence interpretation](references/evidence-and-reporting.md) before making a proof claim. Existing testing skills own assertion syntax, synchronization, and test organization.

### 4. Check the claim and its failure modes

Run checks authorized by the task and project rules, or assess existing artifacts in read-only work. Record the checked revision or exact working snapshot, relevant toolchain/configuration, commands, results, and limits. A missing tool, broken fixture, timeout, crash, or unrelated compiler diagnostic is unavailable or failed verification, never successful evidence of rejection.

Use actual production modules or shared production sources for claims about production. Demonstration types prove only their own behavior. Positive controls must exercise the corresponding valid operation under the same relevant settings.

For consequential claims, consider a small [targeted mutation check](references/targeted-mutations.md): deliberately reopen the exact forbidden path in an isolated copy and confirm the intended check fails. A surviving mutation exposes a gap in that check; it does not, by itself, show the original implementation is wrong.

### 5. Report a bounded conclusion

For each obligation, report the enforcement mechanism, evidence observed, assumptions and limits, and remaining gaps. Identify counterexamples first. Say what was checked and what the result supports; do not collapse compiler restrictions, runtime validation, sampled tests, finite exploration, and formal proof into a single “verified” label.

Normally keep this inventory in the task report. Create or update a maintained registry only when the project already uses one or the task calls for durable CI or a lasting verification contract. Follow project location conventions. Missing evidence alone does not authorize a registry, CI edits, or extra implementation work.

For that durable case, start from [the manifest template](assets/invariants.template.json) and follow [the manifest format](references/manifest-format.md). Validate it with:

```sh
python3 <skill-dir>/scripts/validate_invariants.py <manifest.json> --root <project> --json
```

This command checks schema and local references. It never executes stored commands, proves invariants, or stores a cached verified verdict. Keep execution reports separate and invalidate stale evidence when its implementation, configuration, assumptions, or toolchain changes.

## Reference Map

Read only the reference needed for the current obligation:

- [Construction boundaries](references/construction-boundaries.md): inventory creation and mutation paths and distinguish structural exclusion from checked values.
- [Transition exploration](references/transition-exploration.md): define the model, traverse finite states, handle interleavings, and state bounds.
- [Evidence and reporting](references/evidence-and-reporting.md): interpret evidence strength, report limits, and decide when formal methods are justified.
- [Targeted mutations](references/targeted-mutations.md): test whether a check detects a deliberately reopened invariant violation.
- [Manifest format](references/manifest-format.md): maintain optional obligations and validate their metadata without executing commands.

Use the [completion checklist](references/evidence-and-reporting.md#completion-checklist) before finishing.

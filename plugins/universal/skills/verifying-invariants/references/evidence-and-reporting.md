# Evidence and reporting

An invariant is a proposition about a specified domain. Its enforcement mechanism and the evidence supporting it are separate parts of the claim. Define both, and keep the conclusion no broader than the checked implementation and assumptions.

## Evidence vocabulary

| Evidence | Supports | Does not establish by itself |
| --- | --- | --- |
| Inspection | The examined paths appear to preserve the stated predicate. | Exhaustiveness of paths or executions. |
| Compiler restriction | A specified operation is rejected under the checked language rules, access context, and settings. | Domain correctness or all construction and runtime paths. |
| Boundary tests | The validator accepts and rejects the exercised inputs as expected. | All possible input values or bypass prevention. |
| Property tests | The property held for generated samples from a stated domain and configuration. | Exhaustiveness, even with a fixed seed. |
| Transition tests | The exercised sequences preserve the invariant. | Every reachable interleaving. |
| Bounded exploration | The property held in the explored state space under explicit bounds. | Behavior outside those bounds or unmodeled production behavior. |
| Formal proof | The encoded proposition follows under the proof system's assumptions. | Fidelity of the specification, implementation correspondence, or correctness of trusted components. |
| Integration check | The observed external interaction met the contract at that time. | That the environment will continue to do so. |

Coverage measures exercised code or obligations according to its definition. Mutation checks measure detection of selected changes. Neither metric is a completeness certificate.

Do not call a rejected fixture a compiler restriction until its positive control compiles and the expected diagnostic matches. A malformed fixture is a harness failure. Keep “failed check,” “counterexample,” and “unavailable evidence” distinct: a tool crash is not a counterexample to the domain invariant.

## Evidence ledger

Keep a temporary accounting of the obligations and their evidence. A short assessment can use a few sentences; use a table when sources or evidence strengths differ:

| Obligation | Provenance | Artifact or command | Result | Supports | Pending or limits |
| --- | --- | --- | --- | --- | --- |
| The scoped predicate holds over the explored states. | Supplied | Requester's run description | Reported passing states | No violation was reported among explored states. | Inspect completion and truncation evidence before claiming exhaustive traversal. |
| A required boundary check rejects a forbidden input. | Proposed | Planned boundary test | Not run | No execution conclusion yet. | Run against the recorded implementation and check its valid control. |

**Supplied** means stated by the requester without independent inspection. **Observed** requires an inspected artifact or completed tool result. **Proposed** checks have no result yet. Preserve these distinctions when quoting or summarizing a result; an observed log can still leave the implementation's coverage unestablished.

For behavioral obligations, organize the record as:

> Authority and logical form → input representation and boundary → final outcome and evidence → baseline outcome and evidence, when claiming compatibility → supported wording and exceptions.

A sentence can carry this record for a small task. Keep successful-result postconditions, non-success requirements, and named-error requirements distinct. An observed outcome alone does not authorize a new maintained promise. Retain input representations and failure paths even when they share a business meaning. Source inspection can support a broader scoped argument; sampled outcomes alone cannot. After implementation checks, read back changed behavioral text and derive its wording from this record, including baseline evidence for claims of preserved behavior.

Before returning, reconcile these notes with the tool trace and final plan. Every relevant completed check and every applicable pending obligation must remain accounted for. Each conclusion needs supporting evidence of the stated strength. Do not move an unconfirmed prerequisite into a conclusion merely because the named method ordinarily requires it. This ledger is a task-report aid, not another project registry.

For a confirmed bypass, specify the same-boundary regression and valid control. When repair advice is requested or offered, connect it to that evidence:

| Boundary and counterexample | Repair | Same-path regression and valid control | Status and remaining paths |
| --- | --- | --- | --- |
| Restoration accepts data that construction rejects. | Route restored data through the checked construction boundary while preserving its wire shape. | Reject the predicate-reaching invalid payload; retain a fixed historical payload and current round trip. | Proposed until run against the repair; inspect any other construction and mutation paths separately. |

Verification-only work can stop at the counterexample, checks, and limits. If recommending a repair, keep partial defenses distinct and identify their remaining bypasses. Read-only work may explain a requested repair without applying it. Claims about cleanup or other performed actions also need completed tool results.

## Focused claim review

For implementation work, use an available reviewer focused on correctness to reconcile changed behavior-bearing artifacts and the complete final response draft. Follow the [claim-check return contract](../SKILL.md#4-execute-the-claim-check), including its complete reviewed response and incomplete-review handling. This is the completion check, not an additional whole-change audit. A review already covering the same final snapshot, evidence, and response draft satisfies it. A claim-only request creates no task items; when hardening or a broader correctness review already covers the change, attach the obligations to that review and retain its authorized ordinary defect scope and finding reporting separately. Do not add another reviewer or loop. Preserve the caller's model policy.

Give the reviewer the authoritative obligations, exact changed paths and final contents (including untracked files), baseline source or evidence when comparing behavior, completed-check results, known limits, and the complete response draft. Label missing baseline evidence as unavailable. The draft is transient handoff content; do not create a maintained report file or registry for it.

The reviewer extracts claims in project text verbatim from changed or behaviorally affected statements in the supplied final artifacts within task scope, and claims in the final response from the complete draft. Project-text records start with the actual quotation and path and line; response records cite draft sections. Implementation summaries and draft sentences cannot substitute for project text; relevant maintained sources include docstrings, comments, documentation, error messages, manifests, and workflows. Group equivalent repeated claims in one record with every occurrence and location; separate claims with different conditions, domains, or conclusions. Test names and implementation labels are evidence unless they independently assert a contract. It does not audit unrelated unchanged documentation.

The reviewer returns **Claims in project text (maintained claims)**, **Claims in final response (report claims)**, and **Reviewed response** as defined by that contract. Each claim receives **supported** when scoped evidence establishes it, **contradicted** when scoped evidence supplies a counterexample, or **unestablished** when available evidence cannot decide it. Each disposition names the evidence or gap and minimal supported wording or pending obligation. Respect stated conditions and exclusions; when the domain is ambiguous, record the uncertainty instead of silently broadening it. Tested examples and evidence limits do not silently narrow a maintained claim's domain: if only narrower wording is supported, disposition the exact claim accordingly. A counterexample within the established domain contradicts a claim without separate proof that current callers exercise that case.

For each claim, distinguish its source location from its independent authority. Record whether an independent obligation authorizes the claim or the implementation or response draft introduced it. Introduced text is an assertion under review, not authority to expand behavior. For an unsupported introduced assertion, return one minimal supported textual correction or removal. For a violated independently authoritative obligation, record the counterexample and required caller work; do not propose a repair alternative. Assess any caller-authorized behavior change against that obligation's domain and evidence.

Use this bounded contract with the existing reviewer's instructions:

> Remain read-only. Extract claims in project text verbatim from changed or behaviorally affected statements in the scoped final artifacts, citing path and line; do not substitute implementation summaries or draft sentences. Extract claims in the final response separately from the complete draft, citing its sections. Group equivalent repeated claims in one record with every occurrence and location; separate claims with different conditions, domains, or conclusions. Treat test names and implementation labels as evidence unless they independently assert a contract. Mark every claim supported, contradicted, or unestablished and keep the categories separate. For each claim, distinguish independent authority from text introduced by this change or draft. Inspect scoped source, tests, and supplied baseline as needed. Respect stated conditions and exclusions; record ambiguous domains as uncertain. Tested examples and evidence limits do not silently narrow a maintained claim's domain; if only narrower wording is supported, disposition the exact claim accordingly. Keep successful-result, non-success, and named-error claims distinct, and check compatibility claims against baseline and final outcomes. For unsupported introduced text, give only minimal supported wording or removal; do not offer code or test changes to make it true. Record a violated independently authoritative obligation with its counterexample and required caller work, not a repair alternative. Return Claims in project text (maintained claims), Claims in final response (report claims), and Reviewed response under the skill's claim-check return contract, using its quotation-first table columns: preserve the complete supplied draft with only supported wording corrections and retain required obligations as pending where unestablished. Identify missing or incomplete inputs or unresolved contradictions as an incomplete review. In a claim-only request, return those sections inline, create no task items, then stop; do not run the ordinary defect workflow. In a broader existing review with attached claim obligations, retain the review's authorized ordinary findings separately. Do not build, test, edit, delegate again, add infrastructure, or audit unrelated concerns during a claim-only request.

Require a completed result covering every derived claim before calling the check performed. If independent review is unavailable or fails, use direct extraction and inspection with the same record shape and record that method. Correct, narrow, or remove unsupported assertions about present behavior; do not change production behavior or add tests solely to preserve introduced text. Retain authoritative required obligations as normative when unestablished and mark their verification or implementation pending; a registry does not cache verified assertions.

Post-review edits to behavior-bearing final artifacts must use the record's minimal supported wording. If an edit adds or materially broadens a behavioral statement, derive and disposition that affected maintained claim against the same evidence before completion; this does not start another review cycle.

A behavior-changing correction requires independent task or contract authority, affected applicable checks to run again, and affected records and draft wording to use their actual results; it does not require another reviewer or audit cycle.

Resolve the records and apply any remaining supported corrections to the returned **Reviewed response**, check only affected records against the same evidence, and emit that response rather than rebuilding it from claim records. Post-review additions are limited to formatting and completion metadata copied from the completed review receipt or required follow-up check results; omit new or materially broadened behavioral claims.

Completion requires those resolutions and explicit pending obligations. Fully supported records remain fallible evidence, not proof.

## Execution report

Keep execution evidence separate from the maintained obligation manifest. Include:

- Invariant identifier or precise statement, authority, and scoped boundaries.
- Enforcement mechanism and the paths it covers.
- Revision and working-tree status; for a dirty tree, a reproducible snapshot or input hashes. A commit identifier alone cannot identify uncommitted inputs.
- Toolchain, relevant configuration, exact command or artifact, and observed result.
- Model/input bounds, assumptions, truncation, and implementation linkage where relevant.
- Unchecked paths, unavailable checks, counterexamples, and the next action warranted by the task.

When connecting a requested CI check, start with the project's existing check command and preserve its flags and working directory unless a demonstrated need requires a change. Verify that exact invocation with the relevant configuration. A nearby command that passes supplies local evidence only until its equivalence to the CI invocation is established. If the exact invocation cannot run because its tool or environment is unavailable, report CI execution as unavailable; do not treat another command's success as CI acceptance.

CI must obtain every referenced checker from the checkout or a declared, reproducible dependency. A path into an agent's local plugin installation is not portable. For an authorized project-owned copy, treat the bundled checker as read-only input: read its contents and write the project destination with the available file tools. Confirm the destination exists, then execute the exact CI invocation. If an operation is denied, inspect the stated reason and respect that boundary. Do not re-express the denied operation through other tools. Proceed with a narrower action only when the denial clearly permits it; otherwise report the blocker and do not present an incomplete workflow as working CI.

When copying a checker into a project, compare bytes or digests before calling it unchanged. Added attribution or documentation still changes the file; describe it as adapted when appropriate. Record the source and any changes separately from evidence that the copied checker behaves correctly.

When the task creates or updates maintained contract documents, compare their statements with the production boundary, tests, and manifest assumptions or exclusions. Check both the accepted domain and promised failure behavior. Correct conflicting wording within the authorized scope; explaining the discrepancy only in the final response leaves future callers with a false contract.

For example: “The client fixture cannot construct a validated quantity directly under the recorded compiler settings. Its valid factory control compiles. Decoder tests reject zero and negative inputs. Privileged module code and foreign interfaces were not checked.” This says more than “the type is safe” and is easier to keep accurate.

Evidence becomes stale when relevant source, configuration, toolchain, model, or assumptions change. Re-run affected checks; do not let a stored success label silently survive those changes. A manifest validator can establish well-formed obligations and existing paths, not the truth of the statements or currency of attached results.

Keep the final report at the same evidence level as the analysis. When a run only says its explored states passed, report “all explored states passed within the stated bounds; exhaustion and truncation are unconfirmed.” Do not upgrade that to “exhaustive within bounds” in a concluding sentence. Recommend confirming completion as a next check without writing as though it already happened.

## Proportional persistence

Use a task report for a normal investigation. Maintain a project registry when there is an existing registry or a requested lasting verification contract, such as CI obligations spanning implementations. Keep identifiers stable, use project path conventions, and remove or revise obligations when the domain contract changes. Avoid parallel lists that compete with an existing specification.

Read-only verification may inspect existing reports and suggest concrete checks. It does not authorize editing production, creating a registry, installing dependencies, or changing CI. An evidence gap can be reported without turning it into a refactoring task.

## Formal escalation

Formal methods can discharge a precisely encoded property, but encoding the right property and connecting it to production remain obligations. Consider escalation when a high-consequence invariant resists an understandable structural or finite-state argument. Name the desired proof and its maintenance owner before choosing a tool.

Record model/specification sources, assumptions, axioms, trusted code, toolchain, and the implementation mapping. If code is generated or extracted from a verified model, include that transformation and its trusted boundary. If the proof covers a handwritten model, say how drift from production is checked. For an example of a language with proof obligations, see the [Dafny reference](https://dafny.org/latest/DafnyRef/DafnyRef.html); no proof tool is required by this skill.

## Completion checklist

- Any installed companion required by the language-specific boundary has been loaded and its rules applied.
- The domain contract defines “incorrect,” and the claim has a finite scope.
- Construction, decoding, mutation, transition, and external boundaries relevant to the claim are accounted for.
- Evidence uses production code or states its model-only limit.
- Valid controls distinguish intended rejection from broken fixtures.
- Results identify the checked snapshot and configuration.
- Conclusions and pending checks map to the reconciled evidence ledger, with supplied assertions distinguished from observed results.
- Bounds, assumptions, gaps, and unavailable checks are explicit.
- The conclusion distinguishes enforcement from evidence and does not promise whole-program correctness.
- Persistence and changes remain within the authorized task.

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

## Execution report

Keep execution evidence separate from the maintained obligation manifest. Include:

- Invariant identifier or precise statement, authority, and scoped boundaries.
- Enforcement mechanism and the paths it covers.
- Revision and working-tree status; for a dirty tree, a reproducible snapshot or input hashes. A commit identifier alone cannot identify uncommitted inputs.
- Toolchain, relevant configuration, exact command or artifact, and observed result.
- Model/input bounds, assumptions, truncation, and implementation linkage where relevant.
- Unchecked paths, unavailable checks, counterexamples, and the next action warranted by the task.

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

- The domain contract defines “incorrect,” and the claim has a finite scope.
- Construction, decoding, mutation, transition, and external boundaries relevant to the claim are accounted for.
- Evidence uses production code or states its model-only limit.
- Valid controls distinguish intended rejection from broken fixtures.
- Results identify the checked snapshot and configuration.
- Bounds, assumptions, gaps, and unavailable checks are explicit.
- The conclusion distinguishes enforcement from evidence and does not promise whole-program correctness.
- Persistence and changes remain within the authorized task.

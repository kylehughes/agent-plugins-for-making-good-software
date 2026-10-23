# Fable review of the Swift consolidation

Review date: 2026-10-20. Model identity was verified from the native receipt as `claude-fable-5-1`, medium effort. The review used only Read, Grep, and Glob. This is a historical static review; its statement that native runs were pending reflects the time it was written. The [consolidation record](swift-type-system-consolidation.md) separately reports completed native results and follow-up edits.

## Initial consolidation review

**Verdict: APPROVE WITH NONBLOCKING FOLLOW-UPS.** Static read-only review of the working tree against baseline 8b93376, using Read, Grep, and Glob only. I found no release blockers. Every route the skill body and recipes depend on resolves to an existing heading or explicit ID in the current files. Each destination contains the moved content rather than just naming it, and the Apple Platform plugin remains usable alone.

## Findings

No P0 through P2 findings. The items below are optional.

- **Residual "Swift 6.3 is current" statements outside the diff.** `plugins/apple-platform/skills/using-swift-concurrency/references/sources.md:3` says the skill is written for the 6.3 era and should be refreshed when 6.4 changes defaults, which now contradicts the skill body's deferral to feature status, where 6.4.1 is current. Sibling skills say "Target Swift 6.3" at `organizing-swift-types/SKILL.md:12`, `ordering-symbols/SKILL.md:16`, and `configuring-ios-content/SKILL.md:8`. The renamed `concurrency-model.md:226` keeps "Swift 6.3-only code". The modeling skill's `scripts/audit_project.py:243` and `scripts/validate_skill.py:294` still name a "current Swift 6.3 baseline". None of these produce wrong Swift advice today, but they are the remaining places the next release must touch.
- **The consolidation doc ships a placeholder.** `docs/swift-type-system-consolidation.md:71-74` says verification results and this review "are recorded here after" the snapshot check. Fill it in or reword before committing so the doc does not promise content it lacks.
- **Decision-guide table routes two concerns to whole files.** `references/decision-guide.md:21-22` send generic and ownership problems to the full recipe files while `SKILL.md:59-64` route to sections. Harmless because both recipe files open with a family table, but aligning the two entry points would remove one inconsistency.
- **Unused import.** `scripts/check_swift_type_system_integration.py:14` imports `heading_anchor` and never uses it.

## Assessment against the requested criteria

**Ownership is substantive.** The construction examples moved out of the recipes into the mechanism owner: `Patch` and `NonEmpty` now live under `algebraic-and-refined-values.md:73-96`, and `NonblankLabel` with its draft under `:177-193`. Equality and public-evolution rules moved into `domain-modeling-recipes.md:265-285`. The ownership-operation table was merged with the `borrowing`, `consuming`, and `inout` rows in `ownership-concurrency-errors.md:258-268`. The destruction questions moved into the completion recipe at `ownership-effect-recipes.md:273-281`. The decision guide now defers its checklist, lock, resource, and security sections to owners that carry the same substance, which I confirmed at `security-and-resource-modeling.md:5-17` and `:199-227` and `ownership-concurrency-errors.md:12-25` and `:128-146`.

**Recipes and mechanics form a conditional hierarchy.** The skill body routes eight claims to sections. Each recipe links down to a mechanism section only for a named condition, and each mechanism guide opens with a short "read the applied section when assessing an invariant" list. The typestate transition text now points at the recovery recipe, and the resource mechanics point at the completion recipe, addressing the missing reverse links the prior review flagged.

**No current temporal conflict inside the changed set.** Feature status is the single dated owner at `swift-feature-status.md:5-7` and `:23`. iOS versioning, the modeling sources index, the concurrency baseline, and the new Swift compatibility reference all link there instead of restating a snapshot. The preserved 6.3.2 survey sits in `docs/swift-type-system-source-decisions.md:33-85` and is labeled as historical. The only residual conflicts are the pre-existing sibling statements listed above.

**Plugin stays self-contained.** Cross-skill links stay inside `apple-platform`. The Universal procedure is referenced as `verifying-invariants` "if installed", which also fixes the Claude-style namespacing the prior review noted.

**Research and examples remain available.** The ledger rows I sampled (ALG04, ALG06, VAL01 through VAL05, VAL15, VAL18, worked examples 1 and 2) point at sections whose content matches the row's stated reason. Both frozen case IDs named in the new quality scenarios exist in `evals/swift-type-integration/cases.json`.

**Route traces.** Validated decoding, recovery, correlated generics, result sorts, static dimensions, borrowed lifetimes, typed errors, and completion each resolve from `SKILL.md:57-64` to an existing anchor. Near misses stay diverted by the description's exclusions and the existing negative trigger cases.

**Link gate.** `scripts/validate.py:378-403` now runs `link_errors` over every skill entry point, reference, and agent file. The shared helper handles ATX and setext headings, explicit IDs, duplicate suffixes, fences, frontmatter, inline code, reference definitions, and encoded paths, and the tests in `scripts/test_markdown_links.py` exercise each. The coverage checker imports the same anchor function, so ledger destinations and skill routes agree. CI invokes both without `-I`, so the sibling import resolves.

**Rename and version.** All inbound paths to the two deleted references were updated; the only remaining mentions are in historical eval snapshots, which should stay frozen. The 2.0.0 bump moves together in the marketplace entry and both plugin manifests. Skill and agent names are unchanged.

## Prior follow-ups and evidence limits

All seven prior follow-ups are addressed: forward links, fragment validation, section-level hot routes, provenance moved to `docs/`, snapshot deduplication, the reflow-fragile one-liner now a bullet list at `ownership-effect-recipes.md:48-55`, and skill-local evals extended with a pointer to the frozen suite.

I did not run the validator, unit tests, coverage checker, catalog script, or any native evaluation. The twelve pending runtime cases are not evidence for this review and I make no claim about them. Anchor validity was checked by listing headings and applying the slug rules by hand, not by executing the checker. I did not verify Swift or Xcode release facts, and I did not open the source archive.

## Verification of follow-up corrections

**Verdict: APPROVE.** Bounded static verification of the follow-up corrections, using Read, Grep, and Glob only. The edits resolve all four optional findings from my initial review. I found no concrete new problem or loss of source substance.

**Status of each correction**

- **Residual Swift 6.3-current and iOS 27-beta assumptions: resolved.** A plugin-wide search for "Swift 6.3 is the", "-only", "-era", "baseline", "Target Swift 6.3", "iOS 26/27", "beta SDK behavior", and "6.4+ syntax" returns no hits in the previously flagged files. Six sibling files now link to the feature-status reference's release matrix, and that heading exists at `swift-feature-status.md:21`. The two audit and validator messages now describe a fixture minimum rather than a current baseline, which matches the manifest check that still requires 6.3.
- **Verification placeholder: resolved.** The report now records the test and validator outcomes, the twelve native runs, the single Codex failure with no accepted replacement, and the explicit statement that the final wording repairs postdate the snapshot. Both linked records exist on disk.
- **Decision-guide whole-file routes: resolved.** The three replacement rows target seven anchors. All seven are explicit HTML IDs in the two recipe files, and the skill body routes at `SKILL.md:59-64` use the same targets, so the two entry points now agree.
- **Unused import: resolved.** The integration checker no longer references the anchor helper.

**App Intents wording.** The edited availability paragraph preserves the dated 26.5 SDK symbol-absence evidence and drops the beta inference. The remaining "iOS 27-era" phrasing in four sibling references is tied to "selected-SDK-gated" language and does not assert preview status, so it does not conflict with the feature-status statement that Xcode 27 ships the iOS 27 SDK.

**Native evidence.** The results record contains the failed Codex typed-error receipt with a specific behavior failure reason and passing scope, evidence-honesty, and composition entries. The report's description of that outcome matches the record.

**Scope and evidence limits.** I did not run the validator, unit tests, coverage checker, plugin validators, or any native evaluation. Anchor and link checks were done by reading headings and IDs, not by executing the checker. The native runs predate these wording edits, so this verdict covers organization, ownership, and currentness of the final text only. I did not verify Swift or Xcode release facts independently, and I make no claim that all behavioral cases pass.

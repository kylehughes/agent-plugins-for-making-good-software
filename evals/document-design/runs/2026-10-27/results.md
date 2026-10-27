# Document-design development comparison — 27 October 2026

The provisional implementation adds `designing-documents` to Universal 1.11.0: a 1,154-word core, four selectively loaded references, Codex metadata, and conditional composition with the existing technical-prose skill and reviewer. No new reviewer or publishing system was added.

The comparison suggests useful local-condition placement in these generated documents, but does not validate human benefit or establish a stable advantage over existing guidance. Repeats also exposed an unsupported UI-location assumption and a shared navigation gap. Those observations prompted two narrow checks in the core; focused post-tuning results are recorded separately from the paired comparison.

## Design and exposure

The [frozen manifest](../../manifest.json) contains eight synthetic packets with evaluator keys outside producer input. Cases 01–06 were development cases; 07–08 remain unrun and were not exposed to producers or the independent reviewer. The protocol's evidence-label revision occurred before judging; packet/key bytes did not change.

Each arm used GPT-6.1 Sol at medium effort through native subagents. Both received identical source packets, the pre-change technical-prose skill and references from commit `3d282c2938c86be5bf7733f110d1003fd62ff7c2`, and the same local human-prose guidance. The intervention added the document-design core and selected references. Producers reused the frozen technical-prose version when composition linked back. Thus this comparison isolates adding the core, not the complete updated prose integration.

One fresh agent per arm produced six cases sequentially. After the first review, fresh producers repeated cases 05, 01, and 03, without previous outputs, findings, or keys. This repeat selection followed the observed concerns; it was not a preregistered sampling plan. Neither batch tuned the skill before producing its outputs. Explicit read scopes and copied inputs separated producer material, but filesystem access was not sandbox-enforced. Producers reported no excluded reads. Shared runtime instructions/catalogs and within-batch carryover are confounds.

An independent source-informed reviewer received opaque labels, keys, and outputs, but not the arm mapping. It judged supported task paths and predicted risks, not naive-reader answers. [Run metadata](run.json) records mappings, guidance/output hashes, raw response word counts, original document counts, actual reference reads, and limits. Timing and token telemetry are unavailable. Raw outputs are retained unchanged.

## Paired findings

| Case | First pair: baseline → added skill, words | Editorial result |
| --- | --- | --- |
| 01 Adoption | 335 → 362 | The baseline placed the sync-copy warning after the first build; the added skill placed it at index selection. |
| 02 Explanation | 291 → 338 | Both supported the required relationships and boundaries; editorial tie. |
| 03 Procedure | 369 → 357 | The baseline's direct Pause entry bypassed earlier checks; the added skill kept them in the action section. |
| 04 Reference control | Original 155 → original 155 | Both returned a review accepting the existing reference without rewriting it. |
| 05 Page set | 556 → 609 | The baseline's direct Publish entry required a later scan for private Preview context; the added skill supplied it locally. |
| 06 Short-guide control | Original 134 → original 134 | Both left the guide unchanged. |

Counts include Markdown; page-set counts include response wrappers. Controls use the unchanged reader artifact, not the much shorter acceptance response. The underlying starting documents for 01, 03, and 05 were only 76, 72, and 75 words. Both arms added supplied facts to complete them. These are authorized-content-completion comparisons, not evidence of an isolated rearrangement effect. Supported reasoning included the stale-index explanation, state-dependent pause choice, and restore-to-draft-to-public relationship. No unprovided product guarantee was identified in the first pair.

The [first editorial report](editorial-comparison.md) retains supporting passages and remedies. It predicts three local placement risks; it does not report observed reader failures.

The [repeat report](repeat-comparison.md) found the same placement differences in the three repeated cases. It also found two limitations:

- Both adoption outputs moved refresh instructions before the preserved Query syntax heading without a local return route. A resolving anchor did not preserve task access.
- The added-skill procedure assumed that the Pause control was on the tab used to verify its result. The source did not establish that location. This is an unsupported procedural detail, not a demonstrated false UI claim.

Repeated baseline → added-skill raw word counts were 356 → 392 for adoption, 411 → 480 for the procedure, and 676 → 643 for the page set. Greater length was neither rewarded nor treated as a defect by itself. The repeat adds evidence about these artifacts, not independent topics or human readers.

## Narrow revision and focused check

The core now explicitly treats interface locations as factual claims and rechecks preserved headings after moving material. The original paired outputs and hashes remain intact. Both additions passed scoped review for consistency with the supplied design.

A fresh treatment-only producer then completed cases 01 and 03 using the final core and the same baseline guidance, without prior outputs or findings. [Final adoption output](final-01.md) keeps refresh instructions at Query syntax and the storage condition before building. [Final procedure output](final-03.md) retains the local prerequisite route and does not assign Pause an unsupported tab location. The [focused review](focused-review.md) records the source-and-task assessment. This is a post-tuning regression check on development cases, not a fresh paired or held-out effectiveness result.

## Verification and remaining evidence

[Verification metadata](verification.json) records 176 passing repository tests, the passing repository validator, all six JSON manifests, both Claude plugin validations, skill-creator validation, description budgets, and runtime discovery checks. Codex loaded all 29 plugin skills with no reported errors in an isolated test home. Claude initialization with the local plugin exposed all ten universal commands, including the new skill and alias. Neither check tested automatic model selection. Reviewer-role availability was checked separately; the task used shared reviewer instructions on a native agent.

Mechanical checks preserved the required README destinations and heading, and resolved the generated page sets' internal file/anchor links in both batches. They do not establish external link validity, semantic preservation, or comprehension. Independent reviews found no actionable implementation defect in the scoped skill, integration, manifests, and development evaluation materials. No code was added, so code simplification did not apply.

No human sessions, naive model-reader trials, no-document controls, retrieval-time measurements, delayed retention tests, or component ablations were run. Source-informed editorial review cannot supply those outcomes. The literature rationale preserves the supplied report's inspection limits and was not independently reverified. Next empirical work is the frozen held-out comparison and intended-reader sessions; neither is a prerequisite to describing this implementation as provisional.

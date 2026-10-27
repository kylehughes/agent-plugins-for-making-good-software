# Documentation

Start with the [repository README](../README.md) to install the plugins, choose a
workflow, and find each skill or reviewer. This directory contains maintainer
guides and historical implementation records.

## Maintained guides

| Guide | Use it to |
| --- | --- |
| [Repository guidance](../AGENTS.md) | Change skills, agents, manifests, versions, and validation consistently. |
| [Skill context and discovery](skill-context.md) | Understand catalog metadata, activation cost, and discovery checks. |
| [Agent model selection](agent-model-selection.md) | Keep shared reviewer instructions separate from runtime model and effort settings. |
| [Invariant verification and evaluation](invariant-verification.md) | Use the optional invariant tools and run evaluations with retained evidence. |
| [Document-design evaluation](../evals/document-design/README.md) | Compare reader-task support against existing writing guidance with separate producer packets and evaluator keys. |
| [Composition evaluation procedure](../evals/skill-composition/RUNNING.md) | Declare and assess a new batch of the existing composition scenarios. |

The installed skills and their reference maps define the current workflows.
For Swift support and availability, consult the dated
[feature-status reference](../plugins/apple-platform/skills/modeling-swift-types-for-correctness/references/swift-feature-status.md)
and the toolchain evidence it identifies.

## Historical records

These reports record the source versions, environments, and checks from past
work. They do not verify the current checkout. Some reports and evaluation
inputs have recorded hashes; preserve those files when adding new evidence.

| Record | Contents |
| --- | --- |
| [Swift type-system integration](swift-type-system-integration.md) | Generated source-to-destination ledger for the supplied reference corpus. |
| [Swift source decisions](swift-type-system-source-decisions.md) | Integration decisions and an explicitly archived release survey. |
| [Swift integration validation](swift-type-system-validation.md) | Validation commands, observations, and limits for the integration snapshot. |
| [Swift verification record](swift-type-integration-verification.md) | Recorded coverage and runtime acceptance checks. |
| [Swift type-system review](swift-type-system-review.md) | Review of the integrated reference material and its routing. |
| [Swift consolidation](swift-type-system-consolidation.md) | The consolidation's ownership map, design decisions, and evidence. |
| [Swift consolidation review](swift-type-system-consolidation-review.md) | Independent review and follow-ups for that snapshot. |
| [Hardening release review](hardening-release-review.md) | The Universal 1.9.7 release evaluation, including earlier failures. |
| [Composition results](../evals/skill-composition/results.md) | Recorded composition batches and adjudications. |
| [Original composition protocol](../evals/skill-composition/README.md) | Frozen scenarios, rubrics, and the original run plan. |

An absolute path such as `/tmp/...` in a historical record points to a local
artifact from that run, unavailable in this repository or as a public download.
A digest identifies an artifact but does not give you access to it. When source
archives or transcripts are missing, the reports explain the resulting limits
on reproduction.

## Attribution

Imported and derived material keeps its attribution beside the skill:

- [Configuring iOS content](../plugins/apple-platform/skills/configuring-ios-content/ATTRIBUTION.md)
- [Designing Swift APIs](../plugins/apple-platform/skills/designing-swift-apis/ATTRIBUTION.md)
- [Implementing App Intents](../plugins/apple-platform/skills/implementing-app-intents/ATTRIBUTION.md)
- [Modeling Swift types for correctness](../plugins/apple-platform/skills/modeling-swift-types-for-correctness/ATTRIBUTION.md)
- [Testing Swift code](../plugins/apple-platform/skills/testing-swift-code/ATTRIBUTION.md)

The attribution record for the supplied Swift Type System Companion archive
contains no author or license information. The App Intents attribution refers
to a supplied SDK verification brief that is not included. These gaps remain
unresolved. Crediting a source does not establish permission to redistribute it.

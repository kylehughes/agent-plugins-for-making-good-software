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
| [Composition evaluation procedure](../evals/skill-composition/RUNNING.md) | Declare and assess a new batch of the existing composition scenarios. |

The installed skill entry points and their reference maps define the current
workflows. For Swift support and availability, consult the dated
[feature-status reference](../plugins/apple-platform/skills/modeling-swift-types-for-correctness/references/swift-feature-status.md)
and the toolchain evidence it identifies.

## Historical records

These reports describe the source versions, environments, and checks recorded
in each document. They are not fresh verification of the current checkout.
Some reports and evaluation inputs are bound by recorded hashes; preserve them
when adding new evidence rather than rewriting an old result.

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

An absolute path such as `/tmp/...` in a historical record identifies a local
artifact from that run. It is not a file included in this repository or a public
download. A digest records identity; it does not make the underlying artifact
available. Where source archives or transcripts are not included, the reports
state the resulting reproduction limits.

## Attribution

Imported and derived material keeps its attribution beside the skill:

- [Configuring iOS content](../plugins/apple-platform/skills/configuring-ios-content/ATTRIBUTION.md)
- [Designing Swift APIs](../plugins/apple-platform/skills/designing-swift-apis/ATTRIBUTION.md)
- [Implementing App Intents](../plugins/apple-platform/skills/implementing-app-intents/ATTRIBUTION.md)
- [Modeling Swift types for correctness](../plugins/apple-platform/skills/modeling-swift-types-for-correctness/ATTRIBUTION.md)
- [Testing Swift code](../plugins/apple-platform/skills/testing-swift-code/ATTRIBUTION.md)

The supplied Swift Type System Companion archive has no author or license
information in its attribution record. The App Intents attribution also refers
to a supplied SDK verification brief that is not included. These provenance
limits remain unresolved; source attribution is not a claim of redistribution
permission.

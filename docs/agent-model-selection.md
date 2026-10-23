# Agent model selection

Policy introduced 2026-09-18; runtime documentation checked 2026-10-23.

This repository leaves agent model and effort unset unless measurements justify
pinning them. The caller and host choose the model and effort when these fields
are absent. Honor the user's choices when the runtime supports them.

## Decision

1. Omit `model` and `effort` for ordinary agents. This preserves caller choice,
   environment defaults, and future runtime improvements.
2. Pin either only when repeated reviews show that a specific model or
   effort setting meets the review quality bar at lower cost or latency, or
   prevents a material failure. Record the evidence, compatible effort,
   runtime behavior, user-override impact, and revisit condition in a
   `## Model Selection` section in the agent.
3. Choose models for the task instead of automatically escalating to the
   strongest model. Compare the total cost of a correct review, accounting for
   retries, latency, context use, false negatives, and false positives.

## Runtime behavior

These are host configuration rules, separate from the shared Markdown agent
files in this repository. Check the installed runtime and its current
documentation before relying on a precedence rule.

Claude Code 2.1.251 and later choose the model in this order: caller, definition,
`CLAUDE_CODE_SUBAGENT_MODEL`, then parent. Omitting `model` respects the
environment default; `inherit` bypasses that default. Since 2.1.257, adding
`CLAUDE_CODE_SUBAGENT_MODEL_FORCE=1` forces the environment-selected model for
ordinary subagents. Forks have separate rules. See
[Claude's model selection rules](https://code.claude.com/docs/en/sub-agents#choose-a-model).

Codex native configuration is separate: custom TOML configuration overrides
spawn values; otherwise the order is explicit spawn value, then
`[agents].default_subagent_model` and reasoning settings, then the parent.
Selecting a model can also change its default reasoning effort. See
[Codex subagent configuration](https://learn.chatgpt.com/docs/agent-configuration/subagents).

`model: inherit` is Claude frontmatter, not a portable Codex setting. Codex
custom agents use TOML files under `.codex/agents/` or `~/.codex/agents/`; the
shared Markdown definitions here are not those native registrations. The
[2026-09-18 Codex loader check](skill-context.md#validation-results) verified
skills, not native registration of these Markdown agents. When a named role is
unavailable, pass its instructions to an available native agent and use that
runtime's model controls.

In Claude Code, effort set for an invocation overrides effort in the definition;
`CLAUDE_CODE_EFFORT_LEVEL` takes precedence over both. Per-invocation effort
requires 2.1.292 or later; see [subagent effort](https://code.claude.com/docs/en/sub-agents#choose-an-effort-level).
Effort names do not imply equal compute across models. Check [effort configuration](https://code.claude.com/docs/en/model-config#adjust-effort-level)
instead of translating levels mechanically between runtimes.

## Workload starting points

Use this table to plan which models to compare. It contains starting points,
not measured recommendations. Follow explicit user model requests and runtime
limits. The reasoning and cost categories are local heuristics; they do not
correspond to vendor model tiers or establish equivalence across vendors.

| Agent | Concern | Starting point |
| --- | --- | --- |
| `async-testing-auditor` | Async synchronization and non-occurrence | Strong reasoning when races or timing are subtle |
| `code-standards-auditor` | Codified Swift rules and checks | Balanced; narrow rules are often checkable |
| `information-entropy-reducer` | Swift complexity and cognitive load | Strong reasoning when simplification is subtle |
| `type-driven-design-auditor` | Type invariants and state modeling | Strong reasoning when invalid states or boundaries matter |
| `code-reviewer` | Structural design and architecture fit | Strong reasoning when architecture tradeoffs are material |
| `code-simplifier` | Behavior-preserving simplification | Balanced for local cleanup; strong when risk is unclear |
| `correctness-reviewer` | Correctness, security, compatibility, performance | Strong reasoning as defect risk warrants |
| `technical-writing-auditor` | Developer prose and documentation | Balanced for bounded prose and concrete checks |

Choose based on the work within each role. A narrow rule check or bounded prose
edit may suit a balanced or cheaper model. Correctness, security, architecture,
type invariants, async determinism, and subtle simplification may need stronger
reasoning when the risk justifies it. Where useful, test whether reduced effort
preserves quality before trying a cheaper model.

## Evaluation bar

Evaluate review agents with confirmed or seeded defects and clean near-misses
under fixed scope, tools, and context. Record each model/effort pair and repeat
the runs. Establish a capable baseline before testing cheaper pairs. Check
critical misses, false positives, and compliance with the task requirements
before comparing usage and latency.
"No findings" is not a success signal by itself. Previous routing cases and
Claude smoke fixtures test selection and basic behavior; they are not model
quality benchmarks.

For API model comparisons, keep API rates distinct from subscription quotas.
Record the exact model ID, runtime version, effort, date, and source of usage
measurements with the evidence that justifies a pin. Revisit the pin when the
workload, model, runtime precedence, or available model choices change.
Repository validation checks that an explicit override has a non-empty
`## Model Selection` section;
it does not establish that the evidence in that section is sufficient.

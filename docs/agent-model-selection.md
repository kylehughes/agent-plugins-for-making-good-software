# Agent model selection

Policy introduced 2026-09-18; runtime documentation checked 2026-10-23.

This repository leaves agent model and effort unset unless measured evidence
supports a pin. The caller and host decide what runs when these fields are
absent. Honor user-specified choices within runtime capabilities rather than
silently substituting a plugin author's preference.

## Decision

1. Omit `model` and `effort` for ordinary agents. This preserves caller choice,
   environment defaults, and future runtime improvements.
2. Pin either only when repeated review evidence shows that a specific model or
   effort setting meets the review quality bar at better cost or latency, or
   prevents a material failure. Record the evidence, compatible effort,
   runtime behavior, user-override impact, and revisit condition in a
   `## Model Selection` section in the agent.
3. Do not auto-escalate every task or treat always using the strongest model as
   success. Optimize total cost per correct review, including retries, latency,
   context use, false negatives, and false positives.

## Runtime behavior

These are host configuration rules, separate from the shared Markdown agent
files in this repository. Check the installed runtime and its current
documentation before relying on a precedence rule.

Claude Code 2.1.251 and later resolve model choice as caller, definition,
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

In Claude Code, a per-invocation effort overrides definition effort, while
`CLAUDE_CODE_EFFORT_LEVEL` takes precedence over both. Per-invocation effort
requires 2.1.292 or later; see [subagent effort](https://code.claude.com/docs/en/sub-agents#choose-an-effort-level).
Effort names do not imply equal compute across models. Check [effort configuration](https://code.claude.com/docs/en/model-config#adjust-effort-level)
instead of translating levels mechanically between runtimes.

## Workload starting points

Use this table to plan a comparison, not to choose a proven winner. Follow
explicit user model requests and runtime limits. The reasoning and cost
categories below are local heuristics, not vendor model tiers or claims of
cross-vendor equivalence.

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

The table does not prescribe one model per role. A narrow rule check or
bounded prose pass may suit a balanced or cheaper model; correctness, security, architecture, type
invariants, async determinism, and subtle simplification warrant stronger
reasoning when their risk justifies it. Where useful, test quality at reduced
effort before downgrading the model blindly.

## Evaluation bar

Evaluate review agents with confirmed or seeded defects and clean near-misses
under fixed scope, tools, and context. Record each model/effort pair and repeat
the runs. Establish a capable baseline before testing cheaper pairs. Check
critical misses, false positives, and contract compliance before comparing usage and latency.
"No findings" is not a success signal by itself. Previous routing cases and
Claude smoke fixtures test selection and basic behavior; they are not model
quality benchmarks.

For API model comparisons, keep API rates distinct from subscription quotas.
Record the exact model ID, runtime version, effort, date, and usage source with
the evidence that justifies a pin. Revisit the pin when the workload, model,
runtime precedence, or available model choices change. Repository validation
checks that an explicit override has a non-empty `## Model Selection` section;
it does not establish that the evidence in that section is sufficient.

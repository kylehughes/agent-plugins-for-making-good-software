# Agent model selection

Maintainer note, 2026-09-18.

This repository leaves agent model and effort unset unless measured evidence
supports a pin. Omission is a fallback and override policy, not an adaptive
optimizer: the caller and host still decide what runs. Honor user-specified
choices within runtime capabilities rather than silently substituting a
plugin author's preference.

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

## Runtime facts

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

`model: inherit` is Claude frontmatter, not a portable Codex setting. The
earlier Codex loader check verified skills, not native registration of these
Markdown agents. When a named role is unavailable, pass its instructions to
an available native agent and use that runtime's model controls.

Claude's omitted `effort` inherits session effort; declared effort and operator
caps have their own precedence. Effort names are not equal compute across
models. Check [effort configuration](https://code.claude.com/docs/en/model-config#adjust-effort-level)
instead of translating levels mechanically between runtimes.

## Workload starting points

This is a heuristic starting point, not a measured winner. Follow explicit
user model requests and runtime caps. Current model families are examples:
Astra/Sol and Opus/Fable for hard reasoning; Terra/Sonnet for balanced work;
Luna for narrowly checkable work. These candidates follow the
[OpenAI model catalog](https://developers.openai.com/api/docs/models) and
[Claude model guidance](https://platform.claude.com/docs/en/about-claude/models/choosing-a-model).

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

The table does not prescribe one model per role, and it does not establish
cross-vendor equivalence. A narrow rule check or bounded prose pass may suit a
balanced or cheaper model; correctness, security, architecture, type
invariants, async determinism, and subtle simplification warrant stronger
reasoning when their risk justifies it. Where useful, test quality at reduced
effort before downgrading the model blindly.

## Evaluation bar

Evaluate review agents with confirmed or seeded defects and clean near-misses
under fixed scope, tools, and context. Record each model/effort pair and repeat
the runs. Establish a capable baseline before testing cheaper pairs. Check critical misses,
false positives, and contract compliance before comparing usage and latency.
“No findings” is not a success signal by itself. Previous routing cases and
Claude smoke fixtures test selection and basic behavior; they are not model
quality benchmarks.

For API model comparisons, keep API rates distinct from subscription quotas.
Use the [OpenAI model selection guide](https://developers.openai.com/api/docs/guides/model-selection)
and [Claude's cost and intelligence guidance](https://platform.claude.com/docs/en/about-claude/models/optimizing-for-cost-and-intelligence)
for current provider details, then record the evidence that justifies any pin.

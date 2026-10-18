# Skill context and discovery

Maintainer note, 2026-09-18.

This repository serves one shared skill catalog to Claude Code and Codex. It
has 27 skills and 8 review agents; model-specific forks would multiply upkeep
without improving the underlying guidance. The design separates two costs:

| Layer | What it contains | How it is controlled |
| --- | --- | --- |
| Discovery | Names, descriptions, and paths used to choose a skill | Short, distinctive descriptions and narrow trigger language |
| Activation | The selected body, references, and any agent preloads | Progressive disclosure and conditional same-plugin links |

Measurements use authored Unicode characters, not tokens. They are editorial
measurements for comparison, not claims about fitting a particular host
window. Paths in this document refer to this repository; other plugins and a
crowded work machine are outside the measurement boundary.

The host's listing budget is a separate constraint. Claude Code may retain a
skill's name while dropping its description when the combined metadata exceeds
that budget. Registration alone therefore cannot establish discovery exposure.
The [invariant acceptance launcher](invariant-verification.md#behavioral-acceptance)
sets a supported per-process budget and checks the native diagnostic log for
truncation. It does not preload skill bodies or change user settings. See
[Claude Code's loading model](https://code.claude.com/docs/en/features-overview#understand-how-features-load)
for the distinction between discovery metadata and activated content.

## Context reduction baseline

The baseline commit `f84580d` contained 26 skills with 12,586 description
characters and 8 agents with 3,358 description characters. The catalog at `c3d5df7`
contains 5,022 skill-description characters and 1,630 agent-description
characters: reductions of 60% and 51%. The largest skill description fell
from 848 to 283 characters. Skill entry-point bodies total 243,044 characters,
versus 257,181 in the baseline; examples remain available in references.
Agent preloads total 73,196 characters, versus 195,355 in the baseline, a 63%
reduction. These preload totals are summed across agents, not the cost of one
session. That snapshot used `apple-platform` 1.4.0 and `universal` 1.6.0.
These figures come from `scripts/skill_catalog.py`; they measure authored
Unicode characters and are not token estimates.

The baseline parser exposed a YAML edge case: the unquoted `#expect` in the
Swift Testing description began a comment. The retained scalar ends after
`@Suite,` and measures 65 characters. Discovery descriptions now use one-line
JSON-compatible double-quoted scalars, which preserve hashes, colons, escaped
quotes, and other punctuation.

The largest activation costs are handled by structure. The App Intents skill's
unconditional list of 20 items became a conditional map, and its skeleton
moved out of the activation entry point into conditional reference material.
The general Swift hub now routes to focused Swift guides only when a changed
concern requires them. Agents preload only guides they always need; other
guides are linked and read when a changed concern requires them.

## Lightweight ontology

The ontology is a maintainer map, not a skill loaded by other skills. It keeps
names distinct while avoiding a second catalog of descriptions.

| Concern family | Skills |
| --- | --- |
| General Swift implementation | `writing-swift`, `using-swift-concurrency` |
| Focused Swift conventions | `designing-swift-apis`, `ordering-symbols`, `organizing-swift-types`, `localizing-strings`, `writing-apple-platform-documentation` |
| Invariant obligations and evidence | `verifying-invariants` |
| Swift invariant representations and boundaries | `modeling-swift-types-for-correctness`, `structuring-swift-packages` |
| Test structure and determinism | `testing-swift-code`, `testing-async-swift-code`, `recording-ios-simulator-videos` |
| Apple platform surfaces | `configuring-ios-content`, `presenting-ios-modals`, `instrumenting-accessibility-identifiers`, `implementing-app-intents`, `simplifying-apple-platform-code` |
| Business and release evidence | `analyzing-app-store-business-data`, `auditing-ios-release-size` |
| Workflow: review and repair | `reviewing-code`, `simplifying-code`, `hardening-changes` |
| Workflow: ambiguity and handoff | `brainstorming-design-specs`, `compiling-agent-goals`, `writing-escalation-briefs` |
| Technical prose | `writing-technical-prose` |

`verifying-invariants` owns the cross-language procedure for scoped obligations,
method selection, and evidence limits. Language companions own representation,
construction, access, and compiler details. Testing skills retain assertions and
synchronization; reviewers retain their existing concerns. Conditional workflow
links cover invariant claims and enforcement changes without preloading the new
skill into every agent. See [invariant verification](invariant-verification.md)
for the tooling and acceptance matrix.

The initial invariant-verification addition at `ad72b90` brought the catalog to
27 skills with 5,338 description characters and kept 8 agents. Its entry-point
bodies totaled 253,016 characters and summed agent preloads totaled 74,190.
The follow-up fixes use 5,464 description characters, 264,000 body characters,
and 79,561 summed preload characters. No preload entries were added; the increase
comes from guidance in existing owner skills. The new verifier remains
conditionally loaded, with a 121-line entry point; Swift modeling has 199 lines. The
[validation results](invariant-verification.md#validation-results) distinguish
deterministic tooling checks from runtime activation and response-quality limits.

## Authoring rules

Put the user task or intent in the first sentence of a description. Keep the
rest of the procedure in the body or references. Exclusions belong only when a
near-miss would otherwise trigger the skill. A short description should tell a
model when to select the skill, not summarize every section it contains.

Agent `skills:` entries preload full bodies when the agent starts. Keep only
always-needed owner guides there. Use relative links for conditional guides so
the agent can load precise rules after it sees the changed concern. Preserve
domain rules and progressive disclosure; do not add model-specific prompt
hacks or hide useful coverage merely to reduce a number.

## Research context

Codex limits the initial discovery list to 2% of the model context window,
falling back to 8,000 characters when the window is unknown. It shortens
descriptions first and may omit skills if the list remains too large.
[Codex skills](https://learn.chatgpt.com/docs/build-skills).

Claude's listing budget scales at 1% of context. It keeps skill names and drops
descriptions starting with the least-invoked skills. Each description plus
`when_to_use` is capped at 1,536 characters by default.
[Claude skill descriptions](https://code.claude.com/docs/en/skills#skill-descriptions-are-cut-short).

The portable format has a 1,024-character description limit, which is a format
constraint rather than this repository's target: [Agent Skills specification](https://agentskills.io/specification).

OpenAI's Astra guidance favors short, precise triggers and progressive
disclosure: [rethinking skills and prompts](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra).
The latest-model guidance recommends testing lean prompts against real tasks:
[latest models](https://developers.openai.com/api/docs/guides/latest-model?model=gpt-5.6).
Claude's model guidance emphasizes avoiding generic mandatory verification in
Opus 5 ([Opus 5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5)), literal precise scope in Sonnet 5 ([Sonnet 5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5)), and removing stale formatting constraints in Fable 5.1 ([Fable 5.1](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-1)). Shared instructions therefore preserve domain rules and avoid model-specific tricks.

Claude subagents preload referenced skills at startup, which is why their
`skills:` lists are activation costs rather than labels:
[subagents](https://code.claude.com/docs/en/sub-agents). Description optimization
guidance also recommends testing positive and near-miss triggers:
[optimizing descriptions](https://agentskills.io/skill-creation/optimizing-descriptions).

Host budgets also cover names, paths, formatting, and other installed skills.
The repository's 320-character per-skill and 7,000-character aggregate
description limits are editorial guardrails, not vendor limits or a promise
that any installed catalog fits. Agent limits are 300 and 2,200 characters.

## Evaluation procedure

Run deterministic repository checks first:

```shell
python3 -m unittest discover -s scripts -p 'test_*.py'
python3 scripts/validate.py
python3 scripts/skill_catalog.py --base f84580d
```

`scripts/routing_probe.py` exports and grades fixed cases for
names and descriptions. It does not measure real activation or full response
quality. Use positive cases, near-misses, output checks, three repeats, and a
crowded-catalog spot check on the work machine.

For example, export the self-contained prompt and grade a model response:

```shell
python3 scripts/skill_catalog.py --json > /tmp/skill-catalog.json
python3 scripts/routing_probe.py export \
  --catalog /tmp/skill-catalog.json \
  --cases evals/skill-routing.json \
  --output /tmp/skill-routing-prompt.txt
python3 scripts/routing_probe.py grade \
  --cases evals/skill-routing.json \
  --responses /tmp/skill-routing-response.json \
  --catalog /tmp/skill-catalog.json
```

For native Claude discovery smoke tests, use the reviewed local repository and
the plugin evaluation command documented at [plugin evals](https://code.claude.com/docs/en/plugin-evals):

```shell
SLASH_COMMAND_TOOL_CHAR_BUDGET=24000 \
claude plugin eval plugins/<plugin> --eval-dir evals/discovery-smoke --ablation none --runs 3 --model claude-sonnet-5-5 --no-publish --no-scaffold --trust-plugin --output-dir /tmp/plugin-eval
```

Compare old and new versions from isolated temporary copies using the same
fixtures. A no-plugin baseline answers a different question and should not be
treated as a plugin comparison. Native Codex discovery smoke tests should be
reported separately; agent registration introspection is unavailable in that
path, so do not claim it.

## Validation results

Results below compare `f84580d` with the revised content. The compact
[machine-readable results](../evals/skill-context-results.json) retain scores
and limitations; generated transcripts and HTML reports stay outside the repo.

- All 16 tooling tests and the repository validator pass. Claude Code 2.1.277
  validates both plugins' manifests, agents, and skills. All six JSON manifests
  parse, relative reference files resolve, and the diff passes whitespace checks.
- Codex CLI 0.155.1 discovers both marketplace entries and loads all 26 enabled
  skills with zero errors in a temporary Codex home. This checks metadata loading,
  not model invocation; the protocol does not expose agent registration.
- One 36-case description-selection probe per model and catalog, at medium
  reasoning, scored 35/36 → 36/36 for GPT-6 Astra and 36/36 → 36/36 for GPT-5.6
  Sol, Terra, and Luna. Astra's baseline extra selection was a simplification
  skill for a defect review. These are selection probes, not native activation
  or implementation-quality tests. A Terra run contaminated by a personal prose
  skill was discarded; both arms were rerun with that skill disabled.

Native Claude runs use isolated plugin copies, identical prompts and graders,
and three repetitions per case, extended to nine for Fable's README case.
The table reports requested skill activation, baseline → final:

| Model | Modal review | Swift Testing | Code review | README revision |
| --- | --- | --- | --- | --- |
| Sonnet 5 | 3/3 → 3/3 | 3/3 → 3/3 | 0/3 → 0/3 | 0/3 → 0/3 |
| Opus 5 | 3/3 → 3/3 | 3/3 → 3/3 | 0/3 → 0/3 | 3/3 → 3/3 |
| Fable 5.1 | 3/3 → 3/3 | 3/3 → 3/3 | 0/3 → 0/3 | 8/9 → 8/9 |

All 102 runs in that final comparison pass the basic output checks; every
arithmetic run avoids skill invocation. The activation misses remain failures
of the corresponding smoke graders, even when the answer passes. Tiny review
tasks are still often answered directly. The graders check a few output
properties, not complete correctness or execution of generated tests.

An initial 175-character prose description reduced Fable's README activation
from 8/9 to 3/9. Restoring explicit editing, normalization, and clarity triggers
produced the final 283-character description and the 8/9 result above. Shortest
is not the objective. This case informed the revision, so it is not a held-out
quality estimate.

These samples do not establish statistical equivalence, full-task quality, or
behavior under the work machine's crowded catalog. The remaining deployment
check is to load these versions there, inspect the discovery warning and catalog,
and try representative work tasks with the other installed skills present.

# Skill context and discovery

Context-reduction study, 2026-09-18; maintainer guidance updated 2026-10-23.

This repository serves one shared skill catalog to Claude Code and Codex.
Model-specific forks would add upkeep without improving the guidance. Run
`python3 scripts/skill_catalog.py` from the repository root for current counts
and authored character measurements. The catalog has two context costs:

| Layer | What it contains | How it is controlled |
| --- | --- | --- |
| Discovery | Names, descriptions, and paths used to choose a skill | Short, distinctive descriptions and narrow trigger language |
| Activation | The selected body, references, and any agent preloads | Progressive disclosure and conditional same-plugin links |

Measurements use authored Unicode characters, not tokens. They help compare
revisions; they do not establish whether a catalog fits a particular host
window. Paths in this document refer to this repository; other installed plugins
and skills are outside the measurement boundary.

The host's listing budget is a separate constraint. Claude Code may retain a
skill's name while dropping its description when the combined metadata exceeds
that budget. Registration alone therefore does not show whether the model saw a
description. The [invariant acceptance
launcher](invariant-verification.md#behavioral-acceptance) sets a supported
per-process budget and checks the native diagnostic log for truncation. It does
not preload skill bodies or change user settings. See [Claude Code's loading
model](https://code.claude.com/docs/en/features-overview#understand-how-features-load)
for the distinction between discovery metadata and activated content.

## Invocation policy

Every shipped skill allows automatic selection and direct invocation in both
supported hosts. Keep the defaults: Claude Code's `disable-model-invocation`
is false and `user-invocable` is true; Codex's `allow_implicit_invocation` is
true. Omitted fields use those defaults. The repository validator rejects
opt-outs. See [Claude's invocation controls](https://code.claude.com/docs/en/skills#control-who-invokes-a-skill)
and [Codex skill metadata](https://learn.chatgpt.com/docs/build-skills).

Availability does not guarantee selection. Lead each description with its
concrete job, name the prompt or changed concern that should trigger it, and
reserve exclusions for likely near-misses. Test both matching requests and
near-misses. An instruction to use a guide proactively should remain scoped to
that guide's job; it does not authorize edits, publishing, or extra workflows.

Agent preloads contain complete skill bodies. Reuse preloaded guidance and read
conditional references only when needed. In hosts without a skill invocation
tool, read the same `SKILL.md` and its relative references. This keeps one source
of instructions without requiring every host to register the reviewer role.

## Swift knowledge ownership

The [Swift knowledge-base guide](swift-type-system-consolidation.md) records the
current ownership and routing contract. Entry points select a concern; mechanism
guides explain construction rules; recipes apply them to compound invariants.
Each dated release or availability fact has one owner. Source history and prior
verification reports stay in maintainer documentation, outside ordinary
activation.

The repository validator checks local file targets and Markdown section fragments
in skill entry points, references, and agent instructions. It ignores fenced
examples and source snapshots; it does not verify external URLs or their fragments.
The source-coverage checker uses the same anchor rules for ledger destinations.

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

Changes to the skill structure reduced the largest activation costs. The App
Intents skill's unconditional list of 20 items became a conditional map, and its
skeleton moved out of the activation entry point into conditional reference
material. The general Swift hub now routes to focused Swift guides only when a
changed concern requires them. Agents preload only guides they always need;
other guides are linked and read when a changed concern requires them.

## Lightweight ontology

This map helps maintainers keep skill names distinct without maintaining a
second catalog of descriptions. Other skills do not load it.

| Concern family | Skills |
| --- | --- |
| General Swift implementation | `writing-swift`, `using-swift-concurrency` |
| Focused Swift conventions | `designing-swift-apis`, `ordering-symbols`, `organizing-swift-types`, `localizing-strings`, `writing-apple-platform-documentation` |
| Invariant obligations and evidence | `verifying-invariants` |
| Swift invariant representations and boundaries | `modeling-swift-types-for-correctness`, `structuring-swift-packages` |
| Test structure and determinism | `testing-swift-code`, `testing-async-swift-code`, `recording-ios-simulator-videos` |
| Apple platform surfaces | `configuring-ios-content`, `presenting-ios-modals`, `instrumenting-accessibility-identifiers`, `implementing-app-intents`, `simplifying-apple-platform-code` |
| Business and release evidence | `analyzing-app-store-business-data`, `auditing-ios-release-size` |
| Workflow: delivery, review, and repair | `delivering-changes`, `reviewing-code`, `simplifying-code`, `hardening-changes` |
| Workflow: ambiguity and handoff | `brainstorming-design-specs`, `compiling-agent-goals`, `writing-escalation-briefs` |
| Document design and technical prose | `designing-documents`, `writing-technical-prose` |

`verifying-invariants` owns the cross-language procedure for scoped obligations,
method selection, and evidence limits. Language companions own representation,
construction, access, and compiler details. Testing skills retain assertions and
synchronization; reviewers retain their existing concerns. Conditional workflow
links cover invariant claims and enforcement changes without preloading the new
skill into every agent. See [invariant verification](invariant-verification.md)
for the tooling and acceptance matrix.

The initial invariant-verification addition at `ad72b90` brought the catalog to
27 skills with 5,338 description characters and kept 8 agents. Its entry-point
bodies totaled 253,016 characters and summed agent preloads totaled 74,190. The
historical follow-up snapshot recorded 5,464 description characters, 264,000
body characters, and 79,561 summed preload characters. No preload entries were
added in that follow-up; guidance added to existing owner skills caused the
increase. At that snapshot, the conditionally loaded verifier had a 121-line
entry point and Swift modeling had 199 lines. These figures describe earlier
snapshots, not the current catalog. The [validation
results](invariant-verification.md#validation-results) distinguish deterministic
tooling checks from runtime activation and response-quality limits.

## Authoring rules

Put the user task or intent in the first sentence of a description. Keep the
rest of the procedure in the body or references. Add an exclusion only when a
near-miss would otherwise trigger the skill. A short description should tell a
model when to select the skill, not summarize every section it contains.

Agent `skills:` entries preload full bodies when the agent starts. Keep only
owner guides the agent always needs there. Use relative links for conditional
guides so the agent can load precise rules after it sees the changed concern.
Preserve domain rules and progressive disclosure; do not add model-specific
prompt hacks or hide useful coverage merely to reduce a number.

## Runtime loading and authoring sources

Runtime facts in this section were checked against the linked documentation on
2026-10-22. They can change independently of this repository.

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

Keep shared instructions focused on domain rules and task boundaries. Evaluate
prompt changes against representative tasks rather than adding model-specific
phrasing to the shared catalog.

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

Run these commands from the repository root with Python 3.9 or later and Git
available. The baseline comparison requires repository history containing
`f84580d`; use `--base HEAD` to compare working edits with the current commit.

Run deterministic repository checks first:

```sh
python3 -m unittest discover -s scripts -p 'test_*.py'
python3 scripts/validate.py
python3 scripts/skill_catalog.py --base f84580d
```

`scripts/routing_probe.py` exports and grades fixed cases for
names and descriptions. It does not measure real activation or full response
quality. Use positive cases, near-misses, output checks, three repeats, and a
spot check with other skills installed.

For example, export the self-contained prompt:

```sh
python3 scripts/skill_catalog.py --json > /tmp/skill-catalog.json
python3 scripts/routing_probe.py export \
  --catalog /tmp/skill-catalog.json \
  --cases evals/skill-routing.json \
  --output /tmp/skill-routing-prompt.txt
```

Submit that prompt to the chosen model in an isolated session, without allowing
it to read the case answers. Save its JSON response as
`/tmp/skill-routing-response.json`, then grade it:

```sh
python3 scripts/routing_probe.py grade \
  --cases evals/skill-routing.json \
  --responses /tmp/skill-routing-response.json \
  --catalog /tmp/skill-catalog.json
```

Native smoke tests require an authenticated CLI, access to the chosen model,
and time and usage budget for paid model calls. The example below uses the
model ID recorded by the repository protocol; confirm availability or declare a
separate model comparison. Replace `<plugin>` with `apple-platform` or
`universal`, and choose a new output directory for each batch. Use the reviewed
local repository and the plugin evaluation command documented at [plugin evals](https://code.claude.com/docs/en/plugin-evals):

```sh
SLASH_COMMAND_TOOL_CHAR_BUDGET=24000 \
claude plugin eval plugins/<plugin> --eval-dir evals/discovery-smoke --ablation none --runs 3 --model claude-sonnet-5-5 --no-publish --no-scaffold --trust-plugin --output-dir /tmp/plugin-eval
```

Compare old and new versions from isolated temporary copies using the same
fixtures. A no-plugin baseline answers a different question and should not be
treated as a plugin comparison. Report native Codex discovery smoke tests
separately. That path cannot inspect agent registration, so do not claim to have
checked it.

## Validation results

The 2026-09-18 results below compare `f84580d` with the study snapshot at
`c3d5df7`. They have not been rerun for later documentation or plugin changes.
The compact [machine-readable results](../evals/skill-context-results.json) retain scores
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
produced the final 283-character description and the 8/9 result above. The goal
is a description that triggers reliably, rather than the shortest possible
description. This case informed the revision, so it is not a held-out quality
estimate.

These samples do not establish statistical equivalence, full-task quality, or
behavior with a larger installed catalog. For a deployment check, load the
versions being released in the target runtime,
inspect discovery warnings and the catalog, and try representative work tasks
with the other installed skills present.

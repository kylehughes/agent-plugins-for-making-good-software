# Invariant verification

Universal's `verifying-invariants` skill owns the procedure for specifying scoped
invariants, locating their boundaries, selecting evidence, and reporting limits.
Apple Platform's `modeling-swift-types-for-correctness` owns Swift representations,
checked construction, decoding, access control, and compiler restrictions. Swift
testing skills continue to own assertions and deterministic synchronization.

The following describes the workflow contract, not guaranteed agent compliance.
The [composition evaluation results](../evals/skill-composition/results.md) report
observed behavior and remaining failures separately.

Design, review, simplification, hardening, and goal workflows use this procedure
for concrete invariant claims or enforcement changes. Hardening begins by
investigating domain values and legal transitions introduced, changed, or newly
exposed by its owned work. A concrete gap activates the focused procedure;
cosmetic work does not activate an invariant audit of neighboring models.
Stronger representations must prevent a concrete misuse at a justified cost.

Composition runs within one workflow. Apple companions name their Universal
foundations; Universal skills request platform capabilities without naming a
platform. Active guidance, frozen scope, decisions, and evidence are reused.
Apple simplification directly routes Swift enforcement boundaries to the type
modeling skill and remains usable when Universal is absent.

A bypass and its type-based prevention share one finding and disposition.
Correctness owns failure evidence and impact, the type specialist supplies
representation choices and tradeoffs, and the orchestrator decides the fix.
No reviewer was added and no agent unconditionally preloads invariant verification.
Hardening retains its single compile checkpoint and separate project test gate.
Its handoff names pending invariant obligations, their owner, and the next action;
hardening completion does not establish full invariant verification. Review-only
work does not gain permission to mutate a project.

Implementation tasks choose a bounded claim check before editing. An available
correctness reviewer assesses maintained claims in the scoped final files and
the complete response draft. Equivalent repetitions share a record with every
location; different domains and conclusions stay separate. Each claim receives
a supported, contradicted, or unestablished disposition, separate from runtime
defect findings. When review is unavailable, the calling agent records why and
performs the same inspection directly. An applicable existing review is reused,
and hardening includes these obligations in its existing correctness review.

A claim-only check returns supported wording and counterexamples, without a
separate defect review or repair alternatives. Existing broader reviews retain
their normal defect scope and report claim records separately. Newly introduced
text is an assertion to assess, not authority to expand the requested behavior.

The caller corrects affected artifacts and returns the corrected response draft.
Behavior-changing corrections require affected checks to run again; narrowing
prose uses the existing evidence. Neither requires another reviewer or audit
cycle. Assessment tasks remain direct.

## Tools

The Universal validator uses only Python's standard library. Run it against an
optional project-maintained manifest:

```sh
python3 plugins/universal/skills/verifying-invariants/scripts/validate_invariants.py \
  path/to/invariants.json --root path/to/project --json
```

Its successful exit means the metadata is well-formed and local references exist.
It does not execute check commands or establish correctness. Start from the
[template](../plugins/universal/skills/verifying-invariants/assets/invariants.template.json)
and consult the [format](../plugins/universal/skills/verifying-invariants/references/manifest-format.md).
Execution reports identify the checked snapshot, toolchain, results, and limits
separately. Ordinary investigations need only a task report, not a new registry.

The Swift skill's existing entry point exercises reusable positive controls,
negative compilation fixtures, and runtime examples:

```sh
REQUIRE_SWIFTC=1 plugins/apple-platform/skills/modeling-swift-types-for-correctness/scripts/check_examples.sh
```

Its [compiler-check guide](../plugins/apple-platform/skills/modeling-swift-types-for-correctness/references/compile-check-runner.md)
documents the runner and manifest. Compiler fixtures substantiate production
claims only when they use the production module or shared production sources.
Demonstration examples establish only their own behavior.

## Deterministic validation

Run the repository's normal gate:

```sh
python3 -m unittest discover -s scripts -p 'test_*.py'
python3 scripts/validate.py
python3 scripts/skill_catalog.py --base HEAD
```

The unit suite includes manifest validation and compiler-runner failure modes.
Fake compiler cases check harness behavior; the required Swift run above checks
the real fixture/compiler interaction. Neither substitutes for the other.

## Behavioral acceptance

The [case matrix](../evals/invariant-behavior/cases.json) exercises both runtimes
with the same natural-language prompts. Rubrics and independent assertions stay
outside the responding agent's workspace and are never included in its prompt.

| Installation | Cases | Required behavior |
| --- | --- | --- |
| Universal alone | Decoder bypass, mutable child, stale completion, bounded exploration, missed mutation | Find concrete gaps and bound the conclusion to the available evidence. |
| Apple Platform alone | Swift decoder assessment and implementation | Preserve saved keyed data and validate decoded values without depending on Universal. |
| Both | Swift assessment and implementation | Compose verification and Swift modeling when the request calls for both; keep ordinary fixes scoped. |
| Both | Test organization, async readiness, naming, ordinary defect review | Use the existing owner without activating the invariant workflow. |
| Universal alone | Ordinary import-boundary fix | Fix the source and add tests without creating a registry or CI workflow. |
| Universal alone | Explicit durable contract | Create the requested registry and CI checks; this is the positive control for the ordinary no-registry default. |

Use the [current composition run guide](../evals/skill-composition/RUNNING.md)
for launch, review, and evidence-retention instructions. The suite's original
README preserves the historical initial protocol.

The [composition suite](../evals/skill-composition/cases.json) adds hardening with
an implicit invariant gap, cosmetic-only hardening, and Apple-only simplification
invocation with both plugins installed. Its [frozen criteria](../evals/skill-composition/frozen-criteria.json)
require three independent attempts per case and runtime. Each declared batch has
its own denominator; later passes do not replace earlier failures. The
[prepared protocol](../evals/skill-composition/followup-plan.json) and
[persisted-session protocol](../evals/skill-composition/persisted-plan.json) record
setup corrections and source snapshots separately from those unchanged criteria.

All assessment cases have write tools available. An empty workspace diff
therefore measures scope preservation rather than a tool restriction. The Swift
implementation cases allow source and test edits, but reject an unsolicited
registry, workflow, or configuration change. Their independent executable checks
cover historical keyed payloads, encoded shape, round trips, invalid values, and
the project's own tests. A scalar decoder and a decoder that rejects everything
both fail. Validation-error spelling is not part of the fixture's public contract.
The ordinary Universal implementation case uses the same Python boundary
fixture as the durable case, with source and test edits as its only permitted
changes. Both preserve positive integer, floating-point, and decimal inputs, including
positive infinity. A positive boolean control catches an added category exclusion
that the supplied contract does not authorize. Nonpositive controls enter through
the same import boundary. The durable-contract case also validates the generated manifest with a captured copy
of the canonical validator, then runs project tests and independent boundary
assertions. Review still checks whether the declared obligation and CI workflow
actually match the requested contract. That case permits project-wide file
placement for the requested infrastructure; its scope verdict requires reviewing
the full diff for unrelated changes. The ordinary cases retain strict file
allowlists.

Check metadata exposure separately from plugin registration. Claude Code can
list a skill's name while omitting its description when the combined listing
exceeds the host's budget. This occurred with Sonnet 5.5 on Claude Code 2.1.282:
the CLI treated the unrecognized model as having a 200k context, then truncated
a 10,758-character listing against a 6,000-character budget. A name in the startup
registry did not establish that the model saw the authored trigger description.
The launcher therefore sets a 24,000-character listing budget for each Claude
child through `SLASH_COMMAND_TOOL_CHAR_BUDGET` and retains the native diagnostic
log with its hash. This changes metadata exposure,
not the prompt, expected skill selection, or skill-body preloads. Runs that
cannot confirm an untruncated listing fail verification. No user settings are
modified. The result applies to this recorded configuration; it is not evidence
that the CLI's smaller default budget exposes the complete catalog.
For an interactive installation that reports truncated skill descriptions, the
same [documented environment override](https://code.claude.com/docs/en/env-vars#variables)
can be set when launching Claude Code. The plugin does not change host settings
automatically; other installed skills also consume that host budget.

Run one case in a fresh disposable directory:

```sh
python3 scripts/run_invariant_behavior.py \
  --runtime claude --case combined-decoded-value-readonly \
  --output-dir /tmp/invariant-claude-run --model claude-sonnet-5-5 \
  --effort high --timeout 900
python3 scripts/run_invariant_behavior.py \
  --runtime codex --case swift-decoding-write-combined \
  --output-dir /tmp/invariant-codex-run --model gpt-6.1-sol \
  --effort high --timeout 900 --codex-auth-source "$HOME/.codex/auth.json"
```

For the composition suite, add `--config evals/skill-composition/cases.json`,
choose one of its case IDs, and use medium effort. Add `--fixture-bootstrap` to
prepare its disposable Git baseline and dirty change before the native agent
starts. This opt-in executes the copied fixture script on the host, retains a
setup receipt and streams, and binds them and the source script to the evidence.
The native sandbox stays unchanged; its later bootstrap call is idempotent. A
failed setup prevents native launch. Use this flag only for an inspected,
authorized fixture script.

The launcher creates an unrelated random runtime directory containing the
fixture project, selected plugins without evaluation assets, and temporary
Codex home. It verifies that the plugin copy matches its source and uses native
plugin loading. Grading metadata stays in memory until the child exits; the
bundle and launch record are then written to the separate output directory.
Inherited working-directory hints are removed from the child's environment.
This prevents accidental discovery through neighboring files; it is not a
security boundary against deliberate host filesystem traversal. Claude uses
restricted mode with file editing, shell execution, native delegation, and access
to the copied plugin references. Non-writable configurations omit editing, shell,
and delegation tools. Delegated assistant prose stays in the complete transcript
and is excluded from the root response; child tool calls retain their parent
context. A reviewer invocation alone is not evidence that its review completed.
Codex uses workspace-write for write-capable cases and read-only otherwise.
Write-capable cases retain session files inside the isolated Codex home because
native delegation may need the parent rollout; read-only cases remain ephemeral.
The prepared composition runs recorded missing-rollout errors in native
delegation, so session persistence is part of the subsequent evaluation protocol.
Raw transcripts, responses, stderr,
runtime setup, and every failed or timed-out outcome remain in the output
directory. The runtime directory is retained because evidence binds its live
workspace. `launch.json` records its absolute path and any Codex home. Keep both
directories private; the Codex home may retain an authentication symlink. The
launcher does not install the reviewed plugin changes or publish evaluations.
The native CLI may perform its own background cache maintenance; the disposable
workspace is not an isolation boundary for the host.

A successful process exit is not acceptance. The launcher reports
`pending_manual_review` after deterministic checks pass, and exits nonzero for
execution or artifact failures. It never retries until a case passes. Declare a
matrix and repetition count before running it, retain every attempt, and report
counts separately for execution, behavior, composition, and scope.

The optional `--effort` accepts `low`, `medium`, or `high` and defaults to
`medium`. The launcher records it in both launch metadata and the raw outcome.
Keep the model, effort, tool access, and timeout fixed within a declared run.
Changing those settings creates a separate comparison; a passing high-effort run
does not establish acceptance at medium effort.

### Evidence and review

`scripts/invariant_behavior.py` supports `prepare`, `assess`, `finalize-review`,
and `verify-evidence`. Preparation binds the natural prompt, initial tree, plugin
snapshot, case configuration, rubric, and independent checker. Assessment copies
the resulting workspace once, runs checks against that captured copy, and binds
the complete file map. A later change to the live or captured workspace prevents
finalization. Compiler and runtime failures are failed evidence.
Python artifact checks also reject changes to the tested source tree during
project tests or independent assertions, excluding interpreter caches.
Their validator, project-test, and assertion processes use separate temporary
Python cache prefixes and disable bytecode writes, so those processes do not
write interpreter caches into the captured workspace.
The complete raw diff and file hashes remain in evidence. Only newly added
Python bytecode files directly inside `__pycache__` are excluded from the scope
verdict for Python artifact cases; source files placed there and changes to
preexisting cache files are still assessed. This keeps incidental interpreter
outputs from hiding unrelated edits.
Changes to the selected case configuration or rubric make a prepared run stale;
retain it as historical evidence and prepare a fresh run for current acceptance.

Each new assessment uses evidence schema 2, retains the evaluator source as
`evaluator-engine.py` beside the captured workspace, and requires its version and
SHA-256 in the receipt. `verify-evidence` checks that retained binding, so a
changed or missing evaluator file makes the receipt stale. Legacy schema 1
receipts remain readable but may lack evaluator-engine provenance. These hashes
check artifact consistency; they do not authenticate a receipt's author.

The assessor cannot judge prose or prove that a suggested check was executed.
Review the entire response and completed tool trace against the captured rubric.
Require explicit verdicts for `behavior`, `scope`, and `evidence_honesty`, each
with a reason and concrete response or tool anchors. Record skill composition as
a separate verdict using successful skill loads from the reviewed local snapshot.
A correct diagnosis does not excuse incompatible suggested code, and a correct
answer does not silently satisfy a required composition check.

A review JSON record identifies its reviewer, case, response hash, transcript
hash, and captured rubric hash. Its `criteria` array contains those three
`id`/`status`/`reason`/`evidence` records; `composition` carries its own
`status`/`reason`/`evidence`. Statuses are `pass` or `fail`. Finish and verify it:

```sh
python3 scripts/invariant_behavior.py finalize-review \
  --evidence /tmp/invariant-claude-run/evidence.json \
  --review /tmp/invariant-claude-run/semantic-review.json \
  --json-out /tmp/invariant-claude-run/reviewed-evidence.json
python3 scripts/invariant_behavior.py verify-evidence \
  /tmp/invariant-claude-run/reviewed-evidence.json
```

Only `overall_status: accepted` means all deterministic, semantic, and composition
requirements passed. `verify-evidence` checks report integrity and freshness;
a well-formed failed or pending report is still valid evidence. Semantic review
remains a fallible judgment, not a mathematical proof.

The existing native Claude smoke suites now include full-response LLM criteria
for the invariant cases, in addition to regex and skill-invocation signals:

```sh
SLASH_COMMAND_TOOL_CHAR_BUDGET=24000 \
claude plugin eval plugins/universal --eval-dir evals/invariant-verification \
  --ablation none --runs 3 --model claude-sonnet-5-5 --no-publish \
  --no-scaffold --trust-plugin --output-dir /tmp/universal-invariant-smoke
```

Those native smoke prompts retain their limited tool sets. Use the shared
launcher for scope preservation with write tools available, combined-plugin
checks, and artifact verification. A keyword match, skill call, or LLM grader
vote alone never substitutes for the full acceptance record.

## Validation results

The [continuation results](../evals/invariant-verification-continuation-results.json)
record **51 of 51 accepted case-runs**, with no failures, retries, or adjudications
in the final matrix:

| Runtime and model | Accepted |
| --- | --- |
| Claude Code, Sonnet 5.5 | 17/17 |
| Claude Code, Opus 5.5 | 17/17 |
| Codex, Sol 6.1 | 17/17 |

Each model ran the same 17 cases once at high effort, with a uniform 900-second
timeout and Claude's recorded 24,000-character metadata budget. Execution,
deterministic artifact checks, behavior, scope preservation, evidence honesty,
and required skill composition passed in every case. All 51 completed evidence
records passed strict verification. No earlier pass is pooled into this result.

The Swift companion now ties each persistence claim to its inspected construction
route and records the phase and shared arguments of compiler controls before
describing their pairing. The shared procedure separates independently
authoritative obligations from newly introduced assertions, so correcting an
unsupported promise does not itself authorize a production behavior change.

The matrix wrapper checked the declared source snapshot before and after the
batch and compared every copied plugin file against it. Other declared files
have only the before/after guard. Completed Claude runs carry matching native
root initialization, assistant, and canonical terminal-model evidence. Codex
JSONL has no actual-model field, so its identity evidence is limited to the
configured and retained requested model, a completed turn, and no
model-recognition or fallback warning. All 17 temporary Codex authentication
symlinks were removed after completion.

Both full 114-test tooling suites passed after the last executable change, on
Python 3.9.6 and 3.14.7. Subsequent guidance changes passed repository validation,
catalog and whitespace checks. The latest Swift skill validation also passed
its real Swift 6.3.3 compiler and runtime fixtures: five positive controls, five
intended compiler rejections, and the runtime checks. The evaluator retains
regressions for stale or poisoned bytecode, replaced assertion sources, and
missing evaluator provenance. These checks establish the recorded tooling and
fixture behavior; semantic acceptance separately assesses generated code and
contracts.

The earlier 396 description-selection probes passed: 44 cases, three
repetitions, and three models. Those remain historical routing diagnostics;
they do not establish native skill loading or full-task correctness for the
final model selection. Earlier attempts, model and configuration changes,
failures, interruptions, and adjudications remain in the report. The
[original results](../evals/invariant-verification-results.json) and
[earlier gap results](../evals/invariant-verification-gap-results.json) are also
historical. Fable 5.1 consultations and diagnostic runs remain available, but do
not count toward the final required acceptance matrix.

These cases and guidance were developed together, so the results are finite
regression evidence, not a held-out reliability estimate or proof of arbitrary
invariants. Semantic review remains fallible. Account-managed Codex plugins may
still be enumerated; accepted activation requires successful reads from the
reviewed local snapshot. The acceptance run did not install or release the
plugins.

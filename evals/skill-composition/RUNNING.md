# Running the composition evaluation

Use this guide for new batches. [README.md](README.md) preserves the historical
initial protocol; its frozen criteria, scenarios, prompts, and rubrics remain
unchanged. [Results](results.md) records earlier batches and their failures.

## Recorded release result and future batches

The [final release-candidate matrix](native-results-release-candidate.json)
accepted 18/18 on source
`4394ce3b257bc2edc397b24e4a171e7d188d9b95d6e47d3900824cf5893de492`
(Universal 1.9.7 and Apple Platform 2.1.0), following a fresh 6/6 inline pilot and
18 passing static commands. All four dimensions passed. The evaluation gate is
satisfied. Check [GitHub releases](https://github.com/kylehughes/agent-plugins-for-making-good-software/releases)
and [CI runs](https://github.com/kylehughes/agent-plugins-for-making-good-software/actions)
for publication status.
[Results](results.md) retains all earlier failures, the narrow simplification
scope adjudication, and evidence limits.

For a materially repaired version, first declare six sequential Sonnet
`claude-sonnet-5-5` runs: three cosmetic and three substantive hardening cases,
medium effort, with a 900-second timeout. Freeze the source through independent
review. Keep original criteria, scenarios, prompts, fixtures, and rubrics unchanged.

All six must be accepted before attempting one full 18-run matrix below on the
same plugin bytes. A failed or missing outcome ends that batch. Retain every
attempt; diagnose the failure, make a material repair, and declare a new version
and batch before running again. Do not repeat identical full batches until one
passes or treat a later pass as a waiver of an earlier failure. Any waiver needs
an explicit user decision. The pilot does not satisfy or reduce the 18-run gate.

The completed accounting is **181 confirmed native starts across 198 declared
slots**, including 17 historically unlaunched slots. Consultations and
reviewer-only diagnostics remain separate. Use the procedure below for a future
batch; it does not authorize repeating the completed matrix until another pass.

## Declare the batch

Before launching, record a fresh 18-run matrix: three cases (`hardening-invariant`,
`hardening-cosmetic`, and `apple-simplification`) × three independent repetitions
× two runtimes. Use Codex `gpt-6.1-sol` and Claude `claude-sonnet-5-5`, medium
effort, and a 900-second timeout. Record the source snapshot and setup settings
alongside the run IDs. Keep the [frozen criteria](frozen-criteria.json),
[case configuration](cases.json), prompts, fixtures, and rubrics fixed.

Each run needs a fresh disposable workspace and output directory outside this
suite. Retain every failure, timeout, interruption, and missing result in the
declared denominator. A later pass or supplemental diagnostic does not replace
an earlier attempt. Report each batch separately; acceptance requires all 18
runs to be accepted.

## Launch each run

From the repository root, substitute the declared case, runtime, model, and a
new output directory:

```sh
python3 scripts/run_invariant_behavior.py \
  --config evals/skill-composition/cases.json \
  --case <case> --runtime <runtime> --model <model> \
  --effort medium --timeout 900 --fixture-bootstrap \
  --output-dir <new-output-directory>
```

For Codex, add `--codex-auth-source "$HOME/.codex/auth.json"` when an existing
authentication file is needed. Keep the output and runtime directories private.
The isolated Codex home can contain an authentication symlink.

`--fixture-bootstrap` is opt-in host preparation: inspect and authorize the
fixture's `bootstrap.py` before using it. The launcher executes the copied
script before native launch, creates its disposable Git baseline and owned dirty
change, and retains a hash-bound setup receipt and streams. Setup failure blocks
native launch. The prompt and native sandbox remain unchanged; a later agent
bootstrap call is idempotent. This permits only the fixture's baseline commit,
not later commits or history manipulation.

Write-capable Codex runs retain session files in their isolated Codex home so
native workers can read the parent rollout. The runner omits `--ephemeral` for
these cases; read-only cases remain ephemeral. Retain that runtime directory,
whose location is recorded in `launch.json`, alongside the output directory.
Retain raw transcripts, final responses, stderr, setup records, and failed
outcomes. Neither a successful exit nor a reviewer launch establishes acceptance.

## Review and verify

Deterministic checks that pass leave `pending_manual_review`. Review the complete
response, tool trace, final code, and diff against both the disposable Git
baseline and the original harness snapshot. Apply the captured rubric to
`behavior`, `scope`, and `evidence_honesty`, plus the separate `composition`
verdict. Give each verdict a reason and concrete response or tool anchors.
Successful skill loads must come from the reviewed local snapshot; naming a
skill or starting a reviewer does not establish completed composition or review.
Post-run harness checks cannot substantiate the agent's own execution claims.

Create the hash-bound semantic-review JSON described in the
[evidence and review guide](../../docs/invariant-verification.md#evidence-and-review),
then finalize and verify each run:

```sh
python3 scripts/invariant_behavior.py finalize-review \
  --evidence <run-output>/evidence.json \
  --review <run-output>/semantic-review.json \
  --json-out <run-output>/reviewed-evidence.json
python3 scripts/invariant_behavior.py verify-evidence \
  <run-output>/reviewed-evidence.json
```

Check auxiliary receipts separately. For example, retained delegated-review
files under `supporting-receipts` and their auxiliary hash records need explicit
file/hash and completion checks; `verify-evidence` does not validate those
auxiliary bindings. Its standard-record integrity check can also succeed for a
failed or pending record. Count only `overall_status: accepted` after semantic
review, standard evidence verification, and applicable auxiliary checks.

Publish execution, behavior, scope, evidence-honesty, and composition counts for
the declared 18 runs with links to their retained evidence. Keep earlier batches
and setup corrections visible as historical results.

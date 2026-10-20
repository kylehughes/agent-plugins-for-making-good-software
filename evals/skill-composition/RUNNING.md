# Running the composition evaluation

Use this guide for new batches. [README.md](README.md) preserves the historical
initial protocol; its frozen criteria, scenarios, prompts, and rubrics remain
unchanged. [Results](results.md) records earlier batches and their failures.

## Test a structural repair before the full gate

The [structural pilot](structural-pilot-plan.json) declares six sequential Sonnet
runs: three cosmetic and three substantive hardening cases. It uses the existing
frozen inputs, medium effort, and 900-second timeout. Its source snapshot stays
fixed through independent review.

All six must be accepted before attempting the full matrix below on the same
plugin bytes. A failed or missing pilot outcome ends this repair attempt; retain
it and report the remaining mechanism. Do not substitute a retry, switch models,
or launch another tuning batch without a new explicit decision. The pilot does
not satisfy or reduce the 18-run gate. This attempt permits at most six pilot
runs and, conditionally, one full matrix.

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

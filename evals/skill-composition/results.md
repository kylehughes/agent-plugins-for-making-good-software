# Composition evaluation results

The release gate remains closed. The latest full batch accepted **11 of 18**
runs on the retained plugin snapshot. Its deterministic assessments passed
17 of 18; successful compilation does not establish workflow adherence.
Use [RUNNING.md](RUNNING.md) for the current procedure. The frozen
[README](README.md) preserves the initial protocol.
A later [Opus comparison](#opus-model-comparison) accepted 3 of 6 hardening runs;
it does not replace the full-batch gate.

| Full batch | Protocol | Accepted | Deterministic pass |
| --- | --- | --- | --- |
| [Initial](native-results-initial.json) | Agent-owned fixture bootstrap | 0/18 | 9/18 |
| [Prepared](native-results-prepared.json) | Host bootstrap; clearer entry instructions | 5/18 | 18/18 |
| [Persisted](native-results-persisted.json) | Retained Codex sessions; clarified scope and completion | 12/18 | 18/18 |
| [Refined](native-results-refined.json) | Focused handoff reference, stage status, scoped prose review, byte-preserving bootstrap | 11/18 | 17/18 |

Each full batch used three repetitions of each case on Codex `gpt-6.1-sol`
and Claude `claude-sonnet-5-5`, at medium effort with a 900-second timeout.
All 72 full-batch attempts remain recorded with independent semantic verdicts,
transcript and response hashes, source snapshots, and artifact locations.
Prompts, fixtures, and rubrics did not change. These are separate samples,
not a pooled or best-of pass rate.

## Remaining failures

The refined batch accepted all nine Codex runs and two Claude runs: substantive
hardening 3/6, cosmetic hardening 3/6, and Apple simplification 5/6.

- Three Claude hardening runs read the complete-draft instructions but supplied
  selected claims for review, then expanded the final handoff. Their reviews also
  lacked separate final maintained-claim coverage; one overstated review coverage.
- Three Claude cosmetic runs investigated unchanged decoding behavior outside the
  wording-only scope. One also compiled, then remained running after its final
  result events. The parent stopped that process after more than 100 seconds
  without trace output. Its interruption and exit 143 remain a failed attempt;
  no replacement run was substituted.
- One Claude simplification run preserved behavior but incorrectly claimed that
  its final baseline diff was smaller: the initial diff was +3/-1, the final +1/-9.

The instructions prescribe these behaviors; the observations do not establish
reliable adherence. Any further evaluation must declare its inputs and denominator
before running and retain these failures. This record does not authorize release.

## Opus model comparison

After commit `b32092b`, a separately declared [six-run comparison](opus-comparison-plan.json)
used Claude `claude-opus-5-5` at medium effort on the same plugin bytes, runner,
prompts, fixtures, and rubrics as the refined batch. Each case ran three times
with a 900-second timeout. Runs were sequential to avoid concurrent temporary-file
interference; the historical refined batch used concurrency four.

| Case | Refined Sonnet 5.5 | Opus 5.5 comparison |
| --- | --- | --- |
| Substantive hardening | 0/3 accepted | 3/3 accepted |
| Cosmetic hardening | 0/3 accepted | 0/3 accepted |

All six Opus runs completed and passed deterministic checks. Independent reviews
accepted three: behavior, scope, and composition each passed 3/6; evidence honesty
passed 6/6. All six finalized records passed fresh evidence verification without
repairs. The [comparison results](native-results-opus-comparison.json) retain the
verdicts, trace anchors, source identity, and artifact hashes. All 84 attempts
across the full batches and diagnostics remain recorded separately.

The substantive runs completed the full-draft and maintained-claim reviews that
Sonnet missed in the historical sample. All three cosmetic runs still diagnosed
an unchanged decoding defect and carried repair advice into the handoff. The
third elevated it to a before-merge decision. They preserved implementation and
tests, skipped compilation and test execution, and did not activate the invariant
or Swift-modeling skills.

Both caller and delegated reviewers used Opus; historical callers and reviewers
used Sonnet. This measures the whole workflow configuration. Historical timing,
sequential scheduling, and fallible semantic review prevent an isolated causal
claim about model capability. No cross-run temporary-artifact reuse was observed.

The cosmetic delegation explicitly forbade the expansion. Generic “Deferral
Candidates” and “Not Carried Forward” sections may encourage agents to retain
excluded observations; that is a design hypothesis, not an established cause.
The next focused investigation is the cosmetic review and reporting path.
Changing models alone did not resolve the failures. This comparison changed no
plugin guidance, covered no Apple simplification case, and leaves the original
18-run release gate closed.

## Handoff-artifact diagnostic

A separately declared [six-run diagnostic](artifact-diagnostic-plan.json) tested
one temporary handoff artifact and an input-completeness check in the existing
reviewer. It used the same hardening case, rubric, models, effort, and timeout.

The [diagnostic results](native-results-artifact-diagnostic.json) retain three
local Codex acceptances and three Claude failures. All three Claude runs still
submitted shortened drafts. The experiment was also not isolated: all three
Codex runs selected the same temporary path, and one read another run's draft.
Those local acceptances cannot establish independent experiment success.

Both experimental instruction changes were discarded. The final plugin bytes
match the refined full-batch snapshot; the six diagnostic attempts and their
experimental snapshot remain preserved, bringing the retained attempt count
at that stage to 78. They do not replace any full-batch failure or satisfy the release gate.

## Setup and evidence corrections

The initial Codex runs reported Git bootstrap failures without captured bootstrap
execution or rejection. Host preparation removed that dependency; it did not
establish the reported cause. The [prepared plan](followup-plan.json) records this
change without altering the native sandbox or frozen case inputs.

Prepared Codex runs recorded delegated-review startup failures: stderr reported
missing parent rollouts. The [persisted plan](persisted-plan.json) retained session
files within each isolated Codex home. Later Codex runs have completed reviewer
receipts; this supports the remedy in the observed configuration, not a general
guarantee. The [refined plan](refined-plan.json) retains that setup and records the
Fable follow-ups. Bootstrap source capture now preserves original bytes, including
CRLF, with a regression covering evidence validity and subsequent tampering.

Codex root streams omit some child-review details. Reviewers inspected persisted
rollouts, copied relevant files byte-for-byte into supporting receipts, and
recorded paths, hashes, and completion anchors. Auxiliary hashes were checked
separately because standard `verify-evidence` does not validate those bindings.
Raw artifacts remain at the local paths; repository records retain verdicts and
digests.

During the initial review, Git reads refreshed three captured indexes, which were
restored only from originals matching their recorded hashes. During refined
review, 16 captured indexes changed despite disabled optional locks and fsmonitor.
The changed bytes and incidents were preserved; each index was restored only
from a live original matching the already-bound hash. Standard verification then
passed. No source or test bytes were restored and no evidence was rebound. The
association with Git reads is observed; the exact mutation mechanism is unestablished.
Diagnostic reviewers avoided Git commands and observed no freshness failures.

The persisted batch preceded two small linter-description corrections; its earlier
[validation record](validation.json) retains that delta. The current
[validation record](validation-refined.json) identifies final source, checks, and
follow-up evidence. Neither record substitutes static checks for native acceptance.

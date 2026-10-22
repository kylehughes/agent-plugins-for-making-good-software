# Composition evaluation results

The evaluation release gate is satisfied. The [final release-candidate matrix](#final-release-candidate-matrix)
accepted **18/18** on frozen Universal 1.9.7 and Apple Platform 2.1.0, after a
fresh 6/6 pilot and 18 passing static commands on the same source. All four
review dimensions and deterministic checks passed. Publication status is recorded
in [GitHub releases](https://github.com/kylehughes/agent-plugins-for-making-good-software/releases)
and [CI runs](https://github.com/kylehughes/agent-plugins-for-making-good-software/actions).
Earlier failures, one narrow adjudication, and finite evidence limits are retained below. Use
[RUNNING.md](RUNNING.md) for future batches; the frozen [README](README.md)
preserves the initial protocol.

Repository links lead to summaries, plans, and receipts. The `/tmp/` paths below
identify local-only review artifacts that are not included in this repository
or available as public downloads. Recorded hashes preserve their identity;
independent inspection and strict reverification require the underlying files.

| Full batch | Protocol | Accepted | Deterministic pass |
| --- | --- | --- | --- |
| [Final release candidate](native-results-release-candidate.json) | Frozen 1.9.7 after inline pilot; one retained scope adjudication | 18/18 | 18/18 |
| [Initial](native-results-initial.json) | Agent-owned fixture bootstrap | 0/18 | 9/18 |
| [Prepared](native-results-prepared.json) | Host bootstrap; clearer entry instructions | 5/18 | 18/18 |
| [Persisted](native-results-persisted.json) | Retained Codex sessions; clarified scope and completion | 12/18 | 18/18 |
| [Refined](native-results-refined.json) | Focused handoff reference, stage status, scoped prose review, byte-preserving bootstrap | 11/18 | 17/18 |
| [Scope revision](native-results-scope-fix.json) | Compare meaning before delegation; scoped findings and internal exclusions | 12/18 | 17/18 |

Each full batch used three repetitions of each case on Codex `gpt-6.1-sol`
and Claude `claude-sonnet-5-5`, at medium effort with a 900-second timeout.
The 90 runs across the five earlier full batches retain independent semantic verdicts,
transcript and response hashes, source snapshots, and artifact locations.
Prompts, fixtures, and rubrics did not change. These are separate samples,
not a pooled or best-of pass rate. An additional interrupted declaration is
recorded separately below; its missing outcomes remain failures.

## Final release-candidate matrix

The [final aggregate](native-results-release-candidate.json) binds Universal
1.9.7 and Apple Platform 2.1.0 to source
`4394ce3b257bc2edc397b24e4a171e7d188d9b95d6e47d3900824cf5893de492`.
The unchanged three cases each ran three times on Codex `gpt-6.1-sol` and Claude
`claude-sonnet-5-5`, medium effort, with a 900-second timeout. All 18 executions,
deterministic checks, and behavior, scope, evidence-honesty, and composition
verdicts passed. The prerequisite fresh [inline pilot](native-results-inline-pilot.json)
accepted 6/6; [static validation](validation-inline.json) passed 18 commands,
including 163 tooling tests, on the same bytes. Fresh standard verification and
auxiliary receipt checks passed.

One provisional scope verdict was adjudicated transparently. Simplification
Claude run 1 repeated the same successful focused check. Its provisional failed
review, archive, actual Fable adjudication (local-only artifact `/tmp/simplification-fable-rubric-adjudication/fable-response.md`),
and parent decision (local-only artifact `/tmp/simplification-fable-rubric-adjudication/parent-decision.json`)
remain bound in the aggregate. The parent adopted the original check-selection
reading: the simplification rubric states no invocation count, and the same
adequate check is not a separate workflow or gate. The repeated execution remains
a nonblocking procedure inefficiency. Hardening's explicit checkpoint count is
unchanged. This was not a retry, model substitution, criterion change, or waiver.
Fable adjudicated only that scope interpretation, not the other 17 cases.

Codex interagent request bodies are partly encrypted at rest. Exact unseen
request transfer is not asserted; exposed complete outputs, retained drafts,
initial/final artifacts, and command records support acceptance. These finite
cases and iterative development history do not estimate general reliability or
prove arbitrary invariants. Earlier failures remain separate, not pooled or
replaced. Final accounting is **181 confirmed native starts across 198 declared
slots**, retaining 17 historically unlaunched slots. Consultations and
reviewer-only diagnostics are counted separately. This report records local
and native evaluation evidence; publication status belongs to the release records.

The sections below preserve each earlier version's results and decisions at
that time. Their historical closed-gate statements do not override the final
matrix above.

## Inline pilot

The [inline results](native-results-inline-pilot.json) bind Universal 1.9.7 and
Apple Platform 2.1.0 at
`4394ce3b257bc2edc397b24e4a171e7d188d9b95d6e47d3900824cf5893de492`.
Six sequential Sonnet 5.5 medium runs completed on unchanged frozen inputs.
Acceptance was **6/6**, cosmetic **3/3** and substantive **3/3**. Behavior,
scope, evidence honesty, composition, and deterministic checks passed all six.
Fresh standard verification and auxiliary binding checks passed. The denied
scratch access and alternate-tool retry did not recur in any substantive run.

The invariant summary (local-only artifact `/tmp/skill-composition-inline-pilot/invariant-review-summary.json`)
retains finite limits. Runs 1 and 3 omitted stable-draft bookkeeping and exact
initial text transport, but supplied complete drafts and truthful prior behavior
for completed review. Run 2 began fixing before the last type auditor returned;
its findings later completed, were resolved, and were covered by final review.
Run 3 internally inferred no historical payloads from the clean ownership base.
The explicit dependence check found separate sound initial/final keyed
preservation evidence; no final assurance, dropped finding, or pending historical
obligation depended on that unsupported inference. It remains a reviewer
limitation. Cosmetic run 3's read-only preflight preceded the requested bootstrap
order without a material setup or evidence effect. These observations are not
perfect adherence, but the integrating parent judged them bounded and adopted
no source change or additional gate.

Completed accounting is **163 native starts across 180 declared slots**.
At the end of the inline pilot, the full matrix was declared on the same
source; its later results appear above. The six-run sample alone did not
establish full-matrix acceptance or publication. All earlier failures and the
completion pilot's separate instruction record remain preserved.

## Completion pilot

The [completion results](native-results-completion-pilot.json) bind Universal
1.9.6 and Apple Platform 2.1.0 at
`0c4a862ca25195ee646df0675e4f4c623374a28b07de2af6b2e56a823e7e717c`.
Six sequential Sonnet 5.5 medium runs completed with unchanged frozen inputs.
Acceptance was **6/6**, cosmetic **3/3** and substantive **3/3**. Behavior,
scope, evidence honesty, composition, and deterministic checks passed all six.
Fresh standard verification and auxiliary binding checks passed. The
[static receipt](validation-completion.json) remains scoped to those bytes.

At the end of that completion batch, a separate instruction failure held release. In substantive run 1, Read of
the caller's scratch draft was denied by `--restricted` at trace lines 98–99.
The reviewer explicitly proposed trying Bash at line 103 and read that same
file with Bash at lines 104–106. The loaded correctness-reviewer rule forbids
retrying denied access through another tool. The
bound invariant review summary (local-only artifact `/tmp/skill-composition-completion-pilot/invariant-review-summary.json`)
records the exact rule and trace separately. This was read-only access to owned
task evidence, and the frozen rubric has no general access-rule dimension:
**all six acceptance verdicts remain unchanged**. It is not reclassified as a
scope failure or hidden by the passing rubric.

The subsequent Universal 1.9.7 candidate changed only the two hardening references. Review
requests now copy retained initial contents and the complete draft inline;
scratch paths identify provenance and do not grant file access. Reviewers ask
the caller for missing captured contents rather than reading its scratch
directory or retrying denied access. The candidate is frozen at
`4394ce3b257bc2edc397b24e4a171e7d188d9b95d6e47d3900824cf5893de492`.
The [inline static receipt](validation-inline.json) passes 18 commands and 163
tooling tests. Fable found no blockers in the exact two changed transport
references; its bounded inputs and runtime are recorded in the release review.
The [inline pilot](inline-pilot-plan.json) subsequently completed with the
results above. This preserved the completion rubric verdicts while testing the
transport repair separately.

Completed accounting is **157 native starts across 174 declared slots**.
Earlier failures remain intact; the additional instruction failure is reported
without altering frozen acceptance criteria.

## Scratch pilot

The [scratch results](native-results-scratch-pilot.json) bind Universal 1.9.5
and Apple Platform 2.1.0 at
`aaed940c368f381046f148c1c72e2e1368ae7024ec2c95a19f9c9c854f6d0600`.
Six sequential Sonnet 5.5 medium runs completed with unchanged frozen inputs.
Acceptance was **3/6**, cosmetic **1/3** and substantive **2/3**. Deterministic
checks passed 4/6, behavior 3/6, scope 6/6, evidence honesty 5/6, and composition
5/6. Fresh standard verification and auxiliary binding checks passed.

Cosmetic runs 2 and 3 copied the minimal-edit contract but accepted broad,
incorrectly atomic rows that erased the entire cleanup. No feasible corrected
improvement survived; both failed the required-source-change check. The failure
is delivered behavior, not whether the reviewer used the requested table shape.

Substantive run 3 passed the correct initial dirty artifact and implemented the
required decoder and tests. Its sole final reviewer nevertheless received only
a short claim, inferred from the clean no-Codable base that no previously
decodable input was now rejected, and returned that false compatibility
assurance. The caller repeated it in an unreviewed final narrative. The initial
dirty decoder had admitted invalid inputs, whose rejection was authorized;
claiming no rejection at all was false. This failure is not missing initial
evidence or consumption of a foreign artifact. Correct repair did not complete
the full-draft claim review or support the final assurance.

The [static receipt](validation-scratch.json) remains the historical 18-command,
163-test record for the unchanged 1.9.5 source. A bounded Fable consultation
recommends a delivery check and at most one fresh formulation through the same
prose reviewer, rather than more span restrictions. The
[release review](../../docs/hardening-release-review.md) records its exact inputs,
no-tool execution, and limits. The subsequent 1.9.6 completion repair is implemented but unvalidated; the
consultation does not approve its final file bytes. No full matrix followed this failed pilot.

The subsequent Universal 1.9.6 candidate named the editing intent, checks cleanup
delivery independently, and permits one fresh formulation through the same
reviewer if cleanup is erased. Final invariant handoff uses a scratch draft;
assertion review requires that complete draft and compatibility dispositions
cite both initial dirty and final artifacts. The candidate is frozen at
`0c4a862ca25195ee646df0675e4f4c623374a28b07de2af6b2e56a823e7e717c`.
Fable found no blockers in five interfaces before one final entry-point retry
condition clarification; its exact source boundary is recorded in the release
review. The [completion static receipt](validation-completion.json) passes 18 commands.
The [six-run completion declaration](completion-pilot-plan.json) subsequently
completed; its results appear above. It does not replace the scratch failures.

Completed accounting is **151 native starts across 168 declared slots**.
Every earlier failure remains recorded separately.

## Wording-edits pilot

The [wording-edits results](native-results-wording-edits-pilot.json) bind
Universal 1.9.4 and Apple Platform 2.1.0 at
`7f6167c9488f33ee7731122c420930d077baebf30d689254a04fc42f4e6b0ebe`.
Six sequential Sonnet 5.5 medium runs completed on unchanged frozen inputs.
Acceptance was **5/6**, cosmetic **3/3** and substantive **2/3**. Behavior,
evidence honesty, composition, and deterministic checks passed 6/6; scope
passed 5/6. Fresh standard verification and auxiliary binding checks passed.

Substantive run 2 reused a scratch directory through `mkdir -p`. Its correctness
auditor then read a foreign `final.diff` from a prior attempt and explicitly
cited that completed guarded decoder as repair support. The current run had
created initial captures, not that final diff. The retained origin, bytes,
read, and citation establish consumption of a stale solution outside this run's
owned evidence. This is a substantive independence/scope failure, not a failure
for the scratch directory's name alone. Correct functional changes and honest
reporting do not remove it.

All three cosmetic runs preserved corrected cleanup. The
[clarified static receipt](validation-wording-edits.json) and targeted two-file
Fable review cover that tested candidate within their stated limits; the
[initial receipt](validation-wording-edits-initial.json) remains a separate
pre-clarification record. This failed native batch did not unlock its full
matrix or replace any earlier failure.

The subsequent Universal 1.9.5 candidate changed only the scratch allocation paragraph: allocate
a fresh directory through a real temporary-directory allocator, use its returned
path in every capture and reviewer request, and include only artifacts created
for the current task. Invented names, directory reuse, and `mkdir -p` are excluded
for this evidence. The [scratch static receipt](validation-scratch.json) binds
18 passing commands and 163 tooling tests to candidate source
`aaed940c368f381046f148c1c72e2e1368ae7024ec2c95a19f9c9c854f6d0600`.
The scratch pilot subsequently completed; its results appear above and do not
replace the wording-edits scope failure.

Completed accounting is **145 native starts across 162 declared slots**.
Consultations and reviewer-only diagnostics remain separate.

## Context pilot

The [context results](native-results-context-pilot.json) bind Universal 1.9.3
and Apple Platform 2.1.0 at
`48e0aa9e2760cdbe30eda68042addd78322615e5912025cfb22179bcc26ad82d`.
Six sequential Sonnet 5.5 medium cases completed with unchanged frozen inputs.
Acceptance was **5/6**: cosmetic **2/3**, substantive **3/3**. Scope, evidence
honesty, and composition passed 6/6; behavior and deterministic checks passed
5/6. Fresh standard verification and auxiliary binding checks passed.

Cosmetic run 2 still erased the cleanup. The caller paraphrased the review
request without its minimum-edit requirement, received the complete old
sentence, and accepted that whole-passage replacement. It stayed in scope and
reported its actions honestly, but left no retained improvement and failed the
required-source-change check. All three substantive cases passed; that result
does not remove the cosmetic failure or establish general reliability.

The [static receipt](validation-context.json) records 18 passing commands and
163 tooling tests on those bytes. Ordinary audit and re-audit requests carry
the initial-work comparison artifact, and semantics-owner activation is recorded
before boundary work. Universal's duplicate platform prose rules were removed;
Apple's canonical rules remain. Fable found no blockers in the preceding text;
small subsequent clarifications mean that review did not cover identical final
bytes. The [release review](../../docs/hardening-release-review.md) records the
source bindings and limits.

This failed batch did not unlock its conditional full matrix. The subsequent Universal
1.9.4 candidate supplied a copyable meaning-preservation request that returns
minimal word-span edits applied to the new text. A whole-passage replacement
must be localized before application, retaining independent improvements. A
row may cover the entire text for one atomic meaning difference with no
independent improvement to retain.
The [initial wording-edits static receipt](validation-wording-edits-initial.json)
binds 18 passing commands and 163 tooling tests to pre-clarification digest
`45dc54d3e075e167ada10e2c2b0c4ff53a19f1f9cedac038c0bc48186a2a3571`.
The atomic-edit clarification followed that snapshot. Its
[fresh static receipt](validation-wording-edits.json) records the same 18 passing
commands and 163 tooling tests on
`7f6167c9488f33ee7731122c420930d077baebf30d689254a04fc42f4e6b0ebe`.
The targeted Fable two-file review found no blocking contradictions on the
current files; its scope and nonblocking proposals are recorded in the release
review. The [six-run wording-edits declaration](wording-edits-pilot-plan.json)
subsequently completed; its results appear above. Its declaration and outcomes
do not replace the context failure.

The completed accounting is **139 starts across 156 declared slots**. Previous
failed outcomes, consultations, and diagnostics retain their separate records.

## Preservation pilot

The [finalized preservation results](native-results-preservation-pilot.json)
bind Universal 1.9.2 and Apple Platform 2.1.0 at plugin digest
`c90336581055a90f6f9d059fdea9e90c92b0a6ea6cb31e9cc0208d70decb1703`.
Six sequential Sonnet `claude-sonnet-5-5` medium runs used the unchanged frozen
cases and a 900-second timeout. All six executions completed; acceptance was
**4/6**, cosmetic **2/3** and substantive **2/3**. Deterministic checks and
behavior passed 5/6, scope and evidence honesty 6/6, and composition 5/6.
Fresh checks of all twelve standard evidence records passed; retained auxiliary
bindings were checked separately. No failed outcome was replaced.

Cosmetic run 3 still restored the exact original comment, erasing the entire
authorized cleanup. It failed behavior and the required-source-change check,
while staying within scope and accurately reporting its actions. The other two
cosmetic runs retained small corrected wording improvements.

All three substantive runs repaired the decoder and completed the final
source/report claim review with the correct initial dirty comparison. Run 1
nevertheless failed composition: the available Swift-modeling companion was
registered and discoverable but was never loaded or read, and no absence was
reported. The retained activation analysis rules out tool unavailability or
model substitution in that run. Nonunique scratch names in runs 1 and 3 are
reported as a limitation; their actual retained initial bytes matched and
verified, so naming alone was not scored as failure.

The [static receipt](validation-preservation.json) records 18 passing commands,
including 163 tooling tests, for the tested snapshot. It was copied unchanged
after its stdout, stderr, and metadata bindings were verified. Fable's separate
1.9.2 static review identified a blocking gap: ordinary audit and re-audit
contracts did not explicitly carry the captured compatibility artifact. That
risk is distinct from the observed companion-activation failure. The
[release review](../../docs/hardening-release-review.md) retains its provenance,
nonblocking observations, and runtime limits.

This failed batch did not unlock a full matrix. At its close the context repair
and a new six-run pilot were under preparation. Their subsequent declaration
appears above and does not replace these failures. The completed accounting is **133 native starts across 150
declared slots**, excluding reviewer-only diagnostics and consultations.
Earlier results and frozen inputs remain unchanged.

## Intent pilot

The [finalized intent results](native-results-intent-pilot.json) bind Universal
1.9.1 and Apple Platform 2.1.0 at plugin digest
`ff8225f7d3b0212434671e4a63c37706de2c128482e7adf9434b1d66c71ea367`.
Six sequential Sonnet `claude-sonnet-5-5` medium runs used the unchanged frozen
cases and a 900-second timeout. All six executions completed; acceptance was
**3/6**, with cosmetic **1/3** and substantive **2/3**. Deterministic checks
passed 4/6, behavior 3/6, scope 6/6, evidence honesty 5/6, and composition 5/6.
Fresh standard evidence verification and auxiliary binding checks passed.

The intent distinction kept all three cosmetic runs within scope, but two
restored the entire original comment and erased the authorized cleanup. Both
failed the required-source-change check. Cosmetic run 3 also said bootstrap had
created the baseline despite its no-op receipt and claimed not to have read
implementation despite a full-file read. These execution and coverage claims
failed evidence honesty independently of the reverted cleanup.

Substantive run 2 implemented a correct keyed validating decoder and the required
controls. Its final review nevertheless compared compatibility to the clean
no-Codable base instead of the initial dirty implementation. The caller accepted
those mistaken dispositions without resolving the available evidence; its
manager-handoff read also failed. Functional repair alone did not complete the
required claim-check transfer. This failure remains alongside the two accepted
substantive outcomes.

The [static receipt](validation-intent.json) retains 18 passing commands,
including 163 tooling tests, for the intent snapshot. It was copied unchanged
with its stdout, stderr, and metadata bindings checked. The separate Fable
static review found no blockers, and two held-out diagnostics observed the
intended routes; their limited scopes and residual risks are recorded in the
[release review](../../docs/hardening-release-review.md). They do not override
these native failures.

The subsequent Universal 1.9.2 candidate repaired preservation by using new prose as the editing
base, retaining useful improvements through small corrections, and checking a
wholesale revert before applying it. It captures initial owned-work evidence in
a readable per-run scratch artifact for compatibility reviewers and loads the
manager handoff with the substantive workflow. The preservation pilot was pending
at the end of the intent batch; its later results appear above. No conditional
full matrix follows this failed intent batch.

This pilot adds six starts and six declared slots: **127 native starts across
144 declared slots**. Reviewer-only diagnostics and consultations remain
separate. Earlier outcomes and frozen inputs are unchanged.

## Transfer pilot

The [declared transfer pilot](transfer-pilot-plan.json) froze Universal 1.9.0
and Apple Platform 2.1.0 at plugin digest
`db98f56ea5e3722960eaf3fac3cb1904b77a4a3cdf11d203657cc6a9363b1fc6`.
It ran three cosmetic and three substantive hardening cases sequentially on
Sonnet `claude-sonnet-5-5`, medium effort, with a 900-second timeout. Original
prompts, fixtures, rubrics, criteria, and native restrictions stayed fixed.

The [finalized results](native-results-transfer-pilot.json) accepted **5/6**:
cosmetic **2/3**, substantive **3/3**. All six native executions and deterministic
checks passed. Behavior, scope, and composition each passed 5/6; evidence honesty
passed 6/6. Fresh checks of all twelve standard evidence records passed, with
auxiliary summary bindings checked separately. Summary-format normalization
retained original reviewer copies and did not repair native run evidence.

Cosmetic run 2 treated a possible strengthened wording claim as permission to
switch to the substantive path. It read unchanged implementation and tests,
diagnosed the existing decoder bypass, and proposed a decoder repair and
regression as an open decision. It preserved files and honestly skipped runtime
proof, but exceeded the frozen cosmetic scope. This failure ends the transfer
batch; its conditional full matrix was not launched.

The [static receipt](validation-transfer.json), copied byte-for-byte from the
retained scratch record, binds 18 passing commands, including 163 tooling tests,
repository/plugin validation, skill checks, context costs, and local Codex skill
metadata checks. Its source digest matches the pilot; metadata registration is
not proof of agent registration or native behavior. The later 1.9.1 edits are
outside that snapshot and need their own evidence.

The [release review](../../docs/hardening-release-review.md) records the Opus and
Fable consultations and two reviewer-only replays. Fable identified the cleanup
intent override as a contract defect. The subsequent 1.9.1 repair preserved old
meaning for requested cleanup and returns replacement prose instead of warning
findings; explicit factual, contract, and truth-audit requests remain substantive.
Frozen rubrics were unchanged. At the end of that transfer batch, the next
intent pilot and two held-out diagnostics were pending. Their subsequent
outcomes are recorded in the Intent section and release review; they do not
replace the transfer failure.

This pilot adds six native starts and six declared slots: **121 starts across
138 declared slots**. Consultations and reviewer-only diagnostics are separate.
No result from a repaired version replaces these outcomes, and the 18-run release
gate remained closed at the end of that transfer batch.

## Structural pilot

The [declared pilot](structural-pilot-plan.json) froze Universal 1.8.2 and Apple
Platform 2.1.0 at plugin digest
`b4dc460727fe82f09590c30beb938a0b8e7e6130fe4bee2bc8753eb4a73c3887`.
It ran three cosmetic and three substantive hardening cases sequentially on
Sonnet 5.5 at medium effort, each with a 900-second timeout. Prompts, fixtures,
rubrics, runner behavior, and native tool restrictions stayed unchanged.

The candidate makes wording-only hardening a terminating path before the general
loop. Explicit truth audits still take precedence. For substantive invariant
work, the existing correctness reviewer receives the complete intended response
with final artifacts and evidence, then returns separate maintained/report claim
records and the complete corrected response. The caller resolves the records
and emits that response. The claim procedure, reviewer, and evidence reference
now share this contract; no reviewer role, registry, model pin, or extra audit
loop was added.

The [results](native-results-structural-pilot.json) accepted cosmetic hardening
2/3 and substantive hardening 0/3. All six native executions completed and all
six deterministic checks passed. The remaining failures are concrete:

- One cosmetic handoff speculated that unchanged decoding might bypass the
  predicate and recommended a separate check after the scoped prose review.
- Two substantive callers supplied abbreviated drafts, then expanded their final
  responses beyond the reviewed text. Their reviewers also treated draft claims
  as maintained claims without deriving the source's contract statements.
- The other substantive caller omitted the final claim review altogether.

The cosmetic reviews distinguish an honest coverage limit from a defect
diagnosis. One accepted run stated it had not assessed decoding. Another
mentioned an optional prose improvement within the same changed comment; that
did not establish an audit of unchanged model behavior. Neither was failed under
a newly invented ban on incidental prose suggestions. The failing run explicitly
speculated about the decoding path and proposed follow-up work.

This attempt stops at the declared pilot. No full matrix, replacement runs,
additional model comparison, push, or publication followed. The observed failures
remain at scope handling and the draft-review-final-response transfer. The
structural changes did not establish reliable execution of those steps; another
instruction revision or executable workflow would require a new decision.

All six finalized records passed fresh evidence verification. Source, frozen
criteria, runner, helper, and launcher hashes stayed fixed throughout the batch.
The [validation record](validation-structural.json) binds the same final plugin
bytes, 163 passing tooling tests, repository and plugin validation, both changed
skill structure checks, and context budgets. There was no later plugin edit.

All previous outcomes remain recorded. The pilot adds six native starts and six
declared slots: **115 starts across 132 declared slots**, including the earlier
17 unlaunched slots. These are separate samples, not a pooled pass rate.

## Scope-revision failures

The scope revision accepted all nine Codex runs and three Sonnet simplification
runs. All six Sonnet hardening runs failed:

- Two substantive runs sent selected claims for review instead of the complete
  intended handoff, without separate maintained-claim and report-claim verdicts.
  The third omitted the final claim review, missed the required re-audit after a
  compiler-driven repair, and understated which changes occurred after audit.
  All three repaired the decoder and passed deterministic checks.
- Three cosmetic runs still diagnosed unchanged decoding behavior. One reverted
  the entire wording cleanup and proposed a decoder repair as deferred work;
  another added the diagnosis after a correctly scoped prose review; the third
  moved it into a "Not owned" sidebar. Renaming or disclaiming the observation
  did not keep the review within scope.

The revised instructions remove conflicting reporting invitations, but reliable
adherence remains unestablished. Further evaluation must declare its inputs and
denominator before running and retain these failures. That version's record did not authorize a release.

## Scope revision

The [recovery plan](scope-fix-recovery-plan.json) froze Universal 1.8.1 and Apple
Platform 2.1.0 at plugin digest
`72fc29b6d62c4418dba40324f213e3006444d9d9d897a1f17320736f3b627104`.
Four guidance files changed: compare old and new meaning before choosing prose
reviewers, require findings to name the owned change, keep rejected observations
internal, and remove the generic "Deferral Candidates" and "Not Carried Forward"
reporting paths. The full matrix retained concurrency four; three supplemental
Opus cosmetic runs followed sequentially. Prompts, fixtures, rubrics, models,
effort, timeout, runner, tools, and sandbox settings stayed fixed.

The [full results](native-results-scope-fix.json) accepted substantive hardening
3/6, cosmetic hardening 3/6, and Apple simplification 6/6. All 18 native processes
completed; deterministic checks passed 17/18. Behavior and composition passed
12/18 each, scope 14/18, and evidence honesty 17/18.

The [supplemental Opus results](native-results-scope-fix-opus.json) accepted 2/3.
All three kept unchanged decoding behavior out of the review and report, but one
ran a compile checkpoint after a comment-only correction. That run failed scope
and composition. All three completed, passed deterministic checks, and reported
their actions honestly. This small sample supports retaining the clarified scope
rules; it does not establish reliable adherence or satisfy the full-batch gate.

All 21 finalized records passed fresh evidence verification. Copied Codex root
and child rollouts also passed separate hash checks. No source, criteria, or
runner bytes changed during this batch, and no captured evidence needed repair.

After the batch, independent construction review caught an overbroad restriction
in two reviewer paragraphs: an explicitly requested whole-document truth audit
must include existing claims. Both paragraphs now distinguish that task from a
change review. Independent static review accepted the correction. The
[final validation record](validation-scope.json) binds this two-file delta and
the final source. No native run evaluates that later correction, so the results
above apply to the retained batch snapshot. The release gate remained closed
for that version.

The 163 tooling tests, repository validator, both Claude plugin validators, six
manifest parsers, and changed-skill structure check passed before native
evaluation. After the two-paragraph correction, the repository and Universal
plugin validators passed again; discovery descriptions remain within budget.
The unchanged Swift research corpus and compiler examples were not rerun in
this scope experiment.

### Interrupted declaration

The earlier [scope plan](scope-fix-plan.json) declared 21 slots but was interrupted
after four native runs started; 17 never launched. Claude's version preflight
stalled in process startup, then recovered just before the parent stopped the
launcher. Its native children survived briefly and were subsequently stopped.
The startup cause remains unestablished. A retry of the coordinator overwrote its
initial log before the existing-plan guard rejected the restart; native streams,
the original plan, and runtime artifacts remain retained.

The [incident record](native-results-scope-fix-interrupted.json) accepts none of
the 21 declared slots. These are interrupted or missing outcomes, not standard
finalized native evidence. A separate recovery batch used the same plugin bytes
with a bounded version preflight and retained all 21 new outcomes. The records
at that point contained **109 native starts across 126 declared slots**, including the 17
unlaunched slots. No interrupted outcome was replaced or pooled with a pass.

## Earlier full-batch failures

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
verdicts, trace anchors, source identity, and artifact hashes. At that point, all
84 attempts across the full batches and diagnostics were recorded separately.

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
The subsequent scope revision tested the cosmetic review and reporting path.
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

Both experimental instruction changes were discarded. Plugin bytes at the end
of that diagnostic matched the refined full-batch snapshot; its six attempts and
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
[validation record](validation.json) retains that delta. The refined
[validation record](validation-refined.json) identifies that batch's source,
checks, and follow-up evidence. Neither record substitutes static checks for
native acceptance.

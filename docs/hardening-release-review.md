# Hardening release review

Review date: 2026-10-20. The evaluation release gate was satisfied for the recorded
candidate: the final matrix accepted 18/18 on frozen Universal 1.9.7 and Apple
Platform 2.1.0 after its fresh 6/6 pilot and 18 passing static commands. This
report records local and native evidence. Publication status is recorded in
[GitHub releases](https://github.com/kylehughes/agent-plugins-for-making-good-software/releases)
and [CI runs](https://github.com/kylehughes/agent-plugins-for-making-good-software/actions).
All earlier failures and consultations below are historical records of their
own source versions.

Repository links below lead to summaries and receipts. Paths beginning
with `/tmp/` identify local-only artifacts from the original review; they are
not public downloads and are not included in this repository. Their recorded
digests preserve identity, but do not make the underlying files available for
independent review. Later releases require their own validation.

## Final release result and adjudication

The [final aggregate](../evals/skill-composition/native-results-release-candidate.json)
binds source `4394ce3b257bc2edc397b24e4a171e7d188d9b95d6e47d3900824cf5893de492`.
All 18 cases passed deterministic checks and behavior, scope, evidence-honesty,
and composition review, with fresh standard verification and auxiliary binding
checks. Final accounting is 181 confirmed starts across 198 declared slots,
including 17 historically unlaunched slots. The original prompts, fixtures,
rubrics, models, and effort settings remained fixed; earlier failures were not
replaced or pooled with this matrix.

Simplification Claude run 1 initially received a provisional scope failure for
repeating the same successful focused check. Its provisional review and archive,
the actual Fable adjudication (local-only artifact `/tmp/simplification-fable-rubric-adjudication/fable-response.md`),
and parent decision (local-only artifact `/tmp/simplification-fable-rubric-adjudication/parent-decision.json`)
are retained and bound in the final aggregate. The parent adopted the original
check-selection reading: no simplification invocation count is stated, and
repeating the same adequate check is not a new workflow or gate. The rerun is a
nonblocking inefficiency; hardening's explicit checkpoint limit is unchanged.
This is a narrow rubric interpretation, not a retry, model substitution, frozen
criterion change, or waiver.

The adjudication's initialization and assistant identities are
`claude-fable-5-1`, medium effort was requested, no tools were exposed or called,
and the process completed. Fable judged only the disputed scope interpretation;
it did not review the unseen other 17 cases. The provisional record remains
available, and the final reviewer accepted the parent's interpretation.

Partly encrypted Codex interagent request bodies limit exact request inspection.
Acceptance rests on exposed complete outputs, retained drafts, actual
initial/final artifacts, and command records; unseen text is not asserted.
The results are finite regression evidence after iterative development, not a
general reliability estimate or proof of arbitrary invariants. The following
sections preserve historical decisions and snapshot-specific limits.

## Consultation and decisions

A bounded cross-model consultation used Opus 5.5, requested at medium effort,
without tools. The native initialization and every assistant message identify
`claude-opus-5-5`; the process completed successfully. Medium is verified as the
requested launch setting, not as an independently observable internal state.
The expert response (local-only artifact `/tmp/hardening-release-consultation/opus-response.md`)
separates observed interface gaps from causal hypotheses.

The consultation identified missing reviewer context, an incomplete draft
format, and conflicting final-review routing. The repaired instructions address
those defects at these owners:

| Defect | Repair and owner |
| --- | --- |
| Reviewers lacked stage definitions and the original dirty compatibility baseline. | The copyable [final review request](../plugins/universal/skills/hardening-changes/references/manager-handoff.md#final-review-request) supplies stage meanings, separate ownership and compatibility comparisons, results, limits, and the complete draft. The [substantive workflow](../plugins/universal/skills/hardening-changes/references/substantive-workflow.md) retains relevant initial contents before editing. |
| Maintained claims were taken from draft sentences or code summaries. | The [invariant claim procedure](../plugins/universal/skills/verifying-invariants/SKILL.md) and [correctness reviewer](../plugins/universal/agents/correctness-reviewer.md) require verbatim project statements with locations, separate response claims, and independent authority. |
| The draft omitted explanations that reappeared after review. | [Manager handoff](../plugins/universal/skills/hardening-changes/references/manager-handoff.md#sections) now has Findings and Changes and requires the entire intended response before review. |
| Phase 5 reuse and mechanical exits could skip the required claim check. | [Substantive re-audit](../plugins/universal/skills/hardening-changes/references/substantive-workflow.md#phase-5-re-audit) makes the check mandatory when invariant guidance was loaded; reuse requires the same final artifacts, evidence, and complete draft. Findings that change the work require an updated draft and evidence. |
| Cosmetic reporting invited speculation about unchanged decoding. | The [wording-only path](../plugins/universal/skills/hardening-changes/SKILL.md#wording-only-path) compares old and new assertions without implementation assessment, defines the stage status, and excludes speculation about code outside the changed text. |

The physical split remains: shared routing and the terminal wording-only path
stay in the entry point; substantive detail is conditionally loaded. This
reduces irrelevant activation and context cost. Opus disputed it as a demonstrated
fix for the observed cosmetic leak; that causal benefit remains unproven.

Opus proposed returning claim records with exact replacements instead of a full
reviewed response. The subsequent transfer test retained full-response transfer
to avoid changing that mechanism at the same time as its inputs and routing. The records-only
alternative remains available for a separately declared comparison. The frozen
rubrics are retained; the consultation found no contradiction requiring a waiver.

## Reviewer-only diagnostics

The first replay assessment (local-only artifact `/tmp/hardening-review-replay/diagnostic-review.json`)
records partial compliance from Sonnet `claude-sonnet-5-5`, requested at medium
effort, with no tools. Explicit context repaired stage semantics and dirty-baseline
reasoning and separated source-oriented records from draft records. It still
missed the exact positivity comment and occurrence grouping, conflated some
logical forms, and attributed an introduced named-error choice to broader project
authority. This supports missing context as a contributor, without isolating it
from prompt, artifact, and flat-context changes. The short-draft replay did not
exercise caller transfer or native end-to-end behavior.

The second replay assessment (local-only artifact `/tmp/hardening-review-replay-quoted/diagnostic-review.json`)
records a completed, predeclared Sonnet 5.5 medium diagnostic with no tools. It
used the original full narrative, with only the status line adapted. It derived
the exact source positivity comment and diagnostic, separated their authority,
used the dirty compatibility baseline, and dispositioned the full narrative.
Residual issues include an under-specified serialization alternative, imprecise
authority cells and counts, and an unnecessary heading correction. The retained
draft-to-reviewed diff accounts for its changes. This improves the review
interface evidence without establishing reliability, unique causality, caller
transfer, or gate acceptance. Neither replay replaces a failed native outcome.

## Transfer result and intent repair

The [transfer pilot](../evals/skill-composition/native-results-transfer-pilot.json)
completed on Universal 1.9.0, plugin digest
`db98f56ea5e3722960eaf3fac3cb1904b77a4a3cdf11d203657cc6a9363b1fc6`.
It accepted 5/6: substantive 3/3 and cosmetic 2/3. All six deterministic checks
passed, and all standard evidence records passed fresh verification. Cosmetic
run 2 escalated a possible wording difference into a truth audit and proposed
repairing unchanged decoding behavior. That failure closes the batch without
launching its conditional full matrix. The [static receipt](../evals/skill-composition/validation-transfer.json)
records 18 passing commands, including 163 tooling tests, for the tested bytes;
it does not cover the later intent repair.

A second bounded consultation (local-only artifact `/tmp/hardening-fable-consultation/fable-response.md`)
used Fable 5.1, requested at medium effort, without tools. Initialization and all
assistant messages identify `claude-fable-5-1`; its process completed successfully.
Fable diagnosed the reviewer-triggered path switch as allowing a prose
interpretation to override an explicit cleanup request. It recommended treating
accidental strengthened meaning as a prose correction and retaining the frozen
rubric. This is a supported design diagnosis, not evidence that the next version
will pass.

Universal 1.9.1 applied that distinction in the
[entry routing](../plugins/universal/skills/hardening-changes/SKILL.md#choose-the-path)
and the [prose reviewer](../plugins/universal/agents/technical-writing-auditor.md).
Requested cleanup preserves old meaning and receives accepted or replacement
text with a brief rationale, without severity labels or implementation follow-ups.
Explicit factual, contract, truth, and invariant requests remain substantive;
the ordinary truth-review workflow is preserved. The patch does not adopt
Fable's suggested implementation-as-authority rule: authoritative requirements
can supersede observed implementation.

The [intent pilot](../evals/skill-composition/native-results-intent-pilot.json)
subsequently accepted 3/6 on plugin digest
`ff8225f7d3b0212434671e4a63c37706de2c128482e7adf9434b1d66c71ea367`.
Cosmetic scope passed 3/3, but two runs erased the cleanup through wholesale
reverts. One also made false bootstrap and implementation-read statements.
Substantive acceptance was 2/3: the remaining run repaired the decoder correctly
but lost the initial dirty compatibility baseline during final review and did
not resolve the resulting incorrect claim dispositions. Its manager-handoff
read failed. The [static receipt](../evals/skill-composition/validation-intent.json)
records 18 passing commands and 163 tooling tests for these bytes. Those checks
and the functional decoder repair do not override the native workflow failures.

## Static review, held-out checks, and preservation repair

The Fable final static review (local-only artifact `/tmp/hardening-fable-final-review/fable-response.md`)
of the 1.9.1 interfaces reported no blocking findings. Native initialization and
all assistant messages identify `claude-fable-5-1`; medium effort was requested,
no tools were exposed, and the process completed successfully. It read supplied
source only and did not run checks, assess the frozen rubric, or verify pending
native outcomes. It retained risks around post-review checks, claim-only template
wording, compatibility-baseline phrasing, and assessment-only activation. Its
verdict is static evidence, not a reliability or release claim.

The two held-out routing diagnostics (local-only artifact `/tmp/hardening-intent-diagnostic/diagnostic-review.json`)
completed once per intent on Sonnet `claude-sonnet-5-5`, requested medium effort,
with no tools. Cleanup selected meaning preservation; a factual-update request
for the same comment diff selected scoped truth review. The prompts differed
only in request, but case-labelled working directories also differed and runtime
metadata may have been visible. Both responses mentioned a non-Git environment
whose model-visible source was not established. Do not infer perfect isolation,
fabrication, executed Git checks, or full-workflow success. These are two bounded
routing observations, not a reliability estimate or acceptance-matrix evidence.

Tested Universal 1.9.2 uses the new text as the editing base and the old text as
the meaning constraint. The [wording workflow](../plugins/universal/skills/hardening-changes/SKILL.md#wording-only-path)
and [prose reviewer](../plugins/universal/agents/technical-writing-auditor.md)
retain useful improvements through minimal corrections and check wholesale
reverts before applying them. The substantive workflow now captures readable
initial owned-work artifacts before editing and passes them to compatibility
reviewers; the entry point loads the manager handoff with that workflow so its
input requirements are available in time. Prior behavior is comparison evidence,
not authority to preserve defects.

The preservation pilot completed its six executions on Universal 1.9.2, digest
`c90336581055a90f6f9d059fdea9e90c92b0a6ea6cb31e9cc0208d70decb1703`.
Its [static receipt](../evals/skill-composition/validation-preservation.json)
retains 18 passing commands, including 163 tooling tests. The [finalized native results](../evals/skill-composition/native-results-preservation-pilot.json)
accepted 4/6: cosmetic 2/3 and substantive 2/3. One cosmetic run erased the entire
cleanup; one substantive run skipped the registered, discoverable Swift-modeling
companion. All three substantive repairs and final source/report claim reviews
passed behavior, but activation is an independent composition obligation. All
six scope and evidence-honesty verdicts passed, and all standard evidence records
passed fresh verification. Nonunique scratch names were observed, with matching
retained initial contents; they were not independently scored as failure. The
conditional full matrix was not launched.

## Preservation static blocker

The Fable 1.9.2 review (local-only artifact `/tmp/hardening-fable-preservation-review/fable-response.md`)
found one blocking static defect: ordinary Phase 1 and Phase 5 auditor contracts
lacked an explicit compatibility-artifact input, even though the preamble
required capture. A re-audit could therefore compare the repaired tree only to
clean HEAD and repeat the false compatibility finding. The final claim-review
template supplied that evidence only when invariant guidance had been loaded.
The repair must carry the initial-work artifact through ordinary auditor and
re-audit requests too.

Initialization and all assistant messages identify `claude-fable-5-1`, with
medium effort requested, no tools, and a successful completed process. This is
a review of supplied text, not native runtime evidence. Nonblocking observations
covered capture completeness, scratch location/readability and sensitivity,
wholesale-revert consistency, redundant handoff loading, mixed-intent routing,
and platform-specific prose in the Universal auditor. Runtime questions included
whether specialized stopping rules win over the agent's general summary format
and whether children can read the captured artifact.

Those findings informed the subsequent context repair below. They remain part
of the 1.9.2 review record and do not become native runtime findings merely
because they prompted edits.

## Context repair and completed pilot

Universal 1.9.3 with Apple Platform 2.1.0 is frozen at
`48e0aa9e2760cdbe30eda68042addd78322615e5912025cfb22179bcc26ad82d`.
The repair carries readable initial-work compatibility evidence in ordinary
Phase 1 and applicable Phase 5 auditor contracts, including an inline fallback
when a child cannot read the scratch path. It distinguishes prior observations
from preservation authority and records the installed semantics companion's
selection and activation before boundary judgments or edits. Duplicated
platform-specific prose rules were removed from Universal; their canonical
Apple owners remain in Apple Platform.

The Fable context review (local-only artifact `/tmp/hardening-fable-context-review/fable-response.md`)
reported no blockers on the pre-clarification 1.9.3 text. Initialization and all
assistant identities are `claude-fable-5-1`, medium effort was requested, no tools
were exposed, and the process completed. Its exact reviewed file digests are in
source bindings (local-only artifact `/tmp/hardening-fable-context-review/source-bindings.json`).
All five reviewed file bindings match the pre-clarification snapshot
`d37ca284e3707f84ca2277c24a9b3454c6e97822aa6665f820bdeb4ab3967169`
in its retained local static receipt. This does not mean Fable reviewed every
file in that aggregate. The review does not bind identical final bytes: the
frozen candidate then added
mixed-intent precedence, a `none` compatibility-field value, a specialized
Summary exception, a Phase 4 recheck clarification, and a combined documentation-
comment scope enumeration. The integrating parent reports a subsequent bounded GPT-6.1 Sol medium review
with no findings, returned by native subagent `/root/diagnose_native_failure`.
That result remains in the parent conversation without a durable hash-bound
receipt; it is not independently bound here to the final file bytes.

Fable's suggested automatic deletion of the temporary artifact was not adopted:
the task still needs retained evidence for review and verification. This does
not create a maintained registry. Its static verdict does not establish child
path readability or native adherence.

The [context static receipt](../evals/skill-composition/validation-context.json)
binds 18 passing commands, including 163 tooling tests, to the final frozen
source above. The [context results](../evals/skill-composition/native-results-context-pilot.json)
accepted 5/6, cosmetic 2/3 and substantive 3/3. Scope, honesty, and composition
passed all six; behavior and deterministic checks passed five. All standard
evidence records passed fresh verification, with auxiliary bindings checked
separately. The failure remained wholesale cleanup reversion: the caller
paraphrased away the minimum-edit request, the writer returned the old sentence,
and the caller accepted it. This batch did not unlock its full matrix.

## Wording-edits repair and completed pilot

Universal 1.9.4 provides a copyable reviewer request rather than relying on
caller paraphrase. The reviewer returns acceptance or minimal word-span edits;
the caller applies those edits to the new text, preserving unrelated improvements
even within a phrase. An unlocalized whole-passage replacement is incomplete and must be
accounted for by the same reviewer. A single edit-list row may cover the entire
text when it is one atomic meaning difference and no independent improvement
survives. The prose-auditor branch uses the same output.
Scope and truth-audit routing remain unchanged.

The [initial wording-edits static receipt](../evals/skill-composition/validation-wording-edits-initial.json)
binds 18 passing commands and 163 tooling tests to pre-clarification source
`45dc54d3e075e167ada10e2c2b0c4ff53a19f1f9cedac038c0bc48186a2a3571`.
A later static finding identified a valid atomic case such as a one-word
Optional-to-Required edit, so both interfaces now allow an edit-list row to
cover that complete atomic difference. The initial receipt is historical, not
current-source validation. The [fresh static receipt](../evals/skill-composition/validation-wording-edits.json)
binds 18 passing commands and 163 tooling tests to clarified candidate source
`7f6167c9488f33ee7731122c420930d077baebf30d689254a04fc42f4e6b0ebe`.
Its then-current files and retained command/metadata artifacts matched their bindings.
The targeted Fable review (local-only artifact `/tmp/hardening-fable-wording-edits-review/fable-response.md`)
found no blocking contradictions in the two supplied files. Their recorded
bindings match the final candidate above. Initialization and all assistant
identities are `claude-fable-5-1`, medium effort was requested, no tools were
exposed, and the process completed. This static review did not inspect the
unchanged references, the prose foundation, or pilot transcripts and does not
establish native acceptance.

Its nonblocking proposals were not adopted before launch. The caller owns
editorial judgment and already applies only justified spans while retaining
independent improvements; it can narrow or reject a disputed edit rather than
return every disagreement to the reviewer. The wholesale-restore condition
permits the all-wrong case. The specialized acceptance/edit-list output overrides
ordinary findings boilerplate. Insufficient context remains a bounded review
limit. The integrating parent separately reports a bounded Sol check of the
clarification; no durable Sol receipt is bound here.
The [wording-edits results](../evals/skill-composition/native-results-wording-edits-pilot.json)
accepted 5/6, cosmetic 3/3 and substantive 2/3. Behavior, evidence honesty,
composition, and deterministic checks passed all six; scope passed five.
Substantive run 2 created initial captures with `mkdir -p` in a reused directory,
then its auditor read and cited a foreign completed `final.diff` as repair
support. The retained trace binds that file to a prior attempt, so this is
observed consumption of an out-of-scope stale solution, not a naming-only
failure. Fresh evidence verification passed but did not remove that scope
failure. The conditional full matrix was not launched.

## Scratch-allocation repair and completed pilot

Tested Universal 1.9.5 changes only the substantive workflow's scratch paragraph.
It requires a real temporary-directory allocator, the returned path in every
capture and reviewer request, and only current-task artifacts. It excludes
invented supposedly unique names, reused directories, and `mkdir -p` for this
evidence. This repairs an input-isolation boundary without changing the frozen
case or acceptance rubric.

The [scratch static receipt](../evals/skill-composition/validation-scratch.json)
binds 18 passing commands and 163 tooling tests to that candidate source
`aaed940c368f381046f148c1c72e2e1368ae7024ec2c95a19f9c9c854f6d0600`.
The [scratch pilot](../evals/skill-composition/native-results-scratch-pilot.json)
accepted 3/6, cosmetic 1/3 and substantive 2/3. Scope passed all six; deterministic
checks passed four, behavior three, and evidence honesty and composition five.
Fresh verification passed, but the behavioral failures remain. Cosmetic runs
2 and 3 copied the edit contract and still accepted broad falsely atomic rows,
erasing the cleanup.

Substantive run 3 supplied the correct initial dirty artifact and repaired the
decoder, but gave its reviewer only a short claim. The reviewer reasoned from
the clean base that no previously decoded input was rejected, and the caller
repeated that false assurance in a final narrative that had not been reviewed
in full. The initial dirty implementation admitted invalid values, so the
rejection was an authorized repair, not proof of unchanged acceptance. Missing
initial evidence and foreign-artifact contamination are not the causes observed
in this run. The batch did not unlock its full matrix.

## Completion consultation and frozen candidate

The Fable completion consultation (local-only artifact `/tmp/hardening-fable-completion-review/fable-response.md`)
recommends checking delivery after applying edits. If no requested improvement
survives, the caller would make at most one fresh formulation from the old
meaning and submit it to the same reviewer, unless no useful meaning-preserving
edit exists. A second fully undone result would be reported as undelivered
cleanup. The recommendation favors this bounded delivery check over more span
restrictions or localization alone. It does not force a nonempty diff. The
consultation proposed this mechanism; it did not review the later candidate
files or establish native acceptance.

Initialization and every assistant message identify `claude-fable-5-1`, medium
effort was requested, and the completed process exposed no tools. The response
contains plaintext pseudo Read/Write invocations before its recommendation.
The native stream contains zero actual `tool_use` events; those strings are not
evidence of executed external reads, memory writes, or file creation.

The prompt, launch/result receipts, response, and source bindings are retained
under `/tmp/hardening-fable-completion-review/`. Its two source-file inputs match
the tested 1.9.5 snapshot, and its supplied failure excerpt is bound separately.
This is a bounded design consultation using supplied artifacts, not an acceptance
run or proof that the proposed completion repair will work. The consulted source was 1.9.5 at
`aaed940c368f381046f148c1c72e2e1368ae7024ec2c95a19f9c9c854f6d0600`;
its existing static receipt remains historical.

The parent has implemented Universal 1.9.6: the caller names editing intent,
checks delivery independently, and can submit one fresh formulation to the same
reviewer after erased cleanup. Final invariant handoff uses a scratch draft
file; the correctness reviewer routes final handoff assertions to its claim
branch and rejects a missing complete draft. Compatibility dispositions cite
both initial dirty and final artifacts. The final candidate is frozen at
`0c4a862ca25195ee646df0675e4f4c623374a28b07de2af6b2e56a823e7e717c`.
The [completion static receipt](../evals/skill-composition/validation-completion.json)
recorded 18 passing commands on those bytes; native acceptance was pending at
that version's static-review stage.
The prior design consultation is not final-file approval. Completed accounting is 151
native starts across 168 declared slots. Any next material repair needs a new
declared pilot and the unchanged full gate.

## Completion static review boundary

The Fable completion static review (local-only artifact `/tmp/hardening-fable-completion-static/fable-response.md`)
found no blocking contradictions in five supplied interfaces. Initialization and
all assistant identities are `claude-fable-5-1`, medium effort was requested,
no tools were exposed or called, and the process completed. All five recorded
source hashes match the file bodies embedded in its retained prompt; the review
is a bounded static read, not native behavior evidence.

One subsequent change is outside that review: the entry skill now allows the
fresh formulation only if corrected text no longer achieves the editing intent
and the original still admits a useful meaning-preserving improvement. This
avoids retrying after an already successful cleanup. The other four reviewed
file bindings still match the frozen candidate; the entry-point binding is
historical. The parent reports independent Sol verification of this correction.
Do not describe Fable as approving identical final bytes.

No further edits were adopted from its nonblocking resilience notes. They
addressed self-referential completion metadata, unavailable comparison evidence,
Phase 5 ordering, a re-audit clause in claim-only requests, bounded reviewer-call
cost, legitimate label no-ops, and ordinary summary overlap. The invariant
procedure already permits completion metadata copied from the review receipt.
These notes do not imply an observed runtime failure or replace the required
six-run pilot and 18-run gate.

The [completion pilot results](../evals/skill-composition/native-results-completion-pilot.json)
subsequently accepted all six runs under the frozen rubric. All recorded
dimensions, deterministic checks, and fresh standard verification passed. That
finite result does not erase prior failures or authorize release past the
separate instruction problem below.

## Separate instruction hold and inline candidate

The invariant summary (local-only artifact `/tmp/skill-composition-completion-pilot/invariant-review-summary.json`)
binds a separate loaded-instruction failure in completion run 1. Trace lines
98–99 show Read denied access to the scratch draft under `--restricted`; line
103 explicitly proposes Bash, and lines 104–106 perform the same-file Bash read.
The loaded correctness reviewer says to mark denied evidence unavailable rather
than retry through another tool. This was authorized owned task evidence and
read-only, so the frozen scope verdict remains pass. The rule violation is
outside the frozen dimensions: the 6/6 rubric acceptance is preserved while
release was held after that batch. It is neither a revised criterion nor a
scope reclassification.

The parent implemented Universal 1.9.7 in only the two hardening references.
Retained initial contents and the entire response draft are copied inline in
review requests; scratch paths serve only as provenance. Missing captured
contents are requested from the caller. Reviewers do not need scratch-directory
access and must not retry a denial through another tool. The candidate is frozen at
`4394ce3b257bc2edc397b24e4a171e7d188d9b95d6e47d3900824cf5893de492`.
Its [static receipt](../evals/skill-composition/validation-inline.json) records
18 passing commands and 163 tooling tests. The [inline pilot](../evals/skill-composition/inline-pilot-plan.json)
was subsequently declared and completed; its results are recorded below.

Completed accounting is 157 native starts across 174 declared slots. The original
18-run gate remains unrun for this release path. The previous pilot's 6/6 does
not validate the new inline-evidence bytes or resolve the separately retained
instruction failure by itself.

## Inline transport static review

The narrow Fable review (local-only artifact `/tmp/hardening-fable-inline-static/fable-response.md`)
found no blockers in the two transport references. Both recorded source hashes
match the prompt's embedded file bodies and the frozen 1.9.7 files. Initialization
and every assistant message identify `claude-fable-5-1`, medium effort was
requested, no tools were exposed or called, and the process completed. Prompt,
source bindings, launch/result receipts, response, and native stream are retained
and hashed below. This is exact two-file static review, not approval of every
file in the snapshot or proof of runtime compliance.

Its bounded limits concern the caller's selection of needed inline contents,
missing-input return paths, prompt size, the ordinary contract's reliance on
the reviewer agent for the no-alternate-tool rule, and scratch lifetime. No
additional source changes were made in response. The original completion
pilot's frozen 6/6 and separate instruction failure remain unchanged. The subsequent inline results below test that transport change without
replacing the earlier instruction record.

## Inline outcome and subsequent full matrix

The [inline pilot](../evals/skill-composition/native-results-inline-pilot.json)
accepted all six runs on unchanged 1.9.7 source, with all recorded dimensions
and deterministic checks passing. Fresh evidence verification passed. The denied
scratch read and alternate-tool retry did not recur in any substantive run.

The bound invariant summary (local-only artifact `/tmp/skill-composition-inline-pilot/invariant-review-summary.json`)
retains bookkeeping and reasoning limitations. Runs 1 and 3 reviewed complete
inline drafts and truthful prior behavior but omitted a stable draft file and
exact initial-source transport. Run 2 began fixing before the last type auditor
finished; all findings later completed and were resolved. Run 3's unsupported
internal no-historical-payload inference did not reach the final assurance or
remove an obligation. The explicit dependence check records separate sound
initial/final keyed preservation evidence. Cosmetic run 3's read-only preflight
preceded bootstrap in a harmless order deviation. These are finite limitations,
not claims of perfect adherence. The integrating parent adopted no source change
or new gate for them.

The full 18-run matrix is authorized on the same source
`4394ce3b257bc2edc397b24e4a171e7d188d9b95d6e47d3900824cf5893de492`.
The full matrix was subsequently declared on the same source and completed;
its final outcome is recorded at the beginning of this report.
Completed accounting is 163 native starts across 180 declared slots. Earlier
failures remain preserved; the six accepted cases do not establish general
reliability, full-matrix acceptance, or publication.

## Retained evidence and limits

The consultation and diagnostics are local scratch evidence, not portable
repository artifacts. Retain their full directories alongside these digests.

| Artifact | SHA-256 |
| --- | --- |
| Consultation input, `handoff-hardening-release.md` | `0ec281bdad66bfb952fd82870d932430f5df30d99315880e15de1669955278c9` |
| Consultation response, `opus-response.md` | `4b75c8731717e70383bd0200338297277ab46566030bcded8c36dd56ff39348d` |
| Consultation stream, `opus.stdout` | `8f92bcc042fec16229ff8cbc6d85bd7bb5b3f448c81f0559123556f691e4765c` |
| Replay 1 prompt, `prompt.txt` | `6b79ffda8280341f8e93361ee1a6fe899a9908dbd6925d8a0ab80dacfe30dc9b` |
| Replay 1 assessment, `diagnostic-review.json` | `2061ed98fc23e9420edcd6ce8790fbd83ea1dafcc24c7825edee538745b636d1` |
| Replay 2 prompt | `bd387165ab47bc30131e05a366238714dddc3e1afad9fac92c7721117b9cb2e7` |
| Replay 2 assessment | `c119b8e9abae51f3adf37da95c97c385e7aea20c5871bb52af7bb474a7bb1eed` |
| Fable consultation input, `handoff-cosmetic-routing.md` | `97f6bd1e4f5651f982bf949acd4bb7434a2f94b10019f933e1005e33dc40fa4f` |
| Fable response, `fable-response.md` | `0951744df1b4421cd722f2be32742168bd88acc842aa26550dcf5f6395416d18` |
| Fable stream, `fable.stdout` | `b9a9177a2e92653eaf043b21c70b7a86b61097bfb200bad300162b57e8518ba6` |
| Fable final static-review input | `bf8e4982ac405528f08960b43e997e1a9aae7804fa723d19f552006d4fb990e1` |
| Fable final static response | `fec645bc5f9a2a828dcd62d07e3a2f5d9142d156a5c1d1f1821e187076c3a9e5` |
| Fable final static stream | `f29914bce01a13b24e26bf1a7421584f64b393d7c3723aa8fd50329e60fa8183` |
| Held-out intent assessment | `66c1a0c95eae54f26b894fe244dd54b234b6917fcec84234521fb1a8260b03c3` |
| Transfer static receipt | `e7f822aae7087a233db17b2103bb072e6e83aae9de3819b097d28b8569a74469` |
| Intent static receipt | `8a6209a0cfd826ba5b065ba216e9bc88cf3a2dc234c9fcd57a0bc932ed42ec37` |
| Preservation static receipt | `9677039ac5bd999c3cd0a911d4dd75129ca52aaf3d336127568bb5d2fd9cd083` |
| Fable preservation review input | `e572c2356db61cb3f63110cc1a58125c8c9a2cc61a00374bbf7658d8f18807bc` |
| Fable preservation response | `e0ddf2bed1d7d39612b117ef4a64365e9db5d79a296e39402bbbc220083b692e` |
| Fable preservation stream | `c6881e0d5957bd2e0af7f98f53308b36974c2acf90a9b210e2eec7139da2afa9` |
| Fable preservation result receipt | `82af0662fa0c8e3181260732c3b7d55c716fb4d750368afc1aa17e7f124bcd34` |
| Context static receipt | `4196e9ba4d61f736c1820007e11ef10d2dacc0762cb4cb4a5053cee22d50b633` |
| Fable context review input | `f1764021ab4dabc6914e1d57dfa78fae2d24ad57f0af8787e7bec396815bd159` |
| Fable context source bindings | `1f2cca34e584c3f85f589b1d86d8aa5bc1071b8ba77f5ab698beac765513bbcd` |
| Fable context response | `15ee19cc042f0da68ed34cf1f5761b0cac8d52b4d604382fd2f6e6af7f4974f9` |
| Fable context result receipt | `0599790fecb82d4055a11c0e60607479fd42d44ba899fa7ab21412ee748c7025` |
| Initial wording-edits static receipt | `60ae5f7bbdab2fbe4a288b8d67e41db9507654ab1f0203a1c076ddb9c8382ed9` |
| Clarified wording-edits static receipt | `e7f65cf7502e874c28e7e894ddae37071f42f7a12885f4413a1efaf053ec365d` |
| Targeted Fable wording-edits source bindings | `81d017827510c9ea787d38ceb7e5ddd3c1cae73372e5089d124f6508d381f371` |
| Targeted Fable wording-edits response | `1175c95962fd667ef6cb0e849f203b518143619b436db75d08081d8f1cc6b4e7` |
| Targeted Fable wording-edits result receipt | `fd1ef056966aa7789f99e6ed875cef9206809f9cbc83191884c01e45d1299ea9` |
| Scratch static receipt | `9453663749c8c2b3c395d925004a5b784aff48ceeac810deb921b9f847c7bf55` |
| Fable completion prompt | `4096bd413e9953de7cb04db07472ce4e467fb1697b0041570d8be490b95cb166` |
| Fable completion source bindings | `e429e1ab9d59f5519841973196cedbc405ff4ff7ae60bb0844e4cc1fe5cce4cb` |
| Fable completion response | `4d983b84cf9f49008f32535fc3f7f000b9cb335c984a73e2626a30be7d952815` |
| Fable completion launch receipt | `50656810e7fc355450a1e98e49d2a5d2a1b1e92d0bc32c964e9cb7bd39e7a4d5` |
| Fable completion result receipt | `b7f093ee1882ac6d6f395521d541abaa023c16b0d2eb13c9bf709f0a3426277c` |
| Fable completion native stream | `b6cde9395cdab93a6b1349c09cda5a5a6822cffefdc8fd1fe57a68d40d322c7f` |
| Fable completion static prompt | `924f0c37a7ec49abc42db5eae7abbae18f5577827f1cdef1dd4a6d4bfa9a5eb1` |
| Fable completion static source bindings | `7c1fb919e8c08993040acb12bd2422e75f9814755710aa976e8d94340a001d12` |
| Fable completion static response | `d8acd4633425bbf46a8f2a83da0b009b83f648a49ac15fb75b2fd8f5a1e3cfb9` |
| Fable completion static launch | `e212d74d0b14e777649d2d041e5e365fadcd5dd4afde68162ca757e948f26dc4` |
| Fable completion static result | `531db2232001d23e361fc5c056c1101f0c7837eea71348e4197c7055de9f6e7a` |
| Completion static receipt | `21ddc3dd1f9c69ccf9014146bae160f08b198053384b2521270c4c2289d3bf4f` |
| Completion invariant summary, including separate instruction record | `b1eec0e2c70fe9aba923c4b22bb6e04c98071800dfb17fd5c91502a1ccd91137` |
| Inline static receipt | `ce1134149232626ecbec32cda8ef0667a945dfbec86f3c5caad24252e1521ca1` |
| Fable inline prompt | `a86d9e29823ef06dc22cd40e555c6aef228110608e0eb8923ae81d49014b0952` |
| Fable inline source bindings | `d7401c3197a16c7aa3fafc83a0f439909f54ed22c46d0c53af75d506a870f90c` |
| Fable inline response | `7b8671c3116fd3376cb3bf0f361107c65295a85c8d954acac04100bd06deaa40` |
| Fable inline launch | `42302adeb8c9d82906b3cb66a342dd2dbc2f7ba07534d803a6eba19f0b9baf29` |
| Fable inline result | `e278ab370bc24d4b7d43922ed0f52dd01a1f46e866198b5933315df50579cd60` |
| Fable inline native stream | `a1e9abf2061754eb8ce27a1c73afe30138412fedeb37819c981a5650f9d2a89b` |
| Inline invariant summary, including dependence check | `ab2b5afcbce3fe34a289c2d6184f843bdec849a310255119ef68869bd4ba3557` |
| Final release-candidate aggregate | `afec63afd7c075ce9c1ac905ec0142b10e3498667dc1ea485be95dfe85e3dd46` |
| Simplification adjudication prompt | `e819480b970e1085619c8156c07c072a1be53044c83fa366f8e39f68184c0dc6` |
| Simplification adjudication source bindings | `3e9cd4c2dc2e861051c54b529248acf48df1ba458c74842d9a9d092215cfea7e` |
| Simplification provisional archive bindings | `6d3d3c2af19f33ca0a5855944d88f3aa27190c202fb6eeebffd865847debdd8d` |
| Simplification Fable response | `dcd96f5bd230d5f8b51a8ec09a361f918e3efe2ed0067d51d04dbeaf83eb171a` |
| Simplification Fable launch | `4c1ed9a047a126d649c06d8547295a9bbdf2c11d92d0ccefbff711adca8f485a` |
| Simplification Fable result | `f40bbdd9e0d4453cf8d75a94ba8445b1879e746ba413cdf40de1492141a91725` |
| Simplification parent decision | `e0ad575a3b97053d404ffe4a1dcd0d61ad6e197a89a538bdcf1685493cb41356` |

Replay 1's original assessment hashes the extracted response text before writing
as `d9994f4e42d87aa774a1095ff5ce0b17288dc8cacd490d67a5bce94b91a4b378`.
The written `response.md` adds one final LF and hashes to
`2f7d0ed39c9771ff39068a8b9e0ab72b7a38c514f2942f4e8dc868d2f25ec89b`.
The retained binding erratum (local-only artifact `/tmp/hardening-review-replay/binding-erratum.json`)
explains both bindings without changing the original assessment. Removing
exactly the final LF reproduces the original digest; this is an extraction
formatting difference, not evidence of changed response content.

The [running protocol](../evals/skill-composition/RUNNING.md) requires a fresh
six-run sequential pilot for the repaired version and permits one full 18-run matrix only after
6/6 acceptance on the same plugin bytes. A failed batch requires diagnosis,
material repair, and a new declaration. Original frozen inputs remain unchanged.
Final accounting is 181 confirmed native starts across 198 declared slots.
The evaluation gate is satisfied on the frozen candidate. Consult the linked
release and CI records for publication status.

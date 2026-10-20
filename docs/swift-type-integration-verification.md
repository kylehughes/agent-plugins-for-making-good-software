# Swift type-system verification

Compiler acceptance and the 24-run behavioral selection pass. The final independent
bounded review found no actionable findings. This report records Goal 2's checks; Goal 1's
[integration record](swift-type-system-validation.md) remains historical. Only
the six acceptance criteria in the Goal 2 request define completion.

## Starting evidence

Work started at `0fd5fff` with a clean worktree. The supplied ZIP hashes to
`4454c583ec5a9cc4dd80487ff19a9a2dc9925e5249588db8e4a06482bf35eb13`.
The [baseline record](../evals/swift-type-integration/baseline.json) retains exact
commands, exit codes, and log digests. All seven baseline commands exited 0:

- `git status --short` and `git rev-parse HEAD`.
- `python3 -m unittest discover -s scripts -p 'test_*.py'`: 127 tests passed.
- `python3 scripts/validate.py`.
- `python3 scripts/skill_catalog.py --base HEAD`.
- `python3 scripts/check_swift_type_system_integration.py --source-root /tmp/swift-type-system-integration-source/Swift_Type_System_Companion`.
- `REQUIRE_SWIFTC=1 plugins/apple-platform/skills/modeling-swift-types-for-correctness/scripts/check_examples.sh`:
  five valid controls, five intended rejections, and the existing runtime check passed.

The [environment record](../evals/swift-type-integration/environment.json) records
macOS 26.6.2 on arm64, Xcode 26.6.0's Apple Swift 6.3.3, Codex CLI 0.160.0, and
Claude Code 2.1.282. The supplied compiler report instead records Swift 6.4.1 on
x86_64 Linux. Its results are supplied evidence, not fresh local checks.

## Compiler acceptance

Xcode 27.1 resolved the compiler-access blocker. The
[updated environment](../evals/swift-type-integration/environment-xcode27.1.json)
records Apple Swift 6.4 (`swiftlang-6.4.0.34.1`) and the macOS 27.0 SDK on the same
macOS 26.6.2 arm64 host. This is a fresh local result; the supplied Swift 6.4.1
Linux reports remain separate historical evidence.

The [coverage count](../evals/swift-type-integration/compiler-evidence/coverage-count.json)
matches all 89 indexed identities and expectations: 15 core, 10 modeling,
9 effects, and 55 frontier cases. There are 81 default and 8 experimental cases.
The check compares copied source bytes, appended core/modeling counterexamples,
frontier source digests, and both runtime source identities with the supplied
archive. None of those source fixtures changed for the Apple compiler.

The [current compiler report](../evals/swift-type-integration/compiler-evidence/observed-6.4-macos.json)
passes all 89 cases: 31 accepted compilations and 58 intended rejections. All 15
paired-control invocations pass; every case was invoked, with no blocked case,
crash, or timeout. Acceptance/rejection outcomes match the supplied report.
Thirteen negative cases use reviewed diagnostic alternatives for this exact
Apple compiler build. Each alternative requires all its listed messages and
rejects any additional source error. The original supplied markers remain in
the mapping; the alternatives include a rationale tied to each counterexample.

Both exact runtime sources, `core_examples_runtime.swift` and
`modeling_examples.swift`, build and execute successfully: two build exits and
two runtime exits of 0, with expected output. Their assertions establish only
the checked examples. The unchanged keyed-decoding controls separately pass
full skill validation; the imported scalar-decoding example does not establish
keyed-format compatibility. No decoder implementation changed.

The final corpus command exits 0:

```sh
python3 plugins/apple-platform/skills/modeling-swift-types-for-correctness/scripts/swift_compiler_corpus.py \
  --swiftc /Applications/Xcode-27.1.0.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/bin/swift-frontend \
  --compile-target arm64-apple-macosx27.0 \
  --report /tmp/swift-corpus-6.4-xcode27.1-final.json
```

SIL controls and cases share Swift 6 language mode, SDK, deployment target, and
case feature flags. The report retains effective commands, input hashes,
diagnostics, exits, platform, and toolchain identity. The compile-only target
is macOS 27.0 because six supplied examples use APIs unavailable at the
compiler's macOS 26.0 default target. Runtime builds omit that override and use
the host-compatible default. This proves neither execution of macOS 27 APIs on
this host nor compatibility with an older deployment target. Unsafe, effects,
and frontier probes remain compilation-only. Performance experiments remain
unsupported illustrations outside the counts.

The [attempt index](../evals/swift-type-integration/compiler-evidence/attempts.json)
retains the failed Swift 6.3.3 runs and two initial Swift 6.4 runs. The first
Swift 6.4 run exposed deployment-target availability failures. The second
matched all accept/reject outcomes but failed strict diagnostic checking for
one additional `Span` initializer diagnostic. These failed attempts are not
pooled into the final 89 passing results.

## Frozen behavioral matrix

The [case configuration](../evals/swift-type-integration/cases.json) contains six
positive cases, four near misses, and two additional decoding installation
variants. Prompt and rubric IDs are retained in their files. The runner strips
prompt frontmatter before sending the natural-language request to the child;
rubrics remain outside its workspace.

The [run plan](../evals/swift-type-integration/run-plan.json) binds every prompt,
rubric, and case configuration before native execution. All twelve cases passed
the existing harness's preparation checks. Pre-run corrections and their prior
hashes are recorded in the [freeze metadata](../evals/swift-type-integration/frozen-criteria.json).

Each runtime must produce ten accepted main runs and two additional accepted
decoding runs. The declared models are `gpt-6.1-sol` and `claude-sonnet-5-5`, both
at high effort with a 900-second timeout per case. These match the previous
invariant matrix's settings; no conclusion about medium-effort behavior follows.
Claude's skill-list budget is 24,000 characters per child.

Acceptance follows [invariant verification](invariant-verification.md): complete
response and tool-trace review, separate behavior/scope/evidence-honesty and
composition verdicts, then evidence finalization and strict verification.
Successful process exit alone does not count. Failed attempts remain evidence.

The user explicitly approved sending the frozen prompts and loaded local plugin
content to OpenAI and Anthropic APIs after two prelaunch approval-review
rejections. The batch then started against plugin snapshot
`08471c4a8f7372a31940d2af43a6e74f62e269171a324925e048cf4c8394e583`.
The first Claude launch failed before answering because its OAuth session expired.
After the user signed in again, all 24 evaluations completed with process exit 0.
Full semantic reviews accepted 15 and failed nine; all 25 execution receipts,
including the authentication failure, pass evidence-integrity verification. The
[initial native results](../evals/swift-type-integration/native-results-attempt-01.json)
retain commands, models, runtime versions, snapshot identities, artifact hashes,
review verdicts, and paths to full local traces. The 22 queue entries left
unstarted after the authentication error are not additional execution failures.

| Case | Codex | Claude |
|---|---|---|
| Validated decoding | PASS | FAIL: focused reference not loaded |
| Recoverable workflow | FAIL: concrete evidence scenarios omitted | FAIL: reference and evidence scenarios omitted |
| Correlated generics | FAIL: advanced-encoding selection condition omitted | FAIL: expression relationship incomplete; reference not loaded |
| Static dimensions | PASS | PASS |
| Ownership/lifetime | PASS | FAIL: actor isolation confused with exclusivity |
| Typed failures across concurrency | FAIL: cancellation scenario omitted | FAIL: composition, failure controls, and cancellation mapping |
| Ordinary output tests | FAIL: test name omitted | PASS |
| API naming | PASS | PASS |
| Prose editing | PASS | PASS |
| Defect review | PASS | PASS |
| Decoding: Apple Platform alone | PASS | PASS |
| Decoding: combined plugins | PASS | PASS |

The failed checks prompted scoped guidance corrections: mandatory focused
reference loads, concrete recovery and cancellation evidence plans, the distinction
between actor isolation and exclusivity, complete expression-result modeling,
and named test plans. No prompt, rubric, or acceptance rule changed. Discovery
metadata and shared guidance changed, so the entire 24-run matrix was repeated
against the corrected snapshot; prior passes did not substitute for that matrix.

Automatic approval review initially required separate authorization for the changed
payload. After the user approved it, the [first corrected matrix](../evals/swift-type-integration/native-results-attempt-02.json)
completed all 24 runs and accepted 20: 16 main runs and all four configuration
variants. Every receipt passes integrity verification. The four remaining failures
were Claude's missing concrete evaluator example, both runtimes' omitted
index-bounds/layout limits for static dimensions, and Claude's missed ownership
skill/reference activation with incomplete boundary and evidence coverage.

One Codex ownership review was reconsidered against the unchanged rubric: unsafe
pointer extraction from a lifetime-restricted view is a concrete erasure boundary.
The initial failed review had required a narrower existential/box example that the
rubric did not require. Both review versions and the initial failed receipt remain
available in the result record.

The second correction explicitly named borrowed-view lifetimes in discovery metadata
and made the generic recipe's evaluator example and separate bounds/layout
obligations explicit. Its combined snapshot was
`7183f99e5eb7dec368331dee3173b7e0d4d2db4b66e86a782b1b1a82c67914cc`.
The [second corrected matrix](../evals/swift-type-integration/native-results-attempt-03.json)
completed 24 runs with 21 accepted: 17 main runs and all four configuration runs.
Every receipt passes integrity verification. Three Claude runs failed: static
dimensions omitted dynamic-index bounds, ownership omitted foreign-alias/storage
obligations, and an otherwise valid output-test plan did not load the testing skill.

The third correction made test planning explicit in discovery metadata, added an
arbitrary-index example, and required borrowed-view assessments to state foreign
alias and storage obligations. Its combined snapshot was
`590deaf2e714a5563b56a95646d3e14832abd451da2f2563bcef6cdd524fed33`.
The [third corrected matrix](../evals/swift-type-integration/native-results-attempt-04.json)
accepted 21 of 24 runs: 17 main runs and all four configurations. Both runtimes
passed generic modeling, static dimensions, and all near misses. Three Claude
answers failed: the workflow omitted the eventual-submission limit; ownership
claimed a generation guard catches extracted raw-pointer uses; and typed errors
put cancellation in an outer wrapper while the inner failure type discarded it.
Every execution and evidence-integrity check passed; those facts did not override
the semantic failures.

The fourth correction changes only the workflow and ownership/effects references.
It separates recovery from mandatory completion, bounds generation guards and
borrowing claims, and requires cancellation to survive the complete signature
chain. The [impact audit](../evals/swift-type-integration/correction-impact-04.json)
checks all 24 complete traces and the actual two-file delta. Six affected runs
were repeated: workflow, ownership, and typed errors on both runtimes.
The other 18 accepted runs retain their original snapshots and receipts; their
catalog, entrypoints, and successfully loaded content are unchanged. This is
an affected-case rerun, not a fresh 24-run matrix against one final snapshot.

The [fourth corrected attempt](../evals/swift-type-integration/native-results-attempt-05.json)
accepted three of those six runs: both ownership answers and Claude's workflow.
Codex's workflow omitted its terminal success payload. Both typed-error answers
used an unannotated `do` inside a task closure, which inferred `any Error` and
contradicted their promised `Result` failure type. The responses honestly said
they were uncompiled, but the transport design still failed the frozen rubric.
Paired reviewer compiler checks reproduced the exact error and accepted the
single-change `do throws(Failure)` control.

The fifth correction supplied a complete typed-task example and asked workflow
sketches to show their terminal outcomes. [Those six reruns](../evals/swift-type-integration/native-results-attempt-06.json)
accepted five, producing a [23-of-24 selection](../evals/swift-type-integration/native-selection-attempt-06.json).
Both runtimes passed typed-error transport and workflow recovery. Claude's
ownership answer omitted the actual live/stable-storage obligation after reading
only keyword-matched lines, which split the reference's wrapped paragraph.

The sixth correction requires reading the complete ownership section and keeps
that obligation in one paragraph line. It adds no new compiler claim. The
[impact record](../evals/swift-type-integration/correction-impact-06.json) identifies
five affected reruns: ownership and typed errors on both runtimes, plus Codex's
workflow, which loaded that reference. Nineteen accepted runs are carried:
18 from the third corrected matrix and Claude's workflow from the fifth. Their
catalog and loaded content are unchanged; receipts preserve the original hashes.
The [follow-up plan](../evals/swift-type-integration/followup-plan.json) records
combined snapshot
`aa32b43a4fe2bde32747a4268cb91ff17ef7a5688af920ce03707c2bf90d54cb`.
All [five final reruns](../evals/swift-type-integration/native-results-attempt-07.json)
passed full semantic review and strict evidence verification. The
[accepted selection](../evals/swift-type-integration/native-results.json) contains
20 main runs and four configuration runs, with every selected receipt reverified.
The native versions are Codex 0.163.0 and Claude Code 2.1.304. Prompts, rubrics,
models, and settings stayed frozen; the user authorized necessary evaluations
and corrections without further confirmation.

| Attempt | Completed runs | Accepted | Failed semantic review |
|---|---:|---:|---:|
| Original | 24 | 15 | 9 |
| First correction | 24 | 20 | 4 |
| Second correction | 24 | 21 | 3 |
| Third correction | 24 | 21 | 3 |
| Fourth correction | 6 | 3 | 3 |
| Fifth correction | 6 | 5 | 1 |
| Sixth correction | 5 | 5 | 0 |
| Total | 113 | 90 | 23 |

The separate initial OAuth failure is one additional failed execution. The final
selection is five final-snapshot runs plus 19 earlier accepted runs with unchanged
loaded content, not a fresh 24-run final-snapshot batch. Iterative corrections
were informed by these frozen cases; this is neither a held-out evaluation nor
a statistical reliability estimate. Full responses, transcripts, evaluator
engines, and receipts remain at the recorded local temporary paths; deleting them
prevents strict reverification. In-repository summaries retain hashes and verdicts.

## Release metadata and context costs

Apple Platform's three version fields move together from 1.6.0 to 1.6.1 through
`python3 scripts/bump.py apple-platform patch`. Universal remains unchanged.
Nothing was published. The first packaging gate found Python bytecode generated
by local imports; the runner and test loader now suppress bytecode only around
those imports and restore the previous policy. A subprocess regression exercises
the CLI with `PYTHONDONTWRITEBYTECODE` unset. The failed gate remains in
[attempt 1](../evals/swift-type-integration/repository-checks-attempt-01.json).

Sandboxed Swift 6.4 checks failed when the standard compiler cache was not
writable. Those attempts are retained, including the earlier
[failed attempt](../evals/swift-type-integration/repository-checks-attempt-03.json);
the same suite and affected-skill checks passed with normal cache access.

The [current check record](../evals/swift-type-integration/repository-checks.json)
retains exact argument arrays, exit codes, log paths, and log hashes. These
commands passed after the guidance corrections. Source/count checks reuse their
unchanged-input results, and the record distinguishes those checks. The final
reference-retrieval edit reran the repository validator and diff check; unit and
catalog results were retained because their code and catalog inputs were unchanged:

```sh
python3 -m unittest discover -s scripts -p 'test_*.py'
python3 scripts/validate.py
python3 scripts/skill_catalog.py --base HEAD
python3 plugins/apple-platform/skills/modeling-swift-types-for-correctness/scripts/validate_skill.py
python3 /tmp/swift-type-integration-goal2/count_corpus.py
python3 scripts/check_swift_type_system_integration.py --source-root /tmp/swift-type-system-integration-source/Swift_Type_System_Companion
git diff --check
```

The unit suite passed all 135 tests. Full skill validation passed its five
positive controls, five intended rejections, and existing runtime check. It
reported one limitation: `skills-ref` is absent, so its built-in validation ran.
The separate required corpus gate also passes all 89 cases.

The new task example also has a focused Swift 6.4 SIL pair outside the 89-case
imported corpus: its explicit typed `do` compiles (exit 0), while removing only
that annotation fails with the intended `any Error` conversion diagnostic
(exit 1). [The check record](../evals/swift-type-integration/repository-checks.json)
links the exact commands, sources, and outputs. An initial attempt without an
explicit SDK failed to find the standard library and is retained as an environment
failure; it is not counted as an intended rejection.

The six manifest files passed `python3 -m json.tool`; both
`claude plugin validate plugins/apple-platform` and
`claude plugin validate plugins/universal` exited 0. The local Codex
`plugin/read` smoke check loaded 19 Apple Platform and eight Universal skills.
That protocol check does not establish agent registration or model behavior;
the repository validator separately checks agent metadata and same-plugin skill
references. These checks do not count toward AC4 or AC5.

`python3 scripts/skill_catalog.py --base HEAD` measures characters, not tokens:

| Measure | Starting | Current | Delta |
|---|---:|---:|---:|
| Skill descriptions | 5,442 | 5,455 | +13 |
| Skill entrypoint bodies | 264,665 | 265,861 | +1,196 |
| Skill body lines | 3,786 | 3,795 | +9 |
| Agent descriptions | 1,630 | 1,630 | 0 |
| Summed preloaded skill bodies | 79,448 | 80,325 | +877 |

There are still 27 skills and eight agents. No preload membership changed.
Compiler fixtures, reports, and evaluation criteria are outside default skill
body loads. The changed type-modeling body is 19,578 characters and 203 body
lines; its discovery description is 274 characters. The focused recipe additions
load only when their concerns apply.

## Acceptance status

| Criterion | Status | Remaining evidence |
|---|---|---|
| AC1 | PASS | All 89 identities mapped and all 89 compiler outcomes pass; 81 default and eight experimental cases. Exact-build diagnostic differences are recorded. |
| AC2 | PASS | All 15 paired controls and 58 negative cases pass under shared SIL settings; both runtime examples build and run with exit 0. Decoding implementation is unchanged. |
| AC3 | PASS | Ten natural-language prompt/rubric IDs, six positive concerns, four near misses, and unchanged pre-run hashes. |
| AC4 | PASS | All 20 main runs are accepted, with successful local composition, full semantic/trace review, and strict receipt verification. Affected-case reruns and unchanged-content carry-forward are recorded. |
| AC5 | PASS | All four configuration runs are accepted with unchanged loaded content; the [final bounded review](../evals/swift-type-integration/final-review.json) records coverage, claims, fixtures, report, and final-answer checks with no actionable findings. |
| AC6 | PASS | 135 tests, repository/skill/source/manifest checks, release metadata, context costs, and the required compiler corpus pass. |

All six acceptance criteria pass within the recorded toolchain and case bounds.
The selected behavioral evidence combines five final-snapshot reruns and 19
unaffected earlier accepted runs; it does not estimate general reliability.
Full native traces remain at the recorded temporary paths for reverification.

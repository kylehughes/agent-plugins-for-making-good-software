# Swift knowledge-base ownership

The 2026-10-20 consolidation gives each Swift concern a maintained owner and a
short route from the skill entry point. The imported research remains represented
in the [coverage ledger](swift-type-system-integration.md); historical evidence
and source conflicts remain in [source decisions](swift-type-system-source-decisions.md).

## Loading and ownership

Read the relevant skill body first. It establishes the assessment contract, then
routes to a section for the changed concern. Read supporting mechanics only when
the selected recipe needs them. A borrowed-view assessment requires the complete
ownership section so storage and aliasing obligations are not lost in an excerpt.

| Concern | Canonical owner |
|---|---|
| Representation choice and rollback | Modeling skill's decision guide |
| Sums, products, validated construction, structural collections, compatible decoding | Algebraic and refined values |
| Nominal identity, basic typestate, trusted-issued capabilities | Identity, typestate, and capabilities |
| Compound domain relationships, recoverable workflows, public equality and evolution contracts | Domain modeling recipes |
| Protocol, abstraction, pack, key-path, and generated-API mechanics | Advanced generics and protocols |
| Correlated generic APIs, dimensions, expression sorts, proof witnesses and advanced encodings | Generic proof recipes |
| Ownership operations, language isolation boundaries, strict memory safety, typed-throws mechanics | Ownership, concurrency, and errors |
| Borrowed projections, error transport, completion obligations, binary representation | Ownership and effect recipes |
| Scheduling, isolation repair, task lifecycle and cancellation | Using Swift Concurrency |
| Compatibility axes and package/build policy | Writing Swift's Swift compatibility reference |
| Deployment adapters and stable/preview build policy | Modeling skill's iOS versioning reference |
| Dated compiler/SDK support, availability, experiment flags, unavailable features | Swift feature status |

Mechanism guides and recipes link in both directions only where a task needs the
other layer. Repeated decision rules were replaced with pointers to their owner;
unique examples, proof limits, boundary obligations, and advanced encodings remain.
The Universal invariant procedure stays platform-neutral and optional for an
Apple Platform installation alone.

The former `swift-6.3.2.md` and `swift-6.3-concurrency-model.md` references are now
`swift-compatibility.md` and `concurrency-model.md`. Maintained inbound routes were
updated. Skill and agent invocation names are unchanged. At that historical consolidation snapshot, this repository's rename policy
required both platform manifests and the Claude marketplace entry to prepare
Apple Platform 2.0.0. Later candidate versions supersede that number; this
document does not record a publication.

## Preserved research and evidence

The map retains 262 catalog entries across 18 families, 21 release rows, and 323
HTML headings: 606 records, with no exclusions. The ten worked examples remain
covered. Catalog IDs, source digests, dispositions, source URLs, imported compiler
fixtures, frozen native-evaluation criteria, and previous acceptance records are
preserved. Destinations follow moved canonical material rather than forwarding
stubs. The rendered ledger is generated from the machine-readable map.

The feature-status reference owns current dated facts. Historical source reports
retain their original provenance and limitations; later Apple compiler results
are separate evidence. A preserved release survey is not a second current
baseline. Compatibility examples may deliberately use a lower tools-version floor
or deployment target; those illustrate independent compatibility axes.

The skill-local trigger and quality scenarios now point maintainers to the frozen
native suite in `evals/swift-type-integration/`, with additional local coverage for
generic correlation, expression result sorts, and borrowed storage. Those local
scenarios are design checks, not claims that an agent run passed.

## Verification

`scripts/validate.py` now checks local file targets and Markdown fragments across
skill entry points, maintained references, and agent instructions. The coverage
checker shares its anchor implementation. Focused regression tests cover heading
renames, duplicate slugs, explicit IDs, same-file links, encoded paths, reference
definitions, and fenced examples. External URL health and arbitrary Markdown
syntax remain outside that checker.

The consolidation passed 146 unit tests, the repository validator, the source-backed
coverage check, both Claude plugin validators, all six manifest parses, and local
Markdown route checks. The skill validator also passed its compiler controls,
misuse fixtures, and runtime example; its optional `skills-ref` check was unavailable.
The unchanged imported corpus retains its separately recorded Goal 2 evidence.

Discovery metadata remains 5,455 skill-description characters and 1,630 agent-description
characters. No skills, agents, or preloads were added. Topic routes add a small amount
to entry-point bodies; the exhaustive material remains conditional.

[Native rerun records](../evals/swift-type-integration/consolidation-results.json)
contain one fresh attempt for each of six positive cases on both runtimes. All 12
passed deterministic checks and had matching source snapshots; semantic review
accepted 11. Codex's typed-error response omitted the frozen rubric's required
concrete precision-loss counterexample, although it selected the intended design,
loaded the required guidance, and reported execution limits honestly.
The failed receipt remains part of that snapshot's record.
Every finalized receipt, including the failure, passed integrity verification.

That consolidation batch had 12 positive-case runs, not a fresh 24-run matrix.
Near misses and configuration variants were not rerun. Final stale-wording repairs
in sibling guides, utility messages, and decision-guide anchors followed those
runs; the record lists their exact scope. Do not describe the runs as fresh
execution of that final wording. The prior
[Goal 2 verification](swift-type-integration-verification.md) remains a historical
record of its own source snapshot and native-run selection.

The [native-evaluation follow-up](../evals/swift-type-integration/native-counterexample-followup.json)
addresses that omission in the focused error-transport recipe. The original trace
rules out failed retrieval: Codex read both the full reference and its Effects
section. The recipe explained the repair without explicitly requiring a diagnosis
of the loss being repaired. That is an actionable guidance gap, not evidence of
the model's internal cause. The recipe now asks for the incoming failure type,
the broadening boundary, and the lost caller capability, with a concrete example.

Two declared follow-up batches accepted 6 of 8 and 7 of 8 runs. Both Codex
typed-error attempts passed in each batch. Claude failures exposed uncompiled
adapter proposals and an unreachable separate cancellation outcome; those failed
receipts are retained. The recipe now calls for checking the exact proposed
adapter with its constructing and awaiting caller, and illustrates a separate
cancellation outcome flowing from the core operation through the task.

The final batch accepted all four typed-error runs: two attempts each on Codex
and Claude, with unchanged prompts, rubrics, models, and effort settings.
Ownership and workflow passed on both runtimes in each earlier batch; their
sections were unchanged by the final error-transport example and were not rerun.
All 20 follow-up receipts passed integrity verification. Final checks also
passed 146 unit tests, repository and skill structure checks, source-backed
coverage, both Claude plugin validators, and manifest checks. Discovery metadata
and entry-point bodies did not change in this follow-up.

Paired compiler probes confirmed the precision loss and checked the new transport
example with a constructing and awaiting caller. A runtime probe confirmed that
an explicitly supplied cancellation outcome survives with a clear task flag.
One final Claude run also exercised started-work cancellation through its proposed
handle and dependency cancellation using stand-ins. Execution varies by run;
pending and environment-blocked checks remain explicit. These checks do not prove
production dependency mapping, automatic cancellation propagation, or post-commit
behavior. Iterative batches are development evidence, not a reliability estimate.

[Fable 5.1's independent static review](swift-type-system-consolidation-review.md)
approved with no release blockers and confirmed that all seven earlier follow-ups
were addressed. Its optional findings identified remaining stale sibling wording,
two whole-file decision-guide routes, an unused import, and this report's pending
verification paragraph. Those were corrected after the initial review. Fable
then returned **APPROVE** on the bounded follow-up, confirming all four corrections
and no loss of source substance. That verdict covers organization, ownership, and
currentness at the consolidation snapshot. It predates the focused native-evaluation
fix and does not certify those later edits or the native behavioral matrix.
Nothing in this record claims publication or universal correctness.

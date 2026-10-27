# Matched evaluation protocol

## Freeze and access

Before the first run, verify SHA-256 hashes in `manifest.json`. Freeze producer packets and evaluator keys together. If a packet, key, or scoring rule changes, create a new freeze identifier and retain the previous one with its results; do not silently change the benchmark after observing outputs. Freeze the candidate skill and baseline guidance by revision/hash as well. The manifest freezes these packet inputs, not a skill version or completed result.

An operator may read keys to set up reader trials. Producers receive only their selected `producer/<id>.md` and the guidance for their assigned arm. Do not point producers at this repository, the manifest, protocol, other packets, or evaluator-only directory. Use isolated copies or a context-only session that cannot inspect the benchmark tree. A read-only full-repository session still leaks keys. Producer contexts include the request, factual source, and starting documents exactly as supplied; no key-derived hints or reader questions are added.

Cases 07 and 08 are held out. Keep both their producer packets and keys out of development runs, tuning, and worked examples. Open them only after the candidate skill, comparison plan, and rubric are fixed. Record the first held-out run; failures remain results. If later used to revise the skill, relabel them development and replace the held-out set before another generalization claim.

## Comparison arms

- **Existing-guidance baseline:** same capable producer, same existing `writing-technical-prose` and human-writing guidance, same applicable repository/user instructions and relevant writing references. Include ordinary source inspection and reasonable editorial judgment. Do not suppress organization advice already present in this guidance.
- **Added-skill arm:** identical context plus the candidate `designing-documents` body and the references it selects. The addition is the intervention; no extra user hints, evaluator keys, model capability, time budget, tool access, or permission.

Use fresh sessions for every arm/case, with the same model, reasoning effort, output budget, tool availability, and factual inputs. Record exact guidance bytes, reference reads, runtime/version if available, and any automatically injected guidance. If candidate-only automatic loading changes more than intended, report the confound. No specific runtime, framework, browser, or command runner is required. Pair runs by case; randomize which arm runs first. Additional seeds are useful, but specify their number before seeing results. Do not choose the best treatment seed against an ordinary baseline seed.

The skill's stages are a production aid, not output requirements. Evaluate reader tasks and their relationships, appropriate scope and detail, conditions near their use, and source fidelity. Do not award points for naming stages, filling a template, or reproducing a preferred outline. Preserve distinction between creating, revising, and reviewing.

## Artifacts and cost log

Save raw producer output and delivered document(s), plus any changes to starting artifacts. Keep commentary distinct from the document a reader sees. If no change is authorized or needed, the original is the delivered artifact. An unauthorized rewrite is a mode result; do not quietly substitute it as the authorized artifact.

For each arm log: case/freeze, guidance hashes, producer model/effort, run order, elapsed time, input/output tokens when available, visible reasoning length or reasoning-token count when exposed, reference/tool reads, requested additions, actual new sections/content, word counts before/after, changed links/anchors, and omissions. Classify additions as supplied facts made explicit, supported reasoning/inference, or unsupported new facts; quote consequential examples and their source basis. Do not request private hidden reasoning. Use `unavailable` rather than estimate an internal count. Record the visible rationale, reader-task route, links followed, backtracking, and condition-to-action distance when observable. Long reasoning or added length is a cost, not evidence of better design.

## Reader trials and order blindness

Use independent readers who have not seen the skill, source packet, keys, arm identity, or producer commentary. Give a reader the specified starting context and question from the key, then the delivered document at the specified first or direct entry. Do not teach the answer first. Record the answer, confidence, lookup route, completion time, and any moderator help. For direct entry, withhold prior-page reading until the reader follows a link or explicitly seeks context. A linked route can succeed; record its cost. Ask follow-up 'what would you do next?' only consistently across both arms.

Assign opaque output labels and strip skill mentions from presentation metadata, without editing the artifact. Randomize arm labels and left/right or reading order. Prefer different matched readers for each output of the same case to avoid learning the facts. If reusing a reader, counterbalance order and report carryover; the second exposure is not independent. Judges receive the source and key after the reader trial, but remain blind to arm identity until scores and reasons are recorded.

Run a **no-document model check** with a separate reader model: provide only the reader's starting context and task question, without produced document, source packet, or key. Record correct guesses and invented certainty. This detects questions answerable from priors or question wording. It is a calibration check, not an alternate baseline and not a reason to reveal more answers to producers. Where useful, a separate source-only reader can establish whether a failed question was answerable from evidence at all; keep that upper-bound check separate from document usability results.

## Rubric by failure class

Label each relevant class `supported`, `concern`, `failure`, or `not applicable`: supported means an accurate, usable route without moderator repair; concern means partial, slow, or avoidably ambiguous; failure means task-blocking or materially wrong. Include a reason for not applicable. Support every concern/failure with a location and observed reader consequence. These are failure-class descriptions, not numbers to sum or average.

| Class | What to judge |
| --- | --- |
| Purpose and fit | Reader identifies the job, audience, scope, and a suitable choice. |
| Relationships and explanation | Reader understands distinctions, dependencies, causal behavior, and trade-offs needed for the job. |
| Sequence and conditions | Preconditions, branches, effects, verification, and stopping/recovery limits appear before they are needed. |
| Entry and navigation | First entry, direct anchors, and cross-document routes expose enough context to proceed. |
| Evidence and uncertainty | Claims match source; inference is justified; unknowns and conflicts remain visible at use. |
| Proportionality and preservation | Useful content/anchors survive; good text is left alone; length and structure earn their cost. |

Keep two explicit tracks: **content-preserving organization** (how existing supported information is arranged and connected, with additions identified separately) and **authorized completion** (whether the requested creation, revision, review, or no-change work is delivered). Do not attribute gains from added unsupported facts to organization.

Report task success separately: for each key question, `correct`, `partial`, `wrong`, or `unanswered`, with required conditions checked. A critical unsupported action or fabricated fact cannot be averaged away by attractive organization. Report **authorized completion** separately as `complete`, `partial`, or `mode violation`: full requested artifact, no unrequested operation, review-only restraint, and no-change controls. Do not label a producer's missing rewrite solely an organization failure. Record factual correctness even when organization is excellent, and organization even when a factual defect exists.

Use per-case paired task outcomes, failure classes, and the two positive controls. Do not compute a composite or pooled score. A win needs observable benefit on reader tasks or routes without material factual, authorization, or restraint regression. A tie is a valid outcome when competent baseline guidance already succeeds. A small pilot supports a local observation, not a general effectiveness claim.

## What the evidence can support

Human reader trials provide evidence of usability for those participants and tasks; record familiarity and sample size. Editorial judgments identify plausible design strengths/defects but do not establish measured reader success. Model-reader trials are repeatable proxies influenced by priors, context capacity, and deference to text; do not call them human validation. Automated link/hash checks establish integrity, not comprehension. Report these evidence types separately and retain disagreements rather than turning a model score into a human claim.

## Result template

Copy this once per paired case; do not fill in inferred results.

```text
Case / packet freeze / candidate guidance revision:
Split / date / evaluator:
Producer configuration and guidance hashes (baseline / added):
Arm order / opaque output labels / seeds:
Reference reads / tools / confounds:
Artifact paths and hashes:
Words before -> baseline / added; new sections, removals, anchor changes:
Time / tokens / visible reasoning length (or unavailable):
Authorized completion (each arm) and reason:
Reader type, familiarity, starting entry, presentation order:
Question | baseline answer/result/route/time | added answer/result/route/time
No-document check and optional source-only check:
Content-preserving organization findings (separate added content):
Added facts vs supported reasoning, with source basis:
Class | baseline evidence label | added evidence label | evidence/location
Factual or critical action defects:
Preservation and positive-control behavior:
Paired conclusion: benefit / tie / regression / inconclusive; reason:
Evidence limits and deviations from frozen plan:
```

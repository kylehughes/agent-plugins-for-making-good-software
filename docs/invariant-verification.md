# Invariant verification

Universal's `verifying-invariants` skill owns the procedure for specifying scoped
invariants, locating their boundaries, selecting evidence, and reporting limits.
Apple Platform's `modeling-swift-types-for-correctness` owns Swift representations,
checked construction, decoding, access control, and compiler restrictions. Swift
testing skills continue to own assertions and deterministic synchronization.

The existing design, review, simplification, hardening, and goal workflows link
to this procedure only for explicit invariant claims or changes to enforcement
models and transitions. No reviewer was added and no agent unconditionally
preloads it. Hardening retains its single compile checkpoint and separate project
test gate. Review-only work does not gain permission to mutate a project.

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

Use the same natural-language fixtures and review rubrics on both runtimes:

| Installation | Fixtures | Required behavior |
| --- | --- | --- |
| Universal alone | `plugins/universal/evals/invariant-verification/*` | Find unchecked decoding, mutable-child and stale-completion gaps; reject overclaims from bounded exploration and surviving mutations. |
| Apple Platform alone | `plugins/apple-platform/evals/invariant-verification/decoded-value` | Diagnose the Swift decoding boundary and propose focused evidence without depending on Universal. |
| Both | The Apple fixture with both plugins enabled | Compose the shared evidence procedure with Swift-specific enforcement guidance. |
| Near misses | New cases in `evals/skill-routing.json` and existing discovery smoke fixtures | Keep test organization, async flakiness, naming cleanup, and routine defect review with their existing owners. |

Each fixture has `rubric.md` for full-response and tool-trace review. Regex and
skill-invocation graders are smoke signals only: inspect the actual diagnosis,
scope, evidence limits, and claimed execution. All included verification prompts
are read-only. Confirm no edits, unsolicited registry, or CI changes. Do not pass
the rubrics or routing answer keys to the responding model.

For Claude's native harness:

```sh
claude plugin eval plugins/universal --eval-dir evals/invariant-verification \
  --ablation none --runs 3 --model claude-sonnet-5 --no-publish \
  --no-scaffold --trust-plugin --keep-temp --output-dir /tmp/universal-invariant-eval
claude plugin eval plugins/apple-platform --eval-dir evals/invariant-verification \
  --ablation none --runs 3 --model claude-sonnet-5 --no-publish \
  --no-scaffold --trust-plugin --keep-temp --output-dir /tmp/apple-invariant-eval
```

For combined Claude runs, load both reviewed plugin directories into a fresh
native session and submit the Apple fixture's body. For Codex, register the local
marketplace in a temporary Codex home, enable the required plugin combination,
and submit the same fixture bodies in isolated projects. Use the installed CLI's
help for supported registration and session options. Keep credentials private,
leave the user's installed plugin state untouched, and save raw transcripts
outside this repository.

Report runtime/model, repetitions, activation, behavioral outcomes, and limits
separately. Loading a catalog successfully does not establish behavioral
acceptance. A small smoke sample is not a guarantee of future invocation or
whole-program correctness.

## Validation results

The [2026-10-17 results](../evals/invariant-verification-results.json) record the
source snapshot, toolchains, context costs, and limitations for Universal 1.7.0
and Apple Platform 1.5.0.

- All 55 tooling tests pass, including malformed manifests and compiler failure
  modes. Both plugin validators pass. Real Swift 6.3.3 controls, negative fixtures,
  and runtime examples pass. The keyed decoding documentation example also
  preserves a historical payload and round trip while rejecting invalid input.
- Native Codex checks with GPT-5.6 Sol at medium effort pass all 11 required
  fixture/configuration outcomes. The combined case reads both skills; all four
  near misses avoid the invariant workflow. One incomplete async run was rerun.
  The temporary homes still enumerated account-managed plugins, so accepted
  activation required reads from the locally installed temporary cache.
- Claude Sonnet 5's three-repeat smoke suite passes basic content and read-only
  checks in 15/15 runs, but activates the verifier in 12/15. A separate full-trace
  review found content defects that those basic graders missed. After improving
  the guidance and decoder example, the bounded-exploration and Apple-only
  retests pass. The combined retest still omits Universal and suggests an
  incompatible scalar decoder for keyed data. That case remains a failed
  behavioral acceptance check. The four near misses avoid the verifier; three
  activate their expected owner and the ordinary code review answers directly.
- The 44-case description-selection probe scores 43/44: it selects the verifier
  but omits the Swift companion in the combined proof request. This probe cannot
  measure companion loading after activation.

These results establish working tooling and scoped behavioral evidence. They do
not establish reliable automatic composition on every runtime or correctness of
every generated suggestion. Keep the failing cases in the acceptance suite;
do not weaken their graders or count a correct diagnosis as a correct fix.

# Skill composition evaluation

This suite checks whether installed Universal and Apple skills form one bounded
workflow. It uses the existing native runner with `--config`; it does not modify
runner behavior. Both plugins are installed for every case.

| Case | Owned change | Expected composition |
| --- | --- | --- |
| `hardening-invariant` | Add saved-cart coding support | Hardening → invariant procedure + Swift modeling, with one compile checkpoint and pending project proof |
| `hardening-cosmetic` | Reword a model comment | Hardening stays mechanical; no invariant/modeling activation or build |
| `apple-simplification` | Remove receipt-list redundancy | Apple invocation loads Universal simplification and applies both in one workflow |

## Frozen run plan

Before any native run, `frozen-criteria.json` records the fixture, prompt, rubric,
and config hashes and all 18 independent run IDs. Each case runs three times on
Codex `gpt-6.1-sol` and Claude `claude-sonnet-5-5`, always at medium effort with a
900-second timeout. Every run starts in a fresh runner workspace and output
directory. All 18 must finish with `overall_status: accepted`. Keep every raw
failure, timeout, missing result, and failed attempt; never replace a failure
with a later pass or report a best-of result. Supplemental retries do not change
the predeclared acceptance denominator.

Use each record in the frozen run plan to supply these arguments, from the
repository root (replace the angle-bracket placeholders):

```sh
python3 scripts/run_invariant_behavior.py \
  --config evals/skill-composition/cases.json \
  --case <case> --runtime <runtime> --model <model> \
  --effort medium --timeout 900 --output-dir <new-output-directory>
```

No native runs are launched by fixture validation. Keep run output outside this
suite so it cannot become a fixture input.

## Acceptance and evidence

The frozen dimensions are `behavior`, `scope`, `evidence_honesty`, and
`composition`. The existing review format stores the first three in `criteria`
and the fourth in the separate `composition` verdict. Apply the case rubric to
the full response and raw tool trace, with explicit anchors for every dimension.
Missing evidence fails the affected dimension. Merely naming a skill is not
proof it loaded or influenced work. Verify completed reviewer results and their
read-only behavior, rather than crediting launch calls. Review final diffs
against the disposable Git baseline as well as the original harness snapshot.

The runner initially copies a fixture without Git history. Each prompt authorizes
`python3 bootstrap.py` to create one disposable baseline commit, then apply the
owned dirty change. The script refuses to reapply when `.git` exists. This is the
only permitted commit, confined to a disposable fixture; no repository commit or
`.git` directory belongs in the suite. Deterministic scope checks use the literal
`.git` subtree prefix for setup and Git reads; the harness does not interpret
`.git/**` as a glob. Semantic scope review must reject later commits or history
manipulation. The harness snapshot precedes bootstrap, so its required
path checks alone cannot prove the agent fixed anything. The semantic reviewer
must inspect the final code and regressions.

The substantive hardening case's hidden Swift assertions reject restored zero
and negative counts and check fixed historical keyed data and a valid round
trip. The simplification checker checks empty names, whitespace, order,
duplicates, Unicode, and embedded newlines. The harness compiles and executes
project tests and hidden assertions after the native agent exits. These harness
commands do not count toward the agent's single hardening compile checkpoint and
cannot support the agent's own proof claims. The cosmetic case has no runtime
checker because compilation would not demonstrate its scope discipline.

A passing deterministic assessment remains `pending_manual_review`. Finalize a
hash-bound review through `scripts/invariant_behavior.py finalize-review` and
check the resulting record with `verify-evidence`; only `accepted` counts.
Absent toolchain support, fixture failures, or missing transcripts never pass.
The lightweight fixtures use offline `swiftc`, compile the full dependent graph,
and keep products outside their working trees. The hardening case leaves
`sh Tools/project-proof.sh` for the project's later ship gate even when the
post-run evaluator independently executes its own checks.

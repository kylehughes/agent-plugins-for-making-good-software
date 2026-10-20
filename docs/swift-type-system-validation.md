# Swift type-system integration validation

## Scope and baseline

The acceptance contract is AC1–AC6 from the supplied Goal. This integration adds
progressively disclosed guidance and its provenance checks. Compiler-corpus and
native-runtime behavioral acceptance belong to Goal 2; no such acceptance is
claimed here. Nothing was published or committed.

Work began on 2026-10-19 at commit
`7a6ac750c6e9d1b30342d0bb3bdcc90185651469`, in the existing worktree
`/Users/kyle/Developer/Projects/Kyle Hughes/Codex Plugins for Making Good Software/Repositories/Plugins`.
`git status --short` was empty. The supplied archive SHA-256 matched
`4454c583ec5a9cc4dd80487ff19a9a2dc9925e5249588db8e4a06482bf35eb13`.
The archive was extracted to `/tmp/swift-type-system-integration-source/Swift_Type_System_Companion`.

Before edits, `python3 -m unittest discover -s scripts -p 'test_*.py'` passed
114 tests (exit 0), followed by `python3 scripts/validate.py` (exit 0) and
`python3 scripts/skill_catalog.py --base HEAD` (exit 0). Both Claude plugin
validation commands also passed. There were no pre-existing primary-gate
failures to exempt. Expected negative-fixture diagnostics in test output are
part of the tests, not repository validation failures.

## Design and coverage evidence

The existing type-modeling skill owns the four new references. No new skill or
agent was needed. Swift rules remain inside Apple Platform, Universal is
unchanged, and the shared instructions remain runtime-neutral.

- [Source map](swift-type-system-integration.md): original paths/anchors, all
  catalog and release decisions, HTML headings, member hashes, and original
  source links.
- [Family and routing review](swift-type-system-review.md): 18 family rubrics
  and 18 task-oriented routing walkthroughs.
- [Attribution](../plugins/apple-platform/skills/modeling-swift-types-for-correctness/ATTRIBUTION.md):
  supplied archive identity and derivation policy.
- [Feature decisions](../plugins/apple-platform/skills/modeling-swift-types-for-correctness/references/swift-feature-status.md#conflict-decisions-and-evidence-limits):
  primary-source corrections, duplicated core reports, performance-probe limits,
  and fresh/supplied/unknown evidence labels.

Apple Platform moves from 1.5.1 to 1.6.0 because the integration adds references.
The Claude marketplace and both Apple Platform plugin manifests agree. The Codex
marketplace has no version field and its two existing registrations still match.

## Context costs

Measurements are Unicode characters and source lines, not model tokens. These
figures compare the final owner entrypoints with the starting commit, using
`python3 scripts/skill_catalog.py --base HEAD`; HEAD remains the starting commit.

| Discovery or activation measure | Starting | Final | Delta |
|---|---:|---:|---:|
| Skills | 27 | 27 | 0 |
| Skill descriptions | 5,464 | 5,442 | −22 |
| Skill entrypoint bodies | 264,000 | 264,665 | +665 |
| Skill body lines | 3,787 | 3,786 | −1 |
| Agents | 8 | 8 | 0 |
| Agent descriptions | 1,630 | 1,630 | 0 |
| Summed preloaded skill body characters | 79,561 | 79,448 | −113 |

| Changed body | Starting characters | Final characters | Reason |
|---|---:|---:|---|
| Type modeling | 18,814 | 18,701 | Removed repeated representation routes; added four focused reference-map entries. |
| Swift implementation hub | 7,232 | 7,446 | Distinguishes the recorded compatibility baseline from newer feature decisions and routes generic relationships. |
| Swift concurrency | 8,140 | 8,704 | Removes stale preview assumptions and separates concurrency behavior from enforcement claims. |
| Type-driven design auditor | 7,826 | 7,946 | Explicitly uses conditional reference loading; the preload list is unchanged. |

The type auditor's single preloaded type-modeling body shrinks by 113 characters.
No agent gains a preload. The four new references add 92,351 characters outside
default loads (311, 327, 316, and 325 lines respectively). The largest updated
entrypoint has 200 total lines, including frontmatter. All curated references
remain at or below 500 lines. The longest skill description is 283 characters;
aggregate skill descriptions are below 7,000. Agent descriptions remain below
300 individually and 2,200 in aggregate.

## Validation commands and limits

| Command or check | Result | Scope |
|---|---|---|
| `python3 -m unittest discover -s scripts -p 'test_*.py'` | Exit 0; 127 tests passed | Full repository Python suite, including self-contained coverage-gate and verification-scope tests. |
| `python3 scripts/validate.py` | Exit 0 | Repository structure, manifests, budgets, references, and same-plugin agent preloads. |
| `python3 scripts/skill_catalog.py --base HEAD` | Exit 0 | Discovery/body/preload costs against the recorded start. |
| `python3 scripts/check_swift_type_system_integration.py --source-root /tmp/swift-type-system-integration-source/Swift_Type_System_Companion` | Exit 0 | 262 catalog IDs, 21 release rows, 323 HTML headings, 18 families, 10 examples; zero missing/duplicate records or broken destinations; all 38 archive members match their hashes; all 170 original source-index records are preserved. |
| `python3 plugins/apple-platform/skills/modeling-swift-types-for-correctness/scripts/validate_skill.py --skip-swift` | Exit 0 | Metadata, complete reference map, line limits, local links, eval/fixture wiring; compiler execution intentionally excluded. |
| `python3 -m json.tool <manifest>` for all six AGENTS.md manifests | Exit 0 for all six | JSON validity. |
| `claude plugin validate plugins/apple-platform` | Exit 0 | Claude plugin structure and content metadata. |
| `claude plugin validate plugins/universal` | Exit 0 | Unchanged plugin consistency. |
| `uv run --no-project --with pyyaml python /Users/kyle/.codex/skills/.system/skill-creator/scripts/quick_validate.py <skill>` | Exit 0 for all three | Type modeling, writing Swift, and Swift concurrency entrypoints. |
| `python3 /tmp/swift-integration-evidence/codex_metadata_smoke.py` | Exit 0 | Native local-path plugin metadata read: 19 + 8 skills. |
| `python3 /tmp/swift-integration-evidence/check_links.py` | Exit 0 | 22 affected documents, 118 local links/fragments; 200/500 line caps. |
| Audit-document local-link check | Exit 0 | 630 local links across the integration, review, and validation documents. |
| `git diff --check` | Exit 0 | Whitespace and patch integrity. |

The six parsed manifests are `.claude-plugin/marketplace.json`,
`.agents/plugins/marketplace.json`, and both `.claude-plugin/plugin.json` and
`.codex-plugin/plugin.json` under each of `plugins/apple-platform` and
`plugins/universal`.

The source map records **263 integrated, 313 merged, and 30 corrected** records
across its 606 entries; none are excluded. All 18 literal HTML `section` elements
have mapped enclosing anchors. The independent review found no actionable
coverage or routing defects. The parent corrected two tooling issues before the
final gate: tests depending on a temporary source path and incorrect rendered
JSON/HTML locator combinations. The source discrepancy decisions retain
conceptual guidance while limiting unsupported evidence claims.

`skills-ref` is not installed, so the skill validator reports its built-in fallback.
Its other warning records the requested `--skip-swift`. Neither is disguised as a
compiler or native-runtime acceptance pass. A temporary bytecode file generated
by a new import test initially failed packaging validation; the test now suppresses
bytecode for that import, the file was removed, and skill validation passes.

The metadata smoke check uses `codex app-server --stdio`, negotiates
`initialize`, and calls `plugin/read` for each plugin with this worktree's
`.agents/plugins/marketplace.json` as `marketplacePath`. It reads 19 Apple Platform
and 8 Universal skills from local source paths. It does not install a plugin,
change user configuration, or start a model turn. The current protocol does not
expose agent-registration introspection; agent frontmatter and same-plugin
preloads are checked by the repository validator and Claude validation. This is
a metadata-loading check, not Goal 2 native behavior acceptance.

Temporary raw command output and protocol responses are under
`/tmp/swift-integration-evidence/`. They are not packaged. The system Python lacks
PyYAML, so skill-creator validation uses `uv run --no-project --with pyyaml`;
the repository and skill validators use their normal Python entrypoints.

## Review follow-up

The follow-up review identified 24 incorrect HTML destinations: the decision
matrix, the release baseline and its 21 headings, and worked example 10. The map
now links them to the invariant taxonomy, release matrix and individual release
rows, and typed-error recipe. The rendered ledger was regenerated from the map.
All 24 destinations were checked against their intended sections.

The checker now reports whether success covers `structure only` or `structure
and supplied source`. When the temporary source directory is absent, it warns
that source verification was skipped and explains `--source-root`. An explicitly
missing source path or a source hash mismatch still fails. Four CLI regression
tests cover those outcomes, including both explicit and default source selection.
The targeted map suite passes all 10 tests. The full repository suite passes
127 tests with `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s scripts
-p 'test_*.py'` (exit 0).

The source-backed check passes for 262 catalog items, 21 release rows, and 323
HTML headings. These corrections change repository tooling and maintainer
evidence; the Apple Platform 1.6.0 plugin content is unchanged.

## Acceptance audit

| Criterion | Verdict | Decisive evidence |
|---|---|---|
| AC1 | PASS | 606 mapped records: 262 catalog IDs, 21 release rows, 323 HTML headings; all ten worked examples and all 18 section elements accounted for; 38 member digests match. Zero missing or duplicate entries and zero broken destination anchors. |
| AC2 | PASS | Four task-oriented references; independent 18-section rubric review retains practical recipes, advanced encodings, limitations, and simpler alternatives. |
| AC3 | PASS | All 21 feature rows separate support, flags, Apple availability, and evidence provenance. Primary-source decisions resolve release disputes; duplicate core reports and conflicting performance provenance remain explicitly bounded. |
| AC4 | PASS | Updated entrypoints have 200, 75, and 78 total lines; all curated references are ≤500. Complete maps, 118 production links, 18 routing walkthroughs, decoding controls, and unchanged preload membership were checked. |
| AC5 | PASS | 127 tests, primary validator, skill metadata, six JSON manifests, both Claude plugin validators, and local-path Codex skill metadata reads pass. Apple Platform 1.6.0 is consistent across versioned manifests. |
| AC6 | PASS | Descriptions meet 320/7,000 and 300/2,200 budgets. Entrypoint body growth is +665 characters; summed preloads shrink by 113. Detailed new guidance stays outside default loads. |

No introduced or worsened failure remains in these gates. Release availability
marked unknown is an explicit evidence boundary, not an inferred deployment
promise. Compiler-corpus and native-runtime acceptance remain outside this Goal.

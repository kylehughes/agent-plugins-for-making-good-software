# AGENTS.md

Repository guidance for Agent Plugins for Making Good Software.

This file is the canonical guidance for the repository. `CLAUDE.md` is a symlink to it, so Claude Code and Codex read the same instructions.

## Repository Shape

This repository is a plugin marketplace that is first-class on both Claude Code and Codex. The skill and agent content is shared; only the manifests differ per platform.

- The marketplace ships two plugins under `plugins/`:
  - `apple-platform` — skills and agents tailored to Apple-platform development.
  - `universal` — platform-agnostic tools for making good software.
- Each plugin holds its shared content and both platforms' manifests:
  - `plugins/<plugin>/skills/` — bundled skills, one directory per skill.
  - `plugins/<plugin>/agents/` — bundled subagent definitions.
  - `plugins/<plugin>/.claude-plugin/plugin.json` — Claude plugin manifest.
  - `plugins/<plugin>/.codex-plugin/plugin.json` — Codex plugin manifest.
- Marketplace manifests register every plugin:
  - `.claude-plugin/marketplace.json` for Claude Code.
  - `.agents/plugins/marketplace.json` for Codex.

Keep a skill and the agents that preload it in the same plugin so agent `skills:` references resolve without a cross-plugin dependency. Both runtimes auto-discover `skills/` and `agents/` inside each plugin, so neither manifest needs to enumerate them. Claude Code ignores unknown files (such as `skills/<name>/agents/openai.yaml`) and unknown frontmatter keys, so Codex-only metadata coexists in the shared files without breaking Claude.

There are no MCP servers or hooks in this repository right now.

## Plugin Taxonomy and Composition

- `universal` is the platform-neutral core: its skills define procedure and contract and never embed platform rules.
- Platform plugins (`apple-platform` today; future ones such as `android-platform`) ship companion skills that layer platform specifics on a universal skill. Canonical pairs: `simplifying-code` ↔ `simplifying-apple-platform-code`, `writing-technical-prose` ↔ `writing-apple-platform-documentation`.
- Composition direction is upward-only. A universal skill refers to companions only by what they cover ("compose with a platform companion when one is available; its rules win for that platform") and never names a platform plugin's content. A companion skill names the universal skill it extends. Downward name references from universal to platform content are forbidden.
- Agents follow the same rule: `skills:` frontmatter references only same-plugin skills; other plugins' agents are referred to by concern ("a reviewer focused on structural design fit, when available"), never by name. A plugin must be fully useful installed alone.
- Adding a platform plugin: create `plugins/<platform>/{.claude-plugin,.codex-plugin}/plugin.json`, register it in both marketplace manifests, add companion skills before agents, and extend `scripts/validate.py`'s version-token vocabulary if the platform has its own (for example `Android 15`, `API 35`). No universal file should need editing to add a platform.

## Single-Source Rule

Skills and agents are stored once and serve both platforms. Do not fork content per platform.

- Write skill and agent bodies to be runtime-neutral. Where a behavior depends on the runtime (for example, task tools), describe the preferred path and a fallback rather than hard-coding one runtime.
- Keep platform-specific structure in the manifests, not in the content.
- When you change a skill, an agent, or a manifest, update both platforms' manifests in the same change so they stay consistent.

## Skill Maintenance

- Every skill keeps a `SKILL.md` with `name` and `description` frontmatter.
- The `SKILL.md` `name` must equal the skill's directory name; the Agent Skills spec requires it. On import, strip any version or platform suffix (for example `-ios26-ios27`): both runtimes derive the invocation name from the frontmatter `name` for plugin skills, falling back to the directory, so a mismatch leaves the command and the directory you navigate to under different names.
- Keep identity fields (`name`, the `# ` H1, and the leading clause of `description`) free of specific OS or SDK version numbers; leave version-gating detail in the body where it is accurate.
- Preserve source `REFERENCE.md`, `ATTRIBUTION.md`, and `references/` files with their skill directories.
- Keep `description` written for implicit skill selection: describe in natural language when to use the skill. This drives Claude Code's automatic invocation and Codex's implicit selection.
- Every skill also carries `skills/<name>/agents/openai.yaml` with Codex `interface` metadata: `display_name`, `short_description`, and a `default_prompt` (invoking the skill as `$<name>`). Claude Code ignores this file. Add MCP dependencies or `policy.allow_implicit_invocation: false` to it when a skill needs them.
- Canonical SKILL.md shape: frontmatter (`name` == directory, gerund, version-free identity) → H1 → scope/assumptions including when NOT to use → decision procedure/contract → workflow → `## Reference Map` with an imperative lead-in → checklist pointer. Exemplars: `writing-swift`, `modeling-swift-types-for-correctness`.
- Size budget: SKILL.md targets ≤ ~200 lines; exhaustive rules, tables, and examples live in `references/*.md`; every reference file must appear in the reference map (no orphans); split any reference beyond ~500 lines by topic.
- Attribution: imported or derived skills carry top-level `ATTRIBUTION.md`; source snapshots are top-level `REFERENCE.md`; load-on-demand content lives in `references/`. Manually authored skills may omit attribution.
- openai.yaml contract: `display_name` (Title Case of the gerund name), `short_description`, `default_prompt` beginning "Use $<skill-name> to …".

## Agent Maintenance

- Agents are Markdown files with frontmatter under `plugins/<plugin>/agents/`.
- Frontmatter is a superset: `name`, `description`, plus Claude Code fields (`tools`, `skills`, `model`, `color`). Codex ignores the fields it does not use.
- Frontmatter field order is `name, description, tools, skills, model, color`; `model: inherit` always, and a deviation requires a documented reason in the body. Reviewer agents use the read-only tool set `Bash, Glob, Grep, Read, TaskCreate, TaskList`.
- Description formula: what it checks + "Use PROACTIVELY after/when …" + what it does not cover, with the scope boundary in the first sentence so overlapping agents don't both auto-spawn.
- Bodies are runtime-neutral, use Markdown `##` headers only (no XML section tags), and follow standard sections: Scope with a concern-defer table, Constraints, Process with the layered scope-resolution steps, Classifications or Severity, Output Format, Reporting via TaskCreate/TaskList with a prioritized-list fallback, Final Report. Reporting instructions prefer task tools (`TaskCreate`/`TaskList`) when the runtime exposes them and fall back to a prioritized follow-up list otherwise.
- Each reviewer agent owns exactly one concern. Current concern map: structure (`code-reviewer`), correctness (`correctness-reviewer`), codified rules (`code-standards-auditor`), types (`type-driven-design-auditor`), simplification (`code-simplifier` universally, `information-entropy-reducer` for Swift judgment), prose (`technical-writing-auditor`). A new agent claims an empty concern or explicitly splits one.
- Codex does not automatically spawn custom agents from their descriptions. Spawn the Apple Platform reviewer agents only when the user explicitly asks for subagents, delegated review, or parallel agent work and the runtime exposes those roles. If the roles are not available, run the review directly with the relevant skills.

## Review Workflow

When the user asks to review a PR, branch, or diff:

1. Compare the current branch against the relevant base branch, usually `main`.
2. Use the `reviewing-code` skill for the review frame.
3. For Swift changes, consult the focused Apple Platform skills that match the code touched: `using-swift-concurrency` for concurrency, actors, protocols, logical races, and async tests; then symbol ordering, localization, API design, testing, and type modeling as needed.
4. Present concrete findings first, ordered by severity.
5. Include file paths, symbols, and reproduction or verification notes where possible.
6. Avoid style-only comments unless they hide correctness, maintainability, or platform-convention risk.

When agents are spawned, use the narrowest useful set, wait for their results before finalizing, then consolidate duplicate findings instead of forwarding separate reports wholesale:

- `code-reviewer`: structural design consistency and architecture fit.
- `code-standards-auditor`: codified Swift and Apple Platform standards.
- `type-driven-design-auditor`: opportunities to make invalid states unrepresentable.
- `information-entropy-reducer`: unnecessary complexity and cognitive load.
- `technical-writing-auditor`: README, ADR, Markdown, and Swift doc-comment voice.
- `code-simplifier`: behavior-preserving simplification and reuse opportunities.
- `correctness-reviewer`: concrete correctness, security, concurrency, and compatibility defects.

## Apple Platform Defaults

- Prefer Swift 6 strict-concurrency-safe patterns.
- Prefer structured concurrency over detached or unstructured tasks.
- Treat main-thread UI updates as required.
- Prefer `String(localized:)` and string catalogs for user-facing text.
- Prefer Swift Testing (`@Test`, `@Suite`, `#expect`, `#require`) for new tests unless the project is still XCTest-only.
- Push domain invariants into types when the safety benefit outweighs added complexity.
- Follow existing project architecture before introducing a new pattern.

## Growth Playbooks

- **Adding a skill**: create the directory + SKILL.md per the skill shape + `agents/openai.yaml`; decide universal vs platform (if any rule would be wrong on another platform, it belongs in a platform plugin); add the README table row; run `python3 scripts/validate.py`; load-test on both runtimes.
- **Adding an agent**: confirm the concern slot; same-plugin `skills:` only; update the Review Workflow list and README; validate.
- **Adding a platform plugin**: create `plugins/<platform>/{.claude-plugin,.codex-plugin}/plugin.json`, register it in both marketplace manifests, add companion skills before agents, and extend `scripts/validate.py`'s version-token vocabulary if the platform has its own.

## Validation

- Primary gate: `python3 scripts/validate.py` — the same script CI runs via `.github/workflows/validate.yml`. It checks manifest JSON validity and marketplace↔plugin.json consistency, skill `name` == directory, version-free identity fields, `agents/openai.yaml` presence with a `$<skill-name>` default prompt, SKILL.md relative links and reference-map completeness, agent `skills:` same-plugin resolution, and README table ↔ disk consistency.
- Validate JSON manifests with `python3 -m json.tool`: `.claude-plugin/marketplace.json`, `.agents/plugins/marketplace.json`, `plugins/apple-platform/.claude-plugin/plugin.json`, `plugins/apple-platform/.codex-plugin/plugin.json`, `plugins/universal/.claude-plugin/plugin.json`, and `plugins/universal/.codex-plugin/plugin.json`.
- Run `claude plugin validate plugins/apple-platform` and `claude plugin validate plugins/universal` for the Claude manifests; local-only, since the `claude` CLI is not guaranteed on CI runners.
- Load the marketplace in Codex against the local path to confirm the agents and skills register.
- Do not commit generated state such as `.claude/` worktrees, `.DS_Store`, or local logs.

### Versioning

Plugin `version` bumps when content changes materially: patch for fixes and consistency work, minor for new skills, agents, or references, major for removals or renames. The Claude marketplace entry and both plugin.json files move together; `validate.py` enforces the equality. Bump with `python3 scripts/bump.py <plugin> <patch|minor|major>`, which updates all three version fields atomically. `validate.py` fails when content under a plugin changes without a version bump, so releases cannot be forgotten.

# AGENTS.md

Repository guidance for Codex Plugins for Making Good Software.

## Repository Shape

- This repository is a Codex plugin marketplace.
- `.agents/plugins/marketplace.json` registers local plugins for Codex plugin discovery.
- `plugins/apple-platform/.codex-plugin/plugin.json` is the Codex plugin manifest.
- `plugins/apple-platform/skills/` contains the bundled Codex skills.
- `.codex/agents/*.toml` contains project-scoped Codex custom agents ported from the Claude plugin agents.
- Keep Codex custom agents outside `plugins/apple-platform/` unless Codex documents plugin-bundled custom agents later.
- There are no MCP servers or hooks in this port right now.

## Skill Maintenance

- Every skill must keep a `SKILL.md` with `name` and `description` frontmatter.
- Preserve source `REFERENCE.md` and `ATTRIBUTION.md` files with their skill directories.
- Remove Claude-only skill frontmatter if new skills are ported: `allowed-tools`, `disable-model-invocation`, `agent`, `context`, `model`, `effort`, `paths`, and hook fields.
- Add `skills/<name>/agents/openai.yaml` only when a skill needs Codex UI metadata, MCP dependencies, or `policy.allow_implicit_invocation: false`.
- Keep descriptions written for implicit Codex skill selection: describe when to use the skill in natural language.

## Sibling Repository Sync

- This Codex marketplace is paired with the Claude Code marketplace at `/Users/kyle/Developer/Projects/Kyle Hughes/Claude Plugins for Making Good Software/Repositories/Plugin Marketplace`.
- Treat the Claude repository as the Claude-native source and this repository as the Codex-native port. Keep skill substance aligned, but translate platform-specific structure instead of copying blindly.
- Common mappings: `.claude-plugin/` to `.codex-plugin/`, `.claude-plugin/marketplace.json` to `.agents/plugins/marketplace.json`, Claude plugin `agents/*.md` to project `.codex/agents/*.toml`, and `CLAUDE.md` guidance to `AGENTS.md`.
- When changing a skill, agent, manifest, or marketplace entry in either repo, check the sibling repo for the equivalent update before considering the work complete.
- Do not sync generated state such as `.claude/` worktrees, `.DS_Store`, local logs, or other machine artifacts.

## Review Workflow

When the user asks to review a PR, branch, or diff:

1. Compare the current branch against the relevant base branch, usually `main`.
2. Use the `reviewing-code` skill for the review frame.
3. For Swift changes, consult the focused Apple Platform skills that match the code touched: `using-swift-concurrency` for concurrency, actors, protocols, logical races, and async tests; then symbol ordering, localization, API design, testing, and type modeling as needed.
4. Present concrete findings first, ordered by severity.
5. Include file paths, symbols, and reproduction or verification notes where possible.
6. Avoid style-only comments unless they hide correctness, maintainability, or platform-convention risk.

Codex does not automatically spawn custom agents from their descriptions. Spawn the `.codex/agents` reviewers only when the user explicitly asks for subagents, delegated review, or parallel agent work. If spawned, use the narrowest useful set:

- `code-reviewer`: structural design consistency and architecture fit.
- `code-standards-auditor`: codified Swift and Apple Platform standards.
- `type-driven-design-auditor`: opportunities to make invalid states unrepresentable.
- `information-entropy-reducer`: unnecessary complexity and cognitive load.
- `technical-writing-auditor`: README, ADR, Markdown, and Swift doc-comment voice.

Wait for spawned agent results before finalizing, then consolidate duplicate findings instead of forwarding separate agent reports wholesale.

## Apple Platform Defaults

- Prefer Swift 6 strict-concurrency-safe patterns.
- Prefer structured concurrency over detached or unstructured tasks.
- Treat main-thread UI updates as required.
- Prefer `String(localized:)` and string catalogs for user-facing text.
- Prefer Swift Testing (`@Test`, `@Suite`, `#expect`, `#require`) for new tests unless the project is still XCTest-only.
- Push domain invariants into types when the safety benefit outweighs added complexity.
- Follow existing project architecture before introducing a new pattern.

## Validation

- Validate JSON manifests with `python3 -m json.tool`.
- Validate TOML with Python 3.11+ `tomllib` when available.
- After porting or renaming skills, run `rg --hidden -g '!.git' -n "Claude|CLAUDE|\\.claude|TaskCreate|TaskList" .` and remove stale Claude-specific behavior unless the text is intentionally historical.

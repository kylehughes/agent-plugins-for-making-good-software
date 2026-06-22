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

## Single-Source Rule

Skills and agents are stored once and serve both platforms. Do not fork content per platform.

- Write skill and agent bodies to be runtime-neutral. Where a behavior depends on the runtime (for example, task tools), describe the preferred path and a fallback rather than hard-coding one runtime.
- Keep platform-specific structure in the manifests, not in the content.
- When you change a skill, an agent, or a manifest, update both platforms' manifests in the same change so they stay consistent.

## Skill Maintenance

- Every skill keeps a `SKILL.md` with `name` and `description` frontmatter.
- Preserve source `REFERENCE.md`, `ATTRIBUTION.md`, and `references/` files with their skill directories.
- Keep `description` written for implicit skill selection: describe in natural language when to use the skill. This drives Claude Code's automatic invocation and Codex's implicit selection.
- Add `skills/<name>/agents/openai.yaml` only when a skill needs Codex UI metadata, MCP dependencies, or `policy.allow_implicit_invocation: false`.

## Agent Maintenance

- Agents are Markdown files with frontmatter under `plugins/apple-platform/agents/`.
- Frontmatter is a superset: `name`, `description`, plus Claude Code fields (`tools`, `skills`, `model`, `color`). Codex ignores the fields it does not use.
- Bodies are runtime-neutral. Reporting instructions prefer task tools (`TaskCreate`/`TaskList`) when the runtime exposes them and fall back to a prioritized follow-up list otherwise.
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

## Apple Platform Defaults

- Prefer Swift 6 strict-concurrency-safe patterns.
- Prefer structured concurrency over detached or unstructured tasks.
- Treat main-thread UI updates as required.
- Prefer `String(localized:)` and string catalogs for user-facing text.
- Prefer Swift Testing (`@Test`, `@Suite`, `#expect`, `#require`) for new tests unless the project is still XCTest-only.
- Push domain invariants into types when the safety benefit outweighs added complexity.
- Follow existing project architecture before introducing a new pattern.

## Validation

- Validate JSON manifests with `python3 -m json.tool`: `.claude-plugin/marketplace.json`, `.agents/plugins/marketplace.json`, `plugins/apple-platform/.claude-plugin/plugin.json`, and `plugins/apple-platform/.codex-plugin/plugin.json`.
- Run `claude plugin validate plugins/apple-platform` for the Claude manifest.
- Load the marketplace in Codex against the local path to confirm the agents and skills register.
- Do not commit generated state such as `.claude/` worktrees, `.DS_Store`, or local logs.

# Agent Plugins for Making Good Software

[![Claude Code Plugin](https://img.shields.io/badge/Claude_Code_Plugin-555?logo=claude)](https://code.claude.com/docs/en/plugins)
[![Codex Plugin][codex_plugin_badge]](https://learn.chatgpt.com/docs/plugins)
[![CI](https://github.com/kylehughes/agent-plugins-for-making-good-software/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/kylehughes/agent-plugins-for-making-good-software/actions/workflows/ci.yml)

Plugins for making good software with Claude Code and Codex.

## About

Install `universal` for platform-agnostic workflows. Add `apple-platform`
for Apple-platform development. Each plugin also works on its own. They share
one set of instructions across both runtimes and ship 29 skills and 8 reviewer
definitions in total.

Skills provide task instructions and supporting references. Reviewer agents
check specific concerns, such as correctness or structural design. The plugins
do not include MCP servers or hooks. Some workflows use your project's tools
or delegate work when the host supports it.

## Installation

Use a version of Claude Code or Codex with plugin support. Run the following
commands in your terminal, then start a new session in the project you want to
work on. Install either plugin or both.

### Claude Code

```sh
claude plugin marketplace add kylehughes/agent-plugins-for-making-good-software
claude plugin install universal@making-good-software
claude plugin install apple-platform@making-good-software
```

You can also manage plugins with `/plugin` inside a Claude Code session. See
[Claude Code's installation guide](https://code.claude.com/docs/en/discover-plugins)
for installation scopes and updates.

### Codex

```sh
codex plugin marketplace add kylehughes/agent-plugins-for-making-good-software
codex plugin add universal@making-good-software
codex plugin add apple-platform@making-good-software
```

Use `/plugins` in Codex CLI to inspect installed plugins. See
[Codex's plugin guide](https://learn.chatgpt.com/docs/plugins) for where plugins
are supported and how sessions load them.

### Repository access

If access to the repository is restricted, authenticate with a GitHub account
that has access. To connect over SSH, use this address instead of the repository
slug:

```sh
codex plugin marketplace add git@github.com:kylehughes/agent-plugins-for-making-good-software.git
```

The same SSH source works with `claude plugin marketplace add`.

## Usage

My usual workflow is:

1. Ask for implementation.
2. Verify the result manually, with automated checks, or both.
3. Ask for simplification.
4. Ask for hardening.

Simplification and hardening bring in the relevant skills and project
preferences, including code review.

`delivering-changes` codifies that sequence into one workflow: ask it to implement
a change and take it to a PR-ready handoff. It runs the required checks and pauses
for manual verification where your project instructions require it.

| Step | Claude Code | Codex |
| :--- | :--- | :--- |
| Simplify | `/universal:simplifying-code` | `$simplifying-code` |
| Harden | `/universal:hardening-changes` | `$hardening-changes` |
| Run the whole workflow | `/universal:delivering-changes` | `$delivering-changes` |

For Swift and Apple-platform code, use the
[`simplifying-apple-platform-code`](plugins/apple-platform/skills/simplifying-apple-platform-code/SKILL.md)
companion for the simplification step. All skills also support automatic
selection when relevant and direct invocation.

## Apple Platform

[![Apple Platform release](https://img.shields.io/github/v/release/kylehughes/agent-plugins-for-making-good-software?filter=apple-platform%2Fv%2A&display_name=tag)](https://github.com/kylehughes/agent-plugins-for-making-good-software/releases?q=tag%3Aapple-platform%2Fv+draft%3Afalse+prerelease%3Afalse)

The `apple-platform` plugin contains 19 skills and 4 reviewer definitions.

### Skills

| Skill | Purpose |
| :---- | :------ |
| `analyzing-app-store-business-data` | [Analyze App Store revenue, subscriptions, downloads, reviews, and growth.](plugins/apple-platform/skills/analyzing-app-store-business-data/SKILL.md) |
| `auditing-ios-release-size` | [Audit release download and install size with App Thinning evidence.](plugins/apple-platform/skills/auditing-ios-release-size/SKILL.md) |
| `configuring-ios-content` | [Configure UIKit cells with `UIContentConfiguration`, `UIHostingConfiguration`, and `UIContentView`.](plugins/apple-platform/skills/configuring-ios-content/SKILL.md) |
| `designing-swift-apis` | [Design Swift names, argument labels, and doc comments using Apple's API guidelines.](plugins/apple-platform/skills/designing-swift-apis/SKILL.md) |
| `implementing-app-intents` | [Implement App Intents for Siri, Apple Intelligence, entities, Spotlight, and value representations.](plugins/apple-platform/skills/implementing-app-intents/SKILL.md) |
| `instrumenting-accessibility-identifiers` | [Add type-safe accessibility identifiers and stable UI-test selectors.](plugins/apple-platform/skills/instrumenting-accessibility-identifiers/SKILL.md) |
| `localizing-strings` | [Localize user-facing text with `String(localized:)` and string catalogs.](plugins/apple-platform/skills/localizing-strings/SKILL.md) |
| `modeling-swift-types-for-correctness` | [Model Swift invariants, validated decoding, ownership, and generic relationships.](plugins/apple-platform/skills/modeling-swift-types-for-correctness/SKILL.md) |
| `ordering-symbols` | [Order members within Swift types by declaration kind, access level, and name.](plugins/apple-platform/skills/ordering-symbols/SKILL.md) |
| `organizing-swift-types` | [Organize Swift types, extensions, access control, and file layout.](plugins/apple-platform/skills/organizing-swift-types/SKILL.md) |
| `presenting-ios-modals` | [Present modal sheets with appropriate chrome, button roles, detents, and dismissal behavior.](plugins/apple-platform/skills/presenting-ios-modals/SKILL.md) |
| `recording-ios-simulator-videos` | [Record, compress, and validate iOS Simulator videos with `simctl`.](plugins/apple-platform/skills/recording-ios-simulator-videos/SKILL.md) |
| `simplifying-apple-platform-code` | [Simplify Swift and Apple-platform code with SDK, lifecycle, availability, and concurrency rules.](plugins/apple-platform/skills/simplifying-apple-platform-code/SKILL.md) |
| `structuring-swift-packages` | [Define module boundaries, dependency direction, exported interfaces, and composition roots.](plugins/apple-platform/skills/structuring-swift-packages/SKILL.md) |
| `testing-async-swift-code` | [Make async tests deterministic with explicit synchronization and controlled time.](plugins/apple-platform/skills/testing-async-swift-code/SKILL.md) |
| `testing-swift-code` | [Write unit tests with Swift Testing (`@Test`, `@Suite`, `#expect`).](plugins/apple-platform/skills/testing-swift-code/SKILL.md) |
| `using-swift-concurrency` | [Design and debug Swift concurrency, isolation, cancellation, and async sequences.](plugins/apple-platform/skills/using-swift-concurrency/SKILL.md) |
| `writing-apple-platform-documentation` | [Write DocC, Swift API comments, and Apple-platform developer documentation.](plugins/apple-platform/skills/writing-apple-platform-documentation/SKILL.md) |
| `writing-swift` | [Write and maintain Swift 6 code and packages.](plugins/apple-platform/skills/writing-swift/SKILL.md) |

### Agents

| Agent | Purpose |
| :---- | :------ |
| `async-testing-auditor` | [Check that synchronization in changed Swift async tests is supported by evidence.](plugins/apple-platform/agents/async-testing-auditor.md) |
| `code-standards-auditor` | [Audit Swift changes against the bundled coding standards.](plugins/apple-platform/agents/code-standards-auditor.md) |
| `information-entropy-reducer` | [Flag unnecessary complexity and cognitive load.](plugins/apple-platform/agents/information-entropy-reducer.md) |
| `type-driven-design-auditor` | [Audit Swift representations and opportunities to prevent invalid states.](plugins/apple-platform/agents/type-driven-design-auditor.md) |

## Universal

[![Universal release](https://img.shields.io/github/v/release/kylehughes/agent-plugins-for-making-good-software?filter=universal%2Fv%2A&display_name=tag)](https://github.com/kylehughes/agent-plugins-for-making-good-software/releases?q=tag%3Auniversal%2Fv+draft%3Afalse+prerelease%3Afalse)

The `universal` plugin contains 10 skills and 4 reviewer definitions.

### Skills

| Skill | Purpose |
| :---- | :------ |
| `brainstorming-design-specs` | [Turn ambiguous work into an implementation-ready design through research and dialogue.](plugins/universal/skills/brainstorming-design-specs/SKILL.md) |
| `compiling-agent-goals` | [Turn specs and plans into bounded agent goals with acceptance evidence and stopping conditions.](plugins/universal/skills/compiling-agent-goals/SKILL.md) |
| `delivering-changes` | [Carry a requested change from its initial brief to a verified, PR-ready handoff.](plugins/universal/skills/delivering-changes/SKILL.md) |
| `designing-documents` | [Organize documents for understanding, decisions, action, and lookup.](plugins/universal/skills/designing-documents/SKILL.md) |
| `hardening-changes` | [Prepare owned changes for a PR by reviewing and fixing issues within the agreed scope.](plugins/universal/skills/hardening-changes/SKILL.md) |
| `reviewing-code` | [Review correctness, security, concurrency, and compatibility risks with line-specific findings.](plugins/universal/skills/reviewing-code/SKILL.md) |
| `simplifying-code` | [Simplify and reuse existing code while preserving behavior.](plugins/universal/skills/simplifying-code/SKILL.md) |
| `verifying-invariants` | [Assess invariant boundaries and evidence, with optional manifest validation and language-specific companions.](plugins/universal/skills/verifying-invariants/SKILL.md) |
| `writing-escalation-briefs` | [Prepare a standalone expert handoff with evidence, attempts, and hypotheses.](plugins/universal/skills/writing-escalation-briefs/SKILL.md) |
| `writing-technical-prose` | [Write direct developer-facing prose for READMEs, ADRs, docs, and comments.](plugins/universal/skills/writing-technical-prose/SKILL.md) |

### Agents

| Agent | Purpose |
| :---- | :------ |
| `code-reviewer` | [Review structural design consistency and architecture fit.](plugins/universal/agents/code-reviewer.md) |
| `code-simplifier` | [Find behavior-preserving simplification and reuse opportunities in any language.](plugins/universal/agents/code-simplifier.md) |
| `correctness-reviewer` | [Find concrete correctness, security, concurrency, and compatibility defects.](plugins/universal/agents/correctness-reviewer.md) |
| `technical-writing-auditor` | [Audit developer-facing docs and comments for voice, structure, and generic phrasing.](plugins/universal/agents/technical-writing-auditor.md) |

## Documentation and maintenance

Start with the [documentation index](docs/README.md) for maintained guides,
evaluation procedures, and historical records. Each skill keeps its references
alongside its instructions and loads them only when relevant to the task.

Each reviewer covers a separate concern. Claude Code registers these Markdown
definitions as agents. Codex uses a separate agent configuration format; when a
named reviewer is unavailable, pass its instructions to an available native
agent. If the host cannot delegate, follow the workflow's instructions for
reviewing directly. See [agent model selection](docs/agent-model-selection.md)
for how shared reviewer instructions work with runtime settings.

For maintenance, follow [repository guidance](AGENTS.md). From the repository root,
run the tooling tests, validator, and context-cost report:

```sh
python3 -m unittest discover -s scripts -p 'test_*.py'
python3 scripts/validate.py
python3 scripts/skill_catalog.py --base HEAD
```

These checks validate tooling, metadata, invocation policy, navigation, and catalog consistency.
Behavioral evaluations are separate; see the
[evaluation guide](docs/invariant-verification.md#behavioral-acceptance) for setup,
execution, and evidence requirements.

Plugin versions and release notes are published in
[GitHub releases](https://github.com/kylehughes/agent-plugins-for-making-good-software/releases).
Update installed plugins through your host's plugin manager, then start a new
session. This repository's marketplace is separate from either vendor's public
plugin directory.

## Author

[Kyle Hughes](https://kylehugh.es)

[![Bluesky][bluesky_image]][bluesky_url]\
[![LinkedIn][linkedin_image]][linkedin_url]\
[![Mastodon][mastodon_image]][mastodon_url]

[bluesky_image]: https://img.shields.io/badge/Bluesky-0285FF?logo=bluesky&logoColor=fff
[bluesky_url]: https://bsky.app/profile/kylehugh.es
[linkedin_image]: https://img.shields.io/badge/LinkedIn-0A66C2?logo=linkedin&logoColor=fff
[linkedin_url]: https://www.linkedin.com/in/kyle-hughes
[mastodon_image]: https://img.shields.io/mastodon/follow/109356914477272810?domain=https%3A%2F%2Fmister.computer&style=social
[mastodon_url]: https://mister.computer/@kyle

## Attribution

Imported and derived skills retain their source notices in `ATTRIBUTION.md` and,
where present, `REFERENCE.md`. The [attribution index](docs/README.md#attribution)
links those notices and records missing information about the supplied sources.

<!-- Official OpenAI artwork: https://cdn.openai.com/brand/OpenAI-Logos-2025.zip -->
[codex_plugin_badge]: https://img.shields.io/badge/Codex_Plugin-555?logo=data%3Aimage%2Fsvg%2Bxml%3Bbase64%2CPHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjExOC41NTcgMTIwLjc1OCA0ODQuMTM5IDQ3OS44MTgiPjxwYXRoIGZpbGw9IndoaXRlIiBkPSJNMzA0LjI0NiAyOTUuNDExVjI0OS44MjhDMzA0LjI0NiAyNDUuOTg5IDMwNS42ODcgMjQzLjEwOSAzMDkuMDQ0IDI0MS4xOTFMNDAwLjY5MiAxODguNDEyQzQxMy4xNjcgMTgxLjIxNSA0MjguMDQyIDE3Ny44NTggNDQzLjM5NCAxNzcuODU4QzUwMC45NzEgMTc3Ljg1OCA1MzcuNDQgMjIyLjQ4MiA1MzcuNDQgMjY5Ljk4MkM1MzcuNDQgMjczLjM0IDUzNy40NCAyNzcuMTc5IDUzNi45NTkgMjgxLjAxOEw0NDEuOTU0IDIyNS4zNThDNDM2LjE5NyAyMjIgNDMwLjQzNyAyMjIgNDI0LjY4IDIyNS4zNThMMzA0LjI0NiAyOTUuNDExWk01MTguMjQ1IDQ3Mi45NDVWMzY0LjAyNEM1MTguMjQ1IDM1Ny4zMDQgNTE1LjM2NCAzNTIuNTA3IDUwOS42MDggMzQ5LjE0OUwzODkuMTc0IDI3OS4wOTZMNDI4LjUxOSAyNTYuNTQzQzQzMS44NzcgMjU0LjYyNiA0MzQuNzU3IDI1NC42MjYgNDM4LjExNSAyNTYuNTQzTDUyOS43NjIgMzA5LjMyM0M1NTYuMTU0IDMyNC42NzkgNTczLjkwNSAzNTcuMzA0IDU3My45MDUgMzg4Ljk3MUM1NzMuOTA1IDQyNS40MzYgNTUyLjMxNSA0NTkuMDI0IDUxOC4yNDUgNDcyLjk0MVY0NzIuOTQ1Wk0yNzUuOTM3IDM3Ni45ODJMMjM2LjU5MiAzNTMuOTUyQzIzMy4yMzUgMzUyLjAzNCAyMzEuNzk0IDM0OS4xNTQgMjMxLjc5NCAzNDUuMzE1VjIzOS43NTZDMjMxLjc5NCAxODguNDE2IDI3MS4xMzkgMTQ5LjU0OCAzMjQuNCAxNDkuNTQ4QzM0NC41NTUgMTQ5LjU0OCAzNjMuMjY0IDE1Ni4yNjggMzc5LjEwMiAxNjguMjYyTDI4NC41NzggMjIyLjk2NEMyNzguODIyIDIyNi4zMjEgMjc1Ljk0MiAyMzEuMTE5IDI3NS45NDIgMjM3LjgzOFYzNzYuOTg2TDI3NS45MzcgMzc2Ljk4MlpNMzYwLjYyNiA0MjUuOTIyTDMwNC4yNDYgMzk0LjI1NVYzMjcuMDgzTDM2MC42MjYgMjk1LjQxNkw0MTcuMDAyIDMyNy4wODNWMzk0LjI1NUwzNjAuNjI2IDQyNS45MjJaTTM5Ni44NTIgNTcxLjc4OUMzNzYuNjk4IDU3MS43ODkgMzU3Ljk4OSA1NjUuMDcgMzQyLjE1MSA1NTMuMDc1TDQzNi42NzQgNDk4LjM3NEM0NDIuNDMxIDQ5NS4wMTcgNDQ1LjMxMSA0OTAuMjE5IDQ0NS4zMTEgNDgzLjQ5OVYzNDQuMzUyTDQ4NS4xMzggMzY3LjM4MkM0ODguNDk1IDM2OS4yOTkgNDg5LjkzNiAzNzIuMTc5IDQ4OS45MzYgMzc2LjAxOFY0ODEuNTc3QzQ4OS45MzYgNTMyLjkxNyA0NTAuMTA5IDU3MS43ODUgMzk2Ljg1MiA1NzEuNzg1VjU3MS43ODlaTTI4My4xMzQgNDY0Ljc5TDE5MS40ODYgNDEyLjAxQzE2NS4wOTQgMzk2LjY1NCAxNDcuMzQzIDM2NC4wMjkgMTQ3LjM0MyAzMzIuMzYyQzE0Ny4zNDMgMjk1LjQxNiAxNjkuNDE1IDI2Mi4zMDkgMjAzLjQ4IDI0OC4zOTNWMzU3Ljc5MUMyMDMuNDggMzY0LjUxIDIwNi4zNjEgMzY5LjMwOCAyMTIuMTE3IDM3Mi42NjVMMzMyLjA3NCA0NDIuMjM3TDI5Mi43MjkgNDY0Ljc5QzI4OS4zNzIgNDY2LjcwNyAyODYuNDkxIDQ2Ni43MDcgMjgzLjEzNCA0NjQuNzlaTTI3Ny44NTkgNTQzLjQ4QzIyMy42MzkgNTQzLjQ4IDE4My44MTMgNTAyLjY5NSAxODMuODEzIDQ1Mi4zMTRDMTgzLjgxMyA0NDguNDc1IDE4NC4yOTQgNDQ0LjYzNiAxODQuNzcxIDQ0MC43OTdMMjc5LjI5NSA0OTUuNDk4QzI4NS4wNTEgNDk4Ljg1NiAyOTAuODEyIDQ5OC44NTYgMjk2LjU2OCA0OTUuNDk4TDQxNy4wMDIgNDI1LjkyN1Y0NzEuNTA5QzQxNy4wMDIgNDc1LjM0OSA0MTUuNTYyIDQ3OC4yMjkgNDEyLjIwNCA0ODAuMTQ2TDMyMC41NTcgNTMyLjkyNkMzMDguMDgxIDU0MC4xMjIgMjkzLjIwNiA1NDMuNDggMjc3Ljg1NCA1NDMuNDhIMjc3Ljg1OVpNMzk2Ljg1MiA2MDAuNTc2QzQ1NC45MTEgNjAwLjU3NiA1MDMuMzcgNTU5LjMxMyA1MTQuNDEgNTA0LjYxMkM1NjguMTQ5IDQ5MC42OTYgNjAyLjY5NiA0NDAuMzE1IDYwMi42OTYgMzg4Ljk3NkM2MDIuNjk2IDM1NS4zODcgNTg4LjMwMyAzMjIuNzYyIDU2Mi4zOTIgMjk5LjI1QzU2NC43OTEgMjg5LjE3MyA1NjYuMjMxIDI3OS4wOTYgNTY2LjIzMSAyNjkuMDI0QzU2Ni4yMzEgMjAwLjQxMSA1MTAuNTcxIDE0OS4wNjcgNDQ2LjI3NCAxNDkuMDY3QzQzMy4zMjIgMTQ5LjA2NyA0MjAuODQ2IDE1MC45ODQgNDA4LjM3IDE1NS4zMDVDMzg2Ljc3NSAxMzQuMTkyIDM1Ny4wMjYgMTIwLjc1OCAzMjQuNCAxMjAuNzU4QzI2Ni4zNDIgMTIwLjc1OCAyMTcuODgzIDE2Mi4wMiAyMDYuODQzIDIxNi43MjFDMTUzLjEwNCAyMzAuNjM3IDExOC41NTcgMjgxLjAxOCAxMTguNTU3IDMzMi4zNTdDMTE4LjU1NyAzNjUuOTQ2IDEzMi45NSAzOTguNTcxIDE1OC44NjEgNDIyLjA4M0MxNTYuNDYyIDQzMi4xNiAxNTUuMDIyIDQ0Mi4yMzcgMTU1LjAyMiA0NTIuMzA5QzE1NS4wMjIgNTIwLjkyMiAyMTAuNjgyIDU3Mi4yNjYgMjc0Ljk3OCA1NzIuMjY2QzI4Ny45MzEgNTcyLjI2NiAzMDAuNDA3IDU3MC4zNDkgMzEyLjg4MyA1NjYuMDI4QzMzNC40NzMgNTg3LjE0MSAzNjQuMjIyIDYwMC41NzYgMzk2Ljg1MiA2MDAuNTc2WiIvPjwvc3ZnPg%3D%3D

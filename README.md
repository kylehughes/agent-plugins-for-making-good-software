# Agent Plugins for Making Good Software

Plugins for making good software with Claude Code and Codex.

## About

Install `universal` for platform-agnostic workflows. Add `apple-platform`
for Apple-platform development. Each plugin also works on its own. They share
one set of instructions across both runtimes and ship 28 skills and 8 reviewer
definitions in total.

Skills provide task instructions and supporting references. Reviewer agents
inspect specific concerns, such as correctness or structural design. These
plugins do not bundle MCP servers or hooks; individual workflows may use your
project's tools and the host's delegation capabilities.

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
[Codex's plugin guide](https://learn.chatgpt.com/docs/plugins) for supported
surfaces and session-loading behavior.

### Repository access

If the repository is access-restricted, authenticate GitHub with an account that
has access. For SSH-based access, use this source instead of the repository slug:

```sh
codex plugin marketplace add git@github.com:kylehughes/agent-plugins-for-making-good-software.git
```

The same SSH source works with `claude plugin marketplace add`.

## Usage

Describe the task and its scope in your project session. Select a skill
explicitly when you want a particular workflow:

| Task | Claude Code | Codex |
| :--- | :--- | :--- |
| Take a request through to a PR-ready handoff | `/universal:delivering-changes` | `$delivering-changes` |
| Review a diff without editing it | `/universal:reviewing-code` | `$reviewing-code` |
| Simplify owned code while preserving behavior | `/universal:simplifying-code` | `$simplifying-code` |
| Prepare owned changes through review and fixes | `/universal:hardening-changes` | `$hardening-changes` |
| Simplify Swift or Apple-platform code | `/apple-platform:simplifying-apple-platform-code` | `$simplifying-apple-platform-code` |

For a complete change: "Use $delivering-changes to implement this ticket and take
it to a PR-ready handoff." It handles implementation, simplification, hardening,
and the required pre-PR checks without a separate prompt for each stage. Put
project-specific manual verification requirements in your project instructions;
the workflow pauses at those checkpoints and resumes after you report the result.

For a review: "Use $reviewing-code to review my changes against main. Focus on
correctness and compatibility; do not edit files." Use the matching Claude Code
command for either task in that host.

The Apple simplification companion loads its universal foundation when available,
so invoking that companion is enough to apply both guides. Project-specific
hardening companions are discovered through available descriptions and project
instructions. They contribute requirements to the same scoped pass, including
checks the project requires during hardening.

Reviewer definitions cover separate concerns. Their availability and invocation
depend on the host; when a workflow cannot delegate, follow its documented
direct-review fallback. See [agent model selection](docs/agent-model-selection.md)
for shared reviewer instructions and runtime settings.

## Apple Platform

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
| `async-testing-auditor` | [Audit changed Swift async tests for proven synchronization edges.](plugins/apple-platform/agents/async-testing-auditor.md) |
| `code-standards-auditor` | [Audit Swift changes against the bundled coding standards.](plugins/apple-platform/agents/code-standards-auditor.md) |
| `information-entropy-reducer` | [Flag unnecessary complexity and cognitive load.](plugins/apple-platform/agents/information-entropy-reducer.md) |
| `type-driven-design-auditor` | [Audit Swift representations and opportunities to prevent invalid states.](plugins/apple-platform/agents/type-driven-design-auditor.md) |

## Universal

The `universal` plugin contains 9 skills and 4 reviewer definitions.

### Skills

| Skill | Purpose |
| :---- | :------ |
| `brainstorming-design-specs` | [Turn ambiguous work into an implementation-ready design through research and dialogue.](plugins/universal/skills/brainstorming-design-specs/SKILL.md) |
| `compiling-agent-goals` | [Turn specs and plans into bounded agent goals with acceptance evidence and stopping conditions.](plugins/universal/skills/compiling-agent-goals/SKILL.md) |
| `delivering-changes` | [Carry a requested change from its initial brief to a verified, PR-ready handoff.](plugins/universal/skills/delivering-changes/SKILL.md) |
| `hardening-changes` | [Prepare owned changes for a PR through a scoped review-and-fix loop.](plugins/universal/skills/hardening-changes/SKILL.md) |
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
evaluation procedures, and historical records. Skill-specific references live
beside their entry points and are loaded only when their concern applies.

For maintenance, follow [repository guidance](AGENTS.md). From the repository root,
run the tooling tests, validator, and context-cost report:

```sh
python3 -m unittest discover -s scripts -p 'test_*.py'
python3 scripts/validate.py
python3 scripts/skill_catalog.py --base HEAD
```

These checks validate tooling, metadata, navigation, and catalog consistency.
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
links those notices and records gaps in supplied-source provenance.

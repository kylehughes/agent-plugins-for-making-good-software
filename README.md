# Agent Plugins for Making Good Software

A plugin marketplace for making good software, first-class on both Claude Code and Codex.

It currently ships one plugin, `apple-platform`, whose skills and agents are tailored to Apple-platform development. Content is stored once and shared; each runtime reads its own manifest. The marketplace is named `making-good-software`, so the plugin installs as `apple-platform@making-good-software` on both.

## Install

This is a private repository. Both runtimes need a GitHub account or SSH key with access.

### Claude Code

```shell
/plugin marketplace add kylehughes/agent-plugins-for-making-good-software
/plugin install apple-platform@making-good-software
```

### Codex

```shell
codex plugin marketplace add kylehughes/agent-plugins-for-making-good-software
```

If Codex cannot resolve the private repository by slug, use the SSH URL:

```shell
codex plugin marketplace add git@github.com:kylehughes/agent-plugins-for-making-good-software.git
```

After registration, install or enable `apple-platform` from Codex's plugin UI.

## Marketplace

Each runtime registers plugins from its own manifest:

| Runtime | Marketplace manifest | Plugin manifest |
| :------ | :------------------- | :-------------- |
| Claude Code | `.claude-plugin/marketplace.json` | `plugins/apple-platform/.claude-plugin/plugin.json` |
| Codex | `.agents/plugins/marketplace.json` | `plugins/apple-platform/.codex-plugin/plugin.json` |

## apple-platform

Skills and agent definitions for Apple-platform codebases. The shared content lives under `plugins/apple-platform/skills` and `plugins/apple-platform/agents`; both runtimes auto-discover it.

### Skills

| Skill | Purpose |
| :---- | :------ |
| `configuring-ios-content` | Patterns for `UIContentConfiguration`, `UIHostingConfiguration`, and `UIContentView` in UIKit cells. |
| `designing-swift-apis` | Apple's Swift API design guidelines for naming, argument labels, and doc comments. |
| `implementing-app-intents` | Guidance for App Intents on iOS 26 and 27: Siri, Apple Intelligence, entities, and Spotlight. |
| `instrumenting-accessibility-identifiers` | A type-safe `accessibilityIdentifier` pattern across SwiftUI, UIKit, XCUITest, and screenshot automation. |
| `localizing-strings` | Patterns for `String(localized:)` and string catalogs. |
| `modeling-swift-types-for-correctness` | Patterns for modeling Swift types that make invalid states unrepresentable. |
| `ordering-symbols` | The canonical member ordering for Swift types. |
| `organizing-swift-types` | Conventions for Swift types, extensions, access control, and file layout. |
| `reviewing-code` | A review frame for design consistency, correctness, and concurrency safety. |
| `simplify-code` | A cleanup pass for reuse, simplicity, quality, and efficiency. |
| `testing-swift-code` | Conventions for the Swift Testing framework (`@Test`, `@Suite`, `#expect`). |
| `using-swift-concurrency` | Swift Concurrency design, diagnostics, actor isolation, logical races, and async tests. |
| `writing-swift` | Swift 6 standards for production code and packages. |
| `writing-technical-writing` | Conventions for direct, pragmatic technical prose. |

Invoke a skill with its plugin-qualified name: `$apple-platform:writing-swift` in Codex, or `apple-platform:writing-swift` in Claude Code. Both runtimes can also select skills implicitly from their descriptions.

### Agents

| Agent | Purpose |
| :---- | :------ |
| `code-reviewer` | Reviews structural design consistency and architecture fit. |
| `code-standards-auditor` | Audits Swift changes against the bundled coding standards. |
| `information-entropy-reducer` | Flags unnecessary complexity and cognitive load. |
| `technical-writing-auditor` | Audits Markdown and doc comments for voice and structure. |
| `type-driven-design-auditor` | Finds compile-time correctness opportunities in Swift types. |

Claude Code can invoke these agents proactively. Codex does not spawn plugin agents from their descriptions, so ask for subagents, delegated review, or parallel agent work explicitly; otherwise the review runs directly against the skills.

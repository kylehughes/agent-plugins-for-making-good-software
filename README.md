# Agent Plugins for Making Good Software

A plugin marketplace for the Apple Platform plugin: Swift, UIKit, App Intents, localization, testing, review, and technical writing.

The marketplace is first-class on both Claude Code and Codex. Skills and agent definitions are stored once and shared; each runtime reads its own manifest. The marketplace is named `making-good-software`, so the plugin installs as `apple-platform@making-good-software` on both.

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

Each runtime registers the same plugin from its own manifest:

| Runtime | Marketplace manifest | Plugin manifest |
| :------ | :------------------- | :-------------- |
| Claude Code | `.claude-plugin/marketplace.json` | `plugins/apple-platform/.claude-plugin/plugin.json` |
| Codex | `.agents/plugins/marketplace.json` | `plugins/apple-platform/.codex-plugin/plugin.json` |

## apple-platform

Skills and agent definitions for Apple-platform codebases. The shared content lives under `plugins/apple-platform/skills` and `plugins/apple-platform/agents`; both runtimes auto-discover it.

### Skills

| Skill | Purpose |
| :---- | :------ |
| `configuring-ios-content` | Implements `UIContentConfiguration`, `UIHostingConfiguration`, and `UIContentView`. |
| `designing-swift-apis` | Applies Apple's Swift API design guidelines. |
| `implementing-app-intents` | Implements App Intents for iOS 26 and iOS 27, including Siri, Apple Intelligence, entities, and Spotlight. |
| `instrumenting-accessibility-identifiers` | Builds a compiler-checked `accessibilityIdentifier` contract across SwiftUI, UIKit, XCUITest, and screenshot automation. |
| `localizing-strings` | Localizes user-facing strings with `String(localized:)` and string catalogs. |
| `modeling-swift-types-for-correctness` | Designs Swift types that make invalid states unrepresentable. |
| `ordering-symbols` | Defines canonical member ordering for Swift types. |
| `organizing-swift-types` | Defines Swift type, extension, access control, and file layout conventions. |
| `reviewing-code` | Reviews Apple Platform changes for design consistency and correctness. |
| `simplify-code` | Reviews changed code for reuse, simplicity, quality, and efficiency, then fixes issues directly. |
| `testing-swift-code` | Writes tests with the Swift Testing framework. |
| `using-swift-concurrency` | Covers Swift Concurrency design, diagnostics, actor isolation, logical races, and async tests. |
| `writing-swift` | Writes, edits, debugs, reviews, migrates, and tests production Swift code and packages. |
| `writing-technical-writing` | Writes direct, pragmatic technical prose. |

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

# Codex Plugins for Making Good Software

Codex plugin marketplace for the Apple Platform plugin: Swift, UIKit, App Intents, localization, testing, review, and technical writing.

This repository is the Codex port of the Claude Code marketplace. Plugin-owned files live under `plugins/apple-platform` instead of project-scoped Codex configuration, so installed copies behave like marketplace assets.

## Install

Register the private marketplace:

```shell
codex plugin marketplace add kylehughes/codex-plugins-for-making-good-software
```

If Codex cannot resolve the private repository by slug, use the SSH URL:

```shell
codex plugin marketplace add git@github.com:kylehughes/codex-plugins-for-making-good-software.git
```

Codex needs a GitHub account or SSH key with access to the private repository. After registration, install or enable `apple-platform` from Codex's plugin UI.

## Marketplace

The marketplace file is `.agents/plugins/marketplace.json`. It registers one local plugin:

```text
plugins/apple-platform
```

## Plugins

### apple-platform

Skills and agent definitions for Apple-platform codebases.

The Codex plugin manifest is:

```text
plugins/apple-platform/.codex-plugin/plugin.json
```

#### Skills

| Skill | Purpose |
| :---- | :------ |
| `configuring-ios-content` | Implements `UIContentConfiguration`, `UIHostingConfiguration`, and `UIContentView`. |
| `designing-swift-apis` | Applies Apple's Swift API design guidelines. |
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

#### Agents

Agent definitions are bundled under:

```text
plugins/apple-platform/agents
```

They are plugin artifacts, not project-scoped `.codex/agents` files.

| Agent | Purpose |
| :---- | :------ |
| `code-reviewer` | Reviews structural design consistency and architecture fit. |
| `code-standards-auditor` | Audits Swift changes against the bundled coding standards. |
| `information-entropy-reducer` | Flags unnecessary complexity and cognitive load. |
| `technical-writing-auditor` | Audits Markdown and doc comments for voice and structure. |
| `type-driven-design-auditor` | Finds compile-time correctness opportunities in Swift types. |

Codex runtimes do not always expose plugin-vended agent roles. Use these agents when asking for subagents, delegated review, or parallel agent work. Otherwise invoke skills directly with plugin-qualified names like `$apple-platform:writing-swift`, or let Codex select them implicitly.

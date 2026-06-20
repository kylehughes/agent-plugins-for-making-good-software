# Codex Plugins for Making Good Software

A Codex plugin marketplace for reusable skills and review agents that help make good software.

This is the Codex-native port of the Claude Code plugin marketplace with the same Apple Platform skill and agent set. The port keeps those assets inside the `apple-platform` plugin so the marketplace package, not this repository's project config, owns them.

## Install

Add this private GitHub marketplace to Codex:

```shell
codex plugin marketplace add kylehughes/codex-plugins-for-making-good-software
```

If Codex cannot resolve the private repository by slug, use the SSH URL instead:

```shell
codex plugin marketplace add git@github.com:kylehughes/codex-plugins-for-making-good-software.git
```

The GitHub account or SSH identity used by Codex must have access to the private repository. After the marketplace is registered, install or enable the `apple-platform` plugin from Codex's plugin UI.

## Marketplace

The marketplace file is:

```text
.agents/plugins/marketplace.json
```

It declares one local plugin:

```text
plugins/apple-platform
```

## Plugins

### apple-platform

Tools for Apple platform development.

The Codex plugin manifest lives at:

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
| `using-swift-concurrency` | Uses progressive-disclosure references for Swift Concurrency design, diagnostics, actors, protocols, logical races, anti-patterns, terminology, and async tests. |
| `writing-swift` | Covers Swift 6 coding standards and file organization. |
| `writing-technical-writing` | Writes direct, pragmatic technical prose. |

#### Agents

Agent definitions are bundled with the plugin under:

```text
plugins/apple-platform/agents
```

They are plugin artifacts, not project-scoped `.codex/agents` files:

| Agent | Purpose |
| :---- | :------ |
| `code-reviewer` | Reviews structural design consistency and architecture fit. |
| `code-standards-auditor` | Audits Swift changes against the bundled coding standards. |
| `information-entropy-reducer` | Flags unnecessary complexity and cognitive load. |
| `technical-writing-auditor` | Audits Markdown and doc comments for voice and structure. |
| `type-driven-design-auditor` | Finds compile-time correctness opportunities in Swift types. |

Use these agents only when explicitly asking Codex for subagents, delegated review, or parallel agent work and the current Codex runtime exposes plugin-vended agent roles. Otherwise the skills can be invoked directly with plugin-qualified names like `$apple-platform:writing-swift` or selected implicitly by Codex.

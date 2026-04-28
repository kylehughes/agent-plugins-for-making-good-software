# Codex Plugins for Making Good Software

A Codex plugin marketplace for reusable skills and review workflows that help make good software.

This is the Codex-native port of the Claude Code plugin marketplace with the same Apple Platform skill set. The port keeps skills inside the plugin and moves Claude subagents into project-scoped Codex custom agents under `.codex/agents/`.

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

#### Custom Agents

Codex custom agents are not bundled as plugin components in this port. They live at `.codex/agents/` for project-scoped use:

| Agent | Purpose |
| :---- | :------ |
| `code-reviewer` | Reviews structural design consistency and architecture fit. |
| `code-standards-auditor` | Audits Swift changes against the bundled coding standards. |
| `information-entropy-reducer` | Flags unnecessary complexity and cognitive load. |
| `technical-writing-auditor` | Audits Markdown and doc comments for voice and structure. |
| `type-driven-design-auditor` | Finds compile-time correctness opportunities in Swift types. |

Use these agents only when explicitly asking Codex for subagents, delegated review, or parallel agent work. Otherwise the skills can be invoked directly with plugin-qualified names like `$apple-platform:writing-swift` or selected implicitly by Codex.

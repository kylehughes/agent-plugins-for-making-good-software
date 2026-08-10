# Agent Plugins for Making Good Software

A plugin marketplace for making good software, first-class on both Claude Code and Codex.

It ships two plugins: `apple-platform`, with skills and agents tailored to Apple-platform development, and `universal`, with platform-agnostic tools for making good software.

## Install

This is a private repository. Both runtimes need a GitHub account or SSH key with access.

### Claude Code

```shell
/plugin marketplace add kylehughes/agent-plugins-for-making-good-software
/plugin install apple-platform@making-good-software
/plugin install universal@making-good-software
```

### Codex

```shell
codex plugin marketplace add kylehughes/agent-plugins-for-making-good-software
```

If Codex cannot resolve the private repository by slug, use the SSH URL:

```shell
codex plugin marketplace add git@github.com:kylehughes/agent-plugins-for-making-good-software.git
```

After registration, install or enable `apple-platform` and `universal` from Codex's plugin UI.

## apple-platform

Skills and agent definitions for Apple-platform codebases.

### Skills

| Skill | Purpose |
| :---- | :------ |
| `configuring-ios-content` | Patterns for `UIContentConfiguration`, `UIHostingConfiguration`, and `UIContentView` in UIKit cells. |
| `designing-swift-apis` | Apple's Swift API design guidelines for naming, argument labels, and doc comments. |
| `implementing-app-intents` | Guidance for App Intents: Siri, Apple Intelligence, entities, Spotlight, and value representations. |
| `instrumenting-accessibility-identifiers` | A type-safe `accessibilityIdentifier` pattern across SwiftUI, UIKit, XCUITest, and screenshot automation. |
| `localizing-strings` | Patterns for `String(localized:)` and string catalogs. |
| `modeling-swift-types-for-correctness` | Patterns for modeling Swift types that make invalid states unrepresentable. |
| `ordering-symbols` | The canonical member ordering for Swift types. |
| `organizing-swift-types` | Conventions for Swift types, extensions, access control, and file layout. |
| `simplifying-apple-platform-code` | The Apple-platform companion to `simplifying-code`: Swift, SwiftUI, UIKit, Xcode, availability, and concurrency cleanup. |
| `testing-swift-code` | Conventions for the Swift Testing framework (`@Test`, `@Suite`, `#expect`). |
| `using-swift-concurrency` | Swift Concurrency design, diagnostics, actor isolation, logical races, and async tests. |
| `writing-apple-platform-documentation` | The Apple-platform companion to writing-technical-prose: DocC, Swift doc comments, terminology, availability, and privacy wording. |
| `writing-swift` | Swift 6 standards for production code and packages. |

### Agents

| Agent | Purpose |
| :---- | :------ |
| `code-standards-auditor` | Audits Swift changes against the bundled coding standards. |
| `information-entropy-reducer` | Flags unnecessary complexity and cognitive load. |
| `type-driven-design-auditor` | Finds compile-time correctness opportunities in Swift types. |

## universal

Platform-agnostic tools for making good software.

### Skills

| Skill | Purpose |
| :---- | :------ |
| `compiling-agent-goals` | Turns specs and plans into finite `/goal` contracts that a persistent agent loop can actually finish. |
| `reviewing-code` | A review frame for correctness, security, concurrency, and compatibility risks, with line-specific findings. |
| `simplifying-code` | A behavior-preserving cleanup pass — reuse, simplify, de-duplicate, harden — for any language. |
| `writing-technical-prose` | Conventions for direct, pragmatic developer-facing prose — READMEs, ADRs, docs, and comments. |

### Agents

| Agent | Purpose |
| :---- | :------ |
| `code-reviewer` | Reviews structural design consistency and architecture fit. |
| `code-simplifier` | Finds behavior-preserving simplification and reuse opportunities in any language. |
| `correctness-reviewer` | Evidence-based review for concrete correctness, security, concurrency, and compatibility defects. |
| `technical-writing-auditor` | Audits developer-facing docs and comments for voice, structure, and AI-isms. |

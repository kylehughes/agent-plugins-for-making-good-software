---
name: writing-swift
description: "Write, debug, review, or migrate Swift code and packages. Use for .swift or Package.swift changes, Xcode builds, and compiler diagnostics; apply focused companion skills only for the concerns touched."
---

# Writing Swift

Write correct, idiomatic Swift while respecting the repository's compatibility contract. This skill is an implementation hub: load only the focused companion skill or reference required by the request.

## Resolve conflicts and gather evidence

1. Follow the user's request, repository instructions, and checked-in configuration in that order.
2. Inspect the smallest useful context: package/project/workspace, target or scheme, CI, formatter/linter, analogous code and tests, and generated-code boundaries.
3. Keep toolchain version, language mode, SwiftPM tools version, deployment target, dependency versions, and Xcode requirements separate. Never raise them silently.
4. Preserve user changes and public behavior. Inspect `git status --short`; never discard edits, create commits, or run broad migrations unless requested.

For compatibility decisions, use [Swift compatibility](references/swift-6.3.2.md) for the version axes and its recorded baseline. For newer type-system features, consult [feature status](../modeling-swift-types-for-correctness/references/swift-feature-status.md) only when needed; do not silently upgrade the project.

For broad orientation, run [the project-context script](scripts/swift-project-context.sh). Resolve bundled paths relative to this skill directory.

## Implementation loop

State the behavior or diagnostic, identify the owning layer, make the narrowest coherent edit, and compile early. Add focused tests for changed behavior, then run proportional validation and required repository checks. Inspect `git diff --check`, `git diff --stat`, and the final diff; report commands and gaps. Review-only requests produce findings without edits; explanation-only requests do not mutate the repository.

## Core defaults

- Prefer clear value semantics, immutable bindings, concrete types, and narrow access control.
- Model invalid states with types when that simplifies callers; use typed values instead of stringly typed state.
- Use optionals for legitimate absence and throwing APIs for recoverable failures. Preserve cancellation and error context.
- Avoid force unwraps, force casts, and `try!` except for explicit, documented invariants.
- Choose protocols, generics, `some`, `any`, type erasure, macros, wrappers, and compiler attributes only for a real boundary or measured benefit.
- Follow repository formatting and the Swift API Design Guidelines. For API naming, types, errors, access, docs, and source organization, read [API design and style](references/api-design-and-style.md) or the focused designing-swift-apis skill.

## Focused routing

Load only the concern-specific guidance needed for the task. Use repository instructions first, then the focused companion skill, then this hub's defaults. Prefer the focused sibling skill when available; otherwise use the matching bundled reference. Do not load both by default.

- Swift version, language mode, availability, or compatibility: [Swift compatibility](references/swift-6.3.2.md).
- Concurrency, isolation, `Sendable`, tasks, actors, cancellation, or async sequences: `using-swift-concurrency`; if unavailable, use [Concurrency](references/concurrency.md) for repair patterns or consult it only for an unresolved detail.
- Test structure and assertions: `testing-swift-code`; if unavailable, use [Testing Swift](references/testing.md) or consult it only for an unresolved detail.
- Timing, observers, cancellation, or async-test determinism: `testing-async-swift-code`; if unavailable, use the async portions of [Testing Swift](references/testing.md) or consult them only for an unresolved detail.
- Validated values, initializer or decoding validation, persisted-data compatibility, impossible-state claims, typed IDs, ownership, legal transitions, or preserving generic relationships: [modeling-swift-types-for-correctness](../modeling-swift-types-for-correctness/SKILL.md). Load it before changing or assessing those boundaries; it composes with the shared invariant procedure when needed.
- API design: `designing-swift-apis`; type and file layout: `organizing-swift-types`; member placement: `ordering-symbols`.
- User-facing UI text: `localizing-strings`; UIKit cell content: `configuring-ios-content`; sheets: `presenting-ios-modals`.
- Package/module boundaries: `structuring-swift-packages`.
- Swift developer documentation: `writing-apple-platform-documentation`.
- SwiftPM, Xcode, availability, interop, generated sources, and CI: [Packages, builds, and platforms](references/packages-builds-and-platforms.md).
- Review or debugging evidence and severity: [Review and debugging](references/review-and-debugging.md).

## Concurrency and tests

Treat concurrency as architecture. Identify mutable-state ownership, check default actor isolation, use structured child tasks, retain and cancel unstructured tasks when lifetime matters, and use detached tasks or unchecked escape hatches only with a concrete safety argument. Account for actor reentrancy and cancellation; never suspend while holding a lock.

Preserve the repository's test framework. Prefer Swift Testing for new unit or integration tests when supported; keep XCTest for UI, performance, existing, or framework-specific suites. Avoid sleeps, shared mutable globals, live network dependencies, and order dependence. Test error, cancellation, isolation, and boundary behavior, not only success.

## Build and validate

For SwiftPM, discover and use the repository's standard commands; the usual sequence is `swift package dump-package`, `swift build`, and `swift test`, with [the SwiftPM check script](scripts/swiftpm-check.sh) when applicable. For Xcode, discover the workspace/project, scheme, and destination before using `xcodebuild`; preserve CI signing and derived-data conventions. Run configured formatters and linters, plus [the changed-file lint script](scripts/lint-changed-swift.sh) when appropriate. Do not update dependencies, regenerate projects, or mass-format without a task requirement.

## Review and completion

Prioritize crashes, data loss, races, security/privacy, incorrect behavior, cancellation/lifetime bugs, compatibility, availability, and demonstrated performance regressions. Give file and line evidence; do not manufacture findings.

Before finishing, confirm requested behavior, repository instructions, compatibility and public API stability, defensible isolation/cancellation, proportional deterministic tests, required checks, and a clean diff without generated artifacts, secrets, or dependency churn.

## Reference Map

Read only the references relevant to the requested work. The focused companion skills above are preferred routers.

- [Swift compatibility](references/swift-6.3.2.md): version model, manifest settings, language/runtime gates.
- [Concurrency](references/concurrency.md): isolation, `Sendable`, tasks, actors, cancellation, continuations, streams, and repairs.
- [Testing Swift](references/testing.md): Swift Testing, XCTest, deterministic async tests, migration, and review.
- [API design and style](references/api-design-and-style.md): naming, types, errors, access, docs, formatting, and organization.
- [Packages, builds, and platforms](references/packages-builds-and-platforms.md): SwiftPM, Xcode, availability, platforms, interop, generated sources, and CI.
- [Review and debugging](references/review-and-debugging.md): investigation, severity, compatibility, evidence, and reporting.

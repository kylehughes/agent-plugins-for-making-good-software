---
name: writing-swift
description: >-
  Write, edit, debug, review, migrate, and test production Swift code and Swift packages. Use for .swift or
  Package.swift changes; Swift 6 concurrency, actors, Sendable, async/await, Swift Testing or XCTest, API design,
  SwiftPM, Xcode builds, compiler diagnostics, performance, C/C++ interop, formatting, and documentation. Inspect
  and preserve the repository's toolchain, deployment targets, architecture, and conventions; use Swift 6.3.2 for
  greenfield work or explicit upgrades. Do not use for non-Swift work or product discussion without implementation.
---

# Writing Swift

Produce correct, idiomatic, maintainable Swift while respecting the repository's actual compatibility contract. Treat
this skill as engineering guidance, not a license to rewrite unrelated code.

## Resolve Conflicts in This Order

1. Follow the user's explicit request.
2. Follow repository instructions and checked-in configuration.
3. Preserve public behavior, source compatibility, deployment targets, and architecture unless change is requested.
4. Match nearby code when it is internally consistent and safe.
5. Apply this skill's defaults.

Never silently raise a Swift tools version, language mode, deployment target, dependency version, or Xcode requirement.

## Work from Evidence

Before editing, inspect the smallest useful set of repository context:

- Read applicable `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `CONTRIBUTING.md`, README, host-specific instructions, and
  nested instruction files.
- Identify whether the project uses SwiftPM, an Xcode project/workspace, or both.
- Inspect `Package.swift`, build settings, CI, formatter/linter configuration, and an analogous implementation and test.
- Determine the selected target or scheme, supported platforms, Swift language mode, default actor isolation, enabled
  upcoming/experimental features, test framework, and generated-code boundaries.
- Run the bundled [project-context script](scripts/swift-project-context.sh) when broad orientation is useful.

Resolve bundled script and reference paths relative to this skill directory, not the repository under repair. Pass the
repository path to scripts that accept one.

Before editing, inspect `git status --short` when available. Preserve all user changes. Never use destructive Git
commands, discard unrelated edits, create commits, or amend history unless explicitly requested.

Keep these concepts separate:

- **Toolchain version:** the compiler and tools installed, such as Swift 6.3.2.
- **Language mode:** usually Swift 5 or Swift 6 semantics.
- **SwiftPM tools version:** manifest API compatibility, such as `// swift-tools-version: 6.3`.
- **Deployment target:** the oldest OS/runtime on which the product must run.

A newer compiler does not imply a newer language mode or runtime. See
[Swift 6.3.2 and compatibility](references/swift-6.3.2.md).

## Use a Tight Implementation Loop

Honor the requested mode: implementation requests require edits and validation; review-only requests require findings
without changing files; explanation-only requests should not mutate the repository.

1. State the behavior or diagnostic being changed.
2. Find the owning layer and the narrowest coherent edit.
3. Preserve existing APIs and concurrency semantics unless the task calls for migration.
4. Implement with compiler-enforced invariants where practical.
5. Compile the affected target early; do not accumulate speculative edits.
6. Add or update focused tests that would fail without the change.
7. Run narrow validation, then the repository's broader required checks.
8. Inspect the final diff for accidental formatting, generated files, dependency churn, and compatibility changes.
9. Report exactly what ran and any validation that could not run.

Do not run dependency updates, mass formatting, project regeneration, or automated migrations unless required by the task.

## Core Swift Defaults

- Prefer clear value semantics and immutable bindings, but choose reference identity when the domain requires it.
- Model invalid states out of the type system where doing so simplifies callers.
- Start with concrete types. Introduce protocols for a real abstraction boundary, multiple conformers, or a useful test seam.
- Use the narrowest practical access level. Treat every `public` or `open` declaration as an API commitment.
- Prefer typed values over stringly typed identifiers, flags, notifications, and state machines.
- Use optionals for legitimate absence. Use throwing APIs for failures callers may need to understand or recover from.
- Preserve cancellation and meaningful error context. Do not catch and discard errors merely to simplify control flow.
- Avoid force unwraps, force casts, and `try!` in ordinary paths. They are acceptable only for an intentional invariant
  that cannot reasonably be represented in the type system; make the invariant obvious and fail with useful context.
- Use `precondition` for programmer-contract violations, `assert` for debug-only checking, and errors for recoverable input
  or environmental failures.
- Choose `some`, `any`, generics, and type erasure deliberately. Do not add abstraction solely to make code look generic.
- Add macros, property wrappers, result builders, ownership features, or compiler attributes only when they materially
  improve the design or measured behavior.
- Follow the Swift API Design Guidelines and the repository formatter. See
  [API design and style](references/api-design-and-style.md).

## Treat Concurrency as Architecture

Do not silence Swift 6 diagnostics mechanically. Identify which domain owns mutable state and where values cross isolation
boundaries.

- Check the module's default actor isolation before adding annotations.
- Use `@MainActor` for UI state and main-thread framework contracts, not as a blanket compiler-error suppressor.
- Prefer structured child tasks (`async let`, task groups) whose lifetime is tied to their parent.
- Create an unstructured `Task` only at a synchronous boundary or for an independently managed operation; retain and
  cancel it when lifetime matters.
- Use `Task.detached` only when non-inheritance of actor context, priority, and task-local values is specifically intended.
- Make crossing values `Sendable` by design. Treat `@unchecked Sendable`, `nonisolated(unsafe)`, and `@preconcurrency` as
  audited escape hatches requiring a concrete safety argument.
- Account for actor reentrancy: values observed before an `await` may be stale afterward.
- Use an actor for asynchronously accessed mutable state. Use `Synchronization.Mutex` for small synchronous critical
  sections when deployment constraints permit. Never suspend while holding a lock.
- Check and propagate cancellation in long-running or iterative work.

Use [Concurrency](references/concurrency.md) for diagnostic repair patterns and design guidance.

## Test According to the Repository

Preserve the existing framework unless migration is part of the task.

- Prefer Swift Testing for new unit and integration tests when the supported toolchain and target permit it.
- Keep XCTest for UI tests, performance tests, existing suites, or framework-specific integration where it remains the
  appropriate tool.
- Write deterministic, isolated tests that can run in parallel. Avoid arbitrary sleeps, shared mutable globals, live
  network dependencies, and reliance on test order.
- Use `#require` when a failed prerequisite must stop a Swift Testing test; use `#expect` for independent expectations.
- Prefer parameterized tests for repeated behavior and focused test names or descriptions that state the proved behavior.
- Test error, cancellation, isolation, and boundary cases, not only the happy path.

See [Testing Swift](references/testing.md).

## Respect Style without Creating Churn

- Repository formatter and linter configuration wins over personal preferences.
- Format touched code only unless the task explicitly requests a wider cleanup.
- Preserve established file headers; do not invent copyright or boilerplate headers.
- Use `// MARK:` when it improves navigation and matches the repository. Do not add empty organizational ceremony.
- Prefer one primary type per file, but keep small tightly coupled helpers nearby when separation would harm comprehension.
- Group declarations semantically. Do not alphabetize code when order communicates lifecycle, protocol flow, or usage.
- Document public library API and non-obvious contracts. Explain why, invariants, ownership, isolation, complexity, and
  workarounds; do not narrate obvious syntax.
- Keep comments synchronized with behavior and remove dead commented-out code.

## Build and Validate

Start with the narrowest command that exercises the edit.

For SwiftPM packages:

```bash
swift package dump-package
swift build
swift test
```

Use the bundled [SwiftPM check script](scripts/swiftpm-check.sh) for the standard sequence. Add `--configuration release` only when release optimization is
relevant. Use `--filter` to shorten iteration, then run the required broader suite.

For Xcode projects or workspaces:

```bash
xcodebuild -list -project Project.xcodeproj
xcodebuild -showdestinations -scheme Scheme -project Project.xcodeproj
xcodebuild build -scheme Scheme -project Project.xcodeproj -destination '...'
xcodebuild test -scheme Scheme -project Project.xcodeproj -destination '...'
```

Prefer a workspace when the repository uses one. Never guess a scheme or destination when it can be discovered. Preserve
code-signing and derived-data conventions from CI or repository scripts.

Run `swift-format`, SwiftLint, or other tools only when installed or configured by the repository. Use the bundled
[changed-file lint script](scripts/lint-changed-swift.sh) for a non-mutating `swift-format` check of changed Swift files.

Always inspect:

```bash
git diff --check
git diff --stat
git diff
```

For package, Xcode, platform, interop, and CI details, see
[Packages, builds, and platforms](references/packages-builds-and-platforms.md).

## Review and Debug with Priorities

When reviewing, report concrete findings in descending impact:

1. Crashes, data corruption, data races, security or privacy faults.
2. Incorrect behavior, cancellation or lifetime bugs, broken compatibility, and availability failures.
3. API design and maintainability issues that create plausible future defects.
4. Measured or clearly demonstrated performance regressions.
5. Style only when it violates repository rules or materially impairs readability.

Give a file and line, explain the failure mode, and propose the smallest sound fix. Do not manufacture findings to fill a
review. If no actionable issue is found, say so and identify residual validation gaps.

When debugging, reproduce first, reduce the failing path, form one falsifiable hypothesis at a time, and use compiler
messages, tests, logs, sanitizers, and profiling evidence before redesigning. See
[Review and debugging](references/review-and-debugging.md).

## Completion Criteria

Before finishing, verify that:

- The implementation satisfies the requested behavior and repository instructions.
- Toolchain, language mode, tools version, deployment target, and public API changed only intentionally.
- Concurrency isolation and cancellation behavior are explicit and defensible.
- Tests cover the changed behavior and are deterministic.
- Applicable builds, tests, formatters, and linters pass, or failures are reported precisely.
- The final diff contains no unrelated churn, generated artifacts, secrets, or dependency updates.

## Reference Map

Load only the reference relevant to the task:

- [Swift 6.3.2 and compatibility](references/swift-6.3.2.md): version model, manifest settings, language and runtime gates,
  and notable Swift 6.2/6.3 capabilities.
- [Concurrency](references/concurrency.md): isolation, `Sendable`, tasks, actors, cancellation, continuations, streams,
  synchronization, and diagnostic repairs.
- [Testing Swift](references/testing.md): Swift Testing, XCTest, deterministic async tests, migration, and test review.
- [API design and style](references/api-design-and-style.md): naming, types, errors, access control, docs, formatting,
  performance, and source organization.
- [Packages, builds, and platforms](references/packages-builds-and-platforms.md): SwiftPM, Xcode, availability,
  cross-platform code, interop, generated sources, and CI.
- [Review and debugging](references/review-and-debugging.md): investigation workflow, review severity, compatibility,
  performance evidence, and reporting templates.

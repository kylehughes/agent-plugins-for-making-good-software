---
name: simplifying-code
description: "Simplify existing code while preserving behavior. Use proactively for requested cleanup, deduplication, local refactoring, or simplification review; preserve read-only review scope. Ordinary defect review belongs to reviewing-code."
---

# Simplifying Code

Run this skill as a disciplined, behavior-preserving cleanup and hardening pass over code that already exists or has just been written. The goal is smaller, clearer, safer, more idiomatic, more reusable, and more maintainable code.

This is not a rewrite license. Prefer deletion, reuse, narrower boundaries, and targeted fixes over new architecture. Expand scope only when the current change cannot be simplified safely without touching adjacent code.

For a simplification review, inspect and report opportunities without editing. Apply fixes only when cleanup or implementation is authorized by the current request or enclosing workflow. Preserve that mode throughout the steps below.

## Non-Negotiable Contract

1. Preserve intended behavior, public API, persistence formats, wire formats, analytics names, localization keys, accessibility semantics, migrations, deployment targets, security boundaries, and observable UI behavior unless the user explicitly asked to change them.
2. Treat repository conventions and project configuration as the source of truth. Read nearby code and manifests before changing style, architecture, formatting, tests, or build settings.
3. Use the local toolchain and declared project settings. Do not hard-code assumptions about language versions, SDKs, frameworks, package managers, runtime versions, or CI commands.
4. Search before adding or keeping code. A simplification pass should not leave a duplicate helper, component, formatter, wrapper, service, mock, fixture, utility, compatibility shim, or mini-framework when an existing primitive fits.
5. Keep fixes local and reviewable. Avoid mass formatting, broad renames, dependency churn, file moves, generated-file edits, and architectural migrations unless they remove concrete duplication or fix a concrete defect in the reviewed surface.
6. Never discard user work with destructive git or filesystem operations. Do not run `git reset`, `git checkout --`, `git clean`, force pushes, recursive deletes, or equivalent operations unless the user specifically requested that operation.
7. Verify with the cheapest relevant command that proves the touched code still builds or behaves correctly. If verification cannot be run, report the exact blocker.
8. Be honest about uncertainty. Do not claim tests passed, commands ran, files changed, or behavior was preserved unless that is grounded in actual inspection or execution.

## Platform-Specific Companion Skills

This skill is deliberately universal. It should not contain detailed rules for any single platform or framework.

At the start of the task, infer the target stack from file extensions, manifests, project files, imports, package managers, test files, and the user's wording. If a more specific skill is available for that stack, compose with it:

1. Use this skill to establish the review surface, behavior-preservation contract, reuse/deletion pass, and verification discipline.
2. Use the platform-specific skill as an additional checklist for availability, lifecycle, concurrency, UI, framework, build-system, and compatibility hazards. Reuse already active guidance, the frozen surface, decisions, and evidence in one workflow; neither skill restarts the other. When called from a larger workflow, respect its review and verification boundaries.
3. If the universal checklist and the platform-specific checklist conflict, the more specific rule wins for that platform.
4. Do not copy platform-specific rules into this skill. Keep this skill neutral so it remains valid across languages and ecosystems.
5. If no platform-specific skill is available, infer the analogous checks from the language, runtime, dependency manager, concurrency model, test runner, framework lifecycle, and compatibility mechanism.

Examples of companion-skill areas include mobile platforms, web frameworks, backend runtimes, data systems, game engines, embedded systems, infrastructure-as-code, and security-sensitive domains.

## Workflow

### 1. Identify and Freeze the Review Surface

Start by identifying the code that should be reviewed. Use the same baseline surface for all review passes so findings are not biased by later edits.

Run when available:

```sh
git status --short
git diff --stat
git diff --name-status
```

Then choose the surface:

- If staged or unstaged tracked changes exist, review `git diff HEAD` so staged and unstaged edits are considered together.
- If only unstaged tracked changes exist, `git diff` is acceptable, but still note the changed file list from `git status --short`.
- If untracked source files exist, inspect them explicitly with `git ls-files --others --exclude-standard`; ordinary diffs will not show them.
- If the working tree is clean and the request concerns a branch or commit, compare against its relevant base from project or task context. For a focused cleanup, use the explicitly named files.
- If the repository is not a git repository, use the files identified by the request or enclosing task. Do not infer ownership from modification time alone.
- If there are merge conflicts, stop broad cleanup and only simplify conflict-resolution code unless the user explicitly asked for a larger pass.
- If a file is generated, vendored, minified, binary, huge, or build output, do not hand-edit it. Inspect only enough to identify the relevant hand-written source.

Freeze the initial file list before editing. Expand the surface only for a concrete reason: deleting a duplicated helper, updating necessary call sites, moving a fallback into an existing compatibility layer, or fixing a compile/test error introduced by the cleanup.

### 2. Recon the Repository Before Judging the Diff

Inspect enough context to avoid cargo-cult fixes:

- Project manifests, workspace/project files, package files, lockfiles, module manifests, build settings, language settings, runtime/deployment targets, lint/format configs, test configs, CI scripts, and code-generation config.
- Nearby code: adjacent types, helpers, services, components, reducers/stores, data adapters, fixtures, mock builders, design tokens, environment/dependency wrappers, compatibility shims, and error/logging primitives.
- Ownership boundaries: package/module visibility, public/internal/private API, generated-code boundaries, vendored dependencies, test-only support code, and platform-specific directories.
- Existing commands: README, CONTRIBUTING, Makefile, Justfile, Taskfile, package scripts, CI config, or project-specific docs.

Do not apply a rule merely because it is common elsewhere. Match the host codebase unless the local convention is actively causing the problem being fixed.

### 3. Build an Intent Map

Before editing, identify the contracts the changed code appears to rely on:

- Inputs, outputs, errors, fallback behavior, validation, retries, cancellation, cleanup, resource lifetime, ordering, timing, identity, equality, hashing, pagination, precision, rounding, locale, timezone, encoding, caching, and persistence behavior.
- Public API, ABI, serialization, schema, migration, feature-flag, analytics, logging, accessibility, localization, and configuration boundaries.
- Runtime compatibility: declared minimum runtime, supported platforms, package version ranges, framework availability, database versions, browser/runtime support, or deployment environments.

Use this map to distinguish safe simplification from behavior change.

When a requested proof names an invariant, or a simplification changes an enforcement model or state transition, use [verifying-invariants](../verifying-invariants/SKILL.md) to preserve the relevant boundary with the lightest adequate evidence. Do not turn ordinary cleanup into a proof exercise, refactor, or test-infrastructure project.

### 4. Run Independent Review Passes

Start with behavior preservation, reuse, and cognitive load. Add the concurrency, security, performance, and testing passes when the scoped code implicates those concerns. A requested full audit covers every applicable pass; record a short reason for any exclusion. Keep one frozen surface and consolidate findings before editing. Use independent reviewers only when they add useful evidence within the caller’s delegation and verification rules.

- **Pass A: Behavior, Compatibility, and Correctness** — Find changes that simplify incorrectly or silently alter contracts.
- **Pass B: Reuse, Deletion, and Consolidation** — Look for code that should not exist because the project already has a better primitive.
- **Pass C: Shape, Boundaries, and Cognitive Load** — Find code that makes the system harder to reason about.
- **Pass D: Concurrency, Lifecycle, and Resource Ownership** — Find simplifications that create leaks, races, stuck work, or lifetime bugs.
- **Pass E: Security, Privacy, and Trust Boundaries** — Find changes that weaken safety.
- **Pass F: Performance, Memory, and Scalability** — Find obvious waste without premature optimization.
- **Pass G: Tests, Observability, and Failure Modes** — Check whether simplified code remains testable and diagnosable.

Read the selected pass sections in [review-passes](references/review-passes.md) before classifying findings.

### 5. Classify Findings Before Editing

Classify findings before changing code:

- **Must fix:** compile errors, behavior regressions, compatibility defects, data races, leaks, security/privacy issues, broken tests, invalid migrations, and clear duplicate code that can be removed safely.
- **Should fix:** redundant state, unnecessary wrappers, parameter sprawl, obvious inefficiencies, unclear names, avoidable branching, duplicated fixtures/helpers, and local boundary leaks.
- **May skip:** subjective style differences, churn-heavy refactors, speculative abstractions, low-risk duplication that is clearer as-is, changes requiring product decisions, and improvements outside the frozen surface.

For each skipped real finding, keep a short note explaining why it was not changed. Do not mention speculative findings that proved false unless the user needs to know.

### 6. Apply Safe Fixes

Skip edits in review-only mode and report actionable opportunities instead. When editing:

1. Work in small patches. After each meaningful patch, reassess whether the code got smaller and clearer.
2. Preserve the smallest stable API. Tighten visibility where safe, but do not break public, cross-module, serialized, persisted, reflected, plugin, or external callers.
3. Remove unused code, imports, dependencies, mocks, fixtures, test data, and configuration after consolidation.
4. Keep comments only for non-obvious why: invariants, constraints, compatibility traps, security decisions, performance tradeoffs, and workarounds with a reason. Delete comments that narrate the task or restate the code.
5. Do not introduce dependencies, global mutable state, build settings, formatters, linters, macros, code generation, architectural layers, or background services unless the repository already uses them and the change has a concrete payoff.
6. Avoid mass formatting. Format only touched code unless the user asked for a formatting pass or the repo's formatter can target the changed files.
7. Keep generated files generated. If generated output must change, update the source generator or state that regeneration is required.
8. Re-run `git diff --check` or the repository equivalent before final verification when practical.

### 7. Verify

Choose verification based on the touched files and repository conventions. Prefer documented commands over guesses. Select only checks that add needed evidence; this is not a command sequence. If a focused behavior check already compiles the same dependent graph, do not also run a compile-only command on the unchanged snapshot. Reuse completed evidence from the enclosing workflow.

Choose among:

1. Fast static checks for the touched language or package.
2. Targeted unit tests for changed behavior.
3. Package/module build.
4. App/integration build or CI-equivalent command when the change crosses module boundaries or platform availability.
5. Formatter/linter only when configured by the repository or requested by the user.

If no command is obvious, inspect project files to discover one. If discovery is expensive or ambiguous, run the narrowest safe build/test command and report the limitation.

Include the command and result in the final response. Capture verification results separately: the exit status of a compound shell command belongs to its final operation unless earlier statuses were recorded explicitly. If a command fails for an unrelated pre-existing reason, report that separately from issues introduced by the cleanup.

Before finalizing, confirm the [compact checklist](references/compact-checklist.md).

## Reference Map

Load only the reference relevant to the current step:

- [Review passes](references/review-passes.md): the Pass A–G checklists selected during step 4.
- [Adaptation and anti-simplification](references/adaptation-and-anti-simplification.md): universal adaptation rules, anti-simplifications to reject, and file-type-specific attention prompts.
- [Compact checklist](references/compact-checklist.md): final confirmation checklist before finishing.

## Final Response Format

Finish with a concise summary:

1. What changed, grouped by behavior/reuse/quality/performance when useful.
2. Verification commands run and their results.
3. Any real findings intentionally skipped or deferred, with a brief reason.
4. Any verification not run, with the concrete blocker.

If no fixes were needed, say the reviewed surface was already clean and list the verification performed. Do not invent changes, tests, or results.

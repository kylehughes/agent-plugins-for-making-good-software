---
name: simplify-code
description: Reviews changed code for reuse, simplicity, quality, and efficiency, then fixes issues directly. Use when the user asks to simplify code, clean up a diff, reduce complexity, reuse existing utilities, remove unnecessary code, or run reduce/reuse/recycle.
---

# Simplify Code

Use this as a focused cleanup pass after code has been written. The goal is to make the change smaller, more obvious, and more efficient without changing intended behavior.

## Workflow

### 1. Identify the Review Surface

Run `git status --short` and inspect the current changes:

- If there are only unstaged changes, review `git diff`.
- If there are staged changes, review `git diff HEAD` so staged and unstaged edits are included together.
- If there are no git changes, review the most recently modified files the user mentioned or that you edited earlier in the conversation.

Use the same review surface for every pass.

### 2. Run Three Independent Review Passes

Run these passes independently. If the user or environment policy permits parallel reviewers, use them and give each reviewer the full diff. Otherwise, perform the passes yourself, keeping the findings separated until all three are complete.

#### Reuse Review

For each change:

1. Search for existing utilities, helpers, models, extensions, and components that could replace newly written code. Check shared modules, utility directories, adjacent files, and package exports.
2. Flag any new function, type, or view that duplicates existing functionality. Prefer reusing the existing implementation when it fits.
3. Flag inline logic that should use an existing abstraction: hand-rolled string manipulation, manual path handling, custom environment checks, ad hoc type guards, date formatting, logging, localization, styling tokens, and similar patterns.

#### Quality Review

Look for code that increases cognitive load or weakens existing boundaries:

1. Redundant state: stored values that duplicate existing state, cached values that can be derived, observers/effects that could be direct calls.
2. Parameter sprawl: new parameters added instead of reshaping the call site, introducing a small type, or generalizing existing behavior.
3. Copy-paste with slight variation: near-duplicate blocks that should share a helper, component, or model.
4. Leaky abstractions: internal details exposed across boundaries, especially package internals, service implementation details, or UI/networking leaks.
5. Stringly typed code: raw strings where constants, enums, typed identifiers, or existing domain types already exist.
6. Unnecessary UI nesting: wrapper views/elements that add no layout, styling, identity, or accessibility value.
7. Unnecessary comments: comments explaining what the code does, narrating the task, or referencing the caller/request. Keep only non-obvious whys: hidden constraints, subtle invariants, and real workarounds.

#### Efficiency Review

Look for wasted work or avoidable scaling problems:

1. Unnecessary work: redundant computations, repeated file reads, duplicate network/API calls, and N+1 patterns.
2. Missed concurrency: independent operations run sequentially when they could safely run in parallel.
3. Hot-path bloat: blocking or expensive work added to startup, per-request, per-render, scrolling, layout, or frequently repeated paths.
4. Recurring no-op updates: state/store updates inside polling loops, intervals, observers, subscriptions, or event handlers that fire unconditionally. Add change-detection guards so downstream consumers are not notified when nothing changed. If an updater/reducer callback can signal no change by returning the same reference or equivalent sentinel, verify wrappers preserve that signal.
5. Unnecessary existence checks: pre-checking file/resource existence before operating when direct operation plus error handling would avoid time-of-check/time-of-use races.
6. Memory and lifecycle issues: unbounded data structures, missing cleanup, retained callbacks, observer leaks, and event listener leaks.
7. Overly broad operations: reading full files or loading full collections when only a subset, query, or targeted lookup is needed.

### 3. Fix the Findings

Aggregate findings from all three passes and fix each real issue directly. If a finding is a false positive or not worth changing, skip it and briefly note why.

Prefer small, local fixes that remove code or reuse existing APIs. Avoid turning this cleanup pass into a broad refactor unless the duplication or abstraction leak cannot be addressed safely in a smaller way.

### 4. Verify

Run the cheapest relevant verification for the files touched:

- For Swift formatting-only changes, run the project formatter if appropriate.
- For package-scoped Swift changes, prefer the relevant package build or test target.
- For app-wide or cross-package Swift changes, run the relevant build, test, or CI-equivalent command documented by the host repository when practical.
- If no verification command is practical, state that explicitly in the final summary.

Finish with a short summary of what was fixed, or confirm the code was already clean.

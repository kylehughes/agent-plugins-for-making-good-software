---
name: reviewing-code
description: >
  Review code changes for design consistency, correctness, and concurrency safety on Apple
  platforms. Use when reviewing pull requests, auditing diffs, checking AI-generated code,
  evaluating whether changes fit existing patterns, or performing code review on Swift code.
  Catches implicit architecture changes, concurrency bugs, and implementation issues that
  linting misses.
---

# Reviewing Code

Code review catches what linting misses: changes that violate design assumptions, introduce concurrency bugs, or quietly alter architecture. The most important review question is not "does this code work?" but "does this code belong here, shaped this way?"

## Design vs Implementation

Every piece of code has a design behind it (why it's shaped this way) and an implementation (how it's written). "Design" here means the architectural decisions: which type owns this responsibility, what isolation boundary protects this state, what invariants callers rely on. AI-generated code often changes implementation in ways that violate these decisions, or changes the design without acknowledging the shift.

Reviewing implementation without understanding design leads to approving code that works in isolation but breaks the system.

## Review Process

### 1. Understand the Design

Before evaluating the change, understand what it's working within. Read surrounding code, not just the diff:

- What pattern is this following? (Coordinator, Request/Subscription, ViewModel, etc.)
- What are the isolation boundaries? (MainActor, nonisolated, actor)
- What invariants does surrounding code assume?
- What package or module is this in, and what are its dependency rules?

A change cannot be evaluated without understanding the design it operates in.

### 2. Classify the Change

| Type | What it means | Review focus |
|------|---------------|--------------|
| **Fits existing design** | Implementation within current architecture | Correctness, style, patterns |
| **Extends design** | Adds something new that's consistent | Does it fit? Is it coherent? |
| **Changes design** | Alters fundamental assumptions | Intentional? Documented? Dependents updated? |

Most changes should fit existing design. Changes that alter design need explicit acknowledgment because they are architectural decisions with downstream consequences.

### 3. Check Consistency

If design changed (or might have):

- Does the new design contradict existing code elsewhere?
- Are there files that now violate the updated design?
- Is the change documented (ADR, AGENTS.md, comments)?

Inconsistency means the change is incomplete. A design change that only updates some of the affected code is worse than no change at all because it creates two conflicting patterns.

### 4. Check Implementation

With design verified, check the implementation against these standards. Consult the referenced skills for detailed rules:

**Concurrency** (highest bug priority — concurrency issues are the hardest to reproduce and fix):
- `preventing-swift-logical-races` — Guards before await, reentrancy protection
- `avoiding-problematic-swift-concurrency-patterns` — No Task.detached, no MainActor.run, no blocking async
- `conforming-protocols-with-swift-concurrency` — Isolated conformances, non-Sendable first
- `deciding-when-to-use-swift-actors` — Three conditions for actor use

**Structure**:
- `organizing-swift-types` — Access control, extension usage, no MARK comments
- `ordering-symbols` — Lexicographic ordering within access levels
- `designing-swift-apis` — Naming, fluent usage, documentation

**Patterns**:
- `localizing-strings` — String(localized:) patterns

**Foundation**:
- `writing-swift` — Swift 6, no force unwraps, Swift Testing

### 5. Backtrack If Needed

If implementation doesn't fit design, go back to step 1. The design understanding may be wrong, or the change is trying to alter design without saying so.

Implementation problems often mean incomplete design understanding. Fix that first before flagging individual lines.

## What to Flag

### Always Flag

- Design changes without acknowledgment
- Logical race conditions (check-then-act across await boundaries)
- Actors that don't meet the three-condition test from `deciding-when-to-use-swift-actors`
- Force unwraps (`!`), `try!`, `as!`
- XCTest usage (should be Swift Testing)
- Inconsistency with surrounding code's assumptions

### Flag When Meaningful

- Overly complex solutions when simpler alternatives exist
- Non-Apple platform patterns where Apple conventions apply
- Abstractions that aren't self-explanatory to the next reader
- External dependencies where an internal solution would suffice

### Do Not Flag

- Style preferences not covered by established skills
- Different but equally valid approaches to the same problem
- Minor naming preferences that don't affect clarity

## PR Comment Format

Keep comments actionable. State what is wrong, why it matters, and what to do about it:

```
**[Concurrency]** Logical race in `fetchAndUpdate()`

ViewModel.swift:42 — State is read before `await`, then written after, but another
call could interleave. The guard on line 40 doesn't protect against reentrancy.

Consider adding an `isLoading` guard that is set before the await and checked after,
or restructure to avoid the read-await-write sequence.
```

Categories: `Design`, `Concurrency`, `Pattern`, `Style`, `Question`

## Final Design Check

After reviewing individual issues, step back and evaluate the change holistically:

- **Is the complexity justified?** If the change introduces significant complexity, does it solve a real problem that simpler approaches cannot?
- **Is the right path obvious?** Would another developer reading this code understand the intended usage without extra explanation?
- **Could the compiler catch this?** Are there runtime checks that could be replaced with type-system constraints?
- **Does it feel like standard Apple platform code?** Would this look natural in an Apple sample project?
- **Are new abstractions self-explanatory?** If the change introduces a new pattern, can someone understand it without reading a design document?
- **Is every dependency necessary?** Could an internal implementation replace an external dependency without unreasonable effort?

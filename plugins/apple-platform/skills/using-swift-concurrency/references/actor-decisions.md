# Actor Decisions

Apply these decision criteria when considering whether to introduce a custom actor into a Swift codebase.

Source: Matt Massicotte, <https://www.massicotte.org/actors>, accessed 2025-11-24.

## The Actor Decision Test

An actor is appropriate **only** when all three conditions are met:

1. **Non-Sendable state** - The type holds thread-unsafe data that requires protection
2. **Atomic mutations required** - Operations on that state must be atomic
3. **Cannot run on MainActor** - The work genuinely cannot be performed on the main thread

If any condition is missing, use a different approach.

## Decision Matrix

| Situation | Recommended Approach |
|-----------|---------------------|
| Shared state tied to UI | `@MainActor` class |
| Shared state, all Sendable | Class (no actor needed) |
| State needs synchronous access | Class with explicit synchronization |
| Truly concurrent, non-Sendable state | Custom actor |
| "Network client" with no non-Sendable state | `@MainActor` class with `async let` or `@concurrent` |

## Common Anti-Patterns

### Using Actors to Silence Diagnostics

Never introduce an actor solely to fix a concurrency diagnostic that is not understood. This reinforces incorrect mental models and often leads to fundamentally flawed system designs.

Every custom actor should be justifiable with: "This is an actor because it has non-Sendable state requiring atomic mutations that cannot run on MainActor."

### Empty Protection Actors

A "network client" actor containing zero non-Sendable state misuses actors. The pattern exists because actors happen to run off the main thread, but this creates artificial limitations:

- Cannot perform synchronous work concurrently (like decoding responses)
- Adds unnecessary complexity

**Better**: Use a `@MainActor` class with `async let` or `@concurrent` functions for parallel work.

## Synchronous Access Consideration

Actors do not support synchronous external access. Before choosing an actor, ask:

- Can the rest of the system tolerate asynchronous access to this state?
- Will any code path need synchronous reads or writes?

If synchronous access is required, an actor is not viable.

## The MainActor Default

Every Swift program includes `MainActor`, which already manages enormous amounts of state. For UI-connected state, `@MainActor` is usually the right choice because:

- State is fundamentally tied to UI
- Synchronous access from main thread is often needed
- Simpler mental model than custom isolation domains

## Reference: Value vs Reference Type Selection

Before reaching actor vs class, first determine if a reference type is needed at all:

- **Value type** (struct/enum): When each consumer should have its own copy
- **Reference type** (class/actor): When multiple consumers must share a single source of truth

Choose a class when sharing state without special isolation requirements. Choose an actor only when the three-condition test passes.

## Mental Model: Actors as Remote Services

Think of actors as remote network services:

- Data is physically inaccessible except through requests
- Inputs and outputs must be packaged (Sendable)
- Other requests can happen simultaneously
- All interaction is asynchronous

This metaphor clarifies why synchronous access is impossible and why Sendable boundaries matter.

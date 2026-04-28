---
name: deciding-when-to-use-swift-actors
description: >
  Guides decisions about when Swift actors are appropriate vs classes, structs, or
  @MainActor. Use when choosing between actor, class, or MainActor for shared state
  management, when questioning whether an actor is the right concurrency primitive,
  when actors are being introduced solely to fix Swift 6 compiler diagnostics, or when
  deciding between struct, class, and actor for a new type. Also consult when evaluating
  whether a "network client" or "service" type should be an actor, when synchronous
  access requirements conflict with actor isolation, or when considering value types
  vs reference types for concurrent code.
---

# Deciding When to Use Swift Actors

Apply these decision criteria when considering whether to introduce a custom actor into a Swift codebase.

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
| "Network client" with no non-Sendable state | `@MainActor` class with `async let` or `@concurrent` (Swift 6.2+) |

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

## Concrete Example: Applying the Three-Condition Test

Consider a type that caches downloaded images:

```swift
// Does it hold non-Sendable state? → Yes (NSCache is not Sendable)
// Does it need atomic mutations? → Yes (concurrent cache reads/writes)
// Can it run on MainActor? → No (image decoding is expensive)
// ✅ All three conditions met → actor is appropriate

actor ImageCache {
    private let cache = NSCache<NSString, UIImage>()

    func image(for key: String) -> UIImage? {
        cache.object(forKey: key as NSString)
    }

    func store(_ image: UIImage, for key: String) {
        cache.setObject(image, forKey: key as NSString)
    }
}
```

Now consider a type that fetches JSON from a URL:

```swift
// Does it hold non-Sendable state? → No (URLSession is Sendable)
// ❌ First condition fails → actor is not appropriate

@MainActor
class APIClient {
    func fetchUser(id: Int) async throws -> User {
        let (data, _) = try await URLSession.shared.data(from: url)
        return try JSONDecoder().decode(User.self, from: data)
    }
}
```

## Mental Model: Actors as Remote Services

Think of actors as remote network services:

- Data is physically inaccessible except through requests
- Inputs and outputs must be packaged (Sendable)
- Other requests can happen simultaneously
- All interaction is asynchronous

This metaphor clarifies why synchronous access is impossible and why Sendable boundaries matter.

## Scope

This skill covers custom actors and `@MainActor` for local concurrency. It does not cover `distributed actor`, which introduces network transparency and has different design considerations.

## Related Skills

- **avoiding-problematic-swift-concurrency-patterns** — Covers what goes wrong when actors are misused (stateless actors, actors conforming to synchronous protocols, etc.).
- **preventing-swift-logical-races** — Covers actor reentrancy bugs, which are a common surprise even when actors are the right choice.
- **conforming-protocols-with-swift-concurrency** — Use when an actor or @MainActor type needs to conform to nonisolated protocols like Equatable or Hashable.

# Logical Races and Reentrancy

Logical races occur when multiple asynchronous operations interleave in unexpected ways, causing incorrect state. Unlike data races (multiple threads accessing the same memory), logical races can occur even in single-threaded code with a runloop. This reference covers recognition and prevention strategies.

Source: Matt Massicotte, "Concurrency Step-by-Step: Stateful Systems", <https://www.massicotte.org/step-by-step-stateful-systems/>, accessed 2025-11-24.

## Contents

- [Understanding Logical Races](#understanding-logical-races)
- [Key Principle: Synchronous Critical Sections](#key-principle-synchronous-critical-sections)
- [Actor Reentrancy](#actor-reentrancy)
- [Migration Pitfalls: Completion Handlers → Async/Await](#migration-pitfalls-completion-handlers--asyncawait)
- [Debugging Technique: Artificial Delays](#debugging-technique-artificial-delays)
- [Recognition Checklist](#recognition-checklist)
- [Summary](#summary)

## Understanding Logical Races

### What They Are

Logical races happen when:
- An async operation can be "re-entered" before a previous invocation completes
- Multiple async calls interleave, causing operations to complete out of order
- State assumptions made before an `await` become invalid after it

### Example: The Classic UI Race

```swift
private func press() {
    Task {
        await system.toggleState()
        self.state = await system.state
    }
}
```

If the user taps twice quickly:
1. First tap: `toggleState` begins (slow)
2. Second tap: another `toggleState` begins (fast)
3. Second tap's read completes, UI updates
4. First tap finally completes, UI updates again—**reversing user intent**

## Key Principle: Synchronous Critical Sections

**The check must be synchronous.** Any state consultation that guards an async operation must happen before the first `await`.

### Correct Pattern

```swift
@State private var inProgress = false

private func press() {
    if inProgress { return }  // Synchronous guard
    self.inProgress = true

    Task {
        await system.toggleState()
        self.state = await system.state
        self.inProgress = false
    }
}
```

### Also Correct (Guard Inside Task)

```swift
private func press() {
    Task {
        if inProgress { return }  // Still synchronous within MainActor
        self.inProgress = true

        await system.toggleState()
        self.state = await system.state
        self.inProgress = false
    }
}
```

This works because the Task body runs on @MainActor—only one can execute synchronous code at a time.

### Incorrect Pattern

```swift
private func press() {
    Task {
        if inProgress { return }

        await system.prepare()  // ⚠️ State can change during this await!

        self.inProgress = true  // Too late—race condition exists
        // ...
    }
}
```

**Think of `await` as ending a critical section.** All state checks and modifications that must be atomic need to happen synchronously, before any suspension point.

## Actor Reentrancy

Actors protect against data races but **not** logical races. Actor methods can be called by multiple callers simultaneously.

### Vulnerable Actor Pattern

```swift
actor RemoteSystem {
    private var initialized = false

    func toggleState() async {
        await initializeIfNeeded()  // ⚠️ Multiple callers can reach here
        self.state.toggle()
    }
}
```

Multiple callers can invoke `toggleState()` concurrently. Both may see `initialized == false` and run initialization twice.

### Solutions for Actor Reentrancy

1. **Synchronous guards** (same as UI pattern):
   ```swift
   func toggleState() async {
       if isInitializing { return }
       isInitializing = true
       // ...
   }
   ```

2. **Async locks** for complex scenarios (e.g., `AsyncSemaphore`)

3. **Reconsider the design**: If struggling with actor reentrancy, verify an actor is actually needed. Sometimes simpler approaches work.

## Migration Pitfalls: Completion Handlers → Async/Await

Converting completion handlers to async/await is **not** purely syntactic. Critical semantic differences exist:

### Ordering Changes

**Completion handler version** (synchronous dispatch):
```swift
func toggleState(completionHandler: @escaping @Sendable () -> Void) {
    queue.async {
        self.state.toggle()
        completionHandler()
    }
}
```
The call to `toggleState` synchronously adds work to a queue, preserving call order.

**Async version**:
```swift
func toggleState() async {
    self.state.toggle()
}

await system.toggleState()
```
The `await` introduces a scheduling step—Tasks don't have FIFO semantics in the general case.

### Task Creation Delays

Wrapping code in `Task { }` introduces a scheduling delay that can widen race windows:

```swift
// Before: Synchronous call into system
system.toggleState {
    // callback
}

// After: Async scheduling required
Task {
    await system.toggleState()
}
```

The Task body doesn't run immediately—it must be scheduled.

## Debugging Technique: Artificial Delays

Insert random delays to expose latent races:

```swift
func randomDelay() {
    usleep((0..<1_000_000).randomElement()!)
}

private func press() {
    Task {
        randomDelay()  // Task start latency

        randomDelay()  // Before await
        await system.toggleState()
        randomDelay()  // After await

        randomDelay()  // Before next await
        let value = await system.state
        randomDelay()  // After await

        self.state = value
    }
}
```

These delays magnify real timing variations to make races more observable during testing.

## Recognition Checklist

When reviewing async code, watch for:

- [ ] Multiple invocations possible before completion (button taps, notifications)
- [ ] State checked before `await` but used after
- [ ] Assumptions about execution order across Tasks
- [ ] Actor methods with multiple `await` calls before state modification
- [ ] Migration from completion handlers that changed timing semantics

## Summary

| Concept | Key Point |
|---------|-----------|
| Logical race | State interleaving, not memory corruption |
| Critical section | Synchronous code before first `await` |
| Actor reentrancy | Actors prevent data races, not logical races |
| Migration risk | async/await has different ordering semantics |
| Single-threaded | MainActor code can still have logical races |

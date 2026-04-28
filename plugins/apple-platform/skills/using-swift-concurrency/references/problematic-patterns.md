# Problematic Patterns

Use this reference to recognize and fix common problematic patterns when using Swift Concurrency. These patterns are not inherently wrong but frequently lead to issues, compiler warnings, or unintended behavior.

Source: Matt Massicotte, <https://www.massicotte.org/problematic-patterns/>, accessed 2025-11-24.

## Contents

- [When to Apply This Reference](#when-to-apply-this-reference)
- [Pattern Quick Reference](#pattern-quick-reference)
- [Detailed Patterns](#detailed-patterns)
- [Non-Sendable Types with Async Methods](#non-sendable-types-with-async-methods)
- [Summary Checklist](#summary-checklist)

## When to Apply This Reference

- Reviewing or writing Swift code that uses async/await, actors, or Task
- Diagnosing Swift 6 concurrency warnings or errors
- Refactoring completion-handler code to async/await
- Deciding between structured and unstructured concurrency
- Working with MainActor isolation

## Pattern Quick Reference

| Pattern | Problem | Better Approach |
|---------|---------|-----------------|
| Split isolation | Mixed isolation domains in one type | Apply global actor to entire type |
| Task.detached | Loses priority and task-locals | Use nonisolated async functions |
| Stateless actors | No state to protect | Use nonisolated async functions |
| MainActor.run | Bypasses static isolation checking | Declare functions @MainActor |
| Blocking async work | Deadlock risk | Use await, never semaphores |
| Unstructured tasks | Manual cancellation, unclear flow | Prefer structured concurrency |

## Detailed Patterns

### Split Isolation

A type that mixes isolation domains internally:

```swift
// PROBLEMATIC: Split isolation
class SomeClass {
    var name: String           // non-isolated
    @MainActor var value: Int  // MainActor-isolated
}
```

**Why problematic**: If created off the MainActor, `value` becomes permanently inaccessible. The type isn't Sendable, preventing transfer back to MainActor.

**Fix**: Apply the global actor to the entire type:

```swift
@MainActor
class SomeClass {
    var name: String
    var value: Int
}
```

### Task.detached Misuse

Using `Task.detached` simply to run work off the MainActor:

```swift
// PROBLEMATIC: Task.detached for offloading
@MainActor
func doSomeStuff() {
    Task.detached {
        expensiveWork()
    }
}
```

**Why problematic**: Detached tasks lose priority inheritance and task-local values, not just isolation. This causes unexpected behavior.

**Fix**: Use a nonisolated async function with a regular Task:

```swift
@MainActor
func doSomeStuff() {
    Task {
        await expensiveWork()
    }
}

nonisolated func expensiveWork() async {
    // Work runs off MainActor
}
```

### Explicit Task Priorities

Setting explicit priorities without clear justification:

```swift
// QUESTIONABLE: Why not default priority?
Task(priority: .background) {
    await someWork()
}
```

**Why problematic**: Priority inversions are easy to introduce accidentally. The system handles priority inheritance well by default.

**Guideline**: Always document why the default priority is insufficient:

```swift
// Background because this is non-user-facing analytics upload
// that should yield to all interactive work
Task(priority: .background) {
    await uploadAnalytics()
}
```

### MainActor.run Overuse

Using `MainActor.run` when static isolation would work:

```swift
// PROBLEMATIC: Dynamic isolation
await MainActor.run {
    updateUI()
}
```

**Why problematic**: Bypasses compile-time isolation checking. The compiler cannot verify correct usage at call sites.

**Fix**: Declare the function with static isolation:

```swift
@MainActor
func updateUI() { ... }

// At call site - compiler enforces correctness
await updateUI()
```

### Stateless Actors

Actors with no instance properties:

```swift
// PROBLEMATIC: No state to protect
actor NetworkService {
    func fetchData() async -> Data { ... }
}
```

**Why problematic**: Actors exist to protect mutable state. Without state, the actor just adds overhead and serializes access unnecessarily.

**Fix**: Use a nonisolated async function or a struct with async methods:

```swift
struct NetworkService {
    func fetchData() async -> Data { ... }
}
```

### Redundant Sendable Conformances

Explicitly conforming global-actor-isolated types to Sendable:

```swift
// REDUNDANT: @MainActor types are already Sendable
@MainActor
class ViewModel: Sendable { }
```

**Why problematic**: May indicate confusion about how global actor isolation provides Sendability. Not wrong, but suspicious.

**Fix**: Remove redundant conformance:

```swift
@MainActor
class ViewModel { }  // Already Sendable
```

### @MainActor @Sendable Closures

Combining both attributes on closures:

```swift
// POTENTIALLY REDUNDANT (Swift 6+)
@MainActor @Sendable () -> Void
```

**Context**: In Swift 6, `@MainActor` closures are implicitly Sendable. The combination is only needed for Swift 5/Xcode 15 compatibility.

**For Swift 6 only**:
```swift
@MainActor () -> Void  // Sufficient
```

### Blocking for Async Work

Using DispatchSemaphore or DispatchGroup to wait on async work:

```swift
// DANGEROUS: Deadlock risk
let semaphore = DispatchSemaphore(value: 0)
Task {
    await someWork()
    semaphore.signal()
}
semaphore.wait()  // May deadlock
```

**Why problematic**: Swift's cooperative thread pool can deadlock if threads block waiting for async work that needs those same threads.

**Fix**: Stay in async context or restructure to avoid synchronous waiting:

```swift
// Option 1: Stay async
await someWork()

// Option 2: If sync API required, document the limitation
// and ensure caller is never on cooperative pool
```

### Too Much Code in Closures

Large closure bodies make concurrency diagnostics hard to understand:

```swift
// PROBLEMATIC: Hard to diagnose
someAsyncAPI { result in
    // 50+ lines of code
    // Where exactly is the warning?
}
```

**Fix**: Extract closure bodies into named functions:

```swift
func handleResult(_ result: Result) {
    // Clear isolation context
    // Easier to diagnose
}

someAsyncAPI { result in
    handleResult(result)
}
```

### Unstructured When Structured Would Work

Creating Tasks when structured concurrency is available:

```swift
// PROBLEMATIC: Unstructured without need
func process() async {
    Task {
        await stepOne()
    }
    Task {
        await stepTwo()
    }
}
```

**Why problematic**: Loses automatic cancellation propagation, makes control flow unclear, requires manual coordination.

**Fix**: Use structured concurrency:

```swift
func process() async {
    async let one = stepOne()
    async let two = stepTwo()
    await (one, two)  // Automatic cancellation if parent cancelled
}

// Or with TaskGroup for dynamic parallelism
await withTaskGroup(of: Void.self) { group in
    group.addTask { await stepOne() }
    group.addTask { await stepTwo() }
}
```

### @preconcurrency Import with Async Extensions

Adding async wrappers to types from @preconcurrency imports:

```swift
@preconcurrency import SomeFramework

extension SomeType {
    func doWork() async -> Result {
        await withCheckedContinuation { continuation in
            doWork { result in
                continuation.resume(returning: result)
            }
        }
    }
}
```

**Why problematic**: The async wrapper may run callbacks on different threads than the completion-handler version, changing semantics. The @preconcurrency silences warnings that would catch this.

**Guideline**: Verify the original API's threading guarantees before wrapping. Document any semantic changes.

### Actors Conforming to Synchronous Protocols

Making actors conform to protocols with synchronous requirements:

```swift
protocol DataProvider {
    func getData() -> Data  // Synchronous
}

// PROBLEMATIC: Can't call synchronously from outside
actor MyProvider: DataProvider {
    func getData() -> Data { ... }
}
```

**Why problematic**: Actor methods are inherently async from outside the actor. Synchronous protocol methods can only be called from within the actor itself, limiting usefulness.

**Fix**: Consider whether an actor is appropriate, or use nonisolated methods if the data access is truly safe:

```swift
actor MyProvider: DataProvider {
    private let cachedData: Data  // Immutable after init

    nonisolated func getData() -> Data {
        cachedData  // Safe because immutable
    }
}
```

### Obj-C to Async Translation Issues

Relying on compiler-generated async versions of Objective-C APIs:

```swift
// Compiler generates async version automatically
let result = await objcObject.fetchData()
```

**Why problematic**: Unless the Obj-C type is MainActor-isolated or Sendable, the translation may have different semantics and produce warnings without @preconcurrency.

**Guideline**: Only use auto-translated async APIs when the threading behavior is known. Prefer explicit wrappers when uncertain.

## Non-Sendable Types with Async Methods

Adding async methods to non-Sendable types without isolated parameters:

```swift
// PROBLEMATIC: Where does this run?
class MyClass {  // Not Sendable
    func doWork() async { ... }
}
```

**Why problematic**: Without isolated parameters, the async method's isolation is unclear. This usually produces warnings with strict checking enabled.

**Fix**: Use isolated parameters to make isolation explicit:

```swift
class MyClass {
    func doWork(isolation: isolated (any Actor)? = #isolation) async {
        // Runs on caller's isolation domain
    }
}
```

## Summary Checklist

When reviewing Swift Concurrency code, check for:

- [ ] Types with mixed isolation domains (split isolation)
- [ ] Task.detached used just for MainActor offloading
- [ ] Explicit priorities without documented justification
- [ ] MainActor.run instead of @MainActor declarations
- [ ] Actors without mutable instance state
- [ ] Semaphores or DispatchGroups waiting on async work
- [ ] Large closure bodies (extract to named functions)
- [ ] Unstructured tasks where structured would work
- [ ] Async extensions on @preconcurrency imported types
- [ ] Actors conforming to synchronous protocols

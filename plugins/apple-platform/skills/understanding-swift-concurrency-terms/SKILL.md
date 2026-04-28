---
name: understanding-swift-concurrency-terms
description: >
  Glossary of Swift Concurrency keywords, annotations, protocols, and concepts — including actor,
  async/await, Sendable, isolation, Task, TaskGroup, @MainActor, @globalActor, @concurrent,
  nonisolated, sending, structured concurrency, executors, and continuations. Use this skill whenever
  explaining or looking up Swift concurrency terminology, clarifying what a concurrency keyword or
  annotation means, understanding isolation rules, or distinguishing between related concurrency
  primitives. Covers Swift 5.5 through Swift 6.2.
---

# Understanding Swift Concurrency Terms

Use this glossary to look up Swift Concurrency keywords, annotations, protocols, and concepts. When a user asks what a concurrency term means, how two terms differ, or which annotation to use in a given situation, consult the definitions below and explain using the context provided here.

Definitions are grouped by category in the quick reference, then expanded alphabetically with code examples and SE proposal references.

## Quick Reference by Category

### Keywords

| Keyword | Purpose |
|---------|---------|
| `actor` | Define a reference type that protects mutable state |
| `async` | Mark a function as asynchronous (can suspend) |
| `await` | Mark a suspension point where actor isolation may change |
| `distributed` | Define an actor accessible across processes or devices |
| `isolated` | Define static isolation via a function parameter |
| `nonisolated` | Explicitly remove actor isolation from a declaration |
| `sending` | Express concurrent usage constraints on parameters/returns |

### Annotations & Modifiers

| Annotation | Purpose |
|------------|---------|
| `@concurrent` | Force async function to run on global executor (Swift 6.2+) |
| `@globalActor` | Mark an actor type as a global actor for annotation use |
| `@MainActor` | Apply MainActor isolation |
| `@preconcurrency` | Manage Swift 5/6 compatibility for concurrency |
| `@Sendable` | Mark function types as safe to pass across isolation |
| `@unchecked Sendable` | Disable compiler verification of Sendable conformance |
| `@isolated(any)` | Enable runtime inspection of a closure's static isolation |
| `@_inheritActorContext` | Apply isolation inheritance to closure parameters |
| `nonisolated(nonsending)` | Inherit caller's isolation at runtime (Swift 6.2+) |
| `nonisolated(unsafe)` | Opt out of Sendable checking for a specific declaration |

### Protocols

| Protocol | Purpose |
|----------|---------|
| `Actor` | Base protocol all actor types conform to |
| `AsyncIteratorProtocol` | Iterator for an `AsyncSequence` |
| `AsyncSequence` | Sequence whose values arrive over time |
| `Executor` / `SerialExecutor` | Control how and where actors execute code |
| `GlobalActor` | Protocol that global actors conform to |
| `Sendable` | Mark types as safe to use across isolation boundaries |
| `SendableMetatype` | Mark metatypes as safe across isolation (Swift 6.2+) |

### Types

| Type | Purpose |
|------|---------|
| `AsyncStream` / `AsyncThrowingStream` | Create an `AsyncSequence` from a closure or continuation |
| `CheckedContinuation` / `UnsafeContinuation` | Wrap callback-based code for async/await use |
| `Task` | Create a top-level context for async code |
| `TaskGroup` / `ThrowingTaskGroup` | Manage multiple structured child tasks |
| `TaskLocal` | Task-scoped value storage (analogous to thread-local) |

### Flow Control

| Construct | Purpose |
|-----------|---------|
| `async let` | Begin async work without immediate await |
| `for await` | Iterate over an `AsyncSequence` |
| `withTaskGroup` | Create a scope for structured child tasks |
| `withTaskCancellationHandler` | Register a handler invoked on task cancellation |

## Detailed Definitions

### actor (Keyword)

Defines a reference type that protects mutable state. Actors are the fundamental unit of isolation in Swift Concurrency.

```swift
actor Counter {
    private var value = 0
    func increment() { value += 1 }
}
```

**Introduced**: SE-0306 Actors

### Actor (Protocol)

Protocol that all actor types automatically conform to. Similar to `AnyObject` for classes. Primarily used for creating isolated parameters.

**Introduced**: SE-0306 Actors

### async / await (Keywords)

`async` marks a function that can suspend execution. `await` marks each suspension point — the place where control may yield and the executing context may change. After an `await`, code resumes on whatever executor the function is isolated to (e.g., back on the main actor for a `@MainActor` function).

```swift
func fetchData() async -> Data {
    await networkRequest()  // suspension point
}
```

**Introduced**: SE-0296 Async/await

### async let (Flow Control)

Begin asynchronous work without immediately awaiting the result. Useful for parallelizing slow operations.

```swift
async let image = downloadImage()
async let metadata = fetchMetadata()
let result = await (image, metadata)
```

**Introduced**: SE-0317 async let bindings

### AsyncSequence (Protocol)

A sequence whose values become available over time. Use `for-await` to consume.

```swift
for await value in asyncStream {
    process(value)
}
```

**Introduced**: SE-0298 Async/Await: Sequences

### AsyncStream / AsyncThrowingStream (Types)

Factory types for creating an `AsyncSequence` from imperative code. `AsyncStream` bridges callback-based or event-driven APIs into the async/await world without needing a full continuation.

```swift
let stream = AsyncStream<Int> { continuation in
    continuation.yield(1)
    continuation.yield(2)
    continuation.finish()
}
```

**Introduced**: SE-0314

### @concurrent (Annotation)

Forces an async function to run on the global executor rather than inheriting caller isolation. In Swift 6.2+, `nonisolated async` functions inherit caller isolation by default; `@concurrent` opts out of that behavior and runs the function concurrently.

```swift
@concurrent
func backgroundWork() async { }
```

**Introduced**: SE-0461

### Continuations (Types)

APIs for bridging callback-based code into async functions. Each continuation must be resumed exactly once — resuming zero times leaks the task, and resuming more than once is a programmer error.

- `withCheckedContinuation` / `withCheckedThrowingContinuation` — runtime checks for misuse (recommended)
- `withUnsafeContinuation` / `withUnsafeThrowingContinuation` — no runtime checks (for performance-critical paths)

```swift
func wrapped() async -> String {
    await withCheckedContinuation { continuation in
        legacyAPI { result in
            continuation.resume(returning: result)
        }
    }
}
```

**Introduced**: SE-0300

### distributed actor (Keyword)

Defines an actor whose methods can be called from another process, device, or machine. Distributed actors extend the actor model across network boundaries, with the transport layer abstracted behind an `ActorSystem`.

```swift
distributed actor Player {
    distributed func score() -> Int { 42 }
}
```

**Introduced**: SE-0336 Distributed Actor Isolation, SE-0344 Distributed Actor Runtime

### Default Isolation (Concept)

All declarations have a defined static isolation. Prior to Swift 6.2, the default was `nonisolated`. Swift 6.2 allows changing the default to `MainActor`, creating a language dialect where code semantics depend on this setting.

**Introduced**: SE-0466

### Executor / SerialExecutor (Protocols)

`Executor` is the base protocol for controlling where and how actors run their code. `SerialExecutor` is the refinement that guarantees mutual exclusion — all actor types use a serial executor to enforce isolation. Custom executors are rarely needed in typical development but allow advanced control over scheduling (e.g., running an actor on a specific dispatch queue).

**Introduced**: SE-0304, SE-0392 Custom Actor Executors

### Global Executor (Concept)

The executor for concurrent (non-actor-isolated) code. Unlike actor executors, it runs multiple things simultaneously. Code reaches it via `async let`, `TaskGroup`, or `@concurrent`.

**Introduced**: SE-0338

### GlobalActor (Protocol)

The protocol that all global actors conform to. Requires a `static var shared` property. Types annotated with `@globalActor` automatically conform to this protocol. `MainActor` is the most prominent global actor in the standard library.

**Introduced**: SE-0316

### @globalActor (Annotation)

Makes an actor type usable as an annotation for applying static isolation.

```swift
@globalActor
actor MyGlobalActor {
    static let shared = MyGlobalActor()
}

@MyGlobalActor
func isolatedFunction() { }
```

**Introduced**: SE-0316

### isolated (Keyword)

Defines static isolation through a function parameter. The most powerful but complex isolation mechanism.

```swift
func process(on actor: isolated MyActor) {
    // runs isolated to the passed actor
}
```

**Introduced**: SE-0313

### #isolation (Macro)

Returns the static isolation as `(any Actor)?`. Useful with isolated parameters or debugging.

```swift
print(#isolation)  // prints current isolation context
```

**Introduced**: SE-0420

### @isolated(any) (Annotation)

Enables runtime inspection of a function variable's static isolation. Often paired with `@_inheritActorContext`.

**Introduced**: SE-0431

### Isolation (Concept)

The core abstraction for thread-safety in Swift Concurrency. Every declaration has a static isolation domain — it is either isolated to a specific actor (meaning only that actor can access it synchronously) or `nonisolated` (meaning it has no actor protection). The compiler enforces isolation boundaries at compile time, requiring `await` for cross-isolation calls and `Sendable` for values that cross boundaries.

### @_inheritActorContext (Annotation)

Applies isolation inheritance to closure parameters, matching Task semantics.

```swift
func runLater(@_inheritActorContext operation: @escaping () async -> Void) { }
```

**Note**: Underscored attribute; formalization pending.

### @MainActor (Annotation)

References the shared MainActor instance. The most common global actor annotation.

```swift
@MainActor
class ViewController { }
```

**Introduced**: SE-0316

### nonisolated (Keyword)

Explicitly disables actor isolation for a declaration. Useful for running code off an actor.

```swift
actor MyActor {
    nonisolated func utility() -> String { "safe" }
}
```

**Introduced**: SE-0313

### nonisolated(nonsending) (Annotation)

Makes an async function inherit the caller's isolation. Avoids Sendable requirements. Settings-independent alternative to default isolation inheritance.

**Introduced**: SE-0461

### nonisolated(unsafe) (Annotation)

Opts a specific stored property or variable out of actor isolation and Sendable checking. More targeted than `@unchecked Sendable` — it applies to a single declaration rather than an entire type. Use sparingly for cases like module-level constants the compiler cannot prove are safe.

**Introduced**: SE-0412

### @preconcurrency (Annotation)

Manages compatibility between Swift 6 strict concurrency checking and pre-Swift 6 code. On an `import`, it suppresses Sendable warnings for types from that module. On a declaration, it defers concurrency checks to the caller's Swift version. Essential for libraries that need to support both Swift 5 and Swift 6 clients.

**Introduced**: SE-0337, SE-0423

### Region-Based Isolation (Concept)

Compiler analysis that relaxes Sendable requirements when usage patterns are provably safe within a function body. The `sending` keyword extends this power across function boundaries.

**Introduced**: SE-0414

### Sendable (Protocol)

Marker protocol indicating a type is safe to use across any isolation domain. Has no members but significant implications.

```swift
struct Point: Sendable {
    let x: Int
    let y: Int
}
```

**Introduced**: SE-0302

### SendableMetatype (Protocol)

Marker indicating a metatype is safe across isolation. Required after Swift 6.2 introduced isolated conformances.

**Introduced**: SE-0470

### @Sendable (Attribute)

The Sendable equivalent for function types (since functions cannot conform to protocols).

```swift
let closure: @Sendable () -> Void = { }
```

**Introduced**: SE-0302

### Structured Concurrency (Concept)

The principle that child tasks have a well-defined lifetime bounded by their parent scope. `async let` and `TaskGroup` create structured child tasks — they are automatically awaited (or cancelled) when their scope exits. This guarantees no task leaks and enables automatic cancellation propagation. In contrast, `Task { }` and `Task.detached { }` create unstructured tasks that live independently of any scope.

**Introduced**: SE-0304 Structured Concurrency

### sending (Keyword)

Expresses concurrent usage constraints in function signatures. Relaxes Sendable requirements by encoding behavior promises.

```swift
func transfer(sending value: NonSendableType) { }
```

**Introduced**: SE-0430

### Task (Type)

Creates an unstructured, top-level context for running async code. `Task { }` inherits the caller's actor isolation and priority. `Task.detached { }` inherits neither — it runs fully independently. Both support cancellation, priority, and result access via `task.value`.

```swift
let task = Task {
    await doWork()  // inherits caller's isolation
}
let result = await task.value
```

**Introduced**: SE-0304

### TaskGroup / ThrowingTaskGroup (Types)

Manage multiple structured child tasks for parallel execution. Created via `withTaskGroup` or `withThrowingTaskGroup`. Child tasks are automatically cancelled if the group scope exits early. Results can be collected by iterating the group as an `AsyncSequence`.

```swift
let results = await withTaskGroup(of: Int.self) { group in
    for item in items {
        group.addTask { await process(item) }
    }
    return await group.reduce(into: []) { $0.append($1) }
}
```

**Introduced**: SE-0304

### TaskLocal (Type)

Task-scoped value storage, analogous to thread-local values.

```swift
enum RequestContext {
    @TaskLocal static var id: String?
}
```

**Introduced**: SE-0311

### @unchecked Sendable (Annotation)

Disables compiler verification for a `Sendable` conformance. Use when thread-safety is implemented through mechanisms the compiler cannot verify (locks, atomics, immutable-after-initialization patterns). This is a promise to the compiler — if the implementation is not actually thread-safe, data races will occur at runtime.

```swift
class ThreadSafeCache: @unchecked Sendable {
    private let lock = NSLock()
    // ...
}
```

**Introduced**: SE-0302

### withTaskCancellationHandler (Function)

Registers a cancellation handler that runs immediately if the current task is cancelled — even if the task is suspended at an `await`. Useful for hooking cancellation into callback-based or external APIs.

```swift
await withTaskCancellationHandler {
    await longRunningWork()
} onCancel: {
    externalHandle.cancel()
}
```

**Introduced**: SE-0304

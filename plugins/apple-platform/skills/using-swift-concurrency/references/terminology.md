# Terminology

Use this reference to look up Swift Concurrency keywords, annotations, protocols, and concepts when working with Swift's structured concurrency system.

Source: Matt Massicotte, <https://www.massicotte.org/concurrency-glossary/>, accessed 2025-11-24.

## Contents

- [Quick Reference by Category](#quick-reference-by-category)
- [Detailed Definitions](#detailed-definitions)

## Quick Reference by Category

### Keywords

| Keyword | Purpose |
|---------|---------|
| `actor` | Define a reference type that protects mutable state |
| `async` | Mark a function as asynchronous (can use `await` internally) |
| `await` | Mark a suspension point where actor isolation may change |
| `isolated` | Define static isolation via a function parameter |
| `nonisolated` | Explicitly disable actor isolation for a declaration |
| `sending` | Express concurrent usage constraints on parameters/returns |

### Annotations

| Annotation | Purpose |
|------------|---------|
| `@concurrent` | Force async function to run on global executor (Swift 6.2+) |
| `@globalActor` | Mark an actor type as global for annotation use |
| `@MainActor` | Apply MainActor isolation |
| `@preconcurrency` | Manage Swift 5/6 compatibility for concurrency |
| `@Sendable` | Mark function types as thread-safe |
| `@unchecked` | Disable compiler checks for Sendable conformance |
| `@isolated(any)` | Enable runtime inspection of static isolation |
| `@_inheritActorContext` | Apply isolation inheritance to closure parameters |
| `nonisolated(nonsending)` | Inherit caller's isolation (Swift 6.2+) |
| `nonisolated(unsafe)` | Opt out of Sendable checking for a declaration |

### Protocols

| Protocol | Purpose |
|----------|---------|
| `Actor` | Base protocol all actor types conform to |
| `AsyncSequence` | Sequence whose values arrive over time |
| `Executor` | Control how actors execute code |
| `Sendable` | Mark types as safe to use across isolation boundaries |
| `SendableMetatype` | Mark metatypes as safe across isolation (Swift 6.2+) |

### Types

| Type | Purpose |
|------|---------|
| `Task` | Create top-level context for async code |
| `TaskGroup` | Manage multiple child tasks |
| `TaskLocal` | Task-scoped value storage (like thread-local) |
| Continuations | Wrap callback-based code for async/await use |

### Flow Control

| Construct | Purpose |
|-----------|---------|
| `async let` | Begin async work without immediate await |
| `for-await` | Iterate over AsyncSequence values |

### Compiler Settings and Feature Flags

| Setting or flag | Purpose |
|---|---|
| `DefaultActorIsolation` | Changes the default isolation for declarations, commonly to `MainActor` in UI-heavy targets |
| `InferIsolatedConformances` | Infers global-actor isolation on protocol conformances when possible |
| `NonisolatedNonsendingByDefault` | Makes nonisolated async functions inherit caller isolation by default |

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

`async` marks a function that can suspend. `await` marks suspension points where the executing actor may change.

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

### @concurrent (Annotation)

Forces an async function to run on the global executor rather than inheriting caller isolation. Required in Swift 6.2+ when `nonisolated async` functions inherit caller isolation by default.

```swift
@concurrent
func backgroundWork() async { }
```

**Introduced**: SE-0461

### Continuations

APIs for wrapping callback-based code into async functions:
- `withCheckedContinuation` / `withCheckedThrowingContinuation`
- `withUnsafeContinuation` / `withUnsafeThrowingContinuation`

```swift
func wrapped() async -> Result {
    await withCheckedContinuation { continuation in
        legacyAPI { result in
            continuation.resume(returning: result)
        }
    }
}
```

**Introduced**: SE-0300

### DefaultActorIsolation / Default Isolation (Concept)

All declarations have a defined static isolation. Prior to Swift 6.2, the default was `nonisolated`. Swift 6.2 allows changing the default to `MainActor`, creating a language dialect where code semantics depend on this setting.

**Introduced**: SE-0466

### Executor (Protocol)

Controls how actors execute their code. Rarely needed for typical development but available for advanced performance tuning.

**Introduced**: SE-0304

### Global Executor (Concept)

The executor for concurrent (non-actor-isolated) code. Unlike actor executors, it runs multiple things simultaneously. Code reaches it via `async let`, `TaskGroup`, or `@concurrent`.

**Introduced**: SE-0338

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

The abstraction over thread-safety that actors provide. Actors implement isolation, often via serial queues internally.

### InferIsolatedConformances (Feature Flag)

Allows the compiler to infer global-actor isolation for protocol conformances when the conforming type is isolated. This reduces boilerplate, but explicit isolated conformances are still useful when the compiler cannot infer the intended contract.

**Introduced**: SE-0470

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

### NonisolatedNonsendingByDefault (Feature Flag)

Makes nonisolated async functions inherit the caller's isolation unless marked otherwise. This is important for protocol design because async requirements can become much more flexible when they do not force values across isolation boundaries.

**Introduced**: SE-0461

### nonisolated(unsafe) (Annotation)

Opts a declaration out of Sendable checking. More targeted than `@unchecked Sendable` or preconcurrency imports.

**Introduced**: SE-0306

### @preconcurrency (Attribute)

Manages compatibility between Swift 6 concurrency code and pre-Swift 6 code. Essential for consuming or producing APIs across Swift versions.

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

### sending (Keyword)

Expresses concurrent usage constraints in function signatures. Relaxes Sendable requirements by encoding behavior promises.

```swift
func transfer(sending value: NonSendableType) { }
```

**Introduced**: SE-0430

### Task (Type)

Creates a top-level context for running async code. Supports cancellation, priority, and result access.

```swift
Task {
    await doWork()
}
```

**Introduced**: SE-0304

### TaskGroup (Type)

Manages multiple child tasks for parallel execution.

```swift
await withTaskGroup(of: Result.self) { group in
    for item in items {
        group.addTask { await process(item) }
    }
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

### @unchecked (Annotation)

Disables compiler verification for a Sendable conformance. Use when thread-safety is implemented through mechanisms the compiler cannot verify.

```swift
class ThreadSafeCache: @unchecked Sendable {
    private let lock = NSLock()
    // ...
}
```

**Introduced**: SE-0302

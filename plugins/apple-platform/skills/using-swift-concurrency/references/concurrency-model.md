# Swift Concurrency Model

Use this reference when reasoning about where async code runs, why a Sendable diagnostic appears, or how isolation settings affect concurrency behavior. For dated toolchain and availability facts, consult [feature status](../../modeling-swift-types-for-correctness/references/swift-feature-status.md) when needed.

## The core model

Swift concurrency is based on tasks, isolation domains, and suspension points.

- A task is a unit of asynchronous work.
- An actor or global actor serializes access to isolated state.
- `await` marks a possible suspension point. During suspension, other work can run, including work on the same actor.
- `Sendable` describes values that can be safely used across isolation domains.
- `sending` describes a one-way transfer of a value, including some non-Sendable values, when the caller gives up later access.

Do not reason in terms of “background thread” first. Reason in terms of isolation and executor inheritance.

## `nonisolated(nonsending)` default

With `NonisolatedNonsendingByDefault`, a nonisolated async function runs on the caller’s actor by default. It does not automatically hop to the global concurrent executor.

```swift
@MainActor
final class ImageViewModel {
    func refresh() async throws {
        let image = try await loader.loadImage()
        self.image = image
    }
}

struct ImageLoader {
    nonisolated func loadImage() async throws -> Image {
        // Under NonisolatedNonsendingByDefault, this inherits the caller isolation.
        // If called from MainActor, synchronous work here is MainActor work.
    }
}
```

This is often desirable because it avoids false data-race diagnostics for non-Sendable values that remain in the caller’s isolation. It also means CPU-heavy synchronous work in such a function can overhang the main actor.

Use this rule:

- If the function mostly awaits I/O and does little synchronous CPU work, inherited caller isolation is usually fine.
- If the function parses, decodes, hashes, compresses, transforms images, or does meaningful CPU work, consider `@concurrent` or an explicitly non-main isolated design.

## `@concurrent`

`@concurrent` on an async function means the call switches away from the caller’s actor and may run concurrently with other work on that actor.

```swift
struct ImageDecoder {
    @concurrent
    func decode(_ data: Data) async throws -> Image {
        try Task.checkCancellation()
        return try expensiveDecode(data)
    }
}
```

Use `@concurrent` when all are true:

1. The work should not run on the caller’s actor.
2. The inputs and outputs can safely cross the isolation boundary.
3. The function does not rely on actor-isolated or non-Sendable caller state.

Do not add `@concurrent` just because a function is async. Awaiting a URLSession request suspends instead of blocking the main actor; decoding the resulting bytes may still be CPU-heavy and should be evaluated separately.

## Task isolation inheritance

`Task { ... }` creates an unstructured task. It may inherit priority, task-local values, and actor context from where it is formed, but it is not a structured child task and does not create parent-child cancellation.

```swift
@MainActor
func tapped() {
    Task {
        // MainActor isolated because the task was formed in MainActor context.
        await refresh()
    }
}
```

`Task.detached { ... }` does not inherit actor context. It should capture only values that are safe to send.

```swift
Task.detached(priority: .background) { [payload] in
    await analytics.upload(payload)
}
```

Detached tasks are for intentionally independent work. They are not a general “run this in the background” tool.

## `Task.immediate`

`Task.immediate` is a standard-library API with iOS 26+/macOS 26+ runtime availability, not merely compiler syntax. Guard it or its containing declaration on older deployment targets. A normal `Task` is a fallback only when delayed scheduling preserves the contract; otherwise perform the required synchronous prefix directly before starting async work. See [Apple’s declaration](https://developer.apple.com/documentation/swift/task/immediate(name:priority:executorpreference:operation:)-88o80).

`Task.immediate` starts synchronously on the caller’s execution context until the task reaches an actual suspension point. It is still an unstructured task unless created through a task group immediate-child API.

```swift
@available(iOS 26.0, macOS 26.0, *)
@MainActor
func handleTapSynchronouslyEnough() {
    Task.immediate {
        state = .started       // Runs before returning if no suspension occurred.
        await refresh()        // After real suspension, interleaving is possible.
    }
}
```

Use `Task.immediate` sparingly:

- Good: preserving ordering when bridging from a synchronous callback already running on the correct actor into an async API.
- Good: avoiding a scheduling gap for a tiny actor-isolated state update before first suspension.
- Bad: hiding lifecycle ownership problems.
- Bad: doing CPU-heavy work before the first suspension on the main actor.
- Bad: making task-group child work unexpectedly serial by immediately executing too much of each child.

If a regular `Task` is sufficient, prefer it.

## Structured concurrency

Structured child tasks are created by `async let` and task groups. They have a bounded lifetime and cancellation relationship with the parent.

Use `async let` for a fixed small number of independent child operations:

```swift
async let profile = api.profile(id: id)
async let avatar = api.avatar(id: id)
let user = try await User(profile: profile, avatar: avatar)
```

Use a task group for dynamic parallelism:

```swift
let thumbnails = try await withThrowingTaskGroup(of: Thumbnail.self) { group in
    for item in items {
        group.addTask {
            try await renderer.thumbnail(for: item)
        }
    }

    var result: [Thumbnail] = []
    for try await thumbnail in group {
        result.append(thumbnail)
    }
    return result
}
```

Task-group closures are sending/Sendable boundaries. Do not capture non-Sendable mutable objects unless the compiler proves a safe transfer or the value is actor-isolated in a compatible way.

## Isolated parameters

An `isolated` parameter lets a function run in an actor’s isolation domain for the duration of the call, reducing repeated `await`s and allowing atomic synchronous sections.

```swift
actor Database {
    private var pending: [Mutation] = []

    func enqueue(_ mutation: Mutation) {
        pending.append(mutation)
    }

    func flush() async throws { }
}

func prepareBatch(on database: isolated Database, mutations: [Mutation]) {
    for mutation in mutations {
        database.enqueue(mutation) // No await; same actor isolation.
    }
}
```

Use isolated parameters for scoped access to an actor. Do not store isolated parameters or let them escape.

## `#isolation`

`#isolation` captures the caller’s current isolation. It is useful in APIs that need to inherit caller isolation explicitly, especially generic or higher-order APIs.

```swift
final class Loader {
    func load(
        isolation: isolated (any Actor)? = #isolation
    ) async throws -> Value {
        // Executes in caller isolation when provided by the caller.
    }
}
```

With `NonisolatedNonsendingByDefault`, many ordinary async functions no longer need this boilerplate. Keep it for APIs where inherited isolation is part of the explicit API design or where higher-order function values would otherwise lose important isolation information.

## `sending`

`sending` marks a transfer. The caller must not use the transferred value afterward if doing so could race.

```swift
func store(_ value: sending NonSendablePayload) async {
    await actor.store(value)
}
```

Use `sending` when the API consumes or returns ownership across an isolation boundary. Do not use it to paper over shared mutable aliasing; after sending, the old region is no longer yours to use.

## Region-based isolation

Swift can sometimes prove that a non-Sendable value can be moved between tasks or actors because no concurrent alias remains. This is region-based isolation.

Practical rules:

- A freshly created non-Sendable value may be transferable if it has no other aliases.
- Capturing a non-Sendable value in a task may be allowed if the value is transferred and not used afterward.
- Reusing the value after transfer can produce a diagnostic.
- Region isolation is not a substitute for designing clear ownership.

When diagnostics mention “task-isolated value,” “sending parameter,” or “later accesses,” look for hidden aliases and post-transfer uses.

## Global actor isolated closures

A global-actor-isolated closure is effectively safe to send because it always executes on that actor.

```swift
let update: @MainActor () -> Void = {
    model.count += 1
}

Task {
    await update()
}
```

In Swift 6 language mode, the global actor annotation normally supplies the closure's inferred sendability. Write `@MainActor @Sendable` explicitly when the API contract or a generic/storage context needs it.

## Where code runs: quick table

| Code | Expected execution behavior |
|---|---|
| `@MainActor func f()` | Runs on MainActor. |
| Unannotated declaration in `-default-isolation MainActor` module | Inferred MainActor unless another rule/annotation applies. |
| `nonisolated func f()` synchronous | Runs in caller context; no actor isolation is promised by the declaration. |
| `nonisolated func f() async` with `NonisolatedNonsendingByDefault` | Runs on caller actor by default. |
| `@concurrent func f() async` | Switches off caller actor; inputs/results need safe transfer. |
| `Task {}` inside MainActor context | Usually MainActor-isolated task body. |
| `Task.detached {}` | No actor inheritance; global executor unless explicitly isolated in closure. |
| `Task.immediate {}` | Begins immediately on caller context until actual suspension. |
| `async let` | Structured child task. |
| `TaskGroup.addTask` | Structured child task; closure is a sending boundary. |

## Review checklist

- Did an async function accidentally start doing CPU work on MainActor because `nonisolated(nonsending)` is active?
- Is `@concurrent` justified by real parallel/off-actor work and safe transfers?
- Is `Task.immediate` required for ordering, or would `Task` be safer?
- Are non-Sendable values transferred once, not shared concurrently?
- Are isolated parameters scoped and non-escaping?
- Are task-group captures Sendable or proven safe by region isolation?

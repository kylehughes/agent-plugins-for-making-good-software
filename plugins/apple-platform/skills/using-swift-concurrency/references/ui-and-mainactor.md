# UI and MainActor

Use this reference for SwiftUI, UIKit, view models, presentation state, UI callbacks, and app targets with `-default-isolation MainActor`.

## Default UI rule

UI state belongs to `MainActor`. Prefer static isolation:

```swift
@MainActor
final class SearchViewModel: ObservableObject {
    @Published private(set) var results: [SearchResult] = []
    @Published private(set) var isLoading = false
}
```

Do not rely on `DispatchQueue.main.async`, `MainActor.run`, `Thread.isMainThread`, or runtime assertions when a declaration can be statically `@MainActor`.

## Deployment target and observation

For iOS 16 support, `ObservableObject` and `@Published` remain the safest baseline.

```swift
@MainActor
final class SettingsViewModel: ObservableObject {
    @Published var displayName = ""
}
```

Use Observation (`@Observable`) only when the code is iOS 17+ or availability-gated:

```swift
@available(iOS 17, *)
@Observable
@MainActor
final class SettingsModel {
    var displayName = ""
}
```

Do not introduce `@Observable` unconditionally into a code path that must run on iOS 16.

## UI target default actor isolation

When a UI module uses `-default-isolation MainActor`, unannotated declarations become main-actor isolated unless annotated otherwise. This is useful for UI but harmful for DTOs, persistence models, and utility algorithms.

Mark non-UI declarations explicitly:

```swift
nonisolated struct UserDTO: Sendable, Codable, Identifiable {
    let id: UUID
    let name: String
}

nonisolated enum SearchState: Sendable, Equatable {
    case idle
    case loading
    case loaded([SearchResult])
    case failed(String)
}
```

If a UI target accumulates many `nonisolated` model declarations, move those declarations to a domain package with nonisolated default isolation.

## View-model task ownership

A UI action that starts asynchronous work needs a task owner. Store and cancel task handles for work that can outlive the initiating call.

```swift
@MainActor
final class SearchViewModel: ObservableObject {
    @Published private(set) var results: [SearchResult] = []
    @Published private(set) var isLoading = false

    private let service: SearchService
    private var searchTask: Task<Void, Never>?

    init(service: SearchService) {
        self.service = service
    }

    func search(query: String) {
        searchTask?.cancel()
        searchTask = Task { [weak self] in
            guard let self else { return }
            await self.runSearch(query: query)
        }
    }

    private func runSearch(query: String) async {
        isLoading = true
        defer {
            if !Task.isCancelled { isLoading = false }
        }

        do {
            let updatedResults = try await service.search(query: query)
            guard !Task.isCancelled else { return }
            results = updatedResults
        } catch is CancellationError {
            // Leave current state or set an explicit cancelled state.
        } catch {
            guard !Task.isCancelled else { return }
            results = []
        }
    }

    deinit {
        searchTask?.cancel()
    }
}
```

Weak capture only defers the strong reference: the awaited instance call above retains its owner until `runSearch` returns. Cancel finite search work from the owning lifecycle when required; do not rely solely on `deinit` to cancel an operation that itself keeps the owner alive. If the task is strictly view-lifecycle-managed by SwiftUI `.task`, weak capture may be unnecessary.

## SwiftUI `.task` versus manual tasks

Prefer `.task` or `.task(id:)` when work is tied to a view’s presence:

```swift
struct ProfileView: View {
    @StateObject private var model: ProfileViewModel

    var body: some View {
        content
            .task(id: model.userID) {
                await model.load()
            }
    }
}
```

SwiftUI cancels the task when the view disappears or the `id` changes. The view model should still handle cancellation correctly.

Use manual task handles when work is tied to a user intent rather than a view lifecycle, such as search debouncing, upload, login, or retry.

## UIKit callbacks

UIKit callbacks are main-thread/UI callbacks, but legacy delegate protocols may not be annotated to express that. Prefer isolating the conforming type and crossing into async code explicitly.

```swift
@MainActor
final class ViewController: UIViewController {
    private let model: ScreenViewModel
    private var task: Task<Void, Never>?

    override func viewDidLoad() {
        super.viewDidLoad()
        task = Task { [model] in
            await model.load()
        }
    }

    deinit {
        task?.cancel()
    }
}
```

If a delegate method is nonisolated by protocol requirement, use an isolated conformance when available, make the delegate adapter nonisolated and forward safely, or use a tiny `Task { @MainActor in ... }` bridge. Do not mark the whole app as `@preconcurrency` to avoid one delegate diagnostic.

## MainActor and CPU work

Awaiting does not block the main actor. Synchronous work does.

Problem:

```swift
@MainActor
func load() async throws {
    let (data, _) = try await URLSession.shared.data(from: url)
    self.image = try decodeLargeImage(data) // CPU work on MainActor.
}
```

Better:

```swift
@MainActor
func load() async throws {
    let (data, _) = try await URLSession.shared.data(from: url)
    self.image = try await decoder.decode(data)
}

struct ImageDecoder: Sendable {
    @concurrent
    func decode(_ data: Data) async throws -> Image {
        try Task.checkCancellation()
        return try decodeLargeImage(data)
    }
}
```

Do not use `Task.detached` as the first fix for CPU work. Prefer a well-scoped `@concurrent` async function or a dedicated worker abstraction with Sendable inputs and outputs.

## `MainActor.run`

`MainActor.run` is a bridge, not a design pattern.

Acceptable:

```swift
func legacyCallback(_ value: Value) {
    Task {
        await MainActor.run {
            model.value = value
        }
    }
}
```

Prefer:

```swift
@MainActor
func apply(_ value: Value) {
    model.value = value
}

func legacyCallback(_ value: Value) {
    Task { await apply(value) }
}
```

The second shape gives the compiler a reusable isolation contract.

## UI state after suspension

Every `await` can stale out UI assumptions.

Problem:

```swift
@MainActor
func save() async {
    guard canSave else { return }
    let payload = draft
    try? await service.save(payload)
    draft = .empty // May clear newer edits.
}
```

Better:

```swift
@MainActor
func save() async {
    guard canSave else { return }
    let payload = draft
    let version = draftVersion
    isSaving = true
    defer { isSaving = false }

    do {
        try await service.save(payload)
        if draftVersion == version {
            draft = .empty
        }
    } catch {
        if draftVersion == version {
            errorMessage = error.localizedDescription
        }
    }
}
```

Use identity/version tokens, cancellation, or in-progress guards to prevent stale completions from overwriting newer user intent.

## Deinitialization and cleanup

For UI types, prefer explicit cancellation/cleanup methods plus `deinit` cancellation of task handles. Avoid starting new tasks from `deinit` that capture `self`.

If `deinit` must touch isolated state or main-thread-only APIs, use Swift’s isolated deinit support when appropriate, or move cleanup earlier into an explicit `close`, `invalidate`, or lifecycle method.

```swift
@MainActor
final class ObserverOwner {
    private let events: AsyncStream<Int>
    private var task: Task<Void, Never>?
    private(set) var latestValue: Int?

    init(events: AsyncStream<Int>) { self.events = events }

    func start() {
        task?.cancel()
        let events = events
        task = Task { [weak self] in
            for await value in events {
                guard !Task.isCancelled else { break }
                self?.latestValue = value
            }
        }
    }

    func stop() {
        task?.cancel()
        task = nil
    }

    deinit { task?.cancel() }
}

```

## UI review checklist

- Is the view model/controller type-level `@MainActor`?
- Are DTOs and pure models accidentally main-actor isolated by default settings?
- Does every user action task have a cancellation/ownership story?
- Are stale UI completions prevented with cancellation, versioning, or synchronous guards?
- Is CPU-heavy synchronous work moved out of MainActor with `@concurrent` or another explicit design?
- Is `@Observable` availability compatible with iOS 16?
- Are `MainActor.run`, `Task { @MainActor in }`, and `DispatchQueue.main.async` used only as boundaries from legacy code?

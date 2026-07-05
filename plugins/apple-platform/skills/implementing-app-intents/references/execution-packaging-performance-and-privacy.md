# Execution, Packaging, Performance, and Privacy

## Execution surfaces

The same intent may run from Siri, Shortcuts, Spotlight, widgets, controls, Live Activities, the Action button, the app UI, an App Intents extension, a WidgetKit extension, or the main app process. Design each intent with explicit execution expectations.

## Foreground vs background

Background-friendly intents:

- Query data.
- Create simple local objects.
- Toggle simple state.
- Start/stop timers.
- Mark complete/archive.
- Return search results.
- Export existing safe files.

Foreground-required intents:

- Rich editing.
- Complex authentication.
- Visual preview inspection.
- Multi-step workflows.
- Permissions prompts that require UI.
- Operations only your active scene can perform.

```swift
struct EditCanvasIntent: AppIntent, ForegroundContinuableIntent {
    static let title: LocalizedStringResource = "Edit Canvas"

    @Parameter var canvas: CanvasEntity

    @MainActor
    func perform() async throws -> some IntentResult {
        if needsForegroundEditor {
            try await continueInForeground()
        }
        try await CanvasRouter.shared.openEditor(canvas.id)
        return .result()
    }
}
```

## Supported modes and current mode

Use execution-mode APIs to adapt behavior.

```swift
func perform() async throws -> some IntentResult {
    switch SystemIntentContext.current.currentMode {
    case .foreground:
        return try await performWithUIAvailable()
    case .background:
        if canFinishInBackground {
            return try await performHeadless()
        } else {
            try await continueInForeground()
            return try await performWithUIAvailable()
        }
    default:
        return try await performSafely()
    }
}
```

Exact enum/type names can shift. Preserve the behavior: detect whether foreground continuation is available, continue only when needed, and handle denial.

## TargetContentProvidingIntent

Use when the intent should be delivered to a specific visible view/scene/content target.

Use cases:

- Scroll current document.
- Apply action to visible canvas selection.
- Change current editor mode.
- Insert content into active note.
- Navigate within active tab/window.

```swift
struct InsertIntoCurrentDocumentIntent: AppIntent, TargetContentProvidingIntent {
    static let title: LocalizedStringResource = "Insert Into Current Document"

    @Parameter(title: "Text")
    var text: AttributedString

    func perform() async throws -> some IntentResult {
        return .result()
    }
}

DocumentEditor(document: document)
    .onAppIntentExecution(InsertIntoCurrentDocumentIntent.self) { intent in
        editor.insert(intent.text)
    }
```

Rules:

- Use for active-view semantics, not global actions.
- Multiple views may respond; scope carefully.
- Keep target state synchronized with onscreen annotations.
- Use external-event routing when scene routing is needed.

## UIKit scene execution and navigation

SwiftUI’s `.onAppIntentExecution` is not the UIKit navigation model. For UIKit on iOS 26+, use one of these scene-aware paths:

- Conform an appropriate intent to `UISceneAppIntent` and implement `performNavigation(forScene:)`.
- Conform the scene delegate to `AppIntentSceneDelegate` and route the supplied `any UISceneAppIntent` through the scene’s coordinator.

Choose one owner per intent type. A custom `performNavigation(forScene:)` intent must be ignored by the scene-delegate route mapper; a delegate-routed intent must not also navigate in a custom implementation.

```swift
@MainActor
final class SceneDelegate: UIResponder, UIWindowSceneDelegate, AppIntentSceneDelegate {
    var coordinator: SceneCoordinator!

    func scene(_ scene: UIScene, willPerformAppIntent appIntent: any UISceneAppIntent) {
        guard let route = IntentRouteMapper.route(for: appIntent) else { return }
        coordinator.route(route)
        // Do not call appIntent.perform(). The framework owns execution.
    }
}
```

Cold launch may expose the triggering intent through `UIScene.ConnectionOptions.appIntent`; Apple also delivers the scene-delegate App Intent callback after connection. Build the scene in `willConnectTo`, then route once. Deduplicate if connection options are also used for initial state.

Keep a coordinator per scene. Never select `connectedScenes.first`, retain one global navigation controller, or assume the key window belongs to the intended account/document. See [uikit-integration.md](uikit-integration.md).

## OpensIntent

```swift
struct CreateAndOpenProjectIntent: AppIntent {
    @Parameter var name: String

    func perform() async throws -> some IntentResult & OpensIntent {
        let project = try await ProjectRepository.shared.create(name: name)
        return .result(opensIntent: OpenProjectIntent(target: project))
    }
}
```

Use when creation/search should end by opening the created/found content.

## Long-running work and cancellation

`ProgressReportingIntent` is available since iOS 17 and is the shipping tool for bounded progress. `LongRunningIntent` and `CancellableIntent` are absent from the iPhoneOS 26.5 SDK. Do not reference them in source compiled by that SDK.

For work beyond normal intent limits, design the domain service now:

- Idempotent job creation.
- Durable job state where needed.
- Cooperative cancellation through `Task.checkCancellation()` and service-level cancellation tokens.
- Temporary-file cleanup.
- Retry safety.
- Foreground continuation when the work genuinely requires app UI.

Forward-looking wrapper shape, not buildable with iPhoneOS 26.5:

```swift
// Forward-looking / selected-SDK-gated only.
struct ExportLargeProjectIntent: AppIntent, LongRunningIntent, ProgressReportingIntent, CancellableIntent {
    // Use only when the selected SDK declares these protocols.
}
```

Use long-running APIs, if present in a future selected SDK, for large exports/imports, video processing, ML analysis, sync repair, file conversion, and batch operations. Report progress, support cancellation, persist job state, and avoid duplicate work after retries.

## ProgressReportingIntent

```swift
struct BatchArchiveIntent: AppIntent, ProgressReportingIntent {
    @Parameter var tasks: [TaskEntity]

    func perform() async throws -> some IntentResult & ProvidesDialog {
        let total = tasks.count
        for (index, task) in tasks.enumerated() {
            try Task.checkCancellation()
            try await TaskRepository.shared.archive(task.id)
            progress.completedUnitCount = Int64(index + 1)
            progress.totalUnitCount = Int64(total)
        }
        return .result(dialog: "Archived \(total) tasks.")
    }
}
```

Use bounded progress units. Do not fake progress for unknown-duration operations.

## Cancellation without CancellableIntent

`CancellableIntent` is absent from the iPhoneOS 26.5 SDK. Still make every async intent cancellation-cooperative:

```swift
struct AnalyzeVideoIntent: AppIntent {
    @Parameter var video: VideoEntity

    func perform() async throws -> some IntentResult {
        try Task.checkCancellation()
        try await VideoAnalyzer.shared.analyze(
            video.id,
            cancellation: { Task.isCancelled }
        )
        try Task.checkCancellation()
        return .result()
    }
}
```

Check cancellation in loops, pass cancellation to services, clean temporary files, and never report success after cancellation.

## Background GPU work

For selected SDKs/platforms with background GPU support:

- Declare the proper capability.
- Use long-running semantics only when the selected SDK declares them; otherwise use progress, foreground continuation, and durable jobs.
- Keep work bounded.
- Respect energy and thermal pressure.
- Degrade gracefully when unavailable.
- Test on device.

Good uses: video/image processing, local ML inference, OCR, embedding/index generation. Bad uses: analytics, cosmetic processing, unbounded loops, or precomputable work.

## ExecutionTargets

`ExecutionTargets` is absent from the iPhoneOS 26.5 SDK. Do not declare it for code compiled by that SDK.

Until a selected SDK provides an execution-target declaration API, document the intended process boundary explicitly and enforce it through target membership and dependency design:

```text
Intent can run in app process only:
  - may use main-actor scene router after foreground continuation/open
  - must not be linked into WidgetKit-only extension targets

Intent can run in App Intents extension:
  - dependencies must be extension-safe
  - no UIKit scene/router dependency

Intent can run in WidgetKit extension:
  - small, deterministic mutation only
  - shared app group storage where required
```

Forward-looking wrapper shape, not buildable with iPhoneOS 26.5:

```swift
// Forward-looking / selected-SDK-gated only.
static var allowedExecutionTargets: ExecutionTargets {
    ExecutionTargets {
        .widgetKitExtension
        .appIntentsExtension
    }
}
```

## Dependencies

```swift
final class AppIntentServices: Sendable {
    let tasks: TaskRepository
    let navigator: AppNavigator
}

@main
struct ExampleApp: App {
    init() {
        AppDependencyManager.shared.add(dependency: AppIntentServices(
            tasks: .shared,
            navigator: .shared
        ))
    }

    var body: some Scene { WindowGroup { RootView() } }
}

struct CompleteTaskIntent: AppIntent {
    @Dependency var services: AppIntentServices

    @Parameter var task: TaskEntity

    func perform() async throws -> some IntentResult {
        try await services.tasks.complete(task.id)
        return .result()
    }
}
```

Dependencies must be available in the process/extension where the intent runs. Avoid app-only singletons in extension-capable intents. Use actors or Sendable services. Keep UI routers main-actor and app-process-only.

## AppIntentsPackage

`AppIntentsPackage` is available since iOS 17. If the app supports iOS 16.x devices, intents defined only in Swift packages are not discoverable through `AppIntentsPackage` on those devices even though core `AppIntent`/`AppEntity` protocols exist. Keep iOS 16-critical intents in an app target or accept an effective App Intents package-discovery floor of iOS 17.

```swift
public struct ProjectIntentPackage: AppIntentsPackage {
    public static var includedPackages: [any AppIntentsPackage.Type] {
        [SharedDocumentIntentPackage.self]
    }
}
```

Use for intents/entities in Swift packages or static libraries on iOS 17+. Ensure the app target imports the package and test discovery from the final app bundle on the oldest supported OS.

## Concurrency

Guidelines:

- Use actors for mutable shared state.
- Mark UI navigation `@MainActor`.
- Avoid blocking calls in `perform()`.
- Use `Task.checkCancellation()` in long loops.
- Pass cancellation to URLSession/file operations.
- Keep entity values `Sendable`.
- Do not store non-Sendable framework objects inside entities.

## Performance budgets

| Operation | Target |
| --- | --- |
| Entity ID lookup | <100 ms local, <500 ms with sync fallback |
| Suggested entities | <200 ms |
| String query | <300 ms local/indexed |
| Simple App Shortcut | <500 ms |
| Snippet render | visually immediate; fetch in perform, not body |
| OpenIntent navigation | immediate route after activation |
| Long-running startup | quick start + progress |

If an operation cannot meet these, use indexing, caching, deferred properties, foregrounding, progress, or long-running APIs.

## Privacy rules

App Intents expose app data to system surfaces. Treat every property as user-visible unless proven otherwise.

Do not expose access tokens, server-only IDs, hidden/deleted/locked content, private messages without consent, enterprise-restricted data, internal file paths, debug metadata, security settings, or content from signed-out accounts.

Be careful with display subtitles, indexed text, Transferable exports, snippet views, donations, notification annotations, lock-screen shortcuts, widgets, and controls.

## Lock screen behavior

For actions available while locked:

- Keep output private by default.
- Require unlock for sensitive content.
- Do not speak sensitive titles aloud unless safe.
- Avoid transferring private data while locked.
- Use confirmation/authentication where necessary.

## Error and retry semantics

Intent execution may be retried or resumed. Design for idempotency, duplicate submission protection, transactional mutations, stale IDs, deleted content, permission changes, network unavailability, and app migration in progress.

## Production readiness

Before shipping:

- Run XCTest/manual system-surface coverage; run AppIntentsTesting only if the selected SDK provides that framework.
- Validate manual system surfaces.
- Test fresh install and upgrade.
- Test account switch/sign-out.
- Test disabled search/suggestions.
- Test locked device behavior.
- Test large libraries.
- Test no-network behavior.
- Test cancellation.
- Test old shortcuts after app update.
- Audit all indexed/transferred fields.

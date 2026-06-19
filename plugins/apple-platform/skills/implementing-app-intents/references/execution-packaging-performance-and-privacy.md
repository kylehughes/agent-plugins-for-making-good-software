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

## LongRunningIntent

For work beyond normal intent time limits, use long-running APIs when available.

```swift
@available(iOS 27, *)
struct ExportLargeProjectIntent: AppIntent, LongRunningIntent, ProgressReportingIntent, CancellableIntent {
    static let title: LocalizedStringResource = "Export Project"

    @Parameter var project: ProjectEntity

    func perform() async throws -> some ReturnsValue<IntentFile> & ProvidesDialog {
        try await performBackgroundTask { progress in
            let file = try await ProjectExporter.shared.export(
                project.id,
                progress: progress,
                cancellation: { Task.isCancelled }
            )
            return .result(value: file, dialog: "Exported \(project.name).")
        }
    }

    func onCancel() async {
        await ProjectExporter.shared.cancel(project.id)
    }
}
```

Use for large exports/imports, video processing, ML analysis, sync repair, file conversion, and batch operations. Report progress, support cancellation, persist job state, and avoid duplicate work after retries.

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

## CancellableIntent

```swift
struct AnalyzeVideoIntent: AppIntent, CancellableIntent {
    @Parameter var video: VideoEntity

    func perform() async throws -> some IntentResult {
        try await VideoAnalyzer.shared.analyze(video.id)
        return .result()
    }

    func onCancel() async {
        await VideoAnalyzer.shared.cancel(video.id)
    }
}
```

Check cancellation in loops, pass cancellation to services, clean temporary files, and never report success after cancellation.

## Background GPU work

For iOS 27-era SDKs/platforms with background GPU support:

- Declare the proper capability.
- Use long-running semantics.
- Keep work bounded.
- Respect energy and thermal pressure.
- Degrade gracefully when unavailable.
- Test on device.

Good uses: video/image processing, local ML inference, OCR, embedding/index generation. Bad uses: analytics, cosmetic processing, unbounded loops, or precomputable work.

## ExecutionTargets

Declare where an intent may run.

```swift
@available(iOS 27, *)
struct ToggleWidgetStateIntent: AppIntent {
    static let title: LocalizedStringResource = "Toggle Widget State"

    static var allowedExecutionTargets: ExecutionTargets {
        ExecutionTargets {
            .widgetKitExtension
            .appIntentsExtension
        }
    }

    func perform() async throws -> some IntentResult {
        try await WidgetStateStore.shared.toggle()
        return .result()
    }
}
```

| Target | Use when | Avoid when |
| --- | --- | --- |
| Main app | UI/navigation, app-only state, foreground workflows | Simple headless operations |
| App Intents extension | Headless actions, shared repositories, Siri/Shortcuts | Needs active scene or app-only singleton |
| WidgetKit extension | Widget/control-local state | Needs full navigation or long work |

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

```swift
public struct ProjectIntentPackage: AppIntentsPackage {
    public static var includedPackages: [any AppIntentsPackage.Type] {
        [SharedDocumentIntentPackage.self]
    }
}
```

Use for intents/entities in Swift packages or static libraries. Ensure the app target imports the package and test discovery from the final app bundle.

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

- Run AppIntentsTesting coverage.
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

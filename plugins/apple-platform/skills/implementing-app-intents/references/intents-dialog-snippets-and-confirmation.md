# Intents, Dialog, Snippets, and Confirmation

## AppIntent baseline

An `AppIntent` is one typed action.

```swift
struct CreateTaskIntent: AppIntent {
    static let title: LocalizedStringResource = "Create Task"
    static let description = IntentDescription("Creates a task in the app.")

    @Parameter(title: "Title", requestValueDialog: "What should the task be called?")
    var title: String

    @Parameter(title: "Project")
    var project: ProjectEntity?

    static var parameterSummary: some ParameterSummary {
        Summary("Create \(\.$title)") {
            \.$project
        }
    }

    func perform() async throws -> some ReturnsValue<TaskEntity> & ProvidesDialog {
        let task = try await TaskRepository.shared.create(title: title, project: project)
        return .result(value: task, dialog: "Created \(task.title).")
    }
}
```

Rules:

- One intent = one user-meaningful action.
- Parameters should be typed, not stringly parsed commands.
- Required parameters need request dialogs and parameter summaries.
- Optional parameters need sensible behavior when omitted.
- Result values should be typed when the action creates, finds, updates, or returns content.
- Destructive/sensitive/ambiguous actions need confirmation.
- Foreground only when UI is truly required.

## Parameter summary

Spotlight and Shortcuts discovery depend on parameter summaries.

```swift
static var parameterSummary: some ParameterSummary {
    Summary("Move \(\.$task) to \(\.$destination)")
}
```

Rules:

- Include all required parameters unless defaulted.
- Keep summaries short and readable.
- Hide advanced optional parameters in the trailing parameter block.
- Avoid summaries that hide required context.

## OpenIntent

Use for entities that can be opened from Spotlight, Siri, snippets, widgets, controls, or Visual Intelligence results. In UIKit, deliver navigation to the system-selected scene with `UISceneAppIntent` or `AppIntentSceneDelegate`, then route through that scene’s coordinator.

```swift
struct OpenProjectIntent: OpenIntent {
    static let title: LocalizedStringResource = "Open Project"

    @Parameter(title: "Project")
    var target: ProjectEntity

    func perform() async throws -> some IntentResult {
        // SwiftUI or UIKit scene handling performs navigation.
        return .result()
    }
}
```

Guidelines:

- Navigate, do not mutate.
- Use `@MainActor` when touching UI.
- Handle deleted/missing entities gracefully.
- Route to the correct scene/window when the app supports multiple windows.
- Use target-content handling when the action is meant for a currently visible scene/view.

## Create intent

```swift
struct CreateProjectIntent: AppIntent {
    static let title: LocalizedStringResource = "Create Project"

    @Parameter(title: "Name", requestValueDialog: "What is the project name?")
    var name: String

    @Parameter(title: "Due Date")
    var dueDate: Date?

    func perform() async throws -> some ReturnsValue<ProjectEntity> & ProvidesDialog {
        let project = try await ProjectRepository.shared.create(name: name, dueDate: dueDate)
        try await ProjectIndexer.shared.index([project])
        return .result(value: project, dialog: "Created \(project.name).")
    }
}
```

Create rules:

- Return the created entity.
- Donate/index the entity if useful.
- Avoid duplicate creations on retries; use idempotency if needed.
- Ask confirmation if creation is public, expensive, sends content, purchases, or may surprise the user.

## Update intent

Updates need precise optional semantics. Siri may distinguish omitted values from explicit clearing.

```swift
struct UpdateTaskIntent: AppIntent {
    static let title: LocalizedStringResource = "Update Task"

    @Parameter(title: "Task")
    var target: TaskEntity

    @Parameter(title: "Title")
    var title: String?

    @Parameter(title: "Due Date")
    var dueDate: Date?

    @Parameter(title: "Completed")
    var isCompleted: Bool?

    func perform() async throws -> some ReturnsValue<TaskEntity> & ProvidesDialog {
        var patch = TaskPatch()

        switch $title.valueState {
        case .unset:
            break
        case .set(let value):
            patch.title = .set(value)
        }

        switch $dueDate.valueState {
        case .unset:
            break
        case .set(let value):
            patch.dueDate = .set(value) // nil may mean explicitly clear.
        }

        switch $isCompleted.valueState {
        case .unset:
            break
        case .set(let value):
            patch.isCompleted = .set(value)
        }

        let updated = try await TaskRepository.shared.update(target.id, patch: patch)
        try await TaskIndexer.shared.index([updated])
        return .result(value: updated, dialog: "Updated \(updated.title).")
    }
}
```

Exact projected-value syntax can shift by SDK. Preserve the semantic distinction between omitted and explicitly nil.

## Delete intent

```swift
struct DeleteProjectIntent: DeleteIntent {
    static let title: LocalizedStringResource = "Delete Project"

    @Parameter(title: "Project")
    var target: ProjectEntity

    func perform() async throws -> some IntentResult & ProvidesDialog {
        try await requestConfirmation(
            actionName: .delete,
            dialog: "Delete \(target.name)?"
        )

        try await ProjectRepository.shared.delete(target.id)
        try await ProjectIndexer.shared.remove(id: target.id)
        try await ProjectDonations.shared.deleteDonations(for: target.id)

        return .result(dialog: "Deleted \(target.name).")
    }
}
```

Rules:

- Confirm destructive actions.
- Make confirmation specific.
- Delete index entries and donations.
- Be idempotent when safe.
- Consider `UndoableIntent` only if the operation is truly reversible.

## Search intent

Use schema-specific search where available. Otherwise use system search-in-app or custom search.

```swift
struct FindTasksIntent: AppIntent {
    static let title: LocalizedStringResource = "Find Tasks"

    @Parameter(title: "Query")
    var query: String

    func perform() async throws -> some ReturnsValue<[TaskEntity]> & ProvidesDialog {
        let results = try await TaskRepository.shared.search(query, limit: 10).map(TaskEntity.init(model:))
        return .result(value: results, dialog: "Found \(results.count) tasks.")
    }
}
```

Return entities, not just strings. Limit and rank results. Provide OpenIntent for result types.

## Dialog

```swift
return .result(dialog: IntentDialog(
    full: "Created task \(task.title) in \(project.name).",
    supporting: "Created."
))
```

Guidelines:

- `full` should work without visuals.
- `supporting` can be short when a snippet is visible.
- Avoid leaking private data in spoken responses.
- Avoid over-explaining routine success.
- Localize and pluralize.

## Requesting values

```swift
let project = try await $project.requestValue("Which project should contain the task?")
```

Rules:

- Request missing information only when truly needed.
- Provide short, specific request dialog.
- Do not catch cancellation and proceed.
- Use suggested entities to make value requests useful.

## Confirmation

Use confirmation for delete, send, publish, share, purchase, external side effects, bulk operations, sensitive transfer, ambiguous entity resolution, and irreversible/surprising effects.

```swift
try await requestConfirmation(
    actionName: .delete,
    dialog: "Delete \(document.title)?"
)
```

With snippet:

```swift
try await requestConfirmation(
    actionName: .delete,
    snippetIntent: DeletePreviewSnippetIntent(document: document)
)
```

Do not treat cancellation as approval.

## Request choice

```swift
let option = try await requestChoice(
    between: suggestedProjects,
    dialog: "Which project should I use?"
)
```

Use for ambiguity among a small set. Do not use for browsing thousands of entities; fix the query/index.

## Interactive snippets

Snippets are compact SwiftUI views returned by intents. They can appear in Siri, Spotlight, and Shortcuts.

```swift
struct TaskResultSnippetIntent: SnippetIntent {
    static let title: LocalizedStringResource = "Task Result"

    @Parameter
    var task: TaskEntity

    func perform() async throws -> some IntentResult & ShowsSnippetView {
        .result(view: TaskResultSnippet(task: task))
    }
}

struct CreateTaskIntent: AppIntent {
    @Parameter(title: "Title") var title: String

    func perform() async throws -> some ReturnsValue<TaskEntity> & ProvidesDialog & ShowsSnippetIntent {
        let task = try await TaskRepository.shared.create(title: title)
        return .result(
            value: task,
            dialog: "Created \(task.title).",
            snippetIntent: TaskResultSnippetIntent(task: task)
        )
    }
}
```

Design rules:

- Keep snippets glanceable and compact.
- Avoid scroll-heavy layouts.
- Make the core result visible without interaction.
- Use buttons/toggles only for explicit actions backed by App Intents.
- Do not mutate state inside a render-only snippet intent.
- Fetch dynamic data in `perform()`, not during view body rendering.
- Keep rendering fast.
- Use accessibility labels and Dynamic Type.
- Ensure dialog still communicates the result when no snippet is shown.

UIKit host note: snippet content remains a SwiftUI view rendered by the system. Keep it in a small SwiftUI-only source group that shares entities/services with the UIKit app; do not present an equivalent UIKit modal or import the scene coordinator into the snippet.

## Snippet controls and reload

```swift
struct CompleteTaskButtonIntent: AppIntent {
    static let title: LocalizedStringResource = "Complete Task"

    @Parameter
    var task: TaskEntity

    func perform() async throws -> some IntentResult {
        try await TaskRepository.shared.complete(task.id)
        TaskResultSnippetIntent.reload()
        return .result()
    }
}
```

Do not reload repeatedly in a tight loop. For progress, use progress APIs or long-running intent APIs.

## UndoableIntent

```swift
struct ArchiveTaskIntent: AppIntent, UndoableIntent {
    static let title: LocalizedStringResource = "Archive Task"

    @Parameter var task: TaskEntity

    func perform() async throws -> some IntentResult & ProvidesDialog {
        try await TaskRepository.shared.archive(task.id)
        return .result(dialog: "Archived \(task.title).")
    }

    func undo() async throws {
        try await TaskRepository.shared.unarchive(task.id)
    }
}
```

Only claim undo when you can actually restore state.

## Error design

```swift
enum TaskIntentError: LocalizedError {
    case notFound
    case permissionDenied
    case duplicateTitle

    var errorDescription: String? {
        switch self {
        case .notFound: "I couldn’t find that task."
        case .permissionDenied: "You don’t have permission to change that task."
        case .duplicateTitle: "A task with that title already exists."
        }
    }
}
```

Errors should be user-actionable and safe. Preserve cancellation. Do not expose internal details.

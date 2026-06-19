# App Intents Examples

This file contains composable examples. Adjust schema names and availability gates to the SDK you are compiling against.

## Project/task entity model

```swift
import AppIntents
import CoreSpotlight
import CoreTransferable
import UniformTypeIdentifiers

struct ProjectEntity: IndexedEntity, Sendable, Identifiable {
    static let defaultQuery = ProjectQuery()

    let id: UUID

    @Property(title: "Name", indexingKey: \.displayName)
    var name: String

    @Property(title: "Overview", indexingKey: \.contentDescription)
    var overview: String?

    @Property(title: "Modified", indexingKey: \.contentModificationDate)
    var modifiedDate: Date

    static var typeDisplayRepresentation: TypeDisplayRepresentation {
        TypeDisplayRepresentation(name: "Project", numericFormat: "\(placeholder: .int) projects")
    }

    var displayRepresentation: DisplayRepresentation {
        DisplayRepresentation(
            title: "\(name)",
            subtitle: overview.map { "\($0)" },
            image: .init(systemName: "folder")
        )
    }
}

extension ProjectEntity: Transferable {
    static var transferRepresentation: some TransferRepresentation {
        DataRepresentation(exportedContentType: .plainText) { project in
            let text = try await ProjectRepository.shared.exportPlainText(project.id)
            return Data(text.utf8)
        }

        FileRepresentation(exportedContentType: .pdf) { project in
            let url = try await ProjectRepository.shared.exportPDF(project.id)
            return SentTransferredFile(url)
        }
    }
}

struct TaskEntity: IndexedEntity, Sendable, Identifiable {
    static let defaultQuery = TaskQuery()

    let id: UUID

    @Property(title: "Title", indexingKey: \.displayName)
    var title: String

    @Property(title: "Project")
    var project: ProjectEntity?

    @Property(title: "Due Date")
    var dueDate: Date?

    @Property(title: "Completed")
    var isCompleted: Bool

    var displayRepresentation: DisplayRepresentation {
        DisplayRepresentation(
            title: "\(title)",
            subtitle: project.map { "\($0.name)" },
            image: .init(systemName: isCompleted ? "checkmark.circle.fill" : "circle")
        )
    }

    static var typeDisplayRepresentation: TypeDisplayRepresentation {
        TypeDisplayRepresentation(name: "Task", numericFormat: "\(placeholder: .int) tasks")
    }
}
```

## Queries

```swift
struct ProjectQuery: EntityStringQuery, EntityPropertyQuery {
    func entities(for identifiers: [ProjectEntity.ID]) async throws -> [ProjectEntity] {
        try await ProjectRepository.shared.projects(ids: identifiers).map(ProjectEntity.init(model:))
    }

    func entities(matching string: String) async throws -> [ProjectEntity] {
        try await ProjectRepository.shared.searchProjects(string, limit: 20).map(ProjectEntity.init(model:))
    }

    func suggestedEntities() async throws -> [ProjectEntity] {
        try await ProjectRepository.shared.activeProjects(limit: 10).map(ProjectEntity.init(model:))
    }

    static var properties = QueryProperties {
        Property(\.name) {
            EqualToComparator { $0 }
            ContainsComparator { $0 }
        }
        Property(\.modifiedDate) {
            GreaterThanComparator { $0 }
            LessThanComparator { $0 }
        }
    }

    static var sortingOptions = SortingOptions {
        SortableBy(\.name)
        SortableBy(\.modifiedDate)
    }

    func entities(
        matching comparators: [QueryComparator<ProjectEntity>],
        mode: ComparatorMode,
        sortedBy: [Sort<ProjectEntity>],
        limit: Int?
    ) async throws -> [ProjectEntity] {
        try await ProjectRepository.shared.queryProjects(
            comparators: comparators,
            mode: mode,
            sortedBy: sortedBy,
            limit: limit
        ).map(ProjectEntity.init(model:))
    }
}
```

## Open/Create/Complete/Delete intents

```swift
struct OpenProjectIntent: OpenIntent {
    static let title: LocalizedStringResource = "Open Project"

    @Parameter(title: "Project")
    var target: ProjectEntity

    func perform() async throws -> some IntentResult {
        // Route through SwiftUI view control or the selected UIKit scene.
        return .result()
    }
}

struct CreateTaskIntent: AppIntent {
    static let title: LocalizedStringResource = "Create Task"
    static let description = IntentDescription("Creates a task in a project.")

    @Parameter(title: "Title", requestValueDialog: "What is the task?")
    var title: String

    @Parameter(title: "Project")
    var project: ProjectEntity?

    @Parameter(title: "Due Date")
    var dueDate: Date?

    static var parameterSummary: some ParameterSummary {
        Summary("Create \(\.$title)") {
            \.$project
            \.$dueDate
        }
    }

    func perform() async throws -> some ReturnsValue<TaskEntity> & ProvidesDialog & ShowsSnippetIntent {
        let task = try await TaskRepository.shared.create(title: title, projectID: project?.id, dueDate: dueDate)
        try await TaskIndexer.shared.index([task])
        await TaskDonor.shared.donateCreated(task)

        return .result(
            value: task,
            dialog: IntentDialog(full: "Created \(task.title).", supporting: "Created."),
            snippetIntent: TaskCreatedSnippetIntent(task: task)
        )
    }
}

struct CompleteTaskIntent: AppIntent, UndoableIntent {
    static let title: LocalizedStringResource = "Complete Task"

    @Parameter(title: "Task")
    var task: TaskEntity

    static var parameterSummary: some ParameterSummary {
        Summary("Complete \(\.$task)")
    }

    func perform() async throws -> some ReturnsValue<TaskEntity> & ProvidesDialog {
        let updated = try await TaskRepository.shared.setCompleted(task.id, true)
        try await TaskIndexer.shared.index([updated])
        return .result(value: updated, dialog: "Completed \(updated.title).")
    }

    func undo() async throws {
        let updated = try await TaskRepository.shared.setCompleted(task.id, false)
        try await TaskIndexer.shared.index([updated])
    }
}

struct DeleteTaskIntent: DeleteIntent {
    static let title: LocalizedStringResource = "Delete Task"

    @Parameter(title: "Task")
    var target: TaskEntity

    func perform() async throws -> some IntentResult & ProvidesDialog {
        try await requestConfirmation(actionName: .delete, dialog: "Delete \(target.title)?")
        try await TaskRepository.shared.delete(target.id)
        try await TaskIndexer.shared.remove(ids: [target.id])
        try await TaskDonor.shared.deleteDonations(for: target.id)
        return .result(dialog: "Deleted \(target.title).")
    }
}
```

## App Shortcuts

```swift
struct TaskAppShortcuts: AppShortcutsProvider {
    static var appShortcuts: [AppShortcut] {
        AppShortcut(
            intent: CreateTaskIntent(),
            phrases: [
                "Create a task in \(.applicationName)",
                "Add \(\.$title) to \(.applicationName)"
            ],
            shortTitle: "Create Task",
            systemImageName: "plus.circle"
        )

        AppShortcut(
            intent: CompleteTaskIntent(),
            phrases: [
                "Complete \(\.$task) in \(.applicationName)",
                "Mark \(\.$task) done in \(.applicationName)"
            ],
            shortTitle: "Complete Task",
            systemImageName: "checkmark.circle"
        )
    }
}
```

## Snippet

```swift
struct TaskCreatedSnippetIntent: SnippetIntent {
    static let title: LocalizedStringResource = "Task Created"

    @Parameter
    var task: TaskEntity

    func perform() async throws -> some IntentResult & ShowsSnippetView {
        .result(view: TaskCreatedSnippet(task: task))
    }
}

struct TaskCreatedSnippet: View {
    let task: TaskEntity

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Label("Task Created", systemImage: "checkmark.circle.fill")
                .font(.headline)
            Text(task.title)
                .font(.title3)
            if let project = task.project {
                Text(project.name).font(.subheadline)
            }
            Button(intent: OpenTaskIntent(target: task)) {
                Text("Open")
            }
        }
        .padding()
    }
}
```

## Onscreen annotations

```swift
struct ProjectDetailView: View {
    let project: ProjectEntity
    let tasks: [TaskEntity]
    @State private var selectedTaskIDs: Set<TaskEntity.ID> = []

    var body: some View {
        List(tasks, selection: $selectedTaskIDs) { task in
            TaskRow(task: task)
                .appEntityIdentifier(EntityIdentifier(for: task))
        }
        .navigationTitle(project.name)
        .userActivity("com.example.project.view") { activity in
            activity.title = "Viewing \(project.name)"
            activity.appEntityIdentifier = EntityIdentifier(for: project)
        }
        .appEntityIdentifier(forSelectionType: TaskEntity.self) {
            tasks.filter { selectedTaskIDs.contains($0.id) }
        }
    }
}
```

## UIKit onscreen and navigation equivalents

The semantic entities and intents above are shared. A UIKit host should route open/search intents through the selected scene and publish visible entities through UIKit annotations.

```swift
@available(iOS 26.0, *)
extension OpenProjectIntent: UISceneAppIntent {}

@MainActor
final class SceneDelegate: UIResponder, UIWindowSceneDelegate, AppIntentSceneDelegate {
    var coordinator: SceneCoordinator!

    func scene(_ scene: UIScene, willPerformAppIntent intent: any UISceneAppIntent) {
        if let open = intent as? OpenProjectIntent {
            coordinator.openProject(open.target.id)
        }
        // Do not invoke intent.perform().
        // This type uses delegate-owned navigation; do not also implement
        // performNavigation(forScene:) for OpenProjectIntent.
    }
}
```

```swift
final class TasksViewController: UITableViewController,
    UITableViewAppIntentsDataSource {

    override func viewDidLoad() {
        super.viewDidLoad()
        tableView.appIntentsDataSource = self
    }

    func tableView(
        _ tableView: UITableView,
        appEntityIdentifierForRowAt indexPath: IndexPath
    ) -> EntityIdentifier? {
        guard let id = dataSource.itemIdentifier(for: indexPath) else { return nil }
        return EntityIdentifier(for: TaskEntity.self, identifier: id)
    }
}
```

See [uikit-examples.md](uikit-examples.md) for scene lifecycle, coordinators, `NSUserActivity`, individual view annotations, collection views, custom canvases, Siri tips, donations, drag providers, Objective-C bridges, and tests.

## Spotlight indexing

```swift
enum ProjectIndexer {
    static func index(_ projects: [ProjectEntity]) async throws {
        try await CSSearchableIndex.default().indexAppEntities(projects)
    }

    static func remove(ids: [ProjectEntity.ID]) async throws {
        try await CSSearchableIndex.default().deleteSearchableItems(
            withIdentifiers: ids.map(\.uuidString)
        )
    }

    static func reindexAllForCurrentAccount() async throws {
        let projects = try await ProjectRepository.shared.allSearchableProjects()
            .filter { $0.isVisibleToCurrentUser }
            .map(ProjectEntity.init(model:))
        try await index(projects)
    }
}
```

## Visual Intelligence query

```swift
@UnionValue
enum VisualMatch: Sendable {
    case project(ProjectEntity)
    case task(TaskEntity)
}

struct AppVisualMatchQuery: IntentValueQuery {
    func values(for input: SemanticContentDescriptor) async throws -> [VisualMatch] {
        var output: [VisualMatch] = []

        if let text = input.text {
            output += try await TaskRepository.shared.searchTasks(text, limit: 5)
                .map { .task(TaskEntity(model: $0)) }
        }

        if let pixelBuffer = input.pixelBuffer {
            output += try await VisualMatcher.shared.matches(pixelBuffer: pixelBuffer, limit: 5)
        }

        return Array(output.prefix(10))
    }
}
```

## Relevant entities

```swift
@available(iOS 27, *)
actor ProjectRelevanceController {
    func updateCurrentProject(_ project: ProjectEntity?) async {
        do {
            if let project {
                try await RelevantEntities.shared.updateEntities([project], for: .currentContext)
            } else {
                try await RelevantEntities.shared.updateEntities([], for: .currentContext)
            }
        } catch {
            // Do not fail the user action because relevance update failed.
        }
    }
}
```

## Long-running export

```swift
@available(iOS 27, *)
struct ExportProjectIntent: AppIntent, LongRunningIntent, ProgressReportingIntent, CancellableIntent {
    static let title: LocalizedStringResource = "Export Project"

    @Parameter(title: "Project")
    var project: ProjectEntity

    @Parameter(title: "Format")
    var format: ExportFormat

    func perform() async throws -> some ReturnsValue<IntentFile> & ProvidesDialog {
        try await performBackgroundTask { progress in
            let fileURL = try await ProjectExporter.shared.export(
                projectID: project.id,
                format: format,
                progress: progress
            )
            return .result(
                value: IntentFile(fileURL),
                dialog: "Exported \(project.name)."
            )
        }
    }

    func onCancel() async {
        await ProjectExporter.shared.cancel(projectID: project.id)
    }
}

enum ExportFormat: String, AppEnum {
    case pdf
    case markdown
    case archive

    static var typeDisplayRepresentation: TypeDisplayRepresentation { "Export Format" }
    static var caseDisplayRepresentations: [Self: DisplayRepresentation] = [
        .pdf: "PDF",
        .markdown: "Markdown",
        .archive: "Archive"
    ]
}
```

## Deprecated wrapper

```swift
struct LegacyAddTodoIntent: DeprecatedAppIntent {
    static let title: LocalizedStringResource = "Add Todo"
    static let intentDeprecation = IntentDeprecation(
        recommendedIntents: [CreateTaskIntent.self],
        message: "Use Create Task instead."
    )

    @Parameter(title: "Todo")
    var todo: String

    func perform() async throws -> some ReturnsValue<TaskEntity> & ProvidesDialog {
        var replacement = CreateTaskIntent()
        replacement.title = todo
        replacement.project = nil
        replacement.dueDate = nil
        return try await replacement.perform()
    }
}
```

## Test skeleton

```swift
import XCTest
import AppIntentsTesting

final class ProjectIntentTests: XCTestCase {
    let definitions = IntentDefinitions(bundleIdentifier: "com.example.productivity")

    func testCreateTaskIntent() async throws {
        var intent = try definitions.makeIntent(CreateTaskIntent.self)
        intent.title = "Prepare deck"

        let result = try await intent.run()
        let task = try XCTUnwrap(result.value as? TaskEntity)

        XCTAssertEqual(task.title, "Prepare deck")
    }

    func testTaskQuery() async throws {
        let results = try await TaskQuery().entities(matching: "deck")
        XCTAssertFalse(results.isEmpty)
    }
}
```

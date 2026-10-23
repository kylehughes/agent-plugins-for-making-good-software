# App Intents Examples

Check [current availability](sdk-availability-and-verification.md#current-documentation-check--2026-10-23) for SDK-specific examples; retain older-SDK build lanes only when required by the project.

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

    static var properties: QueryProperties {
        QueryProperties {
            Property(\.name) {
                EqualToComparator { $0 }
                ContainsComparator { $0 }
            }
            Property(\.modifiedDate) {
                GreaterThanComparator { $0 }
                LessThanComparator { $0 }
            }
        }
    }

    static var sortingOptions: SortingOptions {
        SortingOptions {
            SortableBy(\.name)
            SortableBy(\.modifiedDate)
        }
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
                "Add a task to \(.applicationName)"
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

Shipping iPhoneOS 26.5 example: publish the primary screen entity with `NSUserActivity.appEntityIdentifier` through SwiftUI `.userActivity(...)`.

```swift
struct ProjectDetailView: View {
    let project: ProjectEntity
    let tasks: [TaskEntity]
    @State private var selectedTaskIDs: Set<TaskEntity.ID> = []

    var body: some View {
        List(tasks) { task in
            TaskRow(task: task)
        }
        .navigationTitle(project.name)
        .userActivity("com.example.project.view") { activity in
            activity.title = "Viewing \(project.name)"
            activity.appEntityIdentifier = EntityIdentifier(for: project)
        }
    }
}
```

Use the current availability reference and selected SDK declarations for this surface. Omit or source-gate unsupported APIs only when preserving a required older-SDK build lane; runtime gates alone cannot supply missing declarations.

```swift
// Requires selected-SDK declarations and appropriate runtime availability.
List(tasks, selection: $selectedTaskIDs) { task in
    TaskRow(task: task)
        .appEntityIdentifier(EntityIdentifier(for: task))
}
.appEntityIdentifier(forSelectionType: TaskEntity.self) {
    tasks.filter { selectedTaskIDs.contains($0.id) }
}
```

## UIKit onscreen and navigation equivalents

Use the current availability reference and selected SDK declarations for this surface. Omit or source-gate unsupported APIs only when preserving a required older-SDK build lane; runtime gates alone cannot supply missing declarations.

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
final class ProjectViewController: UIViewController {
    func configure(project: ProjectEntity) {
        title = project.name

        let activity = NSUserActivity(activityType: "com.example.project.view")
        activity.title = "Viewing \(project.name)"
        activity.appEntityIdentifier = EntityIdentifier(for: project)
        userActivity = activity
        activity.becomeCurrent()
    }
}
```

Selected-SDK-gated table annotation shape only:

```swift
// Requires selected-SDK declarations and appropriate runtime availability.
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

See [uikit-examples.md](uikit-examples.md) for scene lifecycle, coordinators, `NSUserActivity`, selected-SDK-gated advanced annotations, Siri tips, donations, drag providers, Objective-C bridges, and tests.

## Spotlight indexing

```swift
enum ProjectIndexer {
    static func index(_ projects: [ProjectEntity]) async throws {
        try await CSSearchableIndex.default().indexAppEntities(projects)
    }

    static func remove(ids: [ProjectEntity.ID]) async throws {
        try await CSSearchableIndex.default().deleteAppEntities(
            identifiedBy: ids, ofType: ProjectEntity.self
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

/// `SemanticContentDescriptor` is declared in the VisualIntelligence framework.
struct AppVisualMatchQuery: IntentValueQuery {
    func values(for input: SemanticContentDescriptor) async throws -> [VisualMatch] {
        var output: [VisualMatch] = []

        for label in input.labels {
            output += try await TaskRepository.shared.searchTasks(label, limit: 5)
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

Apple documents `RelevantEntities` on iOS 27+ for media suggestions using supported audio contexts, such as Now Playing and workouts. It is not a general registry for documents, projects, routes, or arbitrary selected items. Use entity queries, screen annotations, and Spotlight for those surfaces. See [the current availability table](sdk-availability-and-verification.md#current-documentation-check--2026-10-23).

## Long-running export

Use the current availability reference and selected SDK declarations for this surface. Omit or source-gate unsupported APIs only when preserving a required older-SDK build lane; runtime gates alone cannot supply missing declarations.

Buildable progress-oriented shape:

```swift
struct ExportProjectIntent: AppIntent, ProgressReportingIntent {
    static let title: LocalizedStringResource = "Export Project"

    @Parameter(title: "Project")
    var project: ProjectEntity

    @Parameter(title: "Format")
    var format: ExportFormat

    func perform() async throws -> some ReturnsValue<IntentFile> & ProvidesDialog {
        let fileURL = try await ProjectExporter.shared.export(
            projectID: project.id,
            format: format,
            progress: progress,
            cancellation: { Task.isCancelled }
        )
        return .result(
            value: IntentFile(fileURL: fileURL),
            dialog: "Exported \(project.name)."
        )
    }
}
```

Selected-SDK-dependent wrapper only:

```swift
// Requires selected-SDK declarations and appropriate runtime availability.
struct FutureExportProjectIntent: AppIntent, LongRunningIntent, ProgressReportingIntent, CancellableIntent {
    // Add long-running/cancellation hooks here only when available.
}
```

```swift
enum ExportFormat: String, AppEnum {
    case pdf
    case markdown
    case archive

    static var typeDisplayRepresentation: TypeDisplayRepresentation { "Export Format" }
    static let caseDisplayRepresentations: [Self: DisplayRepresentation] = [
        .pdf: "PDF",
        .markdown: "Markdown",
        .archive: "Archive"
    ]
}
```

## Deprecated wrapper

`DeprecatedAppIntent` and `IntentDeprecation` are iOS 17 APIs.

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

Use the current availability reference and selected SDK declarations for this surface. Omit or source-gate unsupported APIs only when preserving a required older-SDK build lane; runtime gates alone cannot supply missing declarations.

```swift
import XCTest

final class ProjectIntentTests: XCTestCase {
    func testTaskQuery() async throws {
        let results = try await TaskQuery().entities(matching: "deck")
        XCTAssertFalse(results.isEmpty)
    }
}
```

Selected-SDK-dependent selected-SDK-gated shape:

```swift
#if canImport(AppIntentsTesting)
import XCTest
import AppIntentsTesting

final class ProjectIntentFrameworkTests: XCTestCase {
    let definitions = IntentDefinitions(bundleIdentifier: "com.example.productivity")

    func testCreateTaskIntent() async throws {
        var intent = try definitions.makeIntent(CreateTaskIntent.self)
        intent.title = "Prepare deck"

        let result = try await intent.run()
        let task = try XCTUnwrap(result.value as? TaskEntity)

        XCTAssertEqual(task.title, "Prepare deck")
    }
}
#endif
```

## Structured value mapping: place entity to Maps-style actions

Use the current availability reference and selected SDK declarations for this surface. Omit or source-gate unsupported APIs only when preserving a required older-SDK build lane; runtime gates alone cannot supply missing declarations.

```swift
import AppIntents
import CoreLocation
import GeoToolbox

struct LandmarkEntity: AppEntity, Sendable, Identifiable {
    static let defaultQuery = LandmarkQuery()

    let id: Int
    let name: String
    let coordinate: CLLocationCoordinate2D

    static var typeDisplayRepresentation: TypeDisplayRepresentation { "Landmark" }

    var displayRepresentation: DisplayRepresentation {
        DisplayRepresentation(title: "\(name)", image: .init(systemName: "mappin.and.ellipse"))
    }

    var systemPlaceDescriptor: PlaceDescriptor {
        // Use the exact initializer labels from the selected GeoToolbox SDK.
        fatalError("Use the PlaceDescriptor initializer from the selected GeoToolbox SDK.")
    }
}
```

Selected-SDK-dependent transfer wrapper only:

```swift
// Requires selected-SDK declarations and appropriate runtime availability.
import CoreTransferable
import UniformTypeIdentifiers

extension LandmarkEntity: Transferable {
    static var transferRepresentation: some TransferRepresentation {
        ValueRepresentation(exporting: \.systemPlaceDescriptor)

        DataRepresentation(exportedContentType: .plainText) { landmark in
            Data(landmark.name.utf8)
        }
    }
}
```

Use this pattern when a visible or selected entity should flow into another app as a structured value, for example “get directions to this landmark.” Pair it with primary `NSUserActivity` annotation and an `OpenIntent`; transfer alone does not make the entity discoverable.

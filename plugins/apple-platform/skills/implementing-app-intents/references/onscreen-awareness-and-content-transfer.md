# Onscreen Awareness and Content Transfer

## Why this matters

Siri and Apple Intelligence need contextual cues for requests like:

- “Summarize this.”
- “Open the second one.”
- “Add these to my project.”
- “Send this to Alex.”
- “What can I do with this document?”
- “Find photos like this.”
- “Ask ChatGPT about the chart I’m looking at.”

The screen already contains the user’s referents. App Intents lets you publish those referents as entities, selections, and transferable content.

## Awareness layers

Use all that apply:

1. `NSUserActivity` for the primary current entity.
2. SwiftUI `.appEntityIdentifier(...)` for specific views.
3. Collection annotations for lists, grids, tables, and selections.
4. Custom annotations for canvas/drawing/nonstandard views.
5. UIKit/AppKit equivalents for collection views, table views, and custom UI elements.
6. Notifications, Now Playing, AlarmKit, Live Activities, and other system-surface annotations.
7. `Transferable` and `IntentValueRepresentation` for content inspection/handoff.
8. `IntentValueQuery` for resolving incoming semantic/visual content.

## Primary entity with NSUserActivity

```swift
struct ProjectDetailScreen: View {
    let project: ProjectEntity

    var body: some View {
        ProjectDetailContent(project: project)
            .userActivity("com.example.project.view") { activity in
                activity.title = "Viewing \(project.name)"
                activity.isEligibleForSearch = true
                activity.isEligibleForPrediction = true
                activity.appEntityIdentifier = EntityIdentifier(for: project)
            }
    }
}
```

Guidelines:

- Use stable activity types.
- Set a meaningful title.
- Use `appEntityIdentifier` when the activity corresponds to an AppEntity.
- Keep eligibility flags aligned with user privacy settings.
- Update the activity when the primary entity changes.

## Individual SwiftUI view annotation

```swift
struct TaskRow: View {
    let task: TaskEntity

    var body: some View {
        HStack {
            Text(task.title)
            Spacer()
            if task.isCompleted { Image(systemName: "checkmark") }
        }
        .appEntityIdentifier(EntityIdentifier(for: task))
    }
}
```

Use for list rows, cards, thumbnails, message bubbles, calendar events, and canvas objects that have SwiftUI wrappers.

## Collection and selection annotation

```swift
struct TaskListView: View {
    let tasks: [TaskEntity]
    @State private var selectedIDs: Set<TaskEntity.ID> = []

    var body: some View {
        List(tasks, selection: $selectedIDs) { task in
            TaskRow(task: task)
                .appEntityIdentifier(EntityIdentifier(for: task))
        }
        .appEntityIdentifier(forSelectionType: TaskEntity.self) {
            selectedIDs.compactMap { id in tasks.first { $0.id == id } }
        }
    }
}
```

Exact API shapes can vary by SDK. Preserve the semantic intent: annotate collection members and selected entities so Siri can resolve “these” or “the selected items.”

## Custom canvas annotation

For drawing/canvas apps, semantic objects may not correspond to normal rows.

```swift
struct CanvasView: View {
    let board: BoardEntity
    let visibleObjects: [CanvasObjectEntity]

    var body: some View {
        Canvas { context, size in
            // Draw objects.
        }
        .userActivity("com.example.board.view") { activity in
            activity.title = "Viewing \(board.title)"
            activity.appEntityIdentifier = EntityIdentifier(for: board)
        }
        .appEntityIdentifiers(visibleObjects.map { EntityIdentifier(for: $0) })
    }
}
```

If the SDK exposes custom region/element annotations, include bounds and z-order so Siri can resolve “the blue rectangle” or “the item in the top-right.”

## UIKit strategy

UIKit supports the full onscreen-awareness stack. Do not reduce UIKit support to attaching an identifier to visible cells. Model four levels:

1. **Primary screen entity** — create/update an `NSUserActivity`, set `appEntityIdentifier`, and make it current while the controller represents that entity.
2. **Individual semantic view** — assign `appEntityIdentifier` to a UIKit framework object that already supports `AppEntityAnnotatable`. `UIView` subclasses inherit support; do not declare new conformances.
3. **Table or collection** — set `tableView.appIntentsDataSource` / `collectionView.appIntentsDataSource` and map each index path through the current data source to a stable entity ID.
4. **Custom canvas** — assign `UIView.appEntityUIElementProvider` and return entity identifiers with current geometry and selection state.

### Primary controller

```swift
let activity = NSUserActivity(activityType: "com.example.view-project")
activity.title = "Viewing \(project.name)"
activity.appEntityIdentifier = EntityIdentifier(
    for: ProjectEntity.self,
    identifier: project.id
)
viewController.userActivity = activity
activity.becomeCurrent()
```

Invalidate or replace it when the screen disappears, changes subject, becomes privacy-redacted, or switches accounts.

### Table annotation

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
        guard let id = diffableDataSource.itemIdentifier(for: indexPath) else {
            return nil
        }
        return EntityIdentifier(for: TaskEntity.self, identifier: id)
    }
}
```

Use the equivalent `UICollectionViewAppIntentsDataSource` method for collection views. Never use the index path itself as identity. Return `nil` for placeholders, inaccessible rows, ads, and decoration.

### Reuse invariant

```swift
override func prepareForReuse() {
    super.prepareForReuse()
    representedID = nil
    contentView.appEntityIdentifier = nil
}
```

A stale annotation can cause Siri to act on the wrong, potentially private entity.

### Custom canvas

`appEntityUIElementProvider` returns `AppEntityUIElement` values containing a stable identifier, bounds in the annotated view’s coordinate space, and state such as selection. Keep the provider synchronous, fast, authorization-aware, and free of mutation/network access. Exact initializer labels are SDK-sensitive.

### Scene routing is part of context correctness

When Siri acts on an onscreen UIKit entity, route through the scene that owns that context using `UISceneAppIntent` or `AppIntentSceneDelegate`. Do not guess a window from global application state. Give each intent type one navigation owner; routing it in both `performNavigation(forScene:)` and the scene delegate can navigate twice.

For the complete UIKit architecture and code, see [uikit-integration.md](uikit-integration.md) and [uikit-examples.md](uikit-examples.md).

## Annotations outside the app

Use framework-specific entity annotations when content appears in other surfaces:

- Notification content representing a message, event, task, or order.
- Now Playing media session representing a track, episode, or audiobook.
- Alarm/timer configuration representing an app-defined routine.
- Live Activity content representing an order, trip, timer, or match.

Pattern:

```swift
let content = UNMutableNotificationContent()
content.title = task.title
content.body = task.projectName ?? "Task"
content.appEntityIdentifiers = [EntityIdentifier(for: task)]
```

Use only for entities safe to expose in that surface.

## Transferable for app entities

Transferable tells the system how to export an entity’s content.

```swift
import CoreTransferable
import UniformTypeIdentifiers

extension DocumentEntity: Transferable {
    static var transferRepresentation: some TransferRepresentation {
        DataRepresentation(exportedContentType: .plainText) { document in
            let text = try await DocumentRepository.shared.plainText(for: document.id)
            return text.data(using: .utf8) ?? Data()
        }

        DataRepresentation(exportedContentType: .rtf) { document in
            try await DocumentRepository.shared.rtfData(for: document.id)
        }

        FileRepresentation(exportedContentType: .pdf) { document in
            let url = try await DocumentExporter.shared.pdfURL(for: document.id)
            return SentTransferredFile(url)
        }
    }
}
```

Guidelines:

- Provide plain text for broad compatibility.
- Provide rich text, PDF, image, or file when the app has high-quality exports.
- Do not export fields the current user cannot view.
- Redact secrets and private metadata.
- Prefer temporary files for generated exports.
- Keep exports cancellation-aware.

## IntentValueRepresentation and ValueRepresentation

Use `IntentValueRepresentation` or `ValueRepresentation` when a `Transferable` entity should preserve App Intents value semantics instead of only exporting bytes. This is the right tool when the destination needs a system-known structured value, such as `IntentPerson` or `PlaceDescriptor`, rather than a PDF, image, or string.

```swift
import AppIntents
import CoreTransferable
import GeoToolbox

extension LandmarkEntity: Transferable {
    static var transferRepresentation: some TransferRepresentation {
        ValueRepresentation(exporting: \.placeDescriptor)

        DataRepresentation(exportedContentType: .plainText) { landmark in
            Data(landmark.name.utf8)
        }
    }
}
```

For a full treatment of structured cross-app transfer, including `PlaceDescriptor`, import closures, `IntentValueQuery`, UIKit annotations, and failure modes, see [value-representation-and-structured-transfer.md](value-representation-and-structured-transfer.md).

## Incoming content with IntentValueQuery

```swift
@UnionValue
enum ImportableContentMatch {
    case document(DocumentEntity)
    case task(TaskEntity)
    case project(ProjectEntity)
}

struct ImportableContentQuery: IntentValueQuery {
    func values(for input: SemanticContentDescriptor) async throws -> [ImportableContentMatch] {
        var results: [ImportableContentMatch] = []

        if let text = input.text {
            results += try await SemanticTextIndex.shared.matches(text).map { .document($0) }
        }

        if let pixelBuffer = input.pixelBuffer {
            results += try await VisualIndex.shared.matches(pixelBuffer).map { .project($0) }
        }

        return Array(results.prefix(10))
    }
}
```

Guidelines:

- Return high-confidence results.
- Bound result counts.
- Provide strong display representations.
- Ensure returned entity types have OpenIntent support.
- Avoid server round-trips when the system expects quick visual lookup.

## Visual Intelligence search

Implementation pieces:

1. Semantic content search schema intent or value query.
2. `IntentValueQuery` accepting `SemanticContentDescriptor`.
3. Local or privacy-safe matching pipeline.
4. Result entities or union values with display representations.
5. OpenIntent for result entities.
6. Tests and manual Visual Intelligence validation.

```swift
@UnionValue
enum LandmarkVisualResult {
    case landmark(LandmarkEntity)
    case collection(LandmarkCollectionEntity)
}

struct LandmarkVisualQuery: IntentValueQuery {
    func values(for input: SemanticContentDescriptor) async throws -> [LandmarkVisualResult] {
        guard let pixelBuffer = input.pixelBuffer else { return [] }
        return try await LandmarkMatcher.shared.match(pixelBuffer)
    }
}
```

## Content transfer to ChatGPT or external intelligence

When the user asks an external intelligence service about app content, the system may transfer a representation instead of only a screenshot if your app provides one.

Prefer, when safe:

1. Structured intent value representation.
2. Plain text.
3. Rich text / attributed string.
4. PDF for visual layout.
5. Image for visual content.
6. Original file.

Do not assume screenshot redaction applies to exported representations. You control the bytes.

## Entity identifier vs transferable content

Use entity identifier when the system only needs to refer to the app object, the app can perform the action internally, or the content should not leave the app.

Use Transferable when Siri/Shortcuts/ChatGPT needs to inspect content, another app needs to receive content, or the user explicitly asks to send/export/share/summarize/analyze content.

Often you need both.

## Privacy checklist

For every annotated/transferred entity, ask:

- Can this entity be named in Siri UI?
- Can it be spoken aloud?
- Can it be visible while locked?
- Can it be indexed?
- Can it be transferred out of process?
- Are attachments included?
- Are comments/history/hidden fields included?
- Are account IDs, server IDs, access tokens, or internal URLs included?
- Does enterprise policy allow this?
- Did the user opt out of suggestions/search?

## Pitfalls

- Stale annotations from reused cells cause Siri to resolve the wrong item. Clear/update annotations during reuse.
- Overbroad Transferable exports leak comments, history, metadata, or hidden fields. Use sanitized exports.
- Screen-only context without queryability makes content impossible to reference later. Durable content needs AppEntity and query.
- TransientAppEntity for saved content breaks later references. Use AppEntity for saved content.
- Visual search results without OpenIntent cannot be opened. Add OpenIntent for every returned entity type.

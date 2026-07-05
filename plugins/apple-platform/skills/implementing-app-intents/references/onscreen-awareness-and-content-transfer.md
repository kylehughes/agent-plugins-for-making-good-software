# Onscreen Awareness and Content Transfer

## Why this matters

Siri and Apple Intelligence need a reliable bridge from natural references like “this,” “that,” “the current document,” or “the item I’m viewing” to an `AppEntity` that your app can resolve. Screen pixels and accessibility text are not enough. The system needs durable entity identifiers, queries that can resolve those identifiers, and content representations it can safely pass to other actions.

## Availability reality for iPhoneOS 26.5

The iPhoneOS 26.5 SDK exposes `NSUserActivity.appEntityIdentifier` and `AppEntityAnnotatable` as iOS 18.2 APIs. In that SDK, the only buildable App Intents onscreen annotation path is the `NSUserActivity` level for the primary screen entity.

These APIs are **absent** from iPhoneOS 26.5 and must be treated as forward-looking / selected-SDK-dependent:

- SwiftUI per-view `.appEntityIdentifier(...)`.
- SwiftUI `.appEntityIdentifier(forSelectionType:)`.
- UIKit `UITableViewAppIntentsDataSource` and `UICollectionViewAppIntentsDataSource`.
- UIKit `AppEntityUIElement` and `UIView.appEntityUIElementProvider`.
- Notification-content `appEntityIdentifiers`.

Keep examples for absent APIs out of production targets compiled with the 26.5 SDK. `@available` is not sufficient when the compiler cannot see the declaration.

## Awareness layers

Current shipping layer:

1. **Primary screen entity** — use `NSUserActivity.appEntityIdentifier` to associate the screen’s main semantic subject with an `AppEntity` identifier.

Selected-SDK-gated future layers:

2. **Individual visible object** — per-view entity identifiers, when the selected SDK declares them.
3. **Collection/selection** — list, grid, table, collection, or selection annotations, when the selected SDK declares them.
4. **Custom canvas elements** — geometric entity regions/elements, when the selected SDK declares them.

Do not collapse the mental model. Design your domain model so levels 2–4 can be added later, but ship iOS 26.5 code using level 1 only unless a newer SDK supplies the other declarations.

## Primary entity with NSUserActivity

Use `NSUserActivity` when one entity defines the screen: a document editor, project detail, conversation, photo detail, now-playing item, order status, or account-scoped dashboard.

SwiftUI pattern using the shipping `NSUserActivity` API:

```swift
ProjectDetailView(project: project)
    .userActivity("com.example.project.view") { activity in
        activity.title = "Viewing \(project.name)"
        activity.appEntityIdentifier = EntityIdentifier(for: project.entity)
    }
```

UIKit pattern:

```swift
let activity = NSUserActivity(activityType: "com.example.project.view")
activity.title = "Viewing \(project.name)"
activity.appEntityIdentifier = EntityIdentifier(
    for: ProjectEntity.self,
    identifier: project.id
)
viewController.userActivity = activity
activity.becomeCurrent()
```

Rules:

- Publish one primary entity per semantic screen.
- Replace the activity when the screen’s subject changes in place.
- Invalidate or resign the activity when the controller disappears, redacts content, switches account/workspace, or stops representing the entity.
- Do not publish content the current user cannot access.
- Keep the activity title, visible navigation title, accessibility title, and entity display representation consistent.
- The entity identifier must resolve through the entity query without requiring the original view controller.

## Forward-looking individual SwiftUI view annotation

The following is the intended shape for per-view annotation, but the per-view `.appEntityIdentifier(...)` modifier is absent from `_AppIntents_SwiftUI` in the iPhoneOS 26.5 SDK. Use only when the selected SDK declares it.

```swift
// Forward-looking / selected-SDK-gated; not buildable with iPhoneOS 26.5.
TaskRow(task: task)
    .appEntityIdentifier(EntityIdentifier(for: task))
```

Use cases when available:

- Rows and cards that each represent a durable entity.
- Thumbnails that represent photos, files, pages, or assets.
- Message bubbles, calendar events, annotations, or canvas objects.
- A focused attachment preview or selected visual object.

## Forward-looking collection and selection annotation

The following selection-style API is absent from the iPhoneOS 26.5 SDK. Use only when the selected SDK declares an equivalent API.

```swift
// Forward-looking / selected-SDK-gated; not buildable with iPhoneOS 26.5.
List(tasks, selection: $selectedIDs) { task in
    TaskRow(task: task)
        .appEntityIdentifier(EntityIdentifier(for: task))
}
.appEntityIdentifier(forSelectionType: TaskEntity.self) {
    selectedIDs.compactMap { id in tasks.first { $0.id == id } }
}
```

Preserve the design invariant even before the API exists: selection should be represented by stable model IDs, not index paths or visible-cell objects.

## Forward-looking custom canvas annotation

Custom drawing/canvas apps often need geometry-aware entity annotations. The iPhoneOS 26.5 SDK does not declare `AppEntityUIElement` or `UIView.appEntityUIElementProvider`, and it does not expose a buildable SwiftUI custom-region equivalent.

When a selected SDK provides such an API, each element should be:

- A stable `EntityIdentifier`.
- Current bounds in the annotated view’s coordinate space.
- Current selection/focus state where supported.
- Free of network access, mutation, layout triggering, or side effects.

## UIKit strategy

For iPhoneOS 26.5-compatible UIKit code, implement the primary activity level thoroughly:

```swift
@MainActor
final class ProjectViewController: UIViewController {
    private var projectID: ProjectEntity.ID?

    func configure(project: Project) {
        projectID = project.id
        title = project.name
        publishActivity(for: project)
    }

    private func publishActivity(for project: Project) {
        let activity = NSUserActivity(activityType: "com.example.project.view")
        activity.title = "Viewing \(project.name)"
        activity.appEntityIdentifier = EntityIdentifier(
            for: ProjectEntity.self,
            identifier: project.id
        )
        userActivity = activity
        activity.becomeCurrent()
    }

    override func viewDidDisappear(_ animated: Bool) {
        super.viewDidDisappear(animated)
        userActivity?.invalidate()
        userActivity = nil
    }
}
```

Do not generate UIKit table/collection/canvas annotation code for a 26.5-compiled target. Keep selection and visible-object state in stable model-ID form so a future adapter can expose it when the SDK provides APIs.

## Scene routing is part of context correctness

When Siri acts on an onscreen UIKit entity, route through the scene that owns that context using `UISceneAppIntent` or `AppIntentSceneDelegate`. These APIs are available through the `_AppIntents_UIKit` cross-import overlay when `UIKit` and `AppIntents` are imported.

Do not guess a window from global application state. Give each intent type one navigation owner: either custom `performNavigation(forScene:)` on the intent or central `AppIntentSceneDelegate` routing, not both.

## Annotations outside the app

Do not use `UNMutableNotificationContent.appEntityIdentifiers` for iPhoneOS 26.5 code; that property is absent from the verified SDK. If a future SDK supplies notification entity annotations, apply the same privacy rules as screen context:

- Only expose entities safe for the notification surface.
- Avoid private content on the lock screen.
- Use persistent entity IDs, not transient IDs.
- Remove or update annotations when access changes.

Other system surfaces such as Now Playing, alarms, or Live Activities have their own APIs and availability. Verify each one independently before generating code.

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

## Structured values: PlaceDescriptor and IntentPerson today, transfer wrappers later

`PlaceDescriptor` and `IntentPerson` are distinct from `ValueRepresentation` / `IntentValueRepresentation`.

- `IntentPerson` is in `AppIntents` and is available since iOS 16.
- `PlaceDescriptor` is in `GeoToolbox` and is available in the iOS 26 SDK, with `_GeoToolbox_AppIntents` overlay support.
- `ValueRepresentation` and `IntentValueRepresentation` are absent from the iPhoneOS 26.5 SDK.

For iOS 26.5-compatible code, create pure mapping helpers:

```swift
import AppIntents
import GeoToolbox

extension LandmarkEntity {
    var placeValueForSystemUse: PlaceDescriptor {
        // Use the initializer shape from the selected GeoToolbox SDK.
        fatalError("Use the PlaceDescriptor initializer from the selected GeoToolbox SDK.")
    }
}

extension ContactEntity {
    var personValueForSystemUse: IntentPerson {
        // Use the initializer shape from the selected AppIntents SDK.
        fatalError("Use the IntentPerson initializer from the selected AppIntents SDK.")
    }
}
```

When a selected SDK declares a structured transfer representation API, wrap these helpers beside the entity’s `Transferable` conformance. Do not move this logic into SwiftUI views or UIKit view controllers.

## Incoming content with IntentValueQuery

`IntentValueQuery` is present in the iPhoneOS 26.5 SDK. `SemanticContentDescriptor` is declared in the `VisualIntelligence` framework, not `AppIntents`.

```swift
import AppIntents
import VisualIntelligence

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
2. `IntentValueQuery` accepting `SemanticContentDescriptor` from `VisualIntelligence`.
3. Local or privacy-safe matching pipeline.
4. Result entities or `@UnionValue` values with display representations.
5. OpenIntent for result entities.
6. Tests and manual Visual Intelligence validation.

```swift
import AppIntents
import VisualIntelligence

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

## Content transfer to external intelligence

When the user asks an external intelligence service about app content, the system may transfer a representation instead of only a screenshot if your app provides one.

Prefer, when safe:

1. System-known structured value mapping where a receiving action has a supported value type; use transfer wrappers only when the selected SDK declares them.
2. Plain text.
3. Rich text / attributed string.
4. PDF for visual layout.
5. Image for visual content.
6. Deep link URL only if it is meaningful outside the app and not a substitute for content.

## Entity identifier vs transferable content

They solve different problems.

- Entity identifier: “Which object in your app is this?”
- Entity query: “Can your app still resolve that object?”
- Transferable representation: “What content can leave your app?”
- Structured value mapping: “Can this private entity be expressed as a system-known type like a place or person?”

Do not expose more through transfer than the user could see or intentionally share.

## Privacy checklist

- Primary activity disabled for locked, private, hidden, deleted, or redacted content.
- Entity query enforces account and permission rules.
- Display representation does not leak private metadata.
- Transferable exports re-check authorization at export time.
- Structured value mappers do not include more precise location/person data than the app visibly disclosed.
- Visual matching does not upload pixels unless the user opted into a documented server path.
- Context is invalidated on sign-out, workspace switch, protected-data lock, and privacy mode.

## Pitfalls

- Treating screen text as enough context.
- Publishing stale `NSUserActivity` after navigation.
- Publishing an entity ID whose query cannot resolve after app relaunch.
- Returning private entity titles in error dialogs.
- Confusing `PlaceDescriptor` or `IntentPerson` value mappers with absent structured transfer representation APIs.
- Generating per-view/list/canvas annotation code for iPhoneOS 26.5 even though the symbols are absent.
- Assuming notification content has App Entity annotations without checking the selected SDK.

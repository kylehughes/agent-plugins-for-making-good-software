# Apple Intelligence and Siri Integration

Check [current availability](sdk-availability-and-verification.md#current-documentation-check--2026-10-23) for SDK-specific examples; retain older-SDK build lanes only when required by the project.

## What Siri needs from an app

Siri and Apple Intelligence do not need your app to parse natural language. They need a semantically complete App Intents surface:

- App actions as typed `AppIntent` values.
- App content as typed `AppEntity`, `IndexedEntity`, `TransientAppEntity`, `AppEnum`, union values, structured value mappers, and selected-SDK-gated value representations.
- App Schemas where a system domain exists.
- Entity queries that resolve names, IDs, properties, and suggestions.
- Semantic Spotlight indexing for durable searchable content.
- Onscreen annotations for currently visible content.
- Transferable/value representations for content inspection and handoff.
- Dialog/snippet/confirmation behavior for user interaction.
- Donations and relevance signals for prediction.
- Tests that execute the same framework paths the system uses.

## Siri integration stack

```text
User request
  ↓
Siri / Apple Intelligence intent planning
  ↓
App Schema match + App Shortcut + Spotlight/entity search + visible context + donations + supported media suggestions (when applicable)
  ↓
Entity resolution and parameter filling
  ↓
AppIntent execution
  ↓
Dialog, result value, snippet, opened app, transferred content, progress, or follow-up action
```

The app’s job is to publish enough typed structure that this stack works without fragile phrase-by-phrase handling.

## Priority order for Siri-ready apps

1. Use App Schemas for known domains.
2. Define durable entities and entity queries.
3. Implement open/search/create/update/delete actions with typed parameters.
4. Index searchable entities with semantically useful properties.
5. Annotate visible content and selections.
6. Add Transferable/value representations for content Siri should understand or pass to another service.
7. Add dialog and compact snippets.
8. Donate meaningful interactions; for media apps, add supported audio-context suggestions where useful.
9. Test through XCTest/manual Siri/Spotlight/Shortcuts surfaces, and through AppIntentsTesting only if the selected SDK includes that framework.

## App Schemas

App Schemas describe common domains and action shapes to the system. Use schema annotations when available.

```swift
@AppIntent(schema: .photos.openAsset)
struct OpenPhotoIntent: OpenIntent {
    @Parameter(title: "Photo")
    var target: PhotoEntity

    @MainActor
    func perform() async throws -> some IntentResult {
        try await PhotoRouter.shared.open(target.id)
        return .result()
    }
}

@AppEntity(schema: .photos.asset)
struct PhotoEntity: IndexedEntity {
    static let defaultQuery = PhotoQuery()
    let id: String

    @Property(title: "Title", indexingKey: \.displayName)
    var title: String?

    @Property(title: "Description", indexingKey: \.contentDescription)
    var textDescription: String?

    var creationDate: Date?
    var assetType: PhotoAssetType?
}

@AppEnum(schema: .photos.assetType)
enum PhotoAssetType: String, AppEnum {
    case photo
    case video

    static var typeDisplayRepresentation: TypeDisplayRepresentation { "Asset Type" }
    static let caseDisplayRepresentations: [Self: DisplayRepresentation] = [
        .photo: "Photo",
        .video: "Video"
    ]
}
```

### Schema rules

- Choose the closest correct schema, not the most prestigious one.
- Conform entities, enums, and intents together; schema value mismatches weaken the integration.
- Do not add required parameters beyond schema expectations.
- Additional optional parameters may be acceptable for Shortcuts, but test Siri behavior carefully.
- Mark assistant-only schema intents with `isAssistantOnly` if they should not be a public Shortcuts contract.
- Use Xcode Fix-Its and schema diagnostics; they often reveal missing related schemas, property mappings, and enum schemas.

## Entity access

Siri can reason over app content only when content is exposed in a resolvable way.

```swift
struct ProjectEntity: IndexedEntity {
    static let defaultQuery = ProjectQuery()
    let id: UUID

    @Property(title: "Name", indexingKey: \.displayName)
    var name: String

    @Property(title: "Summary", indexingKey: \.contentDescription)
    var summary: String?

    @Property(title: "Due Date")
    var dueDate: Date?

    var displayRepresentation: DisplayRepresentation {
        DisplayRepresentation(title: "\(name)", subtitle: summary.map { "\($0)" })
    }
}
```

Use `TransientAppEntity` when the value is produced during a flow but cannot be queried later.

```swift
struct DraftSearchResult: TransientAppEntity {
    var title: String
    var snippet: String

    static var typeDisplayRepresentation: TypeDisplayRepresentation { "Search Result" }

    var displayRepresentation: DisplayRepresentation {
        DisplayRepresentation(title: "\(title)", subtitle: "\(snippet)")
    }
}
```

## Semantic search and Spotlight

Use semantic indexing when the user may ask for content by meaning, not exact title.

```swift
func reindexProjects() async throws {
    let entities = try await ProjectRepository.shared.allIndexableProjects()
    try await CSSearchableIndex.default().indexAppEntities(entities)
}
```

Index only fields the user should be able to search. Use `@Property(indexingKey:)`, `@ComputedProperty(indexingKey:)`, and custom CoreSpotlight attributes for semantically important data.

## Onscreen awareness

Onscreen annotations let Siri understand pronouns and context: “summarize this,” “open the second one,” “send these,” “what can I do with this project?”

Shipping iPhoneOS 26.5 path: publish the primary screen entity with `NSUserActivity.appEntityIdentifier` (iOS 18.2+).

SwiftUI primary item:

```swift
ProjectDetailView(project: project)
    .userActivity("com.example.app.viewProject") { activity in
        activity.title = "Viewing \(project.name)"
        activity.appEntityIdentifier = EntityIdentifier(for: project.entity)
    }
```

UIKit primary item:

```swift
let activity = NSUserActivity(activityType: "com.example.app.viewProject")
activity.title = "Viewing \(project.name)"
activity.appEntityIdentifier = EntityIdentifier(for: ProjectEntity.self, identifier: project.id)
viewController.userActivity = activity
activity.becomeCurrent()
```

Use the current availability reference and selected SDK declarations for this surface. Omit or source-gate unsupported APIs only when preserving a required older-SDK build lane; runtime gates alone cannot supply missing declarations.

UIKit context correctness still matters today: route contextual actions through the owning `UIScene`; do not guess a global window, and assign exactly one navigation owner to each scene-targeted intent.

### UIKit context menus and drag resources

On selected iOS 27-era SDKs, UIKit menus can surface Ask Siri when relevant context exists. Apple Intelligence may request resources through UIKit drag delegates without an ordinary gesture. Keep drag loading authorization-aware and side-effect free; do not present UI or animate from `sessionWillBegin`. Per-view annotations remain selected-SDK-dependent.

## Content transfer

Use `Transferable` when Siri, ChatGPT, Shortcuts, or another app should receive the content itself rather than only an entity ID.

For known file/data formats, export plain text, rich text, images, PDFs, or files. For system-known structured values, separate the value type from the transfer wrapper:

Use the current availability reference and selected SDK declarations for this surface. Omit or source-gate unsupported APIs only when preserving a required older-SDK build lane; runtime gates alone cannot supply missing declarations.

Build pure mappers from entities to `IntentPerson` or `PlaceDescriptor` now. Add future `ValueRepresentation` / `IntentValueRepresentation` wrappers only when the selected SDK declares them. A landmark that only exports text can be mailed; a landmark that can be represented as a `PlaceDescriptor` has the right semantic shape for Maps-style actions once a transfer wrapper exists. See [value-representation-and-structured-transfer.md](value-representation-and-structured-transfer.md).

```swift
extension ProjectEntity: Transferable {
    static var transferRepresentation: some TransferRepresentation {
        DataRepresentation(exportedContentType: .plainText) { project in
            """
            Project: \(project.name)
            Summary: \(project.summary ?? "")
            """.data(using: .utf8)!
        }

        FileRepresentation(exportedContentType: .pdf) { project in
            let url = try await ProjectExporter.shared.exportPDF(project.id)
            return SentTransferredFile(url)
        }
    }
}
```

A rich export is powerful, but it is also a privacy boundary.

## Incoming content resolution

Use `IntentValueQuery` when the system has external or semantic input and your app needs to resolve it to app entities or values. `SemanticContentDescriptor` is declared in the `VisualIntelligence` framework, not `AppIntents`.

```swift
@UnionValue
enum SearchableVisualResult {
    case project(ProjectEntity)
    case document(DocumentEntity)
}

struct VisualResultQuery: IntentValueQuery {
    func values(for input: SemanticContentDescriptor) async throws -> [SearchableVisualResult] {
        guard let pixelBuffer = input.pixelBuffer else { return [] }
        let matches = try await VisualSearchIndex.shared.matches(pixelBuffer: pixelBuffer)

        return matches.map { match in
            switch match.kind {
            case .project: .project(match.projectEntity)
            case .document: .document(match.documentEntity)
            }
        }
    }
}
```

## Siri dialog

If an intent returns no dialog, Siri may synthesize a response. Use `ProvidesDialog` when the app must control spoken or visual output.

```swift
struct CompleteTaskIntent: AppIntent {
    static let title: LocalizedStringResource = "Complete Task"

    @Parameter(title: "Task")
    var task: TaskEntity

    func perform() async throws -> some IntentResult & ProvidesDialog {
        try await TaskRepository.shared.complete(task.id)
        return .result(dialog: IntentDialog(
            full: "Marked \(task.title) complete.",
            supporting: "Done."
        ))
    }
}
```

The `full` dialog should stand alone on voice-only devices. The `supporting` dialog can be shorter when a snippet carries context.

## Visual responses

Use `DisplayRepresentation` for entity rows and `ShowsSnippetView`/`ShowsSnippetIntent` for custom result UI.

```swift
struct TaskSummarySnippetIntent: SnippetIntent {
    static let title: LocalizedStringResource = "Task Summary"

    @Parameter
    var task: TaskEntity

    func perform() async throws -> some IntentResult & ShowsSnippetView {
        .result(view: TaskSummarySnippet(task: task))
    }
}
```

Use snippets when visual confirmation or result interpretation genuinely helps. Do not make them the only way to understand the result; voice and accessibility still need coherent dialog and labels.

## Interaction donations

Donate meaningful user interactions so Siri can learn likely actions and entities.

```swift
func donateOpenedProject(_ project: ProjectEntity) async {
    var intent = OpenProjectIntent()
    intent.target = project
    try? await IntentDonationManager.shared.donate(intent: intent)
}
```

For selected-SDK-gated iOS 27-era interactions, include result values when that helps Siri learn entity/action relationships.

```swift
func donateCreatedTask(_ task: TaskEntity) async {
    var intent = CreateTaskIntent()
    intent.title = task.title
    let result = IntentResultContainer<TaskEntity, Never, Never, Never>.result(value: task)
    try? await IntentDonationManager.shared.donate(intent: intent, result: result)
}
```

Delete donations when the underlying content is deleted, access is revoked, or a user disables personalized suggestions.

## RelevantEntities

Apple documents `RelevantEntities` on iOS 27+ for media suggestions using supported audio contexts, such as Now Playing and workouts. It is not a general registry for documents, projects, routes, or arbitrary selected items. Use entity queries, screen annotations, and Spotlight for those surfaces. See [the current availability table](sdk-availability-and-verification.md#current-documentation-check--2026-10-23).

## Search in app

Use the system in-app search schema when the app supports arbitrary in-app search and there is not a more specific schema path.

```swift
@AppIntent(schema: .system.searchInApp)
struct SearchInAppIntent: ShowInAppSearchResultsIntent {
    static let title: LocalizedStringResource = "Search"
    static let searchScopes: [StringSearchScope] = [.general]

    var criteria: StringSearchCriteria

    func perform() async throws -> some IntentResult {
        // Bind this to SwiftUI view control or UIKit scene routing.
        return .result()
    }
}
```

Use specific domain search schemas first when a domain-specific search action exists. Use system search-in-app as a generic fallback. In UIKit, route the criteria through the selected `UIScene`; do not store it in a process-global search router.

## Siri-ready checklist

An app is meaningfully Siri-ready when:

- Major durable nouns are App Entities.
- Common actions are App Intents.
- Known domains use App Schemas.
- Entity IDs are stable and resolvable.
- Entity queries support ID lookup and user naming.
- Important content is semantically indexed.
- The primary visible entity is annotated with `NSUserActivity`; selections/per-view annotations are added only when the selected SDK supports them.
- Transferable representations are implemented for content Siri may inspect.
- Intent result values are meaningful and typed.
- Dialog is clear on voice-only devices.
- Snippets are optional compact visual aids.
- Donations reflect real user behavior; supported media/audio suggestions are kept current when used.
- Tests execute intents, queries, indexing, and annotations through XCTest/manual system surfaces; add AppIntentsTesting only when the framework exists.

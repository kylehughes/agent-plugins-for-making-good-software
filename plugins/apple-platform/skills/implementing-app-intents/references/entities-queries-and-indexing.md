# Entities, Queries, and Indexing

Check [current availability](sdk-availability-and-verification.md#current-documentation-check--2026-10-23) for SDK-specific examples; retain older-SDK build lanes only when required by the project.

UIKit/SwiftUI rule: entities and queries are shared semantic types. Never put `UIView`, `UIViewController`, `UIScene`, `UIImageView`, navigation state, index paths, or diffable data-source instances inside an entity or query. UIKit adapters publish only stable entity IDs.

## Entity taxonomy

| Type | Use for | Notes |
| --- | --- | --- |
| `AppEntity` | Durable app content with an ID | Needs a query. Good for tasks, projects, documents, messages, albums. |
| `IndexedEntity` | Durable content that should be searchable semantically | Add indexable properties and donate/index with CoreSpotlight. |
| `TransientAppEntity` | Temporary values produced during a flow | No durable query. Good for ephemeral search results, generated previews, unsaved drafts. |
| `AppEnum` | Fixed set of values | Stable raw values and strong display names. |
| `@UnionValue` | A parameter/result can be one of several types | Useful for flexible Siri requests and Shortcuts pickers. |
| `PlaceDescriptor` / `IntentPerson` mappers | Convert an entity to a shipping system-known structured value | `IntentPerson` is iOS 16; `PlaceDescriptor` is iOS 26 in `GeoToolbox`. Keep mappers pure and UI-independent. |
| AppIntents `EntityCollection` | Selected-SDK-dependent large/lazy entity collection passed by identifier | Check current availability and selected SDK declarations. |
| `SyncableEntity` | Selected-SDK-dependent entity with local and stable sync identity | Check current availability and selected SDK declarations. |

## AppEntity baseline

```swift
import AppIntents

struct TaskEntity: AppEntity, Identifiable, Sendable {
    static let defaultQuery = TaskEntityQuery()

    let id: UUID
    let title: String
    let projectName: String?
    let dueDate: Date?
    let isCompleted: Bool

    static var typeDisplayRepresentation: TypeDisplayRepresentation {
        TypeDisplayRepresentation(name: "Task", numericFormat: "\(placeholder: .int) tasks")
    }

    var displayRepresentation: DisplayRepresentation {
        DisplayRepresentation(
            title: "\(title)",
            subtitle: projectName.map { "Project: \($0)" },
            image: .init(systemName: isCompleted ? "checkmark.circle" : "circle")
        )
    }
}
```

### Entity identity

Good IDs:

- Stable database UUID.
- Stable cloud record ID represented as a string.
- Stable integer ID if the app already uses one.
- Your own local/sync ID mapping when local and synced identity differ; use `SyncableEntityIdentifier` only if the selected SDK declares it.

Weak IDs:

- Index in an array.
- Title or user-editable name.
- Path that changes during sync or moves.
- Temporary URL.
- Hash of mutable content.

## DisplayRepresentation

Display representation affects Siri UI, Shortcuts pickers, Spotlight results, snippets, and disambiguation.

```swift
var displayRepresentation: DisplayRepresentation {
    DisplayRepresentation(
        title: "\(title)",
        subtitle: dueDate.map { "Due \($0.formatted(date: .abbreviated, time: .omitted))" },
        image: .init(systemName: priority.systemImageName)
    )
}
```

Guidelines:

- Title should be what the user calls the thing.
- Subtitle should disambiguate without leaking private information.
- Image should be small, recognizable, and safe.
- Do not expose raw IDs or debug strings.
- Localize display strings.
- Include type display representation and plural/numeric format.

## EntityQuery

Every durable entity needs ID lookup.

```swift
struct TaskEntityQuery: EntityQuery {
    func entities(for identifiers: [TaskEntity.ID]) async throws -> [TaskEntity] {
        try await TaskRepository.shared.tasks(ids: identifiers).map(TaskEntity.init(model:))
    }

    func suggestedEntities() async throws -> [TaskEntity] {
        try await TaskRepository.shared.recentTasks(limit: 10).map(TaskEntity.init(model:))
    }
}
```

`entities(for:)` must be fast, permission-aware, stable across launches, correct for missing/deleted entities, and safe for IDs from old shortcuts or donations. Return only entities the current user may access.

## EntityStringQuery

Use when users name entities by text.

```swift
struct TaskEntityQuery: EntityStringQuery {
    func entities(for identifiers: [TaskEntity.ID]) async throws -> [TaskEntity] { ... }

    func entities(matching string: String) async throws -> [TaskEntity] {
        let trimmed = string.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmed.isEmpty else { return try await suggestedEntities() }

        return try await TaskRepository.shared.searchTasks(trimmed, limit: 20)
            .map(TaskEntity.init(model:))
    }

    func suggestedEntities() async throws -> [TaskEntity] { ... }
}
```

Guidelines:

- Normalize casing and diacritics if the repository does not.
- Rank exact title matches above fuzzy matches.
- Include aliases only when user-visible.
- Bound result counts.
- Prefer semantic Spotlight/IndexedEntity for large corpora.

## EnumerableEntityQuery

Use only for bounded, safe lists.

```swift
struct PriorityQuery: EnumerableEntityQuery {
    func allEntities() async throws -> [PriorityEntity] {
        Priority.allCases.map(PriorityEntity.init)
    }
}
```

Good uses: small project lists, static presets, user categories under a limit. Bad uses: all emails, photos, messages, files, or enterprise rows.

## EntityPropertyQuery

Use for Shortcuts Find actions and structured filters.

```swift
struct TaskEntityQuery: EntityPropertyQuery {
    typealias Entity = TaskEntity

    static var properties: QueryProperties {
        QueryProperties {
            Property(\.title) {
                EqualToComparator { $0 }
                ContainsComparator { $0 }
            }
            Property(\.projectName) {
                EqualToComparator { $0 }
                ContainsComparator { $0 }
            }
            Property(\.dueDate) {
                LessThanComparator { $0 }
                GreaterThanComparator { $0 }
            }
            Property(\.isCompleted) {
                EqualToComparator { $0 }
            }
        }
    }

    static var sortingOptions: SortingOptions {
        SortingOptions {
            SortableBy(\.title)
            SortableBy(\.dueDate)
        }
    }

    func entities(
        matching comparators: [QueryComparator<TaskEntity>],
        mode: ComparatorMode,
        sortedBy: [Sort<TaskEntity>],
        limit: Int?
    ) async throws -> [TaskEntity] {
        try await TaskRepository.shared.query(
            comparators: comparators,
            mode: mode,
            sortedBy: sortedBy,
            limit: limit
        )
    }
}
```

Implementation notes:

- Push filters into storage when possible.
- Match comparator mode correctly.
- Apply sorting deterministically.
- Respect `limit`.
- Return empty results for no matches; throw only for actual failure/permission denial.

## IndexedEntity

Use for durable searchable content, especially content Siri or Spotlight should find by meaning.

```swift
import CoreSpotlight

struct NoteEntity: IndexedEntity {
    static let defaultQuery = NoteQuery()
    let id: UUID

    @Property(title: "Title", indexingKey: \.displayName)
    var title: String

    @Property(title: "Body", indexingKey: \.textContent)
    var body: AttributedString

    @ComputedProperty(indexingKey: \.contentDescription)
    var summary: String {
        body.characters.prefix(280).description
    }

    @Property(title: "Modified Date", indexingKey: \.contentModificationDate)
    var modifiedDate: Date
}
```

Indexing:

```swift
func indexNotes(_ notes: [Note]) async throws {
    let entities = notes
        .filter { $0.isSearchableByCurrentUser }
        .map(NoteEntity.init(model:))

    try await CSSearchableIndex.default().indexAppEntities(entities)
}

func removeNotesFromIndex(ids: [UUID]) async throws {
    try await CSSearchableIndex.default().deleteAppEntities(identifiedBy: ids, ofType: NoteEntity.self)
}
```

Guidelines:

- Index only useful searchable properties.
- Use built-in indexing keys where possible: display name, description, text content, content dates.
- Use custom keys for app-specific facets.
- Remove deleted, locked, revoked, or account-switched content promptly.
- Reindex when user-visible searchable content changes.
- Implement `OpenIntent` for entities that should be tappable from Spotlight.

## CoreSpotlight association

If you already use `CSSearchableItem`, associate it with the AppEntity.

```swift
func makeSearchableItem(for document: Document) -> CSSearchableItem {
    let attributes = CSSearchableItemAttributeSet(contentType: .text)
    attributes.title = document.title
    attributes.contentDescription = document.summary
    attributes.textContent = document.fullText

    let item = CSSearchableItem(
        uniqueIdentifier: document.id.uuidString,
        domainIdentifier: "documents",
        attributeSet: attributes
    )

    item.associateAppEntity(DocumentEntity(model: document), priority: document.isFavorite ? 10 : 1)
    return item
}
```

Use priority to bias important or recent results. Do not game priority so aggressively that search quality suffers.

## @Property, @ComputedProperty, @DeferredProperty

```swift
struct TrailEntity: IndexedEntity {
    let id: UUID

    @Property(title: "Name", indexingKey: \.displayName)
    var name: String

    @ComputedProperty(indexingKey: \.contentDescription)
    var shortDescription: String {
        [difficulty.displayName, locationName, "\(lengthMiles) miles"].joined(separator: " • ")
    }

    @DeferredProperty(title: "Current Crowd Level")
    var currentCrowdLevel: Int {
        get async throws {
            try await TrailStatusService.shared.crowdLevel(for: id)
        }
    }
}
```

Use `@Property` for stored fields, `@ComputedProperty` for cheap derived fields, and `@DeferredProperty` only for expensive/remote/slow fields. Do not make basic display properties deferred.

## TransientAppEntity

Use when an entity is not durably queryable.

```swift
struct GeneratedSummaryEntity: TransientAppEntity {
    let title: String
    let summary: AttributedString

    static var typeDisplayRepresentation: TypeDisplayRepresentation { "Generated Summary" }

    var displayRepresentation: DisplayRepresentation {
        DisplayRepresentation(title: "\(title)", subtitle: "Generated summary")
    }
}
```

Good for unsaved drafts, search previews, temporary conversion outputs, and live sensor readings. Bad for saved content or anything the user may reference later.

## Sync identity without assuming SyncableEntity

Use the current availability reference and selected SDK declarations for this surface. Omit or source-gate unsupported APIs only when preserving a required older-SDK build lane; runtime gates alone cannot supply missing declarations.

Still design stable identity carefully:

```swift
struct CloudTaskEntity: AppEntity {
    static let defaultQuery = CloudTaskQuery()

    // Stable public AppEntity ID chosen by the app. It may encode or map to local/cloud IDs,
    // but it must remain durable and non-sensitive.
    let id: String

    let localID: UUID
    let cloudID: String?
    let title: String

    init(model: TaskModel) {
        self.localID = model.localID
        self.cloudID = model.cloudRecordID
        self.id = TaskIdentityMapper.entityID(
            localID: model.localID,
            cloudID: model.cloudRecordID
        )
        self.title = model.title
    }
}
```

Implementation notes:

- Keep local lookup fast.
- Resolve sync IDs when local IDs change after migration/reinstall.
- Handle local-only entities without a cloud ID.
- Never expose sync IDs if they are sensitive or account-scoped.
- If a future selected SDK declares `SyncableEntity`, adapt this mapping rather than changing the public entity ID semantics.

## Selected-SDK-dependent EntityCollection

Use the current availability reference and selected SDK declarations for this surface. Omit or source-gate unsupported APIs only when preserving a required older-SDK build lane; runtime gates alone cannot supply missing declarations.

For a 26.5-compatible app, model large relationships with stable IDs and query methods:

```swift
struct PlaylistEntity: AppEntity {
    static let defaultQuery = PlaylistQuery()
    let id: UUID
    let name: String

    @Property(title: "Track Count")
    var trackCount: Int
}

struct TracksInPlaylistIntent: AppIntent {
    static let title: LocalizedStringResource = "Get Tracks in Playlist"

    @Parameter(title: "Playlist")
    var playlist: PlaylistEntity

    func perform() async throws -> some ReturnsValue<[TrackEntity]> {
        let tracks = try await TrackRepository.shared.tracks(inPlaylist: playlist.id, limit: 100)
        return .result(value: tracks)
    }
}
```

If a selected SDK later supplies an AppIntents collection type, wrap this existing relationship/query model rather than resolving every member eagerly.

## Structured value mappers and future ValueRepresentation

Use the current availability reference and selected SDK declarations for this surface. Omit or source-gate unsupported APIs only when preserving a required older-SDK build lane; runtime gates alone cannot supply missing declarations.

```swift
import AppIntents
import GeoToolbox

struct LandmarkEntity: AppEntity {
    static let defaultQuery = LandmarkQuery()

    let id: Int
    let name: String

    var systemPlaceDescriptor: PlaceDescriptor {
        // Use the exact initializer labels from the selected GeoToolbox SDK.
        fatalError("Use the PlaceDescriptor initializer from the selected GeoToolbox SDK.")
    }
}
```

Use the current availability reference and selected SDK declarations for this surface. Omit or source-gate unsupported APIs only when preserving a required older-SDK build lane; runtime gates alone cannot supply missing declarations.

```swift
// Selected-SDK-gated only.
static var transferRepresentation: some TransferRepresentation {
    ValueRepresentation(exporting: \.systemPlaceDescriptor)
}
```

Use structured mapping when the destination needs semantic data such as a place or person. Do not use fake JSON, private IDs, or values the system does not understand. See [value-representation-and-structured-transfer.md](value-representation-and-structured-transfer.md).

## @UnionValue

```swift
@UnionValue
enum MoveDestination: Sendable {
    case project(ProjectEntity)
    case folder(FolderEntity)
    case inbox(InboxEntity)
}

struct MoveTaskIntent: AppIntent {
    static let title: LocalizedStringResource = "Move Task"

    @Parameter(title: "Task")
    var task: TaskEntity

    @Parameter(title: "Destination")
    var destination: MoveDestination

    func perform() async throws -> some IntentResult {
        try await TaskMover.shared.move(task.id, to: destination)
        return .result()
    }
}
```

Use unions when the user naturally thinks in alternatives. Do not use unions to avoid modeling the domain.

## Entity ownership

Use ownership protocols when the system needs to distinguish whether an entity belongs to your app/user/account.

```swift
struct AccountDocumentEntity: AppEntity, OwnershipProvidingEntity {
    let id: UUID
    let accountID: UUID
    let name: String

    // Supply the framework ownership value from the authorized repository.
    let ownership: EntityOwnership
}
```

Ownership is account/access semantics, not only “created by this app.” Omit entities or return false when access is revoked.

## Query performance targets

Aim for:

- ID lookup under 100 ms for local data.
- Suggested entities under 200 ms.
- Text search under 300 ms for local indexes.
- Property query bounded by `limit`.
- No unbounded full-table scans on every Siri request.
- No network-only dependency for basic entity display.
- Cancellation-aware async operations.

## Indexing lifecycle

Index on install/import completion, user-created content, edits, permission changes, account switch, sync completion, and migration completion.

Remove from index on delete, archive/hide/lock if no longer searchable, sign-out, workspace removal, enterprise policy change, or user disabling search/suggestions.

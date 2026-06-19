# App Schema Domains

## Purpose

App Schemas give the system a shared semantic contract for common app domains. A schema-conforming intent says “this action is the standard open/create/update/delete/search/send/capture/read operation for this kind of content.” A schema-conforming entity says “this object has the standard properties and behavior for this domain noun.”

Use schemas whenever they accurately fit your domain. A schema is more valuable than a custom vocabulary because Siri and Apple Intelligence already know what the schema means.

## Schema adoption pattern

```swift
@AppIntent(schema: .photos.openAsset)
struct OpenAssetIntent: OpenIntent {
    @Parameter(title: "Asset")
    var target: AssetEntity

    @MainActor
    func perform() async throws -> some IntentResult {
        try await AssetRouter.shared.open(target.id)
        return .result()
    }
}

@AppEntity(schema: .photos.asset)
struct AssetEntity: IndexedEntity {
    static let defaultQuery = AssetQuery()
    let id: String

    @Property(title: "Title", indexingKey: \.displayName)
    var title: String?

    var creationDate: Date?
    var assetType: AssetType?
    var isFavorite: Bool
}

@AppEnum(schema: .photos.assetType)
enum AssetType: String, AppEnum {
    case photo
    case video

    static var typeDisplayRepresentation: TypeDisplayRepresentation { "Asset Type" }
    static var caseDisplayRepresentations: [Self: DisplayRepresentation] = [
        .photo: "Photo",
        .video: "Video"
    ]
}
```

## General rules

- Prefer schema conformance for common domains.
- Do not lie about the domain. Siri behavior will be worse if you force a mismatch.
- Implement related schema entities and enums when an intent schema expects them.
- Do not add extra required parameters beyond the schema contract.
- Use optional parameters only when they are truly optional, and test Siri behavior.
- Use `isAssistantOnly` for new schema intents that should be used by Siri/Apple Intelligence but not exposed as stable Shortcuts actions.
- Use Xcode diagnostics and Fix-Its for missing schema pieces.
- Keep custom display representations strong even when a schema exists.
- Keep entities queryable/indexed; schema conformance does not replace resolution.

## Assistant-only intents

```swift
@AppIntent(schema: .photos.createAssets)
struct CreateAssetsForAssistantIntent: AppIntent {
    static let title: LocalizedStringResource = "Create Assets"
    static let isAssistantOnly: Bool = true

    @Parameter(title: "Files")
    var files: [IntentFile]

    func perform() async throws -> some ReturnsValue<[AssetEntity]> {
        let created = try await AssetImporter.shared.import(files)
        return .result(value: created)
    }
}
```

Assistant-only intents are intentionally not discovery surfaces for Spotlight or Shortcuts.

## Domain selection matrix

| App domain | Prefer these schema families when they fit | Typical custom extras |
| --- | --- | --- |
| Photos/media library | Photos, Visual Intelligence, Files | Smart albums, custom edits, app metadata |
| Camera/scanning | Camera, Photos, Files, Visual Intelligence | Capture presets, OCR workflows, templates |
| Books/PDF/reading | Books, Reader, Files | Reading state, annotations, collections |
| Browser/web | Browser | Profiles, tab groups, reading list semantics |
| Notes/journal | Journal, Word Processor, Files | Tags, notebooks, templates, mood/state fields |
| Email/messaging | Mail, Messages, Contacts/person values | Team inboxes, thread states, app routing |
| Calendar/tasks | Calendar, System search, Files | Project linkage, task states, custom recurrence |
| Office documents | Presentation, Spreadsheet, Word Processor, Files | Slide/page/table/cell/selection models |
| Whiteboard/canvas | Whiteboard, Files, Visual Intelligence | Nodes, groups, annotations, layers |
| Audio/playback | Audio/media schemas when available | Queue state, playback device, session metadata |
| Clock/timer/alarm | Clock/system schemas when available | Presets, routines, labels, linked workflows |
| Generic search | System search-in-app | App-specific scopes and filters |

## Notable schema families

The exact available schemas depend on the SDK. Use Xcode’s AppIntents schema autocomplete and docs as source of truth. Public documentation and sessions cover or reference these families:

- Photos
- Books
- Browser
- Camera
- Reader/document reader
- Files
- Journal
- Mail
- Messages
- Calendar
- Presentation
- Spreadsheet
- Whiteboard
- Word processor
- Audio/media
- Clock/alarm/timer
- Visual Intelligence / semantic content search
- System search-in-app

## Photos domain pattern

Use for photo/video libraries, assets, albums, search, favorites, imports, and open actions.

```swift
@AppEntity(schema: .photos.asset)
struct PhotoAssetEntity: IndexedEntity {
    static let defaultQuery = PhotoAssetQuery()
    let id: String

    @Property(title: "Title", indexingKey: \.displayName)
    var title: String?

    @Property(title: "Description", indexingKey: \.contentDescription)
    var description: String?

    var creationDate: Date?
    var assetType: PhotoAssetType?
    var isFavorite: Bool
    var isHidden: Bool
}

@AppIntent(schema: .photos.openAsset)
struct OpenPhotoAssetIntent: OpenIntent {
    var target: PhotoAssetEntity

    @MainActor
    func perform() async throws -> some IntentResult {
        try await PhotoRouter.shared.open(assetID: target.id)
        return .result()
    }
}
```

Notes:

- Use `IndexedEntity` for large libraries where semantic search matters.
- Do not index hidden/private assets unless explicitly allowed.
- Use `IntentFile` for imported/exported asset data.
- Use `OpenIntent` for Spotlight and Visual Intelligence results.

## Files domain pattern

```swift
@AppEntity(schema: .files.file)
struct ProjectFileEntity: FileEntity {
    static let defaultQuery = ProjectFileQuery()
    static var supportedContentTypes: [UTType] = [.pdf, .plainText, .image]

    var id: FileEntityIdentifier
    var creationDate: Date?
    var fileModificationDate: Date?

    var displayRepresentation: DisplayRepresentation {
        DisplayRepresentation(title: "\(id.filename ?? "File")")
    }
}

@AppIntent(schema: .files.openFile)
struct OpenProjectFileIntent: OpenIntent {
    var target: ProjectFileEntity

    @MainActor
    func perform() async throws -> some IntentResult {
        try await FileRouter.shared.open(target.id)
        return .result()
    }
}
```

Notes:

- Decide whether file semantics or domain semantics should be primary if the object is both an app entity and a file.
- Use `Transferable`/file representations for export.
- Keep security-scoped URL handling out of entity display code.

## Journal / notes pattern

```swift
@AppIntent(schema: .journal.createEntry)
struct CreateJournalEntryIntent: AppIntent {
    static let title: LocalizedStringResource = "Create Journal Entry"

    @Parameter(title: "Message")
    var message: AttributedString

    @Parameter(title: "Title")
    var title: String?

    @Parameter(title: "Entry Date")
    var entryDate: Date?

    @Parameter(title: "Media")
    var mediaItems: [IntentFile]

    func perform() async throws -> some ReturnsValue<JournalEntryEntity> & ProvidesDialog {
        let entity = try await JournalStore.shared.create(
            title: title,
            message: message,
            date: entryDate ?? Date(),
            media: mediaItems
        )
        return .result(value: entity, dialog: "Created \(entity.displayTitle).")
    }
}
```

Notes:

- Use `AttributedString` for rich text.
- Be conservative exposing private journal content through indexing or Transferable.
- Use snippets sparingly because journal content is sensitive.

## Mail / Messages pattern

```swift
@AppEntity(schema: .messages.message)
struct MessageEntity: IndexedEntity {
    static let defaultQuery = MessageQuery()
    let id: String

    @Property(title: "Text", indexingKey: \.textContent)
    var text: AttributedString

    @Property(title: "Subject", indexingKey: \.displayName)
    var subject: String?

    var sender: IntentPerson?
    var recipients: [IntentPerson]
    var sentDate: Date?
}
```

Notes:

- Model participants with `IntentPerson` or schema-specific people/contact entities.
- Do not index message bodies if privacy settings or enterprise policy prohibit it.
- Distinguish create/update/send draft actions.
- Confirm send/delete/forward actions when ambiguity exists.

## Calendar pattern

Calendar apps usually need multiple entity types: calendar, event, attendee, alarm, recurrence, location, and availability state.

```swift
@AppEntity(schema: .calendar.event)
struct CalendarEventEntity: IndexedEntity {
    static let defaultQuery = CalendarEventQuery()
    let id: String

    @Property(title: "Title", indexingKey: \.displayName)
    var title: String

    @Property(title: "Notes", indexingKey: \.contentDescription)
    var notes: String?

    var startDate: Date
    var endDate: Date
    var attendees: [IntentPerson]
    var calendar: CalendarEntity?
}
```

Notes:

- Optional-parameter updates must distinguish omitted from explicit clearing.
- Deletion should confirm and disambiguate.
- Calendar entities are strong candidates for `IndexedEntity` and onscreen annotation.
- Attendee-like values can be transient if they are not durable app content.

## Browser pattern

```swift
@AppIntent(schema: .browser.createTab)
struct CreateBrowserTabIntent: AppIntent {
    static let title: LocalizedStringResource = "Create Tab"

    @Parameter(title: "URL")
    var url: URL?

    @Parameter(title: "Private")
    var isPrivate: Bool

    @MainActor
    func perform() async throws -> some ReturnsValue<BrowserTabEntity> {
        let tab = try await BrowserController.shared.createTab(url: url, isPrivate: isPrivate)
        return .result(value: tab)
    }
}
```

Notes:

- Treat private browsing as a privacy boundary.
- Consider tab, tab group, profile, window, and history entities separately.
- Do not donate private browsing history.

## Reader / document pattern

```swift
@AppEntity(schema: .reader.document)
struct ReaderDocumentEntity: IndexedEntity {
    static let defaultQuery = ReaderDocumentQuery()
    let id: UUID

    @Property(title: "Title", indexingKey: \.displayName)
    var title: String

    @Property(title: "Text", indexingKey: \.textContent)
    var extractedText: String?

    var pageCount: Int?
    var kind: ReaderDocumentKind
}
```

Notes:

- Model document, page, annotation, selection, and bookmark separately when actions target them.
- Use Transferable for PDF/plain text/rich text export.
- Use onscreen annotation for current page and selected annotation.

## Office document domains

Presentation, spreadsheet, and word-processor apps should model nested entities, not only top-level documents.

```text
Document
  ├─ Section / deck / workbook
  ├─ Page / slide / sheet
  ├─ Object / shape / table / chart / cell range
  ├─ Comment / annotation
  └─ Selection
```

Actions should be granular:

- Open document.
- Create slide.
- Duplicate slide.
- Rename sheet.
- Sort range.
- Insert table.
- Export as PDF.
- Add comment.
- Summarize selection.

## Whiteboard / canvas pattern

Canvas apps should expose both high-level boards and selectable objects.

```swift
struct BoardEntity: IndexedEntity { /* title, creation, modification, owner */ }
struct CanvasObjectEntity: AppEntity { /* board, bounds, kind, label */ }
struct CanvasSelectionEntity: TransientAppEntity { /* selected object IDs */ }
```

Notes:

- Use custom view annotations for drawing/canvas views.
- Use Transferable for selected canvas content as PDF/image/plain text.
- Use snippets only for compact status or confirmation.

## System search-in-app

```swift
@AppIntent(schema: .system.searchInApp)
struct SearchInAppIntent: ShowInAppSearchResultsIntent {
    static let title: LocalizedStringResource = "Search"
    static var searchScopes: [StringSearchScope] = [.general]
    var criteria: StringSearchCriteria

    func perform() async throws -> some IntentResult {
        // The host UI receives the typed criteria and presents its search route.
        return .result()
    }
}
```

Use specific domain search schemas first when available. Use system search-in-app as the generic fallback. In UIKit, deliver the criteria to the selected scene through `UISceneAppIntent` or `AppIntentSceneDelegate`, then route through the scene coordinator.

## Visual Intelligence / semantic content search

```swift
@AppIntent(schema: .visualIntelligence.semanticContentSearch)
struct SearchVisualContentIntent: AppIntent {
    static let title: LocalizedStringResource = "Search Visual Content"

    @Parameter(title: "Content")
    var content: SemanticContentDescriptor

    func perform() async throws -> some ReturnsValue<[VisualSearchResult]> {
        let values = try await VisualResultQuery().values(for: content)
        return .result(value: values)
    }
}
```

Notes:

- Return app entities with good display representations.
- Implement `OpenIntent` for returned entity types.
- Keep matching fast and bounded.
- Use local/device-safe matching where possible.
- Respect privacy and content permissions.

## Schema gap strategy

When no schema exists:

1. Model custom entities with strong display representations.
2. Implement ID, string, and property queries.
3. Add `IndexedEntity` for durable searchable content.
4. Add `OpenIntent` and common actions.
5. Add `AppShortcut` phrases for discovery.
6. Add onscreen annotations.
7. Add Transferable/value representations.
8. Donate interactions.
9. Add RelevantEntities for dynamic context.
10. Test Siri behavior and adjust entity/query surfaces before adding more phrases.

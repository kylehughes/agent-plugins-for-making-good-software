# Migration from iOS 26 to iOS 27 App Intents

## Goal

Keep the iOS 26 integration working while adopting iOS 27 improvements that make Siri and Apple Intelligence more capable. Avoid breaking existing shortcuts, donations, indexes, and entity IDs.

## iOS 26 baseline checklist

Before adopting iOS 27-specific features, ensure the app already has:

- App Entities for major durable nouns.
- Entity queries for ID lookup and string search.
- OpenIntent for tappable entities.
- App Shortcuts for common zero-configuration actions.
- Parameter summaries for discoverability.
- IndexedEntity or CoreSpotlight association for searchable content.
- Onscreen annotations for detail and list views.
- Transferable exports for content Siri/ChatGPT/Shortcuts can inspect.
- Interactive snippets where useful.
- Foreground continuation for UI-dependent actions.
- TargetContentProvidingIntent where actions should hit active content.
- AppIntentsPackage if intents live in Swift packages.
- Tests for entity queries and intent execution.

## iOS 27 adoption priorities

### Priority 1: App Schemas audit

Map each entity/action to available schema domains.

```text
Custom OpenTaskIntent -> schema if task/project/calendar domain exists
Custom SearchIntent -> .system.searchInApp or domain search schema
Custom ImportPhotoIntent -> photos/files schema if applicable
Custom MessageAction -> messages/mail schema if applicable
```

Actions:

- Add schema annotations to matching intents/entities/enums.
- Add missing schema-required properties.
- Split overloaded custom intents into schema-conforming actions.
- Use `isAssistantOnly` for new Siri-only schema actions.
- Keep old public intents as wrappers/deprecated types if users may have shortcuts.

### Priority 2: Strengthen entity identity

Adopt stable sync identity where needed.

```swift
@available(iOS 27, *)
struct TaskEntity: AppEntity, SyncableEntity {
    let id: SyncableEntityIdentifier
    let title: String
}
```

Actions:

- Preserve old IDs for old shortcuts.
- Add migration lookup from old ID to new stable ID.
- Handle offline/local-only entities.
- Avoid changing raw ID semantics of shipped entities unless you provide compatibility.

### Priority 3: Add RelevantEntities

Use for context suggestions: current document, active project, now playing media, current workout/session, current location-specific content, currently selected item.

Do not replace Spotlight indexing with RelevantEntities.

### Priority 4: Use EntityCollection for large relationships

```swift
struct AlbumEntity: AppEntity {
    let id: UUID
    var name: String
    var assets: EntityCollection<AssetEntity>
}
```

Use for album photos, playlist tracks, project tasks, folder files, conversation messages, and calendar events in a calendar.

### Priority 5: Add ValueRepresentation

Use on `Transferable` entities when they can be exported as system-known structured values, especially `PlaceDescriptor` for places and `IntentPerson` for contact-like entities. This is not arbitrary object serialization; if no system value fits, improve schemas, indexing, queries, and app-specific intents instead. See [value-representation-and-structured-transfer.md](value-representation-and-structured-transfer.md).

### Priority 6: Add UnionValue parameters

```swift
@UnionValue
enum ShareTarget {
    case person(IntentPerson)
    case group(GroupEntity)
    case project(ProjectEntity)
}
```

Use when Siri or Shortcuts should accept several target types.

### Priority 7: Adopt LongRunningIntent and execution targets

Use for work that previously timed out or required clumsy foregrounding: large exports, video/image processing, local ML analysis, sync repair, and bulk migration.

Declare execution targets for intents that must run in a specific process or extension.

### Priority 8: Move to AppIntentsTesting

Add tests for intent execution, entity queries, chained intents, view annotations, Spotlight query, snippets, long-running progress, and cancellation.

## Compatibility strategy

### Do not break shipped intents

If a public iOS 26 intent exists, keep it.

```swift
struct OldCreateTaskIntent: DeprecatedAppIntent {
    static let title: LocalizedStringResource = "Create Task"
    static let intentDeprecation = IntentDeprecation(
        recommendedIntents: [CreateTaskIntent.self],
        message: "Use the updated Create Task action."
    )

    @Parameter var title: String

    func perform() async throws -> some ReturnsValue<TaskEntity> {
        var newIntent = CreateTaskIntent()
        newIntent.title = title
        return try await newIntent.perform()
    }
}
```

### Keep entity ID compatibility

```swift
struct TaskIDResolver {
    func resolve(_ legacyOrCurrentID: String) async throws -> TaskRecord? {
        if let uuid = UUID(uuidString: legacyOrCurrentID) {
            return try await store.task(localID: uuid)
        }
        if legacyOrCurrentID.hasPrefix("cloud:") {
            return try await store.task(cloudID: legacyOrCurrentID)
        }
        return try await migrationMap.record(forLegacyID: legacyOrCurrentID)
    }
}
```

### Avoid parameter type churn

Do not change a parameter from `String` to `TaskEntity` in place if users may have shortcuts. Add a new intent and deprecate the old one.

### Add optional parameters carefully

Optional parameters are generally safer, but schema-conforming Siri behavior may depend on the schema’s expected shape. Test Siri and Shortcuts.

## Migration plan template

```text
1. Inventory existing intents, entities, enums, shortcuts, donations, and indexes.
2. Identify public contract: anything users can put in Shortcuts or automations.
3. Mark schema candidates.
4. Add or improve entities/queries first.
5. Add OpenIntent for every durable entity.
6. Add schema-conforming replacement intents.
7. Bridge/deprecate old intents.
8. Migrate indexing to IndexedEntity/CoreSpotlight association.
9. Add onscreen annotations and Transferable exports.
10. Add iOS 27 enhancements: RelevantEntities, SyncableEntity, EntityCollection, ValueRepresentation, LongRunningIntent, ExecutionTargets.
11. Add AppIntentsTesting coverage.
12. Test old shortcuts from prior app versions.
13. Release with telemetry for intent errors, without logging sensitive parameter values.
```

## iOS 26 feature deepening

If you are not ready for iOS 27-only code, improve iOS 26 surfaces first:

- Interactive snippets: result snippets, confirmation snippets, control intents, compact design.
- Visual Intelligence: semantic content search, `IntentValueQuery`, `SemanticContentDescriptor`, OpenIntent for results.
- Onscreen annotations: NSUserActivity, rows/cards/thumbnails, selections, UIKit/AppKit equivalents.
- Transferable: plain text, rich text, PDF, image, file, metadata redaction.
- Foreground and target content: foreground continuation and active editor/selection targeting.

## iOS 27 feature deepening

- App Schemas: use schema intents/entities/enums and test natural requests, not only exact phrases.
- RelevantEntities: feed current context, clear stale values, keep lists small.
- SyncableEntity: model local + stable sync IDs and test reinstall/sync.
- LongRunningIntent: progress, cancellation, persisted job state, energy-aware scheduling.
- ExecutionTargets: separate app-only navigation from extension-safe mutations.
- AppIntentsTesting: test framework integration, annotations, Spotlight, and chains.

## UIKit migration track

A UIKit codebase should migrate in this order:

1. Adopt/verify `UISceneDelegate` and remove assumptions that the process has one window.
2. Extract a per-scene coordinator with semantic routes.
3. Replace intent-side global navigator/window lookup with `UISceneAppIntent` or `AppIntentSceneDelegate`; assign each scene-targeted intent exactly one navigation owner.
4. Add a primary `NSUserActivity.appEntityIdentifier` to detail/editor screens and reuse UIKit’s existing `AppEntityAnnotatable` conformances rather than declaring new ones.
5. Replace ad hoc per-cell annotations with `UITableViewAppIntentsDataSource` or `UICollectionViewAppIntentsDataSource` for large reusable lists.
6. Clear annotations during cell reuse and add privacy/redaction policy.
7. Add `appEntityUIElementProvider` to custom canvases.
8. Add `SiriTipUIView` using `setIntent(intent:)` and use `ShortcutsUIButton(style:)` for the app’s Shortcuts page.
9. Audit drag delegates for iOS 27 Siri/context-menu resource loading; remove presentation and animation from `sessionWillBegin`.
10. Add cold-launch, multiwindow, diffable snapshot, cell reuse, and drag-provider tests.

Do not migrate the app’s entire UI to SwiftUI merely to use App Intents. Snippet, widget, control, Live Activity, and optional Shortcuts-link files can remain isolated SwiftUI surfaces over a shared semantic/domain layer.

## Migration risk register

| Risk | Why it matters | Mitigation |
| --- | --- | --- |
| Changed entity ID | Breaks old shortcuts/donations/index/open | Add resolver and migration map. |
| Removed intent | Breaks user shortcuts | Keep as DeprecatedAppIntent wrapper. |
| Added required parameter | Breaks old shortcut configuration | Add optional/default or new intent. |
| Changed enum raw value | Breaks serialized shortcuts | Never change raw values; add new cases. |
| Over-indexing private content | Privacy issue | Audit indexed properties and opt-outs. |
| New schema mismatch | Siri performs wrong action | Use closest schema only; test natural language. |
| Extension dependency missing | Widget/Siri action fails | Use shared package or execution target. |
| Long-running work duplicates | Retry creates duplicates | Add idempotency/job IDs. |
| Snippet state mutation | Inconsistent UI/action result | Move mutation to explicit action intent. |
| Cell reuse stale annotations | Siri acts on wrong item | Clear/update annotations during reuse. |

## Release notes guidance

Describe user value, not framework names:

- “You can now ask Siri to create, find, and update projects.”
- “Spotlight can find your documents by content.”
- “Siri understands the project or task currently on screen.”
- “Shortcuts can now use tasks, projects, and documents as typed values.”
- “Long exports show progress and can be cancelled.”

Avoid saying “we added App Schemas and IndexedEntity” in user-facing notes unless the audience is developers.

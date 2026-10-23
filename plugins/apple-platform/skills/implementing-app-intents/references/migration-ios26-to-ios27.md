# Migration from iOS 26 to iOS 27 App Intents

Check [current availability](sdk-availability-and-verification.md#current-documentation-check--2026-10-23) for SDK-specific examples; retain older-SDK build lanes only when required by the project.

## Goal

Keep the iOS 26 integration working while adopting newer selected-SDK improvements that make Siri and Apple Intelligence more capable. Avoid breaking existing shortcuts, donations, indexes, and entity IDs.

## iOS 26 baseline checklist

Before adopting iOS 27-specific features, ensure the app already has:

Use the current availability reference and selected SDK declarations for this surface. Omit or source-gate unsupported APIs only when preserving a required older-SDK build lane; runtime gates alone cannot supply missing declarations.

## iOS 27 adoption priorities

Use the current availability reference and selected SDK declarations for this surface. Omit or source-gate unsupported APIs only when preserving a required older-SDK build lane; runtime gates alone cannot supply missing declarations.

### Priority 1: App Schemas audit

Map each entity/action to verified schema domains.

```text
Custom OpenTaskIntent -> custom entity/intent unless a selected SDK declares a matching schema
Custom SearchIntent -> .system search-in-app or verified domain search schema
Custom ImportPhotoIntent -> photos/files schema if applicable
Custom MessageAction -> mail schema only when actually mail-like; no messages domain in iPhoneOS 26.5
```

Actions:

- Add schema annotations to matching intents/entities/enums.
- Add missing schema-required properties.
- Split overloaded custom intents into schema-conforming actions.
- Use `isAssistantOnly` for new Siri-only schema actions.
- Keep old public intents as wrappers/deprecated types if users may have shortcuts.

### Priority 2: Strengthen entity identity without assuming SyncableEntity

Use the current availability reference and selected SDK declarations for this surface. Omit or source-gate unsupported APIs only when preserving a required older-SDK build lane; runtime gates alone cannot supply missing declarations.

```swift
struct TaskIDResolver {
    func entityID(localID: UUID, cloudID: String?) -> String {
        cloudID.map { "cloud:\($0)" } ?? "local:\(localID.uuidString)"
    }
}
```

If a selected SDK later declares `SyncableEntity`, wrap the existing mapping. Do not change the public entity ID shape casually.

Actions:

- Preserve old IDs for old shortcuts.
- Add migration lookup from old ID to new stable ID.
- Handle offline/local-only entities.
- Avoid changing raw ID semantics of shipped entities unless you provide compatibility.

### Priority 3: Add supported media/audio suggestion APIs

Apple documents `RelevantEntities` on iOS 27+ for media suggestions using supported audio contexts, such as Now Playing and workouts. It is not a general registry for documents, projects, routes, or arbitrary selected items. Use entity queries, screen annotations, and Spotlight for those surfaces. See [the current availability table](sdk-availability-and-verification.md#current-documentation-check--2026-10-23).

Do not replace Spotlight indexing with relevance hints.

### Priority 4: Model large relationships; adopt EntityCollection only if present

Use the current availability reference and selected SDK declarations for this surface. Omit or source-gate unsupported APIs only when preserving a required older-SDK build lane; runtime gates alone cannot supply missing declarations.

```swift
struct AlbumEntity: AppEntity {
    let id: UUID
    var name: String
    var assetCount: Int
}
```

If a selected SDK declares AppIntents `EntityCollection`, use it for album photos, playlist tracks, project tasks, folder files, conversation messages, and calendar events only after verifying the declaration is the AppIntents type and not a RealityKit name collision.

### Priority 5: Add structured value mappers now; transfer wrappers only if present

Use the current availability reference and selected SDK declarations for this surface. Omit or source-gate unsupported APIs only when preserving a required older-SDK build lane; runtime gates alone cannot supply missing declarations.

Use pure mappers on entities when they can be represented as system-known structured values, especially `PlaceDescriptor` for places and `IntentPerson` for contact-like entities. Add `ValueRepresentation` / `IntentValueRepresentation` only in source compiled with an SDK that declares those symbols. See [value-representation-and-structured-transfer.md](value-representation-and-structured-transfer.md).

### Priority 6: Use @UnionValue parameters where useful

`@UnionValue` is present in the iPhoneOS 26.5 SDK.

```swift
@UnionValue
enum ShareTarget {
    case person(IntentPerson)
    case group(GroupEntity)
    case project(ProjectEntity)
}
```

Use when Siri or Shortcuts should accept several target types.

### Priority 7: Use progress today; long-running/cancellable/execution-target APIs only if present

Use the current availability reference and selected SDK declarations for this surface. Omit or source-gate unsupported APIs only when preserving a required older-SDK build lane; runtime gates alone cannot supply missing declarations.

For large exports, video/image processing, local ML analysis, sync repair, and bulk migration, ship a progress-aware, idempotent, cancellation-cooperative service now. Add long-running/execution-target protocol conformances only when the selected SDK declares them.

### Priority 8: Use XCTest/manual tests today; AppIntentsTesting only if present

Use the current availability reference and selected SDK declarations for this surface. Omit or source-gate unsupported APIs only when preserving a required older-SDK build lane; runtime gates alone cannot supply missing declarations.

## Compatibility strategy

### Do not break shipped intents

If a public iOS 26 intent exists, keep it. `DeprecatedAppIntent` and `IntentDeprecation` are iOS 17 APIs.

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
        if legacyOrCurrentID.hasPrefix("local:"),
           let uuid = UUID(uuidString: String(legacyOrCurrentID.dropFirst("local:".count))) {
            return try await store.task(localID: uuid)
        }
        if let uuid = UUID(uuidString: legacyOrCurrentID) {
            return try await store.task(localID: uuid) // Historical bare UUID.
        }
        if legacyOrCurrentID.hasPrefix("cloud:") {
            return try await store.task(cloudID: String(legacyOrCurrentID.dropFirst("cloud:".count)))
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
9. Add primary `NSUserActivity.appEntityIdentifier` annotation and Transferable exports; add list/view/canvas annotations only if the selected SDK supports them.
10. Add selected-SDK-gated enhancements only after verification: relevance APIs, SyncableEntity, AppIntents EntityCollection, ValueRepresentation/IntentValueRepresentation, LongRunningIntent, CancellableIntent, ExecutionTargets.
11. Add AppIntentsTesting coverage only if the selected SDK provides that framework; otherwise keep XCTest/manual coverage.
12. Test old shortcuts from prior app versions.
13. Release with telemetry for intent errors, without logging sensitive parameter values.
```

## iOS 26 feature deepening

If you are not ready for selected-SDK-only code, improve iOS 26.5-compatible surfaces first:

Use the current availability reference and selected SDK declarations for this surface. Omit or source-gate unsupported APIs only when preserving a required older-SDK build lane; runtime gates alone cannot supply missing declarations.

## iOS 27 / selected-SDK feature deepening

- App Schemas: use verified schema intents/entities/enums and test natural requests, not only exact phrases.
- Media suggestions: if applicable, donate supported audio contexts and clear stale values.
- SyncableEntity: if present, adapt existing local/stable sync ID mapping and test reinstall/sync.
- Long-running/cancellable APIs: if present, combine progress, cancellation, persisted job state, and energy-aware scheduling.
- ExecutionTargets: if present, separate app-only navigation from extension-safe mutations.
- AppIntentsTesting: if present, add framework integration tests for execution, queries, annotations, Spotlight, and chains.

## UIKit migration track

A UIKit codebase should migrate in this order:

1. Adopt/verify `UISceneDelegate` and remove assumptions that the process has one window.
2. Extract a per-scene coordinator with semantic routes.
3. Replace intent-side global navigator/window lookup with `UISceneAppIntent` or `AppIntentSceneDelegate`; assign each scene-targeted intent exactly one navigation owner.
4. Add a primary `NSUserActivity.appEntityIdentifier` to detail/editor screens. Do not declare new `AppEntityAnnotatable` conformances, and do not use view/list/canvas annotation APIs unless the selected SDK declares them.
5. Keep reusable-list selection as stable model IDs; add `UITableViewAppIntentsDataSource` / `UICollectionViewAppIntentsDataSource` only if the selected SDK declares them.
6. Clear stable IDs and any selected-SDK-supported annotations during cell reuse; add privacy/redaction policy.
7. Keep custom-canvas semantic geometry ready; add `appEntityUIElementProvider` only if the selected SDK declares it.
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

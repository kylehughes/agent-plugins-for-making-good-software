# App Intents Reference for iOS 26 and iOS 27

## Core mental model

App Intents is the semantic interface between your app and system experiences. It does not only power Shortcuts. It is how your app publishes actions, content, relationships, context, and representations to Siri, Apple Intelligence, Spotlight, widgets, controls, Live Activities, the Action button, Visual Intelligence, and other automation surfaces.

The framework has four pillars:

1. **Actions** — `AppIntent` types that do one user-meaningful operation.
2. **Objects** — `AppEntity`, `IndexedEntity`, `TransientAppEntity`, `AppEnum`, union values, entity collections, and value representations.
3. **Resolution** — entity queries, string queries, property queries, semantic indexing, value queries, suggestions, donations, relevant entities, and onscreen annotations.
4. **Execution** — foreground/background modes, snippets, dialog, confirmations, choices, undo, progress, long-running work, cancellation, dependencies, and execution targets.

For Siri and Apple Intelligence, the system needs answers to these questions:

- What content exists in the app?
- Which content is the user looking at now?
- Which content is selected?
- Which content can be searched semantically?
- Which actions can be performed on each kind of content?
- Which actions are safe without confirmation?
- Which result should be spoken, shown, transferred, opened, or passed to another action?
- Which entity identifiers remain stable across devices and sync?
- Which operations require UI, a particular scene, an extension, or long-running background execution?

## iOS 26 vs iOS 27 orientation

Use these as implementation buckets, not a substitute for SDK availability checks.

### iOS 26-era surfaces to implement well

- Interactive snippets from App Intents.
- Visual Intelligence / semantic content search using `IntentValueQuery` and `SemanticContentDescriptor`.
- Onscreen entity annotations in SwiftUI, UIKit, and AppKit.
- Transferable app entities for Siri, ChatGPT handoff, Shortcuts, and sharing.
- Deferred properties for expensive entity data.
- `@ComputedProperty` for computed indexed/queryable properties.
- Undoable intents and improved confirmation/choice APIs.
- Foreground continuation controls and current execution mode awareness.
- `TargetContentProvidingIntent` and `.onAppIntentExecution` for scene/view-directed actions.
- `AppIntentsPackage` for exposing intents from Swift packages and static libraries.
- Better discoverability in Shortcuts and Spotlight when parameter summaries and queries are correct.

### iOS 27-era surfaces to consider

- Broader and deeper App Schemas for Siri.
- App entities and app actions used by Siri for more contextual and personal requests.
- `ValueRepresentation` / `IntentValueRepresentation` for transferring entities as system-known structured values across apps.
- `RelevantEntities` for context-specific suggestions beyond Spotlight indexing and donations.
- `EntityCollection` for passing large or lazy collections by identifier.
- `SyncableEntity` and `SyncableEntityIdentifier` for stable local/synced identity.
- Native parameter support for richer system values such as durations and person-name components.
- `@UnionValue` parameters that can accept one of several value/entity types.
- `LongRunningIntent`, progress reporting, cancellable intent behavior, and long-duration background execution.
- Background GPU execution support where the app capability and platform allow it.
- `ExecutionTargets` for declaring whether an intent should run in the app, App Intents extension, or WidgetKit extension.
- `AppIntentsTesting` for integration tests that exercise the same framework paths used by Siri, Shortcuts, Spotlight, and widgets.

## Structured value transfer orientation

For cross-app Siri and Apple Intelligence workflows, treat transfer as a semantic capability separate from entity resolution. Entity queries and indexing let Siri find the object. Onscreen annotations let Siri know which object the user means by “this.” `Transferable` tells the system how that object can move to another action.

Use `DataRepresentation` and `FileRepresentation` for known byte/file formats. Use `ValueRepresentation` / `IntentValueRepresentation` for system-known structured values such as `PlaceDescriptor` or `IntentPerson`. A place string is not equivalent to a `PlaceDescriptor`; a contact display name is not equivalent to `IntentPerson`. See [value-representation-and-structured-transfer.md](value-representation-and-structured-transfer.md).

## Project architecture

A scalable integration separates intent-facing code from UI and persistence code.

```text
App/
  Scenes/
  Routers/
  Views/
UIKitApp/
  SceneDelegate.swift
  SceneCoordinator.swift
  ViewControllers/
  AppIntentAnnotations/
SystemSwiftUI/
  Snippets/
  Widgets/
  Controls/
Domain/
  Models/
  Repositories/
  Permissions/
AppIntents/
  Entities/
  EntityQueries/
  Intents/
  Shortcuts/
  Snippets/
  Indexing/
  Donations/
  Relevance/
  Schemas/
  TestingSupport/
SharedPackages/
  AppIntentModels/       # Optional AppIntentsPackage
  CoreTransferExports/
```

### Recommended boundaries

- Entities are lightweight values, not managed-object subclasses.
- Queries call repositories, not UI controllers.
- `perform()` orchestrates work and returns results; it does not contain long persistence logic.
- UI navigation lives behind a main-actor router.
- Snippet views render fast and avoid side effects.
- Indexing is explicit, incremental, and permission-aware.
- Donations are event-driven and revocable.
- Tests target the App Intents boundary, not only internal repositories.
- UIKit apps own navigation in a per-scene coordinator; App Intents never discover a window by global process state.
- UIKit view/table/collection/canvas annotations are adapters over stable entity IDs, not a second entity model.
- SwiftUI-only system views such as snippets and WidgetKit remain isolated from UIKit navigation.


## UIKit architecture

UIKit uses the same entities, queries, schemas, intents, indexing, donations, and transfer representations as SwiftUI. The framework-specific boundary is scene navigation and onscreen annotation.

Preferred routing:

```text
App Intent / OpenIntent
  → system-selected UIScene
  → UISceneAppIntent or AppIntentSceneDelegate
  → per-scene coordinator
  → tab/navigation/split/modal route
```

Preferred screen context:

```text
Primary screen entity          → NSUserActivity.appEntityIdentifier
One meaningful UIView          → existing UIKit AppEntityAnnotatable support + appEntityIdentifier
UITableView / UICollectionView → appIntentsDataSource + stable item ID mapping
Custom canvas                  → UIView.appEntityUIElementProvider
```

Never use `UIApplication.shared.connectedScenes.first`, index paths as entity IDs, or a process-global “top controller” helper. Clear entity identifiers during reusable-view reset. Do not declare new `AppEntityAnnotatable` conformances; use UIKit framework types that already conform. The system owns intent execution: `AppIntentSceneDelegate` receives `any UISceneAppIntent` and must not call its `perform()` method. Give each scene-targeted intent one navigation owner—custom `performNavigation(forScene:)` or delegate routing, not both.

Use UIKit-native `SiriTipUIView` and `ShortcutsUIButton` for in-app promotion. Snippets, widgets, controls, and Live Activities are intentional SwiftUI islands in an otherwise UIKit application. See [uikit-integration.md](uikit-integration.md), [uikit-examples.md](uikit-examples.md), and [ui-framework-crosswalk.md](ui-framework-crosswalk.md).

## Design order

### 1. Inventory semantic nouns

List every object Siri might need to refer to.

Examples:

- Photo, video, album, person, memory, search result.
- Document, folder, page, slide, selection, annotation.
- Project, task, milestone, comment, attachment.
- Playlist, track, episode, station, queue item.
- Calendar, event, attendee, alarm, recurrence rule.
- Message, thread, contact, draft, attachment.
- Board, canvas object, layer, frame, shape, selection.

For each noun, decide:

```text
Noun:
User-facing name:
Durable ID:
Schema candidate:
Query by ID:
String search:
Property filters:
Safe to enumerate:
Should be indexed:
Can be opened:
Can appear on screen:
Can be selected:
Transferable representations:
Owner/account rules:
Lock-screen rules:
Privacy notes:
```

### 2. Inventory verbs

Use atomic verbs.

Good verbs:

- Open document.
- Create task.
- Mark task complete.
- Move task to project.
- Search notes.
- Export page as PDF.
- Start timer.
- Add attendee.
- Delete event.
- Summarize selected item.

Weak verbs:

- Do document action.
- Manage task.
- Run smart operation.
- Process content.
- Update everything.

Each intent should have a clear title, schema candidate, parameter summary, execution mode, result type, dialog, confirmation behavior, discoverability strategy, and test coverage.

### 3. Choose schema conformance before custom-only modeling

Use App Schemas whenever your domain is close enough. A schema gives Siri a known semantic contract. Custom-only intents can work in Shortcuts and Spotlight, but schema-conforming actions and entities give Apple Intelligence a better chance to reason over your app without you building natural-language handling.

Do not force a poor schema fit. If no schema matches, use custom entities/intents, strong display representations, robust property queries, semantic indexing, onscreen annotations, and Transferable.

### 4. Build entities and queries first

Actions that accept app content are only as good as the system’s ability to resolve that content.

A strong entity has:

- Stable ID.
- Clear type display representation.
- User-visible display representation.
- Localized title/subtitle/image.
- Query by ID.
- Text search when users name it.
- Suggested entities for pickers.
- Property query for Find actions.
- Semantic index properties for Spotlight and Apple Intelligence.
- Ownership/account checks.
- Transferable representations when the system should inspect content.

### 5. Build OpenIntent for tappable/searchable things

If an entity can appear in Spotlight, snippets, Visual Intelligence results, search results, widgets, controls, or Siri UI, implement an `OpenIntent`.

```swift
struct OpenTaskIntent: OpenIntent {
    static let title: LocalizedStringResource = "Open Task"

    @Parameter(title: "Task")
    var target: TaskEntity

    func perform() async throws -> some IntentResult {
        // Keep the semantic open contract UI-framework independent.
        return .result()
    }
}
```

### 6. Add App Shortcuts after the intent interface is correct

App Shortcuts are discovery aids. They do not replace entity modeling.

```swift
struct TaskShortcuts: AppShortcutsProvider {
    static var appShortcuts: [AppShortcut] {
        AppShortcut(
            intent: CreateTaskIntent(),
            phrases: [
                "Create a task in \(.applicationName)",
                "Add \(\.$title) to \(.applicationName)"
            ],
            shortTitle: "Create Task",
            systemImageName: "checklist"
        )
    }
}
```

### 7. Add screen context

Use onscreen annotations so Siri knows what the user means by “this,” “that,” “these,” “the one I’m looking at,” or “the selected items.”

Use:

- `NSUserActivity` for the main currently viewed entity.
- SwiftUI `.appEntityIdentifier(...)` for individual views.
- Collection annotations for lists/grids/tables and selected content.
- UIKit individual-view annotations for a handful of objects; table/collection App Intents data sources for reusable collections; `appEntityUIElementProvider` for custom canvases. Map index paths through the current data source to durable IDs and clear reused annotations.
- Transferable representations for content Siri or ChatGPT should inspect, including `ValueRepresentation` where the receiver needs a system-known structured value.

### 8. Add indexing and donations

Use indexing for durable searchable content. Use donations for observed user interactions or predicted actions. Use RelevantEntities for dynamic context-specific suggestions.

Do not use donations as a database. Do not use Spotlight indexing for private content without permission. Do not use RelevantEntities for large durable corpora that should be searched.

### 9. Add snippets and dialogs intentionally

Use dialogs for voice. Use snippets for compact visual confirmation/result UI. Do not use snippets as miniature apps.

A good snippet is fast, glanceable, compact, accessible, privacy-aware, and backed by explicit intents for controls that mutate state.

### 10. Test the integration surface

Test with AppIntentsTesting and manual system surfaces:

- Direct intent execution.
- Entity query by ID.
- Entity string query.
- Property query / Find behavior.
- Spotlight indexing/query.
- View annotations.
- App Shortcut discovery.
- Siri execution.
- Foreground/background execution.
- Widget/control execution.
- Snippet rendering.
- Cancellation/confirmation/choice flows.

## Naming guidelines

- Entity names should be user nouns, not database table names.
- Intent titles should be imperative and specific: “Create Note,” “Open Project,” “Mark Task Complete.”
- Parameter titles should match user vocabulary.
- Avoid internal names: `WorkspaceRecord`, `ManagedAsset`, `Node`, `DBObject`.
- Avoid generic titles: “Run,” “Do Action,” “Process,” “Manage.”
- Localize all display strings.

## Availability strategy

Use build-time and runtime isolation.

```swift
enum AppIntentFeatureAvailability {
    static var supportsIOS27Schemas: Bool {
        if #available(iOS 27, *) { return true }
        return false
    }

    static var supportsIOS26SnippetsAndVisualSearch: Bool {
        if #available(iOS 26, *) { return true }
        return false
    }
}
```

Patterns:

- Put iOS 27-only schema code in iOS 27-gated files when symbols are unavailable to older SDKs.
- Use `@available(iOS 27, *)` on types referencing iOS 27-only protocols or schema paths.
- Keep entity IDs, repositories, and display logic platform-neutral.
- Prefer additive intent types over changing shipped intent parameter shapes.
- Deprecate old intents with `DeprecatedAppIntent`; do not silently remove them.

## Breaking-change rules

App Intents can be embedded in user shortcuts and automation. Treat public intent types like API.

Avoid changing:

- Intent type identity.
- Parameter names/types.
- Required/default status.
- Entity ID type or semantics.
- App enum raw values.
- Schema conformance behavior.
- Intent result contract.

Safer changes:

- Improve display strings.
- Add optional parameters for Shortcuts-only use when schema allows it.
- Improve suggested entities.
- Improve indexing.
- Add new intents/entities/transfer representations/snippets.
- Add schema-conforming replacements while deprecating old custom intents.

For new assistant-only schema intents that should not become public Shortcuts surface area, set `isAssistantOnly` when appropriate.

## Privacy and authorization model

Before exposing content, define:

- Which account owns the entity?
- Is the entity available while the device is locked?
- Does it require biometric/authenticated access?
- Does it contain hidden/private fields that must not be indexed?
- Can it be exported through Transferable?
- Can Siri speak the entity title aloud?
- Can it appear in screenshots, snippets, notifications, widgets, or lock screen controls?
- Can it be donated for prediction?
- Can it be used by ChatGPT or another extension as transferred context?

Use conservative defaults. Siri and Apple Intelligence amplify whatever you expose.

## Anti-patterns and corrections

### Shortcut veneer

Only adding `AppShortcut` phrases without entities, schemas, or queries.

Fix: model entities, queries, indexing, and display representation first.

### One giant omnipotent intent

One intent takes a string command and parses it internally.

Fix: split into typed intents with typed parameters. Let Siri/Shortcuts resolve commands.

### Live ORM object as AppEntity

An `AppEntity` stores a managed object, view model, or non-Sendable object.

Fix: use a small Sendable value with durable ID and repository-backed query.

### Enumerable everything

Every entity supports `allEntities()` even for large or private corpora.

Fix: use indexed search, string query, property query, relevant suggestions, or limited suggestions.

### Indexing unredacted content

Every note/body/message is indexed with private fields.

Fix: index only user-authorized, searchable fields. Remove stale/private items promptly.

### Snippet as app clone

A complex, scroll-heavy snippet with nested navigation and hidden side effects.

Fix: make snippets compact. Use app opening for complex workflows.

### Global UIKit navigation lookup

Intent code iterates `connectedScenes`, takes the first window, or uses a process-global “top view controller.”

Fix: let the system select a `UIScene`, receive it through `UISceneAppIntent` or `AppIntentSceneDelegate`, then route through that scene’s coordinator.

### Stale reusable-view annotation

A table/collection cell keeps the `appEntityIdentifier` from its previous model after reuse.

Fix: clear identifiers in `prepareForReuse()`, map index paths through stable diffable item IDs, and test scrolling/filtering/account changes.

### Natural-language handling in app

App tries to interpret Siri utterances from a string parameter.

Fix: use App Schemas, typed parameters, AppEnum, entity queries, indexing, and screen context.

## Implementation deliverables template

For a real project, produce:

```text
1_semantic_model.md
2_intent_catalog.md
3_entity_and_query_plan.md
4_schema_mapping.md
5_spotlight_and_indexing_plan.md
6_onscreen_context_plan.md
7_transferable_plan.md
8_shortcuts_and_discovery_plan.md
9_execution_and_foregrounding_plan.md
10_testing_plan.md
11_ui_framework_integration_plan.md
```

Then implement in this sequence:

```text
Entities -> Queries -> OpenIntent -> Search/Find -> Create/Update/Delete -> Shortcuts -> Indexing -> Annotations -> UIKit/SwiftUI scene integration -> Transferable -> Snippets -> Donations/Relevance -> Tests -> Migration/deprecation
```

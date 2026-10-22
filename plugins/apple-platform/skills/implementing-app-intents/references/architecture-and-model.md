# Architecture and Model

## Core model

App Intents is the app's semantic interface to system experiences. Treat it as an application boundary, not as a shortcuts-only feature. The integration should expose a graph of actions, entities, properties, relationships, queries, indexed content, current-screen context, transfer representations, and execution rules.

The durable architecture is:

```text
Domain models and repositories
  -> App Entities / App Enums / Union values
  -> Entity queries / property queries / value queries / indexing
  -> App Intents / App Schemas / App Shortcuts
  -> Siri, Apple Intelligence, Shortcuts, Spotlight, widgets, controls, snippets, Visual Intelligence
  -> UI host adapter: SwiftUI routing or UIKit scene/coordinator routing
```

Keep the semantic model independent of the UI framework. UIKit, SwiftUI, AppKit, snippets, widgets, and controls should all consume the same entities, queries, intent types, transfer services, authorization checks, and indexing pipeline.

## Design order

1. Inventory semantic nouns: documents, tasks, projects, assets, contacts, places, pages, boards, selections, files, drafts, and other user-visible objects.
2. Decide each noun's stable identity, owner/account boundary, privacy class, display representation, schema candidate, query support, indexing eligibility, open behavior, and transfer support.
3. Inventory verbs as atomic user-observable operations: open, create, update, delete, search, export, share, summarize, capture, send, and navigate.
4. Prefer App Schema conformance when a verified schema accurately fits the noun or verb.
5. Implement entity lookup and search before complex actions. Siri and Shortcuts cannot act on entities they cannot resolve.
6. Add `OpenIntent` for every returned, indexed, visually found, or tappable entity.
7. Add Spotlight indexing and donations only after entity identity and authorization semantics are correct.
8. Add current-screen context using APIs that exist in the selected SDK.
9. Add `Transferable` exports and structured-value mappers where applicable.
10. Add snippets, confirmation, choice requests, undo, progress, foreground continuation, UIKit scene routing, widgets, controls, and tests.

## iPhoneOS 26.5 baseline surfaces

The following are buildable in the verified iPhoneOS 26.5 SDK or earlier, subject to their specific `@available` annotations:

- Core `AppIntent`, `AppEntity`, `AppShortcutsProvider`, and the entity-query family: iOS 16+.
- `IntentPerson`: iOS 16+, `AppIntents`.
- `PredictableIntent`: iOS 16+, `AppIntents`.
- `AppIntentsPackage`: iOS 17+, `AppIntents`. This is a discovery floor for intents stored in Swift packages.
- `ProgressReportingIntent`: iOS 17+, `AppIntents`.
- `DeprecatedAppIntent` and `IntentDeprecation`: iOS 17+, `AppIntents`.
- `IndexedEntity`: iOS 18+, `AppIntents`.
- `NSUserActivity.appEntityIdentifier` and `AppEntityAnnotatable`: iOS 18.2+, `AppIntents`.
- `SnippetIntent`, `ShowInAppSearchResultsIntent`, `IntentValueQuery`, `@UnionValue`, `UndoableIntent`, `ForegroundContinuableIntent`, `TargetContentProvidingIntent` / `.onAppIntentExecution`, and view-based `requestConfirmation` / `requestChoice`: present in the 26-era SDK or earlier.
- UIKit scene and promotion APIs: `UISceneAppIntent`, `AppIntentSceneDelegate`, `SiriTipUIView`, and `ShortcutsUIButton`: iOS 26, `_AppIntents_UIKit` cross-import overlay.
- `SemanticContentDescriptor`: iOS 26, `VisualIntelligence` framework.
- `PlaceDescriptor`: iOS 26, `GeoToolbox` plus `_GeoToolbox_AppIntents` overlay.

## Selected-SDK-gated / forward-looking surfaces

The following were absent from the verified iPhoneOS 26.5 SDK. Do not emit source that references them for a target compiled by that SDK:

- SwiftUI per-view `.appEntityIdentifier(...)`.
- SwiftUI `.appEntityIdentifier(forSelectionType:)`.
- UIKit `UITableViewAppIntentsDataSource` and `UICollectionViewAppIntentsDataSource`.
- UIKit `AppEntityUIElement` and `UIView.appEntityUIElementProvider`.
- Notification-content `appEntityIdentifiers`.
- `ValueRepresentation` and `IntentValueRepresentation`.
- `RelevantEntities`.
- AppIntents `EntityCollection`. Ignore unrelated RealityKit types with the same name.
- `SyncableEntity` and `SyncableEntityIdentifier`.
- `LongRunningIntent`, `CancellableIntent`, and `ExecutionTargets`.
- `AppIntentsTesting` as a framework/module.

If a beta or newer SDK declares one of these APIs, isolate the source that uses it and keep the iPhoneOS 26.5-compatible baseline intact.

## Onscreen-awareness architecture

Implementation verified against iPhoneOS 26.5:

```text
Primary detail object on screen
  -> NSUserActivity(activityType: ...)
  -> activity.appEntityIdentifier = EntityIdentifier(for: entity)
  -> userActivity = activity
  -> activity.becomeCurrent()
```

That is the only buildable current-screen entity annotation path verified in iPhoneOS 26.5. It is appropriate for detail screens, selected documents, currently viewed assets, active boards, active mail drafts, and other primary objects.

Forward-looking APIs for per-view/list/collection/canvas awareness should be treated as adapters over the same stable entity IDs, not as a second model. Keep reusable cells, diffable IDs, selection state, and canvas element geometry clean today so those adapters are easy to add when the selected SDK declares them.

## UIKit host architecture

UIKit apps should route scene-targeted intents through per-scene coordinators:

```text
App Intent / OpenIntent
  -> system-selected UIScene
  -> UISceneAppIntent or AppIntentSceneDelegate
  -> SceneCoordinator
  -> tab/navigation/split/modal route
```

Rules:

- Import `UIKit` and `AppIntents`; UIKit pairing APIs arrive through the `_AppIntents_UIKit` cross-import overlay.
- Do not navigate via `UIApplication.shared.connectedScenes.first`.
- Do not call `perform()` from `AppIntentSceneDelegate.scene(_:willPerformAppIntent:)`.
- Give each scene-targeted intent one navigation owner: custom `performNavigation(forScene:)` or scene-delegate routing, not both.
- Use `NSUserActivity.appEntityIdentifier` for current iPhoneOS 26.5 screen context.
- Treat table/collection/canvas annotation APIs as selected-SDK-gated until verified.

## Package placement strategy

Core App Intents can support iOS 16, but package discovery has a higher floor:

- If an intent type is compiled into the main app target, core protocols can work on iOS 16 where the specific protocol is available.
- If an intent type lives in a Swift package that depends on `AppIntentsPackage` discovery, that package-discovery path is iOS 17+.
- For apps with an iOS 16 deployment target, either keep iOS-16-needed intent declarations in the app target or accept that package-discovered intents have an effective iOS 17 floor.

## Verification rule

Before generating load-bearing source, verify the selected SDK. Runtime `#available` checks do not solve missing compile-time declarations. Use [sdk-availability-and-verification.md](sdk-availability-and-verification.md) for the grep procedure and the iPhoneOS 26.5 verified table.

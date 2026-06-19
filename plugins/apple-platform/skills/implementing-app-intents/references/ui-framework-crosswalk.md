# SwiftUI and UIKit App Intents Crosswalk

Use this document when an implementation example is written in SwiftUI but the host application is UIKit. Most of App Intents is UI-framework independent. The differences are concentrated in screen annotation, scene routing, in-app promotion, and the small system-rendered views that Apple currently defines in SwiftUI.

## Boundary rule

Do not translate UI-independent App Intents code into UIKit. Keep these layers shared:

- `AppIntent`, schema-conforming intents, parameters, summaries, dialogs, confirmations, and result types.
- `AppEntity`, `IndexedEntity`, `AppEnum`, queries, property queries, value queries, and indexing.
- App Shortcuts, donations, relevance, `Transferable`, execution modes, and extension packaging.
- Domain services, repositories, authorization, and idempotency.

Translate only the app-facing presentation and navigation layer.

## API crosswalk

| Goal | SwiftUI | UIKit | Notes |
| --- | --- | --- | --- |
| Publish the primary entity on a screen | `.userActivity(...)` | Create/update an `NSUserActivity`, set `appEntityIdentifier`, assign it to the view controller or call `becomeCurrent()` | Keep one primary activity per semantic screen. Invalidate it when it stops representing visible content. |
| Annotate one visible object | `.appEntityIdentifier(...)` | Set `appEntityIdentifier` on a UIKit framework object that already adopts `AppEntityAnnotatable` | `UIView` subclasses inherit support. Do not declare new protocol conformances. Clear or replace identifiers during reuse. |
| Annotate a list with selection support | `.appEntityIdentifier(forSelectionType:)` | Set `tableView.appIntentsDataSource` and implement `UITableViewAppIntentsDataSource` | Collection annotation is preferable to attaching identifiers to hundreds of reusable rows. |
| Annotate a collection with selection support | `.appEntityIdentifier(forSelectionType:)` | Set `collectionView.appIntentsDataSource` and implement `UICollectionViewAppIntentsDataSource` | Use stable diffable-data-source item IDs rather than index paths as entity identity. |
| Annotate a custom canvas | `.appEntityUIElements(...)` | Assign `UIView.appEntityUIElementProvider` | Return current bounds and selection state. Keep the provider fast and side-effect free. |
| Route an intent into the active UI | `.onAppIntentExecution(...)` | Adopt `UISceneAppIntent` or make the scene delegate conform to `AppIntentSceneDelegate` | Choose exactly one navigation owner per intent type. UIKit routing is scene-aware; never fall back to a process-global navigation singleton. |
| Select which scene handles an intent | `.handlesExternalEvents(...)` | Configure UIKit scene activation conditions and scene-role policy | The scene delegate remains the final owner of navigation state. |
| Promote a Siri invocation | `SiriTipView` | `SiriTipUIView`; call `setIntent(intent:)` before presentation | Place it next to the feature it invokes and honor `isPresented`. |
| Link to Shortcuts | `ShortcutsLink` | `ShortcutsUIButton(style:)` | Prefer the native UIKit button; do not build a private URL workaround. |
| Render a custom result/confirmation snippet | `SnippetIntent` returning a SwiftUI view | The same SwiftUI snippet implementation | Snippets are system-rendered SwiftUI even when the app itself is UIKit. No UIKit snippet-view protocol exists. |
| Build widgets, controls, and Live Activities | WidgetKit/SwiftUI | WidgetKit/SwiftUI extension sharing UIKit app models | Treat these as intentional SwiftUI islands, not a reason to migrate the app UI. |
| Open an entity from Spotlight/Visual Intelligence | `OpenIntent` plus SwiftUI navigation handler | `OpenIntent` plus scene coordinator/router | Ensure warm launch, cold launch, and multiple-window behavior are all deterministic. |
| Donate a user interaction | Donate from the SwiftUI action or model layer | Donate from the `UIAction`, target-action handler, delegate callback, or coordinator after success | Do not donate when the same App Intent executes, or you can create duplicated behavioral signals. |
| Supply transferable content | `Transferable` | The same `Transferable` conformance; optionally bridge to `NSItemProvider`/drag and drop | Keep exports authorization-aware and bounded in size. |
| Expose contextual menu content to Siri | View annotations and transfer representations | View annotations plus well-behaved drag delegates | On iOS 27, Siri can request drag resources from UIKit context menus without an ordinary user-started drag. |

## Scene-routing decision table

| Situation | Preferred UIKit mechanism |
| --- | --- |
| Intent navigates a particular scene and can implement navigation on the intent type | `UISceneAppIntent.performNavigation(forScene:)` |
| Existing scene coordinator should inspect all incoming intents centrally | `AppIntentSceneDelegate.scene(_:willPerformAppIntent:)` |
| Intent performs no UI work | Plain `AppIntent.perform()` calling a UI-independent domain service |
| Intent creates or opens content after a background action | Return `OpensIntent`/an `OpenIntent`; route that open operation through the selected scene |
| Operation applies to the currently edited document or selection | `TargetContentProvidingIntent` plus UIKit scene targeting; reject or clarify when no suitable scene exists |
| App supports several independent windows | Per-scene coordinators and activation conditions; never “first connected scene” routing |
| App still uses only `UIApplicationDelegate` lifecycle | Migrate to `UISceneDelegate` before treating Siri/UIKit routing as production-ready |

The `AppIntentSceneDelegate` callback receives `any UISceneAppIntent`. It must not call `perform()`. A type with custom `performNavigation(forScene:)` should be ignored by the delegate route mapper; a delegate-routed type should not also implement custom navigation.

## What remains SwiftUI in a UIKit app

Some system integrations intentionally accept SwiftUI views. Keep these in a small target or folder with no ownership of app navigation:

- Interactive and confirmation snippet views.
- WidgetKit widgets, controls, and Live Activity UIs.
- Optional previews of entity or snippet content.

A clean UIKit application can therefore contain a few SwiftUI files without adopting SwiftUI navigation or view architecture. Siri tips and the link to the app’s Shortcuts page do not require such a bridge because `SiriTipUIView` and `ShortcutsUIButton` are native UIKit types.

## UIKit translation traps

### Do not put UIKit objects in entities

An `AppEntity` is a semantic value. Never store a `UIViewController`, `UIView`, `UIWindowScene`, `UIImageView`, or diffable data source in it. Store stable IDs and query the domain layer.

### Do not make `perform()` hunt for a window

Avoid code such as:

```swift
UIApplication.shared.connectedScenes
    .compactMap { $0 as? UIWindowScene }
    .first?
    .keyWindow?
    .rootViewController
```

This is nondeterministic with multiple scenes, external displays, iPhone Mirroring, restoration, and tests. Use the scene APIs designed for App Intents.

### Do not equate index path with identity

Index paths are presentation coordinates. They change after sorting, filtering, and diffable snapshots. Map the index path to the stable item ID, then construct the `EntityIdentifier` from that ID.

### Do not leave reused cells annotated with old entities

Clear the annotation in `prepareForReuse()` and assign it every time the cell is configured. A stale annotation is worse than no annotation because Siri may act on the wrong object.

### Do not add `AppEntityAnnotatable` conformances

Apple reserves `AppEntityAnnotatable` conformance for framework types. Use the conformance already supplied by `UIView`, `NSUserActivity`, and other supported system objects. A custom `UIView` subclass inherits the capability; a nonconforming custom object should be represented through a conforming view/activity or a table, collection, or canvas annotation API.

### Do not route a scene intent twice

Choose intent-owned `performNavigation(forScene:)` or delegate-owned routing. Do not implement both for the same type. `AppIntentSceneDelegate` may still observe direct-navigation intents, so the delegate route mapper must explicitly ignore them.

### Do not reimplement snippets in UIKit

A snippet is not an in-app modal. It is system UI driven by a `SnippetIntent`, and its view is SwiftUI. Keep mutation in explicit App Intents attached to snippet buttons/toggles.

### Do not present UI from drag-session startup

Apple Intelligence may invoke a UIKit drag provider from a context menu without the usual gesture path. Loading data must not present modals, run animations, or mutate selection in `sessionWillBegin`.

## Suggested source layout for a UIKit app

```text
App/
  AppDelegate.swift
  SceneDelegate.swift
  SceneCoordinator.swift
  NavigationRoute.swift
UIKit/
  ViewControllers/
  Cells/
  AppIntentAnnotations/
  SiriPromotion/
AppIntents/
  Entities/
  Queries/
  Intents/
  Schemas/
  Shortcuts/
  Indexing/
  Donations/
  Relevance/
  Transfer/
SystemSwiftUI/
  Snippets/
  Widgets/
  Controls/
  LiveActivities/
Domain/
  Models/
  Repositories/
  Services/
```

See [uikit-integration.md](uikit-integration.md) for architecture and operational rules and [uikit-examples.md](uikit-examples.md) for code patterns.

# UIKit Integration for App Intents, Siri, and Apple Intelligence

Check [current availability](sdk-availability-and-verification.md#current-documentation-check--2026-10-23) for SDK-specific examples; retain older-SDK build lanes only when required by the project.

This document treats UIKit as a first-class host for App Intents on iOS 26 and iOS 27. It covers scene routing, `NSUserActivity` primary-screen awareness, selected-SDK-gated list/canvas annotation strategy, Siri promotion, drag and drop, interaction donations, multiwindow behavior, mixed Objective-C applications, testing, and the SwiftUI islands that remain required by system frameworks.

Use the current availability reference and selected SDK declarations for this surface. Omit or source-gate unsupported APIs only when preserving a required older-SDK build lane; runtime gates alone cannot supply missing declarations.

## 1. UIKit is not a second-class App Intents client

The semantic layer is identical for SwiftUI and UIKit:

- App Schemas and schema-conforming intents.
- `AppIntent`, `OpenIntent`, create/update/delete/search/control intents.
- `AppEntity`, `IndexedEntity`, `AppEnum`, `@UnionValue`, structured value mappers, and entity ownership.
- `EntityQuery`, `EntityStringQuery`, `EntityPropertyQuery`, `IntentValueQuery`, and indexing.
- App Shortcuts, donations, dialog, confirmations, progress reporting, selected-SDK-gated relevance/cancellation APIs, and extension execution.
- `Transferable` and representations used by Siri, Shortcuts, Spotlight, Visual Intelligence, sharing, and drag and drop.

UIKit-specific work is concentrated in four places:

1. Selecting and navigating the correct `UIScene`.
2. Describing visible UIKit content with `NSUserActivity.appEntityIdentifier`, plus additional annotation APIs only when the selected SDK declares them.
3. Promoting Siri/Shortcuts actions in UIKit UI.
4. Bridging unavoidable SwiftUI system surfaces such as snippets and WidgetKit; Siri and Shortcuts promotion itself has native UIKit views.

## 2. Required architecture

A production UIKit integration should have these boundaries:

```text
App Intent or system invocation
  ↓
Entity/query/schema layer
  ↓
Domain service or repository
  ↓
Result / OpenIntent / scene navigation request
  ↓
Selected UIScene
  ↓
Per-scene coordinator
  ↓
UIKit navigation containers and view controllers
```

The inverse path handles context:

```text
Visible UIKit screen / selected cell / custom canvas
  ↓
Stable EntityIdentifier
  ↓
NSUserActivity or view/collection/canvas annotation
  ↓
Siri and Apple Intelligence context
```

### Recommended project boundaries

```text
Domain/
  ProjectRepository.swift
  ProjectService.swift
  AuthorizationService.swift
AppIntents/
  Entities/
  Queries/
  Intents/
  Schemas/
  Indexing/
  Donations/
  Transfer/
UIKitApp/
  AppDelegate.swift
  SceneDelegate.swift
  SceneCoordinator.swift
  NavigationRoute.swift
  ViewControllers/
  AppIntentAnnotations/
SystemSwiftUI/
  Snippets/
  Widgets/
  Controls/
```

Rules:

- Keep UIKit imports out of entities, queries, and repositories.
- Keep `UIViewController` lookup out of intent `perform()` methods.
- Give every `UIScene` its own coordinator and navigation state.
- Make routing `@MainActor`.
- Make mutations idempotent because system invocations can be retried or resumed.
- Treat the semantic ID as authoritative; never use an index path, pointer identity, or controller instance as an entity ID.

## 3. Scene lifecycle is foundational

UIKit App Intent navigation should be built on `UISceneDelegate`. It is not enough for a modern multiwindow app to route everything through `UIApplicationDelegate` or a global “top view controller” helper.

Scene lifecycle matters because:

- An App Intent can activate or create a scene.
- iPad can show multiple windows from the same app.
- External displays and iPhone Mirroring create additional scene contexts.
- A currently editing scene may be an inappropriate target for an unrelated open intent.
- Restoration can recreate navigation state before the App Intent is delivered.
- UI tests need deterministic scene selection.

For apps built with current SDKs, treat scene lifecycle adoption as a prerequisite rather than an optional enhancement.

## 4. Bootstrap dependencies once; route per scene

Register UI-independent dependencies during app startup. Create UI coordinators during scene connection.

Good dependency examples:

- Repository actors.
- Authentication/authorization services.
- Sync engines.
- Indexing and donation services.
- File export services.

Bad dependencies:

- A single process-wide `UINavigationController`.
- The “currently visible” view controller.
- A scene chosen by iterating `connectedScenes`.
- A window retained by an App Entity or query.

A global dependency may describe domain state. Navigation state must remain scene-local.

## 5. UIKit navigation mechanisms and ownership

### 5.1 `UISceneAppIntent`

Use `UISceneAppIntent` when an intent should receive the `UIScene` chosen by the system and perform navigation for that scene. Its scene navigation method is main-actor UI work.

This is the closest UIKit equivalent to SwiftUI view-control handling. It avoids reaching through global state from `perform()`.

Use it for:

- Opening an entity in a selected window.
- Switching the current tab and pushing a detail controller.
- Showing search results in a scene.
- Applying a navigation-only command to a compatible scene.

Do not use it to perform the domain mutation twice. The intent action and scene navigation are separate responsibilities.

### 5.2 `AppIntentSceneDelegate`

Make the `UISceneDelegate` conform to `AppIntentSceneDelegate` when the coordinator should centrally inspect incoming intents. The callback's intent parameter is `any UISceneAppIntent`, not an arbitrary `any AppIntent`:

```swift
func scene(
    _ scene: UIScene,
    willPerformAppIntent appIntent: any UISceneAppIntent
)
```

The delegate receives the scene-targeted App Intent shortly before execution/navigation. Important rule: **do not call `perform()` on the supplied intent**. Apple documents that as a programmer error. The framework owns execution; the callback is for scene preparation and navigation.

Use this when:

- The app already centralizes URL, activity, notification, and restoration routing in the scene delegate.
- Several intent types share routing policy.
- The scene must dismiss or preserve editing UI based on intent type.
- You need one place to log and test incoming navigation requests.

### 5.3 Choose one navigation owner per intent

For each `UISceneAppIntent` type, choose exactly one owner:

- **Intent-owned navigation:** implement `performNavigation(forScene:)`; the scene-delegate callback may observe the type but must not route it.
- **Delegate-owned navigation:** let the protocol's default scene-navigation implementation stand and map the type in `AppIntentSceneDelegate`; do not also implement routing in `performNavigation(forScene:)`.

The callback can be delivered for scene-targeted intents regardless of where navigation logic lives. Mapping the same intent in both places is a common source of duplicate pushes, tab switches, or modals. Make ownership visible in the route table and test that direct-navigation intents deliberately map to `nil`.

### 5.4 Plain `perform()` with no scene access

Use a plain `AppIntent.perform()` for actions that do not need UIKit:

- Create, update, delete, archive, or tag content.
- Start/stop a service.
- Export a file.
- Query status and return dialog.
- Schedule work or update an index.

If the result should open UI, return an open intent or an `OpensIntent` result rather than directly finding a controller.

## 6. Scene selection and activation policy

A multiwindow app needs an explicit policy for which scene can handle which intent.

Consider:

- Scene role and content identifier.
- Whether the scene is editing unsaved content.
- Whether the entity is already open in another scene.
- Account/workspace represented by the scene.
- Whether opening should reuse a scene or create a new one.
- Whether a request is navigation-only or destructive.

Recommended rules:

1. Prefer a scene already showing the target entity.
2. Otherwise prefer a foreground-active scene in the same account/workspace.
3. Reject scenes in modal destructive flows or incompatible editing modes.
4. Create a new scene only when that matches the app’s window model.
5. Never route by “first connected scene.” Set iteration order is not semantic policy.

Keep activation predicates and coordinator acceptance logic aligned. A scene that says it can handle an intent must actually be able to route it.

### Configure UIKit activation conditions

`UIScene.activationConditions` gives UIKit a declarative filter and preference for incoming target-content identifiers. Configure it from the scene's account, workspace, or document affinity rather than process-global state.

```swift
@MainActor
func configureActivationConditions(
    for scene: UIScene,
    workspaceID: UUID,
    preferredDocumentID: UUID?
) {
    let workspacePrefix = "workspace:\(workspaceID.uuidString)/"
    let conditions = UISceneActivationConditions()

    conditions.canActivateForTargetContentIdentifierPredicate = NSPredicate(
        format: "SELF BEGINSWITH %@",
        workspacePrefix
    )

    if let preferredDocumentID {
        let preferredIdentifier = workspacePrefix
            + "document:"
            + preferredDocumentID.uuidString
        conditions.prefersToActivateForTargetContentIdentifierPredicate = NSPredicate(
            format: "SELF == %@",
            preferredIdentifier
        )
    }

    scene.activationConditions = conditions
}
```

The incoming scene-targeting operation must use the same identifier vocabulary. Treat the string as a routing namespace, not a user-visible title. Predicate details and the App Intent API that supplies the target-content identifier are SDK-sensitive; compile and test the exact shape against the selected iOS SDK. Activation conditions choose a candidate scene, while the coordinator still enforces authorization, editing-state, and route compatibility.

## 7. Cold launch and warm launch

Test both paths.

### Warm launch

The app already has a connected scene. The framework selects a scene and delivers the intent. The coordinator should route without rebuilding the entire root hierarchy.

### Cold launch

The intent may cause scene creation. `UIScene.ConnectionOptions.appIntent` identifies the App Intent that triggered connection. Apple also documents that the App Intent scene-delegate callback is delivered after scene connection.

Avoid double-routing:

- Build the window and coordinator in `willConnectTo`.
- Use connection options only to establish initial scene context when needed.
- Let the App Intent scene callback perform the actual route, or record that the connection option was consumed.
- Do not independently route the same intent from both code paths without deduplication.

A simple deduplication token can combine the intent persistent identifier and target entity ID.

## 8. Coordinator contract

Define semantic routes rather than passing controllers around:

```text
NavigationRoute
  openProject(ProjectEntity.ID)
  openTask(TaskEntity.ID)
  showSearch(String)
  showExport(ProjectEntity.ID)
  revealSelection(DocumentEntity.ID, [SelectionEntity.ID])
```

The coordinator resolves those routes against current container state:

- `UITabBarController`: select the correct tab before routing.
- `UINavigationController`: pop to a compatible stack or push a new detail.
- `UISplitViewController`: choose primary/supplementary/secondary columns.
- Modal flow: decide whether to dismiss, preserve, or refuse.
- State restoration: encode entity IDs, not controller instances.

Routing should be idempotent. Opening an entity already visible should focus or refresh it, not push duplicate copies indefinitely.

## 9. Authentication, locks, and protected data

An App Intent may arrive when:

- The app is logged out.
- The selected account changed.
- Protected data is unavailable.
- The entity was deleted or moved.
- The target requires a subscription or role.
- The device is locked.

Separate three outcomes:

1. **Not found** — stable ID no longer resolves.
2. **Not authorized** — entity exists but the current principal cannot access it.
3. **Needs foreground authentication** — action may continue after the app presents an auth flow.

Do not return a private display representation merely to explain that access failed. Prefer generic dialog and route to an authentication screen only after foreground continuation succeeds.

## 10. Primary onscreen content with `NSUserActivity`

Use `NSUserActivity` when one entity defines the screen: a project detail, document editor, conversation, now-playing item, order status, or selected photo.

UIKit lifecycle pattern:

- Create or refresh the activity when the controller becomes visible.
- Set a descriptive title and the persistent `EntityIdentifier`.
- Assign it to the view controller’s `userActivity` and make it current.
- Update it when the semantic target changes in-place.
- Resign or invalidate it when the controller no longer represents visible content.
- Never attach an entity merely because it exists in the controller’s cache.

Keep the activity’s entity and the visible navigation title synchronized. Screen OCR and structured context should not disagree.

### One primary entity, not every model object

An activity should express the screen’s main semantic subject. Use view annotations for child rows, cards, attachments, messages, or selections.

### Restoration and handoff are separate decisions

`NSUserActivity` can participate in restoration, Handoff, search, prediction, and App Intent context. Configure only the capabilities actually intended. Adding an App Entity identifier does not require exposing the activity to every other subsystem.

## 11. Selected-SDK-dependent individual UIKit view annotations

Use the current availability reference and selected SDK declarations for this surface. Omit or source-gate unsupported APIs only when preserving a required older-SDK build lane; runtime gates alone cannot supply missing declarations.

Keep this design ready, but do not compile code against it unless the selected SDK declares the relevant properties/protocols.

When available, use individual view annotations for a handful of independently meaningful objects:

- Header card and several child cards.
- An album plus its artist.
- A message bubble currently focused.
- A selected attachment preview.
- Controls that visually represent a domain entity.

Rules when the API exists:

- Assign the identifier after the view is bound to a stable model ID.
- Clear it before reuse or when the content becomes redacted.
- Annotate the semantic container, not every label and image subview.
- Do not annotate decorative views.
- Keep annotations consistent with accessibility semantics.
- Do not declare app-defined `AppEntityAnnotatable` conformances.

## 12. Selected-SDK-dependent `UITableView` collection annotations

Use the current availability reference and selected SDK declarations for this surface. Omit or source-gate unsupported APIs only when preserving a required older-SDK build lane; runtime gates alone cannot supply missing declarations.

When a selected SDK supplies a table annotation API, map an index path to an `EntityIdentifier` through the current table data source or diffable snapshot. Never derive identity from row number.

Why collection annotations are preferable when they exist:

- The system can request identifiers lazily.
- Reuse does not require hundreds of view-level annotations.
- Selection can remain meaningful after a row scrolls offscreen.
- Diffable snapshots can map directly from item ID to entity ID.

Production requirements when available:

- Return no identifier for placeholders, ads, separators, skeleton rows, redacted rows, and inaccessible content.
- Update the annotation data source when account/workspace changes.
- Ensure selected row IDs remain stable across snapshots.
- Test reorder, filter, section insertion, and animated snapshot updates.

## 13. Selected-SDK-dependent `UICollectionView` collection annotations

Use the current availability reference and selected SDK declarations for this surface. Omit or source-gate unsupported APIs only when preserving a required older-SDK build lane; runtime gates alone cannot supply missing declarations.

When a selected SDK supplies a collection annotation API, use the diffable item identifier as the bridge:

```text
IndexPath
  → diffableDataSource.itemIdentifier(for:)
  → durable domain ID
  → EntityIdentifier(for: Entity.self, identifier: ID)
```

Do not instantiate a full entity just to create its identifier. Use identifier-only construction when the selected SDK provides the required initializer.

Collection-specific concerns when available:

- Supplementary views may represent entities independently from cells.
- Orthogonal sections can expose entities outside the obvious viewport.
- Drag selection and multi-selection must use stable IDs.
- Prefetch callbacks are not evidence that content is onscreen.
- A compositional-layout decoration view should not receive an entity annotation unless it is semantic content.

## 14. Selected-SDK-dependent selection and offscreen entities

Selection is semantically important for requests such as:

- “Archive these.”
- “Send the selected photos.”
- “Add those three to the project.”
- “Explain the highlighted note.”

Use the current availability reference and selected SDK declarations for this surface. Omit or source-gate unsupported APIs only when preserving a required older-SDK build lane; runtime gates alone cannot supply missing declarations.

- Maintain selected item IDs independently of visible cells.
- Reapply visual selection after diffable snapshots.
- Remove IDs when access is revoked or items are deleted.
- Do not infer selection solely from `indexPathsForSelectedRows` if the app supports a model-level selection spanning filtered/offscreen content.

When a future selected SDK provides collection annotation APIs, expose this existing ID-based selection through the adapter.

## 15. Selected-SDK-dependent custom canvas and nonstandard content

Use the current availability reference and selected SDK declarations for this surface. Omit or source-gate unsupported APIs only when preserving a required older-SDK build lane; runtime gates alone cannot supply missing declarations.

For custom drawing surfaces, maps, timelines, editors, diagrams, games, or media canvases, keep a semantic element model that can later feed a provider:

- Persistent `EntityIdentifier` or durable domain ID.
- Bounds in the annotated view’s coordinate space.
- State such as selection.
- Optional nested subelements where supported.

Provider rules when the API exists:

- Return only elements represented in the current visual state.
- Use presentation geometry, not stale model coordinates.
- Convert world/document coordinates to the annotated view’s coordinate system.
- Clip or omit elements that cannot be meaningfully referenced.
- Keep the provider fast; Siri may request context during an interaction.
- Capture the controller/model weakly where appropriate.
- Do not perform network requests, mutate selection, or trigger layout from the provider.

## 16. Cell reuse and annotation hygiene

Every reusable view must follow this invariant:

```text
after prepareForReuse:
  represented domain ID == nil
  entity annotation == nil, if a selected SDK provides reusable-view annotations
  transferable/drag provider == nil or reset
  accessibility content == reset
```

Then configuration assigns all four from the same model snapshot.

Common serious bug:

1. In a future annotation-enabled SDK, cell A represents private message X and gets an entity identifier.
2. Cell A is reused for public message Y.
3. Labels update, but the identifier remains X.
4. Siri interprets the visible row as X.

Treat annotation reset as part of privacy and correctness, not polish.

## 17. Component-based display representation queries

When a screen shows many entities, Siri may need their names quickly to resolve “the third one” or “the blue project.” Loading every entity and image can make contextual understanding slow.

Implement display-representation querying on the entity query when supported. Return only requested components, commonly text, without fetching expensive images or deferred metadata.

Design targets:

- Batched ID lookup.
- Preserve input-to-output identity.
- Avoid N+1 database and network requests.
- Text response in tens of milliseconds for local content where feasible.
- Respect the same authorization filters as full entity resolution.

## 18. Context menus, Ask Siri, and drag providers in selected iOS 27-era SDKs

On selected iOS 27-era SDKs, UIKit menus may surface an Ask Siri entry when the system finds relevant content. In iPhoneOS 26.5, the buildable onscreen context source is the primary `NSUserActivity.appEntityIdentifier`; per-view annotations remain selected-SDK-gated.

If the selected SDK supports this flow and the app supports drag and drop, Siri may load resources through existing drag delegate methods when invoked from a context menu.

Consequences:

- A drag provider can be called without the ordinary drag gesture sequence.
- `sessionWillBegin` must not present a modal, start an animation, change selection, or assume touch input.
- Put gesture-dependent UI in `sessionDidMove` or a later phase.
- Data loading must be authorization-aware and safe when called programmatically.
- Register fast representations first and defer expensive file generation.
- A drag item’s semantic entity, visible annotation, and exported `NSItemProvider` data should refer to the same content.

This makes an existing UIKit drag implementation part of the Apple Intelligence surface. Audit it accordingly.

## 19. `Transferable` in UIKit applications

`Transferable` belongs on the entity/value layer, not the view layer. A UIKit app uses the same conformance as a SwiftUI app.

Recommended representations, in priority order where applicable:

1. System-known structured value mapping, such as `PlaceDescriptor` or `IntentPerson`; use `ValueRepresentation`/`IntentValueRepresentation` wrappers only if the selected SDK declares them.
2. Structured app-defined content type where the receiving surface actually supports that type.
3. Plain text or attributed text.
4. Image.
5. PDF or document file.
6. URL/deep link when it is a meaningful representation, not merely a fallback.

Rules:

- Export what the user is allowed to disclose now.
- Do not include hidden fields in “full content.”
- Keep generated file names safe and localized where appropriate.
- Use temporary files with cleanup.
- Cap export size or use file representations for large data.
- Avoid rendering a screenshot when structured text, PDF, or a system-known value mapper provides better semantic content.
- Do not put structured value mapping or future transfer wrappers in view-controller code; they belong beside the entity/value layer.
- Recheck permissions at export time; the entity may have been resolved earlier.

UIKit drag and share code may also expose `NSItemProvider`. Reuse the same export service so Siri transfer, drag and drop, share sheets, and App Intents do not diverge. For details and examples, see [value-representation-and-structured-transfer.md](value-representation-and-structured-transfer.md).

## 20. Visual Intelligence and UIKit navigation

Visual Intelligence integration is UI-framework neutral until the result is opened:

1. Implement `IntentValueQuery` for `SemanticContentDescriptor` from the `VisualIntelligence` framework or the relevant structured search type.
2. Return a small, relevant, ordered set of entities or a union value.
3. Implement `OpenIntent` for every returned entity type.
4. Route the open intent into the selected UIKit scene.
5. Offer a schema-conforming “show more/search in app” intent that navigates to the UIKit search experience.

UIKit concerns:

- Decode image/search input off the main actor.
- Route only the final navigation on the main actor.
- Do not keep a pixel buffer alive in a view controller longer than necessary.
- Provide a loading state when in-app continuation requires network search.
- Make the search controller restorable from structured criteria, not only an ephemeral object.

## 21. Spotlight results in UIKit

Spotlight indexing and entity queries are shared. Opening the result is scene-specific.

A strong path:

```text
Spotlight result
  → entity identifier
  → OpenIntent
  → selected UIScene
  → coordinator route
  → UIKit detail controller
```

Do not maintain a separate Spotlight-only URL route if an `OpenIntent` can be the canonical open contract. If legacy Core Spotlight activities already exist, associate them with the App Entity and converge both paths in the same coordinator.

## 22. Siri and Shortcuts promotion in UIKit

### `SiriTipUIView`

Use `SiriTipUIView` near the control or screen it automates. Apple requires calling `setIntent(intent:)` before displaying it.

Operational rules:

- Create it on the main actor.
- Set the exact intent and default parameters represented by the current UI.
- Add normal Auto Layout constraints.
- Respect `isPresented`; the framework may decide the tip should not be shown.
- Remove or update it when the current entity changes.
- Do not show several tips on one screen.
- Do not use a tip to compensate for poor App Shortcut discoverability.

### `ShortcutsUIButton`

UIKit provides `ShortcutsUIButton`, the native counterpart to SwiftUI’s `ShortcutsLink`. It opens the current app’s page in Shortcuts. Prefer it over a `UIHostingController` or a hand-built `shortcuts://` URL.

```swift
import AppIntents
import UIKit

let shortcutsButton = ShortcutsUIButton(style: .automatic)
shortcutsButton.translatesAutoresizingMaskIntoConstraints = false
view.addSubview(shortcutsButton)
```

Choose a `ShortcutsLinkStyle` that remains legible in the surrounding UI, normally `.automatic` or `.automaticOutline`. Treat the button as system-owned navigation to Shortcuts: do not attach a competing target action, replace its label, or make it responsible for app navigation.

## 23. Interactive snippets in a UIKit app

Interactive snippets are not UIKit views. A `SnippetIntent` returns a system-rendered SwiftUI view even when the containing application uses UIKit.

Architecture:

```text
UIKit app and domain services
  ↕ shared entity/query/repository layer
SnippetIntent
  → small SwiftUI snippet view
  → App Intent buttons/toggles
```

Rules:

- Keep the snippet view in a small SwiftUI-only folder/target.
- Do not import the UIKit coordinator into the snippet.
- Fetch current state in the snippet intent’s `perform()`.
- Keep the snippet intent side-effect free.
- Put mutations in explicit App Intents attached to buttons/toggles.
- Return dialog as a voice-only fallback.
- Do not use `UIHostingController` to present the system snippet yourself.

This is an intentional platform boundary, not incomplete UIKit support.

## 24. Widgets, controls, and Live Activities

A UIKit host app still implements these surfaces with WidgetKit and SwiftUI.

Share:

- Entities and enums.
- Queries and repository protocols.
- App Intent types safe for extension execution.
- App Group storage and authorization state.
- Formatting helpers that do not import UIKit.

Do not share:

- Scene coordinators.
- View controllers.
- UIApplication-only services.
- Main-app database handles that extensions cannot open safely.

Declare or isolate execution targets appropriately and test the extension process separately.

## 25. Donating UIKit interactions

Apple Intelligence knows system-run App Intents, but ordinary in-app UIKit interactions need explicit donation when they represent meaningful user behavior.

Donation candidates:

- User taps Play on a particular playlist.
- User starts navigation to a destination.
- User opens a frequently used project.
- User applies a meaningful filter or workflow.
- User starts an ongoing activity that Siri should understand later.

Donation placement:

- After the UI action succeeds.
- In the coordinator/domain service, not every cell callback.
- With a schema-conforming intent populated with the actual entities/values.
- Once per meaningful interaction, not every redraw or scroll.

Do not donate:

- Passive display.
- Prefetch or cell configuration.
- Failed/cancelled actions.
- The App Intent executing itself.
- High-frequency noise that does not express preference.

Provide deletion/revocation when account, privacy settings, or user data changes.

## 26. Notifications, Now Playing, AlarmKit, and other system surfaces

Use the current availability reference and selected SDK declarations for this surface. Omit or source-gate unsupported APIs only when preserving a required older-SDK build lane; runtime gates alone cannot supply missing declarations.

General rules for surfaces that do expose entity identifiers:

- Add persistent entity identifiers only through APIs that exist in the selected SDK.
- Do not use transient entities for persistent system annotations.
- Clear/update annotations when the underlying content changes.
- Apply lock-screen privacy policy before including entity context.

The same entity ID should resolve through the same query whether Siri receives it from an activity, media session, alarm, Spotlight, or another supported surface.

## 27. Accessibility alignment

Structured context and accessibility should describe the same object.

Audit:

- The primary activity’s entity matches the meaningful accessibility/navigation context; future view annotations should match their accessibility containers.
- Accessibility labels do not contradict `DisplayRepresentation` titles.
- Selection state matches `UIAccessibility` traits today and any future `AppEntityUIElement.State` equivalent when the selected SDK provides it.
- Hidden/redacted accessibility elements are not still exposed as App Entities.
- Custom canvas semantic bounds match the visual/accessibility frame when a future canvas annotation API is available.
- Reordered rows retain stable model identity so future annotation adapters do not expose stale entities.

Do not use accessibility labels as a substitute for App Entity modeling. They solve different problems, but inconsistency between them is a correctness signal.

## 28. Concurrency and isolation

Use these defaults:

- Scene coordinator and UIKit navigation: `@MainActor`.
- Entity/query/repository work: async and `Sendable`, usually actors for mutable stores.
- File export and semantic search: background/non-main isolation.
- `NSUserActivity` and view annotation updates: main actor.
- App Intent `perform()`: call UI-independent services; enter main actor only for the narrow UI boundary.

Do not pass `UIViewController` through `Task.detached`, store UIKit objects in an actor, or make query resolution synchronously dispatch to the main queue.

## 29. Storyboards and programmatic UIKit

Both are supported.

### Storyboard app

- Build the scene’s root controller from the storyboard.
- Create the per-scene coordinator around the instantiated root container.
- Route by semantic IDs after the hierarchy is connected.
- Avoid storyboard segue identifiers as the public App Intent contract.

### Programmatic app

- Construct the window/root hierarchy in the scene delegate or scene factory.
- Install the coordinator before App Intent callbacks can arrive.
- Keep root replacement deterministic during authentication transitions.

In either architecture, the coordinator—not the intent—knows whether navigation is a push, split-column update, tab switch, or modal.

## 30. Mixed Objective-C and Swift applications

App Intents declarations and modern schema macros are Swift-facing. A UIKit app may still contain substantial Objective-C.

Recommended bridge:

```text
Objective-C view controller action
  → @objc Swift facade or protocol
  → Swift domain service / donation service
  → App Intent model
```

Keep all App Intent types in a Swift module. Expose narrow `@objc` facade methods for:

- Updating onscreen entity annotations from Objective-C-owned screens.
- Donating a completed interaction.
- Routing an incoming intent through the Swift scene coordinator.
- Requesting a stable entity identifier from a domain ID.

Do not attempt to mirror App Entity structs into Objective-C classes. Bridge IDs and operations, not the entire semantic type system.

## 31. Extension and package boundaries

If intents live in a Swift package or App Intents extension:

- UIKit types must not leak into the package’s public entity/query layer.
- Scene-routing conformances can live in the app target as extensions when visibility allows.
- Ensure the app includes the package through `AppIntentsPackage` discovery.
- Keep shared resources localized in bundles available to each target.
- Avoid dependencies that only exist in the main app process for extension-executable intents.

A useful split is:

```text
IntentKit package: entities, enums, queries, intent declarations, repository protocols
App target: concrete repositories, scene routing, `NSUserActivity` publisher, selected-SDK-gated UIKit annotation adapters
Snippet/widget targets: SwiftUI views and extension-safe dependencies
```

## 32. Availability strategy

Use the current availability reference as the single source for SDK visibility and runtime floors. Keep version-specific implementation behind small adapters, with a fallback only for platforms or SDK build lanes the project actually supports. On a supported current SDK, implement the annotation adapter rather than leaving it as a no-op.

## 33. Performance targets

Onscreen context is requested while the user is interacting. Avoid making Siri wait for UI metadata.

Targets:

- `NSUserActivity` primary-entity update: in-memory and effectively immediate. Future view/list/canvas identifier lookup: in-memory and effectively immediate when APIs exist.
- Display representation text lookup: batched and local when possible.
- Entity resolution: avoid N+1 operations.
- Transfer preview: fast first representation; defer expensive generation.
- Scene navigation: no full app-state reload when the target is already available.
- Donation: asynchronous and outside animation-critical paths.

Never fetch the network from a table/collection annotation callback or custom canvas element provider.

## 34. Privacy checklist for UIKit context

Before exposing a view/entity:

- Is the view actually visible rather than cached/prefetched?
- Is the user authorized for this account/workspace?
- Is the content hidden behind a privacy blur or secure mode?
- Is the app backgrounded or covered by a sensitive modal?
- Does the title reveal private content on a shared/locked device?
- Is a reusable cell carrying a stale identifier?
- Does a drag/transfer representation include more than the visible object?
- Should the activity be invalidated when screen capture/privacy mode starts?

Centralize this decision in an annotation policy service rather than duplicating it across controllers.

## 35. UIKit testing matrix

Test at four levels.

### Unit

- Route mapping from each intent type to `NavigationRoute`.
- Entity identifier creation from stable domain IDs.
- Authorization/redaction policy.
- Donation construction.
- Transfer export content and cleanup.

### App Intents integration

- Intent execution and results.
- Query resolution.
- Indexing and open intents.
- Dialog/confirmation/cancellation.

### UIKit UI tests

- Warm-open target in a navigation stack.
- Cold launch from an intent.
- Correct tab/split column.
- Existing target is not pushed twice.
- Modal editing policy.
- Multiple scenes with different accounts/content.
- Primary `NSUserActivity` changes as navigation changes.
- Table/collection annotations survive snapshot updates.
- Cell reuse clears old identifiers.
- Custom canvas bounds and selection update.
- Siri tip visibility and layout.

### Manual system validation

- Siri voice and Type to Siri.
- Spotlight.
- Shortcuts editor and automation.
- Visual Intelligence.
- Ask Siri context menu on iOS 27/selected SDKs where available.
- Drag resource loading without a gesture.
- Locked device and privacy modes.
- iPad multiwindow, external display, and iPhone Mirroring.

## 36. UIKit-specific rejection list

Reject code that:

- Uses `connectedScenes.first` to navigate.
- Calls an intent’s `perform()` from `AppIntentSceneDelegate`.
- Routes the same intent in both `performNavigation(forScene:)` and `AppIntentSceneDelegate`.
- Declares a new conformance to `AppEntityAnnotatable` or references view/list/canvas annotation APIs absent from the selected SDK.
- Stores a window/controller in `AppDependencyManager` as the general navigation strategy.
- Uses index paths as App Entity IDs.
- Treats prefetched or hidden content as visible context.
- In a selected SDK with reusable-view annotations, fails to clear entity identifiers in reusable cells.
- In a selected SDK with annotation providers, does network or database writes from an annotation provider.
- Presents UI from drag-session startup.
- Claims snippets can be implemented as UIKit views.
- Duplicates entity/query logic for UIKit and SwiftUI targets.
- Sends a private entity through transfer/drag because the view happens to display it.
- Routes cold launch in both connection options and scene callback without deduplication.
- Assumes one scene, one account, one window, or one navigation controller.

## 37. Implementation order for a UIKit codebase

1. Migrate to/verify `UISceneDelegate` lifecycle.
2. Extract UI-independent repositories and domain services.
3. Build entities and queries.
4. Build a per-scene coordinator with semantic routes.
5. Add `OpenIntent` and one UIKit scene-routing mechanism.
6. Add primary `NSUserActivity` annotations.
7. Add individual view and table/collection annotations.
8. Add custom-canvas providers where needed.
9. Add indexing and transfer representations.
10. Add App Shortcuts plus `SiriTipUIView` and `ShortcutsUIButton` promotion.
11. Add interaction donations from successful UIKit actions.
12. Add snippets/widgets as isolated SwiftUI surfaces.
13. Add multiwindow, privacy, cold-launch, and reuse tests.
14. Audit drag/drop and context menus for iOS 27 Siri access.

See [uikit-examples.md](uikit-examples.md) for code and [ui-framework-crosswalk.md](ui-framework-crosswalk.md) for direct SwiftUI-to-UIKit translations.

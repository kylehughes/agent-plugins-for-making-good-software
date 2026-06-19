# App Intents Production Checklists

## Semantic model checklist

For each app noun:

- [ ] User-facing name identified.
- [ ] Durable ID exists or entity is explicitly transient.
- [ ] Schema domain checked.
- [ ] Entity type created.
- [ ] Type display representation localized.
- [ ] Display representation title/subtitle/image implemented.
- [ ] Privacy-safe fields selected.
- [ ] ID lookup query implemented.
- [ ] String query implemented if users name it.
- [ ] Property query implemented if users filter/find it.
- [ ] IndexedEntity used if durable searchable content.
- [ ] OpenIntent implemented if tappable/openable.
- [ ] Transferable implemented if content may be exported/analyzed/shared.
- [ ] Onscreen annotation plan exists.
- [ ] Ownership/account semantics defined.
- [ ] Tests written.

## Intent checklist

For each intent:

- [ ] One clear user action.
- [ ] Schema checked.
- [ ] Protocol selected: AppIntent, OpenIntent, DeleteIntent, etc.
- [ ] Title localized.
- [ ] Description written.
- [ ] Parameters typed.
- [ ] Required parameters have request dialogs.
- [ ] `parameterSummary` includes required parameters.
- [ ] Defaults supplied where appropriate.
- [ ] Result value typed if action returns content.
- [ ] Dialog provided when needed.
- [ ] Snippet added only when useful.
- [ ] Confirmation added for destructive/sensitive/ambiguous actions.
- [ ] Undo added if truly reversible.
- [ ] Foreground/background mode decided.
- [ ] Execution target decided.
- [ ] Donations/relevance considered.
- [ ] Indexing side effects handled.
- [ ] Errors localized and safe.
- [ ] Cancellation handled.
- [ ] Tests written.

## Siri and Apple Intelligence checklist

- [ ] App Schemas adopted where available.
- [ ] Entity queries resolve spoken names.
- [ ] Important entities are indexed semantically.
- [ ] Onscreen primary detail views have entity identifiers.
- [ ] Lists/grids/cards have per-item annotations.
- [ ] Selections are annotated.
- [ ] Transferable exports exist for content Siri may inspect.
- [ ] `IntentValueQuery` exists for visual/incoming semantic matching where relevant.
- [ ] Dialog works on voice-only devices.
- [ ] Snippets are compact visual aids, not required for comprehension.
- [ ] Donations are meaningful and revocable.
- [ ] RelevantEntities is used for current context, not bulk data.
- [ ] Sensitive content is excluded or gated.
- [ ] AppIntentsTesting covers execution, queries, indexing, annotations.

## App Shortcuts checklist

- [ ] AppShortcutsProvider exists.
- [ ] Each App Shortcut maps to a high-value action.
- [ ] Phrases include `\(.applicationName)`.
- [ ] Parameterized phrases added where useful.
- [ ] Short titles are concise.
- [ ] System images are appropriate.
- [ ] Shortcut appears in Shortcuts app.
- [ ] Shortcut appears in Spotlight if intended.
- [ ] Shortcut works with Siri.
- [ ] Shortcut works from Action button if intended.
- [ ] Lock-screen behavior reviewed.

## Spotlight checklist

- [ ] Searchable entities conform to IndexedEntity or have CoreSpotlight association.
- [ ] Indexable properties use meaningful indexing keys.
- [ ] Custom keys are namespaced.
- [ ] Index add/update/delete paths implemented.
- [ ] Hidden/private/account-revoked content is removed.
- [ ] OpenIntent exists for tappable results.
- [ ] Spotlight tests cover title/content/semantic queries.
- [ ] Indexing is incremental and not too expensive.

## Onscreen awareness checklist

- [ ] Detail screens use NSUserActivity with app entity identifier.
- [ ] Rows/cards/thumbnails have entity annotations.
- [ ] Collections expose selection when applicable.
- [ ] Custom canvas objects are annotated.
- [ ] UIKit/AppKit cells clear stale annotations on reuse.
- [ ] Notifications/Now Playing/AlarmKit/Live Activity annotations are added where relevant.
- [ ] Annotations respect privacy/lock-screen rules.
- [ ] Tests inspect annotations.

## Transferable checklist

- [ ] Plain text export exists where useful.
- [ ] Rich text export exists for rich documents/messages.
- [ ] PDF/image/file export exists when visual fidelity matters.
- [ ] IntentValueRepresentation or ValueRepresentation used where appropriate.
- [ ] Export is permission-aware.
- [ ] Hidden metadata is stripped.
- [ ] Temporary files are managed.
- [ ] Exports are cancellation-aware.
- [ ] Sensitive content requires confirmation or unlock.

## Snippet checklist

- [ ] Snippet has a clear purpose.
- [ ] Snippet is glanceable.
- [ ] Height/content are compact.
- [ ] No hidden state mutation in render-only snippet intent.
- [ ] Buttons/toggles use separate App Intents.
- [ ] Dynamic data fetched in perform.
- [ ] Reload used sparingly and intentionally.
- [ ] Dialog fallback is complete.
- [ ] Accessibility labels and Dynamic Type checked.
- [ ] Dark/light mode checked.

## Execution checklist

- [ ] Intent can run in intended surface/process.
- [ ] Dependencies are available in that process/extension.
- [ ] Main-actor UI work isolated.
- [ ] Background work does not require UI.
- [ ] Foreground continuation used only when necessary.
- [ ] TargetContentProvidingIntent used for active-view actions.
- [ ] Long-running work uses progress/cancellation.
- [ ] ExecutionTargets declared where needed.
- [ ] Network failure path handled.
- [ ] Duplicate retry/idempotency handled.

## UIKit checklist

- [ ] App uses `UISceneDelegate`; intent navigation is not routed solely through `UIApplicationDelegate`.
- [ ] Each scene owns a coordinator/router and navigation state.
- [ ] Incoming navigation uses `UISceneAppIntent` or `AppIntentSceneDelegate`.
- [ ] Every scene-targeted intent has exactly one navigation owner: custom `performNavigation(forScene:)` or delegate routing, never both.
- [ ] `AppIntentSceneDelegate` uses the `any UISceneAppIntent` callback signature and never calls the supplied intent’s `perform()`.
- [ ] Cold-launch connection options and scene callback cannot route the same intent twice.
- [ ] Scene activation policy accounts for account/workspace, editing state, and multiwindow behavior.
- [ ] Multiwindow scenes configure `UIScene.activationConditions` with the same target-content identifier vocabulary used by intent routing.
- [ ] No code selects `connectedScenes.first` or a process-global “top view controller.”
- [ ] Primary semantic screens publish and invalidate `NSUserActivity.appEntityIdentifier`.
- [ ] Individual annotated views clear identifiers when hidden, redacted, or rebound.
- [ ] No app-defined type declares a new `AppEntityAnnotatable` conformance; UIKit framework conformances are reused.
- [ ] Tables use `UITableViewAppIntentsDataSource` when they expose many entities.
- [ ] Collections use `UICollectionViewAppIntentsDataSource` when they expose many entities.
- [ ] Index paths map through the current data source to durable IDs.
- [ ] Reusable cells clear `appEntityIdentifier` in `prepareForReuse()`.
- [ ] Model-level selection survives offscreen scrolling and diffable snapshots.
- [ ] Custom canvases use `appEntityUIElementProvider` with current bounds and selection.
- [ ] Annotation callbacks do no network access, mutation, or presentation.
- [ ] Entity display representations can be fetched cheaply for many onscreen IDs.
- [ ] `SiriTipUIView.setIntent(intent:)` is called before presentation and `isPresented` is honored.
- [ ] `ShortcutsUIButton(style:)` is used for the native UIKit link to the app’s Shortcuts page.
- [ ] SwiftUI-only snippets/widgets/controls/Live Activities are isolated from UIKit navigation.
- [ ] UIKit interaction donations occur after successful user actions, not cell display/prefetch.
- [ ] Drag providers are safe when invoked by Apple Intelligence without a normal gesture.
- [ ] `sessionWillBegin` does not present UI or animate state.
- [ ] Objective-C screens bridge stable IDs/operations into a Swift App Intents module.
- [ ] Warm launch, cold launch, multiwindow, restoration, cell reuse, privacy mode, and drag loading are tested.

## Privacy checklist

- [ ] Indexing excludes private/hidden/locked content.
- [ ] Display representation does not leak private fields.
- [ ] Dialog does not speak sensitive content unexpectedly.
- [ ] Snippet redacts as needed.
- [ ] Transferable exports are sanitized.
- [ ] Donations respect user opt-out.
- [ ] RelevantEntities cleared when context changes.
- [ ] Account/workspace filtering enforced.
- [ ] Lock-screen behavior reviewed.
- [ ] Enterprise/MDM policy considered.

## Testing checklist

- [ ] Intent execution tests.
- [ ] Entity ID lookup tests.
- [ ] Entity string query tests.
- [ ] Property query tests.
- [ ] Search/indexing tests.
- [ ] View annotation tests.
- [ ] Snippet result tests.
- [ ] Foreground continuation tests.
- [ ] Widget/control execution tests.
- [ ] Cancellation tests.
- [ ] Migration/backward-compatibility tests.
- [ ] Manual Siri tests.
- [ ] Manual Shortcuts tests.
- [ ] Manual Spotlight tests.
- [ ] Manual Action button tests if relevant.

## Code review rejection list

Reject code if:

- [ ] Entity ID is mutable/user-editable.
- [ ] Entity query ignores account/permissions.
- [ ] Required parameter missing from summary.
- [ ] String parameter is used where entity/enum/value type is appropriate.
- [ ] Intent mutates state without confirmation when destructive.
- [ ] Snippet render path performs mutation.
- [ ] Transferable export leaks private metadata.
- [ ] Indexing includes content user opted out of.
- [ ] Intent depends on app-only singleton but can run in extension.
- [ ] Cancellation is swallowed.
- [ ] Deprecated public intent was removed without replacement.
- [ ] Schema conformance is semantically wrong.
- [ ] UIKit routing uses `connectedScenes.first`, a guessed key window, or a global top-controller helper.
- [ ] UIKit scene delegate calls the supplied App Intent’s `perform()` method.
- [ ] Table/collection code uses index paths as entity identity or fails to clear reused annotations.
- [ ] Custom-canvas annotation provider performs I/O or changes UI state.
- [ ] Drag-session startup presents UI even though Apple Intelligence may invoke it programmatically.
- [ ] UIKit code claims to replace a system snippet with a UIKit modal.

# Attribution and Verification Notes

Verification baseline: iPhoneOS 26.5 SDK, Xcode 26.5, checked on 2026-07-03 by grepping public `.swiftinterface` files under the selected SDK.

This skill was rebuilt from the user-provided starter skill, expanded for UIKit and structured-value workflows, then corrected against the supplied SDK verification brief. The verification brief is treated as ground truth for availability in this package.

## Primary Apple sources represented

- Apple Developer Documentation: App Intents framework.
- Apple Developer Documentation: `AppEntity`, `AppIntent`, `AppShortcutsProvider`, `EntityQuery`, `EntityStringQuery`, `EnumerableEntityQuery`, `EntityPropertyQuery`, `IndexedEntity`, `OpenIntent`, `SnippetIntent`, `ProgressReportingIntent`, `DeprecatedAppIntent`, `IntentDeprecation`, `PredictableIntent`, `AppIntentsPackage`, CoreSpotlight App Entity indexing, and Transferable-related integration where available.
- Apple Developer Documentation and Swift interfaces for `UISceneAppIntent`, `performNavigation(forScene:)`, `AppIntentSceneDelegate`, `scene(_:willPerformAppIntent:)`, `SiriTipUIView`, `ShortcutsUIButton`, and `UIScene.ConnectionOptions.appIntent` in the `_AppIntents_UIKit` cross-import overlay.
- Apple Developer Documentation: `UIScene.activationConditions`, `UISceneActivationConditions`, `canActivateForTargetContentIdentifierPredicate`, and `prefersToActivateForTargetContentIdentifierPredicate`.
- Apple Developer Documentation / SDK interfaces: `SemanticContentDescriptor` in `VisualIntelligence`; `GeoToolbox` and `PlaceDescriptor`; `_GeoToolbox_AppIntents` overlay.
- Apple WWDC 2025/2026 App Intents, App Schemas, UIKit modernization, Spotlight/Shortcuts, snippets, Visual Intelligence, and Siri sessions, used as design context but subordinated to the selected SDK’s public interfaces.
- Matthew Cassinelli, “Teach Siri AI to Share Structured Types Without Known Formats Across Apps with ValueRepresentation,” July 1, 2026, used as design context for the structured-value transfer mental model.

## SDK correction notes

The package now states that these APIs are absent from iPhoneOS 26.5 and therefore selected-SDK-gated: `ValueRepresentation`, `IntentValueRepresentation`, `RelevantEntities`, AppIntents `EntityCollection`, `SyncableEntity`, `SyncableEntityIdentifier`, `LongRunningIntent`, `ExecutionTargets`, `CancellableIntent`, `AppIntentsTesting`, `UITableViewAppIntentsDataSource`, `UICollectionViewAppIntentsDataSource`, `AppEntityUIElement`, `UIView.appEntityUIElementProvider`, SwiftUI per-view `.appEntityIdentifier(...)`, SwiftUI `.appEntityIdentifier(forSelectionType:)`, and notification-content `appEntityIdentifiers`.

The package now states that the verified Assistant Schemas domains in iPhoneOS 26.5 are: `journal`, `photos`, `visualIntelligence`, `reader`, `system`, `wordProcessor`, `presentation`, `spreadsheet`, `browser`, `files`, `camera`, `mail`, `whiteboard`, and `books`. Messages, Calendar, Tasks, Audio/media, Clock, Alarm, and Timer are not described as shipping schema domains for that SDK.

## Version notes

App Intents and App Schemas evolve quickly across Xcode and OS releases. The selected Xcode SDK, Swift interfaces, Apple documentation for that SDK, and compiler diagnostics are the final source of truth before shipping.

Runtime availability and compile-time visibility are different. If a symbol is absent from the selected SDK, `@available` does not make source code using that symbol compile.

## Relationship to the user-provided draft

The user-provided `SKILL.MD`, `REFERENCE.md`, and `ATTRIBUTION.md` were treated as seed material. This package replaces that draft with a larger multi-file skill, while preserving the original intent: comprehensive App Intents implementation guidance for Siri, Apple Intelligence, Shortcuts, Spotlight, widgets, controls, snippets, onscreen context, entity modeling, queries, schemas, and indexing. The UIKit expansion treats UIKit scene routing, current `NSUserActivity` annotation, selected-SDK-gated advanced annotations, Siri promotion, drag providers, Objective-C bridging, and UIKit testing as first-class concerns rather than brief equivalents to SwiftUI examples.

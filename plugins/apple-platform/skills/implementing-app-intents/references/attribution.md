# Attribution and Verification Notes

Verification date: 2026-06-19.

This skill was rebuilt from the user-provided starter skill and cross-checked against Apple Developer documentation and Apple WWDC transcripts available as of the verification date.

## Primary Apple sources consulted

- Apple Developer Documentation: App Intents framework.
- Apple Developer Documentation: AppEntity, AppIntent, AppShortcutsProvider, EntityQuery, EntityStringQuery, EnumerableEntityQuery, EntityPropertyQuery, IndexedEntity, OpenIntent, SnippetIntent, Transferable-related App Intents integration, CoreSpotlight App Entity indexing, and App Intents testing APIs where available.
- WWDC 2025: “Explore new advances in App Intents”.
- WWDC 2025: “Design interactive snippets”.
- WWDC 2025: “Develop for Shortcuts and Spotlight with App Intents”.
- WWDC 2026: “Build intelligent Siri experiences with App Schemas”.
- WWDC 2026: “Discover new capabilities in App Intents framework”.
- WWDC 2026: “Explore advanced App Intents features for Siri and Apple Intelligence”.
- WWDC 2026: “Code-along: Make your app available to Siri”.
- WWDC 2026: “Validate your App Intents”.
- WWDC 2026: “Modernize your UIKit app”.
- Apple Developer Documentation: `UISceneAppIntent`, `performNavigation(forScene:)`, `AppIntentSceneDelegate`, `scene(_:willPerformAppIntent:)`, and `UIScene.ConnectionOptions.appIntent`.
- Apple Developer Documentation: `UIScene.activationConditions`, `UISceneActivationConditions`, `canActivateForTargetContentIdentifierPredicate`, and `prefersToActivateForTargetContentIdentifierPredicate`.
- Apple Developer Documentation: `AppEntityAnnotatable` (including Apple’s prohibition on app-defined conformances), `UITableViewAppIntentsDataSource`, `UICollectionViewAppIntentsDataSource`, `UIView.appEntityUIElementProvider`, and `AppEntityUIElement`.
- Apple Developer Documentation: `SiriTipUIView`, `setIntent(intent:)`, and `isPresented`.
- Apple Developer Documentation: `ShortcutsUIButton`, `init(style:)`, and `ShortcutsLinkStyle`.
- Apple Developer Documentation: “Providing contextual cues to Apple Intelligence and Siri”.

## Version notes

App Intents and App Schemas evolve quickly across Xcode and OS releases. The skill intentionally marks iOS 27-specific areas as SDK-sensitive where symbols, schema names, annotations, or availability may shift during beta cycles.

Use the selected Xcode SDK, Apple documentation, and compiler diagnostics as the final source of truth before shipping. The package emphasizes architecture, implementation strategy, code shapes, checklists, and failure modes that should remain useful even when exact SDK spellings change.

## Relationship to the user-provided draft

The user-provided `SKILL.MD`, `REFERENCE.md`, and `ATTRIBUTION.md` were treated as seed material. This package replaces that draft with a larger multi-file skill, while preserving the original intent: comprehensive App Intents implementation guidance for Siri, Apple Intelligence, Shortcuts, Spotlight, widgets, controls, snippets, onscreen context, entity modeling, queries, schemas, and indexing. The UIKit expansion treats UIKit scene routing, onscreen annotations, collection/canvas context, Siri promotion, drag providers, Objective-C bridging, and UIKit testing as first-class concerns rather than brief equivalents to SwiftUI examples.

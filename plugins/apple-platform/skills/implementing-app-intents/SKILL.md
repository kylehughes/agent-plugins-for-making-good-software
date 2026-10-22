---
name: implementing-app-intents
description: "Build or debug App Intents for Siri, Shortcuts, Apple Intelligence, Spotlight, widgets, and controls. Use for entities, queries, schemas, intent routing, and system integrations."
---

# Implementing App Intents

Use this skill when designing, auditing, or implementing App Intents for Apple-platform apps, especially when the goal is integration with Siri, Apple Intelligence, Shortcuts, Spotlight, widgets, controls, Live Activities, the Action button, visual intelligence, onscreen awareness, or cross-app automation.

This is a production implementation skill, not a short reference card. It assumes Swift, SwiftUI/UIKit/AppKit, AppIntents, CoreSpotlight, CoreTransferable, WidgetKit where relevant, and current Xcode SDKs. Treat the selected SDK’s Swift interfaces, Xcode autocomplete, and Apple documentation as the final authority. Runtime `#available` gates do not help when the selected SDK lacks a declaration.

## Primary objective

Expose the requested actions and data in a way the system can understand semantically. For a broad Siri or Apple Intelligence integration, model the app as a graph of entities, properties, relationships, queries, and actions, then expose the relevant surfaces through App Schemas, indexing, onscreen annotations, content transfer, donations, and relevance signals supported by the selected SDK. For a narrow fix, preserve the existing semantic model and change only the surfaces the request requires.

## Reference Map

Read only the references needed for the requested integration; do not read the whole map. Use architecture and the agent playbook for broad integration work, migration guidance for an upgrade, examples for a concrete implementation pattern, and attribution for provenance. For other tasks, select the matching concern below.

- [Architecture and model](references/architecture-and-model.md): semantic model, design order, availability buckets, package placement, and host boundaries.
- [Entities, queries, and indexing](references/entities-queries-and-indexing.md): entities, queries, identity, indexing, and Spotlight.
- [Intents, dialog, snippets, and confirmation](references/intents-dialog-snippets-and-confirmation.md): actions, results, dialogs, snippets, choices, confirmation, and undo.
- [Onscreen awareness and content transfer](references/onscreen-awareness-and-content-transfer.md): screen context, annotations, Transferable, visual intelligence, and incoming content.
- [SDK availability and verification](references/sdk-availability-and-verification.md): selected-SDK facts, absent symbols, module locations, and verification.
- [UIKit integration](references/uikit-integration.md): scene routing, onscreen awareness, drag/drop, promotion, privacy, and lifecycle.
- [UI framework crosswalk](references/ui-framework-crosswalk.md): SwiftUI/UIKit equivalence and SwiftUI-only system surfaces.
- [Shortcuts, Spotlight, widgets, and controls](references/shortcuts-spotlight-widgets-and-controls.md): discovery surfaces and system integrations.
- [Execution, packaging, performance, and privacy](references/execution-packaging-performance-and-privacy.md): execution, progress, extensions, packages, and privacy.
- [Testing and debugging](references/testing-and-debugging.md): XCTest, selected-SDK-gated AppIntentsTesting, manual validation, and diagnosis.
- [Checklists](references/checklists.md): production checklists.
- [Minimal modern skeleton](references/minimal-skeleton.md): composable Swift entity, query, intent, and shortcut example; read when implementing the basic shape.
- [Agent playbook](references/agent-playbook.md): applying this skill to a codebase.
- [ATTRIBUTION.md](ATTRIBUTION.md): provenance and verification notes.
- [Reference](references/reference.md): expanded mental model, implementation reference, and anti-patterns.
- [Apple Intelligence and Siri](references/apple-intelligence-and-siri.md): Siri and Apple Intelligence integration strategy.
- [Assistant schema domains](references/assistant-schema-domains.md): schema adoption, domain mapping, and constraints.
- [Value representation and structured transfer](references/value-representation-and-structured-transfer.md): structured-value mapping seams and transfer handoff failure modes.
- [UIKit examples](references/uikit-examples.md): focused UIKit code patterns.
- [Migration](references/migration-ios26-to-ios27.md): migration and adoption plan.
- [Examples](references/examples.md): additional composable Swift skeletons.

## When to use this skill

Use this skill when the user asks to:

- Add or improve Siri support.
- Integrate an app with Apple Intelligence.
- Build App Intents, App Shortcuts, App Entities, App Enums, or App Schemas.
- Make app content visible to Siri, Spotlight, Visual Intelligence, Shortcuts, widgets, controls, Live Activities, or the Action button.
- Implement entity ID lookup, string search, property queries, semantic Spotlight indexing, `IntentValueQuery`, or `Transferable` exports; plan seams for `SyncableEntity` / AppIntents `EntityCollection` only when the selected SDK contains those symbols.
- Annotate onscreen content so Siri understands the primary item the user is viewing; in the iPhoneOS 26.5 SDK this means `NSUserActivity.appEntityIdentifier` for the primary screen entity. Per-view/list/canvas annotations are selected-SDK-dependent and must be compile-verified.
- Integrate a UIKit application using `UISceneAppIntent`, `AppIntentSceneDelegate`, and `NSUserActivity.appEntityIdentifier`; do not invent `AppEntityAnnotatable` conformances, and treat per-view/table/collection/canvas annotation APIs as forward-looking unless present in the selected SDK.
- Translate SwiftUI-only examples into correct UIKit scene/coordinator architecture without duplicating the semantic model.
- Build interactive snippets, confirmation snippets, dialog, undo, progress-reporting, or selected-SDK-gated long-running/cancellable intent flows.
- Test App Intents with XCTest/manual system surfaces, and with `AppIntentsTesting` only when that framework exists in the selected SDK.
- Migrate older SiriKit, Intent Definition, or earlier App Intents code to iOS 26/iOS 27 patterns.

## Operating algorithm

Apply only the steps relevant to the requested integration surface. A narrow entity-query fix does not require implementing every App Intents surface; keep analysis, edits, and output proportional to scope.

1. Inventory the app’s semantic nouns. These become App Entities, App Enums, union values, transient entities, or value representations.
2. Inventory the app’s atomic verbs. These become App Intents, usually one user-observable operation each.
3. Map nouns and verbs to App Schemas first. Prefer schema conformance over custom-only intents when a schema accurately fits.
4. Model entity identity, persistence, display representation, ownership, relationships, and privacy.
5. Implement queries before writing complex intents. Siri and Shortcuts cannot act reliably on entities they cannot resolve.
6. Add OpenIntent for every entity that can be tapped, opened, returned, indexed, or found visually.
7. Add semantic indexing for durable searchable content. Use CoreSpotlight/AppIntents indexing, not ad hoc string matching.
8. Add onscreen awareness for visible content. In the iPhoneOS 26.5 SDK, use `NSUserActivity.appEntityIdentifier` for the primary item (iOS 18.2+). Treat per-view SwiftUI modifiers, UIKit table/collection data sources, and custom-canvas providers as forward-looking until the selected SDK declares them. Route incoming UIKit intents through the selected `UIScene`.
9. Add `Transferable` representations. Use `DataRepresentation`/`FileRepresentation` for known file/data formats. `IntentPerson` (iOS 16) and `PlaceDescriptor` (iOS 26, `GeoToolbox`) can be mapped today; `ValueRepresentation`/`IntentValueRepresentation` are absent from iPhoneOS 26.5 and must be added only when the selected SDK declares them.
10. Add App Shortcuts and parameter summaries for discoverability. Required parameters must appear in parameterSummary unless defaulted.
11. Add dialog, snippets, confirmation, requestChoice, undo, ownership, and foreground continuation for sensitive, ambiguous, or visual workflows.
12. Add donations, `PredictableIntent` (iOS 16), and Spotlight associations only after the model is correct. Add `RelevantEntities` only if the selected SDK declares it.
13. Test through XCTest, Shortcuts, Spotlight, Siri, widgets/controls, snippets, and foreground/background paths. Add `AppIntentsTesting` only if the selected SDK provides that framework.

## Default design position

For Siri and Apple Intelligence, the best implementation is not a natural-language parser inside the app. It is a clean semantic surface area: schema-conforming intents, queryable/indexed entities, rich display representations, screen annotations supported by the SDK, Transferable content, value queries, contextual relevance, and robust execution semantics.

## UI-framework rule

Entities, queries, schemas, indexing, donations, transfer, and domain services are UI-framework independent. For UIKit, use per-scene coordinators plus `UISceneAppIntent` or `AppIntentSceneDelegate` from the `_AppIntents_UIKit` cross-import overlay; use `NSUserActivity.appEntityIdentifier` for onscreen context in the verified iPhoneOS 26.5 baseline. Do not generate UIKit view/list/canvas annotation APIs unless the selected SDK declares them. Use `SiriTipUIView` and `ShortcutsUIButton` for native UIKit promotion. Snippets, widgets, controls, and Live Activities remain small SwiftUI system surfaces even in a UIKit app. See [ui-framework-crosswalk.md](references/ui-framework-crosswalk.md).

## Hard rules

- Do not expose private, locked, deleted, hidden, permission-gated, or cross-account content through entities, indexing, annotations, donations, snippets, or transfer representations unless the user has current access.
- Do not add required parameters beyond what a schema expects when conforming to an App Schema.
- Do not overload one App Intent with unrelated modes. Split actions unless the user concept is genuinely one action.
- Do not rely on phrase engineering for Siri intelligence. Phrases help discovery; entities, schemas, queries, indexing, and context drive understanding.
- Do not make every entity enumerable unless the corpus is bounded and safe to enumerate.
- Do not mutate app state inside a SnippetIntent whose purpose is only rendering. Put mutations in the primary action or explicit button/toggle intents.
- Do not swallow cancellation from confirmation, value request, choice request, long-running work, or async operations.
- Do not block intent execution on network calls that can be deferred, cached, indexed, represented as progress, or continued in the foreground.
- Do not leak raw internal IDs, file paths, access tokens, hidden metadata, location precision, or private content in display representations, Transferable/value exports, snippets, dialogs, or indexed properties.
- Do not mark an intent `isAssistantOnly` if it is expected to appear in Spotlight or Shortcuts.
- Do not navigate a UIKit app by taking `connectedScenes.first`, finding a global top view controller, or retaining one process-wide navigation controller.
- Do not call `perform()` on the `any UISceneAppIntent` supplied to `AppIntentSceneDelegate`; the framework owns execution.
- Do not route the same scene-targeted intent in both `performNavigation(forScene:)` and `AppIntentSceneDelegate`; assign one navigation owner per intent type.
- Do not declare new `AppEntityAnnotatable` conformances in app code. In iPhoneOS 26.5, only `NSUserActivity.appEntityIdentifier` is the buildable onscreen annotation path; use view/list/canvas APIs only when the selected SDK exposes them.
- Do not use an index path as entity identity. If a future SDK supplies reusable-view annotation APIs, clear stale annotations during reuse.
- Do not perform network work, mutations, or presentation from a UIKit annotation provider or drag-session startup callback.
- Do not claim a custom snippet can be implemented as a UIKit view; system snippet content is SwiftUI regardless of the host app UI framework.

## Output expectations when using this skill

For a broad implementation, cover the applicable items below. For a narrow change, provide only the affected code, design decisions, and validation; do not expand the assignment to fill this list.

- Semantic model: entities, properties, relationships, queries, indexing, schemas, screen context, and transfer semantics.
- Intent catalog: Open/Create/Update/Delete/Search/Export/Share/Control actions with protocols, parameters, result types, snippets, confirmation, execution target, and tests.
- Swift code availability-gated for iOS 26/iOS 27 when necessary, and source-gated when the selected SDK lacks a symbol.
- UI-host plan: SwiftUI view-control path or UIKit scene/coordinator path, including cold launch, multiwindow behavior, `NSUserActivity` primary-screen annotation, forward-looking selected-SDK gates for per-view/list/canvas annotations, and unavoidable SwiftUI islands.
- Siri/Apple Intelligence plan: App Schemas, current onscreen annotation, `Transferable`, structured-value mappers for `PlaceDescriptor`/`IntentPerson`, selected-SDK-gated transfer representations, `IntentValueQuery`, donations, optional relevance APIs, and semantic search.
- Discoverability plan: App Shortcuts, parameter summaries, Spotlight, widgets, controls, Live Activities, Action button.
- Testing plan: XCTest/UI coverage, manual system surfaces, selected-SDK-gated AppIntentsTesting, and failure-mode checks.

## Availability guidance

Do not trust era labels without checking the selected SDK. The iPhoneOS 26.5 SDK verified on 2026-07-03 has these important floors:

- Core `AppIntent`, `AppEntity`, `AppShortcutsProvider`, and entity queries: iOS 16.
- `IntentPerson` and `PredictableIntent`: iOS 16.
- `AppIntentsPackage`, `ProgressReportingIntent`, `DeprecatedAppIntent`, and `IntentDeprecation`: iOS 17.
- `IndexedEntity`: iOS 18.
- `NSUserActivity.appEntityIdentifier` and `AppEntityAnnotatable`: iOS 18.2.
- `UISceneAppIntent`, `AppIntentSceneDelegate`, `SiriTipUIView`, and `ShortcutsUIButton`: iOS 26 through the `_AppIntents_UIKit` cross-import overlay.
- `SemanticContentDescriptor`: iOS 26 in the `VisualIntelligence` framework.
- `PlaceDescriptor`: iOS 26 in `GeoToolbox` plus `_GeoToolbox_AppIntents` overlay.

The same SDK does **not** declare `ValueRepresentation`, `IntentValueRepresentation`, `RelevantEntities`, AppIntents `EntityCollection`, `SyncableEntity`, `LongRunningIntent`, `ExecutionTargets`, `CancellableIntent`, `AppIntentsTesting`, UIKit table/collection/canvas annotation APIs, SwiftUI per-view `.appEntityIdentifier(...)`, or notification `appEntityIdentifiers`. A runtime availability check cannot make absent declarations compile.

Use this workflow before generating production code:

```bash
SDK=$(xcrun --sdk iphoneos --show-sdk-path)
find "$SDK/System/Library/Frameworks" -name "arm64e-apple-ios.swiftinterface"   | xargs grep -l -w "SymbolName"
```

Then inspect the matching declaration and `@available` annotation. Cross-import overlays matter; check `_AppIntents_UIKit`, `_AppIntents_SwiftUI`, and `_GeoToolbox_AppIntents` when the API depends on two frameworks. See [sdk-availability-and-verification.md](references/sdk-availability-and-verification.md).

## Common failure pattern

A weak App Intents integration looks like this: three custom intents, no entities, no indexing, no schemas, no onscreen annotations, no Transferable exports, no tests, and a pile of hand-written Siri phrases.

A strong integration looks like this: durable schema-conforming entities, rich indexed properties, robust queries, atomic schema-conforming actions, meaningful App Shortcuts, contextual donations, onscreen annotations, content transfer, interactive snippets where they help, and tests that execute the same integration paths Siri and Shortcuts use.

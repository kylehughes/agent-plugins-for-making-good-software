---
name: implementing-app-intents
description: Implements modern App Intents with emphasis on Siri, Apple Intelligence, App Schemas, App Entities, entity queries, semantic Spotlight indexing, UIKit scene routing, NSUserActivity-level onscreen awareness, Visual Intelligence, Transferable content, Shortcuts, widgets, controls, snippets, progress reporting, package discovery, and SDK availability verification.
---

# Implementing App Intents

Use this skill when designing, auditing, or implementing App Intents for Apple-platform apps, especially when the goal is integration with Siri, Apple Intelligence, Shortcuts, Spotlight, widgets, controls, Live Activities, the Action button, visual intelligence, onscreen awareness, or cross-app automation.

This is a production implementation skill, not a short reference card. It assumes Swift, SwiftUI/UIKit/AppKit, AppIntents, CoreSpotlight, CoreTransferable, WidgetKit where relevant, and current Xcode SDKs. Treat the selected SDK’s Swift interfaces, Xcode autocomplete, and Apple documentation as the final authority. Runtime `#available` gates do not help when the selected SDK lacks a declaration.

## Primary objective

Expose the app’s actions and data in a way the system can understand semantically. Do not merely add a few Shortcuts actions. Model the app as a graph of entities, properties, relationships, queries, and actions, then make that graph available to Siri and Apple Intelligence through App Schemas, semantic indexing, onscreen annotations, content transfer, donations, and relevance signals that actually exist in the selected SDK.

## Read order

1. [architecture-and-model.md](references/architecture-and-model.md) — architecture, design order, availability buckets, package placement, and host boundaries.
2. [reference.md](references/reference.md) — expanded mental model, implementation reference, and anti-patterns.
3. [apple-intelligence-and-siri.md](references/apple-intelligence-and-siri.md) — Siri/Apple Intelligence integration strategy.
4. [assistant-schema-domains.md](references/assistant-schema-domains.md) — schema adoption, domain mapping, and constraints.
5. [entities-queries-and-indexing.md](references/entities-queries-and-indexing.md) — entities, queries, property queries, identity, indexing, Spotlight.
6. [intents-dialog-snippets-and-confirmation.md](references/intents-dialog-snippets-and-confirmation.md) — AppIntent design, results, dialog, snippets, confirmation, choices, undo.
7. [onscreen-awareness-and-content-transfer.md](references/onscreen-awareness-and-content-transfer.md) — screen context, annotations, Transferable, visual intelligence, incoming content.
8. [value-representation-and-structured-transfer.md](references/value-representation-and-structured-transfer.md) — `PlaceDescriptor`, `IntentPerson`, structured-value mapping seams, future transfer representations, import, and handoff failure modes.
9. [sdk-availability-and-verification.md](references/sdk-availability-and-verification.md) — iPhoneOS 26.5 availability facts, absent-symbol list, schema domains, module locations, and grep procedure for the selected SDK.
10. [uikit-integration.md](references/uikit-integration.md) — full UIKit architecture, scene routing, onscreen awareness, drag/drop, promotion, privacy, and lifecycle guidance.
11. [uikit-examples.md](references/uikit-examples.md) — UIKit code patterns.
12. [ui-framework-crosswalk.md](references/ui-framework-crosswalk.md) — SwiftUI/UIKit equivalence and intentional SwiftUI-only system surfaces.
13. [shortcuts-spotlight-widgets-and-controls.md](references/shortcuts-spotlight-widgets-and-controls.md) — discovery surfaces and system integrations.
14. [execution-packaging-performance-and-privacy.md](references/execution-packaging-performance-and-privacy.md) — foreground/background execution, progress reporting, selected-SDK-gated long-running work, extensions, packages, privacy.
15. [testing-and-debugging.md](references/testing-and-debugging.md) — XCTest/UI tests, selected-SDK-gated AppIntentsTesting, manual validation, failure diagnosis.
16. [migration-ios26-to-ios27.md](references/migration-ios26-to-ios27.md) — migration and adoption plan.
17. [checklists.md](references/checklists.md) — production checklists.
18. [examples.md](references/examples.md) — composable Swift skeletons.
19. [agent-playbook.md](references/agent-playbook.md) — how an agent should apply this skill to a codebase.
20. [ATTRIBUTION.md](ATTRIBUTION.md) — source list and verification notes.

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

Entities, queries, schemas, indexing, donations, transfer, and domain services are UI-framework independent. For UIKit, use per-scene coordinators plus `UISceneAppIntent` or `AppIntentSceneDelegate` from the `_AppIntents_UIKit` cross-import overlay; use `NSUserActivity.appEntityIdentifier` for current shipping onscreen context. Do not generate UIKit view/list/canvas annotation APIs unless the selected SDK declares them. Use `SiriTipUIView` and `ShortcutsUIButton` for native UIKit promotion. Snippets, widgets, controls, and Live Activities remain small SwiftUI system surfaces even in a UIKit app. See [ui-framework-crosswalk.md](references/ui-framework-crosswalk.md).

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

When asked to implement App Intents, produce:

- Semantic model: entities, properties, relationships, queries, indexing, schemas, screen context, and transfer semantics.
- Intent catalog: Open/Create/Update/Delete/Search/Export/Share/Control actions with protocols, parameters, result types, snippets, confirmation, execution target, and tests.
- Swift code availability-gated for iOS 26/iOS 27 when necessary, and source-gated when the selected SDK lacks a symbol.
- UI-host plan: SwiftUI view-control path or UIKit scene/coordinator path, including cold launch, multiwindow behavior, `NSUserActivity` primary-screen annotation, forward-looking selected-SDK gates for per-view/list/canvas annotations, and unavoidable SwiftUI islands.
- Siri/Apple Intelligence plan: App Schemas, current onscreen annotation, `Transferable`, structured-value mappers for `PlaceDescriptor`/`IntentPerson`, selected-SDK-gated transfer representations, `IntentValueQuery`, donations, optional relevance APIs, and semantic search.
- Discoverability plan: App Shortcuts, parameter summaries, Spotlight, widgets, controls, Live Activities, Action button.
- Testing plan: XCTest/UI coverage, manual system surfaces, selected-SDK-gated AppIntentsTesting, and failure-mode checks.

## Minimal modern skeleton

```swift
import AppIntents
import CoreSpotlight
import CoreTransferable

struct ItemEntity: IndexedEntity, Identifiable, Sendable {
    static let defaultQuery = ItemEntityQuery()

    let id: UUID

    @Property(title: "Name", indexingKey: \.displayName)
    var name: String

    @Property(title: "Description", indexingKey: \.contentDescription)
    var details: String?

    var displayRepresentation: DisplayRepresentation {
        DisplayRepresentation(
            title: "\(name)",
            subtitle: details.map { "\($0)" },
            image: .init(systemName: "doc.text")
        )
    }

    static var typeDisplayRepresentation: TypeDisplayRepresentation {
        TypeDisplayRepresentation(name: "Item", numericFormat: "\(placeholder: .int) items")
    }
}

struct ItemEntityQuery: EntityStringQuery, EntityPropertyQuery {
    typealias Entity = ItemEntity

    func entities(for identifiers: [ItemEntity.ID]) async throws -> [ItemEntity] {
        try await ItemRepository.shared.entities(ids: identifiers)
    }

    func entities(matching string: String) async throws -> [ItemEntity] {
        try await ItemRepository.shared.searchEntities(text: string)
    }

    func suggestedEntities() async throws -> [ItemEntity] {
        try await ItemRepository.shared.recentEntities(limit: 10)
    }

    static var properties = QueryProperties {
        Property(\.name) {
            EqualToComparator { $0 }
            ContainsComparator { $0 }
        }
        Property(\.details) {
            ContainsComparator { $0 }
        }
    }

    static var sortingOptions = SortingOptions {
        SortableBy(\.name)
    }

    func entities(
        matching comparators: [QueryComparator<ItemEntity>],
        mode: ComparatorMode,
        sortedBy: [Sort<ItemEntity>],
        limit: Int?
    ) async throws -> [ItemEntity] {
        try await ItemRepository.shared.query(
            comparators: comparators,
            mode: mode,
            sortedBy: sortedBy,
            limit: limit
        )
    }
}

struct OpenItemIntent: OpenIntent {
    static let title: LocalizedStringResource = "Open Item"

    @Parameter(title: "Item")
    var target: ItemEntity

    func perform() async throws -> some IntentResult {
        // Bind navigation in the host UI: SwiftUI view control or UIKit scene routing.
        return .result()
    }
}

struct ItemShortcuts: AppShortcutsProvider {
    static var appShortcuts: [AppShortcut] {
        AppShortcut(
            intent: OpenItemIntent(),
            phrases: ["Open \(\.$target) in \(.applicationName)"],
            shortTitle: "Open Item",
            systemImageName: "doc.text"
        )
    }
}
```

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

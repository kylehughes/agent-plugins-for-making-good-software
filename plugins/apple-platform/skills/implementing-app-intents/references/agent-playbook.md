# Agent Playbook

Use this when responding to a user who wants App Intents implemented in a real codebase.

## First pass: ask or infer

Infer from the app domain when possible. Ask only when needed:

- App domain and core user objects.
- Minimum deployment target.
- Which Xcode/iPhoneOS SDK is selected, which deployment targets it supports, and whether the project permits preview SDK APIs. Use [feature status](../../modeling-swift-types-for-correctness/references/swift-feature-status.md) for the dated release/channel snapshot.
- SwiftUI/UIKit/AppKit mix. For UIKit, determine scene lifecycle, storyboard/programmatic construction, navigation containers, multiwindow/account model, diffable data sources, custom canvases, drag/drop, and Objective-C boundaries.
- Existing CoreSpotlight, SiriKit, WidgetKit, Shortcuts, or AppIntents code.
- Privacy constraints.
- Which system surfaces matter most.

If the user gave code, audit it before designing new files. If the task involves an API availability claim, verify the selected SDK first or clearly mark the claim as unverified.

## Produce a semantic model

Always start with a table:

```text
Entity | Schema | Durable ID | Query | Indexed | OpenIntent | Transferable | Onscreen | Privacy notes
```

Then produce the intent catalog:

```text
Intent | Schema | Parameters | Result | Surface | Foreground? | Confirmation | Tests
```

## Implementation sequence

1. Create entities and enums.
2. Create queries.
3. Create OpenIntent for each openable entity.
4. Implement create/update/delete/search/control intents.
5. Create AppShortcutsProvider.
6. Add indexing/donation services.
7. Add onscreen awareness. For iPhoneOS 26.5-compatible code: primary `NSUserActivity.appEntityIdentifier` only. Add per-view/list/canvas annotations only if the selected SDK declares them.
8. Add `Transferable` exports and structured value mappers (`IntentPerson`, `PlaceDescriptor`) where applicable; add `ValueRepresentation`/`IntentValueRepresentation` wrappers only if the selected SDK declares them.
9. Add snippets/confirmation.
10. Add tests.
11. Add migration/deprecation wrappers.

## Code generation rules

- Prefer typed parameters over strings.
- Use schema macros when accurate.
- Add source isolation and runtime availability gates for selected-SDK-only APIs. If the selected SDK does not declare a symbol, do not reference it at all.
- Keep repositories abstract if app storage is unknown.
- Mark UI navigation `@MainActor`. For UIKit, route through the system-selected scene and a per-scene coordinator; never generate `connectedScenes.first` navigation code. Use the exact `any UISceneAppIntent` delegate callback, choose one navigation owner per intent, never invent `AppEntityAnnotatable` conformances, and do not reference UIKit view/list/canvas annotation APIs unless the selected SDK declares them.
- Avoid app-only dependencies in extension-targeted intents.
- Include privacy checks in query/index/export paths.
- Include `parameterSummary` for public/discoverable intents.
- Include `OpenIntent` for Spotlight/Visual Intelligence results.
- Include deletion of stale index items and donations.

## Verify against the selected SDK

Before using any API that might be new, beta-era, or niche, inspect the selected SDK’s Swift interfaces. This is mandatory for symbols called out in [sdk-availability-and-verification.md](sdk-availability-and-verification.md).

```bash
SDK=$(xcrun --sdk iphoneos --show-sdk-path)

# Which frameworks declare a symbol:
find "$SDK/System/Library/Frameworks" -name "arm64e-apple-ios.swiftinterface" \
  | xargs grep -l -w "SymbolName"

# Its @available annotation, when in AppIntents:
grep -B4 "public protocol SymbolName" \
  "$SDK/System/Library/Frameworks/AppIntents.framework/Modules/AppIntents.swiftmodule/arm64e-apple-ios.swiftinterface"

# Assistant Schema domains in this SDK:
grep -o -E "public static var [a-zA-Z]+: some AppIntents\.AssistantSchemas\.[A-Za-z]+" \
  "$SDK/System/Library/Frameworks/AppIntents.framework/Modules/AppIntents.swiftmodule/arm64e-apple-ios.swiftinterface" | sort -u
```

Check cross-import overlays such as `_AppIntents_UIKit`, `_AppIntents_SwiftUI`, and `_GeoToolbox_AppIntents`. Beware name collisions such as `EntityCollection` in RealityKit. Absence from the GA SDK does not preclude presence in a beta SDK; audit the SDK actually selected by the project.

## Audit questions

Ask these of every integration:

- Can Siri resolve the user’s nouns?
- Can Siri understand the user’s current screen? For UIKit on iPhoneOS 26.5, is primary `NSUserActivity.appEntityIdentifier` correct and invalidated? Are list/collection/selection/canvas annotation plans gated on SDK support?
- Can Siri pass the content to another system safely?
- Can Spotlight find content by title and meaning?
- Can Shortcuts chain typed results?
- Can widgets/controls run safely in their extension context?
- Can old shortcuts survive the next release?
- Can tests catch broken entity resolution?

## Review output shape

For complex tasks, return:

1. Architecture summary.
2. File tree.
3. Key Swift files.
4. Availability notes.
5. Test plan.
6. Migration notes.
7. Privacy risks.
8. UI framework integration plan. For UIKit include scene routing, cold launch, multiwindow policy, primary activity annotation, selected-SDK-gated advanced annotations, reuse, promotion, drag/drop, SwiftUI islands, and UI tests.

Do not claim code is paste-ready if it references SDK-beta symbols that may drift. Say “compile-check with the selected Xcode SDK” and isolate likely drift points.

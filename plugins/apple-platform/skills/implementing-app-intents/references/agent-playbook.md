# Agent Playbook

Use this when responding to a user who wants App Intents implemented in a real codebase.

## First pass: ask or infer

Infer from the app domain when possible. Ask only when needed:

- App domain and core user objects.
- Minimum deployment target.
- Whether iOS 27 beta APIs may be used.
- SwiftUI/UIKit/AppKit mix. For UIKit, determine scene lifecycle, storyboard/programmatic construction, navigation containers, multiwindow/account model, diffable data sources, custom canvases, drag/drop, and Objective-C boundaries.
- Existing CoreSpotlight, SiriKit, WidgetKit, Shortcuts, or AppIntents code.
- Privacy constraints.
- Which system surfaces matter most.

If the user gave code, audit it before designing new files.

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
4. Create create/update/delete/search/control intents.
5. Create AppShortcutsProvider.
6. Add indexing/donation services.
7. Add onscreen annotations in views. In UIKit: primary `NSUserActivity`, view annotations, table/collection App Intents data sources, canvas provider, and reuse cleanup.
8. Add Transferable exports.
9. Add snippets/confirmation.
10. Add tests.
11. Add migration/deprecation wrappers.

## Code generation rules

- Prefer typed parameters over strings.
- Use schema macros when accurate.
- Add availability gates for iOS 27-only APIs.
- Keep repositories abstract if app storage is unknown.
- Mark UI navigation `@MainActor`. For UIKit, route through the system-selected scene and a per-scene coordinator; never generate `connectedScenes.first` navigation code. Use the exact `any UISceneAppIntent` delegate callback, choose one navigation owner per intent, and never invent `AppEntityAnnotatable` conformances.
- Avoid app-only dependencies in extension-targeted intents.
- Include privacy checks in query/index/export paths.
- Include `parameterSummary` for public/discoverable intents.
- Include `OpenIntent` for Spotlight/Visual Intelligence results.
- Include deletion of stale index items and donations.

## Audit questions

Ask these of every integration:

- Can Siri resolve the user’s nouns?
- Can Siri understand the user’s current screen? For UIKit, are primary activity, list/collection, selection, and custom-canvas annotations complete and reuse-safe?
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
8. UI framework integration plan. For UIKit include scene routing, cold launch, multiwindow policy, annotations, reuse, promotion, drag/drop, SwiftUI islands, and UI tests.

Do not claim code is paste-ready if it references SDK-beta symbols that may drift. Say “compile-check with the selected Xcode SDK” and isolate likely drift points.

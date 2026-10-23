# Shortcuts, Spotlight, Widgets, Controls, and Discovery

## Discovery surfaces

App Intents can appear in Shortcuts, Spotlight, Siri, Apple Intelligence planning, widgets, controls, Live Activities, Action button assignment, Focus automations, Visual Intelligence results, and in-app prediction surfaces.

Each surface has different visibility rules. A good integration makes the same entities and actions available through multiple appropriate surfaces without duplicating business logic.

## App Shortcuts

Use `AppShortcutsProvider` for zero-configuration actions users can invoke immediately.

App Shortcut phrase parameters must use supported fixed-value `AppEnum` or `AppEntity` parameters. Keep free-text and duration input out of phrase interpolation; collect those through the intent’s normal parameter flow. Swift typechecking alone does not verify App Shortcut metadata extraction. See [Explore enhancements to App Intents](https://developer.apple.com/videos/play/wwdc2023/10102/).

```swift
struct ProjectAppShortcuts: AppShortcutsProvider {
    static var appShortcuts: [AppShortcut] {
        AppShortcut(
            intent: CreateProjectIntent(),
            phrases: [
                "Create a project in \(.applicationName)",
                "Add a project in \(.applicationName)"
            ],
            shortTitle: "Create Project",
            systemImageName: "folder.badge.plus"
        )

        AppShortcut(
            intent: SearchInAppIntent(),
            phrases: [
                "Search \(.applicationName)",
                "Find content in \(.applicationName)"
            ],
            shortTitle: "Search",
            systemImageName: "magnifyingglass"
        )
    }
}
```

Phrase rules:

- Include `\(.applicationName)`.
- Include parameterized phrases for common direct invocations.
- Avoid phrase stuffing.
- Keep phrases localizable.
- Prefer user vocabulary over product-internal terms.
- Do not expect phrases to compensate for weak entity queries.

## Parameterized phrases

```swift
AppShortcut(
    intent: StartFocusSessionIntent(),
    phrases: [
        "Start a focus session in \(.applicationName)",
        "Focus on \(\.$project) in \(.applicationName)"
    ],
    shortTitle: "Start Focus",
    systemImageName: "timer"
)
```

The parameter type must have good query/suggestion behavior.

## Shortcuts “Use Model” and Apple Intelligence

Shortcuts can pass rich data between model-driven actions and App Intents. To be useful:

- Use typed parameters and return values.
- Use `AttributedString` for rich text content.
- Use entities with exposed properties and display representations.
- Use Transferable for files/images/PDFs/rich content.
- Avoid opaque string blobs.

```swift
struct SummarizeDocumentIntent: AppIntent {
    static let title: LocalizedStringResource = "Summarize Document"

    @Parameter(title: "Document")
    var document: DocumentEntity

    func perform() async throws -> some ReturnsValue<AttributedString> {
        let text = try await DocumentRepository.shared.plainText(for: document.id)
        let summary = try await Summarizer.shared.summary(for: text)
        return .result(value: AttributedString(summary))
    }
}
```

## Spotlight intent visibility

An intent generally needs these to appear well in Spotlight:

- Not hidden.
- Not `isDiscoverable == false`.
- Not `isAssistantOnly == true`.
- Valid `perform()`.
- Required parameters represented in `parameterSummary` or supplied by defaults.
- Parameter types the system can resolve.
- Good title, description, and system image.

```swift
static var parameterSummary: some ParameterSummary {
    Summary("Create \(\.$title) in \(\.$project)")
}
```

If an intent does not appear in Spotlight, check parameter summary first.

## Spotlight entity results

For entities to show as useful search results:

- Use `IndexedEntity` or CoreSpotlight association.
- Index title/body/description/date fields.
- Implement `OpenIntent`.
- Provide display representation.
- Keep index updated.
- Respect privacy settings.

```swift
try await CSSearchableIndex.default().indexAppEntities(projectEntities)
```

## Find actions

Shortcuts can create Find-style actions from `EntityPropertyQuery` and/or indexed entities.

```swift
static var properties: QueryProperties {
    QueryProperties {
        Property(\.title) {
            ContainsComparator { $0 }
            EqualToComparator { $0 }
        }
        Property(\.dueDate) {
            GreaterThanComparator { $0 }
            LessThanComparator { $0 }
        }
    }
}
```

Use semantic indexing for natural-language search over large corpora.

## Suggested entities

```swift
func suggestedEntities() async throws -> [ProjectEntity] {
    try await ProjectRepository.shared.recentOrPinned(limit: 12).map(ProjectEntity.init(model:))
}
```

Good suggestions are recent, favorite/pinned, active/current, context-aware, and limited. Bad suggestions are everything, random entities, private entities from another account, or expensive remote-only results.

## Donations

Donate actions the user actually performed or is likely to repeat.

```swift
func donateCompletedTask(_ task: TaskEntity) async {
    var intent = CompleteTaskIntent()
    intent.task = task
    try? await IntentDonationManager.shared.donate(intent: intent)
}
```

Delete donations when no longer valid:

```swift
try await IntentDonationManager.shared.deleteDonations(
    matching: .intentType(CompleteTaskIntent.self)
)
```

Rules:

- Donate meaningful actions, not every render.
- Include result values when supported and useful.
- Delete stale donations.
- Respect opt-out.
- Do not donate private browsing, locked notes, hidden photos, or sensitive content unless explicitly allowed.

## RelevantEntities

Apple documents `RelevantEntities` on iOS 27+ for media suggestions using supported audio contexts, such as Now Playing and workouts. It is not a general registry for documents, projects, routes, or arbitrary selected items. Use entity queries, screen annotations, and Spotlight for those surfaces. See [the current availability table](sdk-availability-and-verification.md#current-documentation-check--2026-10-23).

## PredictableIntent

`PredictableIntent` is available since iOS 16. Use it when the system should predict an action based on usage and context.

```swift
struct StartWorkoutIntent: AppIntent, PredictableIntent {
    static let title: LocalizedStringResource = "Start Workout"

    @Parameter(title: "Workout")
    var workout: WorkoutEntity

    static var predictionConfiguration: some IntentPredictionConfiguration {
        IntentPrediction(parameters: (\.$workout)) { workout in
            DisplayRepresentation(
                title: "Start \(workout.displayRepresentation.title)",
                subtitle: "Begin workout"
            )
        }
    }

    func perform() async throws -> some IntentResult {
        try await WorkoutManager.shared.start(workout.id)
        return .result()
    }
}
```

Use prediction for repeated, low-risk, context-sensitive actions. Avoid for destructive/sensitive operations.

## Widgets

Widgets can use App Intents for configuration and actions. A UIKit host app still implements WidgetKit presentation in SwiftUI; share the semantic entity/query/intent layer, not UIKit controllers or coordinators.

```swift
struct ProjectWidgetConfigurationIntent: WidgetConfigurationIntent {
    static let title: LocalizedStringResource = "Project Widget"

    @Parameter(title: "Project")
    var project: ProjectEntity?
}

struct CompleteTaskFromWidgetIntent: AppIntent {
    static let title: LocalizedStringResource = "Complete Task"

    @Parameter
    var task: TaskEntity

    func perform() async throws -> some IntentResult {
        try await TaskRepository.shared.complete(task.id)
        return .result()
    }
}
```

Rules:

- Widget intents must be fast and extension-safe unless routed elsewhere with execution targets.
- Share entities/queries with app intents.
- Avoid app-only singletons in widget extension execution.
- Refresh widget timelines after mutations.

## Controls

Controls are also WidgetKit/SwiftUI system surfaces even when the main app is UIKit. Their App Intents and domain services should remain UI-framework independent.

```swift
struct StartTimerControlIntent: AppIntent {
    static let title: LocalizedStringResource = "Start Timer"

    @Parameter(title: "Duration")
    var duration: Duration

    func perform() async throws -> some IntentResult {
        try await TimerService.shared.start(duration)
        return .result()
    }
}
```

Control intents should be low-latency, clear, minimally parameterized, and safe for their surface. Avoid unexpected foreground launches.

## Live Activities

A UIKit app hosts Live Activity UI through ActivityKit/WidgetKit SwiftUI. Keep activity attributes and intents shared while routing any app opening through the UIKit scene coordinator.

Patterns:

- Start a Live Activity from an intent result.
- Update state from a control intent.
- Open relevant content using OpenIntent.
- Use a long-running intent with progress when the operation spans time.

## Action button

App Shortcuts can be assigned to the Action button. Action-button-friendly shortcuts are fast, low ambiguity, safe without long dialog, useful from lock screen if permitted, have defaults/contextual suggestions, and do not require complex UI unless opening the app is the point.

Examples: start workout, capture note, open current project, add quick task, start timer, toggle app mode.

## Focus and automation

Use App Intents to adapt behavior around Focus states and automations: set app mode, start focus session, silence a project, change notification preferences, open a context-specific view. Avoid broad unexpected mutations from Focus changes.

## In-app promotion

```swift
// SwiftUI
SiriTipView(intent: CreateTaskIntent())
ShortcutsLink()

// UIKit
let tipView = SiriTipUIView()
tipView.setIntent(intent: CreateTaskIntent()) // Required before display.
tipView.isHidden = !tipView.isPresented

let shortcutsButton = ShortcutsUIButton(style: .automatic)
```

Show tips near the feature the shortcut automates. Do not spam. Keep phrase/title aligned with the actual intent. UIKit provides `ShortcutsUIButton(style:)` as the native counterpart to SwiftUI’s `ShortcutsLink`; prefer it over hosting SwiftUI or constructing a private URL. Siri tips and Shortcuts buttons must not own app navigation.

## Discovery debugging matrix

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| Intent missing in Spotlight | Required parameter not in summary | Add it to `parameterSummary` or default it. |
| App Shortcut phrase fails | Parameter query weak | Improve `EntityStringQuery` and suggestions. |
| Entity opens app but not item | Missing/incorrect OpenIntent routing | Implement/fix OpenIntent. |
| Siri asks too many follow-ups | Poor suggestions or missing parameterized phrase | Add suggestions and parameterized shortcut. |
| Find action missing | No property query/indexing | Add `EntityPropertyQuery` or indexing. |
| Wrong account content appears | Query/index ignores account | Filter and remove stale index entries. |
| Widget action fails | App-only dependency in extension | Use shared dependency or execution target. |
| Action button feels slow | Intent does network/clarification | Add defaults, cache, or open app directly. |

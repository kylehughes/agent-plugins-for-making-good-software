# Testing and Debugging App Intents

## Testing philosophy

Unit tests for repositories are not enough. App Intents need integration tests that exercise the framework boundary: generated intent definitions, parameter bridging, entity queries, result values, Spotlight indexing, view annotations, snippets, and execution in the same style used by Siri, Shortcuts, widgets, and Spotlight.

Use AppIntentsTesting where available, plus manual validation on devices.

## Test layers

1. Repository/domain unit tests.
2. Entity/query tests.
3. Intent execution tests.
4. Snippet result tests.
5. Spotlight indexing/query tests.
6. Onscreen annotation tests.
7. App Shortcut discovery tests.
8. Siri/Shortcuts manual tests.
9. Widget/control execution tests.
10. Migration and backward-compatibility tests.

## AppIntentsTesting setup

Use an XCUITest bundle for AppIntentsTesting integration tests.

```swift
import XCTest
import AppIntents
import AppIntentsTesting

final class TaskIntentTests: XCTestCase {
    let definitions = IntentDefinitions(bundleIdentifier: "com.example.app")

    override func setUp() async throws {
        continueAfterFailure = false
        try await TestDataSeeder.shared.resetAndSeed()
    }
}
```

Notes:

- The test bundle and app must be signed with the same team.
- Tests run outside the app process; do not import app-only internals unless shared through a testable package.
- Use test-only intents or test data hooks only when safe and excluded from production discovery.

## Executing an intent in tests

```swift
func testCreateTask() async throws {
    var intent = try definitions.makeIntent(CreateTaskIntent.self)
    intent.title = "Pay invoice"

    let result = try await intent.run()

    let value = try XCTUnwrap(result.value as? TaskEntity)
    XCTAssertEqual(value.title, "Pay invoice")
}
```

For custom entity/value types, wrap values as required by the SDK, for example with intent value conversion wrappers.

## Entity query test

```swift
func testTaskStringQueryFindsSeededTask() async throws {
    let query = TaskEntityQuery()
    let results = try await query.entities(matching: "invoice")

    XCTAssertEqual(results.first?.title, "Pay invoice")
}
```

Test exact matches, case-insensitive matches, diacritic matches if supported, empty search behavior, deleted IDs, wrong account IDs, permission-denied entities, ranking, and limits.

## Property query test

```swift
func testFindIncompleteTasksDueThisWeek() async throws {
    let query = TaskEntityQuery()
    let results = try await query.entities(
        matching: [
            .init(\.isCompleted, .equalTo(false)),
            .init(\.dueDate, .lessThan(Date.now.addingTimeInterval(7 * 86400)))
        ],
        mode: .and,
        sortedBy: [.init(\.dueDate, order: .ascending)],
        limit: 10
    )

    XCTAssertLessThanOrEqual(results.count, 10)
    XCTAssertTrue(results.allSatisfy { !$0.isCompleted })
}
```

Exact comparator constructors vary by SDK. The important coverage is AND/OR mode, sort, limit, and permission filtering.

## Chained intent test

```swift
func testCreateThenOpen() async throws {
    var create = try definitions.makeIntent(CreateProjectIntent.self)
    create.name = "Website Redesign"

    let createResult = try await create.run()
    let project = try XCTUnwrap(createResult.value as? ProjectEntity)

    var open = try definitions.makeIntent(OpenProjectIntent.self)
    open.target = project

    let openResult = try await open.run()
    XCTAssertTrue(openResult.didComplete)
}
```

Use chains to test real user paths.

## Spotlight indexing test

```swift
func testIndexedProjectAppearsInSpotlightQuery() async throws {
    let project = try await ProjectRepository.shared.create(name: "Launch Plan", overview: "Marketing timeline")
    try await ProjectIndexer.shared.index([project])

    let results = try await spotlightQuery("marketing timeline")

    XCTAssertTrue(results.contains { $0.entityIdentifier == project.id.uuidString })
}
```

Test index add, update, delete, privacy exclusion, title/content/semantic queries, and OpenIntent from result.

## View annotation test

```swift
func testProjectDetailAnnotatesCurrentProject() async throws {
    let app = XCUIApplication()
    app.launchArguments += ["-UITestSeedProject", "Launch Plan"]
    app.launch()

    app.buttons["Launch Plan"].tap()

    let annotations = try await viewAnnotations(in: app)
    XCTAssertTrue(annotations.containsEntity(ProjectEntity.self, id: seededProjectID))
}
```

Test detail primary entity, list rows, selection annotations, cell reuse, custom canvas annotations, and notification/Now Playing annotations if used. In UIKit, explicitly test table/collection App Intents data sources against diffable snapshot changes and verify reused cells do not retain old identifiers.

## Snippet test

```swift
func testCreateTaskReturnsSnippet() async throws {
    var intent = try definitions.makeIntent(CreateTaskIntent.self)
    intent.title = "Book flights"

    let result = try await intent.run()

    XCTAssertNotNil(result.snippet)
    XCTAssertEqual(result.dialog?.spokenText, "Created Book flights.")
}
```

Test result snippet, confirmation snippet before mutation, button/toggle intents, snippet reload, and dialog fallback.

## Long-running/cancellation test

```swift
func testExportCanBeCancelled() async throws {
    var intent = try definitions.makeIntent(ExportLargeProjectIntent.self)
    intent.project = seededLargeProject

    let task = Task { try await intent.run() }
    try await Task.sleep(for: .milliseconds(100))
    task.cancel()

    do {
        _ = try await task.value
        XCTFail("Expected cancellation")
    } catch is CancellationError {
        // Expected.
    }

    XCTAssertFalse(FileManager.default.fileExists(atPath: temporaryExportPath.path))
}
```

Test cancellation propagation, temporary cleanup, no success after cancel, and retry idempotency.

## Manual Siri matrix

Test utterances:

```text
Open [entity] in [app]
Create [thing] in [app]
Find [thing] in [app]
Show [category] from last week in [app]
Delete [specific thing] in [app]
Summarize this
Send this to [person]
Add these to [container]
Search for [semantic phrase] in [app]
```

For each, record whether Siri chose the expected intent, resolved the right entity, asked necessary follow-ups only, showed correct dialog/snippet/confirmation, navigated correctly, and preserved privacy.

## Manual Shortcuts matrix

Test each intent as a blank shortcut, configured with literals and variables, with model-generated text, `AttributedString`, `IntentFile`, Find actions, create→update→open chains, search→choose→open chains, and automations if relevant.

## Widget/control matrix

Test execution target, shared dependencies, timeline refresh, control state update, lock-screen behavior, network failure, and app opening behavior.

## Debugging: intent not discovered

Check:

- Type is in app target or included package.
- Target imports AppIntents.
- Intent has static `title`.
- Intent has `perform()`.
- Intent is not hidden/assistant-only for the desired surface.
- Required parameters appear in `parameterSummary` or have defaults.
- Parameter types conform correctly.
- App Shortcuts provider is in target.
- Availability gates do not exclude current OS.
- Extension/process includes intent package.
- Clean build/reinstall after changing definitions.

## Debugging: Siri resolves wrong entity

Check display title, string-query ranking, suggested entities, stale donations, stale Spotlight duplicates, onscreen annotations, account filtering, hidden/private exclusions, and enum display names.

## Debugging: Spotlight missing entity

Check `IndexedEntity`/CoreSpotlight association, indexable properties, indexing call success, identifier match, privacy exclusion, OpenIntent, index update timing, and deleted stale records.

## Debugging: snippet fails

Check snippet intent parameter serializability, data fetching in `perform()`, no slow work in `body`, button/toggle intent wiring, no hidden mutation in render-only snippet, supported SwiftUI APIs, and dialog fallback.

## Debugging: foreground continuation fails

Check protocol conformance, continuation availability, app scene/user activity handling, main-actor router, denial path, and resume behavior after activation.

## UIKit integration tests

UIKit adds scene, annotation, reuse, and multiwindow failure modes that entity/intent unit tests cannot catch.

Test at minimum:

- Warm navigation through `UISceneAppIntent` or `AppIntentSceneDelegate`.
- Cold scene creation from an App Intent without duplicate routing.
- Correct tab, navigation stack, split column, and modal policy.
- Two scenes open to different accounts/workspaces; the intent reaches only a compatible scene.
- An entity already open is focused rather than pushed twice.
- `NSUserActivity.appEntityIdentifier` changes when the primary controller changes semantic subject and is invalidated on disappearance/privacy mode.
- `UITableViewAppIntentsDataSource` and `UICollectionViewAppIntentsDataSource` map through stable diffable item IDs after reorder/filter/snapshot updates.
- Reusable cells clear old `appEntityIdentifier` values.
- Custom-canvas `appEntityUIElementProvider` updates bounds and selection and performs no I/O.
- `SiriTipUIView` is configured with `setIntent(intent:)`, lays out correctly, and honors `isPresented`.
- Drag providers load data without presenting UI from `sessionWillBegin`.
- Storyboard and restoration paths install the scene coordinator before intent callbacks.

Unit-test a pure `AppIntent → NavigationRoute` mapper separately from `UIScene`. UI-test the real route and annotation hierarchy.

## CI recommendations

- Run AppIntentsTesting in XCUITest on every PR touching intents/entities/queries/indexing.
- Include deterministic seed data.
- Run at least one Spotlight test on a clean simulator.
- Run UI annotation tests on stable views.
- Add migration tests for changed definitions.
- Capture snippet screenshots if feasible.
- Run device smoke tests before release for Siri and Visual Intelligence.

## Release gate

Do not ship until every public intent executes, every durable entity has ID lookup tests, every OpenIntent navigates, every indexed entity add/update/remove path works, destructive actions confirm, sensitive actions pass privacy review, snippets have dialog fallback, App Shortcuts appear in intended surfaces, and old shortcuts still run or show deprecation guidance.

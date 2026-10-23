# UIKit App Intents Examples

Check [current availability](sdk-availability-and-verification.md#current-documentation-check--2026-10-23) for SDK-specific examples; retain older-SDK build lanes only when required by the project.

Availability note: buildable iPhoneOS 26.5 UIKit onscreen context is `NSUserActivity.appEntityIdentifier` for the primary screen entity. Sections that mention per-view `appEntityIdentifier`, table/collection App Intents data sources, custom canvas providers, notification `appEntityIdentifiers`, or AppIntentsTesting are selected-SDK-gated unless explicitly stated otherwise.

These examples focus on UIKit-specific integration. Entity/query/intent definitions remain the same as in [examples.md](examples.md).

The examples span SDK generations; determine stable versus preview status from the project’s selected SDK. Code marked **SDK-sensitive** shows the intended API shape; use Xcode autocomplete and compiler diagnostics for the selected SDK’s exact declaration.

## Shared assumptions

```swift
import AppIntents
import UIKit

struct ProjectEntity: AppEntity, Identifiable, Sendable {
    static let defaultQuery = ProjectEntityQuery()

    static var typeDisplayRepresentation: TypeDisplayRepresentation {
        TypeDisplayRepresentation(
            name: "Project",
            numericFormat: "\(placeholder: .int) projects"
        )
    }

    let id: UUID
    let name: String

    var displayRepresentation: DisplayRepresentation {
        DisplayRepresentation(
            title: "\(name)",
            image: .init(systemName: "folder")
        )
    }
}

struct TaskEntity: AppEntity, Identifiable, Sendable {
    static let defaultQuery = TaskEntityQuery()

    static var typeDisplayRepresentation: TypeDisplayRepresentation {
        TypeDisplayRepresentation(
            name: "Task",
            numericFormat: "\(placeholder: .int) tasks"
        )
    }

    let id: UUID
    let title: String
    let projectID: UUID

    var displayRepresentation: DisplayRepresentation {
        DisplayRepresentation(
            title: "\(title)",
            image: .init(systemName: "checkmark.circle")
        )
    }
}
```

Use durable IDs from the domain store. The entity values above contain no UIKit state.

## App startup and dependency registration

Register repositories and services once. Create navigation coordinators per scene.

```swift
@main
final class AppDelegate: UIResponder, UIApplicationDelegate {
    let projectRepository = ProjectRepository.live
    let taskRepository = TaskRepository.live
    let projectService = ProjectService.live

    func application(
        _ application: UIApplication,
        didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]? = nil
    ) -> Bool {
        AppDependencyManager.shared.add(dependency: projectRepository)
        AppDependencyManager.shared.add(dependency: taskRepository)
        AppDependencyManager.shared.add(dependency: projectService)
        return true
    }

    func application(
        _ application: UIApplication,
        configurationForConnecting connectingSceneSession: UISceneSession,
        options: UIScene.ConnectionOptions
    ) -> UISceneConfiguration {
        let configuration = UISceneConfiguration(
            name: "Default Configuration",
            sessionRole: connectingSceneSession.role
        )
        configuration.delegateClass = SceneDelegate.self
        return configuration
    }
}
```

Do not register a single global navigation controller as an App Intent dependency.

## Semantic route and per-scene coordinator

```swift
enum NavigationRoute: Equatable, Sendable {
    case project(ProjectEntity.ID)
    case task(TaskEntity.ID)
    case search(String)
    case export(ProjectEntity.ID)
}

@MainActor
protocol SceneRouting: AnyObject {
    func canHandle(_ route: NavigationRoute) -> Bool
    func route(_ route: NavigationRoute, animated: Bool)
}

@MainActor
final class SceneCoordinator: SceneRouting {
    private let window: UIWindow
    private let tabBarController: UITabBarController
    private let projectsNavigationController: UINavigationController
    private let searchNavigationController: UINavigationController

    init(windowScene: UIWindowScene) {
        window = UIWindow(windowScene: windowScene)
        tabBarController = UITabBarController()
        projectsNavigationController = UINavigationController(
            rootViewController: ProjectsViewController()
        )
        searchNavigationController = UINavigationController(
            rootViewController: SearchViewController()
        )

        projectsNavigationController.tabBarItem = UITabBarItem(
            title: "Projects",
            image: UIImage(systemName: "folder"),
            tag: 0
        )
        searchNavigationController.tabBarItem = UITabBarItem(
            title: "Search",
            image: UIImage(systemName: "magnifyingglass"),
            tag: 1
        )

        tabBarController.viewControllers = [
            projectsNavigationController,
            searchNavigationController,
        ]
        window.rootViewController = tabBarController
    }

    func start() {
        window.makeKeyAndVisible()
    }

    func canHandle(_ route: NavigationRoute) -> Bool {
        // Add account/workspace/editing-state checks here.
        true
    }

    func route(_ route: NavigationRoute, animated: Bool = true) {
        guard canHandle(route) else { return }

        switch route {
        case .project(let id):
            tabBarController.selectedViewController = projectsNavigationController
            showProject(id, animated: animated)

        case .task(let id):
            tabBarController.selectedViewController = projectsNavigationController
            showTask(id, animated: animated)

        case .search(let term):
            tabBarController.selectedViewController = searchNavigationController
            let controller = searchNavigationController.viewControllers
                .compactMap { $0 as? SearchViewController }
                .first
            controller?.applySearch(term)

        case .export(let projectID):
            tabBarController.selectedViewController = projectsNavigationController
            showExport(projectID, animated: animated)
        }
    }

    private func showProject(_ id: UUID, animated: Bool) {
        if let existing = projectsNavigationController.viewControllers
            .compactMap({ $0 as? ProjectDetailViewController })
            .first(where: { $0.projectID == id }) {
            projectsNavigationController.popToViewController(existing, animated: animated)
            existing.refreshIfNeeded()
            return
        }

        let detail = ProjectDetailViewController(projectID: id)
        projectsNavigationController.pushViewController(detail, animated: animated)
    }

    private func showTask(_ id: UUID, animated: Bool) {
        let detail = TaskDetailViewController(taskID: id)
        projectsNavigationController.pushViewController(detail, animated: animated)
    }

    private func showExport(_ projectID: UUID, animated: Bool) {
        let controller = ExportViewController(projectID: projectID)
        projectsNavigationController.present(controller, animated: animated)
    }
}
```

The route is stable and testable. Whether it becomes a push, tab switch, split-column update, or modal is UIKit implementation detail.

## Scene-delegate-routed intents

The following intents use **centralized scene-delegate routing**. They adopt `UISceneAppIntent` so UIKit can target a scene, but they intentionally use the protocol's default `performNavigation(forScene:)` implementation. `SceneDelegate` is the sole navigation owner for these types.

```swift
struct OpenProjectIntent: OpenIntent {
    static let title: LocalizedStringResource = "Open Project"

    @Parameter(title: "Project")
    var target: ProjectEntity

    func perform() async throws -> some IntentResult {
        .result()
    }
}

@AppIntent(schema: .system.searchInApp)
struct SearchProjectsIntent: ShowInAppSearchResultsIntent {
    static let searchScopes: [StringSearchScope] = [.general]
    var criteria: StringSearchCriteria

    func perform() async throws -> some IntentResult {
        .result()
    }
}

@available(iOS 26.0, *)
extension OpenProjectIntent: UISceneAppIntent {}

@available(iOS 26.0, *)
extension SearchProjectsIntent: UISceneAppIntent {}
```

**One-owner rule:** an intent routed by `AppIntentSceneDelegate` must not also navigate in a custom `performNavigation(forScene:)`. Conversely, the scene delegate must ignore an intent whose custom `performNavigation(forScene:)` owns navigation. The callback may observe every scene-targeted intent, so duplicate ownership causes duplicate pushes or presentations.

The empty conformances above rely on the SDK-provided default navigation implementation. The exact schema/conformance relationship is SDK-sensitive; compile-check it against the selected iOS SDK.

## `SceneDelegate` plus `AppIntentSceneDelegate`

**SDK-sensitive declaration shape.** The scene callback is for preparation/routing. Do not call `perform()` on the supplied intent.

```swift
import AppIntents
import UIKit

@MainActor
final class SceneDelegate: UIResponder, UIWindowSceneDelegate, AppIntentSceneDelegate {
    private(set) var coordinator: SceneCoordinator!

    func scene(
        _ scene: UIScene,
        willConnectTo session: UISceneSession,
        options connectionOptions: UIScene.ConnectionOptions
    ) {
        guard let windowScene = scene as? UIWindowScene else { return }

        coordinator = SceneCoordinator(windowScene: windowScene)
        coordinator.start()

        // `connectionOptions.appIntent` can explain why this scene was created.
        // Do not route it here and again in `willPerformAppIntent` unless the
        // app has explicit deduplication.
        if connectionOptions.appIntent != nil {
            prepareForIntentDrivenLaunch()
        }
    }

    func scene(_ scene: UIScene, willPerformAppIntent appIntent: any UISceneAppIntent) {
        guard let route = Self.route(for: appIntent) else { return }
        coordinator.route(route, animated: scene.activationState == .foregroundActive)

        // Never: try await appIntent.perform()
        // App Intents owns execution.
    }

    private func prepareForIntentDrivenLaunch() {
        // Restore only the minimum root/account state needed for routing.
    }

    private static func route(for intent: any AppIntent) -> NavigationRoute? {
        switch intent {
        case let open as OpenProjectIntent:
            return .project(open.target.id)
        case let search as SearchProjectsIntent:
            return .search(search.criteria.term)
        default:
            // `OpenTaskIntent` owns navigation in `performNavigation(forScene:)`.
            return nil
        }
    }

    // Keep this pure and internal so unit tests do not need a real UIScene.
    static func routeForTesting(_ intent: any AppIntent) -> NavigationRoute? {
        route(for: intent)
    }
}
```

Centralizing the mapping allows tests to verify every delegate-routed public intent has a UIKit route. Direct-navigation intent types should deliberately map to `nil`.

## `UISceneAppIntent` direct navigation

Use this when the intent type itself should express how to navigate a system-selected scene. `performNavigation(forScene:)` is main-actor UIKit work. Do not also add the same type to the scene delegate's route mapper.

```swift
struct OpenTaskIntent: OpenIntent {
    static let title: LocalizedStringResource = "Open Task"

    @Parameter(title: "Task")
    var target: TaskEntity

    func perform() async throws -> some IntentResult {
        // Domain work is optional for an open-only intent.
        .result()
    }
}

@available(iOS 26.0, *)
extension OpenTaskIntent: UISceneAppIntent {
    @MainActor
    func performNavigation(forScene scene: UIScene) {
        guard
            let delegate = scene.delegate as? SceneDelegate,
            delegate.coordinator.canHandle(.task(target.id))
        else {
            return
        }

        delegate.coordinator.route(.task(target.id), animated: true)
    }
}
```

Some SDK versions may require an additional target-content conformance or provide a different default-implementation relationship. Compile-check the selected SDK rather than adding a global window-discovery fallback.

## Scene activation conditions

Activation conditions help UIKit choose among existing scenes before the coordinator routes. Use the same target-content identifier namespace on both sides.

```swift
@MainActor
func configureSceneAffinity(
    _ scene: UIScene,
    workspaceID: UUID,
    preferredProjectID: UUID?
) {
    let workspacePrefix = "workspace:\(workspaceID.uuidString)/"
    let conditions = UISceneActivationConditions()

    conditions.canActivateForTargetContentIdentifierPredicate = NSPredicate(
        format: "SELF BEGINSWITH %@",
        workspacePrefix
    )

    if let preferredProjectID {
        let preferredIdentifier = workspacePrefix
            + "project:"
            + preferredProjectID.uuidString
        conditions.prefersToActivateForTargetContentIdentifierPredicate = NSPredicate(
            format: "SELF == %@",
            preferredIdentifier
        )
    }

    scene.activationConditions = conditions
}
```

Activation conditions are candidate-selection policy, not authorization. The coordinator must still reject an incompatible account, protected entity, unsaved editor, or destructive modal. The exact API that supplies an incoming App Intent's target-content identifier is SDK-sensitive.

## Split-view routing

```swift
@MainActor
final class DocumentSceneCoordinator: SceneRouting {
    private let splitViewController: UISplitViewController

    func route(_ route: NavigationRoute, animated: Bool) {
        switch route {
        case .project(let id):
            let detail = ProjectDetailViewController(projectID: id)
            let navigation = UINavigationController(rootViewController: detail)
            splitViewController.setViewController(navigation, for: .secondary)

        default:
            break
        }
    }

    func canHandle(_ route: NavigationRoute) -> Bool {
        !isPresentingDestructiveEditor
    }
}
```

For compact-width collapse, let the coordinator’s normal split-view policy determine where the detail appears. Do not encode size-class behavior in the App Intent.

## Primary onscreen entity with `NSUserActivity`

```swift
import AppIntents
import UIKit

@MainActor
final class ProjectDetailViewController: UIViewController {
    let projectID: ProjectEntity.ID

    private var project: ProjectModel?
    private var viewingActivity: NSUserActivity?

    init(projectID: ProjectEntity.ID) {
        self.projectID = projectID
        super.init(nibName: nil, bundle: nil)
    }

    @available(*, unavailable)
    required init?(coder: NSCoder) {
        fatalError("init(coder:) has not been implemented")
    }

    override func viewDidAppear(_ animated: Bool) {
        super.viewDidAppear(animated)
        publishPrimaryEntity()
    }

    override func viewWillDisappear(_ animated: Bool) {
        super.viewWillDisappear(animated)
        stopPublishingPrimaryEntity()
    }

    func apply(_ project: ProjectModel) {
        self.project = project
        title = project.name

        if viewIfLoaded?.window != nil {
            publishPrimaryEntity()
        }
    }

    private func publishPrimaryEntity() {
        guard let project, project.isVisibleToCurrentUser else {
            stopPublishingPrimaryEntity()
            return
        }

        stopPublishingPrimaryEntity()

        let activity = NSUserActivity(activityType: "com.example.projects.view-project")
        activity.title = "Viewing \(project.name)"
        activity.appEntityIdentifier = EntityIdentifier(
            for: ProjectEntity.self,
            identifier: project.id
        )

        // Set Handoff, prediction, search, or restoration eligibility only
        // when the product intentionally supports those features.
        userActivity = activity
        activity.becomeCurrent()
        viewingActivity = activity
    }

    private func stopPublishingPrimaryEntity() {
        viewingActivity?.resignCurrent()
        viewingActivity?.invalidate()
        viewingActivity = nil
        userActivity = nil
    }
}
```

If the controller stays visible while switching among child entities, republish whenever the semantic subject changes.

## Selected-SDK-dependent: annotating an individual `UIView`

Use the current availability reference and selected SDK declarations for this surface. Omit or source-gate unsupported APIs only when preserving a required older-SDK build lane; runtime gates alone cannot supply missing declarations.

```swift
@MainActor
final class ProjectHeaderView: UIView {
    private let titleLabel = UILabel()
    private var representedProjectID: ProjectEntity.ID?

    func configure(project: ProjectModel) {
        representedProjectID = project.id
        titleLabel.text = project.name

        appEntityIdentifier = project.isVisibleToCurrentUser
            ? EntityIdentifier(for: ProjectEntity.self, identifier: project.id)
            : nil
    }

    func clear() {
        representedProjectID = nil
        titleLabel.text = nil
        appEntityIdentifier = nil
    }
}
```

Annotate the semantic container, not every child label/image.

## Reusable cell hygiene

The stable-ID cleanup portion is buildable today. The `contentView.appEntityIdentifier` lines are selected-SDK-dependent and must be removed or source-gated unless the selected SDK declares per-view annotation on UIKit views.

```swift
@MainActor
final class TaskCell: UITableViewCell {
    private(set) var representedTaskID: TaskEntity.ID?

    override func prepareForReuse() {
        super.prepareForReuse()
        representedTaskID = nil
        contentConfiguration = nil
        contentView.appEntityIdentifier = nil
        accessibilityIdentifier = nil
    }

    func configure(with task: TaskModel) {
        representedTaskID = task.id
        var content = defaultContentConfiguration()
        content.text = task.title
        content.secondaryText = task.projectName
        contentConfiguration = content

        contentView.appEntityIdentifier = task.isVisibleToCurrentUser
            ? EntityIdentifier(for: TaskEntity.self, identifier: task.id)
            : nil
        accessibilityIdentifier = "task.\(task.id.uuidString)"
    }
}
```

Even when a collection data source supplies identifiers, clearing any per-cell annotation avoids stale data from earlier implementations or child views.

## Selected-SDK-dependent: `UITableViewAppIntentsDataSource`

Use the current availability reference and selected SDK declarations for this surface. Omit or source-gate unsupported APIs only when preserving a required older-SDK build lane; runtime gates alone cannot supply missing declarations.

```swift
import AppIntents
import UIKit

@MainActor
final class TasksViewController: UITableViewController,
    UITableViewAppIntentsDataSource {

    enum Section: Hashable { case main }

    private lazy var dataSource = UITableViewDiffableDataSource<Section, TaskEntity.ID>(
        tableView: tableView
    ) { [weak self] tableView, indexPath, taskID in
        guard let self else { return nil }
        let cell = tableView.dequeueReusableCell(
            withIdentifier: "TaskCell",
            for: indexPath
        ) as! TaskCell

        if let task = self.tasksByID[taskID] {
            cell.configure(with: task)
        }
        return cell
    }

    private var tasksByID: [TaskEntity.ID: TaskModel] = [:]

    override func viewDidLoad() {
        super.viewDidLoad()
        tableView.register(TaskCell.self, forCellReuseIdentifier: "TaskCell")
        tableView.appIntentsDataSource = self
    }

    func tableView(
        _ tableView: UITableView,
        appEntityIdentifierForRowAt indexPath: IndexPath
    ) -> EntityIdentifier? {
        guard
            let taskID = dataSource.itemIdentifier(for: indexPath),
            let task = tasksByID[taskID],
            task.isVisibleToCurrentUser
        else {
            return nil
        }

        return EntityIdentifier(for: TaskEntity.self, identifier: taskID)
    }
}
```

The index path is used only to query the current diffable snapshot.

## Selected-SDK-dependent: `UICollectionViewAppIntentsDataSource`

Use the current availability reference and selected SDK declarations for this surface. Omit or source-gate unsupported APIs only when preserving a required older-SDK build lane; runtime gates alone cannot supply missing declarations.

```swift
import AppIntents
import UIKit

@MainActor
final class ProjectGridViewController: UIViewController,
    UICollectionViewAppIntentsDataSource {

    enum Section: Hashable { case recent, all }

    private let collectionView: UICollectionView
    private var projectsByID: [ProjectEntity.ID: ProjectModel] = [:]
    private lazy var dataSource = makeDataSource()

    init() {
        collectionView = UICollectionView(
            frame: .zero,
            collectionViewLayout: Self.makeLayout()
        )
        super.init(nibName: nil, bundle: nil)
    }

    @available(*, unavailable)
    required init?(coder: NSCoder) { fatalError() }

    override func viewDidLoad() {
        super.viewDidLoad()
        collectionView.appIntentsDataSource = self
    }

    func collectionView(
        _ collectionView: UICollectionView,
        appEntityIdentifierForItemAt indexPath: IndexPath
    ) -> EntityIdentifier? {
        guard
            let projectID = dataSource.itemIdentifier(for: indexPath),
            projectsByID[projectID]?.isVisibleToCurrentUser == true
        else {
            return nil
        }

        return EntityIdentifier(for: ProjectEntity.self, identifier: projectID)
    }

    private static func makeLayout() -> UICollectionViewLayout {
        UICollectionViewCompositionalLayout.list(using: .init(appearance: .insetGrouped))
    }

    private func makeDataSource()
        -> UICollectionViewDiffableDataSource<Section, ProjectEntity.ID> {
        UICollectionViewDiffableDataSource(
            collectionView: collectionView
        ) { collectionView, indexPath, projectID in
            // Configure a cell from `projectsByID[projectID]`.
            UICollectionViewCell()
        }
    }
}
```

Return `nil` for loading placeholders, inaccessible entities, advertisements, and purely decorative cells.

## Model-level selection across offscreen rows

```swift
@MainActor
final class SelectionModel<ID: Hashable & Sendable> {
    private(set) var selectedIDs: Set<ID> = []

    func setSelected(_ selected: Bool, id: ID) {
        if selected {
            selectedIDs.insert(id)
        } else {
            selectedIDs.remove(id)
        }
    }

    func removeUnavailableIDs(_ available: Set<ID>) {
        selectedIDs.formIntersection(available)
    }
}
```

The table/collection and App Intents annotation adapter should read from the same selection model. Do not lose semantic selection merely because a cell scrolled away.

## Selected-SDK-dependent: custom canvas with `appEntityUIElementProvider`

Use the current availability reference and selected SDK declarations for this surface. Omit or source-gate unsupported APIs only when preserving a required older-SDK build lane; runtime gates alone cannot supply missing declarations.

```swift
import AppIntents
import UIKit

@MainActor
final class BoardCanvasView: UIView {
    struct VisibleCard {
        let id: UUID
        let frameInCanvas: CGRect
        let isSelected: Bool
        let isVisibleToCurrentUser: Bool
    }

    var visibleCards: [VisibleCard] = [] {
        didSet {
            setNeedsDisplay()
        }
    }

    override init(frame: CGRect) {
        super.init(frame: frame)
        installEntityElementProvider()
    }

    required init?(coder: NSCoder) {
        super.init(coder: coder)
        installEntityElementProvider()
    }

    private func installEntityElementProvider() {
        appEntityUIElementProvider = { [weak self] view, _ in
            guard let self else { return [] }

            return self.visibleCards.compactMap { card in
                guard card.isVisibleToCurrentUser else { return nil }

                let visibleBounds = card.frameInCanvas.intersection(view.bounds)
                guard !visibleBounds.isNull, !visibleBounds.isEmpty else { return nil }

                return AppEntityUIElement(
                    identifier: EntityIdentifier(
                        for: CardEntity.self,
                        identifier: card.id
                    ),
                    bounds: visibleBounds,
                    state: AppEntityUIElement.State(
                        isSelected: card.isSelected
                    ),
                    subelements: []
                )
            }
        }
    }
}
```

Do not query a database or mutate selection inside the provider. If the SDK exposes useful request context, use it only to reduce the returned geometry.

## Fast display-representation lookup

```swift
struct ProjectEntityQuery: EntityStringQuery {
    @Dependency var repository: ProjectRepository

    func entities(for identifiers: [ProjectEntity.ID]) async throws -> [ProjectEntity] {
        try await repository.entities(for: identifiers)
    }

    func entities(matching string: String) async throws -> [ProjectEntity] {
        try await repository.search(string)
    }

    func displayRepresentations(
        for identifiers: [ProjectEntity.ID]
    ) async throws -> [ProjectEntity.ID: DisplayRepresentation] {
        let summaries = try await repository.summaries(for: identifiers)
        return Dictionary(uniqueKeysWithValues: summaries.map { summary in
            (
                summary.id,
                DisplayRepresentation(
                    title: "\(summary.name)",
                    subtitle: summary.workspaceName.map { "\($0)" }
                )
            )
        })
    }
}
```

This lets Siri resolve many onscreen IDs without loading full projects or images.

## `SiriTipUIView`

```swift
import AppIntents
import UIKit

@MainActor
final class ProjectActionsViewController: UIViewController {
    private let siriTipView = SiriTipUIView()

    override func viewDidLoad() {
        super.viewDidLoad()

        siriTipView.setIntent(intent: CreateTaskIntent())
        siriTipView.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(siriTipView)

        NSLayoutConstraint.activate([
            siriTipView.leadingAnchor.constraint(equalTo: view.layoutMarginsGuide.leadingAnchor),
            siriTipView.trailingAnchor.constraint(equalTo: view.layoutMarginsGuide.trailingAnchor),
            siriTipView.topAnchor.constraint(equalTo: view.safeAreaLayoutGuide.topAnchor),
        ])

        siriTipView.isHidden = !siriTipView.isPresented
    }

    func updateTip(for project: ProjectEntity) {
        siriTipView.setIntent(
            intent: CreateTaskIntent(project: project)
        )
        siriTipView.isHidden = !siriTipView.isPresented
    }
}
```

The exact synthesized initializer for an intent depends on its parameter declarations. Assign parameters after initialization when no suitable initializer exists.

## Native `ShortcutsUIButton`

UIKit has a first-party button for opening the current app’s page in Shortcuts. No SwiftUI hosting bridge is needed.

```swift
import AppIntents
import UIKit

@MainActor
final class AutomationDiscoveryViewController: UIViewController {
    private let shortcutsButton = ShortcutsUIButton(style: .automatic)

    override func viewDidLoad() {
        super.viewDidLoad()

        shortcutsButton.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(shortcutsButton)

        NSLayoutConstraint.activate([
            shortcutsButton.leadingAnchor.constraint(
                equalTo: view.layoutMarginsGuide.leadingAnchor
            ),
            shortcutsButton.topAnchor.constraint(
                equalTo: view.safeAreaLayoutGuide.topAnchor
            ),
        ])
    }
}
```

Use `.automatic` or `.automaticOutline` unless the surrounding surface requires an explicit light/dark style. The button owns its Shortcuts navigation; do not add a duplicate target action or substitute a private URL scheme.

## Donate a successful UIKit interaction

```swift
import AppIntents
import UIKit

@MainActor
final class ProjectDetailViewController: UIViewController {
    let projectID: ProjectEntity.ID
    private let service: ProjectService

    @objc private func favoriteButtonTapped() {
        let projectID = projectID

        Task {
            let updated = try await service.setFavorite(true, projectID: projectID)
            applyFavoriteState(updated.isFavorite)

            let entity = ProjectEntity(id: updated.id, name: updated.name)
            let intent = FavoriteProjectIntent(project: entity, isFavorite: true)
            try? await IntentDonationManager.shared.donate(intent: intent)
        }
    }
}
```

Donate after success. Do not donate from `cellForRowAt`, prefetch, view appearance, or the App Intent’s own `perform()`.

## Shared UI action and App Intent service

Avoid duplicating business logic between UIKit and App Intents.

```swift
actor TaskCompletionService {
    func setCompleted(_ completed: Bool, taskID: UUID) async throws -> TaskModel {
        // Authorization, idempotency, persistence, sync, indexing.
    }
}

struct CompleteTaskIntent: AppIntent {
    @Parameter var task: TaskEntity
    @Dependency var completionService: TaskCompletionService

    func perform() async throws -> some IntentResult {
        _ = try await completionService.setCompleted(true, taskID: task.id)
        return .result()
    }
}

@MainActor
final class TaskDetailViewController: UIViewController {
    let taskID: UUID
    let completionService: TaskCompletionService

    @objc private func completeTapped() {
        Task {
            _ = try await completionService.setCompleted(true, taskID: taskID)
            renderCompletedState()
            // Donate the corresponding schema intent here if meaningful.
        }
    }
}
```

The UI action and intent share a service but do not invoke each other.

## Visual Intelligence result opened in UIKit

```swift
@UnionValue
enum VisualProjectResult {
    case project(ProjectEntity)
    case task(TaskEntity)
}

struct VisualProjectQuery: IntentValueQuery {
    @Dependency var searchService: SemanticSearchService

    func values(
        for input: SemanticContentDescriptor
    ) async throws -> [VisualProjectResult] {
        try await searchService.search(input, limit: 30)
    }
}

```

Every union case returned by the value query needs a viable open path.

## In-app search intent routed to UIKit

`SearchProjectsIntent`, declared earlier, is scene-delegate-routed. Its structured criteria become a semantic, restorable UIKit route:

```swift
case let search as SearchProjectsIntent:
    return .search(search.criteria.term)
```

The search intent does not find a window in `perform()`, and it does not also implement custom scene navigation. The exact schema/protocol relationship is SDK-sensitive; the durable architecture is structured criteria → selected scene → coordinator route → UIKit search controller.

## Selected-SDK-dependent: notification entity annotation

Use the current availability reference and selected SDK declarations for this surface. Omit or source-gate unsupported APIs only when preserving a required older-SDK build lane; runtime gates alone cannot supply missing declarations.

```swift
import AppIntents
import UserNotifications

func makeTaskNotification(task: TaskModel) -> UNMutableNotificationContent {
    let content = UNMutableNotificationContent()
    content.title = task.title
    content.body = task.projectName

    if task.isVisibleOnLockScreenToCurrentUser {
        content.appEntityIdentifiers = [
            EntityIdentifier(for: TaskEntity.self, identifier: task.id)
        ]
    }

    return content
}
```

Do not annotate a notification with an entity that cannot be safely resolved from the lock-screen context.

## Drag provider backed by the same export service

```swift
import UIKit
import UniformTypeIdentifiers

final class ProjectDragDelegate: NSObject, UIDragInteractionDelegate {
    let projectID: UUID
    let exportService: ProjectExportService

    func dragInteraction(
        _ interaction: UIDragInteraction,
        itemsForBeginning session: any UIDragSession
    ) -> [UIDragItem] {
        let provider = NSItemProvider()

        provider.registerDataRepresentation(
            forTypeIdentifier: UTType.plainText.identifier,
            visibility: .all
        ) { [projectID, exportService] completion in
            Task {
                do {
                    let data = try await exportService.plainText(projectID: projectID)
                    completion(data, nil)
                } catch {
                    completion(nil, error)
                }
            }
            return nil
        }

        let item = UIDragItem(itemProvider: provider)
        item.localObject = projectID
        return [item]
    }

    func dragInteraction(
        _ interaction: UIDragInteraction,
        sessionWillBegin session: any UIDragSession
    ) {
        // Do not present UI or animate selection here. Apple Intelligence can
        // request drag resources without the normal user gesture path.
    }
}
```

The export service should enforce the same authorization and redaction rules as the entity’s `Transferable` conformance.

## Mixed Objective-C facade

```swift
import AppIntents
import UIKit

@objcMembers
@MainActor
final class AppIntentUIKitBridge: NSObject {
    static let shared = AppIntentUIKitBridge()

    // Selected-SDK-dependent: only compile this adapter when the selected SDK exposes
    // per-view entity annotation on UIKit views.
    func annotate(
        view: UIView,
        projectIdentifier: UUID?,
        isAuthorized: Bool
    ) {
        guard let projectIdentifier, isAuthorized else {
            view.appEntityIdentifier = nil
            return
        }

        view.appEntityIdentifier = EntityIdentifier(
            for: ProjectEntity.self,
            identifier: projectIdentifier
        )
    }

    func donateProjectOpen(identifier: UUID, name: String) {
        let entity = ProjectEntity(id: identifier, name: name)
        Task {
            try? await IntentDonationManager.shared.donate(
                intent: OpenProjectIntent(target: entity)
            )
        }
    }
}
```

Objective-C controllers pass stable IDs and operation data into the Swift bridge; they do not model App Entities themselves.

## Annotation policy adapter

Centralize privacy and availability checks.

```swift
struct OnscreenEntityPolicy: Sendable {
    let accountID: UUID
    let privacyModeEnabled: Bool

    func identifier(
        for project: ProjectModel
    ) -> EntityIdentifier? {
        guard !privacyModeEnabled else { return nil }
        guard project.accountID == accountID else { return nil }
        guard project.isVisibleToCurrentUser else { return nil }

        return EntityIdentifier(
            for: ProjectEntity.self,
            identifier: project.id
        )
    }
}
```

Use the same policy for activity, view, table/collection, canvas, and drag annotations.

## Unit-test the route mapper

```swift
import XCTest
@testable import ExampleApp

final class AppIntentRouteTests: XCTestCase {
    func testOpenProjectMapsToProjectRoute() throws {
        let project = ProjectEntity(id: UUID(), name: "Launch")
        let intent = OpenProjectIntent(target: project)

        let route = SceneDelegate.routeForTesting(intent)

        XCTAssertEqual(route, .project(project.id))
    }

    func testDirectNavigationIntentDoesNotAlsoRouteThroughDelegate() throws {
        let task = TaskEntity(
            id: UUID(),
            title: "Ship",
            projectID: UUID()
        )
        let intent = OpenTaskIntent(target: task)

        XCTAssertNil(SceneDelegate.routeForTesting(intent))
    }

    func testMutationOnlyIntentDoesNotRoute() throws {
        let intent = CompleteTaskIntent(/* configured fixture */)
        XCTAssertNil(SceneDelegate.routeForTesting(intent))
    }
}
```

Expose a test-only pure mapping function rather than constructing a real `UIScene` for every routing test.

## Selected-SDK-dependent: UI-test reusable-cell annotations

Use the current availability reference and selected SDK declarations for this surface. Omit or source-gate unsupported APIs only when preserving a required older-SDK build lane; runtime gates alone cannot supply missing declarations.

```swift
func testCellReuseDoesNotExposeOldTask() async throws {
    let app = XCUIApplication()
    app.launchArguments = ["-SeedManyTasks", "YES"]
    app.launch()

    let firstID = seededTaskIDs.first!
    let lastID = seededTaskIDs.last!

    app.tables.cells.firstMatch.swipeUp(velocity: .fast)
    app.tables.cells.lastMatch.tap()

    let annotations = try await inspectAppEntityAnnotations(in: app)
    XCTAssertFalse(annotations.visibleEntityIDs.contains(firstID))
    XCTAssertTrue(annotations.visibleEntityIDs.contains(lastID))
}
```

Also test diffable reorder, filtering, multi-selection, privacy mode, and account switching.

## Cold-launch deduplication pattern

```swift
@MainActor
final class IntentRouteDeduplicator {
    struct Key: Hashable {
        let intentIdentifier: String
        let targetIdentifier: String?
    }

    private var recentlyHandled: [Key: ContinuousClock.Instant] = [:]
    private let clock = ContinuousClock()

    func shouldHandle(_ key: Key) -> Bool {
        let now = clock.now
        recentlyHandled = recentlyHandled.filter { _, timestamp in
            timestamp.duration(to: now) < .seconds(5)
        }

        guard recentlyHandled[key] == nil else { return false }
        recentlyHandled[key] = now
        return true
    }
}
```

Use a product-appropriate token and retention window. The point is to prevent the connection-options path and scene callback from pushing the same destination twice.

## UIKit implementation audit

For each controller that displays semantic content, record:

```text
Controller:
Primary entity/activity:
Child view annotations:
Table/collection annotation data source:
Selection source of truth:
Custom canvas provider:
Transfer/drag representations:
Incoming App Intent routes:
Privacy/redaction state:
Cell reuse reset:
UI tests:
```

For each scene, record:

```text
Scene role:
Account/workspace affinity:
Accepted App Intent content identifiers:
Coordinator route table:
Cold-launch behavior:
Editing/modal exclusion policy:
Restoration IDs:
Multiwindow tests:
```

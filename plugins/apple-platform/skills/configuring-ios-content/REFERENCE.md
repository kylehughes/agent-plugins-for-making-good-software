# Modern iOS Content Configuration Reference

This reference expands the skill entry point with complete Swift 6.3 templates for UIKit content configuration in iOS 16+ applications.

## Availability and scope

| API | Availability | Use in an iOS 16+ project |
| --- | --- | --- |
| `UIContentConfiguration` / `UIContentView` | iOS 14+ | Always available for this skill's baseline. |
| `UIListContentConfiguration` | iOS 14+ | Prefer for standard title/subtitle/image layouts. |
| `UIBackgroundConfiguration` | iOS 14+ | Prefer for state-aware cell backgrounds. |
| `UICollectionView.CellRegistration` / `UITableView.CellRegistration` | iOS 14+ | Prefer over string reuse identifiers for new code. |
| `configurationUpdateHandler` | iOS 15+ | Always available for the iOS 16 baseline. |
| `UICollectionViewDiffableDataSource.reconfigureItems(_:)` | iOS 15+ | Prefer for visible content updates that keep identity. |
| `UIHostingConfiguration` | iOS 16+ | Prefer for SwiftUI cell content. |
| `UIContentUnavailableConfiguration` | iOS 17+ | Gate with `#available(iOS 17.0, *)` if the app still supports iOS 16. |

When the deployment target is iOS 16, generated code should be clean Swift 6.3 with availability checks only for APIs above iOS 16. Do not add fallback branches for older systems unless the user asks.

## Architecture model

A content configuration is value-like data that describes what to render. A content view is a `UIView` that knows how to render that data. UIKit applies the configuration to a cell or view, asks the configuration for a content view when needed, and asks the configuration to update itself for state changes.

The flow is:

```text
model -> content configuration -> content view -> UIKit cell/view
                         ^
                         |
                 UIConfigurationState
```

Keep this separation strict. Configurations should not own UIKit view instances. Content views should not reach into data sources. Cells should not hand-edit content view subviews.

## Choosing the implementation

Use this order unless the user has a strong reason to do otherwise.

1. `UIListContentConfiguration` for Apple's built-in list-like layouts.
2. `UIHostingConfiguration` for SwiftUI-rendered cell bodies.
3. `UIContentUnavailableConfiguration` for empty/loading/search states on iOS 17+.
4. A custom `UIContentConfiguration`/`UIContentView` pair for custom reusable UIKit layouts.
5. A cell subclass only to provide custom cell state, lifecycle, cancellation, focus/drag/drop behavior, or non-content cell features.

## System list content configuration

Use `defaultContentConfiguration()` from the cell. It has context-specific defaults for the cell and list style.

```swift
@MainActor
private func configure(_ cell: UICollectionViewListCell, with item: Item, state: UICellConfigurationState) {
    var content = cell.defaultContentConfiguration().updated(for: state)
    content.text = item.title
    content.secondaryText = item.subtitle
    content.image = item.thumbnail

    content.textProperties.font = .preferredFont(forTextStyle: .body)
    content.textProperties.adjustsFontForContentSizeCategory = true
    content.textProperties.color = state.isDisabled ? .secondaryLabel : .label

    content.secondaryTextProperties.font = .preferredFont(forTextStyle: .subheadline)
    content.secondaryTextProperties.adjustsFontForContentSizeCategory = true
    content.secondaryTextProperties.color = .secondaryLabel

    content.imageProperties.maximumSize = CGSize(width: 40, height: 40)
    content.imageProperties.cornerRadius = 20

    cell.contentConfiguration = content

    var background = UIBackgroundConfiguration.listGroupedCell().updated(for: state)
    background.backgroundColor = state.isSelected ? .secondarySystemGroupedBackground : .systemGroupedBackground
    cell.backgroundConfiguration = background

    cell.accessories = item.isFavorite ? [.checkmark()] : []
}
```

Use a single helper that accepts the cell state, then call it from the update handler.

```swift
private lazy var itemRegistration = UICollectionView.CellRegistration<UICollectionViewListCell, Item.ID> { [weak self] cell, _, id in
    cell.configurationUpdateHandler = { [weak self] cell, state in
        guard let self,
              let cell = cell as? UICollectionViewListCell,
              let item = self.itemStore.item(for: id)
        else { return }

        self.configure(cell, with: item, state: state)
    }

    cell.setNeedsUpdateConfiguration()
}
```

Notes:

- Set `configurationUpdateHandler` once per registration invocation. It is replaced when the cell is reused for another item.
- Capture `id`, not `indexPath`.
- The handler should not call `setNeedsUpdateConfiguration()` on itself.
- If the model changes without changing identity, update the store and call `dataSource.reconfigureItems([id])`.

## UITableView registration variant

The same pattern works for table views.

```swift
private lazy var rowRegistration = UITableView.CellRegistration<UITableViewCell, Item.ID> { [weak self] cell, _, id in
    cell.configurationUpdateHandler = { [weak self] cell, state in
        guard let self, let item = self.itemStore.item(for: id) else { return }

        var content = cell.defaultContentConfiguration().updated(for: state)
        content.text = item.title
        content.secondaryText = item.subtitle
        content.image = item.thumbnail
        cell.contentConfiguration = content

        var background = UIBackgroundConfiguration.listGroupedCell().updated(for: state)
        background.backgroundColor = state.isHighlighted ? .secondarySystemGroupedBackground : .systemGroupedBackground
        cell.backgroundConfiguration = background
    }

    cell.setNeedsUpdateConfiguration()
}
```

## UIHostingConfiguration for SwiftUI cell content

Use `UIHostingConfiguration` when the cell body is easier as SwiftUI. Do not create a `UIHostingController` per cell on iOS 16+.

```swift
import SwiftUI
import UIKit

struct ItemRow: View {
    let item: Item
    let isSelected: Bool
    let isHighlighted: Bool
    let onDelete: () -> Void

    var body: some View {
        HStack(spacing: 12) {
            Image(systemName: item.symbolName)
                .imageScale(.large)
                .accessibilityHidden(true)

            VStack(alignment: .leading, spacing: 2) {
                Text(item.title)
                    .font(.body)
                    .foregroundStyle(.primary)
                if let subtitle = item.subtitle, !subtitle.isEmpty {
                    Text(subtitle)
                        .font(.subheadline)
                        .foregroundStyle(.secondary)
                }
            }

            Spacer(minLength: 8)
        }
        .opacity(isHighlighted ? 0.65 : 1.0)
        .fontWeight(isSelected ? .semibold : .regular)
        .contentShape(Rectangle())
        .swipeActions(edge: .trailing, allowsFullSwipe: false) {
            Button(role: .destructive, action: onDelete) {
                Label("Delete", systemImage: "trash")
            }
        }
    }
}
```

```swift
private func configureHostingCell(_ cell: UICollectionViewCell, id: Item.ID, state: UICellConfigurationState) {
    guard let item = itemStore.item(for: id) else { return }

    cell.contentConfiguration = UIHostingConfiguration {
        ItemRow(
            item: item,
            isSelected: state.isSelected,
            isHighlighted: state.isHighlighted
        ) { [weak self] in
            self?.deleteItem(withID: id)
        }
    }
    .margins(.vertical, 8)
    .margins(.horizontal, 16)

    var background = UIBackgroundConfiguration.listGroupedCell().updated(for: state)
    background.backgroundColor = state.isSelected ? .secondarySystemGroupedBackground : .systemGroupedBackground
    cell.backgroundConfiguration = background
}
```

```swift
let registration = UICollectionView.CellRegistration<UICollectionViewListCell, Item.ID> { [weak self] cell, _, id in
    cell.configurationUpdateHandler = { [weak self] cell, state in
        self?.configureHostingCell(cell, id: id, state: state)
    }

    cell.setNeedsUpdateConfiguration()
}
```

Guidance:

- Pass cell state into the SwiftUI view when the SwiftUI body should reflect selection/highlight/focus/disabled state.
- Use `.margins(_:_:)` to align hosted content with UIKit list geometry.
- Use `.background(_:)` on `UIHostingConfiguration` for hosted background content; use `cell.backgroundConfiguration` for UIKit cell background behavior.
- Keep durable state outside the SwiftUI row. Cell reuse and reconfiguration can recreate the SwiftUI view.
- Do not assume SwiftUI navigation environment exists inside a hosted cell. Route navigation through UIKit selection, delegate, coordinator, or an action closure.
- Be careful with interactive SwiftUI controls inside selectable cells. Define whether taps select the row, activate the control, or both.

## Custom UIContentConfiguration and UIContentView

Use a custom pair when you need reusable UIKit rendering that the list configuration or SwiftUI hosting configuration does not cover.

### Configuration

The configuration is plain data plus optional action closures. It does not have to be `Hashable` or `Equatable`.

```swift
import UIKit

struct UserRowContentConfiguration: UIContentConfiguration {
    var id: User.ID
    var title: String
    var subtitle: String?
    var image: UIImage?
    var imageIdentifier: AnyHashable?
    var onAccessoryTap: ((User.ID) -> Void)?

    fileprivate var isSelected = false
    fileprivate var isHighlighted = false
    fileprivate var isDisabled = false

    @MainActor
    func makeContentView() -> any UIView & UIContentView {
        UserRowContentView(configuration: self)
    }

    func updated(for state: any UIConfigurationState) -> Self {
        var updated = self

        if let state = state as? UICellConfigurationState {
            updated.isSelected = state.isSelected
            updated.isHighlighted = state.isHighlighted
            updated.isDisabled = state.isDisabled
        } else if let state = state as? UIViewConfigurationState {
            updated.isSelected = state.isSelected
            updated.isHighlighted = state.isHighlighted
            updated.isDisabled = state.isDisabled
        }

        return updated
    }
}
```

### Content view

The content view owns the subviews and renders whatever the configuration says. Build the hierarchy once. Apply data many times.

```swift
final class UserRowContentView: UIView, UIContentView {
    private let rootStack = UIStackView()
    private let textStack = UIStackView()
    private let imageView = UIImageView()
    private let titleLabel = UILabel()
    private let subtitleLabel = UILabel()
    private let accessoryButton = UIButton(type: .system)

    var configuration: any UIContentConfiguration {
        didSet {
            applyConfiguration()
        }
    }

    init(configuration: UserRowContentConfiguration) {
        self.configuration = configuration
        super.init(frame: .zero)
        setupViews()
        setupConstraints()
        applyConfiguration()
    }

    required init?(coder: NSCoder) {
        fatalError("init(coder:) has not been implemented")
    }

    func supports(_ configuration: any UIContentConfiguration) -> Bool {
        configuration is UserRowContentConfiguration
    }

    private func setupViews() {
        directionalLayoutMargins = NSDirectionalEdgeInsets(top: 10, leading: 16, bottom: 10, trailing: 16)
        preservesSuperviewLayoutMargins = true

        rootStack.axis = .horizontal
        rootStack.alignment = .center
        rootStack.spacing = 12

        textStack.axis = .vertical
        textStack.alignment = .fill
        textStack.spacing = 2

        imageView.contentMode = .scaleAspectFill
        imageView.clipsToBounds = true
        imageView.layer.cornerRadius = 20
        imageView.setContentHuggingPriority(.required, for: .horizontal)
        imageView.setContentCompressionResistancePriority(.required, for: .horizontal)

        titleLabel.font = .preferredFont(forTextStyle: .body)
        titleLabel.adjustsFontForContentSizeCategory = true
        titleLabel.numberOfLines = 0

        subtitleLabel.font = .preferredFont(forTextStyle: .subheadline)
        subtitleLabel.adjustsFontForContentSizeCategory = true
        subtitleLabel.textColor = .secondaryLabel
        subtitleLabel.numberOfLines = 0

        accessoryButton.setImage(UIImage(systemName: "ellipsis.circle"), for: .normal)
        accessoryButton.setContentHuggingPriority(.required, for: .horizontal)
        accessoryButton.addTarget(self, action: #selector(accessoryButtonTapped), for: .touchUpInside)

        addSubview(rootStack)
        rootStack.addArrangedSubview(imageView)
        rootStack.addArrangedSubview(textStack)
        rootStack.addArrangedSubview(accessoryButton)
        textStack.addArrangedSubview(titleLabel)
        textStack.addArrangedSubview(subtitleLabel)
    }

    private func setupConstraints() {
        rootStack.translatesAutoresizingMaskIntoConstraints = false
        imageView.translatesAutoresizingMaskIntoConstraints = false

        NSLayoutConstraint.activate([
            rootStack.leadingAnchor.constraint(equalTo: layoutMarginsGuide.leadingAnchor),
            rootStack.trailingAnchor.constraint(equalTo: layoutMarginsGuide.trailingAnchor),
            rootStack.topAnchor.constraint(equalTo: layoutMarginsGuide.topAnchor),
            rootStack.bottomAnchor.constraint(equalTo: layoutMarginsGuide.bottomAnchor),

            imageView.widthAnchor.constraint(equalToConstant: 40),
            imageView.heightAnchor.constraint(equalTo: imageView.widthAnchor)
        ])
    }

    private func applyConfiguration() {
        guard let configuration = configuration as? UserRowContentConfiguration else {
            assertionFailure("Expected UserRowContentConfiguration")
            return
        }

        titleLabel.text = configuration.title
        subtitleLabel.text = configuration.subtitle
        subtitleLabel.isHidden = configuration.subtitle?.isEmpty != false

        imageView.image = configuration.image
        imageView.isHidden = configuration.image == nil

        accessoryButton.isHidden = configuration.onAccessoryTap == nil
        accessoryButton.isEnabled = !configuration.isDisabled

        alpha = configuration.isDisabled ? 0.45 : 1.0
        backgroundColor = (configuration.isSelected || configuration.isHighlighted) ? .secondarySystemFill : .clear

        accessibilityLabel = [configuration.title, configuration.subtitle]
            .compactMap { $0 }
            .joined(separator: ", ")
    }

    @objc private func accessoryButtonTapped() {
        guard let configuration = configuration as? UserRowContentConfiguration else { return }
        configuration.onAccessoryTap?(configuration.id)
    }
}
```

Use it like this:

```swift
cell.configurationUpdateHandler = { [weak self] cell, state in
    guard let self, let item = self.itemStore.item(for: id) else { return }

    var configuration = UserRowContentConfiguration(
        id: id,
        title: item.title,
        subtitle: item.subtitle,
        image: item.thumbnail,
        imageIdentifier: item.thumbnailURL
    )

    configuration.onAccessoryTap = { [weak self] id in
        self?.showActions(for: id)
    }

    cell.contentConfiguration = configuration.updated(for: state)
}

cell.setNeedsUpdateConfiguration()
```

### Optional no-op optimization

Do not add equality until measurement shows it matters. Most content views are cheap to reapply. If you do add a no-op guard, compare a render key that includes every rendered field.

```swift
private struct UserRowRenderKey: Equatable {
    var id: User.ID
    var title: String
    var subtitle: String?
    var imageIdentifier: AnyHashable?
    var isSelected: Bool
    var isHighlighted: Bool
    var isDisabled: Bool
}

private var currentRenderKey: UserRowRenderKey?

private func applyConfiguration() {
    guard let configuration = configuration as? UserRowContentConfiguration else { return }

    let nextKey = UserRowRenderKey(
        id: configuration.id,
        title: configuration.title,
        subtitle: configuration.subtitle,
        imageIdentifier: configuration.imageIdentifier,
        isSelected: configuration.isSelected,
        isHighlighted: configuration.isHighlighted,
        isDisabled: configuration.isDisabled
    )

    guard nextKey != currentRenderKey else { return }
    currentRenderKey = nextKey

    // Apply all visual properties here.
}
```

Do not use `UIImage` equality as your only image identity if the image may be decoded, transformed, or replaced by cache. Prefer a model image ID, URL, asset name, or cache key.

## Custom configuration state keys

Use custom keys when app-specific state should participate in UIKit's configuration update cycle.

```swift
extension UIConfigurationStateCustomKey {
    static let isPinned = UIConfigurationStateCustomKey("com.example.user-row.isPinned")
}

extension UICellConfigurationState {
    var isPinned: Bool {
        get { self[.isPinned] as? Bool ?? false }
        set { self[.isPinned] = newValue }
    }
}
```

```swift
final class PinnedListCell: UICollectionViewListCell {
    var isPinned = false {
        didSet {
            guard oldValue != isPinned else { return }
            setNeedsUpdateConfiguration()
        }
    }

    override var configurationState: UICellConfigurationState {
        var state = super.configurationState
        state.isPinned = isPinned
        return state
    }
}
```

Then read it in the update handler or configuration:

```swift
cell.configurationUpdateHandler = { cell, state in
    var content = cell.defaultContentConfiguration().updated(for: state)
    content.text = item.title
    content.image = state.isPinned ? UIImage(systemName: "pin.fill") : nil
    cell.contentConfiguration = content
}
```

Use custom state for state that belongs to the cell's rendering. Do not use it as a general data transport mechanism.

## Content-unavailable states on iOS 17+

For iOS 17+, prefer `UIContentUnavailableConfiguration` over custom empty-state overlays. In an iOS 16+ app, gate it.

```swift
private enum ViewState {
    case loading
    case loaded([Item.ID])
    case empty
    case failed(String)
}

private var viewState: ViewState = .loading {
    didSet {
        if #available(iOS 17.0, *) {
            setNeedsUpdateContentUnavailableConfiguration()
        } else {
            updateLegacyEmptyStateView()
        }
    }
}

@available(iOS 17.0, *)
override func updateContentUnavailableConfiguration(using state: UIContentUnavailableConfigurationState) {
    switch viewState {
    case .loading:
        var configuration = UIContentUnavailableConfiguration.loading()
        configuration.text = "Loading"
        contentUnavailableConfiguration = configuration

    case .empty:
        var configuration = UIContentUnavailableConfiguration.empty()
        configuration.image = UIImage(systemName: "tray")
        configuration.text = "No Items"
        configuration.secondaryText = "New items will appear here."
        contentUnavailableConfiguration = configuration

    case .failed(let message):
        var configuration = UIContentUnavailableConfiguration.empty()
        configuration.image = UIImage(systemName: "exclamationmark.triangle")
        configuration.text = "Unable to Load"
        configuration.secondaryText = message
        configuration.button = .borderedProminent()
        configuration.button.title = "Retry"
        configuration.buttonProperties.primaryAction = UIAction { [weak self] _ in
            self?.reload()
        }
        contentUnavailableConfiguration = configuration

    case .loaded:
        contentUnavailableConfiguration = nil
    }
}
```

For iOS 16 fallback, keep a normal view-owned empty-state view and hide/show it from a single method. Do not duplicate business logic across two renderers; both should read the same `viewState`.

## Diffable data source integration

Use stable identifiers in snapshots. Keep full models in a store keyed by ID, or use lightweight `Hashable` item values whose equality represents identity and intentional reload behavior.

```swift
enum Section: Hashable {
    case main
}

private var dataSource: UICollectionViewDiffableDataSource<Section, Item.ID>!
private var itemStore: [Item.ID: Item] = [:]

@MainActor
private func apply(items: [Item], animatingDifferences: Bool) {
    itemStore = Dictionary(uniqueKeysWithValues: items.map { ($0.id, $0) })

    var snapshot = NSDiffableDataSourceSnapshot<Section, Item.ID>()
    snapshot.appendSections([.main])
    snapshot.appendItems(items.map(\.id), toSection: .main)
    dataSource.apply(snapshot, animatingDifferences: animatingDifferences)
}

@MainActor
private func updateItem(_ item: Item) {
    itemStore[item.id] = item
    dataSource.reconfigureItems([item.id])
}
```

Use `reconfigureItems(_:)` for visual changes to the same item: title, subtitle, image, badge count, progress, favorite state, disabled state, and similar. Use snapshot moves/inserts/deletes when identity or ordering changes.

## Async image loading and reuse safety

Avoid starting network work from `updated(for:)`. For images, prefer a separate loader/cache keyed by model ID or URL, then reconfigure the item when the image is available.

```swift
@MainActor
private func loadThumbnail(for id: Item.ID, url: URL) {
    Task { [weak self] in
        guard let self else { return }

        do {
            let image = try await imageLoader.image(for: url)
            guard var item = self.itemStore[id], item.thumbnailURL == url else { return }
            item.thumbnail = image
            self.updateItem(item)
        } catch {
            // Keep the placeholder. Log or surface the error elsewhere if needed.
        }
    }
}
```

When a cell or content view itself owns a task, cancel it on reconfiguration, reuse, and deinit. Prefer model/store-driven image updates when possible; cell-owned tasks are easier to race.

## Background configurations

Use `UIBackgroundConfiguration` for cell backgrounds rather than setting `cell.backgroundColor` directly.

```swift
var background = UIBackgroundConfiguration.listPlainCell().updated(for: state)
background.cornerRadius = 12
background.backgroundInsets = NSDirectionalEdgeInsets(top: 4, leading: 12, bottom: 4, trailing: 12)
background.backgroundColor = switch (state.isSelected, state.isHighlighted) {
case (true, _): .tertiarySystemFill
case (_, true): .secondarySystemFill
default: .clear
}
cell.backgroundConfiguration = background
```

Keep background state logic together with content state logic. If the content changes on selection, the background probably belongs in the same update path.

## Accessories and actions

Prefer cell accessories for standard trailing UI.

```swift
cell.accessories = [
    .disclosureIndicator(displayed: .always)
]
```

For custom accessory actions, prefer `UICellAccessory.CustomViewConfiguration` or a button inside a custom content view. Capture an item ID, not the index path.

```swift
configuration.onAccessoryTap = { [weak self] id in
    self?.presentMenu(for: id)
}
```

If an action truly needs the current index path, query it at action time.

```swift
configuration.onAccessoryTap = { [weak self, weak cell] _ in
    guard let self,
          let cell,
          let indexPath = self.collectionView.indexPath(for: cell)
    else { return }

    self.presentMenu(at: indexPath)
}
```

Use this sparingly. Stable IDs are usually safer.

## Migration from legacy cells

Legacy code:

```swift
cell.textLabel?.text = item.title
cell.detailTextLabel?.text = item.subtitle
cell.imageView?.image = item.image
```

Modern replacement:

```swift
var content = cell.defaultContentConfiguration()
content.text = item.title
content.secondaryText = item.subtitle
content.image = item.image
cell.contentConfiguration = content
```

Do not leave both systems active in the same cell. Remove assumptions that labels exist as subviews. In modern configuration code, the content view is implementation detail.

## Testing and review checklist

Check all generated or modified code against this list.

- Configuration is assigned back to the cell.
- State updates are handled by `configurationUpdateHandler`, `updateConfiguration(using:)`, or `updated(for:)`, not ad hoc `isSelected` observers.
- No `setNeedsUpdateConfiguration()` call appears inside an update callback, `layoutSubviews`, or apply method.
- No constraints are activated repeatedly during configuration updates.
- No stale index path is captured in a long-lived closure.
- No closure stored in a configuration captures the owner strongly.
- Equality/hash logic, if present, includes all rendered fields and excludes closures.
- Diffable item identifiers are stable IDs, not mutable content configurations.
- iOS 17+ APIs are gated when supporting iOS 16.
- SwiftUI cell state is model-driven or passed in from `UICellConfigurationState`; durable state is not stored in cell-local `@State`.
- Dynamic Type, multiline text, semantic colors, layout margins, and accessibility labels are handled.
- Async work is cancellable or model/store-driven, and visible cells are reconfigured by ID when results arrive.

## Sources

- [Apple Developer Documentation: `UIContentConfiguration`](https://developer.apple.com/documentation/uikit/uicontentconfiguration-9eib5)
- [Apple Developer Documentation: `UIContentView`](https://developer.apple.com/documentation/uikit/uicontentview-5fh3z)
- [Apple Developer Documentation: `UIConfigurationState`](https://developer.apple.com/documentation/uikit/uiconfigurationstate-1smq1)
- [Apple Developer Documentation: `UIViewConfigurationState`](https://developer.apple.com/documentation/uikit/uiviewconfigurationstate-swift.struct)
- [Apple Developer Documentation: `UICellConfigurationState`](https://developer.apple.com/documentation/uikit/uicellconfigurationstate-swift.struct)
- [Apple Developer Documentation: `UIConfigurationStateCustomKey`](https://developer.apple.com/documentation/uikit/uiconfigurationstatecustomkey)
- [Apple Developer Documentation: `UIListContentConfiguration`](https://developer.apple.com/documentation/uikit/uilistcontentconfiguration-swift.struct)
- [Apple Developer Documentation: `UIBackgroundConfiguration`](https://developer.apple.com/documentation/uikit/uibackgroundconfiguration-swift.struct)
- [Apple Developer Documentation: `UICollectionView.CellRegistration`](https://developer.apple.com/documentation/uikit/uicollectionview/cellregistration)
- [Apple Developer Documentation: `UITableView.CellRegistration`](https://developer.apple.com/documentation/uikit/uitableview/cellregistration)
- [Apple Developer Documentation: `UIHostingConfiguration`](https://developer.apple.com/documentation/swiftui/uihostingconfiguration)
- [Apple Developer Documentation: `UIHostingConfiguration.margins(_:_:)`](https://developer.apple.com/documentation/swiftui/uihostingconfiguration/margins%28_%3A_%3A%29-7ptqj)
- [Apple Developer Documentation: `UIHostingConfiguration.background(_:)`](https://developer.apple.com/documentation/swiftui/uihostingconfiguration/background%28_%3A%29)
- [Apple Developer Documentation: `UIContentUnavailableConfiguration`](https://developer.apple.com/documentation/uikit/uicontentunavailableconfiguration-swift.struct)
- [Apple Developer Documentation: `UIViewController.contentUnavailableConfiguration`](https://developer.apple.com/documentation/uikit/uiviewcontroller/contentunavailableconfiguration-4b95e)
- [Apple Developer Documentation: `UIViewController.updateContentUnavailableConfiguration(using:)`](https://developer.apple.com/documentation/uikit/uiviewcontroller/updatecontentunavailableconfiguration%28using%3A%29)
- [Apple Developer Documentation: `UIViewController.setNeedsUpdateContentUnavailableConfiguration()`](https://developer.apple.com/documentation/uikit/uiviewcontroller/setneedsupdatecontentunavailableconfiguration%28%29)
- [Swift.org: Swift 6.3 release notes](https://www.swift.org/blog/swift-6.3-released/)

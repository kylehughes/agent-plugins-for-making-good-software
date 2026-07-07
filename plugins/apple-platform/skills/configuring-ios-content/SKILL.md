---
name: configuring-ios-content
description: Implement modern UIKit content configuration for iOS projects. Use when configuring UITableViewCell or UICollectionViewCell content, UICollectionView.CellRegistration, UITableView.CellRegistration, UIListContentConfiguration, UIBackgroundConfiguration, UIHostingConfiguration, UIContentUnavailableConfiguration, custom UIContentConfiguration/UIContentView pairs, cell state updates, diffable-data-source reconfiguration, or migration away from legacy cell.textLabel/imageView/detailTextLabel code.
---

# Configuring iOS Content

Use this skill for modern cell and content-view configuration in UIKit projects. The default project shape is Swift 6.3, UIKit/SwiftUI on the main actor, and an iOS deployment target of 16 or newer spanning current and beta iOS releases. Do not include Swift 5 compatibility branches or iOS 13-15 fallback code unless the user explicitly asks.

## Baseline assumptions

- Minimum deployment target: iOS 16 unless the user states otherwise.
- Use `UIHostingConfiguration` freely for cell content because it is iOS 16+.
- Gate iOS 17+ APIs, especially `UIContentUnavailableConfiguration`, with `#available(iOS 17.0, *)` when the target remains iOS 16.
- For iOS 26/27-beta-specific APIs, do not invent availability or behavior. Use stable APIs unless the user provides beta docs or asks for a beta-only implementation.
- Treat UIKit code as main-actor UI code. Do not update cells, configurations, snapshots, or views from background tasks.

## Decision order

1. **Simple title/subtitle/image/accessories**: use `cell.defaultContentConfiguration()` or `UIListContentConfiguration`, plus `UIBackgroundConfiguration` and `UICellAccessory`.
2. **SwiftUI cell body on iOS 16+**: use `UIHostingConfiguration`, especially when the content is easier to express as SwiftUI.
3. **Empty/loading/search unavailable states**: use `UIContentUnavailableConfiguration` on iOS 17+, with an iOS 16 fallback only when necessary.
4. **Reusable custom UIKit rendering**: implement a custom `UIContentConfiguration` struct and a separate `UIView & UIContentView` class.
5. **Cell subclass**: use only for cell-specific lifecycle/state plumbing, such as `configurationState`, async task cancellation, `prepareForReuse`, focus/drag/drop behavior, or truly cell-owned views. Do not subclass cells just to set labels and images.

## Rules for generated code

- Always assign the finished configuration back to the cell: `cell.contentConfiguration = content`.
- Prefer `cell.defaultContentConfiguration()` over `UIListContentConfiguration.cell()` inside cells because the default is context-aware.
- Use `configurationUpdateHandler` or `updateConfiguration(using:)` for state-dependent content/background updates. Rebuild a fresh configuration in the handler.
- Start state-dependent system configurations with `.updated(for: state)` before applying custom overrides.
- Never call `setNeedsUpdateConfiguration()` from inside `configurationUpdateHandler`, `updateConfiguration(using:)`, `layoutSubviews`, or an `apply(configuration:)` method.
- Do not mix legacy `textLabel`, `detailTextLabel`, or `imageView` cell APIs with `contentConfiguration` for the same cell.
- Use stable model IDs in diffable data sources. Do not use configuration structs as item identifiers.
- Use `dataSource.reconfigureItems(_:)` for visible content changes that keep identity the same; use snapshot inserts/deletes/moves for identity changes.
- Do not capture `indexPath` in action closures. Capture a stable item ID, or query the current index path at action time.
- Closure properties stored in configurations must capture owners weakly and must not retain cells, view controllers, image loaders, tasks, or data sources strongly.
- `UIContentConfiguration` does **not** require `Hashable` or `Equatable`. Add equality only when there is a concrete reason.
- If a content view skips no-op updates by comparing configurations, the comparison must include every field that affects rendered output, including state-derived fields such as selected/highlighted/disabled, image identity, colors, fonts, accessories, and visibility. Otherwise, do not skip the update.
- Keep configurations lightweight. Do not perform networking, image decoding, formatting-heavy work, or database access in `updated(for:)` or `makeContentView()`.
- A content view must set up its subviews and constraints once in initialization, then apply new configuration values without recreating the hierarchy.
- Reset every output-affecting property in `apply`: text, attributed text, image, hidden flags, colors, fonts, alpha, background, accessibility, actions, and layout margins as relevant.
- Use Dynamic Type-friendly fonts, `adjustsFontForContentSizeCategory`, `numberOfLines = 0` where appropriate, directional margins, and semantic colors.
- When generating SwiftUI for `UIHostingConfiguration`, keep durable state in the model or observable object. Do not rely on cell-local `@State` to survive reuse or reconfiguration.
- Use `UIHostingController`, not `UIHostingConfiguration`, for arbitrary UIKit container views outside cell/content-configuration contexts.

## Standard patterns

### System list content

```swift
private func configure(_ cell: UICollectionViewListCell, with item: Item, state: UICellConfigurationState) {
    var content = cell.defaultContentConfiguration().updated(for: state)
    content.text = item.title
    content.secondaryText = item.subtitle
    content.image = item.symbolImage
    content.textProperties.font = .preferredFont(forTextStyle: .body)
    content.textProperties.adjustsFontForContentSizeCategory = true
    content.secondaryTextProperties.color = .secondaryLabel
    cell.contentConfiguration = content

    var background = UIBackgroundConfiguration.listGroupedCell().updated(for: state)
    background.backgroundColor = state.isSelected ? .secondarySystemGroupedBackground : .systemGroupedBackground
    cell.backgroundConfiguration = background
}
```

### Cell registration with state updates

```swift
let registration = UICollectionView.CellRegistration<UICollectionViewListCell, Item.ID> { [weak self] cell, _, id in
    cell.configurationUpdateHandler = { [weak self] cell, state in
        guard let self,
              let cell = cell as? UICollectionViewListCell,
              let item = self.item(for: id)
        else { return }

        self.configure(cell, with: item, state: state)
    }

    cell.setNeedsUpdateConfiguration()
}
```

### SwiftUI in a UIKit cell

```swift
cell.configurationUpdateHandler = { [weak self] cell, state in
    guard let self, let item = self.item(for: itemID) else { return }

    cell.contentConfiguration = UIHostingConfiguration {
        ItemRow(item: item, isSelected: state.isSelected, isHighlighted: state.isHighlighted) { [weak self] in
            self?.delete(itemID)
        }
    }
    .margins(.vertical, 8)
    .margins(.horizontal, 16)
}
```

### Custom configuration split

```swift
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

## Critical pitfalls

- Excluding state-derived appearance from equality causes selected/highlighted/disabled updates to be skipped.
- Capturing old index paths causes actions to hit the wrong item after inserts, deletes, moves, or filtering.
- Doing async image work in a configuration causes reuse races. Put async work in a loader/cache and update the model/snapshot, or cancel work in a cell/content view.
- Rebuilding constraints in `apply` or `layoutSubviews` creates duplicate constraints and layout churn.
- Calling `setNeedsUpdateConfiguration()` from an update callback creates loops.
- Storing heavyweight reference objects in configurations makes reuse, equality, and memory behavior harder to reason about.

For complete templates, custom state keys, content-unavailable examples, diffable-data-source guidance, and review checklists, read `REFERENCE.md`.

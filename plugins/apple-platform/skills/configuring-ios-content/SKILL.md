---
name: configuring-ios-content
description: Implement UIContentConfiguration, UIHostingConfiguration, and UIContentView for modern UIKit cell and view architecture. Use when configuring collection view cells, table view cells, cell registration, content views, diffable data sources, replacing legacy cell.textLabel code, embedding SwiftUI views in UIKit cells, or building custom content configurations.
---

# Configuring iOS Content

UIContentConfiguration (iOS 14+) and UIHostingConfiguration (iOS 16+) replace legacy UIKit view configuration with a declarative, state-driven architecture. Configurations are lightweight value types that describe *what* to display; content views handle *how* to display it.

## Rules

1.  **Prefer Composition**: Use `UIContentConfiguration` over subclassing `UITableViewCell` or `UICollectionViewCell` for standard layouts. Composition makes cells reusable and testable without inheritance hierarchies.
2.  **Use Value Types**: Define configurations as `struct`s conforming to `UIContentConfiguration` and `Hashable`. Value semantics enable safe copy-on-write mutation in `updated(for:)`.
3.  **Separate Setup from Updates**: Content views should perform one-time view hierarchy setup in `init` and apply configuration changes in a dedicated `apply(configuration:)` method. This prevents redundant view creation on every update.
4.  **Handle State**: Implement `updated(for state:)` to return modified configurations based on `UICellConfigurationState` (selected, highlighted, disabled, etc.).
5.  **SwiftUI Integration**: For iOS 16+, prefer `UIHostingConfiguration` to embed SwiftUI views directly in cells. It handles sizing, margins, and lifecycle automatically.
6.  **Create Fresh Configurations**: Do not cache configuration objects. They are lightweight value types and UIKit expects fresh instances.
7.  **Diffable Data Sources**: Use `Item.ID` as the diffable item identifier, not the configuration struct. Configurations change on every state update, which would cause unnecessary diffing.
8.  **Memory Safety**: Use `[weak self]` in closures stored within configurations to prevent retain cycles between the cell and its configuration.

## Common Patterns

### Modern Cell Registration (iOS 14+)

```swift
let registration = UICollectionView.CellRegistration<UICollectionViewListCell, Item> { cell, indexPath, item in
    var content = cell.defaultContentConfiguration()
    content.text = item.title
    content.secondaryText = item.subtitle
    content.image = item.icon
    cell.contentConfiguration = content
}
```

### Configuration Update Handler (iOS 15+)

Rebuild the configuration each time the cell's state changes, so appearance stays in sync with selection, highlighting, and other states:

```swift
cell.configurationUpdateHandler = { cell, state in
    var content = cell.defaultContentConfiguration().updated(for: state)
    content.text = item.title

    if state.isSelected {
        content.textProperties.color = .systemRed
    }

    cell.contentConfiguration = content
}
```

### SwiftUI in UIKit Cells (iOS 16+)

```swift
cell.contentConfiguration = UIHostingConfiguration {
    HStack {
        Image(systemName: "star")
        VStack(alignment: .leading) {
            Text(item.title).font(.headline)
            Text(item.subtitle).foregroundStyle(.secondary)
        }
    }
}
```

### Custom Configuration Boilerplate

Use this pattern when creating a fully custom configuration:

```swift
struct CustomConfig: UIContentConfiguration, Hashable {
    var title: String?

    func makeContentView() -> UIView & UIContentView {
        return CustomContentView(configuration: self)
    }

    func updated(for state: UIConfigurationState) -> CustomConfig {
        var updated = self
        // Apply state-based changes here (e.g., adjust colors for selection)
        return updated
    }
}
```

## Critical Pitfalls

-   **Legacy Mixing**: `cell.textLabel` and `cell.contentConfiguration` are mutually exclusive. Using both produces undefined behavior.
-   **State Loops**: Calling `setNeedsUpdateConfiguration()` inside `layoutSubviews()` creates an infinite layout cycle.
-   **Stale IndexPaths**: In action closures, query `tableView.indexPath(for: cell)` at call time instead of capturing `indexPath` from the registration closure, because index paths change after insertions and deletions.

## Reference

For detailed implementation of custom content views, standalone usage outside cells, and advanced state handling, see [REFERENCE.md](REFERENCE.md).

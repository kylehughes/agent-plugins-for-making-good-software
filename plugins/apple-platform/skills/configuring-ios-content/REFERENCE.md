# UIContentConfiguration and UIContentView: The Modern UIKit Architecture

UIContentConfiguration represents a fundamental paradigm shift in iOS development introduced in iOS 14, replacing direct view manipulation with a **declarative, state-driven architecture** that separates data from presentation.

## Overview

- **Configurations** are lightweight value types (structs) that describe **what** to display.
- **Content views** are reference types (classes) that handle **how** to display it.
- **UIKit** handles the orchestration, state updates, and performance optimizations.

Key benefits:
- Eliminates entire classes of state management bugs.
- Provides automatic performance optimizations.
- Enables composition over inheritance.
- iOS 16+ `UIHostingConfiguration` brings revolutionary SwiftUI integration.

## Architecture Fundamentals

The architecture separates configuration from view implementation.

### The Protocol Contract

The `UIContentConfiguration` protocol requires just two methods:
1. `makeContentView()`: Creates a new `UIView` instance conforming to `UIContentView`.
2. `updated(for state:)`: Returns a new configuration adjusted for a given state (selected, highlighted, disabled).

`UIContentView` requires only a `configuration` property. When this property changes, the view updates its appearance.

**Unidirectional Data Flow**: Configuration → View.

### Type Relationships

- `UIConfigurationState`: All inputs determining how a view should appear.
- `UIViewConfigurationState`: Base properties like `isDisabled`, `isHighlighted`, `isSelected`, `isFocused`.
- `UICellConfigurationState`: Extends this with cell-specific states: `isEditing`, `isExpanded`, `isSwiped`.

## Implementation Patterns

### Custom Configuration Pattern

Your configuration struct must conform to both `UIContentConfiguration` and `Hashable`.

```swift
struct CustomContentConfiguration: UIContentConfiguration, Hashable {

    // Data properties - the actual content
    var title: String?
    var subtitle: String?
    var image: UIImage?
    
    // Styling properties - appearance customization
    var titleColor: UIColor?
    var titleFont: UIFont = .preferredFont(forTextStyle: .body)
    var backgroundColor: UIColor?
    
    // State reference for access in content view if needed
    private(set) var state: UICellConfigurationState?
    
    func makeContentView() -> UIView & UIContentView {
        return CustomContentView(configuration: self)
    }
    
    func updated(for state: UIConfigurationState) -> CustomContentConfiguration {
        guard let cellState = state as? UICellConfigurationState else {
            return self
        }
        
        var updatedConfig = self
        updatedConfig.state = cellState
        
        // Apply state-based styling using copy-on-write
        if cellState.isSelected || cellState.isHighlighted {
            updatedConfig.titleColor = .white
            updatedConfig.backgroundColor = .systemBlue
        } else {
            updatedConfig.titleColor = .label
            updatedConfig.backgroundColor = .systemBackground
        }
        
        if cellState.isDisabled {
            updatedConfig.titleColor = .secondaryLabel
        }
        
        return updatedConfig
    }
    
    // Only hash identity properties, not state or derived styling
    func hash(into hasher: inout Hasher) {
        hasher.combine(title)
        hasher.combine(subtitle)
    }
    
    static func == (lhs: Self, rhs: Self) -> Bool {
        return lhs.title == rhs.title && 
               lhs.subtitle == rhs.subtitle &&
               lhs.image == rhs.image
    }
}
```

### Custom Content View Pattern

Critically separate one-time view setup from configuration application.

```swift
class CustomContentView: UIView, UIContentView {
    private let titleLabel = UILabel()
    private let subtitleLabel = UILabel()
    private let stackView = UIStackView()
    
    var configuration: UIContentConfiguration {
        didSet {
            // Guard against no-op updates for performance
            guard let newConfig = configuration as? CustomContentConfiguration,
                  newConfig != oldValue as? CustomContentConfiguration else {
                return
            }
            apply(configuration: newConfig)
        }
    }
    
    init(configuration: CustomContentConfiguration) {
        self.configuration = configuration
        super.init(frame: .zero)
        
        setupViewHierarchy()
        setupConstraints()
        apply(configuration: configuration) // Apply initial configuration
    }
    
    required init?(coder: NSCoder) {
        fatalError("init(coder:) has not been implemented")
    }
    
    private func setupViewHierarchy() {
        stackView.axis = .vertical
        stackView.spacing = 8
        
        addSubview(stackView)
        stackView.addArrangedSubview(titleLabel)
        stackView.addArrangedSubview(subtitleLabel)
        
        titleLabel.numberOfLines = 0
        subtitleLabel.numberOfLines = 0
    }
    
    private func setupConstraints() {
        stackView.translatesAutoresizingMaskIntoConstraints = false
        NSLayoutConstraint.activate([
            stackView.leadingAnchor.constraint(equalTo: layoutMarginsGuide.leadingAnchor),
            stackView.trailingAnchor.constraint(equalTo: layoutMarginsGuide.trailingAnchor),
            stackView.topAnchor.constraint(equalTo: layoutMarginsGuide.topAnchor),
            stackView.bottomAnchor.constraint(equalTo: layoutMarginsGuide.bottomAnchor)
        ])
    }
    
    private func apply(configuration: CustomContentConfiguration) {
        titleLabel.text = configuration.title
        subtitleLabel.text = configuration.subtitle
        
        if let titleColor = configuration.titleColor {
            titleLabel.textColor = titleColor
        }
        titleLabel.font = configuration.titleFont
        
        if let bgColor = configuration.backgroundColor {
            backgroundColor = bgColor
        }
        
        subtitleLabel.isHidden = configuration.subtitle == nil
    }
}
```

## Advanced Patterns

### Configuration Composition

Use system configurations as building blocks.

```swift
extension UIListContentConfiguration {
    static func customCell() -> UIListContentConfiguration {
        var config = UIListContentConfiguration.cell()
        config.textProperties.font = .preferredFont(forTextStyle: .headline)
        config.textProperties.color = .label
        config.imageProperties.maximumSize = CGSize(width: 40, height: 40)
        config.imageProperties.cornerRadius = 20
        return config
    }
}
```

### Layout Guides

`UIListContentView` exposes `textLayoutGuide`, `secondaryTextLayoutGuide`, and `imageLayoutGuide`.

```swift
let checkmark = UIImageView(image: UIImage(systemName: "checkmark"))
contentView.addSubview(checkmark)

checkmark.translatesAutoresizingMaskIntoConstraints = false
if let textGuide = contentView.textLayoutGuide {
    NSLayoutConstraint.activate([
        checkmark.leadingAnchor.constraint(equalTo: textGuide.trailingAnchor, constant: 8),
        checkmark.centerYAnchor.constraint(equalTo: textGuide.centerYAnchor)
    ])
}
```

### Custom State Properties

Use `UIConfigurationStateCustomKey` for type-safe custom state.

```swift
extension UIConfigurationStateCustomKey {
    static let isPinned = UIConfigurationStateCustomKey("com.myapp.isPinned")
    static let priority = UIConfigurationStateCustomKey("com.myapp.priority")
}

extension UICellConfigurationState {
    var isPinned: Bool {
        get { self[.isPinned] as? Bool ?? false }
        set { self[.isPinned] = newValue }
    }
    
    var taskPriority: Int {
        get { self[.priority] as? Int ?? 0 }
        set { self[.priority] = newValue }
    }
}

// In your cell
override var configurationState: UICellConfigurationState {
    var state = super.configurationState
    state.isPinned = item?.isPinned ?? false
    state.taskPriority = item?.priority.rawValue ?? 0
    return state
}
```

## Standalone Usage (Not Just Cells)

`UIContentConfiguration` works with any `UIView`.

### Lists Without UITableView

Use `UIStackView` with `UIListContentView`.

```swift
let stackView = UIStackView()
stackView.axis = .vertical
stackView.spacing = 0

for item in items {
    var config = UIListContentConfiguration.valueCell()
    config.text = item.name
    config.secondaryText = item.value
    config.image = item.icon
    
    let contentView = UIListContentView(configuration: config)
    stackView.addArrangedSubview(contentView)
}
```

### Custom Controls

Example of a switch control using the configuration pattern:

```swift
struct SwitchContentConfiguration: UIContentConfiguration, Hashable {
    var isOn = false
    var onToggle: ((Bool, UIView) -> Void)?

    func makeContentView() -> UIView & UIContentView {
        return SwitchContentView(configuration: self)
    }

    func updated(for state: UIConfigurationState) -> SwitchContentConfiguration {
        return self
    }

    // Closures cannot participate in Hashable; hash only the data properties.
    func hash(into hasher: inout Hasher) {
        hasher.combine(isOn)
    }

    static func == (lhs: Self, rhs: Self) -> Bool {
        lhs.isOn == rhs.isOn
    }
}

class SwitchContentView: UIView, UIContentView {
    var configuration: UIContentConfiguration {
        didSet { updateSwitch() }
    }
    
    private let switchControl = UISwitch()
    
    init(configuration: UIContentConfiguration) {
        self.configuration = configuration
        super.init(frame: .zero)
        
        addSubview(switchControl)
        switchControl.translatesAutoresizingMaskIntoConstraints = false
        NSLayoutConstraint.activate([
            switchControl.centerXAnchor.constraint(equalTo: centerXAnchor),
            switchControl.centerYAnchor.constraint(equalTo: centerYAnchor)
        ])
        
        switchControl.addAction(UIAction { [unowned self] _ in
            if let config = self.configuration as? SwitchContentConfiguration {
                config.onToggle?(self.switchControl.isOn, self)
            }
        }, for: .valueChanged)
        
        updateSwitch()
    }
    
    required init?(coder: NSCoder) {
        fatalError("init(coder:) has not been implemented")
    }
    
    private func updateSwitch() {
        guard let config = configuration as? SwitchContentConfiguration else { return }
        switchControl.isOn = config.isOn
    }
}
```

### View Controller Integration

```swift
class DetailViewController: UIViewController {
    private var contentView: UIListContentView!
    
    override func viewDidLoad() {
        super.viewDidLoad()
        
        var config = UIListContentConfiguration.valueCell()
        config.text = "Property Name"
        config.secondaryText = "Property Value"
        config.image = UIImage(systemName: "info.circle")
        
        contentView = UIListContentView(configuration: config)
        view.addSubview(contentView)
        
        contentView.translatesAutoresizingMaskIntoConstraints = false
        NSLayoutConstraint.activate([
            contentView.topAnchor.constraint(equalTo: view.safeAreaLayoutGuide.topAnchor),
            contentView.leadingAnchor.constraint(equalTo: view.leadingAnchor),
            contentView.trailingAnchor.constraint(equalTo: view.trailingAnchor)
        ])
    }
}
```

## Modern Collection and Table View Integration

### Type-Safe Cell Registration

```swift
let cellRegistration = UICollectionView.CellRegistration<UICollectionViewListCell, Item> { 
    cell, indexPath, item in
    
    var content = cell.defaultContentConfiguration()
    content.image = item.icon
    content.text = item.title
    content.secondaryText = item.subtitle
    cell.contentConfiguration = content
    
    var background = UIBackgroundConfiguration.listGroupedCell()
    cell.backgroundConfiguration = background
}

// Dequeue with direct item access
return collectionView.dequeueConfiguredReusableCell(
    using: cellRegistration,
    for: indexPath,
    item: item
)
```

### Configuration Update Handlers (iOS 15+)

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

## iOS 16: UIHostingConfiguration

Enable direct SwiftUI view usage in `UITableViewCell` and `UICollectionViewCell`.

### Basic Usage

```swift
cell.contentConfiguration = UIHostingConfiguration {
    VStack(alignment: .leading, spacing: 4) {
        Text(item.title)
            .font(.headline)
        Text(item.subtitle)
            .font(.caption)
            .foregroundStyle(.secondary)
        HStack {
            ForEach(item.tags, id: \.self) { tag in
                Text(tag)
                    .font(.caption2)
                    .padding(.horizontal, 8)
                    .padding(.vertical, 4)
                    .background(.blue.opacity(0.2))
                    .cornerRadius(8)
            }
        }
    }
    .padding(.vertical, 8)
}
```

### SwiftUI Swipe Actions

```swift
cell.contentConfiguration = UIHostingConfiguration {
    ItemView(item: item)
        .swipeActions(edge: .trailing) {
            Button(role: .destructive) {
                deleteItem(item)
            } label: {
                Label("Delete", systemImage: "trash")
            }
        }
}
```

### Data Flow

Changes to `@Published` properties automatically refresh SwiftUI content.

```swift
class ItemViewModel: ObservableObject {
    @Published var item: Item
    
    func toggleFavorite() {
        item.isFavorite.toggle()
        // SwiftUI view automatically updates
    }
}

cell.contentConfiguration = UIHostingConfiguration {
    ItemView(viewModel: viewModel)
}
```

## Performance Optimization

- **Create fresh configurations**: Never cache configurations. They are lightweight value types.
- **View Recycling**: Handled automatically by UIKit.
- **Diffable Data Sources**: Use IDs as items, not configurations.
- **Memory Management**: Always use `[weak self]` in closure-based configuration properties.

```swift
// ❌ Wrong - captures indexPath
config.onTap = {
    handleTap(at: indexPath) // May be wrong after moves
}

// ✓ Correct - queries current position
config.onTap = { [weak self] in
    guard let indexPath = self?.tableView.indexPath(for: cell) else { return }
    self?.handleTap(at: indexPath)
}
```

## Common Pitfalls

1. **Mixing APIs**: Don't mix configurations with legacy properties (`cell.textLabel` vs `cell.contentConfiguration`).
2. **Forgetting Application**: Remember to assign the configuration back to the cell (`cell.contentConfiguration = content`).
3. **Infinite Loops**: Never call `setNeedsUpdateConfiguration()` inside `layoutSubviews`.
4. **Retain Cycles**: Watch out for strong self captures in closures stored in configurations.

## SwiftUI Interoperability

### UIViewRepresentable

```swift
struct CustomContentViewWrapper: UIViewRepresentable {
    let config: CustomContentConfiguration
    
    func makeUIView(context: Context) -> CustomContentView {
        config.makeContentView() as! CustomContentView
    }
    
    func updateUIView(_ uiView: CustomContentView, context: Context) {
        uiView.configuration = config
    }
}
```

### Hybrid Architecture

- **UIKit**: For complex table structure, editing, custom interactions, large lists (1000+ items).
- **UIHostingConfiguration**: For rapid UI development, moderate list sizes.
- **Pure SwiftUI**: For greenfield projects, no UIKit dependencies.

## Sources

- [UIContentConfiguration — Apple Developer Documentation](https://developer.apple.com/documentation/uikit/uicontentconfiguration)
- [UIHostingConfiguration — Apple Developer Documentation](https://developer.apple.com/documentation/swiftui/uihostingconfiguration)
- [UIContentView — Apple Developer Documentation](https://developer.apple.com/documentation/uikit/uicontentview)
- [UICollectionView.CellRegistration — Apple Developer Documentation](https://developer.apple.com/documentation/uikit/uicollectionview/cellregistration)
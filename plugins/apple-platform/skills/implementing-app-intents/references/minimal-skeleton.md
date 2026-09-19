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

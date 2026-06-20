public protocol AccessibilityElement:
    RawRepresentable,
    CaseIterable,
    Equatable,
    Hashable,
    Sendable
where RawValue == String {}

public protocol AccessibilityInstrumented {
    associatedtype AccessibilityUIElement: AccessibilityElement

    static var accessibilityIdentifierScope: AccessibilityIdentifierScope { get }
    static func accessibilityIdentifier(
        for element: AccessibilityUIElement
    ) -> AccessibilityIdentifier
}

public extension AccessibilityInstrumented {
    static func accessibilityIdentifier(
        for element: AccessibilityUIElement
    ) -> AccessibilityIdentifier {
        AccessibilityIdentifier(
            scope: accessibilityIdentifierScope,
            element: element.rawValue
        )
    }

    static var accessibilityIdentifiers: AccessibilityIdentifierNamespace<Self> {
        AccessibilityIdentifierNamespace()
    }

    static var allAccessibilityIdentifiers: [AccessibilityIdentifier] {
        AccessibilityUIElement.allCases.map {
            accessibilityIdentifier(for: $0)
        }
    }
}

public struct AccessibilityIdentifierNamespace<Owner: AccessibilityInstrumented>:
    Sendable
{
    public init() {}

    public subscript(
        _ element: Owner.AccessibilityUIElement
    ) -> AccessibilityIdentifier {
        Owner.accessibilityIdentifier(for: element)
    }

    public func callAsFunction(
        _ element: Owner.AccessibilityUIElement
    ) -> AccessibilityIdentifier {
        Owner.accessibilityIdentifier(for: element)
    }

    public var all: [AccessibilityIdentifier] {
        Owner.allAccessibilityIdentifiers
    }
}

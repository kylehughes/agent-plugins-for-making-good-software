public struct AccessibilityIdentifierScope:
    Codable,
    Equatable,
    Hashable,
    Sendable,
    RawRepresentable,
    CustomStringConvertible
{
    public let rawValue: String

    public var description: String { rawValue }

    public init(rawValue: String) {
        precondition(
            !rawValue.isEmpty,
            "Accessibility scope must not be empty."
        )
        precondition(
            rawValue.count <= 80,
            "Accessibility scope is too long: \(rawValue)"
        )
        precondition(
            rawValue.unicodeScalars.allSatisfy(Self.isAllowedScalar),
            "Invalid accessibility scope: \(rawValue)"
        )

        self.rawValue = rawValue
    }

    public init(_ rawValue: String) {
        self.init(rawValue: rawValue)
    }

    private static func isAllowedScalar(_ scalar: Unicode.Scalar) -> Bool {
        switch scalar.value {
        case 48...57,  // 0-9
             65...90,  // A-Z
             95,       // _
             97...122: // a-z
            return true
        default:
            return false
        }
    }
}

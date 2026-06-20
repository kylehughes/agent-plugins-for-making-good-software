public struct AccessibilityIdentifier:
    Codable,
    Equatable,
    Hashable,
    Sendable,
    Identifiable,
    RawRepresentable,
    CustomStringConvertible
{
    public typealias RawValue = String

    public let rawValue: String

    public var value: String { rawValue }
    public var id: String { rawValue }
    public var description: String { rawValue }

    public init(rawValue: String) {
        precondition(
            Self.isValid(rawValue),
            "Invalid accessibility identifier: \(rawValue)"
        )
        self.rawValue = rawValue
    }

    @available(
        *,
        deprecated,
        message: "Use a screen-scoped identifier factory."
    )
    public init(_ rawValue: String) {
        self.init(rawValue: rawValue)
    }

    public init(
        scope: AccessibilityIdentifierScope,
        element: String,
        components: [AccessibilityIdentifierComponent] = []
    ) {
        var parts = [scope.rawValue, element]
        parts.append(contentsOf: components.map(\.rawValue))
        self.init(rawValue: parts.joined(separator: "_"))
    }

    public init(from decoder: Decoder) throws {
        let container = try decoder.singleValueContainer()
        let rawValue = try container.decode(String.self)

        guard Self.isValid(rawValue) else {
            throw DecodingError.dataCorruptedError(
                in: container,
                debugDescription: "Invalid accessibility identifier: \(rawValue)"
            )
        }

        self.rawValue = rawValue
    }

    public func encode(to encoder: Encoder) throws {
        var container = encoder.singleValueContainer()
        try container.encode(rawValue)
    }

    public static func isValid(_ value: String) -> Bool {
        guard !value.isEmpty else { return false }
        guard value.count <= 180 else { return false }
        guard !value.hasPrefix("_") else { return false }
        guard !value.hasSuffix("_") else { return false }
        guard !value.contains("__") else { return false }
        return value.unicodeScalars.allSatisfy(isAllowedScalar)
    }

    private static func isAllowedScalar(_ scalar: Unicode.Scalar) -> Bool {
        switch scalar.value {
        case 45,       // -
             46,       // .
             48...57,  // 0-9
             58,       // :
             65...90,  // A-Z
             95,       // _
             97...122: // a-z
            return true
        default:
            return false
        }
    }
}

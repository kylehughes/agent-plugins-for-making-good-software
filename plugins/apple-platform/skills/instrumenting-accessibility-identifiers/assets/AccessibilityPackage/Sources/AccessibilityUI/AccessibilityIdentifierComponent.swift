public struct AccessibilityIdentifierComponent:
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
        let sanitized = rawValue.unicodeScalars
            .map(Self.sanitizedScalar)
            .joined()

        precondition(
            !sanitized.isEmpty,
            "Identifier component must not be empty."
        )
        precondition(
            sanitized.count <= 80,
            "Identifier component is too long: \(sanitized)"
        )

        self.rawValue = sanitized
    }

    public init(_ value: some CustomStringConvertible) {
        self.init(rawValue: value.description)
    }

    public init(from decoder: Decoder) throws {
        let container = try decoder.singleValueContainer()
        let rawValue = try container.decode(String.self)
        let sanitized = rawValue.unicodeScalars.map(Self.sanitizedScalar).joined()

        guard !sanitized.isEmpty && sanitized.count <= 80 else {
            throw DecodingError.dataCorruptedError(
                in: container,
                debugDescription: "Invalid accessibility identifier component."
            )
        }

        self.rawValue = sanitized
    }

    private static func sanitizedScalar(_ scalar: Unicode.Scalar) -> String {
        switch scalar.value {
        case 45,       // -
             46,       // .
             48...57,  // 0-9
             65...90,  // A-Z
             97...122: // a-z
            return String(scalar)
        default:
            return "-"
        }
    }
}

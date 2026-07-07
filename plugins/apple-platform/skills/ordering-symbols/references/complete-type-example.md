# Complete Type Example

This reference shows a full type applying every ordering rule together, with notes on the non-obvious placements.

## Complete Type Example

```swift
struct UserViewModel {
    typealias Identifier = UUID

    enum Mode {
        case compact
        case expanded
    }

    static let defaultName = "Guest"
    static var registrationCount = 0

    public let id: Identifier

    let name: String

    private let apiClient: APIClient

    var email: String
    var isActive: Bool

    public init(id: Identifier, name: String, email: String, isActive: Bool, apiClient: APIClient) {
        self.id = id
        self.name = name
        self.apiClient = apiClient
        self.email = email
        self.isActive = isActive
    }

    init(name: String, apiClient: APIClient) {
        self.id = UUID()
        self.name = name
        self.apiClient = apiClient
        self.email = ""
        self.isActive = true
    }

    public var displayName: String {
        name.isEmpty ? Self.defaultName : name
    }

    public func refresh() async throws {
        try await load()
    }

    var isValid: Bool {
        !email.isEmpty && isActive
    }

    func activate() {
        isActive = true
    }

    func deactivate() {
        isActive = false
    }

    private lazy var cache = UserCache()

    private var hasCachedValue: Bool {
        cache.contains(id)
    }

    private func load() async throws {
        // ...
    }
}
```

Notes about the example:

- Stored properties use storage kind first, then access level.
- Implementation details use access level first, then lazy/computed/method kind.
- The `private lazy var cache` appears after internal methods because access level is primary inside implementation details.

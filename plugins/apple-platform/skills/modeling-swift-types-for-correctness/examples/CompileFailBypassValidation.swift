enum ValidationError: Error {
    case empty
}

struct NonEmptyString {
    private let storage: String

    init(_ raw: String) throws {
        guard !raw.isEmpty else { throw ValidationError.empty }
        storage = raw
    }

    private init(uncheckedStorage: String) {
        storage = uncheckedStorage
    }
}

func demonstrateBypassingValidation() {
    // expected-error: inaccessible due to 'private' protection level
    _ = NonEmptyString(uncheckedStorage: "")
}

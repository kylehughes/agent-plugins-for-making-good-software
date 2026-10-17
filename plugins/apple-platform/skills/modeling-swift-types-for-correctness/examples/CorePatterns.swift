import Foundation

// iOS 16-safe domain patterns compiled in the project's current Swift 6 language mode.
// Runtime availability, not legacy compiler support, determines this baseline.

enum LoadState<Value: Sendable, Failure: Error & Sendable>: Sendable {
    case idle
    case loading(previous: Value?)
    case loaded(Value)
    case failed(Failure, previous: Value?)

    var isLoading: Bool {
        if case .loading = self { true } else { false }
    }
}

enum NonEmptyStringError: Error, Equatable, Sendable {
    case empty
    case tooLong(maximum: Int)
}

struct NonEmptyString: Hashable, Sendable {
    static let maximumLength = 200

    private let storage: String

    init(_ raw: String) throws {
        let canonical = raw.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !canonical.isEmpty else { throw NonEmptyStringError.empty }
        guard canonical.count <= Self.maximumLength else {
            throw NonEmptyStringError.tooLong(maximum: Self.maximumLength)
        }
        storage = canonical
    }

    private init(uncheckedStorage: String) {
        storage = uncheckedStorage
    }

    var value: String { storage }
}

extension NonEmptyString: Codable {
    init(from decoder: Decoder) throws {
        let container = try decoder.singleValueContainer()
        let raw = try container.decode(String.self)
        do {
            try self.init(raw)
        } catch {
            throw DecodingError.dataCorruptedError(
                in: container,
                debugDescription: "Expected a nonempty string within the type's fixed maximum length."
            )
        }
    }

    func encode(to encoder: Encoder) throws {
        var container = encoder.singleValueContainer()
        try container.encode(storage)
    }
}

struct Identifier<Domain>: RawRepresentable, Hashable, Codable, Sendable {
    let rawValue: UUID

    init(rawValue: UUID) {
        self.rawValue = rawValue
    }
}

enum UserDomain {}
enum WorkspaceDomain {}

typealias UserID = Identifier<UserDomain>
typealias WorkspaceID = Identifier<WorkspaceDomain>

struct User: Sendable {
    let id: UserID
    let displayName: NonEmptyString
}

enum EmailCandidateError: Error, Equatable, Sendable {
    case missingAtSign
}

/// A bounded, nonempty registration input containing `@`.
/// This does not prove RFC conformance, deliverability, ownership, or server acceptance.
struct EmailCandidate: Hashable, Sendable {
    private let storage: NonEmptyString

    init(_ raw: String) throws {
        let canonical = try NonEmptyString(raw)
        guard canonical.value.contains("@") else {
            throw EmailCandidateError.missingAtSign
        }
        storage = canonical
    }

    var value: String { storage.value }
}

protocol RegistrationState: Sendable {}

struct DraftRegistration: RegistrationState {
    let rawEmail: String
    let acceptedTerms: Bool
}

struct ReadyRegistration: RegistrationState {
    let emailCandidate: EmailCandidate
}

struct Registration<State: RegistrationState>: Sendable {
    fileprivate let state: State

    fileprivate init(state: State) {
        self.state = state
    }
}

enum RegistrationError: Error, Equatable, Sendable {
    case termsNotAccepted
}

extension Registration where State == DraftRegistration {
    init(rawEmail: String, acceptedTerms: Bool) {
        state = DraftRegistration(rawEmail: rawEmail, acceptedTerms: acceptedTerms)
    }

    func validate() throws -> Registration<ReadyRegistration> {
        guard state.acceptedTerms else { throw RegistrationError.termsNotAccepted }
        return Registration<ReadyRegistration>(
            state: ReadyRegistration(emailCandidate: try EmailCandidate(state.rawEmail))
        )
    }
}

extension Registration where State == ReadyRegistration {
    var emailCandidate: EmailCandidate { state.emailCandidate }
}

struct AccountID: RawRepresentable, Hashable, Codable, Sendable {
    let rawValue: UUID

    init(rawValue: UUID) {
        self.rawValue = rawValue
    }
}

struct DeleteAccountCapability: Sendable {
    fileprivate let accountID: AccountID

    fileprivate init(accountID: AccountID) {
        self.accountID = accountID
    }
}

actor AuthorizationService {
    private var deletableAccounts: Set<AccountID> = []

    func allowDeletion(of accountID: AccountID) {
        deletableAccounts.insert(accountID)
    }

    func authorizeDeletion(of accountID: AccountID) throws -> DeleteAccountCapability {
        guard deletableAccounts.contains(accountID) else {
            throw AuthorizationError.denied
        }
        return DeleteAccountCapability(accountID: accountID)
    }
}

enum AuthorizationError: Error, Sendable {
    case denied
}

struct BoundedArray<Element: Sendable>: Sendable {
    private let storage: [Element]
    let allowedCount: ClosedRange<Int>

    init(_ elements: [Element], allowedCount: ClosedRange<Int>) throws {
        guard allowedCount.contains(elements.count) else {
            throw CardinalityError.outOfRange(
                actual: elements.count,
                allowed: allowedCount
            )
        }
        storage = elements
        self.allowedCount = allowedCount
    }

    var elements: [Element] { storage }
}

enum CardinalityError: Error, Equatable, Sendable {
    case outOfRange(actual: Int, allowed: ClosedRange<Int>)
}

struct AccountDidChange: Sendable {
    let accountID: AccountID
    let revision: Int
}

import Foundation

enum RuntimeCheckFailure: Error {
    case expectedEmptyRejection
    case expectedLengthRejection
    case expectedDecodeRejection
    case expectedEmailCandidateRejection
    case emailCandidateChangedValue
    case roundTripChangedValue
}

@main
struct CorePatternsRuntimeChecks {
    static func main() throws {
        let canonical = try NonEmptyString("  value  ")
        guard canonical.value == "value" else {
            throw RuntimeCheckFailure.roundTripChangedValue
        }

        do {
            _ = try NonEmptyString(" \n\t ")
            throw RuntimeCheckFailure.expectedEmptyRejection
        } catch NonEmptyStringError.empty {
            // Expected.
        }

        let exact = String(repeating: "a", count: NonEmptyString.maximumLength)
        _ = try NonEmptyString(exact)

        let tooLong = exact + "a"
        do {
            _ = try NonEmptyString(tooLong)
            throw RuntimeCheckFailure.expectedLengthRejection
        } catch NonEmptyStringError.tooLong(maximum: NonEmptyString.maximumLength) {
            // Expected.
        }

        let encoded = try JSONEncoder().encode(canonical)
        let decoded = try JSONDecoder().decode(NonEmptyString.self, from: encoded)
        guard decoded == canonical else {
            throw RuntimeCheckFailure.roundTripChangedValue
        }

        let invalidEncoded = try JSONEncoder().encode(tooLong)
        do {
            _ = try JSONDecoder().decode(NonEmptyString.self, from: invalidEncoded)
            throw RuntimeCheckFailure.expectedDecodeRejection
        } catch is DecodingError {
            // Expected: decoding reuses the same fixed validation policy.
        }

        let candidate = try EmailCandidate("  local@example  ")
        guard candidate.value == "local@example" else {
            throw RuntimeCheckFailure.emailCandidateChangedValue
        }

        do {
            _ = try EmailCandidate("not-an-email")
            throw RuntimeCheckFailure.expectedEmailCandidateRejection
        } catch EmailCandidateError.missingAtSign {
            // Expected. This checks only the type's documented, deliberately narrow guarantee.
        }
    }
}

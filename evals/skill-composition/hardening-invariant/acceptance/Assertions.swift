import Foundation

enum AcceptanceFailure: Error {
    case failed(String)
}

@main
struct Acceptance {
    static func main() throws {
        let decoder = JSONDecoder()
        let encoder = JSONEncoder()

        let historical = try decoder.decode(Quantity.self, from: Data(#"{"value":7}"#.utf8))
        guard historical.value == 7 else {
            throw AcceptanceFailure.failed("historical keyed payload changed value")
        }

        guard let direct = Quantity(11) else {
            throw AcceptanceFailure.failed("valid direct construction failed")
        }
        let encoded = try encoder.encode(direct)
        let object = try JSONSerialization.jsonObject(with: encoded) as? [String: Any]
        guard (object?["value"] as? NSNumber)?.intValue == 11 else {
            throw AcceptanceFailure.failed("encoded representation is no longer keyed")
        }
        let roundTrip = try decoder.decode(Quantity.self, from: encoded)
        guard roundTrip == direct else {
            throw AcceptanceFailure.failed("valid keyed round trip changed the value")
        }

        try assertPredicateRejection(0, decoder: decoder)
        try assertPredicateRejection(-4, decoder: decoder)
    }

    private static func assertPredicateRejection(_ value: Int, decoder: JSONDecoder) throws {
        let payload = Data(#"{"value":\#(value)}"#.utf8)
        do {
            _ = try decoder.decode(Quantity.self, from: payload)
            throw AcceptanceFailure.failed("decoded invalid quantity \(value)")
        } catch DecodingError.dataCorrupted {
            return
        } catch DecodingError.typeMismatch {
            throw AcceptanceFailure.failed("invalid quantity failed because the historical keyed shape was not decoded")
        } catch DecodingError.keyNotFound {
            throw AcceptanceFailure.failed("invalid quantity failed before its keyed value was read")
        } catch DecodingError.valueNotFound {
            throw AcceptanceFailure.failed("invalid quantity failed before its keyed value reached domain validation")
        } catch let error as AcceptanceFailure {
            throw error
        } catch {
            // Domain validation may use its own error type. The valid historical
            // and round-trip controls above independently establish the keyed
            // wire shape before this invalid value is presented.
            return
        }
    }
}

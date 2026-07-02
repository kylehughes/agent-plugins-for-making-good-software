// Current Swift 6 language-mode examples. These language features do not inherently
// raise an iOS 16 deployment target. Platform and standard-library symbols still
// need independent runtime availability checks.

enum ParseFailure: Error, Equatable, Sendable {
    case empty
    case notAnInteger
}

func parseCount(_ text: String) throws(ParseFailure) -> Int {
    guard !text.isEmpty else { throw .empty }
    guard let value = Int(text) else { throw .notAnInteger }
    return value
}

/// Demonstrates compiler-enforced single consumption only; it owns no native resource.
struct OneShotValue: ~Copyable {
    private let identifier: Int

    init(identifier: Int) {
        self.identifier = identifier
    }

    consuming func takeIdentifier() -> Int {
        identifier
    }
}

func useOnce(_ value: consuming OneShotValue) -> Int {
    value.takeIdentifier()
}

struct CounterSnapshot: Sendable {
    let value: Int
}

actor Counter {
    private var value = 0

    func increment() -> CounterSnapshot {
        value += 1
        return CounterSnapshot(value: value)
    }

    func snapshot() -> CounterSnapshot {
        CounterSnapshot(value: value)
    }
}

struct WorkItem: Sendable {
    let run: @Sendable () async -> Void
}

enum PurchaseFailure: Error, Equatable, Sendable {
    case alreadyReserved
    case rejected
}

actor Inventory {
    private var reserved: Set<Int> = []

    func purchase(
        _ id: Int,
        operation: @Sendable (Int) async -> Bool
    ) async throws(PurchaseFailure) {
        guard reserved.insert(id).inserted else { throw .alreadyReserved }
        defer { reserved.remove(id) }

        guard await operation(id) else { throw .rejected }
    }
}

import Foundation

/// A count of items in a saved cart. Counts are strictly positive.
struct Quantity: Equatable {
    let value: Int

    init?(_ value: Int) {
        guard value > 0 else { return nil }
        self.value = value
    }
}

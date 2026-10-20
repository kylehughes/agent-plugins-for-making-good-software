import Foundation

precondition(Quantity(0) == nil)
precondition(Quantity(-1) == nil)
precondition(Quantity(3)?.value == 3)

let original = Quantity(7)!
let stored = try JSONEncoder().encode(original)
let restored = try JSONDecoder().decode(Quantity.self, from: stored)
precondition(restored == original)

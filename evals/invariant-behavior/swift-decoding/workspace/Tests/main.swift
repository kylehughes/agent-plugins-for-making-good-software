import Foundation

guard Quantity(5)?.value == 5 else {
    fatalError("valid quantity construction failed")
}

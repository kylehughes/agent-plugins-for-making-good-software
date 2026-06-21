#if canImport(UIKit)
import UIKit

@MainActor
public extension UIAccessibilityIdentification where Self: AnyObject {
    var typedAccessibilityIdentifier: AccessibilityIdentifier? {
        get {
            accessibilityIdentifier.map {
                AccessibilityIdentifier(rawValue: $0)
            }
        }
        set {
            accessibilityIdentifier = newValue?.rawValue
        }
    }

    @discardableResult
    func setAccessibilityIdentifier(
        _ identifier: AccessibilityIdentifier?
    ) -> Self {
        accessibilityIdentifier = identifier?.rawValue
        return self
    }
}
#endif

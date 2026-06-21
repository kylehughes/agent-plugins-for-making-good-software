#if canImport(SwiftUI)
import SwiftUI

public extension View {
    func accessibilityIdentifier(
        _ identifier: AccessibilityIdentifier
    ) -> some View {
        accessibilityIdentifier(identifier.rawValue)
    }

    @ViewBuilder
    func accessibilityIdentifier(
        _ identifier: AccessibilityIdentifier?
    ) -> some View {
        if let identifier {
            accessibilityIdentifier(identifier)
        } else {
            self
        }
    }
}
#endif

#if canImport(XCTest) && (os(iOS) || os(macOS) || os(tvOS) || os(visionOS))
import AccessibilityUI
import Foundation
import XCTest

public extension XCUIElementQuery {
    func matching(
        accessibilityIdentifier: AccessibilityIdentifier
    ) -> XCUIElementQuery {
        matching(
            NSPredicate(
                format: "%K == %@",
                "identifier",
                accessibilityIdentifier.rawValue
            )
        )
    }

    subscript(
        _ accessibilityIdentifier: AccessibilityIdentifier
    ) -> XCUIElement {
        matching(
            accessibilityIdentifier: accessibilityIdentifier
        ).firstMatch
    }
}

public extension XCUIElement {
    @discardableResult
    func requireExistence(
        timeout: TimeInterval = 2,
        file: StaticString = #filePath,
        line: UInt = #line
    ) -> Self {
        XCTAssertTrue(
            waitForExistence(timeout: timeout),
            "Expected element with identifier '\(identifier)' to exist.",
            file: file,
            line: line
        )
        return self
    }
}
#endif

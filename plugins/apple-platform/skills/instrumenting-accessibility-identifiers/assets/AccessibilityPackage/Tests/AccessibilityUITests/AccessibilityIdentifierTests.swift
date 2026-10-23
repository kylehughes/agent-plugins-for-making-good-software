import AccessibilityUI
import Foundation
import XCTest

private enum LoginAccessibility: AccessibilityInstrumented {
    enum AccessibilityUIElement: String, AccessibilityElement {
        case emailField
        case passwordField
        case submitButton
    }

    static let accessibilityIdentifierScope =
        AccessibilityIdentifierScope("LoginView")
}


private enum LegacyAccessibility: AccessibilityInstrumented {
    enum AccessibilityUIElement: String, AccessibilityElement {
        case submitButton
    }

    static let accessibilityIdentifierScope =
        AccessibilityIdentifierScope("CheckoutView")

    static func accessibilityIdentifier(
        for element: AccessibilityUIElement
    ) -> AccessibilityIdentifier {
        switch element {
        case .submitButton:
            AccessibilityIdentifier(rawValue: "checkout_submit")
        }
    }
}

final class AccessibilityIdentifierTests: XCTestCase {
    func testStaticIdentifierConstruction() {
        XCTAssertEqual(
            LoginAccessibility.accessibilityIdentifiers[.submitButton].rawValue,
            "LoginView_submitButton"
        )
        XCTAssertEqual(LoginAccessibility.allAccessibilityIdentifiers.count, 3)
    }


    func testCustomFactoryDispatchesThroughNamespace() {
        XCTAssertEqual(
            LegacyAccessibility.accessibilityIdentifiers[.submitButton].rawValue,
            "checkout_submit"
        )
    }

    func testDynamicIdentifierConstruction() {
        let identifier = AccessibilityIdentifier(
            scope: AccessibilityIdentifierScope("ProductListView"),
            element: "row",
            components: [AccessibilityIdentifierComponent("abc_123")]
        )

        XCTAssertEqual(identifier.rawValue, "ProductListView_row_abc-123")
    }

    func testValidation() {
        XCTAssertTrue(
            AccessibilityIdentifier.isValid("LoginView_submitButton")
        )
        XCTAssertFalse(AccessibilityIdentifier.isValid(""))
        XCTAssertFalse(
            AccessibilityIdentifier.isValid("_LoginView_submitButton")
        )
        XCTAssertFalse(
            AccessibilityIdentifier.isValid("LoginView__submitButton")
        )
        XCTAssertFalse(
            AccessibilityIdentifier.isValid("Login View_submitButton")
        )
    }

    func testCodableRoundTrip() throws {
        let original = LoginAccessibility.accessibilityIdentifiers[.emailField]
        let data = try JSONEncoder().encode(original)
        let decoded = try JSONDecoder().decode(
            AccessibilityIdentifier.self,
            from: data
        )

        XCTAssertEqual(decoded, original)
    }

    func testScopeDecodingPreservesHistoricalShapeAndValidation() throws {
        let historical = Data(#""LoginView""#.utf8)
        let value = try JSONDecoder().decode(AccessibilityIdentifierScope.self, from: historical)
        XCTAssertEqual(value.rawValue, "LoginView")
        XCTAssertEqual(
            try JSONDecoder().decode(
                AccessibilityIdentifierScope.self,
                from: JSONEncoder().encode(value)
            ),
            value
        )

        for invalid in ["", "Login View", String(repeating: "a", count: 81)] {
            let payload = try JSONEncoder().encode(invalid)
            XCTAssertThrowsError(try JSONDecoder().decode(AccessibilityIdentifierScope.self, from: payload))
        }
    }

    func testComponentDecodingPreservesHistoricalShapeAndValidation() throws {
        let historical = Data(#""abc-123""#.utf8)
        let value = try JSONDecoder().decode(AccessibilityIdentifierComponent.self, from: historical)
        XCTAssertEqual(value.rawValue, "abc-123")
        XCTAssertEqual(
            try JSONDecoder().decode(
                AccessibilityIdentifierComponent.self,
                from: JSONEncoder().encode(value)
            ),
            value
        )

        XCTAssertEqual(
            try JSONDecoder().decode(AccessibilityIdentifierComponent.self, from: Data(#""abc_123""#.utf8)).rawValue,
            "abc-123"
        )

        for invalid in ["", String(repeating: "a", count: 81)] {
            let payload = try JSONEncoder().encode(invalid)
            XCTAssertThrowsError(try JSONDecoder().decode(AccessibilityIdentifierComponent.self, from: payload))
        }
    }

}

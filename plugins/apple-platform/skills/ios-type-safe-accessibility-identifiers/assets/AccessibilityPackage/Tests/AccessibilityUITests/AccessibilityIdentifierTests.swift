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
}

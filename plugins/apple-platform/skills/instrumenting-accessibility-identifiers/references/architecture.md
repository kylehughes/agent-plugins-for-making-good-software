# Architecture reference

## Purpose and boundary

This pattern creates a public, compiler-checked contract for the string transported through Apple platform `accessibilityIdentifier` APIs and consumed by XCUITest.

It does not replace semantic accessibility work. Continue to review labels, hints, traits, values, focus order, Dynamic Type, contrast, Reduce Motion, keyboard behavior, and assistive-technology operation separately.

## Recommended module topology

Prefer two reusable products:

```swift
.library(name: "AccessibilityUI", targets: ["AccessibilityUI"]),
.library(name: "AccessibilityUIForTest", targets: ["AccessibilityUIForTest"]),
```

`AccessibilityUI` is safe for application and feature modules. `AccessibilityUIForTest` depends on `AccessibilityUI`, imports XCTest, and is linked only by UI-test or screenshot-test targets.

A standalone package can start with:

```swift
// swift-tools-version: 6.0
import PackageDescription

let package = Package(
    name: "Accessibility",
    platforms: [
        .iOS(.v16),
    ],
    products: [
        .library(name: "AccessibilityUI", targets: ["AccessibilityUI"]),
        .library(name: "AccessibilityUIForTest", targets: ["AccessibilityUIForTest"]),
    ],
    targets: [
        .target(name: "AccessibilityUI"),
        .target(
            name: "AccessibilityUIForTest",
            dependencies: ["AccessibilityUI"]
        ),
        .testTarget(
            name: "AccessibilityUITests",
            dependencies: ["AccessibilityUI"]
        ),
    ],
    swiftLanguageModes: [.v6]
)
```

Adapt the deployment target, tools version, language mode, and target names to the repository. Do not force an upgrade solely for this pattern.

If the repository already has equivalent support modules, use them rather than creating parallel infrastructure. If Swift packages are prohibited, use equivalent Xcode library/framework targets while preserving the production/test dependency boundary.

## Core value type

Use a non-generic value object. The concrete owner matters while constructing the identifier, but SwiftUI, UIKit, reusable components, and XCTest only need a stable string afterward.

```swift
public struct AccessibilityIdentifier:
    Codable,
    Equatable,
    Hashable,
    Sendable,
    Identifiable,
    RawRepresentable,
    CustomStringConvertible
{
    public typealias RawValue = String

    public let rawValue: String
    public var value: String { rawValue }
    public var id: String { rawValue }
    public var description: String { rawValue }

    public init(rawValue: String) {
        precondition(
            Self.isValid(rawValue),
            "Invalid accessibility identifier: \(rawValue)"
        )
        self.rawValue = rawValue
    }

    @available(
        *,
        deprecated,
        message: "Use a screen-scoped identifier factory."
    )
    public init(_ rawValue: String) {
        self.init(rawValue: rawValue)
    }

    public init(
        scope: AccessibilityIdentifierScope,
        element: String,
        components: [AccessibilityIdentifierComponent] = []
    ) {
        var parts = [scope.rawValue, element]
        parts.append(contentsOf: components.map(\.rawValue))
        self.init(rawValue: parts.joined(separator: "_"))
    }

    public init(from decoder: Decoder) throws {
        let container = try decoder.singleValueContainer()
        let rawValue = try container.decode(String.self)
        guard Self.isValid(rawValue) else {
            throw DecodingError.dataCorruptedError(
                in: container,
                debugDescription: "Invalid accessibility identifier: \(rawValue)"
            )
        }
        self.rawValue = rawValue
    }

    public func encode(to encoder: Encoder) throws {
        var container = encoder.singleValueContainer()
        try container.encode(rawValue)
    }

    public static func isValid(_ value: String) -> Bool {
        guard !value.isEmpty else { return false }
        guard value.count <= 180 else { return false }
        guard !value.hasPrefix("_") else { return false }
        guard !value.hasSuffix("_") else { return false }
        guard !value.contains("__") else { return false }
        return value.unicodeScalars.allSatisfy(isAllowedScalar)
    }

    private static func isAllowedScalar(_ scalar: Unicode.Scalar) -> Bool {
        switch scalar.value {
        case 45,       // -
             46,       // .
             48...57,  // 0-9
             58,       // :
             65...90,  // A-Z
             95,       // _
             97...122: // a-z
            return true
        default:
            return false
        }
    }
}
```

Do not add `ExpressibleByStringLiteral` to the core target. If migration cannot proceed without it, put the deprecated conformance in a clearly named migration-only file or target and delete it after raw strings are removed.

## Scope and dynamic components

```swift
public struct AccessibilityIdentifierScope:
    RawRepresentable,
    Equatable,
    Hashable,
    Sendable,
    CustomStringConvertible
{
    public let rawValue: String
    public var description: String { rawValue }

    public init(rawValue: String) {
        precondition(!rawValue.isEmpty, "Accessibility scope must not be empty.")
        precondition(rawValue.count <= 80, "Accessibility scope is too long.")
        precondition(
            rawValue.unicodeScalars.allSatisfy(Self.isAllowedScalar),
            "Invalid accessibility scope: \(rawValue)"
        )
        self.rawValue = rawValue
    }

    public init(_ rawValue: String) {
        self.init(rawValue: rawValue)
    }

    private static func isAllowedScalar(_ scalar: Unicode.Scalar) -> Bool {
        switch scalar.value {
        case 48...57, 65...90, 95, 97...122:
            return true
        default:
            return false
        }
    }
}
```

Most identifiers must remain static. Use a dynamic component only when automation must address a specific repeated element by a stable identity.

```swift
public struct AccessibilityIdentifierComponent:
    Codable,
    Equatable,
    Hashable,
    Sendable,
    RawRepresentable,
    CustomStringConvertible
{
    public let rawValue: String

    public var description: String { rawValue }

    public init(rawValue: String) {
        let sanitized = rawValue.unicodeScalars
            .map(Self.sanitizedScalar)
            .joined()

        precondition(
            !sanitized.isEmpty,
            "Identifier component must not be empty."
        )
        precondition(
            sanitized.count <= 80,
            "Identifier component is too long: \(sanitized)"
        )

        self.rawValue = sanitized
    }

    public init(_ value: some CustomStringConvertible) {
        self.init(rawValue: value.description)
    }

    public init(from decoder: Decoder) throws {
        let container = try decoder.singleValueContainer()
        let rawValue = try container.decode(String.self)
        let sanitized = rawValue.unicodeScalars.map(Self.sanitizedScalar).joined()

        guard !sanitized.isEmpty && sanitized.count <= 80 else {
            throw DecodingError.dataCorruptedError(
                in: container,
                debugDescription: "Invalid accessibility identifier component."
            )
        }

        self.rawValue = sanitized
    }

    private static func sanitizedScalar(_ scalar: Unicode.Scalar) -> String {
        switch scalar.value {
        case 45,       // -
             46,       // .
             48...57,  // 0-9
             65...90,  // A-Z
             97...122: // a-z
            return String(scalar)
        default:
            return "-"
        }
    }
}
```

Sanitization is not anonymization. Do not pass names, email addresses, tokens, localized text, raw content, or other sensitive values into this type.

Good dynamic inputs include stable database IDs, UUIDs, and stable enum raw values. Avoid transient list indexes unless index behavior is explicitly under test.

## Owner and element protocols

```swift
public protocol AccessibilityElement:
    RawRepresentable,
    CaseIterable,
    Equatable,
    Hashable,
    Sendable
where RawValue == String {}

public protocol AccessibilityInstrumented {
    associatedtype AccessibilityUIElement: AccessibilityElement
    static var accessibilityIdentifierScope: AccessibilityIdentifierScope { get }
    static func accessibilityIdentifier(
        for element: AccessibilityUIElement
    ) -> AccessibilityIdentifier
}
```

Default construction and catalog support:

```swift
public extension AccessibilityInstrumented {
    static func accessibilityIdentifier(
        for element: AccessibilityUIElement
    ) -> AccessibilityIdentifier {
        AccessibilityIdentifier(
            scope: accessibilityIdentifierScope,
            element: element.rawValue
        )
    }

    static var accessibilityIdentifiers: AccessibilityIdentifierNamespace<Self> {
        AccessibilityIdentifierNamespace()
    }

    static var allAccessibilityIdentifiers: [AccessibilityIdentifier] {
        AccessibilityUIElement.allCases.map {
            accessibilityIdentifier(for: $0)
        }
    }
}

public struct AccessibilityIdentifierNamespace<Owner: AccessibilityInstrumented>:
    Sendable
{
    public init() {}

    public subscript(
        _ element: Owner.AccessibilityUIElement
    ) -> AccessibilityIdentifier {
        Owner.accessibilityIdentifier(for: element)
    }

    public func callAsFunction(
        _ element: Owner.AccessibilityUIElement
    ) -> AccessibilityIdentifier {
        Owner.accessibilityIdentifier(for: element)
    }

    public var all: [AccessibilityIdentifier] {
        Owner.allAccessibilityIdentifiers
    }
}
```

This gives the canonical generic spelling:

```swift
LoginView.accessibilityIdentifiers[.submitButton]
```

## Choosing the owner type

### Public, non-generic, importable owner

Conform the actual view or view controller:

```swift
extension LoginView: AccessibilityInstrumented {
    public enum AccessibilityUIElement: String, AccessibilityElement {
        case emailField
        case passwordField
        case submitButton
    }

    public static let accessibilityIdentifierScope =
        AccessibilityIdentifierScope("LoginView")
}
```

### Generic, internal, or non-importable owner

Use a standalone namespace:

```swift
public enum RankingFlowComparisonAccessibility: AccessibilityInstrumented {
    public enum AccessibilityUIElement: String, AccessibilityElement {
        case leftButton
        case rightButton
    }

    public static let accessibilityIdentifierScope =
        AccessibilityIdentifierScope("RankingFlowComparisonView")
}
```

Use the standalone approach when a UI-test target cannot import the concrete owner. This is common in monolithic app executable targets and avoids exposing implementation types merely for test compilation.

### Compact screen-specific factory

For high-traffic tests, layer a readable factory over the protocol-backed implementation:

```swift
public extension AccessibilityIdentifier {
    static func loginView(_ element: LoginView.AccessibilityUIElement) -> Self {
        LoginView.accessibilityIdentifier(for: element)
    }
}
```

Then:

```swift
app.buttons[.loginView(.submitButton)].tap()
```

The factory must live in a module that can see the owner element type and can be imported by the UI-test target. Never introduce a reverse dependency from the core package to feature modules.

## Naming policy

Static identifiers use:

```text
Scope_element
```

Dynamic identifiers use:

```text
Scope_element_component
```

Examples:

```text
LoginView_emailField
LoginView_submitButton
SettingsView_sortingAlgorithmRow
ProductListView_row_0F0B7F4F-A97E-43C0-A48D-1C65E0BEF6AF
```

Scope names are stable `UpperCamelCase` ownership names. Element names are stable `lowerCamelCase` roles.

Prefer:

```swift
case rankButton
case sortingAlgorithmRow
case emptyStateRetryButton
case destructiveConfirmButton
```

Avoid:

```swift
case button
case row
case blueButton
case localizedTitle
case readyToRankStartRankingNowButton
```

A protocol enforces shape, not naming quality. Naming remains a code-review and lint concern.

## SwiftUI bridge

```swift
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
```

Attach the identifier to the semantic automation target:

```swift
Button("Sign In", action: signIn)
    .accessibilityIdentifier(
        LoginView.accessibilityIdentifiers[.submitButton]
    )
```

Do not attach it only to the `Text` inside the button. For rows, attach it to the `NavigationLink` or tappable row container when the row is the interaction unit. Avoid assigning both parent and child identifiers unless automation needs both.

## UIKit bridge

```swift
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
```

Usage:

```swift
doneButton.setAccessibilityIdentifier(
    SettingsViewController.accessibilityIdentifiers[.doneButton]
)
```

For reusable cells:

```swift
override func prepareForReuse() {
    super.prepareForReuse()
    setAccessibilityIdentifier(nil)
}
```

Do not add new raw identifiers in storyboards or XIBs. Preserve existing Interface Builder identifiers only as explicit migration state.

## XCTest bridge

Put this in the test-only module:

```swift
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
```

The predicate is deliberate. Do not forward the typed subscript to `self[rawValue]`, and do not use a broader lookup that may match labels, titles, values, or placeholders.

## Shared components

Reusable UI accepts the value type and does not own screen naming:

```swift
public struct PrimaryActionButton: View {
    private let title: LocalizedStringKey
    private let identifier: AccessibilityIdentifier?
    private let action: () -> Void

    public init(
        title: LocalizedStringKey,
        accessibilityIdentifier: AccessibilityIdentifier? = nil,
        action: @escaping () -> Void
    ) {
        self.title = title
        self.identifier = accessibilityIdentifier
        self.action = action
    }

    public var body: some View {
        Button(action: action) {
            Text(title)
                .frame(maxWidth: .infinity)
        }
        .accessibilityIdentifier(identifier)
    }
}
```

The screen supplies identity:

```swift
PrimaryActionButton(
    title: "Start",
    accessibilityIdentifier:
        RankingFlowStartAccessibility.accessibilityIdentifiers[.startButton],
    action: start
)
```

A shared component that owns multiple automation-relevant controls may accept multiple optional typed identifiers.

## Static catalog and duplicate tests

Swift does not provide useful automatic discovery of every conforming screen type. Maintain an explicit app-level catalog in a test-support location:

```swift
enum AppAccessibilityIdentifierCatalog {
    static let all: [AccessibilityIdentifier] =
        LoginView.allAccessibilityIdentifiers
        + SettingsAccessibility.allAccessibilityIdentifiers
        + RankingFlowComparisonAccessibility.allAccessibilityIdentifiers
}
```

Contract tests:

```swift
final class AccessibilityIdentifierContractTests: XCTestCase {
    func testAllStaticIdentifiersAreValid() {
        let invalid = AppAccessibilityIdentifierCatalog.all
            .map(\.rawValue)
            .filter { !AccessibilityIdentifier.isValid($0) }

        XCTAssertEqual(invalid, [])
    }

    func testAllStaticIdentifiersAreUnique() {
        let grouped = Dictionary(
            grouping: AppAccessibilityIdentifierCatalog.all.map(\.rawValue),
            by: { $0 }
        )

        let duplicates = grouped
            .filter { $0.value.count > 1 }
            .map(\.key)
            .sorted()

        XCTAssertEqual(duplicates, [])
    }
}
```

The catalog catches static collisions and factory mistakes only when maintained. Dynamic identifiers need separate behavior-specific tests when necessary.

## Linting baseline

A SwiftLint-style starter rule:

```yaml
custom_rules:
  no_raw_accessibility_identifiers:
    name: "No raw accessibility identifiers"
    regex: '(\.accessibilityIdentifier\s*\(\s*"|accessibilityIdentifier\s*=\s*")'
    message: "Use typed AccessibilityIdentifier factories instead of raw strings."
    severity: error
```

Exclude only the core package, explicit migration files, and generated code. Mature codebases should prefer SwiftSyntax so the rule can distinguish identifier APIs from unrelated strings more accurately.

Also audit UI-test selectors such as:

```swift
app.buttons["LoginView_submitButton"]
```

## Selection policy

Instrument stable workflow anchors:

- Primary and navigation buttons.
- Destructive confirmation controls.
- Important form fields.
- Settings rows.
- Tab items.
- Repeated cells or rows automation must address.
- Screenshot-flow controls.
- Controls with localized or dynamic visible labels.

Do not instrument every subview. Avoid decorative views, layout-only containers, unused labels, and implementation details that tests can select more clearly by role and hierarchy.

## Test-writing policy

Use identifiers for lookup:

```swift
app.buttons[.loginView(.submitButton)].requireExistence().tap()
```

Do not use raw strings or localized visible copy when a typed identifier exists.

Do not assert the raw identifier string in normal UI tests. Contract tests cover construction. Use user-facing labels and values for user-facing assertions.

## Trade-offs

The ceremony is intentional. It buys compiler-checked element references, stable localized-test behavior, explicit ownership, a curated public automation surface, and duplicate detection.

It does not make uniqueness automatic, because the app catalog is explicit. It does not prove real-world accessibility quality, because identifiers are only the transport used by automation.

## Decoding the validated wrappers

The bundled Scope and Component types preserve their RawRepresentable scalar-string wire format with custom decoding. Reject malformed values with a decoding error instead of routing untrusted input through a trapping initializer. Components retain constructor sanitization before checking empty/length constraints. Keep fixed historical payload, invalid payload, and valid round-trip tests for each wrapper.

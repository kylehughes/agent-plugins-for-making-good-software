# Migration guide

Use this guide when raw app-side identifiers or raw UI-test selectors already exist.

## Principles

- Separate type-safety migration from identifier renaming whenever possible.
- Preserve behavior first; normalize names later.
- Keep migration shims isolated, deprecated, measurable, and removable.
- Migrate automation-critical flows before incidental instrumentation.
- Do not convert visible labels into identifiers merely because a test currently selects by copy.

## 1. Inventory

Run:

```bash
python3 scripts/audit_accessibility_identifiers.py /path/to/repository
```

The script reports likely raw SwiftUI modifiers, UIKit assignments, raw XCUI query subscripts, and broad identifier lookup calls. It is intentionally conservative and may report false positives; inspect each result.

Also search for:

```text
accessibilityIdentifier
XCUIElementQuery
XCUIApplication
firstMatch
waitForExistence
screenshot
snapshot
```

Identify:

- Raw values and their owning screens.
- Test targets and screenshot targets that consume each value.
- Duplicate values used across screens.
- Values derived from localized text or sensitive data.
- Interface Builder identifiers.
- Shared components that currently accept `String?`.
- Whether UI tests can import the owning feature type.

## 2. Establish infrastructure without changing values

Add the production and test-only modules first. Add the core types, SwiftUI/UIKit bridges, and strict XCTest bridge.

Do not rename raw values in the same change unless the repository is small and the test impact is trivial.

For a legacy value that does not match the final naming policy, preserve it behind the typed factory:

```swift
extension CheckoutAccessibility: AccessibilityInstrumented {
    public enum AccessibilityUIElement: String, AccessibilityElement {
        case submitButton
    }

    public static let accessibilityIdentifierScope =
        AccessibilityIdentifierScope("CheckoutView")

    public static func accessibilityIdentifier(
        for element: AccessibilityUIElement
    ) -> AccessibilityIdentifier {
        switch element {
        case .submitButton:
            AccessibilityIdentifier(rawValue: "checkout_submit")
        }
    }
}
```

If only one element is exceptional, prefer a small screen-specific factory rather than weakening the generic core. Add a clear migration comment or tracking reference.

## 3. Choose screen ownership deliberately

Use a concrete view/view-controller conformance only when it is public and importable by all consumers.

For app executable targets, internal owners, generic types, or dependency-boundary problems, create a standalone namespace in an importable production library:

```swift
public enum CheckoutAccessibility: AccessibilityInstrumented {
    // ...
}
```

Do not make an implementation type public solely to satisfy UI tests. Do not use `@testable import` as the public automation contract.

## 4. Migrate app-side assignments

Replace:

```swift
.accessibilityIdentifier("checkout_submit")
```

with:

```swift
.accessibilityIdentifier(
    CheckoutAccessibility.accessibilityIdentifiers[.submitButton]
)
```

Replace:

```swift
button.accessibilityIdentifier = "checkout_submit"
```

with:

```swift
button.setAccessibilityIdentifier(
    CheckoutAccessibility.accessibilityIdentifiers[.submitButton]
)
```

For shared components, change `String?` parameters to `AccessibilityIdentifier?` and keep identity at the screen call site.

For reusable cells, clear identifiers in `prepareForReuse()` when configuration can change or omit the identifier.

## 5. Migrate test selectors

Replace:

```swift
app.buttons["checkout_submit"].tap()
```

with either:

```swift
app.buttons[
    CheckoutAccessibility.accessibilityIdentifiers[.submitButton]
].tap()
```

or a compact factory:

```swift
app.buttons[.checkoutView(.submitButton)].tap()
```

Ensure the typed query resolves through the strict predicate bridge. Do not implement it by forwarding to the raw string subscript.

Replace copy-coupled selectors only when the element has a stable typed identifier. Keep labels for assertions about user-facing text.

## 6. Handle temporary string-literal compatibility

Avoid it. When a large migration genuinely requires source compatibility, isolate this in a migration-only file:

```swift
@available(
    *,
    deprecated,
    message: "Use a screen-scoped factory. Remove after identifier migration."
)
extension AccessibilityIdentifier: ExpressibleByStringLiteral {
    public init(stringLiteral value: String) {
        self.init(rawValue: value)
    }
}
```

Requirements:

- The file name must make the temporary status obvious.
- Exclude only that file from lint.
- Track remaining uses with the audit script or compiler warnings.
- Delete the conformance as soon as call sites are migrated.
- Never ship it as the default reference API.

## 7. Normalize names separately

After typed construction and selectors are stable, optionally rename legacy values to:

```text
Scope_element
Scope_element_component
```

Treat this as an automation-contract change. Update app code and all automation consumers atomically. Consider external screenshot runners, Appium consumers, or downstream test repositories before renaming.

## 8. Add the catalog and lint

Build an explicit static catalog from every screen/namespace and add validity and uniqueness tests.

Then add lint preventing new raw app-side identifiers. Keep exclusions narrow:

- Core infrastructure.
- Explicit legacy migration files.
- Generated code when unavoidable.

Do not exclude entire feature or test directories merely to make the migration pass.

## 9. Validate each migration slice

For each migrated screen or flow:

1. Compile the feature/app target.
2. Compile the UI-test target.
3. Run relevant unit/contract tests.
4. Run the narrow UI-test or screenshot flow when available.
5. Run the audit script and compare findings with the previous baseline.
6. Inspect the accessibility hierarchy when SwiftUI container behavior is non-obvious.

## 10. Completion criteria

A migration is complete when:

- Normal app code contains no raw identifier strings.
- UI and screenshot tests contain no raw selectors for instrumented controls.
- The string-literal conformance is deleted.
- Legacy raw-value exceptions are either removed or explicitly documented.
- Static identifiers are cataloged and unique.
- New raw identifiers are blocked by lint or equivalent tooling.
- The test-only bridge is not linked into app-facing targets.

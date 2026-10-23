---
name: instrumenting-accessibility-identifiers
description: "Add or audit typed accessibility identifiers and XCUITest selectors in SwiftUI or UIKit. Use proactively for automation contracts and selector migration; not a general VoiceOver audit."
---

# Instrumenting Accessibility Identifiers

Create or migrate a compiler-checked accessibility-identifier contract that works across SwiftUI, UIKit, XCUITest, and screenshot automation.

Resolve bundled `scripts/`, `assets/`, and reference paths relative to this skill directory, not the consumer repository.

Read [references/architecture.md](references/architecture.md) before implementing or reviewing this pattern. Read [references/migration.md](references/migration.md) when the repository already contains raw identifiers. Before finishing, check the work against [references/review-checklist.md](references/review-checklist.md).

## Non-negotiable decisions

1. Keep `AccessibilityIdentifier` non-generic. Owner typing belongs at construction time, not in every shared component API.
2. Do not add `ExpressibleByStringLiteral` to the core module. A deprecated migration-only conformance may exist in an isolated file and must have an explicit removal plan.
3. In XCUITest, match `identifier == rawValue` with an `NSPredicate`. Do not implement the typed subscript by forwarding to a string subscript or broad identifier-style lookup.
4. Keep XCTest code out of app-facing products. The test bridge must live in a separate target or module that is linked only by UI-test and screenshot-test targets.
5. Treat identifiers as an automation contract, not as a substitute for labels, hints, traits, values, focus behavior, Dynamic Type, contrast, or other accessibility work.
6. Never put localized copy, user data, credentials, tokens, email addresses, names, or other sensitive content into an identifier.
7. Do not use `@testable import` for the automation contract. Types consumed by UI tests must be public and live in an importable library/module.

## Workflow

### 1. Inspect the repository

Determine these facts from the repository before editing:

- Xcode project, workspace, Swift package, or mixed structure.
- Deployment targets and Swift language mode.
- Existing support, design-system, feature, test-support, or accessibility modules.
- Which modules are importable from the UI-test target.
- SwiftUI, UIKit, or mixed ownership of each instrumented control.
- Existing raw app-side identifiers, raw UI-test selectors, screenshot automation, and identifier conventions.
- Existing lint, formatter, package, and build/test commands.

Run the bundled read-only inventory when useful:

```bash
python3 scripts/audit_accessibility_identifiers.py /path/to/repository
```

Do not raise the deployment target, Swift tools version, or language mode merely to install this pattern. Match the repository unless the user explicitly requests an upgrade.
Do not introduce macros, code generation, page-object architecture, or a new dependency unless the repository already standardizes it or the user explicitly requests it.

### 2. Choose the module boundary

Use this order:

1. Extend an existing production-safe support module and existing test-support module when their dependency direction is correct.
2. Otherwise add a local Swift package with `AccessibilityUI` and `AccessibilityUIForTest` products.
3. If repository policy forbids local packages, create equivalent production and test-only framework/library targets.

Never make `AccessibilityUI` depend on app or feature modules. Screen contracts and compact screen factories belong in the owning feature module or a separate app-specific identifier-contract module.

For a modular app, a public view or view controller may conform directly to `AccessibilityInstrumented`. For a monolithic executable target, an internal owner, or any type the UI-test target cannot import, use a standalone public namespace in a shared library instead of forcing the concrete UI type public.

Use [assets/AccessibilityPackage](assets/AccessibilityPackage) as the baseline only when creating new infrastructure. Adapt names, deployment target, language mode, file headers, access control, and repository conventions rather than copying blindly.

### 3. Implement the core contract

The production-facing module must provide:

- `AccessibilityIdentifier`
- `AccessibilityIdentifierComponent`
- `AccessibilityIdentifierScope`
- `AccessibilityElement`
- `AccessibilityInstrumented`
- `AccessibilityIdentifierNamespace`
- SwiftUI typed modifier overloads when SwiftUI is available
- UIKit typed setter/property helpers when UIKit is available

The canonical generated form is:

```text
Scope_element
Scope_element_component
```

Use stable `UpperCamelCase` scopes and stable `lowerCamelCase` element roles. Dynamic components must come from stable, non-sensitive identities and pass through `AccessibilityIdentifierComponent`.

### 4. Define screen contracts

Prefer a nested enum when the owner is non-generic, public, and importable by consumers:

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

Use a standalone namespace when the owner is generic, internal, app-executable-only, or otherwise unsuitable as the public contract:

```swift
public enum LoginAccessibility: AccessibilityInstrumented {
    public enum AccessibilityUIElement: String, AccessibilityElement {
        case emailField
        case passwordField
        case submitButton
    }

    public static let accessibilityIdentifierScope =
        AccessibilityIdentifierScope("LoginView")
}
```

Normal app spelling:

```swift
LoginView.accessibilityIdentifiers[.submitButton]
LoginAccessibility.accessibilityIdentifiers[.submitButton]
```

A compact screen-specific factory is optional and recommended for high-traffic UI tests:

```swift
public extension AccessibilityIdentifier {
    static func loginView(_ element: LoginView.AccessibilityUIElement) -> Self {
        LoginView.accessibilityIdentifier(for: element)
    }
}
```

Do not create a dependency cycle to obtain the compact spelling.

### 5. Instrument semantic targets

SwiftUI:

- Attach the identifier to `Button`, `TextField`, `SecureField`, `NavigationLink`, or the actual tappable row/container.
- Do not attach only to decorative descendants such as the `Text` inside a `Button`.
- Verify complex containers because SwiftUI can combine or transform accessibility elements.

UIKit:

- Set identifiers in code through the typed helper.
- Clear reusable cell identifiers in `prepareForReuse()` when configuration can omit or change them.
- Treat Interface Builder strings as migration-only legacy state.
- Instrument `UIBarButtonItem`, cells, controls, and semantic containers only when automation needs them.

Shared components accept `AccessibilityIdentifier?`, never `String?`, and forward it to the concrete interactive element. Shared components do not invent screen identity.

### 6. Add the strict XCTest bridge

The test-only module must provide:

```swift
app.buttons[.loginView(.submitButton)]
```

or:

```swift
app.buttons[LoginView.accessibilityIdentifiers[.submitButton]]
```

Implement lookup with a predicate on the `identifier` attribute and return `firstMatch`. Keep existence helpers small and assertion messages identifier-focused.

### 7. Migrate without unnecessary churn

Preserve existing raw identifier values during the first migration pass when renaming them would create unrelated test churn. Encode those values behind typed factories, then normalize names in a separate deliberate change.

Replace in this order:

1. Core infrastructure and bridges.
2. Automation-critical screen contracts.
3. App-side raw assignments/modifiers.
4. UI-test and screenshot-test raw selectors.
5. Static identifier catalog and duplicate tests.
6. Lint rule preventing new raw strings.
7. Temporary migration conformance and legacy exceptions.

Do not instrument every view. Keep the public automation surface curated around stable workflow anchors.

### 8. Add enforcement

Create an app-level catalog of all static identifiers and tests for validity and uniqueness. The catalog must be maintained explicitly; Swift cannot reliably discover every conforming type automatically.

Add a repository-appropriate lint rule that blocks raw `.accessibilityIdentifier("...")` calls and raw `accessibilityIdentifier = "..."` assignments outside the core package and explicit migration files. Prefer SwiftSyntax for mature codebases; a custom regex rule is acceptable as a starter.

### 9. Validate

Run the narrowest available checks first, then the repository-standard checks:

- `swift test` for a standalone package when applicable.
- Targeted build/tests for changed app and feature targets.
- UI-test compilation and relevant UI tests when the environment supports them.
- Identifier catalog validity and uniqueness tests.
- The audit script again, accounting only for documented migration exceptions.
- Existing lint and formatting commands.

Inspect the final diff for accidental public API expansion, app-to-test dependencies, raw strings, sensitive dynamic components, and identifiers attached to the wrong semantic element.

## Completion report

State:

- Where the production and test-only contracts live.
- Which screens or components were instrumented or migrated.
- Whether raw values were preserved or renamed.
- Which build, test, lint, and audit commands ran and their results.
- Any remaining legacy exceptions and the exact reason each remains.

Do not claim that identifier instrumentation proves the UI is accessible.

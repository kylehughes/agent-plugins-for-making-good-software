# Review checklist

## Architecture

- [ ] Production identifier infrastructure is importable by app/feature code.
- [ ] XCTest helpers live in a separate test-only product or target.
- [ ] No app-facing target links `AccessibilityUIForTest` or XCTest transitively.
- [ ] The core module does not depend on app or feature modules.
- [ ] UI tests import a public contract rather than using `@testable import`.
- [ ] Concrete owner types are used only when they are suitable public/importable contracts; otherwise a standalone namespace is used.

## Core API

- [ ] `AccessibilityIdentifier` is non-generic and validates raw values.
- [ ] The normal API builds identifiers from typed scope and element models.
- [ ] `ExpressibleByStringLiteral` is absent from the core target.
- [ ] Any migration-only string-literal conformance is isolated, deprecated, tracked, and scheduled for removal.
- [ ] Dynamic components are sanitized, stable, and non-sensitive.

## Screen contracts

- [ ] Every new static identifier has a screen-scoped element case.
- [ ] Element enums conform through `AccessibilityElement` and are `CaseIterable`.
- [ ] Scope names are stable and element cases name roles rather than visible copy or styling.
- [ ] Generic/internal/non-importable screens use a standalone namespace where needed.
- [ ] Compact factories do not create dependency cycles.

## SwiftUI and UIKit

- [ ] SwiftUI identifiers are attached to semantic controls, not decorative children.
- [ ] UIKit code uses typed setters or properties rather than raw assignments.
- [ ] Reusable cells clear stale identifiers when necessary.
- [ ] New Interface Builder raw identifiers were not introduced.
- [ ] Shared components accept `AccessibilityIdentifier?`, not `String?`.
- [ ] Shared components forward identifiers and do not invent screen identity.

## Tests

- [ ] XCTest lookup uses `NSPredicate(format: "%K == %@", "identifier", rawValue)` or an equivalent strict identifier-only predicate.
- [ ] The typed query subscript does not forward to a raw string subscript.
- [ ] UI tests use typed selectors for instrumented controls.
- [ ] Visible labels remain the basis for user-facing copy assertions.
- [ ] Tests do not assert raw identifier strings except focused contract tests.
- [ ] Static validity and uniqueness tests exist and the catalog includes new cases.

## Policy and migration

- [ ] No localized copy, user data, credentials, tokens, or secrets appear in identifiers.
- [ ] The automation surface is curated; decorative and layout-only views are not instrumented without need.
- [ ] Existing raw values were preserved intentionally or renamed atomically across consumers.
- [ ] Lint or equivalent tooling prevents new raw identifier strings.
- [ ] Exclusions are narrow and migration-specific.
- [ ] Remaining legacy exceptions are documented with reasons.

## Validation

- [ ] Changed package/targets compile.
- [ ] Contract tests pass.
- [ ] Relevant UI or screenshot tests compile and run when the environment permits.
- [ ] The raw-string audit was rerun.
- [ ] Existing lint and formatting checks pass.
- [ ] The final report does not imply that identifier coverage proves accessibility quality.

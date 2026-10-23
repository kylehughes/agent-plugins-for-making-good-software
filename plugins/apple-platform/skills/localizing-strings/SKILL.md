---
name: localizing-strings
description: "Localize Apple-platform UI text with string catalogs and bundle-aware APIs. Use proactively for new user-facing strings, plurals, interpolation, or hardcoded-string extraction."
---

# Localizing Strings

Localize application UI text while preserving the repository’s catalog keys, resource bundles, extraction workflow, and language-selection behavior. Use for interpolation, plural variations, accessibility text, and catalog migration. Do not translate developer diagnostics or change the app’s language policy.

## Inspect before editing

- Find the affected target, catalog, source language, and owning resource bundle.
- Preserve existing key conventions. Phrase keys are readable defaults; stable semantic keys are also valid, especially when source wording changes independently of identity.
- Use `Bundle.module` only for Swift package targets that provide resources. App resources normally use the main bundle; frameworks use the bundle owning their catalog. See [localizing package resources](https://developer.apple.com/documentation/xcode/localizing-package-resources).
- Inspect the project’s extraction/build commands and supported OS versions. Do not raise deployment targets to use a localization API.

## Choose the API

- SwiftUI controls such as `Text("Delete Message")` already treat suitable literal initializers as localizable. Preserve that path when it fits; do not wrap every literal in `String(localized:)`.
- Use `String(localized:bundle:comment:)` when UIKit or another caller needs a resolved `String`.
- Preserve `LocalizedStringResource`, localization wrappers, generated symbols, or legacy APIs when they serve the project’s compatibility or deferred-resolution contract.
- Keep interpolation in one localized phrase so translators can reorder arguments. Avoid concatenating translated fragments.
- Localize labels, button titles, placeholders, visible errors, accessibility labels/hints, and help text. Keep logs, assertions, programming errors, and automation identifiers unlocalized.

## Implementation workflow

1. Identify the new or changed user-facing text within the requested surface. Check SwiftUI initializer overloads before classifying literals as hardcoded.
2. Add a translator comment where context, grammar, or argument meaning is unclear.
3. Follow existing extraction style. When no convention exists, use inline localization for short one-off UI text or file-local `String` helpers for repeated/resolved strings. Helper extraction is a style choice, not an Apple requirement.
4. Preserve the catalog’s existing keys and translations. Avoid renaming keys solely to follow an example.
5. Run the documented extraction/build command and inspect the catalog diff. Some repositories provide `make build/package PACKAGE=<PackageName>` or `make build/app`; these are project targets, not standard SwiftPM commands.
6. Add plural variations using Xcode’s catalog editor or carefully editing the existing schema. Configure all categories required by each locale; English commonly uses `one` and `other`. Retain the actual extracted integer placeholder instead of guessing its width.
7. Verify representative zero, one, and multiple counts, interpolation order, long translations, and the owning bundle as relevant. Report extraction/build checks actually run.

For a phrase key, choose grammatical source wording consistent with the existing catalog. A singular base phrase is an example convention, not a requirement for plural selection.

## File-local helpers

When the project uses extracted helpers:

```swift
extension String {
    fileprivate static var deleteMessageButton: String {
        String(localized: "Delete Message", comment: "Button that deletes a message.")
    }

    fileprivate static func peopleCount(_ count: Int) -> String {
        String(localized: "\(count) people", comment: "Number of people; configure plural variations.")
    }
}
```

Use the resource-owning bundle where needed. A computed property resolves on each access; `static let` caches the first result. Choose according to the app’s language-change behavior. Keep helper visibility, ordering, and formatting consistent with the file.

## Reference Map

Read only the examples needed for the requested change, adapting their optional helper/key conventions and package bundle:

- [Simple strings](references/implementation-examples.md#simple-strings): fixed UI text.
- [Strings with parameters](references/implementation-examples.md#strings-with-parameters): interpolation.
- [Mixed properties and functions](references/implementation-examples.md#mixed-properties-and-functions): reusable members.
- [Strings with plurality](references/implementation-examples.md#strings-with-plurality): extraction and plural catalog entries.
- [Legacy pattern](references/implementation-examples.md#legacy-pattern): optional modernization of NSLocalizedString.

Before finishing, confirm the bundle, extraction, keys, plural categories, and language-resolution behavior match the project.

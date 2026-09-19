---
name: localizing-strings
description: "Localize Apple-platform UI strings with String(localized:) and string catalogs. Use for new user-facing text, hardcoded-string extraction, plurals, or localization bundles."
---

# String Localization

Extract hardcoded string literals from SwiftUI and UIKit code into properly localized `String` extensions following modern localization conventions.

## Key Format

Use the actual user-facing phrase as the localization key. Dot-separated identifiers make string catalogs harder to review and provide no context to translators:

```swift
// ✅ Phrase as key — readable in Localizable.xcstrings
String(localized: "Message Will Be Deleted", bundle: .module, comment: "...")

// ❌ Dot-separated identifier — opaque to translators
String(localized: "alert.deleteTitle", bundle: .module, comment: "...")
```

## Extraction Requirement

Extract `String(localized:...)` calls into a `fileprivate extension String` rather than leaving them inline. This keeps view bodies focused on layout and makes localized strings reusable within the file:

```swift
// ❌ Inline in view body — noisy and non-reusable
Text(String(localized: "Delete Message", bundle: .module, comment: "Button title"))

// ✅ Extracted to extension — clean call site
Text(.deleteMessageButton)

// In extension:
extension String {
    fileprivate static let deleteMessageButton = String(
        localized: "Delete Message",
        bundle: .module,
        comment: "Button title for deleting a message."
    )
}
```

## What to Localize

Only localize strings displayed to end users. Developer-facing text should remain as plain string literals.

**Localize:** UI text, labels, button titles, user-facing messages, prompts, placeholders, error messages shown to users, accessibility labels and hints, tooltips and help text.

**Do not localize:** Log messages, assertions, fatal errors, precondition failures, programming errors, debug strings, code comments, test strings (including `#Preview` blocks).

## Process

1. **Identify hardcoded strings** in the current file or selection that should be localized (UI text, labels, messages, placeholders, etc.)

2. **Create static properties/functions** in a `fileprivate extension String`:
   - Place after all extensions on the file's primary type, sorted lexicographically with other type extensions
   - Use `String(localized:bundle:comment:)` initializer
   - Set `bundle: .module` (required)
   - Write a descriptive but terse comment explaining context and usage
   - Name properties/functions using camelCase with clear semantic meaning
   - For strings with counts, use **singular variants** (e.g., "\(count) person" not "people")
   - Sort properties lexicographically, then functions lexicographically (properties before functions)
   - Add one empty line between each property/function
   - No documentation comments on properties/functions

3. **Replace call sites** with implicit member syntax (e.g., `label.text = .messageStatusFailed`)

4. **Build the package** to auto-generate `Localizable.xcstrings` entries:
   ```bash
   make build/package PACKAGE=<PackageName>
   ```

   If the package build doesn't generate the entries, try building the full app:
   ```bash
   make build/app
   ```

5. **Configure plurality** (if applicable):
   - Locate the newly created entries in `Localizable.xcstrings`
   - For strings with integer parameters, add plural variations:
     - `"one"`: singular form
     - `"other"`: plural form
   - Edit the JSON directly to add the `"localizations"."en"."variations"."plural"` structure

6. **Format constraints**:
   - LINE WRAP AT 120 CHARACTERS
   - KEEP COMMENTS ON ONE LINE WHEN POSSIBLE
   - Use proper grammar (incomplete sentences allowed for terseness)
   - Maintain lexicographic ordering

## Rules

- Only localize user-facing application strings; do not localize logs, assertions, fatal errors, or developer-facing diagnostics
- Use `bundle: .module` so the string catalog resolves from the correct Swift package
- Use the actual phrase as the key (e.g., `"Delete Message"`) for translator readability, not dot-separated identifiers (e.g., `"alert.delete"`)
- Extract to `fileprivate extension String`; do not leave `String(localized:...)` inline in views
- Place `extension String` after extensions on the file's primary type, sorted lexicographically with other type extensions
- Sort properties before functions; sort each group lexicographically within the extension
- Use implicit member syntax at call sites when type context allows (e.g., `.deleteMessageButton`)
- Do not add documentation comments to the static properties/functions — the `comment:` parameter serves that purpose
- Do not localize strings in test files or `#Preview` blocks
- Keep `comment:` values descriptive but terse
- One empty line between each property/function definition
- **For strings with plurality**: extract using the singular variant in Swift code, build to auto-generate the catalog entry, then edit `Localizable.xcstrings` directly to add plural variations (one, other, etc.)

## Reference Map

Read only the examples needed for the requested localization change:

- [Simple strings](references/implementation-examples.md#simple-strings): extract fixed UI text.
- [Strings with parameters](references/implementation-examples.md#strings-with-parameters): preserve interpolation.
- [Mixed properties and functions](references/implementation-examples.md#mixed-properties-and-functions): order reusable members.
- [Strings with plurality](references/implementation-examples.md#strings-with-plurality): build and edit plural catalog entries.
- [Legacy pattern](references/implementation-examples.md#legacy-pattern): migrate NSLocalizedString.

Before finishing, check the extraction and catalog changes against the Rules above.

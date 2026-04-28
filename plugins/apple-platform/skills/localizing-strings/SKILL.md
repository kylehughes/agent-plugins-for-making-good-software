---
name: localizing-strings
description: Localizes user-facing strings in Apple-platform software using String(localized:) extensions, bundle configuration, and Localizable.xcstrings string catalogs. Use when writing UI code with user-facing strings, extracting hardcoded strings, implementing string extensions, working with text displayed to users in SwiftUI/UIKit, migrating from NSLocalizedString, setting up pluralization, or managing i18n/l10n in Swift packages.
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

## Examples

### Simple strings

#### Before
```swift
label.text = "Failed to send"
textField.placeholder = "Enter message…"
```

#### After
```swift
label.text = .messageStatusFailed
textField.placeholder = .messageComposerInputPlaceholder

// At appropriate place in the file:
extension String {
    fileprivate static let messageComposerInputPlaceholder = String(
        localized: "Enter message…",
        bundle: .module,
        comment: "Placeholder text for the message composer text field, before a message has been entered."
    )

    fileprivate static let messageStatusFailed = String(
        localized: "Failed to send",
        bundle: .module,
        comment: "Error message displayed when a message fails to send to the server."
    )
}
```

### Strings with parameters

#### Before
```swift
label.text = "Seen by \(count) people"
titleLabel.text = "\(userName) sent a message"
```

#### After
```swift
label.text = .messageSeenBy(count: count)
titleLabel.text = .userSentMessage(userName: userName)

// At appropriate place in the file:
extension String {
    fileprivate static func messageSeenBy(count: Int) -> String {
        String(
            localized: "Seen by \(count) people",
            bundle: .module,
            comment: "Label showing how many people have seen a message; count is the number of people who have seen it."
        )
    }

    fileprivate static func userSentMessage(userName: String) -> String {
        String(
            localized: "\(userName) sent a message",
            bundle: .module,
            comment: "Notification text indicating a user sent a message; userName is the name of the user who sent it."
        )
    }
}
```

### Mixed properties and functions

#### Before
```swift
label.text = "Failed to send"
statusLabel.text = "Sent \(timeAgo) ago"
```

#### After
```swift
label.text = .messageStatusFailed
statusLabel.text = .messageSentTime(timeAgo: timeAgo)

// At appropriate place in the file:
extension String {
    // Properties come first, sorted lexicographically
    fileprivate static let messageStatusFailed = String(
        localized: "Failed to send",
        bundle: .module,
        comment: "Error message displayed when a message fails to send to the server."
    )

    // Functions come after properties, sorted lexicographically
    fileprivate static func messageSentTime(timeAgo: String) -> String {
        String(
            localized: "Sent \(timeAgo) ago",
            bundle: .module,
            comment: "Label showing when a message was sent; timeAgo is a relative time string like '5 minutes'."
        )
    }
}
```

### Strings with plurality

When dealing with plurality (e.g., "1 person" or "2 people"), **use the singular variant** in the localized string, then automatically configure the plural variations in the string catalog.

#### Before
```swift
label.text = "\(count) people"
```

#### After - Step 1: Add localized string with singular variant
```swift
label.text = .messageSeenByCount(count: count)

// At appropriate place in the file:
extension String {
    fileprivate static func messageSeenByCount(count: Int) -> String {
        String(
            localized: "\(count) person",
            bundle: .module,
            comment: "Label showing how many people have seen a message; count is the number of people."
        )
    }
}
```

#### Step 2: Build the package to auto-generate catalog entry
```bash
make build/package PACKAGE=<PackageName>
```

If the package build doesn't generate the entry, try building the full app:
```bash
make build/app
```

This creates the base entry in `Localizable.xcstrings` with the singular variant.

#### Step 3: Add plural variations to Localizable.xcstrings

Find the newly created entry and add plural variations:

```json
"%lld person" : {
  "comment" : "Label showing how many people have seen a message; count is the number of people.",
  "localizations" : {
    "en" : {
      "variations" : {
        "plural" : {
          "one" : {
            "stringUnit" : {
              "state" : "translated",
              "value" : "%lld person"
            }
          },
          "other" : {
            "stringUnit" : {
              "state" : "translated",
              "value" : "%lld people"
            }
          }
        }
      }
    }
  }
}
```

**Important**: After adding the localized string to Swift code, ALWAYS:
1. Build the package (or app if needed) to generate the catalog entry
2. Edit `Localizable.xcstrings` directly to add plural variations

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

## Legacy Pattern

You may encounter older code using `NSLocalizedString`. When refactoring, convert to the modern pattern:

```swift
// ❌ Legacy — NSLocalizedString
let text = NSLocalizedString(
    "Failed to send",
    bundle: .module,
    comment: "Error message when sending fails"
)

// ✅ Modern — String(localized:) in fileprivate extension
extension String {
    fileprivate static let messageStatusFailed = String(
        localized: "Failed to send",
        bundle: .module,
        comment: "Error message when sending fails."
    )
}
```

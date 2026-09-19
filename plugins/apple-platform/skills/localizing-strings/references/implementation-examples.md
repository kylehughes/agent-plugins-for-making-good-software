# Localization implementation examples

Read the section matching the current task.

## Contents

- [Simple strings](#simple-strings)
- [Strings with parameters](#strings-with-parameters)
- [Mixed properties and functions](#mixed-properties-and-functions)
- [Strings with plurality](#strings-with-plurality)
- [Legacy pattern](#legacy-pattern)

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

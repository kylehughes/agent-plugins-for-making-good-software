# Localization implementation examples

Read the section matching the current task. The helper extraction, phrase keys, and singular base wording below are optional conventions; preserve the repository’s established pattern. These Swift examples assume a Swift package target with localized resources and `Bundle.module`; adapt the bundle for app or framework targets as described in [Scope and assumptions](../SKILL.md#inspect-before-editing).

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

When dealing with plurality (e.g., "1 person" or "2 people"), **use the singular variant** in the localized string, then configure the plural variations in the string catalog.

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

#### Step 2: Build with string extraction enabled
Use the repository's documented extraction/build workflow. The following commands are examples for projects that provide these Make targets:

```bash
make build/package PACKAGE=<PackageName>
```

If that project's package build does not generate the entry, try its app build:
```bash
make build/app
```

Verify that extraction created the base entry in `Localizable.xcstrings` with the singular variant. If these Make targets are absent, use the project's Xcode scheme or extraction workflow.

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

After adding the localized string, run the project’s extraction workflow and inspect the catalog entry. Configure plural variations in Xcode or edit the existing JSON schema carefully. The English example shows `one` and `other`; other locales can require additional categories.

## Legacy Pattern

You may encounter older code using `NSLocalizedString`. When modernization is within scope and deployment targets support it, the equivalent modern pattern is:

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

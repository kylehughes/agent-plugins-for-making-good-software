---
name: presenting-ios-modals
description: "Build or review SwiftUI and UIKit modal sheets: navigation chrome, close/cancel/done actions, detents, and dismissal. Use for modal presentation, not ordinary navigation or general visual styling."
---

# Presenting iOS Modals

Use this alongside your SwiftUI or UIKit implementation skills when a screen is presented modally, especially when it has a navigation bar, a close button, a save/done action, or sheet detents.

## Sources

Current Apple guidance:

- [Toolbars](https://developer.apple.com/design/human-interface-guidelines/toolbars)
- [Modality](https://developer.apple.com/design/human-interface-guidelines/modality)
- [Sheets](https://developer.apple.com/design/human-interface-guidelines/sheets)

## Navigation Chrome

Use the real navigation bar for modal chrome whenever the presentation needs a title, close/cancel
button, primary action, or future back button. Prefer a `UINavigationController`-based modal container
for new modal flows so pushed steps, back navigation, and nested presentations compose naturally.

Do not draw an in-content header to replace a navigation bar. A custom header is only appropriate for a
surface that truly has no navigation bar, such as a compact custom picker. If that header contains a
close affordance, keep it on the leading side.

## Button Roles

Pick the button by role before choosing placement:

- **Close / Cancel**: Dismisses the modal surface. Put it in the leading cancellation slot.
- **Done / Save / Submit**: Completes or commits the task. Put the primary completion action on the trailing side.
- **Back**: Navigates to the previous step in a hierarchy. Do not use Back to dismiss a sheet.

Avoid showing Back, Close/Cancel, and Done together. Multi-step sheets can vary controls by step, but
each step should have one clear escape path and one clear completion path when completion is available.

If dismissal can lose user-generated content, guard both the close button and interactive dismissal with
the same confirmation path.

## Implementation

SwiftUI modal close:

```swift
@Environment(\.dismiss) private var dismiss

// …

.toolbar {
    ToolbarItem(placement: .cancellationAction) {
        Button(String(localized: "Close")) {
            dismiss()
        }
    }
}
```

UIKit modal close:

```swift
navigationItem.leftBarButtonItem = UIBarButtonItem(
    systemItem: .close,
    primaryAction: UIAction { [weak self] _ in
        self?.dismiss(animated: true)
    }
)
```

Pair a leading close/cancel with a trailing completion action when the task has an explicit commit:

```swift
ToolbarItem(placement: .confirmationAction) {
    Button(String(localized: "Save")) {
        viewModel.save()
    }
}
```

```swift
navigationItem.rightBarButtonItem = UIBarButtonItem(
    title: String(localized: "Save"),
    style: .done,
    target: self,
    action: #selector(saveButtonTapped)
)
```

## Sheet Size

Choose detents by task shape:

- Use medium + large when progressive disclosure helps: the useful first slice fits at medium height,
  and expansion reveals more detail.
- Use large-only or full-screen when people need room to create content, compare details, search broadly,
  or complete a prolonged flow.
- Show the grabber when a sheet has multiple detents.
- Support swipe-to-dismiss unless the current state requires confirmation or the task must stay visible.
- Prefer form or page sheet presentation on iPadOS for modal tasks scoped to the current context.

Configure sheets through `UISheetPresentationController` (or SwiftUI's `presentationDetents` family), and
centralize the configuration — detents, grabber state, edge attachment, undimmed behavior,
interactive-dismissal policy, and background — in one shared site per app rather than repeating it at
every call site. One-off per-controller configuration is where inconsistent chrome and dismissal behavior
come from.

Edge-attached sheets default to full width. Set `widthFollowsPreferredContentSizeWhenEdgeAttached: true` only
when a compact-height sheet should intentionally narrow to a nonzero preferred content width.

For content-sized sheets — a custom detent that resolves to the content's natural height — add `.large()`
or another expandable detent only when the flow benefits from expansion, and let the grabber default
follow whether expandable detents exist. Handle keyboard-aware sizing in the shared configuration site,
not per feature.

When hosting SwiftUI content in a content-sized sheet, the hosting controller owns vertical scrolling so
the detent can measure the content's natural height; do not root the hosted content in another
`ScrollView`, `List`, or vertically greedy `maxHeight: .infinity` frame.

Leave modal navigation chrome to UIKit unless the feature has a specific chrome treatment.

## Review Checklist

- Close/Cancel is leading; Done/Save/Submit is trailing.
- Back only navigates within a hierarchy.
- A modal with possible data loss confirms dismissal from every dismissal path.
- The screen uses navigation-bar chrome unless a custom header is truly necessary.
- The sheet size matches task complexity and shows a grabber when it has multiple detents.

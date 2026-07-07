# Parameters and Body Ordering

This reference covers semantic ordering of parameters and the narrow cases where statements inside function, initializer, and closure bodies may be safely sorted.

## Function and Initializer Parameters

Do not apply lexicographic ordering to function parameters, initializer parameters, closure parameters, tuple elements used as API shape, or result-builder child order.

Parameters should be ordered semantically based on role and relationships:

1. Identity: `id` and identifiers typically come first.
2. Related groups: keep conceptually related parameters together, such as `firstName`, `lastName`, `fullName`.
3. Primary data: the main subject/content being operated on.
4. Configuration: settings that modify behavior.
5. Dependencies: required collaborators and services.
6. Optionals/defaulted parameters: values with sensible defaults.
7. Closures: completion handlers, callbacks, and builder closures go last.

When parameters have no clear semantic relationship, use lexicographic ordering only as a tiebreaker.

```swift
// ✅ Good: semantic parameter ordering.
init(
    id: UUID,
    firstName: String,
    lastName: String,
    fullName: String,
    profilePhotoURL: URL?,
    completion: @escaping () -> Void
)

func send(
    _ content: String,
    with attachments: [Attachment],
    isImportant: Bool,
    completion: @escaping (Result) -> Void
) async

// ❌ Bad: lexicographic parameter ordering overrides semantics.
init(
    completion: @escaping () -> Void,
    firstName: String,
    fullName: String,
    id: UUID,
    lastName: String,
    profilePhotoURL: URL?
)
```

## Ordering Inside Function, Initializer, and Closure Bodies

Inside executable bodies, sort only contiguous independent statements.

Safe targets for sorting:

- Independent `let` / `var` declarations, alphabetical by declared identifier.
- Independent assignment/configuration statements, first by receiver name, then by property/method name.
- Independent array or dictionary literal elements when order is not semantically observed.
- Constraint lists such as `NSLayoutConstraint.activate([...])`, sorted by primary item/receiver, then anchor/attribute, then relation.
- Test fixture declarations when no setup sequence is required.

Never sort across:

- Data dependencies or first-use dependencies.
- Side effects, `await`, `try`, `defer`, locking, transactions, animations, notifications, logging, metrics, or lifecycle calls unless independence is obvious.
- `guard`, `if`/`else`, `switch`, `catch`, `defer`, loops, task groups, or cancellation handlers.
- Result builders, SwiftUI `body` child views, `VStack`/`HStack`/`ZStack` contents, menus, table/collection sections, navigation routes, toolbar items, accessibility order, or any UI sequence.
- Arrays used as displayed data, ordered commands, ordered validation steps, ordered middleware, ordered tests, or ordered fallback chains.

```swift
// ✅ Correct: independent declarations and independent assignments are sorted.
func setupUI() {
    let backButton = UIButton()
    let headerLabel = UILabel()
    let subtitleLabel = UILabel()

    backButton.setTitle("Back", for: .normal)
    headerLabel.text = "Welcome"
    subtitleLabel.text = "Please sign in"
}

// ✅ Correct: dependencies preserve original order.
func processUser() {
    let user = fetchUser()
    let name = user.name
    let validated = validate(name)

    updateUI(with: validated)
}
```

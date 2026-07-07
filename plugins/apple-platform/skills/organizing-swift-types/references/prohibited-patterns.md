# Prohibited Patterns

Reference for organizational patterns to remove from Swift files: MARK comments, organizational extensions, unnecessary self, and constants namespaces.

## Prohibited Patterns

### No MARK Comments

Do not add `// MARK:`, `// MARK: -`, section headers, lifecycle banners, protocol banners, or visual separators.

```swift
// ❌ BAD
// MARK: - UICollectionViewDataSource

// ❌ BAD
// MARK: Private Helpers
```

Deterministic file layout and symbol ordering replace navigational comments. MARK comments become stale and encourage organizational extensions.

Explanatory comments and documentation comments are still allowed when they explain non-obvious behavior, public API, workarounds, or availability fallbacks. Do not use comments as structure.

### No Organizational Extensions

An extension is organizational when it exists only to group members that could be written in the primary declaration. Organizational extensions are prohibited.

```swift
// ❌ BAD
extension ProfileViewController {
    private func configureView() { }
}

// ❌ BAD
private extension ProfileViewController {
    func bind() { }
}

// ❌ BAD
extension ProfileViewController {
    @objc private func didTapSaveButton() { }
}
```

Move ordinary properties, initializers, lifecycle overrides, actions, and helper methods into the primary declaration.

```swift
// ✅ GOOD
final class ProfileViewController: UIViewController {
    override func viewDidLoad() {
        super.viewDidLoad()
        configureView()
        bind()
    }

    @objc private func didTapSaveButton() { }

    private func bind() { }

    private func configureView() { }
}
```

### No Unnecessary `self`

Use `self` only when required by Swift or when it materially changes capture semantics.

Required or appropriate cases include:

- Disambiguating an instance member from a parameter or local variable with the same name.
- Satisfying Swift's explicit-self requirement in escaping closures.
- Working with weak/unowned captures where `self` must be explicit before rebinding.
- Referring to `Self`/`self` as a value or type where the language requires it.

```swift
// ❌ BAD
init(name: String) {
    self.name = name
    self.isActive = true
    self.configureDefaults()
}

// ✅ GOOD
init(name: String) {
    self.name = name
    isActive = true
    configureDefaults()
}
```

In closures, be explicit only as long as necessary.

```swift
// ✅ GOOD
loader.load { [weak self] result in
    guard let self else { return }
    handle(result)
}
```

Do not use `self.` for symmetry, style, or visual scanning.

### No Constants Namespaces

Do not introduce local namespace buckets for constants.

```swift
// ❌ BAD
private enum Constants {
    static let dotDiameter: CGFloat = 4
    static let numberOfDots = 3
}

// ❌ BAD
private enum Metrics {
    static let avatarSize: CGFloat = 40
}
```

Use file-scoped primitive constant extensions instead, as described below.

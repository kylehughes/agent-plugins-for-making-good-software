# Formatting and Comments

This reference covers required multi-line brace formatting and how comments, MARKs, and documentation interact with reordering.

## Formatting Enforcement

Always use multi-line formatting for braced constructs. Do not use single-line braced forms.

Use this:

```swift
var isValid: Bool {
    !email.isEmpty
}

guard isValid else {
    return
}

let handler = {
    refresh()
}
```

Do not use this:

```swift
var isValid: Bool { !email.isEmpty }

guard isValid else { return }

let handler = { refresh() }
```

Single-statement bodies are acceptable only when the braces remain multi-line.

## Comments, MARKs, and Documentation

- Move documentation comments and attached comments with the declaration they document.
- Do not let `// MARK:` sections override the canonical ordering rules.
- Remove or update stale `// MARK:` headings if reordering makes them inaccurate.
- Do not add new `// MARK:` sections merely to justify a noncanonical order.
- Preserve generated-code comments, copyright headers, lint directives, formatter directives, and warning-suppression comments exactly unless explicitly asked to edit them.

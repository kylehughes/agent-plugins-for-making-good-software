---
name: organizing-swift-types
description: Defines conventions for organizing iOS Swift types across a deployment span from older minimum targets through current and beta SDKs. Use when writing or editing Swift type declarations, choosing access control, ordering modifiers, deciding whether an extension is legitimate, placing protocol conformances, organizing nested types, handling file-scoped constants, applying availability guards, placing previews, or removing prohibited organizational patterns such as MARK comments, organizational extensions, unnecessary self, global constants, and Constants namespaces.
---

# Swift Type Organization Conventions

## Scope and Assumptions

These conventions apply to Swift source for iOS projects.

- Target Swift 6.3. Do not write compatibility branches for older Swift compilers or older Swift language syntax.
- Assume Swift 6 language mode unless project settings explicitly prove otherwise. Do not optimize style for Swift 5-era limitations.
- Target iOS 16 as the minimum runtime unless a file or target explicitly states a higher minimum.
- Support the latest stable iOS 26 SDKs. Treat iOS 27 as beta: do not use iOS 27-only APIs, beta SDK behavior, or Swift 6.4+ syntax unless the user explicitly asks for beta code.
- A newer compiler or SDK does not make newer OS APIs available on iOS 16. Guard every post-iOS-16 API at runtime or isolate it behind an available declaration.
- This skill governs organization. For detailed symbol ordering inside a declaration, apply the `ordering-symbols` skill when available. If that skill is unavailable, use deterministic ordering: compiler-required declarations first, then lexicographic order by symbol name. Never compensate for missing ordering rules with MARK comments.

When a rule here conflicts with compiler correctness, compiler correctness wins. Make the smallest possible exception and preserve the rest of the structure.

## Required Outcome

Every generated or edited Swift file should converge toward this shape:

1. Imports.
2. Primary type declaration, including synthesized conformances.
3. Custom protocol conformance extensions, one protocol per extension, sorted lexicographically by protocol name.
4. Legitimate constrained extensions for the primary type, sorted lexicographically by constraint text.
5. Nested type extensions, one nested type per extension, sorted lexicographically by nested type name, with each nested type's subtree completed before moving to the next sibling.
6. Static constants extensions for non-primitive types, when the constants are true type API.
7. File-scoped primitive constant extensions using `fileprivate static let`.
8. `#if DEBUG` previews last.

The file should not contain MARK comments, organizational extensions, unnecessary `self`, global implementation constants, `private enum Constants`, `private struct Constants`, `private enum Metrics`, or equivalent namespace buckets.

## Editing Procedure for Agents

When editing Swift under this skill:

1. Identify the primary type and minimum deployment target.
2. Collapse organizational extensions into the primary declaration.
3. Keep synthesized, marker, and empty conformances on the primary declaration.
4. Move custom conformance implementations into one-protocol extensions.
5. Move nested types into one-nested-type extensions and complete each nested subtree before moving to siblings.
6. Replace `private enum Constants`, `private struct Constants`, global implementation constants, and type-polluting private static constants with `fileprivate static let` primitive extensions unless the constant is true type API.
7. Remove MARK comments and visual section comments.
8. Remove unnecessary `self` while preserving required disambiguation and capture semantics.
9. Add or preserve iOS availability guards for every post-iOS-16 API.
10. Place previews last inside `#if DEBUG`.

Do not create churn outside the touched file unless moving a legitimate external-type extension or top-level production type into its own file is necessary for correctness or explicitly requested.

## Reference Map

Load only the reference relevant to the task:

- [Access control and modifiers](references/access-control-and-modifiers.md): access level selection, `final`, and declaration modifier ordering.
- [Availability and version spanning](references/availability-and-version-spanning.md): guarding post-iOS-16 APIs across the deployment span.
- [Prohibited patterns](references/prohibited-patterns.md): MARK comments, organizational extensions, unnecessary `self`, and constants namespaces to remove.
- [Primary declaration and conformances](references/primary-declaration-and-conformances.md): what belongs in the primary type declaration and how to organize synthesized, custom, and retroactive conformances.
- [Extensions and nested types](references/extensions-and-nested-types.md): when an extension is legitimate and how to structure nested type subtrees.
- [Constants, file structure, and previews](references/constants-file-structure-and-previews.md): file-scoped constant extensions, overall file ordering, and preview placement.
- [Complete shape example](references/complete-shape-example.md): a full worked example applying every rule to one file.

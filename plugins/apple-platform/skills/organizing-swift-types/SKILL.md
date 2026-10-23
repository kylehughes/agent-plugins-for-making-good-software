---
name: organizing-swift-types
description: "Organize Swift types, conformances, extensions, access control, and files. Use proactively when adding or restructuring declarations; apply repository conventions before the suggested layout."
---

# Organizing Swift Types

## Scope and Assumptions

Use these suggested conventions for Swift source when the repository has no established layout. Repository style wins, including MARK comments, organizational extensions, nested types, and constants namespaces. These are layout choices, not platform restrictions; apply them only within the requested surface.

- Inspect and preserve the project’s compiler, language mode, deployment targets, and SDK. Do not assume iOS 16 or Swift 6 when settings are unknown.
- Gate newer APIs relative to the affected target’s deployment minimum; organization alone does not justify changing build settings.
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
9. Preserve availability guards required by the actual deployment targets.
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

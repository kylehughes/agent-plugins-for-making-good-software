# Receipt fixture

This is an offline Swift 6 command-line project. `Sources/Quantity.swift` is the
legacy source filename; `Tests/main.swift` is its only client. There are no
external packages. Receipt output preserves input order and duplicates, drops
only empty names, and prefixes every retained name with `Item: `.

`sh Tools/compile.sh` compiles the complete source/test graph without running it.
`sh Tools/project-proof.sh` compiles and runs the focused project checks.
Keep compiler products outside the working tree and implementation edits within
`Sources` and `Tests`. Preserve the output contract and do not add dependencies
or verification infrastructure.

# Cart fixture

This is an offline Swift 6 command-line project. `Sources/Quantity.swift` and
`Tests/main.swift` are the complete dependent graph; there are no external packages.
Preserve existing valid inputs and the keyed saved-cart representation.

`sh Tools/compile.sh` compiles the source and all test clients without running them.
`sh Tools/project-proof.sh` compiles and runs the focused project checks.
Keep compiler products outside the working tree. Do not add dependencies or
verification infrastructure. Keep implementation changes in `Sources` and `Tests`.

For change-set hardening, project proof belongs to the later project ship gate.
Leave that command pending in the handoff; a compile-only checkpoint is not a
passing test run. Audit workers stay read-only and do not compile or run checks.

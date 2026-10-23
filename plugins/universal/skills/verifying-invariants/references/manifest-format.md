# Invariant manifest format

`validate_invariants.py` checks that an invariant manifest is structurally complete and that each declared local reference exists. It does not execute commands, inspect symbols, run tests, or prove any invariant. A successful exit status means only that the manifest is well-formed against the selected project root.

Resolve the checker from the installed skill directory; the manifest and root arguments identify the project to inspect:

```sh
python3 /absolute/path/to/verifying-invariants/scripts/validate_invariants.py \
  path/to/invariants.json --root path/to/project
```

Add `--json` for stable machine-readable output. The output is one JSON object with `valid` and a path-, code-, and message-sorted `diagnostics` array. Exit status is `0` for a well-formed manifest and `1` for a missing, invalid, or nonconforming manifest.

## Root object

The root object has exactly these fields:

```json
{
  "schema_version": 1,
  "invariants": []
}
```

`invariants` must contain at least one invariant. `schema_version` must be the integer `1`; booleans and floating-point values are rejected. Unknown fields are rejected at every object level so spelling mistakes do not silently become metadata. Duplicate JSON object keys are rejected rather than silently taking the last value.

## References

Every reference is an object with a project-relative `path` and an optional non-empty `symbol`:

```json
{ "path": "Sources/Store.swift", "symbol": "Store.commit" }
```

Paths are resolved under `--root`, must not be absolute or contain `..`, and must exist. A `symbol` is descriptive linkage only; the validator deliberately does not parse source code to guess whether it exists. Use `{ "path": "." }` when the relevant authority, scope, or artifact is the whole project.

## Invariant entries

Each item in `invariants` has exactly these required fields:

```json
{
  "id": "unique-invariant-id",
  "statement": "The property that must remain true.",
  "kind": "structural",
  "scope": { "references": [{ "path": "Sources" }] },
  "authority": {
    "description": "Where this requirement comes from.",
    "references": [{ "path": "Documents/contract.md" }]
  },
  "boundaries": {
    "surfaces": ["construction", "transition"],
    "exclusions": ["What this invariant does not establish."]
  },
  "assumptions": [],
  "checks": []
}
```

`id`, `statement`, and every textual list member must be non-empty. Invariant IDs and check IDs are unique within their respective parent collections. `kind` is one of `structural`, `refined-value`, `transition`, or `external`.

`scope.references` identifies code or artifacts affected by the invariant. `authority` identifies the source that requires it and includes a non-empty human description. `boundaries.surfaces` is a non-empty list of lifecycle surfaces where the invariant applies: `construction`, `decoding`, `mutation`, `transition`, or `external`. `boundaries.exclusions` may be empty; it records claims intentionally outside the invariant. This separates affected lifecycle surfaces from a check's evidence limitations.

`assumptions` may be empty: an empty list explicitly means the manifest records no known assumptions. It must be non-empty when any check uses `formal-proof`.

## Checks

Each check has `id`, `method`, and `limitations`, plus at least one of `command` or `artifact`:

```json
{
  "id": "state-machine-search",
  "method": "transition-test",
  "command": "python3 Tools/check_transitions.py",
  "artifact": { "path": "Tools/explore.py", "symbol": "main" },
  "limitations": ["Does not exercise an external integration."]
}
```

Allowed methods are `static-analysis`, `compiler-rejection`, `boundary-test`, `property-test`, `transition-test`, `integration-test`, `artifact-inspection`, `manual-review`, `bounded-exploration`, and `formal-proof`. Choose the specific test method when it communicates the intended evidence; `static-analysis` remains available for analyzers that do not fit these categories. `limitations` may be empty; that means the author has recorded no known limitation, not that the check establishes a proof. Command text is metadata and is never executed by this validator.

`bounded-exploration` requires a non-empty `bounds.domain` description of the explored finite model. It may declare `resource_limits` when execution has a safety cap; allowed positive integer limits are `max_states`, `max_depth`, and `max_seconds`. A complete finite model does not need a depth cutoff.

```json
"bounds": {
  "domain": "All 12 states and their declared transitions",
  "resource_limits": { "max_states": 12 }
}
```

`formal-proof` requires a non-empty invariant `assumptions` list and an `implementation` reference on the check:

```json
{
  "id": "proof",
  "method": "formal-proof",
  "artifact": { "path": "Proofs/model.lean" },
  "implementation": { "path": "Sources/Store.swift", "symbol": "Store.commit" },
  "limitations": []
}
```

The manifest contains declared validation metadata. Execution reports belong in a separate, time-stamped system owned by the runner; do not add cached `verified`, pass/fail, timestamp, command-output, or report fields to this format. The validator also rejects unreadable manifests, invalid UTF-8, a non-directory `--root`, and references that resolve through a symlink outside `--root`.

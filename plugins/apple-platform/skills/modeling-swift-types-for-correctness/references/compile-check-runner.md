# Swift Compile-Check Runner

Use `scripts/swift_compile_checks.py` to preserve a high-value compiler rejection against a recorded Swift source snapshot. The runner uses only the Python standard library. It runs paired valid and invalid inputs with the same compiler arguments and can also build and execute runtime checks.

## Command Line

Run from the skill directory or pass an explicit manifest path:

```sh
python3 scripts/swift_compile_checks.py examples/compile-checks.json
python3 scripts/swift_compile_checks.py examples/compile-checks.json --json
python3 scripts/swift_compile_checks.py path/to/checks.json --swiftc /path/to/swiftc --timeout 45
```

Arguments:

- `manifest` defaults to `examples/compile-checks.json` beside the runner’s skill directory.
- `--swiftc PATH` selects the compiler. Without it, the runner uses `SWIFTC`, then searches `PATH`.
- `--timeout SECONDS` sets a finite positive timeout for each compiler or runtime process. The default is 30 seconds.
- `--json` writes the machine-readable report. The default report is intended for a person running the check.
- `--allow-unavailable` changes an unavailable toolchain from exit status 2 to a clearly labeled `SKIP` with exit status 0. It does not change the report status from `unavailable`.

Exit statuses:

| Status | Meaning |
|---|---|
| `0` | Every declared control and check passed, or the toolchain was unavailable and `--allow-unavailable` was explicit. |
| `1` | The manifest was invalid or a control, negative fixture, compiler invocation, or runtime check failed. |
| `2` | The compiler or required compiler version was unavailable. No compiler claim was checked. |

`scripts/check_examples.sh` is the compatibility entry point. It passes `--allow-unavailable` by default. `REQUIRE_SWIFTC=1 scripts/check_examples.sh` preserves unavailable status as a failure.

## Manifest Schema

The manifest is a closed JSON object. Unknown fields are errors so a misspelled setting cannot be silently ignored. Required string values must contain at least one non-whitespace character; values are validated without being rewritten.

```json
{
  "schema_version": 1,
  "minimum_swift_version": "6.3",
  "compiler_arguments": [
    "-emit-module",
    "-parse-as-library",
    "-swift-version",
    "6",
    "-strict-concurrency=complete"
  ],
  "support_sources": ["Sources/DomainTypes.swift"],
  "positive_controls": [
    {
      "name": "CorrectIdentifierDomain",
      "sources": ["Fixtures/CompilePassCorrectID.swift"]
    }
  ],
  "negative_fixtures": [
    {
      "name": "WrongIdentifierDomain",
      "sources": ["Fixtures/CompileFailWrongID.swift"],
      "positive_control": "CorrectIdentifierDomain",
      "diagnostic_markers": ["cannot convert value of type"]
    }
  ],
  "runtime_checks": []
}
```

Required top-level fields:

- `schema_version` is the JSON integer `1`. Booleans and floating-point values are rejected.
- `minimum_swift_version` is a dotted version at least `6.3`. A missing, unparseable, or older selected compiler is unavailable evidence.
- `compiler_arguments` is a nonempty string array. It must select the emit-module phase, must contain exactly one `-swift-version 6` pair, and must not contain `-typecheck`. Every positive and negative compilation receives these arguments.
- `support_sources` is a nonempty string array containing production sources shared by every positive control, negative fixture, and runtime build.
- `positive_controls` is a nonempty array of objects with a unique nonempty `name` and nonempty `sources`. A negative fixture is not run when its paired control fails.
- `negative_fixtures` is a nonempty array of objects with a unique nonempty `name`, nonempty `sources`, a declared `positive_control`, and nonempty `diagnostic_markers`.

`runtime_checks` is optional. Each entry has a nonempty `name`, nonempty `sources`, and optional `compiler_arguments`. Runtime arguments are separate because an executable build does not use the negative fixture’s emit-module arguments. A successful build is followed by execution of the temporary binary.

For a rejected fixture, every marker must occur in an actual parsed Swift `error:` message, and every parsed source error must match at least one declared marker. Marker text echoed in source context does not count. Prefer the shortest wording that identifies the intended type-system failure without matching unrelated errors.

## Paths and Module Linkage

Source paths are resolved relative to the manifest’s directory. Compiler and runtime processes also use that directory as their working directory. Relative paths embedded in `compiler_arguments`, such as an `-I` search path, therefore use the manifest directory as their base. Reported commands contain resolved source paths.

The shared-source form compiles `support_sources` and one control or fixture source into the same temporary module. Use it when the production source can be compiled directly without its full build system. The generated module name is derived from the check name and is intentionally unique per check.

To check a prebuilt production module, put `import ProductModule` in each control and fixture and provide the required `-I`, `-F`, SDK, target, or other search arguments in `compiler_arguments`. Prepare that module before invoking the runner. The runner does not build dependencies, infer SwiftPM or Xcode settings, or grant test-only access. A module-import check observes only the API visible under the supplied build and import settings.

Use the same linkage form for a negative fixture and its paired control. Mixing copied stand-in declarations into one side weakens the comparison and does not establish a claim about the production API.

## Reports and Limits

The JSON report contains these fields; the human report summarizes the same toolchain, snapshot, phase, results, and limitations:

- `status`: `pass`, `fail`, or `unavailable`.
- `phase`: the enforced emit-module ownership-checking phase.
- `toolchain`: selected compiler path, raw version output, and parsed version.
- `snapshot`: manifest path and SHA-256 digest plus a SHA-256 digest for every declared source.
- `inputs`: compiler arguments, support sources, controls, negative fixtures, and runtime checks.
- `results`: command, return status, reason, and diagnostics for each check.
- `limitations`: statements that bound the evidence.

A pass means the recorded compiler accepted each positive control, rejected each negative fixture for only its declared error markers, and completed any runtime checks. The runner also fails on compiler crashes, timeouts, unexpected acceptance, missing markers, unrelated or unparsed error diagnostics, and broken controls. Non-UTF-8 compiler output is retained with Unicode replacement characters instead of causing a traceback.

The report is evidence for the recorded source bytes, compiler, arguments, linkage, and misuse. It does not establish that every production target uses those settings or sources. It does not prove runtime validation, serialization, availability, synchronization, interop, security, ABI stability, or the absence of unchecked construction paths. Keep those claims tied to their own build, test, inspection, or operational evidence.

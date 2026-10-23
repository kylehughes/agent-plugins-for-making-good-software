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

## Scratch compiler checks

Keep allocation, cleanup registration, compilation, and execution in one tool command. Use a scoped temporary-directory API or register an exit trap immediately after allocation:

```sh
scratch_dir=$(mktemp -d) || exit 1
trap 'rm -rf -- "$scratch_dir"' EXIT
# Compile into "$scratch_dir", then run the check in this shell.
```

Keep scratch sources and binaries outside the project. Cleanup chained only after success does not cover compiler failure. Report compiler runs, tests, file changes, and cleanup only when completed tool results confirm them.

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

Source paths are resolved relative to the manifest’s directory. The runner reads the manifest and every declared source once, hashes those exact bytes, and gives each compiler invocation fresh temporary copies. Later checkout edits, deletion, renames, and symlink retargeting cannot change the compiled source snapshot. An invocation fails if its temporary sources are changed or removed before the compiler exits.

Compiler and runtime processes still use the manifest directory as their working directory. Relative paths embedded in `compiler_arguments`, such as an `-I` search path, therefore use the manifest directory as their base. Reported commands contain the temporary source paths used for that invocation. Source-path-sensitive behavior such as `#filePath`, along with compiler settings that match original source paths, observes the temporary paths; use the project’s normal build when original checkout paths are part of the behavior under test. Basenames are preserved, including the special behavior associated with `main.swift`.

The shared-source form compiles `support_sources` and one control or fixture source into the same temporary module. Use it when the production source can be compiled directly without its full build system. The generated module name is derived from the check name and is intentionally unique per check.

To check a prebuilt production module, put `import ProductModule` in each control and fixture and provide the required `-I`, `-F`, SDK, target, or other search arguments in `compiler_arguments`. Prepare that module before invoking the runner. The runner does not build dependencies, infer SwiftPM or Xcode settings, or grant test-only access. This also applies to `@testable import`: the imported module must already have been built with testing enabled. A module-import check observes only the API visible under the supplied build and import settings.

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

A pass means the recorded compiler accepted each positive control, rejected each negative fixture for only its declared error markers, and completed any runtime checks using fresh copies of the recorded bytes. The runner also fails on compiler crashes, timeouts, source mutation or removal during compilation, unexpected acceptance, missing markers, unrelated or unparsed error diagnostics, and broken controls. Non-UTF-8 compiler output is retained with Unicode replacement characters instead of causing a traceback.

The report is evidence for the recorded source bytes, compiler, arguments, linkage, and misuse. Prebuilt modules, SDK contents, compiler plugins, response files, and other dependencies named through compiler arguments remain external inputs; the report records their arguments but does not hash their bytes. It does not establish that every production target uses those settings or sources. It does not prove runtime validation, serialization, availability, synchronization, interop, security, ABI stability, or the absence of unchecked construction paths. Keep those claims tied to their own build, test, inspection, or operational evidence.

## Imported companion corpus

The separate `examples/compiler-corpus-map.json` maps the supplied companion's
89 indexed compiler cases and two runtime examples. Include it through the existing
entry point, or request a separate report, from the skill directory:

```sh
REQUIRE_SWIFTC=1 CHECK_SWIFT_COMPILER_CORPUS=1 scripts/check_examples.sh
python3 scripts/swift_compiler_corpus.py --report /tmp/swift-corpus-report.json
```

Use `--swiftc /path/to/swift-frontend` to select a compiler explicitly. Compilation
probes use SIL emission so ownership-flow diagnostics are checked. Runtime builds
use the colocated `swiftc` driver. The report separates default and experimental
cases and records effective arguments, input digests, diagnostics, exit codes, and
differences from the supplied results. It reuses the baseline runner's strict
diagnostic evaluator; an unrelated error, crash, or timeout cannot establish the
intended rejection.

When SDK declarations require a newer deployment target than the host default,
pass it explicitly for compile-only evidence, for example
`--compile-target arm64-apple-macosx27.0`. The runner applies that target identically
to positive controls and their paired negative cases and records it in
`shared_arguments`. Runtime builds omit the compile target, record their separate
arguments, and keep the compiler's host-compatible default because the resulting
binaries execute on the current host.

The supplied comparison report was produced with Swift 6.4.1 on Linux. A local
compiler must independently satisfy the declared cases and their controls; the
supplied report is not a substitute for that run. Read the current report before
claiming compatibility with another compiler or SDK. Accepted unsafe, effects,
and frontier probes are compilation-only. Only the two named runtime examples
are executed. Performance experiments are unsupported illustrations and are not
part of these acceptance counts.

## Included utilities and fixtures

- `scripts/audit_project.py`: inventories Swift/Xcode compatibility settings.
- `scripts/swift_compile_checks.py` and `swift_compiler_corpus.py`: run paired baseline fixtures and the imported corpus, with separate compiler/runtime evidence.
- `examples/compile-checks.json` and `compiler-corpus-map.json`: declare the baseline fixtures and 89 imported cases; corpus controls and experimental lanes remain explicit.
- `scripts/check_examples.sh`: compatibility entry point with optional skip and `REQUIRE_SWIFTC=1` behavior.
- `scripts/validate_skill.py`: validates metadata, links, evals, manifest wiring, and fixtures.
- `examples/CorePatterns.swift`, `CurrentSwiftPatterns.swift`, and `TrustStatePatterns.swift`: shared sources used by controls and misuse fixtures.
- `examples/CorePatternsRuntimeChecks.swift`: executable validation and `Codable` checks.
- `examples/CompilePass*.swift` and `CompileFail*.swift`: paired valid and invalid uses of the shared sources.
- `evals/trigger-evals.json` and `evals/quality-evals.md`: activation and response-quality scenarios.

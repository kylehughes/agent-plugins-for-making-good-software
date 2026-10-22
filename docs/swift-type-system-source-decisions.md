# Swift type-system source decisions

This maintainer record preserves archive-forensic decisions from the original source integration. It is not an operational dependency of the shipped plugin. The [integration ledger](swift-type-system-integration-map.json) retains original source URLs, paths, digests, and decisions; its source records are preserved; consolidation updates destinations to the current canonical owners.

Archive: `Swift_Type_System_Companion/`, dated 2026-10-18; supplied ZIP SHA-256 `4454c583ec5a9cc4dd80487ff19a9a2dc9925e5249588db8e4a06482bf35eb13`.

The archive is not included in this repository. The ledger preserves its identity
and citations; source-backed reproduction requires a separate copy matching that digest.

The decisions below were recorded during the 2026-10-19 source review. “Fresh” in this historical table means that review's primary-source inspection; “supplied” means archived reports. Neither label claims a new compiler run during the 2026-10-20 documentation consolidation.

## Conflict decisions and evidence limits

| Question | Decision | Evidence classification |
|---|---|---|
| Are `core_validation.json` and `core_validation_641.json` independent 6.4.0/6.4.1 evidence? | No. They are byte-identical (`aeef6ae6…` in the supplied checksum file) and contain no per-record compiler identity. Treat them as one supplied result set of unknown toolchain provenance. | Supplied; content identity observed locally; toolchain provenance unknown |
| Do the performance experiments prove no allocation, no locks, or semantic effects? | No. `performance_experiments/modeling_gap_validation.json` records typecheck, optimized SIL, and SIL with `-experimental-performance-annotations`. `noalloc_array` and `nolocks_mutex` already fail in optimized SIL without that flag; `effects_lie` compiles. The subdirectory README names 6.4.0 while the package README describes a 6.4.1 baseline; the report records neither compiler identity nor target, so its toolchain provenance is unknown. These are unsupported compile-only probes, not performance measurements. | Supplied report inspected; compiler/target unknown; no fresh compiler execution |
| Does the Swift 6.4 release blog prove SE-0532 APIs shipped? | No. The accepted proposal, implementation-status report, and supplied official-release probes say the scoped APIs were absent. Record the release-blog list as contradicted for those APIs. | Fresh primary decision/status plus supplied compiler evidence |
| Does the retained SE-0527 manuscript or Apple `UniqueArray` prose prove public `RigidArray` exists? | No. The steering-group acceptance decision declined it, and the supplied public-name probe rejects it. | Fresh primary decision plus supplied compiler evidence |
| Do accepted proposals or Linux SIL probes establish Apple deployment support? | No. Use Apple symbol documentation or the selected SDK interface. Mark the floor unknown when neither establishes it. | Evidence rule |
| Does compilation establish arbitrary correctness or liveness? | No. It establishes only the checked compiler rule for the exact source, phase, flags, and toolchain. Runtime validation, semantic laws, cleanup, progress, and exactly-once behavior need separate evidence. | Evidence rule |

During the original source integration, the companion archive was inspected as supplied; that review did not accept or rerun its compiler corpus or runtime suite. Its `release_matrix.json`, README, HTML catalog, saved reports, tagged checksums, and proposal links informed the conflict inventory. Primary-source status wins over descriptive archive prose, while supplied compiler outcomes remain explicitly scoped corroboration.

The performance interpretation also follows the freshly inspected [Swift underscored-attribute reference](https://github.com/swiftlang/swift/blob/main/docs/ReferenceGuides/UnderscoredAttributes.md#_effectseffectname): `_effects` supplies optimizer assumptions, and violating them can cause undefined behavior. The original [performance-annotation pitch](https://forums.swift.org/t/performance-annotations/54441) describes compiler diagnostics, not stable general effect types. Neither source turns the supplied probes into a latency, allocation-count, purity, or constant-time proof.


## Later verification and current ownership

[Goal 2 verification](swift-type-integration-verification.md) subsequently established all 89 imported compiler outcomes and 15 paired controls on Apple Swift 6.4 (`swiftlang-6.4.0.34.1`) from Xcode 27.1, with a compile-only macOS 27.0 target. Both imported runtime sources separately built and ran using the host-compatible default target. Those results do not repair the unknown compiler identity of the duplicate core reports or the performance report, establish iOS deployment support, or turn compilation into performance measurement.

The final behavioral selection contains five final-snapshot reruns and 19 unaffected earlier accepted runs. It is not a fresh 24-run matrix on the final snapshot. Read the verification report for attempts, settings, carry-forward rules, and limitations.

The shipped [feature status](../plugins/apple-platform/skills/modeling-swift-types-for-correctness/references/swift-feature-status.md) owns dated release/channel facts, feature availability, and operational evidence limits. Compatibility references own deployment and build principles and link there for the current snapshot. Historical release notes remain linked in the source index; compatibility guidance no longer presents Swift 6.3.2 as the current baseline.

## Previous compatibility reference snapshot

The following text preserves the former `writing-swift/references/swift-6.3.2.md` release survey. It was copied during the 2026-10-20 consolidation for historical upgrade/workaround research, not reverified as a current baseline. Its specific patch publication date and Xcode association are inherited claims, not new verification. Use the linked official release sources before relying on them.

## Swift 6.2 Baseline

Swift 6.2 introduced several capabilities that commonly affect modern code and migration decisions:

- Module-level default actor isolation, including default `MainActor` isolation for suitable targets.
- Caller-context execution for nonisolated async functions under the corresponding language behavior, plus `@concurrent`
  for work that must run independently of the caller's actor.
- `InlineArray` and `Span` for specialized storage and safe contiguous-memory access.
- Opt-in strict memory safety checking.
- Warning-control settings in SwiftPM.
- Named tasks for diagnostics and observability.
- Typed `NotificationCenter` messages and observation-related improvements on supported Apple platforms.
- Swift Testing exit tests, attachments, and raw-identifier test names.

Adopt these only when they solve a concrete problem and all supported platforms/toolchains permit them. In particular,
`Span`, ownership annotations, and strict memory-safety features are not routine replacements for ordinary collections.

## Swift 6.3 Additions

Swift 6.3 adds capabilities that may matter in specialized work:

- `@c` declarations and `@c @implementation` for direct C implementation/interoperability workflows.
- Module-qualified symbol selection with syntax such as `ModuleA::Type` when imported names collide.
- Additional optimization and implementation-only controls, including `@specialize`, `@inline(always)`, and
  `@export(implementation)`. Use such attributes only with measurements and compatibility review.
- Swift Build as a preview build engine surfaced through SwiftPM workflows.
- Prebuilt Swift Syntax support for shared macro implementation libraries and package traits inspection through
  `swift package show-traits`.
- Swift Testing warning-severity issues, explicit test cancellation, and image attachments.
- Experimental DocC Markdown output, per-page static HTML content, and code-block annotations such as `nocopy`, `highlight`,
  `showLineNumbers`, and `wrap`. Keep experimental flags confined to documentation pipelines that intentionally adopt them.
- Official Swift SDK support for Android and further Embedded Swift improvements.

Do not “modernize” existing code by introducing new syntax without a need. Newer constructs can raise the minimum compiler
version, complicate source compatibility, or obscure a simpler implementation.

## Swift 6.3.2 Patch Release

Swift 6.3.2 is a patch release published May 13, 2026. It includes targeted compiler, interoperability, SwiftPM,
Swift Testing, and SourceKit-LSP fixes. Xcode 26.5 contains Swift 6.3.2. On supported standalone installations, use the
repository's toolchain manager or `swiftly install 6.3.2` rather than replacing a shared toolchain ad hoc.

Notable fixes include C++23 header imports on Linux, `Bundle.module` access from outside `MainActor`, and Swift Testing exit
tests that produce no standard output or error. When one of these symptoms appears on an earlier 6.3 toolchain, verify it
under 6.3.2 before preserving a workaround in source.

Patch releases should be low-risk, but still run the full relevant build and test matrix. Compiler fixes can expose code
that previously compiled accidentally, and tooling fixes can alter diagnostics or indexing behavior.

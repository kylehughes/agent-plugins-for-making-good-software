---
name: auditing-ios-release-size
description: >
  Audits iOS release build size using the real distribution path, App Thinning, local
  binary and resource breakdowns, baseline comparison, optional size-analysis service
  reports, and issue-tracker follow-up capture. Use when investigating IPA size, install
  size, release binary size, App Thinning reports, embedded framework or resource bloat,
  size regressions, or recurring iOS size-budget work. Do not use for Debug or simulator
  build size except as an explicitly requested comparison.
---

# Auditing iOS Release Size

Use this skill to turn a build-size investigation into repeatable evidence and follow-up work. The goal is not to make a one-off report permanent; it is to preserve the process so future audits can start from known questions, measurements, and capture points.

## Principles

- Measure the real shipping path. Do not use Debug, simulator, or ad hoc build products unless the user explicitly wants a non-release comparison.
- Size is not one number. Report universal IPA size, representative thinned download size, representative thinned install size, extracted app bundle size, executable size, framework size, resource size, extension/plugin size, and dSYM size separately.
- Treat dSYMs and local analysis output as diagnostic artifacts. They are not shipped app payload unless the app bundle actually embeds them.
- Prefer evidence-backed follow-up issues over broad cleanup claims. Each follow-up needs an expected impact, risk, and validation path.
- Keep local audit directories and reports disposable unless the user asks for a committed tool or durable documentation. Do not add one-off audit output paths to `.gitignore`.

## Coordinate Skills

- Use the project's build, archive, and simulator conventions — or a build-tooling skill covering them, when one is available — rather than inventing commands.
- Use `writing-technical-prose` when writing durable Markdown or long-form issue summaries.
- Use `hardening-changes` only when the audit produces tracked code, build-system, documentation, or skill changes that should be reviewed.

## Discover The Shipping Path

Before measuring, identify the release path that actually creates the submitted artifact.

Record:

- Branch, commit, ticket, Xcode version, Swift version, minimum iOS version, and build date.
- Scheme, workspace or project, configuration, variant, destination, archive path, and export method.
- Whether the source of truth is a release-automation tool, a build-system target, raw `xcodebuild`, CI configuration, or App Store Connect output.
- App targets, notification extensions, widgets, plugins, and other embedded products.
- Package managers and major binary dependencies.
- Baseline source, if one exists: a previous release tag, main branch build, CI artifact, App Store Connect size report, or earlier audit.

If no reliable baseline exists, say that explicitly and establish this audit as a baseline instead of implying a regression.

## Build And Export

Use the same lane or command family the project uses for distribution whenever possible. If you must use a local command, keep the deviation explicit in the report.

Minimum outputs:

- Archive for the release configuration.
- Exported universal IPA using the selected distribution method.
- App Thinning report when available.
- Representative thinned IPA or app bundle for a common device class.

If App Store export does not generate useful thinning output locally, run a separate release-testing export with thinning enabled for all variants and label it as diagnostic. Do not confuse this diagnostic export with the submitted artifact.

## Measure The Payload

Capture these metrics from the exported and thinned artifacts:

- Universal IPA compressed size.
- Representative thinned compressed download size.
- Representative thinned install size from the App Thinning report.
- Extracted `.app` bundle size.
- Main executable size.
- Embedded framework total and largest frameworks.
- Asset catalog size and largest loose resources.
- Extension, plugin, or embedded app bundle size.
- Localization, font, media, generated-code, and test-resource size where present.
- dSYM archive size, reported separately as non-shipping diagnostic payload.

Use MiB/KiB consistently for filesystem measurements. If a tool reports decimal MB, preserve the tool's unit label and avoid mixing it with binary units without saying so.

## Attribute Contributors

Inspect the largest categories first. Useful audit surfaces:

- Binary and Mach-O: executable size, linked libraries, Swift metadata, generated source, dead stripping, exported symbols, and link maps when enabled. `size -m`, `nm`, `otool -L`, and a linker map (`-Xlinker -map`) cover most local questions; `bloaty` is an optional deep-dive when symbol-level attribution matters.
- Frameworks: embedded third-party SDKs, dynamic frameworks, duplicated dependencies, unused product modules, and extension-safe dependency boundaries.
- Resources: asset catalogs, loose images, fonts, localizations, bundled JSON, test fixtures, storyboards, nibs, and accidentally shipped configuration files.
- Extensions and plugins: duplicated app dependencies, extension-only resource needs, and whether shared code pulls app-side services into the extension bundle.
- Build configuration: release configuration selection, optimization flags, dead-code stripping, install stripping, Swift symbol stripping, dSYM separation, debug-only flags, test plan/resource embedding, and App Thinning behavior.
- External reports: App Store Connect size reports, the Xcode Organizer, and any hosted size-analysis service the project has configured — those services add per-module/per-symbol breakdowns and cross-build diffs the local toolchain cannot produce. When none is configured, say the tier is unavailable rather than approximating it.

Build configuration findings should distinguish between confirmed misconfiguration, healthy configuration, and diagnostic-only settings. Do not invent a fix when the evidence says the release configuration is already doing the expected stripping and optimization.

## Classify Findings

For each finding, decide whether it is:

- A likely direct size win.
- A product or dependency tradeoff that needs owner review.
- A release/build-system correctness issue.
- A measurement gap or baseline gap.
- Not worth actioning now.

Each actionable finding should include:

- Problem statement.
- Evidence from the audit.
- Expected impact, using measured size when possible.
- Risk or product tradeoff.
- Validation command, report, or artifact to confirm the fix.

Be skeptical of source-code refactors when the largest contributors are binary SDKs, generated code, resources, or extension duplication. The follow-up should match the measured contributor.

## Capture The Outcome

The durable result of a size audit belongs in the project's issue tracker and the PR narrative, not in local scratch files. When the project has no tracker, the PR description is the durable home; write a committed doc only when the user asks.

Update the source issue with:

- Final size metrics and measurement context.
- Baseline status.
- Build configuration findings.
- Local artifact status, including which paths are scratch and not intended for check-in.
- Links to follow-up issues.

Before creating follow-ups, search for existing issues to avoid duplicates. When creating issues, carry over the source issue's project, parent, assignee, and status equivalents where the tracker has them, unless the user asks otherwise.

Create focused follow-up issues rather than one omnibus cleanup task. Good follow-ups name one measurable contributor or correctness issue and include the evidence, expected impact, risk, and validation path.

## PR Guidance

Put tracked changes up for PR only when they are durable project improvements, such as:

- A build script, build-system target, CI artifact, or reusable measurement tool.
- A project skill, agent instruction, or committed process document.
- A build configuration fix.
- A test or guard that prevents a known release-size mistake from recurring.

Do not put local archives, exported IPAs, App Thinning output, copied app bundles, temporary Markdown reports, or raw generated audit data in a PR unless the user explicitly asks for a committed fixture.

## Done Criteria

The audit is complete when:

- The shipping path and any diagnostic deviations are documented.
- Core compressed, install, executable, framework, resource, extension, and dSYM metrics are captured.
- Build configuration was checked and categorized.
- Baseline comparison is present or the lack of baseline is explicit.
- Optional external reports were used or noted as unavailable.
- Actionable findings are captured as focused issues, or in the PR narrative when no tracker exists.
- Local scratch artifacts are clearly excluded from the PR surface.

---
name: analyzing-app-store-business-data
description: "Analyze App Store Connect revenue, subscriptions, acquisition, reviews, and growth. Use proactively for app business performance or experiment planning; not in-app engineering."
---

# Analyzing App Store Business Data

Turn App Store Connect data into business judgment: honest KPIs, a diagnosed
funnel, and growth plans where every lever has a hypothesis and a measurement
source. The data backbone is the `asc` CLI (https://asccli.sh); this skill
supplies the methodology. Resolve bundled scripts relative to this skill directory.

## Scope

Covers analysis, planning, and — with explicit approval — App Store Connect
changes for one app at a time. It assumes the working repository is that app's
repository, so bundle ID and metadata resolve locally.

Do not use this skill for:

- implementing in-app changes such as paywalls, prompts, or new tiers; this
  skill specifies the measurement plan and hands the build off as normal
  engineering work;
- storefronts outside the App Store;
- questions answerable without App Store Connect data.

## Requirements and Setup

For live CLI access, run `asc doctor` and check installed command help before use; skip setup when analyzing supplied exports. Resolve only blockers relevant to the requested analysis. Do not install tools, alter telemetry preferences, or configure credentials unless authorized.

- **CLI**: use the installed `asc` CLI when available. `brew install asc` is an optional setup step; inspect its telemetry preferences with the user rather than changing them automatically.
- **Auth**: keychain-backed profiles via
  `asc auth login --name <profile> --key-id … --issuer-id … --private-key <path>.p8 --network`.
  Prefer a dedicated machine-local key (never committed to a repo). Select
  non-default profiles with the global `--profile <name>` flag.
- **App discovery**: bundle ID comes from the repo's `fastlane/Appfile`
  (`app_identifier`). Resolve the numeric app ID with `asc apps --output json`
  and match on `bundleId`. Set `ASC_APP_ID` for the session once resolved.
- **Vendor number** (required for sales/finance reports): from env
  `ASC_VENDOR_NUMBER`, else `~/.config/app-store-business-analyst/config.toml`
  (`vendor_number = "…"`), else ask the user (they can read it from
  App Store Connect → Payments and Financial Reports).
- **Analytics reports**: live collection requires an ONGOING request per app. Reuse an existing request; create one only when live collection is within the authorized scope:
  `asc analytics request --app $ASC_APP_ID --access-type ONGOING --reuse-existing`.
  First data appears ~48h later; requests stop if unread for long periods
  (re-run the same command to revive).

## Tooling Contract

- Prefer an available App Store Connect connector or the installed `asc` CLI; command examples assume `asc` and may vary by version. Do not invent authentication plumbing when a supported tool exists. Discover unfamiliar commands with installed help; public Search/Lookup endpoints are covered in the ASO reference.
- Download raw reports into the cache, not the repo:
  `~/.cache/app-store-business-analyst/vendor-<num>/sales/` for Sales & Trends
  (vendor-wide reports) and
  `~/.cache/app-store-business-analyst/<bundle-id>/{analytics,reviews,market}/`
  for app-scoped data.
  Use deterministic versioned file names (`SALES_SUMMARY_DAILY_2026-07-01_v1_3.tsv`). The
  cache is the durable history — Apple expires old daily reports, so backfill
  early with `scripts/backfill-sales.sh` and preserve the cache. The helper keeps legacy unversioned files but downloads versioned replacements; inspect schemas before reusing older files.
- The cache and config directories keep the `app-store-business-analyst` name
  this skill was first published under. They are deliberately not renamed:
  the cached history cannot be re-downloaded once Apple expires it.
- Never stream a full report into context. Pull digests with
  `--output json`/`markdown`, and Read/grep cached files for row-level detail.
- Read the data-sources reference before interpreting any report, and the
  metrics playbook before computing any KPI.
- Every quoted metric must trace to a cache file or an `asc` output you ran.
  Label the trailing ~2 days of sales data as provisional (Apple restates).
  When mixing Analytics with sales data, state report-specific coverage,
  definitions, date windows, and privacy limits. Usage metrics are opt-in;
  do not apply that restriction or an opt-in scaling factor to every metric.

## Procedure A: Business Review

Use when asked "how is the app doing" or as the foundation for any plan.

1. `asc doctor`, resolve app ID, confirm vendor number.
2. Snapshot the monetization structure: `asc subscriptions list --app …`,
   `asc pricing` (current price points), intro/promo offers, `asc iap list`.
3. Pull data (cache-first; skip files already cached):
   - Monthly SALES for the trailing 13 months; daily SALES for the trailing
     30 days; daily SUBSCRIPTION and SUBSCRIPTION_EVENT reports for the
     available history. Use the latest subscription snapshot per period
     and sum event counts for monthly views; do not sum snapshots across
     days (`scripts/backfill-sales.sh` loops the requested dates).
   - `asc insights weekly --source sales` and `--source analytics` for
     this-week-vs-last-week movement.
   - Analytics: App Store Discovery & Engagement + Downloads reports, monthly
     granularity, trailing 12 instances (`asc analytics view / download`).
   - `asc reviews ratings --app … --all` (all territories) and
     `asc reviews --app … --paginate` into the cache.
4. Compute the standard tables from the metrics playbook:
   KPI snapshot (with 3- and 12-month deltas), acquisition funnel with
   source-type split, subscriber cohort grid, territory table.
5. Mine reviews/ratings for themes mapped to the funnel stage they affect.
   If there are few or no written reviews, say so — silence is itself a signal.
6. Return the review in the requested destination. Use `Documentation/Business/YYYY-MM-DD-business-review.md` only when the user requests a repository artifact and its visibility is appropriate for financial data. Suggested order: executive summary (5 bullets, numbers
   required) → KPI table → funnel → cohorts → reviews/ratings themes →
   risks and anomalies → data caveats.

## Procedure B: Growth Plan Ideation

Requires a current Procedure A in context (run it first if stale).

1. Diagnose the binding constraint: compute stage-over-stage funnel ratios and
   name the weakest stage. The plan attacks the constraint, not everything.
2. Market pass per the ASO methodology: keyword opportunity scan,
   competitor teardowns, current metadata audit from `fastlane/metadata/`.
3. Generate levers from the growth playbook, filtered to the
   constraint. For each: hypothesis ("If we X, metric Y moves A→B within T"),
   implementation sketch, measurement plan naming the exact report/field or
   `asc` command, effort, risk.
4. Assemble the plan: target (e.g. 2× trailing-12-month proceeds), the
   multiplication math showing which stage improvements compound to the
   target, a sequenced 90-day experiment schedule, kill/scale checkpoints,
   and a monitoring cadence (which pulls to re-run, when).
5. Return the plan in the requested destination; for an authorized repository artifact, use `Documentation/Business/YYYY-MM-DD-growth-plan.md`. Include: goal and
   baseline → constraint diagnosis → plan table (lever, hypothesis, success
   metric + target, measurement source, effort, timeline) → sequencing →
   monitoring plan.

## Procedure C: Execution

Only with explicit user approval of a specific change; propose first, apply
after confirmation. Prefer dry-run/diff modes wherever `asc` offers them.

- **ASO/metadata**: propose diffs to `fastlane/metadata/<locale>/` files; on
  approval apply, run the repo's localization tooling, then upload via the
  repo's existing lane (e.g. `make app-store/upload-metadata`). If the repo
  has no fastlane metadata, `asc metadata pull/validate/apply` is the
  fallback.
- **Pricing and offers**: `asc pricing`, `asc subscriptions offers`,
  `asc iap offer-codes` — always show the exact command and expected effect,
  get confirmation, then run.
- **Review responses**: draft first; `asc reviews respond-batch --dry-run`
  before any real send.
- **In-app changes** (paywall, prompts, new tiers): hand off as normal
  engineering work in the app repo; this skill specifies the measurement plan.

## Rules

- Never fabricate or extrapolate silently; small samples get called small.
- Never print private key material or move keys into repos.
- Destructive or customer-visible actions (responses, prices, metadata)
  always require explicit confirmation with the exact change shown.

## Reference Map

Load only what the current step needs:

- [Data sources](references/data-sources.md): what each report contains and how
  to interpret it. Read before interpreting any report.
- [Metrics playbook](references/metrics-playbook.md): KPI definitions and the
  standard tables. Read before computing any KPI.
- [Growth playbook](references/growth-playbook.md): the lever catalog for
  Procedure B, step 3.
- [ASO methodology](references/aso-methodology.md): keyword scans, competitor
  teardowns, and metadata audits for Procedure B, step 2.
- `scripts/backfill-sales.sh`: bulk historical sales pull into the cache.

Before delivering, confirm every quoted number traces to a cache file or a
command you ran, provisional and opt-in caveats are stated, and any
customer-visible change was explicitly confirmed.

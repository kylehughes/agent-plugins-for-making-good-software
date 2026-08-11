# Data Sources

Which question maps to which source, what each report actually contains, and
the timing rules that keep analysis honest.

## Routing Table

| Question | Source | Command |
|---|---|---|
| Revenue / units by period | Sales & Trends `SALES` | `asc analytics sales --type SALES --subtype SUMMARY --frequency MONTHLY --date YYYY-MM` |
| Active subscribers, trial states | `SUBSCRIPTION` report | `asc analytics sales --type SUBSCRIPTION --subtype SUMMARY --frequency DAILY --version 1_3` |
| Subscribes / renewals / cancels / refunds | `SUBSCRIPTION_EVENT` report | `asc analytics sales --type SUBSCRIPTION_EVENT --subtype SUMMARY --frequency DAILY --version 1_3` |
| Period-over-period movement | derived | `asc analytics compare --source sales --from … --to …` / `asc insights weekly` |
| Impressions, page views, conversion, source types | App Analytics | `asc analytics view/download` (Discovery & Engagement reports) |
| First-time vs redownloads, installs/deletions, sessions | App Analytics | `asc analytics view/download` (Downloads / Usage reports) |
| Ratings histogram per territory | Ratings | `asc reviews ratings --app … [--all]` |
| Written review content | Customer Reviews | `asc reviews --app … --paginate` |
| What Apple actually paid (fiscal months) | Finance reports | `asc finance reports --vendor … --date YYYY-MM` |
| Crashes, launch time, disk writes | Performance | `asc performance` |
| Competitor listings, ratings counts, pricing | iTunes Search/Lookup (no auth) | curl recipes in `aso-methodology.md` |
| Category top charts | Apple RSS (no auth) | curl recipes in `aso-methodology.md` |

`asc search <term>` finds commands not listed here.

## Sales & Trends Reports

Delivered as gzipped TSV (`--decompress` writes plain `.tsv`). Reports cover
**all apps under the vendor number** — cache them per vendor
(`vendor-<num>/sales/`), and always filter rows to the app under analysis
(`Apple Identifier` column = numeric app ID; SKU column also works).

### SALES (subtype SUMMARY, version 1_0 — the latest; the API rejects 1_1)

One row per product/date/country/type combination.

- **Units / Developer Proceeds**: proceeds are post-Apple-cut, in the
  `Currency of Proceeds`; `Customer Price` is what the buyer paid.
- **Product Type Identifier** (memorize these):
  `1`/`1F`/`1T` app download (iPhone/universal/iPad), `7`/`7F`/`7T` app
  update, `3`/`3F` redownload, `IA1` consumable IAP, `IA9` non-consuming IAP,
  `IAY` auto-renewable subscription, `IAC` free trial/intro.
  "Downloads" for funnel math = types 1/1F/1T only (not updates, not
  redownloads).
- Promo/offer codes appear in the `Promo Code` column; B2B and
  family-sharing rows have their own type codes — check before summing.

### SUBSCRIPTION (subtype SUMMARY, version 1_3)

Point-in-time snapshot per day: active standard-price subscribers, active
intro/offer subscribers, billing-retry and grace-period counts, marketing
opt-ins. Use for "how many active subscribers right now/then"; do not sum
across days.

### SUBSCRIPTION_EVENT (subtype SUMMARY, version 1_3)

Event counts per day: Subscribe, Renew, Cancel, Refund, billing retry
entry/recovery, and **cancellation reasons**. This is the flow data —
subscriber math (new vs renewal, churn) comes from here.

### SUBSCRIBER (subtype DETAILED, version 1_3) — cohort/LTV source

Row-per-subscriber-event with proceeds, subscriber age, and consecutive paid
periods — the input for cohort and LTV analysis. **Not currently exposed by
`asc analytics sales --type`** (its type list stops at SUBSCRIPTION_EVENT).
Before doing cohort work, re-check `asc analytics sales --help`; if still
missing, approximate cohorts from SUBSCRIPTION_EVENT (subscribe month ×
subsequent renew/cancel counts) and note the approximation.

### Timing rules

- Daily reports appear the next day (early morning Pacific); the trailing ~2
  days are subject to restatement — label them provisional and re-fetch when
  they age past the window.
- Date formats: daily/weekly `YYYY-MM-DD` (weekly accepts Monday-start or
  Sunday-end per `asc`), monthly `YYYY-MM`, yearly `YYYY`.
- **SUBSCRIPTION and SUBSCRIPTION_EVENT reports are daily-only** (verified
  empirically 2026-07: monthly/weekly requests return "no report available").
  Build monthly aggregates by summing daily files; event reports exist only
  on days with at least one event.
- Retention horizons (verified empirically 2026-07): monthly SALES reports
  reach back ~12 months; older dates return "no report available".
  **Backfill immediately and treat the cache as the durable record.**
- A 404 also means "no data for that period" for small apps (common for
  DAILY SUBSCRIPTION_EVENT). Zero-sales days simply have no rows/report.

## App Analytics Reports

Prerequisite: an ONGOING `analyticsReportRequest` (see SKILL.md setup).
Flow: `asc analytics requests --app …` → `view --request-id …` (report list
with names/categories) → `instances` (by granularity + processing date) →
`download`. Segments are gzipped CSVs.

Report categories: `APP_STORE_ENGAGEMENT` (Discovery and Engagement:
impressions, product page views, taps, by source type and territory),
`APP_STORE_COMMERCE` (Downloads: first-time vs redownload; Purchases:
proceeds by content type), `APP_USAGE` (Sessions; Installations and
Deletions; Crashes), `FRAMEWORK_USAGE`, `PERFORMANCE`.

**The opt-in caveat (mandatory):** App Analytics only counts users who share
analytics with developers (roughly a quarter to a third of users; varies).
Sales reports count everyone. Before mixing, compute the calibration ratio:
`analytics first-time downloads ÷ sales-report downloads` for the same
window, and state it. Conversion *rates* within analytics (page views →
downloads) are internally consistent; absolute analytics counts are not.

Source types: `App Store search`, `App Store browse`, `App referrer`,
`Web referrer`, `Unavailable` — the search share is the ASO signal.

## Reviews and Ratings

- Ratings (`asc reviews ratings`) are per-territory histograms; `--all`
  aggregates every territory. Ratings ≫ written reviews for small apps.
- Written reviews (`asc reviews`) page 200 at a time; `--paginate` fetches
  all. Fields: rating, title, body, territory, createdDate, developer
  response state.
- `asc reviews summarizations` returns Apple's AI review summary where
  available (US, sufficient volume).

## Finance Reports

`asc finance reports` — what Apple actually pays, by **fiscal month** (Apple's
fiscal calendar, not calendar months; fiscal 2026 began 2025-09-28). Use to
reconcile proceeds sums from SALES reports when exactness matters (currency
conversion happens here). Region `ZZ` = consolidated.

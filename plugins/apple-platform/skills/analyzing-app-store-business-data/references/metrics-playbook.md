# Metrics Playbook

Formulas and hygiene rules. Every KPI below names its source; if you can't
trace a number to a cached report, don't quote it.

## Core KPIs

| KPI | Formula | Source |
|---|---|---|
| Proceeds (T12M) | Σ (`Units` × per-unit `Developer Proceeds`) over trailing 12 complete months, grouped by currency | SALES monthly |
| Proceeds run rate | trailing 3 complete months × 4 | SALES monthly |
| Downloads | Σ Units where Product Type ∈ {1, 1F, 1T} | SALES |
| Active subscribers | latest SUBSCRIPTION snapshot (standard + offer rows) | SUBSCRIPTION |
| New subscribers | Σ Subscribe events per period | SUBSCRIPTION_EVENT |
| Paid conversion | new subscribers ÷ downloads, same window | EVENT ÷ SALES |
| Proceeds per download | net proceeds ÷ downloads, same period | SALES |
| Proceeds per paid transaction | net proceeds ÷ paid transaction units, same period | SALES |
| Refund rate | Refund events ÷ Subscribe+Renew events | SUBSCRIPTION_EVENT |
| Rating quality/volume | average and count, per territory | `asc reviews ratings` |

Proceeds are net of applicable taxes and Apple's commission; use the report
values rather than assuming a commission rate. See [Apple's metric
definitions](https://developer.apple.com/help/app-store-connect-analytics/reference/metrics-definitions/).
State which currency column you used; reconcile mixed currencies through
finance reports or label the conversion as approximate. [Summary Sales
Report proceeds are per unit](https://developer.apple.com/help/app-store-connect/reference/reporting/summary-sales-report/):
multiply by signed units before summing, including refunds and credits.
Proceeds per download or transaction are not ARPU or ARPPU; those metrics
require user counts for the denominator.

## The Funnel

```
Impressions → Product Page Views → Downloads → Subscribes → Paid retention
   (analytics)      (analytics)     (SALES 1/1F/1T)  (EVENT)     (EVENT renews)
```

- Compute each stage-over-stage ratio for the same window (monthly is the
  right default for small apps; daily is noise).
- Split by source type (search / browse / referrer) — ASO work moves search
  impressions; conversion work moves page-view→download.
- Coverage: verify report definitions, populations, date windows, and privacy
  limits before combining Analytics and sales counts. Usage metrics are
  opt-in; discovery and download counts must not be scaled as though all
  Analytics data were an opt-in sample. State unresolved differences.
- Benchmarks for orientation (state as heuristics, not truth): page-view →
  download commonly 25–35% for utility apps; download → paid for freemium
  utilities commonly 1–5%; search impression → page view is highly
  keyword-dependent.

## Annual Subscriptions (the 1-year SKU case)

Monthly churn is the wrong lens for an annual product. Instead:

- **Cohorts**: group subscribers by subscribe month (from SUBSCRIPTION_EVENT
  Subscribe counts; per-subscriber detail needs the SUBSCRIBER report — see
  data-sources.md for its availability). Track each cohort's renewal events
  at month +12.
- **Year-1 renewal rate** = renewals in month M ÷ subscribes in month M−12.
  Only quote when the denominator ≥ 20; below that report raw counts
  ("3 of 7 renewed") instead of percentages.
- **Realized LTV** per cohort = Σ proceeds attributed to the cohort so far.
  Projected LTV = ASP × (1 + r + r² …) using observed renewal rate r — label
  the projection and the r you assumed.
- Refunds cluster near purchase; deduct them from the cohort's realized LTV.

## Standard Output Tables

Use exactly these shapes so reviews are comparable over time.

**KPI snapshot**

| KPI | Current | 3-mo Δ | 12-mo Δ | Source |
|---|---|---|---|---|

**Funnel (window: <month>)**

| Stage | Count | Conversion from prior | vs prior period |
|---|---|---|---|

**Cohorts**

| Subscribe month | Subscribes | Renewed (mo+12) | Refunds | Realized proceeds |
|---|---|---|---|---|

**Territories**

| Territory | Downloads | Proceeds | Subscribers | Rating (n) |
|---|---|---|---|---|

## Hygiene Rules

- Exclude the trailing 2 days of sales data or label them provisional.
- Never sum the SUBSCRIPTION snapshot across days; it's a level, not a flow.
- Use one report frequency for each covered period. Do not add daily and
  monthly SALES totals for overlapping dates; aggregate currencies
  separately until an explicit conversion is applied.
- Deduplicate by (report date, SKU, country, type) when concatenating cached
  TSVs; re-downloads of restated reports can differ — latest fetch wins.
- Minimum samples: no percentage from a denominator under 20; no
  trend claims from fewer than 3 periods.
- When a report 404s, record the period as "no data" — for a small app that
  usually means zero, but say "no report" rather than asserting zero sales
  when the date is recent.
- Every table cites its cache files at the bottom.

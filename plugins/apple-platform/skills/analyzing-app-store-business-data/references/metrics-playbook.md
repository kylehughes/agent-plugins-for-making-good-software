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
| Subscription acquisition ratio | new subscription starts ÷ downloads, same window; distinguish trials and paid starts | EVENT ÷ SALES |
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
- Prefer the app’s own comparable historical windows and controlled experiments. Use external benchmarks only with a cited source, category, population, and date. These aggregate stage ratios do not establish user-level conversion.

## Annual Subscriptions (the 1-year SKU case)

Monthly churn is the wrong lens for an annual product. Instead:

- **Cohorts** require subscriber-level linkage between the original paid start and later renewal events. Aggregate SUBSCRIPTION_EVENT totals alone cannot establish membership; report aggregate flows when linkage is unavailable.
- **Year-1 renewal rate** = first-renewal successes for a cohort ÷ members eligible for that first renewal. Account for trials, refunds, grace periods, product changes, and incomplete observation. Renewals in one calendar month divided by starts twelve months earlier is only an aggregate proxy, not this cohort rate.
- **Realized cohort proceeds** = proceeds attributable to the cohort so far; divide by the stated cohort population for per-subscriber realized LTV. A projection such as ASP × (1 + r + r² …) requires explicit horizon, constant-price and retention assumptions; label it as a model, not an observed KPI.
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
- Deduplicate report files by vendor, report type, frequency, date, and version; replace a restated report as a unit. Do not collapse rows by date/SKU/country/type: legitimate rows may differ in price, currency, offer, or other dimensions.
- Minimum samples: no percentage from a denominator under 20; no
  trend claims from fewer than 3 periods.
- When a report 404s, record the period as "no data" — for a small app that
  usually means zero, but say "no report" rather than asserting zero sales
  when the date is recent.
- Every table cites its cache files at the bottom.

# Metrics Playbook

Formulas and hygiene rules. Every KPI below names its source; if you can't
trace a number to a cached report, don't quote it.

## Core KPIs

| KPI | Formula | Source |
|---|---|---|
| Proceeds (T12M) | Σ `Developer Proceeds` over trailing 12 complete months | SALES monthly |
| Proceeds run rate | trailing 3 complete months × 4 | SALES monthly |
| Downloads | Σ Units where Product Type ∈ {1, 1F, 1T} | SALES |
| Active subscribers | latest SUBSCRIPTION snapshot (standard + offer rows) | SUBSCRIPTION |
| New subscribers | Σ Subscribe events per period | SUBSCRIPTION_EVENT |
| Paid conversion | new subscribers ÷ downloads, same window | EVENT ÷ SALES |
| ARPU | proceeds ÷ downloads (per period) | SALES |
| ARPPU / ASP | proceeds ÷ paying transactions | SALES (IAY rows) |
| Refund rate | Refund events ÷ Subscribe+Renew events | SUBSCRIPTION_EVENT |
| Rating quality/volume | average and count, per territory | `asc reviews ratings` |

Proceeds are Apple-cut-adjusted (developer receives 70%, or 85% in the Small
Business Program — nearly all indie accounts are in it). Note which currency
column you summed; when mixing currencies use the proceeds-currency column
plus finance reports for exact conversion, or state the approximation.

## The Funnel

```
Impressions → Product Page Views → Downloads → Subscribes → Paid retention
   (analytics)      (analytics)     (SALES 1/1F/1T)  (EVENT)     (EVENT renews)
```

- Compute each stage-over-stage ratio for the same window (monthly is the
  right default for small apps; daily is noise).
- Split by source type (search / browse / referrer) — ASO work moves search
  impressions; conversion work moves page-view→download.
- Calibration: analytics counts are opted-in users only. Compute
  `sales downloads ÷ analytics downloads` and apply it before comparing
  stages that cross the analytics/sales boundary. State it in output.
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
- Deduplicate by (report date, SKU, country, type) when concatenating cached
  TSVs; re-downloads of restated reports can differ — latest fetch wins.
- Minimum samples: no percentage from a denominator under 20; no
  trend claims from fewer than 3 periods.
- When a report 404s, record the period as "no data" — for a small app that
  usually means zero, but say "no report" rather than asserting zero sales
  when the date is recent.
- Every table cites its cache files at the bottom.

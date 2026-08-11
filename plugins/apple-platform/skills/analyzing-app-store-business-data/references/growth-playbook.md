# Growth Playbook

A taxonomy of revenue levers, each with its measurement plan. Plans attack the
measured funnel constraint — never propose levers for stages that aren't the
bottleneck.

## The 2× vs 10× Math

Revenue = impressions × (page-view rate) × (download rate) × (paid
conversion) × ASP × (1 + renewals). Because stages multiply:

- **2×** is usually compounding: four stages improved 20% each ≈ 2.07×.
  Realistic through optimization alone.
- **10×** is never optimization. It requires a new term in the equation: a
  new acquisition channel (featuring, virality, a platform moment, paid ads),
  a new market (locales with real demand), or a new monetization model
  (different price structure, new audience tier, another app). Say this
  plainly in 10× plans and structure them as bets, not tweaks.

State the current value of every factor before proposing to move it.

## Acquisition Levers (move impressions / page views)

| Lever | Mechanism | Measure with | Time to signal |
|---|---|---|---|
| Keyword/metadata iteration | rank for higher-demand terms | search impressions + search-source downloads (analytics, Discovery report) | 2–6 weeks per iteration |
| Localization depth | rank in non-English storefronts | territory split of impressions/downloads | 4–8 weeks |
| Featuring nomination | editorial placement | browse-source spike; `asc nominations` submits | event-driven |
| In-app events | extra store surface | event page views (analytics) | per event |
| Custom product pages | per-audience landing pages | per-page conversion via `asc product-pages` + analytics | 2–4 weeks |
| Apple Search Ads | paid search placement | out of scope unless the user runs ads (`asc ads`) | days |

## Conversion Levers (move download rate / paid rate)

| Lever | Mechanism | Measure with |
|---|---|---|
| Screenshots/preview reorder | better page-view → download | Product Page Optimization test (`asc versions experiments-v2`) — Apple-native A/B, use it rather than before/after when volume allows |
| Intro offer / free trial | lower the paid entry barrier | intro-offer rows in SUBSCRIPTION report; Subscribe events with offer type |
| Paywall placement/copy/timing | more upgrade moments | paid conversion (EVENT ÷ downloads) before/after release, noted by version date |
| Ratings volume prompts | social proof on listing | rating count velocity (`asc reviews ratings` over time) → page-view→download rate |

## Monetization-Structure Levers (move ASP / addressable buyers)

| Lever | Mechanism | Measure with |
|---|---|---|
| Add monthly tier next to annual | capture lower-commitment buyers | tier mix in SUBSCRIPTION report; total proceeds (watch cannibalization: annual units before/after) |
| Lifetime unlock tier | capture subscription-averse buyers | IA9 rows appearing in SALES; net proceeds vs subscription decline |
| Territory price tuning | price-elasticity by market | per-territory units × proceeds before/after (`asc pricing`, change one territory batch at a time as a holdout design) |
| Offer codes campaigns | reactivation / promo channels | `SUBSCRIPTION_OFFER_CODE_REDEMPTION` report; downstream renewals |
| Win-back offers | recover lapsed subscribers | win-back offer redemptions (`asc subscriptions offers`); EVENT resubscribes |

## Retention Levers (move renewals)

- Billing grace period + retry: free renewal-rate recovery; check it's
  enabled, measure billing-retry recovery counts in SUBSCRIPTION_EVENT.
- Pre-renewal value reminders (in-app): renewal rate by cohort before/after.
- Cancellation-reason mining: EVENT report cancel reasons → targeted fixes.

## Experiment Design on Apple's Platform

No server-side experimentation without infra, so:

1. **Listing changes** → Product Page Optimization (real A/B, Apple splits
   traffic). Needs enough page views: at current volume compute the
   minimum detectable effect first; if MDE > 30% relative, run sequential
   before/after instead and accept the weaker inference.
2. **Pricing** → change a comparable territory cluster first (holdout
   design), or accept before/after with seasonality noted.
3. **In-app changes** → ship, compare stable windows around the release,
   attribute by version. State that this is not causal proof.
4. Every experiment gets: hypothesis, metric + target, sample/duration
   precomputed, kill criterion, scale criterion — written down *before*
   launch, in the growth-plan doc.

## Prioritization

Score levers ICE-style (impact on the constraint × confidence × ease), but
impact must be computed from the actual funnel numbers, not vibes: "moving
page-view→download from 28%→34% at current 10k monthly impressions = +X
downloads = +Y subscribers at current paid rate = +$Z/yr."

Sequence: cheap-and-fast constraints first (metadata, offers) while
long-lead bets (localization, new tiers, featuring) run in the background.
Cap concurrent experiments so measurement windows don't overlap on the same
metric.

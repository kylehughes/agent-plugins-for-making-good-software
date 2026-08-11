# ASO Methodology

App Store Optimization with free data only: your own analytics, the public
iTunes APIs, and disciplined competitor teardown.

## Current-State Audit

Source of truth is the repo: `fastlane/metadata/<locale>/` — `name.txt`
(30 chars), `subtitle.txt` (30), `keywords.txt` (100, comma-separated, no
spaces after commas), `description.txt` (not indexed for search on iOS —
write it for conversion, not keywords), `promotional_text.txt` (170,
changeable without review). Also `asc app-tags` for Apple-generated
discoverability tags (read-only signal of how Apple classifies the app).

Audit checks: character budgets fully used; no word duplicated between
title/subtitle/keywords (duplicates waste budget — all three combine into
one index); plurals not duplicated (Apple matches loosely); every claimed
locale actually localized rather than copied English.

## Free Market Data (no auth)

```sh
# Keyword SERP: who ranks for a term in a storefront
curl -s "https://itunes.apple.com/search?term=TERM&country=us&entity=software&limit=25"

# One app's full listing (own or competitor)
curl -s "https://itunes.apple.com/lookup?bundleId=BUNDLE_ID&country=us"
curl -s "https://itunes.apple.com/lookup?id=TRACK_ID&country=us"

# Category top charts (no top-grossing in this feed)
curl -s "https://rss.marketingtools.apple.com/api/v2/us/apps/top-free/50/apps.json"
```

Useful lookup fields: `averageUserRating`, `userRatingCount` (demand/traction
proxy), `price`, `genres`, `releaseDate` + `currentVersionReleaseDate`
(maintenance signal), `description`. Throttle to ~20 requests/min; cache
responses under `market/` in the skill cache.

## Keyword Research Loop

1. Seed 10–20 candidate terms from: the app's job-to-be-done, competitor
   titles/subtitles, review language (what words do users use?), and the
   Discovery & Engagement report's search performance.
2. For each term, pull the SERP and record: top-10 apps, each one's
   `userRatingCount`, and whether the term appears in their title/subtitle.
3. Score: **opportunity = relevance × demand proxy ÷ competition strength**,
   where demand proxy = median rating count of the top 10 (crowded, reviewed
   SERPs indicate real search volume) and competition strength = how many of
   the top 10 carry the term in their *title* (title matches are hard to
   outrank).
4. Target terms where the app can plausibly reach top 5; a #40 ranking is
   worth nothing. Verify movement 2–6 weeks after shipping metadata via
   search-source impressions in analytics.

## Competitor Teardown Checklist

For each of the top 3–5 competitors: positioning (title/subtitle promise),
monetization (price, IAP list from lookup + their listing), rating velocity
(`userRatingCount` now vs a cached earlier snapshot — build history by
caching every run), update cadence, screenshot narrative (first two
screenshots carry most conversion), and their negative-review themes (fetch
their public reviews via the same reviews RSS/lookup surfaces) — those are
positioning gaps you can claim.

## Locale Strategy

1. From the territory table (metrics playbook), find storefronts with
   downloads but weak/absent localization, and large storefronts with zero
   traction.
2. Localized *keywords* are the cheap win — a translated keyword field can
   rank where English never will. Repo tooling (e.g. app-localizer) handles
   translation; ASO review still needs human-plausible search terms per
   locale, not literal translations.
3. Measure per-locale exactly like the global funnel: search impressions →
   downloads by territory.

## Shipping Changes

Metadata changes go through Procedure C (SKILL.md): diff to
`fastlane/metadata/`, translate, upload via the repo's lane. Title/subtitle
changes require an app version review; keywords ship with the next version
too — batch them with releases. Promotional text is the only field
changeable anytime.

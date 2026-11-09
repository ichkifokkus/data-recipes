---
name: find-public-tenders
description: Finds open public tenders (calls for bids) in Germany and the EU for a product, service or industry and returns a short, ranked list with buyer, deadline, estimated value and official link. Use when the user asks for public tenders, Ausschreibungen, öffentliche Aufträge, Vergabe, procurement opportunities, government contracts or bid opportunities in Germany, Austria or other EU countries.
license: MIT
metadata:
  author: fast-data
  version: "1.0"
  tested: "2026-11-09"
---

# Find public tenders (Germany + EU)

## When to use

The user wants to know which public bodies are currently buying something they sell, e.g.
"Are there tenders for IT security in Bavaria?", "Ausschreibungen für Gebäudereinigung in NRW",
"EU tenders for cloud software in Austria this week".

## Tools

Both are public Apify Actors, callable through Apify's MCP server
(`https://mcp.apify.com/?tools=fast_data_asap/german-public-tenders-bund,fast_data_asap/eu-tenders-ted-api`)
or the Apify API (`POST https://api.apify.com/v2/acts/<owner>~<actor>/run-sync-get-dataset-items`).

| Actor | Source | Use for |
|---|---|---|
| `fast_data_asap/german-public-tenders-bund` | service.bund.de (German federal portal, includes many state and municipal notices) | national German tenders, also below EU thresholds |
| `fast_data_asap/eu-tenders-ted-api` | TED, the EU's official tenders journal | EU-wide notices above EU thresholds, any EU country |

## Steps

1. **Clarify in one question only if needed:** what is being sold (keywords), where (German state / EU country), how recent.
   Defaults: last 7 days, open tenders only, max 20 results per source.
2. **German tenders** – call `fast_data_asap/german-public-tenders-bund` with:
   ```json
   {"keywords": ["Software"], "states": ["Bayern"], "lastDays": 7, "maxItems": 20, "includeDetails": true, "excludeKeywords": []}
   ```
   German keywords work best (Software, Reinigung, Dachsanierung, Beratung). Use `categories` / `procedureRules` only if the user asks.
3. **EU tenders** (if the user wants EU, a non-German country, or large contracts) – call `fast_data_asap/eu-tenders-ted-api` with:
   ```json
   {"keywords": ["software"], "countries": ["DEU"], "cpvCodes": ["72"], "noticeTypes": ["competition"], "publishedWithinDays": 7, "deadlineAfter": "today", "maxResults": 20}
   ```
   `countries` are ISO alpha-3 codes (DEU, AUT, FRA …). CPV prefixes: 72 IT services, 48 software, 45 construction, 90 cleaning/environment, 79 business services. Add `minValueEur` if the user names a minimum size.
4. **Merge and clean:** drop tenders whose `deadline` has passed; the same procedure can appear in both sources (EU-wide German tenders) – keep the TED entry when buyer and title match.
5. **Rank:** soonest `deadline` first; flag deadlines under 21 days as urgent.

## Output fields (as returned on 2026-11-09)

- German Actor: `tenderId, title, contractingAuthority, city, state, category, procedureRules, procedureType, scope, cpvCodes, publishedAt, deadline, publicationEnd, url`
  (`deadline` can be empty – then use `publicationEnd`).
- TED Actor: `noticeId, title, buyerName, buyerCountry, buyerCity, cpvMain, cpvCodes, procedureType, estimatedValue, currency, publishedAt, deadline, lotsCount, url, summary`.

## Output format

A table, max 10 rows, then one line with totals:

| Deadline | Buyer | Title (short) | Place | Value | Source |
|---|---|---|---|---|---|
| 07.12.2026 ⚠️ | Stadt Brandis | Development of OpenCore modules | Brandis, DE | €625,600 | [TED](url) |

End with: "Always read the official notice before deciding to bid."

## Limits

- Not every contracting body publishes on service.bund.de; TED only lists notices above EU thresholds (and voluntary ones).
- Portal titles are sometimes truncated; the `url` always leads to the official notice.
- This is a search aid, not legal or procurement advice. No personal data is collected (only organisations).

## Cost (published prices, 2026-11-09)

- German Public Tenders: $0.002 per tender returned.
- EU Tenders (TED): $0.002 per notice returned; empty runs are free.
- A typical query (20 + 20 results) costs about $0.08 in the user's own Apify account.

## Tested

2026-11-09: both calls above run with `maxItems`/`maxResults` = 2 (256 MB). German Actor returned 2 tenders (Universität Hamburg, Stadt Regensburg) with all fields listed; TED returned 2 notices (Stadt Brandis €625,600, BWI GmbH) with all fields listed. Each call finished in under a minute.

## Disclosure

This skill uses Fast Data actors we maintain ([apify.com/fast_data_asap](https://apify.com/fast_data_asap)). The skill itself is free.

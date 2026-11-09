---
title: "How to build a daily B2B sales-signal feed from public tenders and hiring data with n8n"
published: true
description: "A free n8n workflow that collects German public tenders and new job postings at your target accounts every weekday, scores them with two simple rules and posts only the new ones to Slack, Google Sheets and (optionally) your CRM."
tags: n8n, automation, productivity, sales
---

Most "intent data" tools sell you a score without telling you where it comes from. But two of the strongest B2B buying signals are public and free to read:

1. **A public body publishes a tender.** It has a budget, a need and a deadline.
2. **A company opens several jobs at once.** It is growing, reorganising or starting a project, and it will buy tools and services for it.

This post is a ready-to-import n8n workflow that collects both every weekday morning, turns them into one feed with a simple score, and sends only the new signals to Slack, a Google Sheet and, if you want, Pipedrive or HubSpot.

*Disclosure: I built the two Apify actors used here, [German Public Tenders](https://apify.com/fast_data_asap/german-public-tenders-bund) and [Career Site Jobs API](https://apify.com/fast_data_asap/career-site-jobs-api). The workflow is free in our [data-recipes repo](https://github.com/ichkifokkus/data-recipes/tree/main/9-sales-signals-daily-feed).*

## What the feed looks like

This is a real run from 8 November 2026 (keyword "Software", three target companies), passed through the workflow's own Code nodes:

```
Sales signals: 6 new (1 high, 3 medium, 2 low)
2 public tender(s), 4 job posting(s)

[high] Tender: Hochschule Zittau/Görlitz - Bereitstellung einer virtuellen Plattform ... - due 2026-11-13
    5 day(s) to end of publication
[medium] Tender: Stadt Regensburg - Einfuehrung und Nutzung eines Archivinformationssystems ... - due 2026-12-07
    30 day(s) to offer deadline
[medium] Hiring: Tibber - Pricing & Project Lead
    2 role(s) posted at Tibber in the last 7 day(s)
...and 2 more in the sheet
```

Every signal also lands as one row in a sheet: `signalId, found_at, signalType, organisation, title, location, date, deadline, url, score, reason`. Only organisations appear, never people or contact details.

## The workflow

```
Weekdays 7:00 → Settings ─┬─ Get public tenders ─┐
                          └─ Get hiring signals ─┴─ Combine → Normalize & score
  → Read signal log → Keep new signals only ─┬─ Log new signals (Sheets)
                                             ├─ Build Slack digest → Post to Slack
                                             └─ High score only → Create Pipedrive activity (disabled)
```

All nodes are built in. The two data calls are plain HTTP Request nodes against Apify's synchronous endpoint, which runs the actor and returns its results in one step:

```
POST https://api.apify.com/v2/acts/fast_data_asap~german-public-tenders-bund/run-sync-get-dataset-items
Authorization: Bearer <your Apify token>   (Header Auth credential in n8n)

{"keywords": ["Software"], "states": [], "excludeKeywords": [], "lastDays": 2, "maxItems": 50, "includeDetails": true}
```

```
POST https://api.apify.com/v2/acts/fast_data_asap~career-site-jobs-api/run-sync-get-dataset-items

{"companies": ["teamtailor:tibber", "ashby:n8n", "greenhouse:celonis"], "postedWithinDays": 2, "maxJobsPerCompany": 25, "includeDescription": false}
```

The tender actor reads service.bund.de, the German federal portal that aggregates many federal, state and municipal publishers, and adds details such as contracting authority, place of performance, procedure type, CPV codes and the offer deadline. The jobs actor reads the public job-board APIs behind company career sites (Greenhouse, Lever, Ashby, Personio, Teamtailor, Workday and others), so there is no fragile HTML scraping.

All inputs live in one **Settings** node: keywords, optional German states, words to exclude, and your list of target companies. The lookback window is automatic: four days on Mondays to cover the weekend, two days otherwise. The extra day is a safety net if a run fails.

## One schema, two simple scores

The *Normalize & score* Code node maps both sources to the same fields and applies two rules you can explain to any salesperson:

- **Tender**: if the offer deadline (or, when none is published, the end of publication) is less than 21 days away, it is **high**. Someone has to make a bid/no-bid decision this week. Otherwise **medium**. Tenders whose deadline has already passed are dropped.
- **Hiring**: three or more roles at the same company in the window is **high**. Two roles, or one leadership role (Head of, Director, VP), is **medium**. A single other role is **low**.

| Signal | High | Medium | Low |
|---|---|---|---|
| Tender | deadline < 21 days away | deadline 21+ days away | – (expired tenders are dropped) |
| Hiring | 3+ roles at one company | 2 roles, or 1 leadership role | 1 other role |

Both thresholds are constants at the top of the node. In practice you will want to tune them: count only Sales or Engineering titles, or give extra weight to your core regions.

## Deduplication with a Google Sheet

Instead of n8n's internal "seen before" memory, the workflow reads the `signalId` column of the sheet and drops anything that is already there. The ID is simply the type plus the source URL (`tender:https://...`, `job:https://...`). The advantage: the memory is visible. If a rep wants to see a signal again, they delete the row.

## What the test showed

I ran each actor once with small limits (256 MB, a few results) on a Sunday:

- **Tenders**: the keyword "Software" with a 2-day window returned **2 tenders** (the search page had 100 results, 2 inside the window). One had a published offer deadline 30 days out; the other had no deadline, only an end of publication 5 days later, which is why the score falls back to that date. Weekdays bring more.
- **Jobs**: Tibber had **13 open roles**, n8n **48** and Celonis **233**; with `postedWithinDays: 7` and a cap of 1-2 jobs per company the run returned 4 postings. `personio:personio` returned 0, a reminder to check each company's career-site URL once.
- Both calls finished in under 6 seconds.

## What it costs

Both actors charge per result: **$0.002 per tender** and **$0.002 per job posting** on the Free and Starter plans. The test run returned 6 results, so $0.012. A realistic day with 10 tenders and 15 new jobs, each returned twice because of the overlap day, is about $0.10, or roughly **$2 per month** for 21 weekdays. You control the ceiling with `maxTenders` and `maxJobsPerCompany`.

## Limits worth knowing

- Tenders cover **Germany via one portal**. Not every contracting body publishes there, and some titles are truncated by the portal. For EU-wide notices, our [EU Tenders (TED) API](https://apify.com/fast_data_asap/eu-tenders-ted-api) ($0.002 per notice) can be added as a third HTTP branch with the same schema mapping.
- Hiring data is only as good as the career site. Custom career pages without a supported job board return nothing, and a re-posted job counts as new.
- This is a lead feed, not procurement or legal advice. Read the official notice before you bid.

## Setup in ten minutes

1. Import `workflow.json` from the [repo folder](https://github.com/ichkifokkus/data-recipes/tree/main/9-sales-signals-daily-feed) into n8n.
2. Create a Header Auth credential (`Authorization` = `Bearer YOUR_APIFY_TOKEN`) and select it in both HTTP nodes.
3. Edit the Settings node.
4. Create a sheet with a tab `Signals` and the header row from the README, then connect Google Sheets and Slack.
5. Optionally enable the Pipedrive node, run once, and activate.

The workflow, the full README with the scoring table and the limits are in the [data-recipes repo](https://github.com/ichkifokkus/data-recipes/tree/main/9-sales-signals-daily-feed). Pull requests welcome.

## Try it

- [German Public Tenders on Apify](https://apify.com/fast_data_asap/german-public-tenders-bund)
- [Career Site Jobs API on Apify](https://apify.com/fast_data_asap/career-site-jobs-api)
- [Workflow + README on GitHub](https://github.com/ichkifokkus/data-recipes/tree/main/9-sales-signals-daily-feed)

**Question for the sales and RevOps people here:** which public signal has actually led to a meeting for you – tenders, hiring, funding news, or something else entirely? I would like to add the one that really works as the next branch.

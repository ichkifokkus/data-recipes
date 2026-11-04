---
title: "Get a Slack alert when a competitor adds or removes product pages (n8n + sitemaps), and why you should ignore lastmod"
published: true
description: "A free n8n workflow that diffs your competitors' sitemaps every morning and posts new and removed product pages to Slack and Google Sheets. Plus what a real test showed: Shopify bumped the lastmod of all 352 Allbirds product URLs at once."
tags: n8n, automation, ecommerce, webdev
---

Your competitors announce new products in many places, but they always update one: their sitemap. A new product page appears there the moment it is published, and a discontinued one disappears. If you compare the sitemap every morning with yesterday's, you get a quiet, reliable launch tracker, no scraping of product pages needed.

This post is a ready-to-import n8n workflow that does exactly that, plus two things I learned while testing it on real sites.

*Disclosure: I built the Apify actor used here, the [Sitemap Change Monitor](https://apify.com/fast_data_asap/sitemap-change-monitor). The workflow is free in our [data-recipes repo](https://github.com/ichkifokkus/data-recipes/tree/main/7-competitor-sitemap-alert).*

## What it does

Every morning at 9:00:

1. The actor reads each competitor's sitemaps (found via `robots.txt`, including nested sitemap indexes and `.gz` files), keeps only URLs matching your patterns (for example `/products/`), and compares them with the list saved on the previous run.
2. It returns one row per change (`new`, `removed`, optionally `updated`) plus one summary row per domain.
3. n8n appends the changes to a Google Sheet and posts a digest to Slack. The format (placeholders, not real data):

```
Competitor sitemap changes: <n> page(s) on <n> site(s)

competitor.com: <n> new, <n> removed, 0 updated
+ <slug of a new product page>
- <slug of a removed product page>
```

The first run only saves a baseline. From the second run on, you see changes.

## The workflow

Six nodes, all built in:

**Every day 9:00** (Schedule Trigger) → **Check competitor sitemaps** (HTTP Request) → **Change rows only** (Code) → **Log to Google Sheets**, and in parallel **Build Slack digest** (Code) → **Post to Slack**.

The HTTP Request calls Apify's synchronous endpoint, so n8n waits for the result and gets the dataset items back in one step:

```
POST https://api.apify.com/v2/acts/fast_data_asap~sitemap-change-monitor/run-sync-get-dataset-items
Authorization: Bearer <your Apify token>   (Header Auth credential in n8n)
```

with this body:

```json
{
  "domains": ["https://www.allbirds.com", "https://your-competitor.com"],
  "includePatterns": ["/products/"],
  "stateKey": "competitors",
  "trackLastmod": false
}
```

The previous URL list is stored per `stateKey` and domain in a key-value store in your own Apify account, so n8n does not need to keep any state. Change the patterns to `/blog/`, `/collections/` or `/pages/` to watch other kinds of pages; changing them starts a fresh baseline.

## What the real test showed

I ran the actor on Allbirds (products) and TechCrunch (November 2026 articles), saved a baseline, and ran it again 28 minutes later.

**1. lastmod is mostly noise on Shopify.** The second run reported **352 of 352 Allbirds product URLs as "updated"**. Every single one had its `lastmod` moved from 20:54 to 23:22 (US Pacific time) on the same day, at the same second. It is very unlikely that someone edited 352 product pages in the same second; more likely the platform regenerated the dates. If you alert on lastmod changes, you get a 352-line Slack message every night and learn nothing.

That is why the recipe sets `"trackLastmod": false`. New and removed URLs are the reliable signal: a URL only appears when a page is published and only disappears when it is unpublished.

**2. Big sites have huge sitemaps.** To find the 56 TechCrunch URLs from November, the actor had to read **2,065 sitemap files**. That works (about three minutes), but for news-sized sites point the actor straight at the one sitemap you care about, or use a narrow include pattern. For a typical shop the whole check takes seconds: Allbirds has 9 sitemaps with 352 product URLs.

In 28 minutes neither site added or removed a page, which is also realistic: product launches happen a few times a week, not every hour. A daily schedule is enough.

## What it costs

The actor charges **$0.003 per domain checked**, and failed domains are free. Five competitors checked daily is about **$0.45 per month**, well inside the free monthly credit of an Apify Free plan. n8n Cloud or a self-hosted n8n handles the rest.

## Setup in five minutes

1. Import `workflow.json` from the [repo folder](https://github.com/ichkifokkus/data-recipes/tree/main/7-competitor-sitemap-alert) into n8n.
2. Create a Header Auth credential: name `Authorization`, value `Bearer YOUR_APIFY_TOKEN`, and select it in the HTTP Request node.
3. Edit `domains` and `includePatterns` in the request body.
4. Connect Google Sheets (a tab named `Changes`) and Slack (channel `#competitors`).
5. Run it once by hand to save the baseline, then leave the schedule on.

## Ideas to extend it

- **Product details for new pages**: pass each new product URL to a product-data actor and add price and availability to the sheet.
- **Weekly summary instead of daily pings**: run daily, but send the Slack message only on Mondays with a count per competitor.
- **Your own site**: watch your own sitemap for pages that disappear by accident after a deploy.

The workflow, README and a sample sheet layout are in the [data-recipes repo](https://github.com/ichkifokkus/data-recipes/tree/main/7-competitor-sitemap-alert). Pull requests welcome.

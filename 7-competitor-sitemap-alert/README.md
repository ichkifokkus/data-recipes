# Recipe 7: Competitor product & page alert (sitemap changes) → Slack + Google Sheets

Every morning, compare your competitors' sitemaps with yesterday and get the **new and removed product pages** (or blog posts, collections, landing pages) in Slack and Google Sheets. A URL appears in a sitemap when a page is published and disappears when it is unpublished, so this is a quiet, reliable launch tracker.

**Actor:** [Sitemap Change Monitor](https://apify.com/fast_data_asap/sitemap-change-monitor) by Fast Data
**n8n nodes:** Schedule Trigger, HTTP Request, Code (2), Google Sheets, Slack

## How it works

1. **Every day 9:00**: Schedule Trigger.
2. **Check competitor sitemaps**: HTTP Request to the Actor's `run-sync-get-dataset-items` endpoint with:
   ```json
   {
     "domains": ["https://www.allbirds.com"],
     "includePatterns": ["/products/"],
     "stateKey": "competitors",
     "trackLastmod": false
   }
   ```
   The Actor finds the sitemaps via robots.txt (sitemap indexes and .gz included), keeps the URLs matching your patterns and compares them with the list saved on the previous run (stored per `stateKey` + domain in your Apify account). The first run saves a baseline only.
3. **Change rows only** → **Log to Google Sheets** (tab `Changes`: `detected_at | domain | change | url | lastmod`).
4. **Build Slack digest** → **Post to Slack** (`#competitors`): new/removed pages per competitor. No message when nothing changed.

## Why `trackLastmod: false`

In a real test (4 Nov 2026) all **352 of 352** Allbirds product URLs had their `lastmod` moved to the same second within one day. Shopify-style platforms regenerate these dates, so lastmod changes are mostly noise. New and removed URLs are the signal. Switch it on only for sites where you know lastmod is maintained by hand.

## Setup (5 minutes)

1. Import `workflow.json` into n8n.
2. Header Auth credential: name `Authorization`, value `Bearer YOUR_APIFY_TOKEN`; select it in *Check competitor sitemaps*.
3. Edit `domains` and `includePatterns`.
4. Connect Google Sheets (tab `Changes`) and Slack.
5. Run once by hand (baseline), then activate.

## Cost

$0.003 per domain checked (failed domains are free): 5 competitors daily ≈ $0.45/month, inside the Apify Free plan's monthly credit.

## Tips

- Very large sites (news publishers) can have thousands of sitemap files (TechCrunch: 2,065 to find one month of articles). Use a narrow `includePatterns` or point `domains` directly at one sitemap URL.
- Changing `includePatterns` starts a new baseline for that domain.
- Watch your own site too: removed URLs after a deploy are often accidents.

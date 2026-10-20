# Recipe 3: Weekly keyword trend report → Google Sheets

Every Monday, pull Google Trends data for a list of keywords and append one row per keyword to a Google Sheet: interest this week vs. last week, change in %, the 90-day average, the peak day and the top rising related searches. After a few weeks the sheet is a trend history you can chart, filter and share.

**Actor:** [Google Trends Scraper](https://apify.com/fast_data_asap/google-trends-scraper) by Fast Data
**n8n nodes:** Schedule Trigger, HTTP Request, Code, Google Sheets

## What you get

Rows appended to the tab `Trends`, from a real test run (US, past 90 days):

| report_date | keyword | geo | this_week | last_week | change_pct | period_avg | peak | rising_queries |
|---|---|---|---|---|---|---|---|---|
| 2026-10-20 | notion | US | 52.9 | 53.4 | -1.1 | 61.1 | Aug 24, 2026 | coursicle (Breakout), notion ai workspace (+200%), ... |
| 2026-10-20 | obsidian | US | 74.1 | 75.1 | -1.3 | 75.6 | Jul 26, 2026 | air jordan 12 obsidian 2027 (Breakout), ... |
| 2026-10-20 | evernote | US | 2.9 | 3.7 | -23.1 | 3.4 | Aug 13, 2026 | how to delete evernote account (Breakout), miro (+300%), ... |

Values are Google Trends' relative interest (0-100) on one shared scale, so you can compare keywords directly. They are not absolute search volumes. The "obsidian" row also shows why rising queries are useful: they reveal when a keyword is ambiguous (the gem, the sneaker colour, the app).

## How it works

1. **Every Monday 8:00**: Schedule Trigger.
2. **Get Google Trends**: HTTP Request to the Actor's `run-sync-get-dataset-items` endpoint. Input:
   ```json
   {
     "searchTerms": ["notion", "obsidian", "evernote"],
     "geo": "US",
     "timeRange": "today 3-m",
     "includeInterestOverTime": true,
     "includeInterestByRegion": false,
     "includeRelatedQueries": true
   }
   ```
   The Actor returns one `interestOverTime` result (daily values for all keywords) and one `relatedQueries` result per keyword.
3. **Weekly summary per keyword**: a Code node. It ignores the last, incomplete data point, averages the last 7 days and the 7 days before, and picks the top 5 rising queries. If you switch to a range with weekly data points (for example `today 12-m`), it compares the last two weeks automatically.
4. **Append to Google Sheets**.

## Setup (about 5 minutes)

1. **Import** `workflow.json` into n8n.
2. **Apify token**: Apify Console → **Settings → API & Integrations** → copy the Personal API token.
3. **Get Google Trends** node: create a **Header Auth** credential, Name `Authorization`, Value `Bearer YOUR_APIFY_TOKEN`.
4. Edit `searchTerms` and `geo` (`US`, `DE`, `GB`, `US-CA`...; empty string = worldwide). You can use more than 5 keywords: the Actor links batches through an anchor keyword so all of them stay on one scale (something the Google Trends website cannot do).
5. Create a spreadsheet with a tab `Trends` and this header row:
   `report_date | keyword | geo | this_week | last_week | change_pct | period_avg | peak | rising_queries`
6. **Append to Google Sheets**: connect Google and select the spreadsheet.
7. **Execute workflow** to test, then set the workflow **Active**.

## Cost

| Item | Price |
|---|---|
| Result (one timeline, one regional breakdown or one related-queries list) | $0.003 |
| This workflow as shipped | 1 timeline + 3 related-query lists = 4 results = **$0.012 per week, about $0.05/month** |
| 20 keywords | 1 timeline + 20 lists = $0.063 per week |

Turn off `includeRelatedQueries` and every run costs only $0.003, regardless of the number of keywords.

## Ideas to adapt it

- **Slack alert on spikes**: add an IF node `change_pct > 30` and a Slack node.
- **Seasonality planning**: one-off run with `"timeRange": "today 5-y"` to see yearly peaks before you plan campaigns.
- **Where is interest highest?**: set `"includeInterestByRegion": true` and `"regionResolution": "REGION"` (or `CITY`) and write the regions to a second tab.
- **YouTube or Shopping trends**: `"searchProperty": "youtube"` or `"shopping"` measures interest in those searches instead of web search.
- **Brand vs. competitors**: track your brand and competitors on one scale; use `"anchorTerm"` with a steady keyword when you track more than 5.

## Troubleshooting

- **401 from Apify**: the credential value must be `Bearer ` + token.
- **Error "No interestOverTime result"**: check the Actor run in Apify Console (Runs tab). Google occasionally rate-limits; the Actor retries with new proxies, and a rerun usually works.
- **Very low numbers for one keyword**: it is compared to the most popular keyword in the list. Use `"compareMode": "separate"` to give each keyword its own 0-100 scale.

## Links

- Actor: https://apify.com/fast_data_asap/google-trends-scraper
- All recipes: [../README.md](../README.md)

Disclosure: the Actor is built and maintained by Fast Data, the authors of this recipe.

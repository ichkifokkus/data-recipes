# Recipe 2: Daily brand & competitor news alert → Slack

Every morning, search Google News for your brand and your competitors, drop everything you have already seen, and post one compact digest to a Slack channel. Optional: send the same digest by e-mail.

**Actor:** [Google News Scraper](https://apify.com/fast_data_asap/google-news-scraper) by Fast Data
**n8n nodes:** Schedule Trigger, HTTP Request, Remove Duplicates, Code, Slack, Send Email (disabled by default)

## What you get

One Slack message per day, grouped by search query, newest first, with links to the original publisher (not Google redirect links). From a real test run:

```
News digest 2026-10-20: 19 new article(s)

OpenAI (10)
- Ex-OpenAI Engineer Detained in Spy Device Case as Saudi Royal Contacts Emerge (The Hacker News)
- OpenAI races to raise $30 billion at $1.4 trillion valuation ahead of Anthropic IPO (CTech)
- EXCLUSIVE: OpenAI seeks to accelerate fundraising ahead of Anthropic IPO, sources say (Reuters)
...

Anthropic (9)
- Former Google CEO Schmidt owns 1% stake in Anthropic, Bloomberg reports (Reuters)
- Anthropic is AI trade's last big hope for a major IPO this year (CNBC)
...
```

If there is nothing new, no message is sent.

## How it works

1. **Every day 7:30**: Schedule Trigger.
2. **Search news**: HTTP Request to the Actor's `run-sync-get-dataset-items` endpoint. Input:
   ```json
   {
     "queries": ["\"OpenAI\"", "\"Anthropic\""],
     "edition": "US:en",
     "timeRange": "1d",
     "maxArticlesPerSource": 10,
     "includeFullText": false
   }
   ```
   Quotes inside a query mean "exact phrase". `timeRange: 1d` = last 24 hours.
3. **New articles only**: Remove Duplicates ("processed in previous executions"), keyed by article URL. Stories that appear two days in a row are posted once.
4. **Build digest**: a Code node that groups the articles by query and builds the Slack text (and an HTML version for e-mail). It returns nothing when there are no new articles, so the workflow stops quietly.
5. **Post to Slack**, and optionally **Send e-mail**.

## Setup (about 5 minutes)

1. **Import** `workflow.json` into n8n.
2. **Apify token**: Apify Console → **Settings → API & Integrations** → copy the Personal API token.
3. **Search news** node: create a **Header Auth** credential with Name `Authorization` and Value `Bearer YOUR_APIFY_TOKEN`.
4. Edit `queries` in the JSON body: your brand, product names, competitors. Google News operators work, for example:
   - `"Acme Corp" -jobs` (exact phrase, exclude a word)
   - `intitle:acme` (word must be in the headline)
   - `"acme" site:techcrunch.com`
5. Pick your edition: `US:en`, `GB:en`, `DE:de`, `FR:fr`, `JP:ja` and 13 more (see the Actor's input page).
6. **Post to Slack**: connect Slack (OAuth or bot token with `chat:write`), set the channel (default `#news-alerts`) and invite the bot to it.
7. Optional: enable **Send e-mail**, add SMTP credentials and set the addresses.
8. **Execute workflow** once to test, then switch it to **Active**.

## Cost

| Item | Price |
|---|---|
| Article (title, source, date, original URL) | $0.0025 |
| Full-text add-on (only if `includeFullText: true` and text was found) | +$0.0025 |
| This workflow as shipped | at most 2 queries × 10 articles = 20 articles/day = $0.05/day, **about $1.50/month** |

Quiet brands return fewer articles and cost less. Duplicates are removed in n8n after the Actor run, so they are still paid; keep `maxArticlesPerSource` close to the number of articles you really expect per day.

## Ideas to adapt it

- **AI summary**: set `"includeFullText": true` and add a Basic LLM Chain after *New articles only*: "Summarise in two sentences and rate the sentiment towards our brand".
- **Only important sources**: add a Filter node that keeps `source` in a list (Reuters, Bloomberg, TechCrunch...).
- **Industry radar instead of brand**: use `"topics": ["TECHNOLOGY", "BUSINESS"]` in addition to or instead of `queries`.
- **Several markets**: duplicate the HTTP node with `"edition": "DE:de"` and merge the outputs.
- **Archive**: add a Google Sheets *Append* node after *New articles only* to keep every article.
- **Microsoft Teams / Discord / Telegram**: replace the Slack node; the `text` field is plain text with Slack-style links.

## Troubleshooting

- **401 from Apify**: the credential value must be `Bearer ` + token.
- **Slack "not_in_channel"**: invite the Slack app to the channel.
- **The first run posts a lot**: the deduplication history is empty on the first run. From the second run on only new articles are posted.
- **"exceeds the maximum history size"**: the deduplication node remembers the last 50,000 keys. Raise *History Size* in that node, or run it once with *Clear Deduplication History*.

## Links

- Actor: https://apify.com/fast_data_asap/google-news-scraper
- All recipes: [../README.md](../README.md)

Disclosure: the Actor is built and maintained by Fast Data, the authors of this recipe. Article texts belong to their publishers.

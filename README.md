# Data Recipes by Fast Data

Free, ready-to-import **n8n workflows** that solve one small data job each: summarise a YouTube channel, get a daily news alert, track keyword trends, watch companies for new job postings, upscale product photos in bulk, turn incoming PDFs into Markdown with an AI summary.

Each recipe is one folder with:

- `workflow.json`: import it into n8n (cloud or self-hosted)
- `README.md`: what it does, step-by-step setup, cost example, ideas for changes
- `devto.md`: a longer write-up of the same recipe

The data comes from public [Apify](https://apify.com) Actors by **Fast Data** ([apify.com/fast_data_asap](https://apify.com/fast_data_asap)). Disclosure: we build and maintain these Actors, and the recipes exist so you can try them in a real workflow in about 10 minutes.

| # | Recipe | Actor | Trigger | Output | Typical cost |
|---|---|---|---|---|---|
| 1 | [YouTube channel to AI summaries](1-youtube-channel-ai-summaries/) | [YouTube Transcript Scraper](https://apify.com/fast_data_asap/youtube-transcript-scraper) | Weekly | Google Sheets (+ OpenAI/Anthropic) | $0.002 per video |
| 2 | [Daily brand & competitor news alert](2-daily-news-alert/) | [Google News Scraper](https://apify.com/fast_data_asap/google-news-scraper) | Daily | Slack (e-mail optional) | ~$1.50/month |
| 3 | [Weekly keyword trend report](3-weekly-trend-report/) | [Google Trends Scraper](https://apify.com/fast_data_asap/google-trends-scraper) | Weekly | Google Sheets | ~$0.05/month |
| 4 | [Hiring-signal alert for target companies](4-hiring-signal-alert/) | [Job Search API](https://apify.com/fast_data_asap/job-search-api) | Daily | Slack + Google Sheets | ~$1/month for 3 companies |
| 5 | [Bulk-upscale product images from a sheet](5-bulk-image-upscale/) | [AI Image Upscaler](https://apify.com/fast_data_asap/ai-image-upscaler) | Manual | Google Drive + Google Sheets | $0.015 per image |
| 6 | [PDF inbox to Markdown and AI summary](6-pdf-inbox-to-markdown/) | [Document to Markdown](https://apify.com/fast_data_asap/document-to-markdown) | New file in Drive / webhook | Google Docs (+ OpenAI) | $0.0015 per page |

Costs are the Actors' pay-per-result prices on the Apify Free and Starter plans (higher plans pay less). You pay only for results; there is no separate compute charge for these Actors. The Apify Free plan includes $5 of usage every month, which covers recipes 2, 3 and 4 running together every month.

## Before you start (once for all recipes)

1. **n8n**: n8n Cloud or self-hosted. All workflows use built-in nodes only, nothing to install. Tested on n8n 2.43; recent 1.x versions (2025 or later) should work too.
2. **Apify account**: sign up free at [apify.com](https://apify.com). No credit card needed for the Free plan.
3. **Apify API token**: in Apify Console go to **Settings → API & Integrations** and copy your **Personal API token**.
4. **One n8n credential for Apify**: in n8n go to **Credentials → Add credential → Header Auth** and enter:
   - Name: `Authorization`
   - Value: `Bearer YOUR_APIFY_TOKEN` (the word `Bearer`, a space, then the token)

   Call it e.g. `Apify API token`. Every recipe uses this credential in its HTTP Request nodes. Never paste the token into the URL or the workflow JSON: credentials are encrypted, workflow JSON is not.

## How the recipes call Apify

Every recipe uses n8n's standard **HTTP Request** node against Apify's synchronous endpoint:

```
POST https://api.apify.com/v2/acts/fast_data_asap~<actor-name>/run-sync-get-dataset-items
Authorization: Bearer <token>
Content-Type: application/json

{ ...Actor input... }
```

It starts the Actor, waits until it has finished and returns the results as a JSON array; n8n turns each result into one item. The JSON body is exactly the Actor's input, so you can design an input in Apify Console (Input tab → JSON view) and paste it into the node.

Why not the Apify node? There is an Apify integration for n8n (the `@apify/n8n-nodes-apify` package), and it works well. We use the plain HTTP Request node because it runs on every n8n instance without installing a community node, and the request is easy to see and debug. If you prefer the Apify node, use its "run Actor and get dataset items" operation with the same Actor and input.

Limits of the synchronous endpoint: Apify waits up to 300 seconds. Runs that take longer return HTTP 408 while the Actor keeps running in Apify. All recipes are sized well below that; recipe 5 splits images into batches for this reason.

## Import a recipe

1. Download the recipe's `workflow.json`.
2. In n8n: **Workflows → Create → ⋯ menu → Import from File** (or copy the file content and paste it onto the canvas).
3. Open each node with a red warning and pick your credentials.
4. Click **Execute workflow** to test, then switch the workflow to **Active** for scheduled recipes.

## How these recipes were tested

Every workflow was imported into n8n 2.43 and checked against n8n's own node definitions (node types, versions, parameters). Each one was then executed end-to-end with real Apify runs of the exact input shown in the recipe; only the steps that need your accounts (Slack, Google Sheets, Google Drive, OpenAI, e-mail) were replaced by placeholders. The example outputs in the READMEs come from those runs (October 2026).

## Use these tools from Claude/Cursor via MCP

All Fast Data Actors can also be called directly by AI agents (Claude, Claude Code, Cursor, VS Code) through **Apify's hosted MCP server**, limited to our Actors:

```
https://mcp.apify.com/?tools=fast_data_asap/youtube-transcript-scraper,fast_data_asap/google-trends-scraper,fast_data_asap/google-news-scraper,fast_data_asap/job-search-api,fast_data_asap/career-site-jobs-api,fast_data_asap/document-to-markdown,fast_data_asap/ai-image-upscaler,fast_data_asap/ai-background-remover,fast_data_asap/bulk-image-downloader
```

Add it as a custom connector in Claude (sign in to Apify via OAuth), or send `Authorization: Bearer <APIFY_TOKEN>` from Cursor or Claude Code. The server is run by Apify, not by us; runs are billed to your Apify account at the Actors' normal prices. Copy-paste configs for each client: [mcp/README.md](mcp/). Registry entry: `io.github.ichkifokkus/fast-data` ([server.json](server.json)).

## License

The workflows and texts in this folder are free to use, copy and change (MIT). The data you collect belongs to its owners; respect copyright, site terms and data protection rules.

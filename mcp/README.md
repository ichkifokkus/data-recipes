# Fast Data Actors via MCP (Claude, Cursor, VS Code, Claude Code)

**What this is, honestly:** this folder contains **no server code**. It is a ready-made configuration for
[Apify's hosted MCP server](https://mcp.apify.com) (`https://mcp.apify.com`, run by Apify), restricted to the
public Apify Actors by **Fast Data** ([apify.com/fast_data_asap](https://apify.com/fast_data_asap)).
We build and maintain these Actors; Apify runs the MCP server. Your AI client talks to Apify, Apify runs the
Actor in your own Apify account, and you pay Apify's normal pay-per-result price for the results.

Registry name: `io.github.ichkifokkus/fast-data` (see [`server.json`](../server.json)).

## Tools you get

| Actor | What the agent can do with it |
|---|---|
| [YouTube Transcript Scraper](https://apify.com/fast_data_asap/youtube-transcript-scraper) | Get transcripts of YouTube videos/channels |
| [Google News Scraper](https://apify.com/fast_data_asap/google-news-scraper) | Search Google News articles for a query |
| [Google Trends Scraper](https://apify.com/fast_data_asap/google-trends-scraper) | Interest over time / related queries for keywords |
| [Job Search API](https://apify.com/fast_data_asap/job-search-api) | Search job postings |
| [Career Site Jobs API](https://apify.com/fast_data_asap/career-site-jobs-api) | Job postings from company career sites |
| [Document to Markdown](https://apify.com/fast_data_asap/document-to-markdown) | Convert PDFs and other documents to Markdown |
| [AI Image Upscaler](https://apify.com/fast_data_asap/ai-image-upscaler) | Upscale images |
| [AI Background Remover](https://apify.com/fast_data_asap/ai-background-remover) | Remove image backgrounds |
| [Bulk Image Downloader](https://apify.com/fast_data_asap/bulk-image-downloader) | Download many images at once |

See each Actor page for the exact input fields and prices.

## Server URL

```
https://mcp.apify.com/?tools=fast_data_asap/youtube-transcript-scraper,fast_data_asap/google-trends-scraper,fast_data_asap/google-news-scraper,fast_data_asap/job-search-api,fast_data_asap/career-site-jobs-api,fast_data_asap/document-to-markdown,fast_data_asap/ai-image-upscaler,fast_data_asap/ai-background-remover,fast_data_asap/bulk-image-downloader
```

Want fewer tools? Delete Actors from the `tools=` list (comma-separated, `owner/actor-name`).

## Authentication

- **OAuth** (Claude.ai / Claude Desktop custom connectors, VS Code): just add the URL, then sign in to Apify in the browser window that opens.
- **API token**: send the header `Authorization: Bearer <APIFY_TOKEN>`. Get the token in Apify Console under **Settings → API & Integrations**. An Apify account is free; the Free plan includes $5 of usage per month.

## Setup

### Claude.ai / Claude Desktop

**Settings → Connectors → Add custom connector**, name it `Fast Data`, paste the server URL above, then connect and sign in to Apify.

### Claude Code

```bash
claude mcp add --transport http fast-data "https://mcp.apify.com/?tools=fast_data_asap/youtube-transcript-scraper,fast_data_asap/google-trends-scraper,fast_data_asap/google-news-scraper,fast_data_asap/job-search-api,fast_data_asap/career-site-jobs-api,fast_data_asap/document-to-markdown,fast_data_asap/ai-image-upscaler,fast_data_asap/ai-background-remover,fast_data_asap/bulk-image-downloader" \
  --header "Authorization: Bearer $APIFY_TOKEN"
```

### Cursor (`~/.cursor/mcp.json` or `.cursor/mcp.json`)

```json
{
  "mcpServers": {
    "fast-data": {
      "url": "https://mcp.apify.com/?tools=fast_data_asap/youtube-transcript-scraper,fast_data_asap/google-trends-scraper,fast_data_asap/google-news-scraper,fast_data_asap/job-search-api,fast_data_asap/career-site-jobs-api,fast_data_asap/document-to-markdown,fast_data_asap/ai-image-upscaler,fast_data_asap/ai-background-remover,fast_data_asap/bulk-image-downloader",
      "headers": { "Authorization": "Bearer YOUR_APIFY_TOKEN" }
    }
  }
}
```

### VS Code (`.vscode/mcp.json`, OAuth)

```json
{
  "servers": {
    "fast-data": {
      "type": "http",
      "url": "https://mcp.apify.com/?tools=fast_data_asap/youtube-transcript-scraper,fast_data_asap/google-trends-scraper,fast_data_asap/google-news-scraper,fast_data_asap/job-search-api,fast_data_asap/career-site-jobs-api,fast_data_asap/document-to-markdown,fast_data_asap/ai-image-upscaler,fast_data_asap/ai-background-remover,fast_data_asap/bulk-image-downloader"
    }
  }
}
```

## Try it

- "Get the transcript of https://www.youtube.com/watch?v=... and summarise it in 5 bullets."
- "What did Google News report about <company> in the last 24 hours?"
- "Is OpenAI hiring more engineers in Europe this month? Use the job search tool."
- "Convert this PDF to Markdown: https://.../report.pdf"

## Notes

- Don't put your token into files you commit. Use OAuth or your client's secret storage where possible.
- More about Apify's MCP server (other options like `ui=true`): [github.com/apify/apify-mcp-server](https://github.com/apify/apify-mcp-server).

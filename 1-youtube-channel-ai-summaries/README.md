# Recipe 1: YouTube channel → AI summaries → Google Sheets

Every Monday, fetch the newest videos of a YouTube channel, summarise each new video with an LLM and add one row per video to a Google Sheet. You get a searchable log of what a channel (yours, a competitor's, a creator you follow) talked about, without watching hours of video.

**Actor:** [YouTube Transcript Scraper](https://apify.com/fast_data_asap/youtube-transcript-scraper) by Fast Data
**n8n nodes:** Schedule Trigger, HTTP Request, Filter, Remove Duplicates, Basic LLM Chain + OpenAI Chat Model, Edit Fields, Google Sheets

## What you get

One row per new video in the tab `Summaries`:

| date | channel | title | url | minutes | words | summary |
|---|---|---|---|---|---|---|
| 2026-10-20 | https://www.youtube.com/@Fireship/videos | The runtime wars are over... and Node won | https://www.youtube.com/watch?v=l3L_lETiSzc | 6 | 1155 | TL;DR: ... key points ... quote ... |

(The first five columns come from a real test run of the workflow's Actor call; the summary depends on your model.)

## How it works

1. **Every Monday 7:00**: Schedule Trigger.
2. **Get transcripts**: HTTP Request to the Actor's `run-sync-get-dataset-items` endpoint. Input:
   ```json
   {
     "startUrls": ["https://www.youtube.com/@Fireship/videos"],
     "maxVideosPerSource": 3,
     "languages": ["en"],
     "includeSegments": false
   }
   ```
   `maxVideosPerSource: 3` takes the three newest videos. `includeSegments: false` drops the timestamped segments, because the summary only needs the full text (`text`).
3. **Has transcript**: keeps videos with `status = ok`. Videos without subtitles come back with a status like `transcripts_disabled` and are not charged.
4. **Only new videos**: Remove Duplicates in "processed in previous executions" mode, keyed by `videoId`. A video is summarised once, even if it is still among the newest three next week.
5. **Summarize transcript**: Basic LLM Chain with an OpenAI Chat Model (`gpt-5-mini`). The prompt asks for a TL;DR, 3-5 key points and one quote. The transcript is cut at 60,000 characters (about 1 hour of speech) to keep LLM costs predictable.
6. **Prepare row** and **Append to Google Sheets**.

## Setup (about 10 minutes)

1. **Import** `workflow.json` into n8n (Workflows → Create → ⋯ → Import from File).
2. **Apify token**: in Apify Console open **Settings → API & Integrations** and copy your Personal API token.
3. **Get transcripts** node: Authentication is already set to *Generic Credential Type → Header Auth*. Create a new credential:
   - Name: `Authorization`
   - Value: `Bearer YOUR_APIFY_TOKEN`
4. Still in **Get transcripts**, replace the channel URL in the JSON body. Any of these work: `https://www.youtube.com/@handle/videos`, a playlist URL, or single video URLs. You can list several.
5. **OpenAI Chat Model**: add your OpenAI API key, or delete the node and attach an **Anthropic Chat Model** (or Gemini, Mistral, Ollama...) to the chain's *Model* input instead.
6. **Google Sheets**: create a spreadsheet with a tab `Summaries` and this header row:
   `date | channel | title | url | minutes | words | summary`
   In **Append to Google Sheets**, connect your Google account and select the spreadsheet.
7. Click **Execute workflow**. After 15-30 seconds the rows appear in the sheet.
8. Switch the workflow to **Active**.

## Cost

| Item | Price |
|---|---|
| Transcript (Actor) | $0.002 per video with a transcript; videos without one are free |
| This workflow as shipped | 3 videos per week, only new ones are summarised: about **$0.006 per week** for Apify |
| Backfill a channel once | 100 videos = $0.20 |
| LLM | a 10-minute video is roughly 2,000 input tokens; with a small model that is a fraction of a cent |

The Apify Free plan's $5 monthly credit is 2,500 transcripts.

## Ideas to adapt it

- **Watch several channels**: add more URLs to `startUrls`. `maxVideosPerSource` applies per channel.
- **Topic monitoring instead of channels**: replace `startUrls` with `"searchQueries": ["n8n tutorial"]` to summarise the top search results.
- **Notion instead of Sheets**: replace the last node with Notion → *Create database page* and map `title`, `url` and `summary`.
- **Other languages**: set `"languages": ["de", "en"]`; the Actor falls back to any available language unless you set `"fallbackToAnyLanguage": false`. You can also ask the LLM to summarise in your language.
- **RAG / chat with a channel**: set `"chunkSizeChars": 1500` and send the `chunks` (with start and end times) to a vector store node instead of the LLM chain.
- **Repurpose content**: change the prompt to "write a LinkedIn post" or "write a newsletter section".

## Troubleshooting

- **401 / 403 from Apify**: the Header Auth value must be `Bearer ` plus the token, with the space.
- **No rows**: the videos may have no subtitles (check the *Has transcript* input), or all of them were already processed. To reprocess, open *Only new videos* and run it once with the operation *Clear Deduplication History*.
- **408 timeout**: the endpoint waits up to 300 seconds. Keep `maxVideosPerSource` modest (up to ~50) per scheduled run.
- **"exceeds the maximum history size"**: the deduplication node remembers the last 50,000 keys. Raise *History Size* in that node, or run it once with *Clear Deduplication History*.

## Links

- Actor: https://apify.com/fast_data_asap/youtube-transcript-scraper
- All recipes: [../README.md](../README.md)

Disclosure: the Actor is built and maintained by Fast Data, the authors of this recipe. Transcripts belong to their creators; make sure your use complies with copyright and YouTube's terms.

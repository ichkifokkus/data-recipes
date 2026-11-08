# Recipe 9: Sales signals: a daily B2B buying-signal feed for your CRM → Slack + Google Sheets

Every weekday at 7:00, collect two kinds of public buying signals, score them and send only the new ones to Slack and a Google Sheet (and, if you like, to your CRM):

- **Public tenders** from the German federal portal service.bund.de that match your keywords ("Software", "Cloud", "Beratung", ...). A public body that is buying is the clearest buying signal there is.
- **Hiring signals** from the career sites of your target accounts. A company that opens several roles at once is growing, reorganising or starting a project.

Both sources are normalised to one schema, so your sales team gets one feed instead of two tools.

**Actors:** [German Public Tenders](https://apify.com/fast_data_asap/german-public-tenders-bund) and [Career Site Jobs API](https://apify.com/fast_data_asap/career-site-jobs-api) by Fast Data
**n8n nodes:** Schedule Trigger, Edit Fields (Set), HTTP Request (2), Merge, Code (3), Google Sheets (2), Slack, Filter, Pipedrive (disabled example)

## What you get

A Slack message like this one. It comes from a real test on Sunday, 8 Nov 2026 (2 tenders for the keyword "Software" from the last 2 days, 4 job postings from 3 companies), run through the workflow's own Code nodes:

```
Sales signals: 6 new (1 high, 3 medium, 2 low)
2 public tender(s), 4 job posting(s)

[high] Tender: Hochschule Zittau/Görlitz - Bereitstellung einer virtuellen Plattform zur Umsetzung digitaler Informationsformate der Studienwerbung - due 2026-11-13
    5 day(s) to end of publication
[medium] Tender: Stadt Regensburg - Einfuehrung und Nutzung eines Archivinformationssystems inklusive eines Digitalen Lesesaals und eines Digitale - due 2026-12-07
    30 day(s) to offer deadline
[medium] Hiring: Tibber - Pricing & Project Lead
    2 role(s) posted at Tibber in the last 7 day(s)
[medium] Hiring: Tibber - AI Commercial Lead - Price Portals
    2 role(s) posted at Tibber in the last 7 day(s)

...and 2 more in the sheet
```

(The two "low" signals were single new roles at n8n and Celonis. Tibber shows 2 roles because the test was capped at 2 jobs per company to keep it cheap.)

…and one row per signal in the tab `Signals`:

`signalId | found_at | signalType | organisation | title | location | date | deadline | url | score | reason`

Only organisations appear in the feed (contracting authority, employer). The workflow does not collect names or contact details of people.

## How it works

1. **Weekdays 7:00**: Schedule Trigger with the cron expression `0 7 * * 1-5` (in the time zone of your n8n instance or workflow settings).
2. **Settings**: one place for all inputs:
   ```json
   {
     "tenderKeywords": ["Software"],
     "tenderStates": [],
     "excludeKeywords": [],
     "lookbackDays": 0,
     "maxTenders": 50,
     "targetCompanies": ["teamtailor:tibber", "ashby:n8n", "greenhouse:celonis"],
     "maxJobsPerCompany": 25
   }
   ```
   `lookbackDays: 0` means automatic: 4 days on Mondays (covers the weekend), 2 days on other weekdays. The one-day overlap makes sure nothing is lost if a run fails; the sheet log removes the duplicates.
3. **Get public tenders** and **Get hiring signals** run in parallel. Each is an HTTP Request to Apify's `run-sync-get-dataset-items` endpoint. The bodies the workflow sends (as recorded on a Sunday):
   ```json
   {"keywords": ["Software"], "states": [], "excludeKeywords": [], "lastDays": 2, "maxItems": 50, "includeDetails": true}
   ```
   ```json
   {"companies": ["teamtailor:tibber", "ashby:n8n", "greenhouse:celonis"], "postedWithinDays": 2, "maxJobsPerCompany": 25, "includeDescription": false}
   ```
4. **Combine** (Merge, append) → **Normalize & score**: a Code node maps both sources to `{signalType, organisation, title, location, date, deadline, url, score}` plus `reason`, `signalId` and `found_at`. Tenders whose deadline has passed are dropped.
5. **Read signal log** (Google Sheets, runs once) → **Keep new signals only**: drops every signal whose `signalId` is already in the sheet. This is the "new since last time" memory, and it lives in your sheet, so you can see and edit it.
6. **Log new signals** (append to the sheet), **Build Slack digest** → **Post to Slack** (`#sales-signals`), and **High score only** → **Create Pipedrive activity** (disabled until you switch it on).

## Scoring logic

Kept simple on purpose, so a salesperson can understand why something is "high". Both thresholds are constants at the top of the *Normalize & score* node.

| Signal | high | medium | low |
|---|---|---|---|
| Public tender | offer deadline (or, if none is published, end of publication) **less than 21 days** away | deadline 21+ days away, or no date published | – |
| Hiring | **3 or more** roles posted at the same company in the lookback window | 2 roles, or a single leadership role (Head of, Director, VP, Chief, Country/General Manager) | a single other role |

Why these rules: a tender with a short deadline needs a bid/no-bid decision this week; a burst of hiring is a stronger signal than one replacement hire. Tune them to your sales cycle, e.g. only count Sales or Engineering titles, or add points for your target states.

## Setup (about 10 minutes)

1. **Import** `workflow.json` into n8n.
2. **Apify credential**: in both HTTP Request nodes select (or create) the **Header Auth** credential: Name `Authorization`, Value `Bearer YOUR_APIFY_TOKEN`. Same credential as in the other recipes.
3. **Settings** node:
   - `tenderKeywords`: German terms work best (`Software`, `IT-Dienstleistungen`, `Cloud`, `Rechenzentrum`, `Beratung`, `Schulung`). Each keyword is searched separately; duplicates are merged by the Actor.
   - `tenderStates`: optional, e.g. `["Bayern", "Baden-Württemberg"]` (exact names: see the [Actor's input](https://apify.com/fast_data_asap/german-public-tenders-bund/input-schema)).
   - `excludeKeywords`: words that remove a tender by title, e.g. `["Reinigung"]`.
   - `targetCompanies`: careers URLs or short forms: `https://boards.greenhouse.io/<slug>`, `https://jobs.lever.co/<slug>`, `https://jobs.ashbyhq.com/<slug>`, `https://<company>.jobs.personio.de`, `teamtailor:<slug>`, Workday career-site URLs, or just a company name (the Actor tries the common systems).
4. **Google Sheets**: create a spreadsheet with a tab `Signals` and the header row
   `signalId | found_at | signalType | organisation | title | location | date | deadline | url | score | reason`.
   Select the same spreadsheet in **Read signal log** and **Log new signals**.
5. **Slack**: connect Slack in **Post to Slack**, set the channel, invite the app to it.
6. **Optional CRM**: connect Pipedrive in **Create Pipedrive activity** and enable the node. It creates a task per high signal, due tomorrow. For HubSpot, replace it with the HubSpot node (e.g. create a task or a company note).
7. **Execute workflow** once, check the sheet, then set it **Active**.

The first run reports everything in the lookback window as new. From the second run on, you only see signals that are not in the sheet yet.

## Cost

Both Actors charge per result; there is no separate compute charge.

| Item | Price (Apify Free/Starter plan) |
|---|---|
| Tender returned | $0.002 |
| Job posting returned | $0.002 (less on higher Apify plans) |
| Real test run (2 tenders + 4 jobs) | 6 results = **$0.012** |
| Typical daily run (e.g. 10 tenders + 15 jobs, each returned twice because of the overlap day) | 50 results = $0.10, about **$2/month** over 21 weekdays |

Ways to pay less: cap `maxTenders` and `maxJobsPerCompany`, set `lookbackDays` to 1 (and accept a small gap risk after a failed run), or use narrow keywords. Large companies (Celonis had 233 open roles on the test day) only cost what falls inside the date window.

## Limits

- **Tenders: Germany, one portal.** service.bund.de aggregates many federal, state and municipal publishers, but not every German contracting body publishes there. The Actor returns what the portal shows (title, authority, place, dates, procedure, CPV codes when given). Some titles are truncated by the portal itself ("Software as a Se..."). Always read the official notice before you decide to bid; this workflow does not give legal or procurement advice.
- **EU tenders (TED): coming soon.** A Fast Data Actor for EU-wide notices from TED is in preparation but not public yet, so it is not part of this workflow. When it is published it will slot in as a third HTTP Request with its own branch in *Normalize & score*.
- **Hiring: only what the career site shows.** Jobs come from the companies' public ATS boards (Greenhouse, Lever, Ashby, SmartRecruiters, Workable, Recruitee, Personio, Teamtailor, Workday). A company with a custom careers site and no supported board returns 0 jobs (in the test, `personio:personio` returned 0). Posting dates are the employer's; a re-posted job counts as new.
- **"3 new roles" is counted per run**, inside the lookback window, before the sheet dedupe. On a Monday the window is 4 days, so bursts are slightly easier to reach.
- **The sheet is the memory.** Deleting rows makes those signals appear again. Very large logs (tens of thousands of rows) slow the read step; archive old rows to a second tab.
- Timeout: Apify's synchronous endpoint waits up to 300 seconds. Both calls in the test finished in under 6 seconds; keep company lists below a few hundred.

## Ideas to adapt it

- **Awarded contracts instead of open calls**: add `awardedContracts: true` to the tender body to see who won which public contract (competitor research).
- **Job seekers' market instead of named accounts**: replace the second HTTP Request with the [Job Search API](https://apify.com/fast_data_asap/job-search-api) and its `keywords` search (job boards including the German Bundesagentur für Arbeit) to find any company hiring for, say, "SAP Basis". Check its input schema for the exact fields; it costs $0.0025 per job.
- **AI summary**: add an LLM node after *Keep new signals only* that writes one sentence per high signal for the account owner.
- **Weekly digest for management**: a second workflow that reads the sheet every Monday and counts signals per organisation.

## Links

- German Public Tenders: https://apify.com/fast_data_asap/german-public-tenders-bund
- Career Site Jobs API: https://apify.com/fast_data_asap/career-site-jobs-api
- All recipes: [../README.md](../README.md)

Disclosure: the Actors are built and maintained by Fast Data, the authors of this recipe. Tender notices and job ads are public, but they belong to their publishers; follow the portals' terms and data protection rules when you store or share them.

# Recipe 4: Hiring-signal alert for a list of companies → Slack + Google Sheets

Watch the career pages of the companies you care about (prospects, competitors, portfolio companies, dream employers). Every morning, new job postings are logged to Google Sheets and summarised in Slack: who is hiring, how many roles, in which teams.

A company that suddenly opens five sales roles in a new country, or its first "Head of Data", is telling you something. Sales teams use this as a buying signal, investors and analysts as a growth signal, job seekers as an early alert.

**Actor:** [Job Search API](https://apify.com/fast_data_asap/job-search-api) by Fast Data
**n8n nodes:** Schedule Trigger, HTTP Request, Remove Duplicates, Code (2), Google Sheets, Slack

## What you get

A Slack message like this one (real test run, 3 companies, postings of the last 2 days):

```
Hiring signals: 13 new role(s) at 3 company(ies)

Stripe: 9 new (Sales 3, Engineering 3, Leadership 1, Marketing 1, Customer 1)
- Account Executive, Velocity Platforms (Hunter) - Chicago, IL; New York, NY; San Franciso, CA
- Backend / API Engineer, Radar - N/A
- Commercial Counsel, Sales - Remote, US
- Country Manager, Israel - Israel
- Engineering Manager, Money as a Service (MaaS) - Singapore
...and 4 more (see the sheet)

Ramp: 2 new (Recruiting & People 2)
- Technical Sourcer - Engineering (Contract) - New York, NY (HQ)
- Lead Recruiter - Executive - New York, NY (HQ)

Palantir: 2 new (Engineering 2)
- Software Engineer, Internship - Query Engines - London, United Kingdom
- Software Engineer, New Grad - Query Engines - London, United Kingdom
```

…and one row per posting in the tab `Jobs`:
`found_at | company | team | title | location | remote | posted_at | url | source`

## How it works

1. **Every day 8:00**: Schedule Trigger.
2. **Get open roles**: HTTP Request to the Actor's `run-sync-get-dataset-items` endpoint. Input:
   ```json
   {
     "companies": ["greenhouse:stripe", "ashby:ramp", "lever:palantir"],
     "postedWithinDays": 2,
     "maxJobsPerSource": 100,
     "includeDescription": false
   }
   ```
   No `keywords`, so only the company career pages are read (no job boards) and all roles are returned. The Actor reads the official public APIs of Greenhouse, Lever, Ashby and SmartRecruiters, so there is no fragile HTML scraping.
3. **New postings only**: Remove Duplicates ("processed in previous executions"), keyed by job URL. This is the "new since the last run" logic: n8n remembers every URL it has seen. `postedWithinDays: 2` gives a one-day overlap, so nothing is missed if a run fails.
4. **Tag team & pick columns**: a Code node guesses the team from the job title (Leadership, Sales, Engineering, Data & AI, ...) and keeps the columns for the sheet.
5. **Log to Google Sheets** and **Build Slack digest** → **Post to Slack**.

## Setup (about 5 minutes)

1. **Import** `workflow.json` into n8n.
2. **Apify token**: Apify Console → **Settings → API & Integrations** → copy the Personal API token.
3. **Get open roles** node: create a **Header Auth** credential, Name `Authorization`, Value `Bearer YOUR_APIFY_TOKEN`.
4. Edit `companies`. Find the company's careers page and use either the URL or the short form:
   - `https://boards.greenhouse.io/stripe` or `greenhouse:stripe`
   - `https://jobs.lever.co/palantir` or `lever:palantir`
   - `https://jobs.ashbyhq.com/ramp` or `ashby:ramp`
   - SmartRecruiters: `smartrecruiters:<company-id>`
5. Create a spreadsheet with a tab `Jobs` and the header row `found_at | company | team | title | location | remote | posted_at | url | source`; select it in **Log to Google Sheets**.
6. **Post to Slack**: connect Slack, set the channel (default `#hiring-signals`), invite the app to the channel.
7. **Execute workflow** once, then set it **Active**.

The first run reports everything posted in the last 2 days as new. From the second run on, only new postings appear.

## Cost

| Item | Price |
|---|---|
| Job returned | $0.0025 ($2.50 per 1,000) |
| This workflow as shipped | the test run returned 13 jobs for 3 companies = $0.0325, **about $1/month** for a daily run |
| 20 mid-size companies | typically 20-60 postings per day = $0.05-0.15 per run |

The overlap day means many postings are returned twice and paid twice; for large companies set `"postedWithinDays": 1` to halve the cost.

## Ideas to adapt it

- **Only certain roles**: add a Filter node after *Tag team & pick columns*, e.g. `team` is `Sales` or `title` contains `Data`.
- **Full job descriptions for AI analysis**: set `"includeDescription": true` and ask an LLM "Which tools and technologies does this company use?". Great for sales research.
- **Job-seeker version**: add `"keywords": "python developer"` and `"remoteOnly": true`. With keywords set, the Actor also searches Remote OK, Himalayas, Arbeitnow and the German Bundesagentur für Arbeit.
- **CRM instead of Slack**: replace the Slack node with HubSpot / Pipedrive and create a task "Company X is hiring 5 sales reps in Germany".
- **Weekly report**: switch the trigger to weekly, `postedWithinDays: 8`.

## Troubleshooting

- **401 from Apify**: the credential value must be `Bearer ` + token.
- **A company returns 0 jobs**: check the slug in the careers URL (`boards.greenhouse.io/<slug>`). Some companies host their board on a custom domain; open a job and look for `greenhouse.io`, `lever.co` or `ashbyhq.com` in the apply link.
- **Too many messages**: it is the first run. Or set `SHOW_TITLES` in *Build Slack digest* to a lower number.
- **"exceeds the maximum history size"**: the deduplication node remembers the last 50,000 keys. Raise *History Size* in that node, or run it once with *Clear Deduplication History*.

## Links

- Actor: https://apify.com/fast_data_asap/job-search-api
- All recipes: [../README.md](../README.md)

Disclosure: the Actor is built and maintained by Fast Data, the authors of this recipe. Job ads may contain recruiter contact details; use them in line with data protection rules.

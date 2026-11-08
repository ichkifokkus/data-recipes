# Agent Tool Catalog: Germany/EU business data for AI agents

A curated, regularly re-checked list of tools and MCP servers that give AI agents reliable **German and EU business data** (finance, compliance, sales signals, public sector). Includes our own Fast Data tools and third-party tools we found useful. Inclusion is editorial and free; nothing here is paid placement.

Machine-readable version: [catalog.json](catalog.json) · Last checked: see `checkedAt` in catalog.json.

| Tool | Provider | Category | What an agent gets | Access | Checked |
|---|---|---|---|---|---|
| [Deutsche Bundesbank MCP](https://pipeworx.io/packs/bundesbank-de) | Pipeworx (pipeworx.io) | finance | Queries Bundesbank statistical time series such as interest rates, exchange rates and banking statistics. | Remote MCP + package | 2026-11-08 |
| [ECB Data Portal MCP](https://pipeworx.io/packs/ecb) | Pipeworx (pipeworx.io) | finance | Pulls European Central Bank statistics (policy rates, FX reference rates, monetary aggregates) as time series. | Remote MCP + package | 2026-11-08 |
| [einvoice checker MCP](https://einvoicechecker.com/mcp/) | einvoicechecker.com | finance | Detects, validates and renders EU e-invoices (XRechnung, ZUGFeRD, Factur-X, Peppol, KSeF) with rule-level errors. | Remote MCP | 2026-11-08 |
| [IBAN Validator & Bank Lookup](https://apify.com/fast_data_asap/iban-validator-bank-lookup) (ours) | Fast Data (fast_data_asap) | finance | Validates IBANs in bulk and adds bank name, BIC and city from official bank registries. | Apify Store / API / MCP | 2026-11-08 |
| [OpenIBAN MCP](https://pipeworx.io/packs/openiban) | Pipeworx (pipeworx.io) | finance | Checks an IBAN's checksum and bank code and resolves bank name, BIC and city via OpenIBAN. | Remote MCP + package | 2026-11-08 |
| [XRechnung & ZUGFeRD / Factur-X Parser](https://apify.com/fast_data_asap/xrechnung-zugferd-einvoice-parser) (ours) | Fast Data (fast_data_asap) | finance | Parses German/EU e-invoices (XRechnung, ZUGFeRD, Factur-X) into JSON with parties, IBAN, totals, VAT breakdown and line items. | Apify Store / API / MCP | 2026-11-08 |
| [XRechnung Validator MCP (checkxrechnung.com)](https://checkxrechnung.com) | RechnungCheck (checkxrechnung.com) | finance | Checks XRechnung XML and ZUGFeRD/Factur-X PDFs against the current KoSIT rule set and explains each error code. | Local MCP | 2026-11-08 |
| [ZUGFeRD Validator](https://zugferd-validator.de) | zugferd-validator.de | finance | Validates ZUGFeRD/Factur-X and XRechnung invoices against EN 16931 and suggests corrections. | Remote MCP + package | 2026-11-08 |
| [BaFin Warnings Scraper](https://apify.com/fast_data_asap/bafin-investor-warnings) (ours) | Fast Data (fast_data_asap) | compliance | Lists current BaFin investor warnings and screens company names or domains against them with a match score. | Apify Store / API / MCP | 2026-11-08 |
| [E-Invoice Map](https://einvoicemap.com/en/use-with-ai-assistants/) | einvoicemap.com | compliance | Answers read-only questions on e-invoicing mandate dates by country, Peppol providers and validation error codes. | Remote MCP | 2026-11-08 |
| [EU VAT Number Validator (VIES)](https://apify.com/fast_data_asap/eu-vat-number-validator) (ours) | Fast Data (fast_data_asap) | compliance | Checks EU VAT IDs against the official VIES service and returns validity plus registered name and address where shared. | Apify Store / API / MCP | 2026-11-08 |
| [EU VIES MCP](https://pipeworx.io/packs/vies-eu) | Pipeworx (pipeworx.io) | compliance | Validates EU VAT numbers live against the European Commission's VIES system, including member-state availability. | Remote MCP + package | 2026-11-08 |
| [EUR-Lex MCP Server](https://github.com/cyanheads/eur-lex-mcp-server) | cyanheads (open source) | compliance | Searches EU legislation, CJEU case law and treaties via EUR-Lex/CELLAR with EuroVoc concepts. | Remote MCP + package | 2026-11-08 |
| [German Court Decisions](https://apify.com/fast_data_asap/german-federal-court-decisions) (ours) | Fast Data (fast_data_asap) | compliance | Returns German federal court decisions (BGH, BVerfG, BAG and others) from the official open-data portal. | Apify Store / API / MCP | 2026-11-08 |
| [German Law MCP](https://github.com/Ansvar-Systems/German-law-mcp) | Ansvar Systems | compliance | Queries German federal statutes and related case law from gesetze-im-internet.de with citations. | Local MCP + hosted | 2026-11-08 |
| [German Shop Legal Check](https://apify.com/fast_data_asap/german-shop-compliance-checker) (ours) | Fast Data (fast_data_asap) | compliance | Checks German online shops for common warning-letter risks such as Impressum, unit prices and accessibility notices. | Apify Store / API / MCP | 2026-11-08 |
| [OpenSanctions MCP](https://pipeworx.io/packs/open-sanctions) | Pipeworx (pipeworx.io) | compliance | Searches OpenSanctions for sanctioned entities and politically exposed persons for KYC/AML screening. | Remote MCP + package | 2026-11-08 |
| [Sanctions Screening MCP Server](https://github.com/cyanheads/sanctions-screening-mcp-server) | cyanheads (open source) | compliance | Screens names against eleven sanctions and export-control lists (incl. EU and UN) and resolves GLEIF entities. | Remote MCP + package | 2026-11-08 |
| [Arbeitsagentur Job Search API](https://apify.com/fast_data_asap/job-search-api) (ours) | Fast Data (fast_data_asap) | sales-signals | Searches German Federal Employment Agency job postings by keyword, city and radius as a hiring signal. | Apify Store / API / MCP | 2026-11-08 |
| [Arbeitsagentur Jobs Feed](https://apify.com/blackfalcondata/arbeitsagentur-jobs-feed) | Black Falcon Data | sales-signals | Exports job listings from Germany's federal employment agency portal with filters for location and occupation. | Apify Store / API / MCP | 2026-11-08 |
| [Career Site Jobs Scraper](https://apify.com/fast_data_asap/career-site-jobs-api) (ours) | Fast Data (fast_data_asap) | sales-signals | Reads all open jobs from company career sites (Workday, Greenhouse, Lever and more) with a new-jobs-only mode. | Apify Store / API / MCP | 2026-11-08 |
| [German Newsfeed MCP (tagesschau.de)](https://github.com/Jakolo121/german-newsfeed-mcp) | Jakolo121 (open source) | sales-signals | Reads current German national and regional news from the public tagesschau.de API for company and market monitoring. | Local MCP | 2026-11-08 |
| [StepStone Jobs Scraper (Germany)](https://apify.com/valig/stepstone-jobs-scraper) | valig | sales-signals | Collects structured job listings from StepStone Germany to spot which companies are hiring for what. | Apify Store / API / MCP | 2026-11-08 |
| [Ausschreibungsagenten Tender Search](https://www.ausschreibungsagenten.de/entwickler) | Ausschreibungsagenten | public-sector | Searches public procurement notices from 17 German, EU and UK sources, always linking to the original notice. | Remote MCP | 2026-11-08 |
| [Bundestag DIP MCP](https://pipeworx.io/packs/bundestag-de) | Pipeworx (pipeworx.io) | public-sector | Searches the Bundestag documentation system (DIP) for bills, printed papers and plenary proceedings. | Remote MCP + package | 2026-11-08 |
| [Destatis MCP](https://pipeworx.io/packs/destatis) | Pipeworx (pipeworx.io) | public-sector | Queries official German statistics tables from Destatis GENESIS-Online. | Remote MCP + package | 2026-11-08 |
| [EU Funding & Tenders MCP](https://pipeworx.io/packs/eu-funding-tenders) | Pipeworx (pipeworx.io) | public-sector | Searches calls for proposals and tenders on the EU Funding & Tenders Portal. | Remote MCP + package | 2026-11-08 |
| [EU TED Tenders Scraper](https://apify.com/foxlabs/ted-tenders) | foxlabs | public-sector | Fetches EU procurement notices, contract awards and RFPs from the official TED API. | Apify Store / API / MCP | 2026-11-08 |
| [Eurostat MCP Server](https://github.com/cyanheads/eurostat-mcp-server) | cyanheads (open source) | public-sector | Searches and queries the Eurostat catalogue for EU economic, demographic, trade and regional data. | Remote MCP + package | 2026-11-08 |
| [German Public Tenders (service.bund.de)](https://apify.com/fast_data_asap/german-public-tenders-bund) (ours) | Fast Data (fast_data_asap) | public-sector | Searches current German public tenders from the federal procurement portal with deadlines and links. | Apify Store / API / MCP | 2026-11-08 |
| [Germany Tenders MCP](https://pipeworx.io/packs/germany-tenders) | Pipeworx (pipeworx.io) | public-sector | Lists official German government tender notices without needing an API key. | Remote MCP + package | 2026-11-08 |
| [TenderAPI](https://tenderapi.eu/en/) | TenderAPI.eu | public-sector | Searches EU tenders from TED and national portals by CPV code, country, buyer or contract value. | Remote MCP | 2026-11-08 |
| [Vergabeweiser](https://vergabeweiser.de/api) | vergabeweiser.de | public-sector | Searches German public tenders and contract awards with deadlines, winners and market figures from open data. | Remote MCP | 2026-11-08 |
| [Agentic Firmenbuch (Handelsregister + Firmenbuch MCP)](https://www.agentic-firmenbuch.at) | Agentic-Firmenbuch | company-data | Gives master data, financials and ratios for companies in the German Handelsregister and Austrian Firmenbuch. | Remote MCP | 2026-11-08 |
| [Bundesanzeiger Scraper](https://apify.com/memo23/bundesanzeiger-scraper) | memo23 | company-data | Retrieves published annual financial statements and filings from the German Federal Gazette with parsed key figures. | Apify Store / API / MCP | 2026-11-08 |
| [Entyrix MCP](https://entyrix.com) | Entyrix | company-data | Provides KYB company briefs, financials, ownership and AML screening from 23 European business registers. | Remote MCP + package | 2026-11-08 |
| [GLEIF LEI MCP](https://pipeworx.io/packs/gleif) | Pipeworx (pipeworx.io) | company-data | Looks up Legal Entity Identifiers and parent/child relationships from the GLEIF database. | Remote MCP + package | 2026-11-08 |
| [Handelsregister API](https://apify.com/radeance/handelsregister-api) | Radeance | company-data | Fetches live company data from handelsregister.de: register court and number, status, address and official documents. | Apify Store / API / MCP | 2026-11-08 |

38 tools (9 by Fast Data, marked "(ours)"). Sorted by category, then alphabetically; our own tools get no special placement. Pricing is as published by each provider on the check date; the provider's page is authoritative. Full access details (MCP URLs, package names) are in [catalog.json](catalog.json).

## Inclusion criteria

- Publicly reachable and clearly documented.
- Actively maintained (release or update in the last ~6 months, or active users in Apify Store).
- Serious provider; official or open data sources preferred.
- No bulk personal data and no scraping behind logins (e.g. no tools that harvest personal e-mail addresses or phone numbers).
- No paid placements. Suggestions are welcome via [GitHub issues](https://github.com/ichkifokkus/data-recipes/issues).

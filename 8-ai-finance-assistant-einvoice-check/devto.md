---
title: "How to build an AI accounts-payable check for German e-invoices with n8n"
published: false
description: "A free n8n workflow that parses XRechnung and ZUGFeRD invoices, checks the supplier's IBAN, EU VAT ID (VIES) and BaFin warnings, and writes a green/yellow/red light to Google Sheets. Plus what happened with the official test invoices."
tags: n8n, automation, fintech, ai
---

Germany is switching B2B invoicing to structured e-invoices. Since January 2025 every business must be able to receive them, and by 2028 most invoices between companies will be XRechnung XML or ZUGFeRD / Factur-X PDFs with embedded XML. For accounts payable that is good news: the IBAN, the supplier's VAT ID and the amounts are no longer pixels in a PDF, they are fields.

Fields can be checked automatically. This post is a ready-to-import n8n workflow that does a first-line check on every incoming e-invoice and gives it a traffic light, before anyone presses "pay". It is also a good building block for an AI finance agent: the agent gets clean, verified facts instead of guessing from a PDF.

*Disclosure: I built the four Apify actors used here. The workflow is free in our [data-recipes repo](https://github.com/ichkifokkus/data-recipes/tree/main/8-ai-finance-assistant-einvoice-check).*

## What it does

You drop an invoice file into a Google Drive folder (or POST its URL to a webhook). Then:

1. **Parse** the invoice: XRechnung (UBL or CII) or ZUGFeRD / Factur-X PDF to flat JSON with seller, buyer, IBAN, totals, VAT breakdown and plausibility warnings.
2. **Check the IBAN**: checksum, length, SEPA flag, and the bank behind the bank code from the official Bundesbank file.
3. **Check the seller's VAT ID** against the EU Commission's VIES service.
4. **Screen the seller name** against current warnings of BaFin, the German financial regulator (unauthorised firms, scam websites, identity clones).
5. A Code node turns the results into **green / yellow / red with reasons**, appends a row to a Google Sheet `Eingangsrechnungen`, and posts red invoices to Slack.

## The workflow

All nodes are built in: Drive Trigger / Webhook → HTTP Request (parse) → three HTTP Requests (IBAN, VAT, BaFin) → Code (traffic light) → Google Sheets and Slack, with small Code nodes in between.

Every HTTP Request calls Apify's synchronous endpoint:

```
POST https://api.apify.com/v2/acts/fast_data_asap~xrechnung-zugferd-einvoice-parser/run-sync-get-dataset-items
Authorization: Bearer <your Apify token>   (Header Auth credential in n8n)

{ "fileUrls": ["https://.../invoice.xml"], "includeLineItems": false }
```

The three check calls look the same with their own input:

```json
{ "ibans": ["DE79000000001234567890"], "includeBankInfo": true }
{ "vatNumbers": ["DE123456789"], "maxRetries": 3 }
{ "mode": "screen", "queries": ["Lieferant GmbH"], "minScore": 85, "maxMatchesPerQuery": 1 }
```

Two design choices matter in practice:

- **One call per actor per execution.** A Code node collects the unique IBANs, VAT IDs and seller names of all invoices in the run, and the check nodes use *Execute Once*. Ten invoices from the same supplier cost one VAT check, not ten.
- **Checks never block the run.** The check nodes use *Always Output Data* and *On Error: Continue*. If VIES is down for Italy, that invoice turns yellow with "VIES could not answer"; the rest go through.

## The traffic-light rules

**Red** (do not pay before a human looked at it): the IBAN is invalid, VIES says the VAT ID is invalid, the VAT ID has an impossible format, or the seller name matches a BaFin warning with a score of 85 or more.

**Yellow** (could not verify): not a structured e-invoice, plausibility warnings from the parser (for example totals that do not add up), no IBAN on the invoice, bank code unknown, IBAN country differs from the seller country, VIES unavailable, VIES name differs from the invoice name, or a BaFin near-match.

**Green**: no automatic check found anything.

Each rule is a few lines in one Code node, so you can make it stricter or looser. One catch: German VAT IDs return no company name from VIES, so the name comparison only helps with suppliers from countries that share it.

## What the real test showed

I ran the four actors on the two public test invoices from the parser's example input: KoSIT's official XRechnung test case `01.01a` (UBL) and `EN16931_Einfach.pdf` from the Mustang project (a ZUGFeRD PDF).

The **parser** read both in 3 seconds: invoice `123456XX` over 336.90 EUR at 7 % VAT, and invoice `471102` over 529.87 EUR with a 7 % and a 19 % VAT line. Zero plausibility warnings. The ZUGFeRD PDF has no IBAN at all in its XML.

Then the checks, and this is the interesting part:

- The **IBAN** `DE79 0000 0000 1234 5678 90` passed the checksum and length test, so a simple validator would call it valid. But its bank code is `00000000`, and the actor answered `"Bank code not found in Bundesbank list"`.
- The **VAT ID** `DE123456789`, used by both test invoices, has a valid format. VIES said `invalid`.
- **BaFin**: `Lieferant GmbH` was screened against 60 current warnings and measures, no match (best score 50). (33 seconds, it reads the live warning pages).

So both official test invoices end up **red**. That is the correct result: test files use placeholders that are formally perfect but do not exist. It is also the best argument for this workflow. A format check would have passed both invoices; the registry checks did not.

With real supplier invoices you will see mostly green, and yellow when a supplier leaves out the IBAN or VIES has a bad day.

## What it costs

The actors charge per result, and failed items are free:

- parse: $0.003 per invoice
- IBAN: $0.0005
- VAT ID: $0.001
- BaFin screening: $0.01 per name

That is **$0.0145 per invoice**, about $1.45 for 100 invoices a month. BaFin is the largest part; screen long-standing suppliers once a month instead and a repeat invoice costs $0.0045.

## What it does not do

This is a technical plausibility check, not tax or legal advice. It does not tell you whether an invoice satisfies § 14 UStG or whether you may deduct the input VAT.

The BaFin data covers roughly the last five weeks of warnings, because that is what BaFin publishes in machine-readable form. It is a check against current warnings, not a historical archive.

And it does not catch the most common invoice fraud: a real supplier's invoice with a changed IBAN that is perfectly valid, just not the supplier's. For that, add a supplier master-data tab and a rule "IBAN differs from the known IBAN". It is the first extension I would build.

## Setup in ten minutes

1. Import `workflow.json` from the [repo folder](https://github.com/ichkifokkus/data-recipes/tree/main/8-ai-finance-assistant-einvoice-check).
2. Create a Header Auth credential (`Authorization` / `Bearer YOUR_APIFY_TOKEN`) and select it in the four HTTP nodes.
3. Create a Drive folder, share it by link, and pick it in the trigger (or use the webhook with presigned URLs).
4. Connect Google Sheets (tab `Eingangsrechnungen`) and Slack.
5. Activate and drop the KoSIT test invoice into the folder: you should get a red row.

The workflow, the README with all rules and the sheet layout are in the [data-recipes repo](https://github.com/ichkifokkus/data-recipes/tree/main/8-ai-finance-assistant-einvoice-check). If you would rather give these checks to Claude or Cursor directly, the same actors are available as MCP tools in the repo's Finance & Sales pack.

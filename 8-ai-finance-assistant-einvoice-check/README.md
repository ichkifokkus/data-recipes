# Recipe 8: AI finance assistant: check incoming e-invoices automatically → Google Sheets + Slack

Drop an incoming e-invoice (XRechnung XML or ZUGFeRD / Factur-X PDF) into a Google Drive folder, or send its URL to a webhook. The workflow reads the invoice, checks the supplier's **IBAN**, **VAT ID (EU VIES)** and **name against BaFin warnings**, and writes a **traffic light (green / yellow / red) with reasons** to a Google Sheet `Eingangsrechnungen`. Red invoices are posted to Slack (e-mail optional) before anyone pays them.

Since 2025 every German business must be able to receive e-invoices, and from 2027/2028 most B2B invoices will arrive that way. Structured invoices make an automatic pre-check easy: the fields are already there, so nobody has to type an IBAN into three websites. This workflow is that pre-check, as a building block your AI agent or your accounts-payable team can rely on.

**Actors** (all by Fast Data): [XRechnung & ZUGFeRD Parser](https://apify.com/fast_data_asap/xrechnung-zugferd-einvoice-parser), [IBAN Validator & Bank Lookup](https://apify.com/fast_data_asap/iban-validator-bank-lookup), [EU VAT Number Validator (VIES)](https://apify.com/fast_data_asap/eu-vat-number-validator), [BaFin Warnings Scraper](https://apify.com/fast_data_asap/bafin-investor-warnings)
**n8n nodes:** Google Drive Trigger, Webhook, HTTP Request (4), Code (4), Google Sheets, Slack, Send Email (optional)

## What you get

One row per invoice in the tab `Eingangsrechnungen`:

`checked_at | light | reasons | file | invoice_number | issue_date | due_date | seller | seller_vat_id | vies_status | iban | bank | bafin_match | amount_due | currency | format | source_url`

and, only if at least one invoice is red, a Slack message. This is the real output for the two public test invoices used below (8 Nov 2026):

```
:red_circle: 2 incoming invoice(s) need a manual check before payment

[Seller name] | invoice 123456XX | 336.9 EUR
   VAT ID DE123456789 is not valid according to VIES; IBAN checksum OK, but: Bank code not found in Bundesbank list

Lieferant GmbH | invoice 471102 | 529.87 EUR
   VAT ID DE123456789 is not valid according to VIES; No IBAN on the invoice (direct debit, card or other payment means?)
```

Both are red, and that is correct: see [What the real test showed](#what-the-real-test-showed).

## How it works

1. **New invoice in Drive** (polled every minute) or **Webhook: check invoice URL** (`POST {"url": "https://.../invoice.xml"}` or `{"urls": [...]}`).
2. **Collect invoice files**: keeps XML and PDF files and builds one list, so each Actor starts **once per execution**, however many invoices arrived. Drive files are passed as `https://drive.google.com/uc?export=download&id=<id>`.
3. **Parse e-invoices**: [xrechnung-zugferd-einvoice-parser](https://apify.com/fast_data_asap/xrechnung-zugferd-einvoice-parser)
   ```json
   { "fileUrls": ["https://.../invoice.xml"], "includeLineItems": false }
   ```
   XRechnung UBL and CII, ZUGFeRD / Factur-X PDFs (the embedded XML is extracted). Returns seller, buyer, IBAN, totals, VAT breakdown and plausibility warnings (e.g. totals that do not add up).
4. **Collect check inputs**: unique IBANs, seller VAT IDs and seller names of all parsed invoices.
5. **Check IBANs**: [iban-validator-bank-lookup](https://apify.com/fast_data_asap/iban-validator-bank-lookup) with `{ "ibans": [...], "includeBankInfo": true }`. Checksum, length, SEPA flag, bank name and BIC from the Bundesbank BLZ file.
6. **Check VAT IDs**: [eu-vat-number-validator](https://apify.com/fast_data_asap/eu-vat-number-validator) with `{ "vatNumbers": [...], "maxRetries": 3 }` against the European Commission's VIES service.
7. **Screen BaFin warnings**: [bafin-investor-warnings](https://apify.com/fast_data_asap/bafin-investor-warnings) with `{ "mode": "screen", "queries": [seller names], "minScore": 85, "maxMatchesPerQuery": 1, "includeMeasures": true }`.
8. **Traffic light** (Code) → **Log to Google Sheets** and **Red invoices only** → **Post to Slack** / **Send e-mail**.

Steps 5 to 7 use *Execute Once*, *Always Output Data* and *On Error: Continue*, so a VIES outage or an invoice without IBAN never stops the run; the missing check simply turns the invoice yellow.

## Traffic-light logic

| Light | Meaning | Triggered by |
|---|---|---|
| 🔴 red | Do not pay before a human has checked | IBAN invalid (checksum, length or format) · VIES says the seller VAT ID is **invalid** · VAT ID has an invalid format · seller name matches a BaFin warning (score ≥ 85) |
| 🟡 yellow | Something could not be verified | file is not a readable XRechnung/ZUGFeRD (e.g. plain PDF) · parser plausibility warnings · no IBAN on the invoice · IBAN valid but bank code unknown · IBAN country differs from seller country · IBAN outside SEPA · no VAT ID (only a Steuernummer) · VIES unavailable · VIES company name differs from invoice name · BaFin similarity score 70-84 · a check did not answer |
| 🟢 green | All automatic checks passed | none of the above |

`reasons` lists every red and yellow finding, red first. Change the rules in the *Traffic light* Code node; each check is one short block.

Note on names: German VAT IDs return **no company name** from VIES (Germany does not share it), so the name comparison only works for suppliers from countries that do (e.g. IE, NL, AT, FR).

## Setup (about 10 minutes)

1. **Import** `workflow.json` into n8n.
2. **Apify token**: Apify Console → **Settings → API & Integrations** → copy the Personal API token.
3. In the four HTTP Request nodes select one **Header Auth** credential: Name `Authorization`, Value `Bearer YOUR_APIFY_TOKEN`.
4. Create a Drive folder `Eingangsrechnungen`, share it as **Anyone with the link: Viewer** (the Actor downloads the file by link), connect Google Drive in *New invoice in Drive* and pick the folder. Prefer not to share the folder? Use the webhook with presigned URLs instead (e.g. from S3 or an Apify key-value store).
5. Create a spreadsheet with a tab `Eingangsrechnungen` and the header row above; select it in **Log to Google Sheets**.
6. **Post to Slack**: connect Slack, set the channel (default `#accounts-payable`), invite the app. Want e-mail instead? Enable **Send e-mail** and add SMTP credentials.
7. Optional: in *Check VAT IDs* add `"requesterVatNumber": "DE..."` (your own VAT ID). VIES then returns a consultation number per valid check that you can keep as proof.
8. **Activate**.

Test without your own invoices:

```bash
curl -X POST https://<your-n8n>/webhook/einvoice-check -H 'Content-Type: application/json' \
  -d '{"url": "https://raw.githubusercontent.com/itplr-kosit/xrechnung-testsuite/master/src/test/business-cases/standard/01.01a-INVOICE_ubl.xml"}'
```

## Cost

Real prices of the four Actors (pay per event, Apify Free and Starter plans):

| Check | Price | Charged when |
|---|---|---|
| Parse e-invoice | $0.003 per invoice | only successfully parsed invoices |
| IBAN | $0.0005 per IBAN | only well-formed IBANs |
| VAT ID (VIES) | $0.001 per number | only numbers VIES answered (valid or invalid) |
| BaFin screening | $0.01 per name | every screened name, hit or not |
| **One invoice, all checks** | **$0.0145** | |

100 invoices a month from 40 different suppliers, processed one by one as they arrive: about **$1.45/month**. The BaFin screening is two thirds of the cost; if most of your invoices come from long-standing suppliers, see *Ideas* below to screen each supplier only once a month. Within one execution, duplicate IBANs, VAT IDs and names are checked once.

## What the real test showed

Test on 8 Nov 2026, all four Actors at 256 MB, with the two public test invoices from the parser's example input:

- [KoSIT XRechnung test case 01.01a](https://raw.githubusercontent.com/itplr-kosit/xrechnung-testsuite/master/src/test/business-cases/standard/01.01a-INVOICE_ubl.xml) (UBL, XRechnung 3.0)
- [Mustang project `EN16931_Einfach.pdf`](https://raw.githubusercontent.com/ZUGFeRD/mustangproject/master/library/src/test/resources/EN16931_Einfach.pdf) (ZUGFeRD/Factur-X PDF, profile EN16931)

| Step | Result | Run time |
|---|---|---|
| Parser | both parsed, `status: ok`, 0 plausibility warnings. KoSIT: invoice `123456XX`, 336.90 EUR (7 % VAT), seller `[Seller name]`, VAT ID `DE 123456789`, IBAN `DE79000000001234567890`. Mustang: invoice `471102`, 529.87 EUR (7 % + 19 %), seller `Lieferant GmbH`, VAT ID `DE123456789`, **no IBAN** in the XML | 3 s |
| IBAN | `DE79 0000 0000 1234 5678 90`: `valid: true` (checksum and length are fine) but bank code `00000000` → `"Bank code not found in Bundesbank list"` | 4 s |
| VAT ID | `DE123456789`: format valid, VIES `status: invalid` | 3 s |
| BaFin | `Lieferant GmbH` screened against 60 current BaFin warnings/measures: `matched: false`, best score 50 | 33 s |

**Test invoices contain placeholders, and the workflow says so.** `DE123456789` is a dummy VAT ID and `DE79000000001234567890` an IBAN with a non-existent bank code. They are built to be formally correct (the IBAN checksum even passes), which is exactly why format checks alone are not enough: VIES and the Bundesbank list reject them, so both test invoices come out **red**. With real supplier invoices you will mostly see green, and yellow where a supplier's invoice has no IBAN or VIES is down.

In the test I screened only `Lieferant GmbH` at BaFin (to keep the test cheap); the workflow screens every seller name, so on the KoSIT invoice it would also screen the placeholder `[Seller name]`, which cannot match anything useful. The *Traffic light* node was run with the real Actor outputs of this test; the workflow itself is built from the same nodes as the other recipes but was not executed end-to-end in n8n with Drive, Sheets and Slack connected.

## Limits (please read)

- **No tax or legal advice.** This is a technical plausibility check. It does not check whether an invoice meets all requirements of § 14 UStG, whether you may deduct input VAT, or whether the service was delivered. Green means "no automatic check found a problem", not "safe to pay".
- **BaFin coverage: only the last ~5 weeks.** The Actor reads the warnings and measures currently listed on bafin.de (60 entries in the test, roughly the last five weeks). Older warnings are not covered, and BaFin only warns about firms in its own remit (unauthorised financial services, scam websites, identity clones). A missing hit says nothing about other kinds of fraud. Every hit must be verified on bafin.de.
- **The classic invoice fraud is not detected here**: a real supplier's invoice with a changed IBAN. The IBAN check catches typos and invented accounts, not a valid account of the wrong person. Compare the IBAN with your supplier master data (see *Ideas*) and confirm changed bank details by phone.
- **VIES** is sometimes slow or down for single member states; those invoices turn yellow, run them again later. German numbers return no name or address.
- **Drive sharing**: the parser downloads files by link. Use a dedicated folder and only share it by link if that fits your data protection rules, or use presigned URLs via the webhook.
- Plain PDFs (no embedded XML) are not read; they turn yellow. For those, combine with [recipe 6](../6-pdf-inbox-to-markdown/) (Document to Markdown) and an LLM.

## Ideas to adapt it

- **Supplier master data**: read a tab `Suppliers` (name, VAT ID, IBAN) with Google Sheets and add a red rule "IBAN differs from the known IBAN of this supplier". This is the single most useful extension.
- **Screen each supplier once a month**: look up the seller in the sheet first and skip the BaFin call if it was screened in the last 30 days. Cuts the cost per repeat invoice to $0.0045.
- **AI agent instead of a person**: give the sheet row to an LLM node with the instruction "draft an e-mail to the supplier asking to confirm the bank details" for every yellow or red invoice.
- **Line items**: set `"includeLineItems": true` and post the lines of large invoices to Slack for approval.
- **Accounting software**: replace Google Sheets with a webhook to your DMS or ERP and attach the light as a tag.

## Troubleshooting

- **401 from Apify**: the credential value must be `Bearer ` + token.
- **Parser says `HTTP 403 while downloading` or not an e-invoice for Drive files**: the folder is not shared by link, or the file is larger than Drive's direct-download limit (virus-scan page). Share the folder, or use the webhook with another URL.
- **All invoices yellow with "check not available"**: one of the check nodes returned an error; open its output in the execution (it continues on error by design).
- **BaFin node takes ~30 s**: normal, it reads the current warning pages on each run.

## Links

- Actors: [E-Invoice Parser](https://apify.com/fast_data_asap/xrechnung-zugferd-einvoice-parser) · [IBAN Validator](https://apify.com/fast_data_asap/iban-validator-bank-lookup) · [EU VAT Validator](https://apify.com/fast_data_asap/eu-vat-number-validator) · [BaFin Warnings](https://apify.com/fast_data_asap/bafin-investor-warnings)
- All recipes: [../README.md](../README.md)
- Same Actors as tools for Claude/Cursor: [Finance & Sales MCP pack](../mcp/#finance--sales-pack)

Disclosure: the Actors are built and maintained by Fast Data, the authors of this recipe. Invoices contain personal and business data; process them in line with GDPR and your retention rules.

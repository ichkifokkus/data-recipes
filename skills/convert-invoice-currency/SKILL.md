---
name: convert-invoice-currency
description: Converts foreign-currency invoice amounts (USD, GBP, CHF, PLN, JPY and about 25 more) into EUR or another ECB currency with the official ECB euro reference rate of the invoice date, flags weekend and holiday fallbacks, and returns the exact ECB source URL per amount as an audit trail. Use when the user asks to convert an invoice or a list of amounts to euros, wants "the ECB rate on the invoice date", needs a Fremdwährungsrechnung or Kreditorenliste in EUR, or asks which exchange rate applies on a Saturday or holiday.
license: MIT
metadata:
  author: fast-data
  version: "1.0"
  tested: "2026-11-11"
---

# Convert invoice amounts with official ECB rates

## When to use

Accounts payable / receivable, expense reports or month-end lists with amounts in foreign currencies.
Typical requests: "Convert these 40 USD and GBP invoices to EUR at the invoice date", "What was CHF 2,999.90 on 30 Oct in euros (ECB)?", "The invoice is dated Saturday, which rate do we use?".

## Tools

Public Apify Actor, via Apify's MCP server
(`https://mcp.apify.com/?tools=fast_data_asap/ecb-exchange-rates-invoice-converter`)
or the Apify API (`POST https://api.apify.com/v2/acts/fast_data_asap~ecb-exchange-rates-invoice-converter/run-sync-get-dataset-items`).

| Actor | Does |
|---|---|
| `fast_data_asap/ecb-exchange-rates-invoice-converter` | Daily ECB euro reference rates (ECB Data Portal, dataset EXR), conversion per row with fallback rule, cross rates via EUR, rounding |

## Steps

1. **Collect rows** from the user, a table or parsed invoices: `amount`, `currency` (ISO code), `date` (`YYYY-MM-DD`, normally the invoice date), optional `id`. Ask which date the company uses (invoice, delivery or payment date) if it is unclear; default to the invoice date.
2. **Choose the fallback rule** for dates without an ECB rate (weekends, TARGET holidays, today before ~16:00 CET): `previous` (default, last earlier fixing day), `next`, or `none` (returns an error row so a human decides).
3. **Call the Actor** once for all rows (mode `convert`):
   ```json
   {
     "mode": "convert",
     "targetCurrency": "EUR",
     "fallback": "previous",
     "items": [
       {"id": "INV-A", "amount": "1.250,00", "currency": "USD", "date": "2026-11-07"},
       {"id": "INV-B", "amount": 1000, "currency": "USD", "date": "2026-11-10", "targetCurrency": "GBP"}
     ]
   }
   ```
   Amounts may be numbers or strings in German or English format. `targetCurrency` can be set per row.
4. **Read each result row**: `status` (`ok` / `error` + `error`), `convertedAmount` (half-up, 2 decimals), `convertedAmountUnrounded`, `rate` (units of `currency` per 1 EUR, as published by the ECB), `targetRate`, `crossRate`, `rateDate` (fixing day actually used), `fallbackUsed`, `daysShifted`, `sourceUrl`.
5. **Report** a table and point out every row with `fallbackUsed: true` (rate of another day) and every `error` row (unknown currency, future date, invalid amount).
6. Only if the user needs a rate series (not conversions): mode `rates` with `currencies`, `startDate`, `endDate` returns one row per currency and fixing day (`date`, `currency`, `rate`, `inverseRate`).

## Output format

| id | amount | currency | → | converted | rate day | rate | note |
|---|---|---|---|---|---|---|---|
| INV-A | 1,250.00 | USD | EUR | 1,119.57 | 2026-11-06 | 1.1165 | invoice date is a Saturday, previous fixing day used |
| INV-B | 1,000.00 | USD | GBP | 745.01 | 2026-11-10 | 1.1214 / 0.83545 | cross rate via EUR |

End with: "Source: ECB euro foreign exchange reference rates (ECB Data Portal); rate URLs per row available." Offer the `sourceUrl` list for the audit file.

## Limits

- The ECB publishes its reference rates **for information purposes only**; it is the user's decision to use them for bookkeeping. **No tax or legal advice**: for VAT, other rates can be prescribed (in Germany, e.g., the monthly average rates published by the Federal Ministry of Finance under § 16 (6) UStG). Tell the user to confirm with their tax advisor which rate applies.
- About 30 currencies (those the ECB publishes); no crypto, no rates before 1999-01-04, no intraday or bank rates.
- The bank's actual conversion of a payment differs; that difference is an FX gain/loss for the accountant.
- No personal data is needed or processed; only amounts, currencies and dates.
- Related: for XRechnung/ZUGFeRD files, our separate parser `fast_data_asap/xrechnung-zugferd-einvoice-parser` extracts `issueDate`, `currency` and `grandTotal`, which map to `date`, `currency` and `amount` here (not part of this skill's tested calls).

## Cost

$0.001 per converted row (`converted-row`) or per daily rate (`rate-row`) on the test date; error rows are free; no start fee. 100 invoices ≈ $0.10. Requires an Apify account (free plan works).

## Tested

2026-11-11, 256 MB, one run with 3 rows: USD 1,250.00 on Sat 2026-11-07 → 1,119.57 EUR (rate 1.1165 of 2026-11-06, `fallbackUsed: true`, `daysShifted: -1`); USD 1,000 on 2026-11-10 → 745.01 GBP (rate 1.1214, `targetRate` 0.83545, `crossRate` 0.7450062422); `XYZ` → `status: "error"` (unknown currency, not charged). Field names above match the actual output.

## Disclosure

This skill uses a Fast Data Actor we maintain (pay per result on Apify). The skill itself is free. Not affiliated with or endorsed by the ECB.

---
name: verify-supplier-de
description: Checks a new or existing supplier (or customer) before payment or onboarding - official company identity from GLEIF (legal name, register number, address, LEI status, parent company), EU VAT number validity via VIES, and the supplier's IBAN (checksum, SEPA, bank name and BIC). Use when the user asks to verify, vet or onboard a supplier, Lieferant, Kreditor or business partner, to check a VAT ID (USt-IdNr.) or IBAN on an invoice, or to do a KYB / Lieferantenprüfung for German or EU companies.
license: MIT
metadata:
  author: fast-data
  version: "1.0"
  tested: "2026-11-10"
---

# Verify a supplier (Germany / EU)

## When to use

Before the first payment to a new supplier, when bank details on an invoice change, or when onboarding a business customer.
Typical requests: "Check this supplier before we pay: Muster GmbH, DE123456789, IBAN DE…", "Is this VAT ID valid?", "Who is the parent company of …?".

## Tools

Public Apify Actors, via Apify's MCP server
(`https://mcp.apify.com/?tools=fast_data_asap/dach-company-kyb-official,fast_data_asap/iban-validator-bank-lookup`)
or the Apify API (`POST https://api.apify.com/v2/acts/<owner>~<actor>/run-sync-get-dataset-items`).

| Actor | Checks |
|---|---|
| `fast_data_asap/dach-company-kyb-official` | Company identity from GLEIF (LEI register) + optional EU VAT check via VIES |
| `fast_data_asap/iban-validator-bank-lookup` | IBAN structure, checksums, SEPA flag, bank name/BIC/city (Germany: Deutsche Bundesbank data) |

## Steps

1. **Collect inputs** from the user or the invoice: company name (or LEI, or register number like `HRB 237558`), country (default `DE`), VAT number if known, IBAN if known.
2. **Company + VAT** – call `fast_data_asap/dach-company-kyb-official`:
   ```json
   {"companies": ["SAP SE; DE143454214", "Siemens Healthineers AG"], "country": "DE", "includeParents": true}
   ```
   A VAT number can follow the name after `;` (or pass `vatNumbers` in the same order as `companies`).
3. **IBAN** – call `fast_data_asap/iban-validator-bank-lookup`:
   ```json
   {"ibans": ["DE89370400440532013000"], "includeBankInfo": true}
   ```
4. **Evaluate** and give a traffic-light verdict per supplier:
   - 🔴 **Stop and clarify:** `found` is false (`No match`) *and* the user expected a registered company; `VAT invalid`; IBAN `valid` is false.
   - 🟡 **Check manually:** flags such as `LEI lapsed (not renewed)`, `Entity inactive`, `Fuzzy name match - verify`, `Name differs from VAT name`, `Multiple matches (n)`; IBAN country differs from the company country.
   - 🟢 **No findings:** company found and active, VAT valid (if checked), IBAN valid.
   Never state that a supplier is "safe" or "trustworthy" – only report what the official sources show.

## Output fields (as returned on 2026-11-10)

- KYB Actor: `query, matchType, found, lei, legalName, legalForm, status, registrationStatus, nextRenewal, registeredAs, jurisdiction, legalAddress{street, postalCode, city, country}, headquartersAddress, directParent{lei, legalName}, ultimateParent{lei, legalName}, vat{number, valid, name, address, checkedAt}, flags[]`.
- IBAN Actor: `input, iban, countryCode, valid, checksumValid, nationalChecksumValid, sepa, bankCode, bankName, bic, bankCity, bankDataSource, error`.

## Output format

```
Supplier check – Siemens Healthineers AG          🟢 No findings
Company:  Siemens Healthineers AG (Aktiengesellschaft), HRB 237558, ACTIVE, LEI ISSUED (renewal 2027-03-05)
Address:  HQ Siemensstr. 3, 91301 Forchheim, DE
Parent:   Siemens Aktiengesellschaft (LEI W38RGI023J3WT1HWRP32)
IBAN:     DE89 3704 0044 0532 0130 00 – valid, SEPA, Commerzbank (COBADEFFXXX), Köln
Sources:  GLEIF, EU VIES, Deutsche Bundesbank (checked 2026-11-10)
```
For several suppliers, use one table row each and list only the flags.

## Limits

- Only companies with an LEI are in GLEIF; many small firms have none (`No match` is then normal – ask for a register extract instead).
- An IBAN check confirms the IBAN is well-formed and which bank it belongs to, **not** who owns the account.
- This is identity data from official sources, not a credit check, sanctions screening or legal/tax advice. For BaFin warnings use `fast_data_asap/bafin-investor-warnings` separately.
- No personal data is collected (organisations only).

## Cost (published prices, 2026-11-10)

- EU Company Check (KYB): $0.004 per company found (VIES check included); no match = free.
- IBAN Validator: $0.0005 per IBAN.
- One supplier with company + IBAN ≈ $0.0045 in the user's own Apify account.

## Tested

2026-11-10: KYB call with `companies: ["Siemens Healthineers AG"]`, `country: "DE"` returned LEI 529900QBVWXMWANH7H45, HRB 237558, ACTIVE/ISSUED, direct and ultimate parent Siemens Aktiengesellschaft. IBAN call with `DE89370400440532013000` returned valid, SEPA, Commerzbank, BIC COBADEFFXXX, Köln (source Deutsche Bundesbank). Both at 256 MB, each under 10 s. The VAT path (`SAP SE; DE143454214` → valid) was verified in the Actor's test run on the same day.

## Disclosure

This skill uses Fast Data actors we maintain ([apify.com/fast_data_asap](https://apify.com/fast_data_asap)). The skill itself is free.

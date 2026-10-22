# Recipe 6: PDF inbox → Markdown → AI summary

Drop a PDF into a Google Drive folder and, a minute later, a Google Doc appears next to it with a short AI summary (what the document is, key facts with page numbers, what needs doing) followed by the full text as clean Markdown. Scanned pages are OCRed automatically. You can also send a document URL to a webhook instead of using Drive.

Typical uses: invoices and receipts, contracts and offers, supplier price lists, reports and papers you want to skim before reading.

**Actor:** [Document to Markdown](https://apify.com/fast_data_asap/document-to-markdown) by Fast Data
**n8n nodes:** Google Drive Trigger, Webhook, Code, HTTP Request, IF, Basic LLM Chain + OpenAI Chat Model, Google Docs (create + update), Edit Fields

## What you get

For every new file, a Google Doc called `Summary - <file name>`:

```
SUMMARY

<one-sentence description, 3-7 key facts with page numbers, "Action needed: ...">

----------
Source: https://drive.google.com/file/d/…/view
Pages: 1 (OCR: 0), words: 326

FULL TEXT (Markdown)

<!-- Page 1 -->
...
```

In our test run we converted a one-page sample AWS invoice (from the open-source [invoice2data](https://github.com/invoice-x/invoice2data) test files). The Actor needed 0.9 seconds for the conversion and about 10 seconds for the whole run, found 326 words, needed no OCR and billed 1 page. The invoice tables came back as Markdown tables:

```markdown
## Invoice Summary

| Invoice Number: | 42183017        |
| --------------- | --------------- |
| Invoice Date:   | August 3 , 2014 |

# Summary

| AWS Service Charges    | $4.11 |
| ---------------------- | ----- |
| Charges                | $4.11 |
| Credits                | $0.00 |
| Tax *                  | $0.00 |
| Total for this invoice | $4.11 |
```

Not everything is perfect: the bill-to address lines came out as `##` headings because they are set in a larger font in the PDF. For an LLM summary that does not matter, but don't use the headings as a reliable outline for invoices.

## How it works

1. **New file in PDF inbox**: Google Drive Trigger, polls one folder every minute for new files.
   **Webhook: convert URL** (optional): `POST /webhook/pdf-inbox` with `{"url": "https://…/file.pdf", "name": "optional"}`, e.g. from a mail parser or a form.
2. **Collect documents**: a Code node turns both into `{ url, name }`, skips folders and unsupported files, and maps native Google Docs/Slides/Sheets to their export links.
3. **Convert to Markdown**: HTTP Request to the Actor's `run-sync-get-dataset-items` endpoint, one run per document:
   ```json
   { "documentUrls": ["<url>"], "ocr": "auto", "includePageBreaks": true }
   ```
   The result has `status`, `markdown`, `title`, `pageCount`, `pagesProcessed`, `ocrPages`, `billedPages` and `wordCount`.
4. **Converted?**: `status = success` goes on; anything else goes to **Conversion failed** (not charged).
5. **Summarize document**: Basic LLM Chain with an OpenAI model (`gpt-5-mini`). The prompt asks for page references, which works because every page starts with `<!-- Page N -->`.
6. **Create Google Doc** + **Write summary + Markdown**: creates the doc and inserts the summary, source info and the full Markdown.

## Setup (about 10 minutes)

1. **Import** `workflow.json` into n8n.
2. **Drive folder**: create a folder, e.g. `PDF inbox`, and share it as **Anyone with the link → Viewer**. The Actor runs in the Apify cloud and downloads each file by its link; it has no access to your Google account. Files you put into the folder inherit the setting.
3. **Apify token**: Apify Console → **Settings → API & Integrations** → copy the Personal API token. Create a **Header Auth** credential, Name `Authorization`, Value `Bearer YOUR_APIFY_TOKEN`, and select it in **Convert to Markdown**.
4. **Google**: connect Google Drive in **New file in PDF inbox** and pick the folder; connect Google Docs in **Create Google Doc** (choose where summaries go, default is the root of My Drive) and **Write summary + Markdown**.
5. **LLM**: add an OpenAI credential in **OpenAI Chat Model**, or replace that node with Anthropic, Gemini, Mistral or a local Ollama model; the chain stays the same.
6. **Activate** the workflow and drop a PDF into the folder.

**Confidential documents?** "Anyone with the link" means anyone who gets the link can open the file. Drive file IDs are long and random, but if that is not acceptable for your documents (contracts, payroll, health data), don't use the Drive folder: send the files from a place you already serve over HTTPS with expiring links (S3 pre-signed URLs, Dropbox links) through the webhook, or run an open-source converter such as MarkItDown on your own server.

## Cost

| Item | Price |
|---|---|
| Normal page (text layer) | $0.0015 ($1.50 per 1,000 pages) |
| Scanned page (OCR) | $0.0065 (page price + $5 per 1,000 OCR pages) |
| 50 invoices of 1-2 pages per month | about $0.10 |
| 200-page report | $0.30 |

Higher Apify plans get up to 25 % off. Failed files are free. The Apify Free plan's $5 monthly credit covers about 3,300 normal pages. The LLM call is billed by your model provider; with a small model a few-page document costs a fraction of a cent.

## Ideas to adapt it

- **Only some pages**: add `"pages": "1-5"` to the body. You only pay for those pages; good for long reports where the executive summary is enough.
- **Notion instead of Google Docs**: replace the two Docs nodes with a Notion *Create Page* node (database item with title, summary, and the Markdown as content).
- **Structured fields instead of prose**: swap the Basic LLM Chain for the *Information Extractor* node and extract `invoice_number`, `date`, `total`, `vendor` into a Google Sheet.
- **E-mail attachments**: forward invoices to a mailbox, save attachments to the Drive folder with the Gmail Trigger + Google Drive *Upload* node, and this workflow takes it from there.
- **RAG**: add `"outputChunks": 1500` and send the chunks (each with `pageStart`/`pageEnd`) to a vector store instead of, or in addition to, the summary.
- **Force OCR** for PDFs with a broken text layer (garbled characters): `"ocr": "always"`.

## Troubleshooting

- **status is not `success`, error mentions 403/401 or an HTML page**: the Drive file is not shared by link. Check the folder sharing (step 2).
- **401 from Apify**: the Header Auth value must be `Bearer ` + token.
- **Nothing triggers**: the Drive Trigger only sees files directly in the watched folder, not in subfolders, and only files created after activation.
- **Empty or very short Markdown for a scan**: the file may be an image-only PDF with a fake text layer; set `"ocr": "always"`.
- **408 timeout**: very large files can exceed the 300-second limit of the synchronous endpoint. Use `"pages"` or split the file.

## Links

- Actor: https://apify.com/fast_data_asap/document-to-markdown
- All recipes: [../README.md](../README.md)

Disclosure: the Actor is built and maintained by Fast Data, the authors of this recipe. Only process documents you are allowed to share with third-party services.

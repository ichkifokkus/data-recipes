# Recipe 5: Bulk-upscale product images from a Google Sheet

Put image URLs into a Google Sheet, click one button, and get every image upscaled 4x with AI (Real-ESRGAN), saved to Google Drive, with the Drive link and the new size written back into the same row. Rows that are already done are skipped, so you can add more URLs and run it again at any time.

Typical uses: small supplier photos for a shop or marketplace listing, old catalogue images, AI-generated images that need print resolution.

**Actor:** [AI Image Upscaler](https://apify.com/fast_data_asap/ai-image-upscaler) by Fast Data
**n8n nodes:** Manual Trigger, Google Sheets (read + update), Filter, Code, HTTP Request (2), IF, Google Drive, Edit Fields (2)

## What you get

Your sheet before (example data):

| image_url | upscaled_url | size | status |
|---|---|---|---|
| https://example.com/img/sku-1001.jpg | | | |
| https://example.com/img/sku-1002.jpg | | | |

…and after:

| image_url | upscaled_url | size | status |
|---|---|---|---|
| https://example.com/img/sku-1001.jpg | https://drive.google.com/file/d/…/view | 3200x3200 | done |
| https://example.com/img/sku-1002.jpg | | | failed: HTTPStatusError: Client error '404 Not Found' for url '…' |

In our test run of this workflow, a 179x179 px JPG became a 716x716 px file (`0014-4x.jpg`, 92 kB) after about one second of processing, and a broken link was written back as `failed` without being charged.

## How it works

1. **Start**: Manual Trigger (click *Execute workflow*).
2. **Read image list**: reads the tab `Images`.
3. **Not done yet**: keeps rows that have an `image_url` and no `upscaled_url`.
4. **Batch URLs**: a Code node groups the URLs into batches of 5. Each batch is one Actor run, which keeps every run far below the 300-second limit of the synchronous API.
5. **Upscale images**: HTTP Request to the Actor's `run-sync-get-dataset-items` endpoint with
   ```json
   { "imageUrls": ["…", "…"], "scale": "4", "outputFormat": "jpg", "quality": 92 }
   ```
   The Actor returns one result per image with `status`, `outputUrl`, `outputWidth` and `outputHeight`.
6. **Upscaled?**: successful images go on to **Download result** → **Save to Google Drive** → **Row: done**. Failed images (broken links, unsupported files) go to **Row: failed** and are not charged.
7. **Write back to sheet**: updates the row whose `image_url` matches.

Why save to Google Drive? The Actor stores results in the Apify run's key-value store. Those links work immediately but, like all unnamed Apify storage, are deleted after your plan's data retention period (7 days on the Free plan at the time of writing). Drive keeps the files for good.

## Setup (about 10 minutes)

1. **Import** `workflow.json` into n8n.
2. Create a spreadsheet with a tab `Images` and the header row `image_url | upscaled_url | size | status`. Paste direct image links (JPG, PNG or WebP) into `image_url`.
3. **Apify token**: Apify Console → **Settings → API & Integrations** → copy the Personal API token.
4. Create a **Header Auth** credential, Name `Authorization`, Value `Bearer YOUR_APIFY_TOKEN`, and select it in **Upscale images** and **Download result**.
5. Connect Google in **Read image list** and **Write back to sheet** (select the same spreadsheet in both) and in **Save to Google Drive** (pick a folder, default is the root of My Drive).
6. Click **Execute workflow**.

Tip: test with 2-3 rows first.

## Cost

| Item | Price |
|---|---|
| Upscaled image | $0.015 ($15 per 1,000); failed images are free |
| 100 product photos | $1.50 |
| 1,000 product photos | $15 |

The Apify Free plan's $5 monthly credit covers about 330 images.

## Ideas to adapt it

- **2x instead of 4x**: `"scale": "2"`, smaller files and enough for most web shops.
- **PNG with transparency**: `"outputFormat": "png"` for logos and cut-out product shots (use a PNG file name in the Drive node or keep the expression, it uses the returned format).
- **Bigger inputs**: images are scaled down to 1 megapixel before upscaling (`maxInputMegapixels`), so 4x gives up to about 16 MP. That is the sweet spot for quality and speed.
- **Run automatically**: replace the Manual Trigger with a Google Sheets Trigger (row added) or a Schedule Trigger.
- **Shopify / WooCommerce**: instead of Drive, upload the downloaded file as a new product image via the shop's node.

## Troubleshooting

- **401 from Apify** in *Upscale images* or *Download result*: both use the same Header Auth credential with `Bearer ` + token.
- **Rows are not updated**: the `image_url` in the sheet must exactly match the URL that was sent (no extra spaces). The workflow trims spaces when it sends URLs; remove leading/trailing spaces in the sheet as well.
- **status "failed: …"**: the link is not a direct image (for example an HTML page or a Google Drive "view" link) or the server blocks downloads.
- **408 timeout**: lower `BATCH_SIZE` in *Batch URLs*.

## Links

- Actor: https://apify.com/fast_data_asap/ai-image-upscaler
- All recipes: [../README.md](../README.md)

Disclosure: the Actor is built and maintained by Fast Data, the authors of this recipe. Only process images you have the rights to use. The model (Real-ESRGAN) is BSD-licensed.

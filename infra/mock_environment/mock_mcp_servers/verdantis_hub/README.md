# Verdantis Hub intranet

Verdantis Hub is the company intranet in the [productivity scenario](../../../../docs/scenarios/productivity/scenario.md). It's the **synced** connector: Microsoft's Enterprise Websites cloud connector crawls it and indexes it for everyone in the tenant. It has no live tools and no write actions, so **it isn't an MCP server**. This folder holds a small website that serves the pages, so links to the Hub (for example, the playbook link in the Notion launch plan) open a real page.

Live site: <https://mock-verdantis-hub.yellowsand-9530f5dc.eastus.azurecontainerapps.io> (Azure Container Apps app `mock-verdantis-hub`; see [DEPLOYMENT.md](../DEPLOYMENT.md)). Every page carries a **Mock intranet · LAB654** badge. The real `verdantis.com` domain belongs to another company, so the lab never links there.

## Where the data lives

The pages are seeded straight into the COEP tenant as `intranetwebsite` items, built by `productivity.intranetpages()` in [`tools/scenarios/productivity/__init__.py`](../../tools/scenarios/productivity/__init__.py) and written to `Connectors_Ignite_EMP/intranetwebsite/intranetwebsite_productivity.jsonl` (one page per line, as COEP's Connector Entity Guide requires). That replaces a crawl for testing, so Copilot answers from the tenant whether or not the site is up. The site and the tenant use the same page data and URLs:

- `export_pages.py` calls `hub_pages()` (the same source `intranetpages()` uses) and writes `seed_files/pages.json` with site-relative links. The site's container image can't import `tools/`, so it reads this file. Re-run the script after changing a page; a test fails if the file is out of date.
- `HUB` in the scenario module is the site's base URL, so the URLs in the tenant items (and in Copilot's citations) open the hosted page.

## Prompts it powers

| Step | What Copilot asks Verdantis Hub for |
|------|--------------------------------|
| 2 | Is shipping signage after the original date allowed if it still arrives 3 days before training? Who approves a split? Answer must cite the current playbook, not the archived one |
| 4 | The partner communication structure for the email to Riley |

## Pages

Base URL `https://mock-verdantis-hub.yellowsand-9530f5dc.eastus.azurecontainerapps.io`. All pages are visible to Everyone.

| Page | Path | Content the demo relies on |
|------|------|----------------------------|
| Retail Partner Launch Playbook | `/retail/launch-playbook` | Every POS kit wave in partner stores at least **3 days** before store staff training. Split shipments allowed with approval from the Retail Ops lead (**Sam Patel**), logged in the Launch Decision Log. Partner changes communicated within **1 business day** |
| Approved Vendors – Print | `/procurement/approved-vendors/print` | Northwind Print (primary). Litware Print (backup): **3-business-day rush, +15% surcharge**, Procurement approval for a PO change |
| Partner Communication Guidelines | `/comms/partner-updates` | Update structure: what changed, impact on you, new dates, what we need from you, contact |

Decoys, to check Copilot picks the current, relevant page:

| Page | Path | Content |
|------|------|---------|
| Retail Partner Launch Playbook (2025, archived) | `/retail/launch-playbook-2025` | Older **5-day** rule, no split shipments; banner says it's superseded |
| Holiday Returns Policy | `/customer-service/holiday-returns` | Unrelated customer policy |
| Verdantis Lumen Launch FAQ | `/products/verdantis-lumen/launch-faq` | A different product's launch |
| Travel & Expense Policy | `/finance/travel-expense-policy` | Unrelated finance policy |

Decoy paths are invented; the doc names only the pages.

## Page requirements

- COEP requires each page body to be at least 2,000 characters and each description at least 150, so the pages carry supporting sections (scope, process, FAQ) around the rules above. That text is authored, not from the doc, and is written not to change the Step 2 answer.
- Each page shows a fixed "Last updated" date between July and September 2026, before any lab run; the archived playbook is over a year old. Unlike Notion, the pages don't mention launch dates, so they don't need to move with the calendar.
- One placeholder author identity, "Verdantis Hub Content Team" (`hubcontent@verdantis.com`), for every page.

## Run locally

From `infra/mock_environment/mock_mcp_servers`:

```powershell
python verdantis_hub/export_pages.py   # after changing pages in the scenario module
$env:PYTHONPATH = "verdantis_hub"
python -m mock_hub                    # http://127.0.0.1:8000 (HOST and PORT override)
python -m pytest verdantis_hub        # tests
```

Routes: `/` (home), each page path, section indexes for any path prefix (for example `/retail`), `/sitemap.xml`, `/robots.txt` and `/healthz`. Unknown paths return 404.

## If the real connector is used

The doc's setup (sections 6.1 and 6.4) applies: static server-rendered HTML (the connector doesn't crawl JavaScript-rendered content), a sitemap listed in `robots.txt`, one Enterprise Websites connection named "Verdantis Hub" with sitemap crawling on, Everyone permissions. The hosted site already meets these: static HTML, `robots.txt` pointing to `sitemap.xml`.

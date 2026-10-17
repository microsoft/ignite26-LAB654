# Verdantis Hub intranet

Verdantis Hub is the company intranet in the [productivity scenario](../../../../docs/scenarios/productivity/scenario.md). It's the **synced** connector: Microsoft's Enterprise Websites cloud connector crawls it and indexes it for everyone in the tenant. It has no live tools and no write actions, so **it isn't an MCP server**. This folder documents the site so it sits next to the other connectors.

## Where the data lives

The pages are seeded straight into the COEP tenant as `intranetwebsite` items, built by `productivity.intranetpages()` in [`tools/scenarios/productivity/__init__.py`](../../tools/scenarios/productivity/__init__.py) and written to `Connectors_Ignite_EMP/intranetwebsite/intranetwebsite_productivity.jsonl` (one page per line, as COEP's Connector Entity Guide requires). That replaces a crawl for testing. No site needs to be hosted unless the lab uses the real Enterprise Websites connector.

## Prompts it powers

| Step | What Copilot asks Verdantis Hub for |
|------|--------------------------------|
| 2 | Is shipping signage on Oct 27 allowed? Who approves a split? Is there a backup print vendor? Answer must cite the current playbook, not the archived one |
| 5 | The partner communication structure for the email to Riley |

## Pages

Base URL `https://hub.verdantis.com` (placeholder). All pages are visible to Everyone.

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
- Each page shows a "Last updated" date. All dates are before Mon Oct 12, 2026 (the shifted "today"); the archived playbook is over a year old.
- One placeholder author identity, "Verdantis Hub Content Team" (`hubcontent@verdantis.com`), for every page.

## If the real connector is used

The doc's setup (sections 6.1 and 6.4) applies: static server-rendered HTML (the connector doesn't crawl JavaScript-rendered content), a sitemap listed in `robots.txt`, one Enterprise Websites connection named "Verdantis Hub" with sitemap crawling on, Everyone permissions. The page HTML in the seed module can be served as-is.

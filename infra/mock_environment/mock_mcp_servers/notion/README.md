# Notion mock server

Mock of the Notion MCP server for the [productivity scenario](../../../../docs/scenarios/productivity/scenario.md). The server isn't built yet. This README specifies the data it must serve; `seed_files/` will hold that data.

Notion is the **federated** connector in this scenario: nothing is indexed, and Copilot reads and writes live as the user.

All dates use the scenario's shifted timeline: "today" is **Mon Oct 12, 2026** (`STORY_DATE` in `tools/scenarios/productivity/__init__.py`).

## Tools to mirror

Match names, descriptions and input schemas to the real Notion MCP server.

| Tool | Used in | Purpose |
|------|---------|---------|
| `notion-search` | Steps 1, 4 | Find the launch plan, sync notes and decision log by name |
| `notion-fetch` | Steps 1, 4 | Read a page's content or a database's schema |
| `notion-query-data-sources` | Step 1 | Query the decision log (and other databases) |
| `notion-create-pages` | Step 4 | Add a row to the Launch Decision Log |
| `notion-update-page` | Step 4 | Edit a page or row (Copilot may use it to fill properties after creating) |

Write tools must change the stored data so a later read shows the new row.

## Prompts it powers

| Step | What Copilot asks Notion for |
|------|------------------------------|
| 1 | Read the Aurora Launch Plan and the latest weekly sync notes; flag that the sync says POS kits must include signage |
| 4 | Add a Launch Decision Log row for the two-wave shipment, with context and links to the playbook and the Smartsheet row |
| 5 | Provide the decision page's link for the partner email |

## Data required

### 1. Page: "Aurora Launch Plan"

| Section | Content |
|---------|---------|
| Goals | Retail launch of the Verdantis Aurora smart-home hub |
| Key dates | Store staff training **Tue Oct 27**; launch event **Tue Nov 3** |
| Owners | Marcus (launch lead); Sam (Retail Ops); workstream owners as in the Smartsheet tracker |
| Links | The Smartsheet "Verdantis Aurora Launch Tracker" and the Verdantis Hub Retail Partner Launch Playbook (`https://hub.verdantis.com/retail/launch-playbook`) |

### 2. Page: "Weekly Sync – Oct 6"

The latest weekly sync (doc: "Weekly Sync – Nov 10", shifted). It must be the most recent sync page.

- Notes include: **"POS kits must include signage – Contoso Retail needs complete kits before staff training."**
- Action items: a few plausible items with owners, none of which resolve the Northwind slip (it hasn't happened yet).

Older sync pages are optional. If included, date them before Oct 6.

### 3. Database: "Launch Decision Log"

| Property | Type | Values |
|----------|------|--------|
| Decision | Title | |
| Owner | Person or text | |
| Approver | Person or text | |
| Status | Select | Proposed, Approved, Rejected |
| Date | Date | |
| Context | Rich text | |
| Links | URL or rich text | |

Seed **3 prior decisions** as examples, dated before Oct 12 and about other Aurora topics (for example the retail price point or the hero video cut), with a mix of statuses. None should be about split shipments or the Northwind slip; Step 4 creates that row.

Step 4's expected new row: Decision "Ship Contoso Retail POS kits in two waves – kits + brochures on Oct 21, signage express on Oct 23 (in stores Oct 24)", Owner Marcus, Approver Sam (Retail Ops), Status Proposed, with context and both links.

## Seats and isolation

- One Notion workspace member per lab seat (`mhollowell01`, `mhollowell02`, …). Each seat needs its own copy of the decision log, or Step 4 rows from different seats collide.
- Reset each seat's pages and database to the seed state between lab runs.

## Consistency rules

- Names match the tenant: Marcus Hollowell (seat user), Sam Patel (Retail Ops lead). Contoso Retail is the partner.
- Dates and the Sam approval rule match the [Verdantis Hub playbook](../verdantis_hub/README.md).

## Open questions

- Is Owner/Approver a Notion person property (needs Notion users for Marcus and Sam per seat) or plain text?

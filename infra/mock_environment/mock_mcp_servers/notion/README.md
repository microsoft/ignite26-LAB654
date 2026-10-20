# Notion mock server

Mock of the Notion MCP server for the [productivity scenario](../../../../docs/scenarios/productivity/scenario.md). The server isn't built yet. This README specifies the data it must serve; `seed_files/` will hold that data.

Notion is the **federated** connector in this scenario: nothing is indexed, and Copilot reads and writes live as the user. It holds the launch tracker, the launch plan and the decision log.

All dates use the scenario's shifted timeline: "today" is **Mon Oct 12, 2026** (`STORY_DATE` in `tools/scenarios/productivity/__init__.py`).

## Tools to mirror

Match names, descriptions and input schemas to the real Notion MCP server.

| Tool | Used in | Purpose |
|------|---------|---------|
| `notion-search` | Steps 1, 3 | Find the tracker, launch plan and decision log by name |
| `notion-fetch` | Steps 1, 3 | Read a page's content, or a database's schema and rows |
| `notion-update-page` | Step 3 | Set the print row's Due and Status |
| `notion-create-pages` | Step 3 | Add a row to the Launch Decision Log |

Copilot may also call `notion-query-data-sources` to filter tracker rows by due date; mirror it if the real server exposes it. Write tools must change the stored data so a later read shows the new values.

## Prompts it powers

| Step | What Copilot asks Notion for |
|------|------------------------------|
| 1 | Scheduled catch-up: tracker tasks due in the next 3 weeks and any vendor updates; flag the Northwind slip against the POS kit shipment |
| 3 | Set "Print brochures & in-store signage" to Due Oct 23 / At Risk; add the two-wave Decision Log entry with context and the playbook link |
| Stretch | Read the whole tracker for an interactive dashboard |

## Data required

### 1. Database: "Verdantis Aurora Launch Tracker"

| Property | Type | Values |
|----------|------|--------|
| Task | Title | |
| Workstream | Select | Retail, PR, Events |
| Owner | Text | |
| Status | Select | Not Started, In Progress, At Risk, Complete |
| Due | Date | |
| Vendor update | Rich text | |

"At Risk" must be a valid option even though no row starts with it (Step 3 sets it).

| Task | Workstream | Owner | Status | Due | Vendor update |
|------|-----------|-------|--------|-----|---------------|
| Print brochures & in-store signage | Retail | Northwind Print | In Progress | Fri Oct 16 | "Paper stock shortage – brochures and signage now deliver Oct 23 instead of Oct 16. We can split: brochures Oct 20, signage Oct 23." |
| Assemble POS kits | Retail | Ops | Not Started | Sun Oct 18 | |
| Ship POS kits to Contoso Retail stores | Retail | Ops | Not Started | Wed Oct 21 | |
| Store staff training | Retail | Contoso Retail | Not Started | Tue Oct 27 | |
| Press briefing deck | PR | Marcus | In Progress | Sat Oct 24 | |
| Launch event run-of-show | Events | Events team | In Progress | Sat Oct 31 | |
| Launch event | Events | All | Not Started | Tue Nov 3 | |

The print row must be the most recently edited row (last edited overnight before Oct 12, e.g. Sun Oct 11 late evening) so "any vendor updates" finds it. Only that row has a Vendor update.

### 2. Page: "Aurora Launch Plan"

| Section | Content |
|---------|---------|
| Goals | Retail launch of the Verdantis Aurora smart-home hub |
| Key dates | Store staff training **Tue Oct 27**; launch event **Tue Nov 3** |
| Owners | Marcus (launch lead); Sam (Retail Ops); workstream owners as in the tracker |
| Rules | **"POS kits must include signage before staff training."** |
| Links | The Verdantis Hub Retail Partner Launch Playbook (`https://hub.verdantis.com/retail/launch-playbook`) |

### 3. Database: "Launch Decision Log"

| Property | Type | Values |
|----------|------|--------|
| Decision | Title | |
| Owner | Person or text | |
| Approver | Person or text | |
| Status | Select | Proposed, Approved, Rejected |
| Date | Date | |
| Context | Rich text | |

There's no Links property; links go in Context. Seed **2 prior decisions** as examples, dated before Oct 12 and about other Aurora topics (for example the retail price point or the press briefing format). None should be about split shipments or the Northwind slip; Step 3 creates that row.

Step 3's expected new row: Decision "Ship Contoso Retail POS kits in two waves (kits + brochures Oct 21; signage express Oct 23, in stores Oct 24)", Owner Marcus, Approver Sam Patel, Status Proposed, Context summarizing the Northwind delay with the playbook link.

### 4. Decoy databases

They test that Copilot picks the right tracker.

| Database | Contents |
|----------|----------|
| Verdantis Lumen Launch Tracker | A different product's launch plan |
| 2025 Holiday Launch Tracker (archived) | Old rows including Northwind Print tasks with 2025 dates |

Decoys need only enough rows to be plausible. None should mention Aurora POS kits with 2026 dates.

## Seats and isolation

- One Notion workspace member per lab seat (`mhollowell01`, `mhollowell02`, …), each with its own copy of every page and database, or Step 3 writes from different seats collide.
- Step 3 changes are made by the seat user, so edits record that user as the author.
- Reset between lab runs: restore the print row and delete lab-created Decision Log entries.

## Consistency rules

- Names match the tenant: Marcus Hollowell (seat user), Sam Patel (Retail Ops lead). "Contoso Retail" and "Northwind Print" are organization names, not users.
- Dates match the shifted timeline in the [scenario doc](../../../../docs/scenarios/productivity/scenario.md); weekdays must be right.
- The Step 2 answer depends on these dates: signage must be in stores by Sat Oct 24 (3 days before training on Oct 27), so Northwind's signage ships express Oct 23. The approval rule matches the [Verdantis Hub playbook](../verdantis_hub/README.md).

## Open questions

- Is Owner/Approver a Notion person property (needs Notion users for Marcus and Sam per seat) or plain text?
- Should the mock store per-seat copies, or one copy reset per run?

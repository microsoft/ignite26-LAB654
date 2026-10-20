# Notion mock server

Mock of the Notion MCP server for the [productivity scenario](../../../../docs/scenarios/productivity/scenario.md). It serves the Verdantis workspace in `seed_files/workspace.json`: the Aurora launch tracker, the launch plan, the decision log and two decoy trackers. There's no sign-in and no MCP Apps widget. The real Notion server doesn't return one in Microsoft 365 Copilot either.

Notion is the **federated** connector in this scenario: nothing is indexed, and Copilot reads and writes live as the user.

All dates use the scenario's shifted timeline: "today" is **Mon Oct 12, 2026** (`STORY_DATE` in `tools/scenarios/productivity/__init__.py`).

## Tools

Names, descriptions, input schemas, output text and error envelopes follow the real Notion MCP server, as recorded in a Cowork session trace.

| Tool | Kind | Used in | Purpose |
|------|------|---------|---------|
| `notion-search` | Read | Steps 1, 3 | Find pages, databases and rows by title and content |
| `notion-fetch` | Read | Steps 1, 3 | Read a page, a database (schema, SQLite table definition, views) or a row |
| `notion-query-data-sources` | Read | Steps 1, 3 | Read database rows, with filters and sorts (`rows` mode) or a small SQL subset (`sql` mode) |
| `notion-update-page` | Write | Step 3 | Change a row's properties or a page's content |
| `notion-create-pages` | Write | Step 3 | Add pages or database rows, for example the Decision Log entry |
| `notion-update-data-source` | Write (destructive) | If needed | Change a database schema, for example add a select option |

Select values are checked against the schema. An unknown value such as `Status: "Blocked"` fails with the real server's `validation_error` text, which tells Copilot to update the data source first.

## How writes work

The server has no sign-in, so it can't tell lab seats apart. Microsoft 365 Copilot and Cowork both send an `x-microsoft-ai-conversationid` header that stays the same for every tool call in one chat. The server keys write state on it:

- Reads return the seed data, plus any changes made earlier **in the same conversation**.
- A write copies the seed into that conversation's own state, then applies the change. Other conversations and other seats never see it.
- A conversation's state is discarded after **2 hours** without a call to the server, or when more than 5,000 conversations have state (least recently used first). A new conversation always starts from the seed, so there's nothing to reset between lab runs.
- A call without the header gets the seed. Its writes return a normal response but aren't kept.
- IDs of created pages are derived from the conversation, so they don't clash and stay the same on retry.

State lives in memory, so run **one replica** (`--max-replicas 1`). A restart or redeploy clears every conversation's changes.

## Run locally

From `infra/mock_environment/mock_mcp_servers`:

```powershell
$env:PYTHONPATH = "_framework;notion"
python -m mock_notion            # streamable HTTP on :8000/mcp
python -m pytest notion          # tests
```

The seed is generated from the scenario data. Edit `seed_files/workspace.json` directly for small changes, and keep IDs unique.

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
| Owner | Text | |
| Approver | Text | |
| Status | Select | Proposed, Approved, Rejected |
| Date | Date | |
| Context | Rich text | |

There's no Links property; links go in Context. The seed has **2 prior Approved decisions**, both before Oct 12: the retail price point (Oct 2) and moving the press briefing from Oct 17 to Oct 24 (Oct 7). None should be about split shipments or the Northwind slip; Step 3 creates that row.

Step 3's expected new row: Decision "Ship Contoso Retail POS kits in two waves (kits + brochures Oct 21; signage express Oct 23, in stores Oct 24)", Owner Marcus, Approver Sam Patel, Status Proposed, Context summarizing the Northwind delay with the playbook link.

### 4. Decoy databases

They test that Copilot picks the right tracker.

| Database | Contents |
|----------|----------|
| Verdantis Lumen Launch Tracker | A different product's launch plan |
| 2025 Holiday Launch Tracker (archived) | Old rows including Northwind Print tasks with 2025 dates |

Lumen rows are dated 2027. Decoys need only enough rows to be plausible. None should mention Aurora POS kits with 2026 dates.

## Consistency rules

- Names match the tenant: Marcus Hollowell (seat user), Sam Patel (Retail Ops lead). "Contoso Retail" and "Northwind Print" are organization names, not users.
- Dates match the shifted timeline in the [scenario doc](../../../../docs/scenarios/productivity/scenario.md); weekdays must be right.
- The Step 2 answer depends on these dates: signage must be in stores by Sat Oct 24 (3 days before training on Oct 27), so Northwind's signage ships express Oct 23. The approval rule matches the [Verdantis Hub playbook](../verdantis_hub/README.md).

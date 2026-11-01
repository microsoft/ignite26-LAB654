# Notion mock server

Mock of the Notion MCP server for the [productivity scenario](../../../../docs/scenarios/productivity/scenario.md). It serves the Zava workspace in `seed_files/workspace.json`: the Aurora launch tracker, the launch plan, the decision log and two decoy trackers. There's no sign-in and no MCP Apps widget. The real Notion server doesn't return one in Microsoft 365 Copilot either.

Notion is the **federated** connector in this scenario: nothing is indexed, and Copilot reads and writes live as the user.

## Dates move with the calendar

Story dates aren't fixed. The seed stores them as offsets from an **anchor**: the Monday of the current week, in US Eastern time. On Saturday and Sunday the anchor is the next Monday. So the scenario always reads as "it's Monday, the print order is due this Friday", whenever someone runs the lab. During lab week (anchor **Mon Nov 16, 2026**) the dates match the scenario spec exactly: print due Fri Nov 20, staff training Tue Dec 1, launch Tue Dec 8.

- Seed values use tokens such as `{{+4|iso}}` (anchor + 4 days, `2026-11-20`), `{{+4|md}}` (`Nov 20`), `{{+22|long}}` (`Tue Dec 8, 2026`) and `{{-3T16:35|ts}}` (a UTC timestamp 3 days before the anchor). `mock_notion/timeline.py` replaces them once per anchor. Decoy trackers have no tokens and keep their fixed dates.
- If a timestamp would be in the future (for example, early on a Monday), all of them move back together so the newest is a few minutes before now. Their order stays the same.
- A conversation keeps the dates it started with, even across midnight on Sunday.
- Created and edited pages are stamped with the real time.
- `STORY_ANCHOR=2026-11-16` pins the anchor; `MOCK_NOW=2026-11-16T14:00:00Z` pins "now" (tests use it). Leave both unset in production.

The tables below give the offset and the lab-week date.

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

## Page viewer

The server also serves browsable, read-only HTML pages in Notion's light theme, so the links in tool results open. Each page has a sidebar, breadcrumbs, and a red **Mock Notion · LAB654** badge saying whether it shows a conversation's changes or the original data. Pages, databases (table view with coloured select pills) and database rows (properties, then content) all render. Content is escaped, so nothing in a page can run script.

| Route | Shows |
|-------|-------|
| `/` | Redirects to the workspace's top page |
| `/p/{id}` | The original (seed) data |
| `/v/{token}/p/{id}` | One conversation's data: its edits and the pages it created |

Set `PUBLIC_BASE_URL` to the server's public address (no trailing slash) to turn this on. Tool results then link to `{base}/v/{token}/p/{id}` when the call has a conversation ID, and `{base}/p/{id}` otherwise. Without it, links stay `https://app.notion.com/p/{id}`. The tools also accept the viewer URLs as page IDs.

The token is the first 20 hex characters of an HMAC-SHA256 of the conversation ID, so a link reveals neither the ID nor any other conversation's data. It's the same before and after the first write, so earlier links keep working. When the conversation's state has expired, or the server restarted, the page shows the original data with a notice. The HMAC key is random per process; set `NOTION_VIEW_SECRET` to keep links stable across restarts (the changes themselves are still lost).

## Run locally

From `infra/mock_environment/mock_mcp_servers`:

```powershell
$env:PYTHONPATH = "_framework;notion"
python -m mock_notion            # streamable HTTP on :8000/mcp
$env:PUBLIC_BASE_URL = "http://127.0.0.1:8000"   # optional: links open the local page viewer
python -m pytest notion          # tests
```

The seed is generated from the scenario data. Edit `seed_files/workspace.json` directly for small changes, and keep IDs unique.

## Prompts it powers

| Step | What Copilot asks Notion for |
|------|------------------------------|
| 1 | Scheduled catch-up: tracker tasks due in the next 3 weeks and any vendor updates; flag the Lucerne Publishing slip against the POS kit shipment |
| 3 | Set "Print brochures & in-store signage" to Due Nov 27 (anchor + 11) / At Risk; add the two-wave Decision Log entry with context and the playbook link |
| Stretch | Read the whole tracker for an interactive dashboard |
## Data required

### 1. Database: "Zava Aurora Launch Tracker"

| Property | Type | Values |
|----------|------|--------|
| Task | Title | |
| Workstream | Select | Retail, PR, Events |
| Owner | Text | |
| Status | Select | Not Started, In Progress, At Risk, Complete |
| Due | Date | |
| Vendor update | Rich text | |

"At Risk" must be a valid option even though no row starts with it (Step 3 sets it).

| Task | Workstream | Owner | Status | Due (offset → lab week) | Vendor update |
|------|-----------|-------|--------|-----|---------------|
| Print brochures & in-store signage | Retail | Lucerne Publishing | In Progress | +4 → Fri Nov 20 | "Paper stock shortage – brochures and signage now deliver Nov 27 instead of Nov 20. We can split: brochures Nov 24, signage Nov 27." (+11, +4, +8, +11) |
| Assemble POS kits | Retail | Ops | Not Started | +6 → Sun Nov 22 | |
| Ship POS kits to Lakeshore Retail stores | Retail | Ops | Not Started | +9 → Wed Nov 25 | |
| Store staff training | Retail | Lakeshore Retail | Not Started | +15 → Tue Dec 1 | |
| Press briefing deck | PR | Emil | In Progress | +12 → Sat Nov 28 | |
| Launch event run-of-show | Events | Events team | In Progress | +19 → Sat Dec 5 | |
| Launch event | Events | All | Not Started | +22 → Tue Dec 8 | |

The print row must be the most recently edited row (edited 03:47 UTC on the anchor day, which is Sunday late evening Eastern) so "any vendor updates" finds it. Only that row has a Vendor update.

### 2. Page: "Aurora Launch Plan"

| Section | Content |
|---------|---------|
| Goals | Retail launch of the Zava Aurora smart-home hub |
| Key dates | Store staff training **Tue Dec 1** (+15); launch event **Tue Dec 8** (+22) |
| Owners | Emil (launch lead); Tama (Retail Ops); workstream owners as in the tracker |
| Rules | **"POS kits must include signage before staff training."** |
| Links | The Zava Hub Retail Partner Launch Playbook (`https://mock-zava-hub.yellowsand-9530f5dc.eastus.azurecontainerapps.io/retail/launch-playbook`, served by the retired Zava Hub mock) |

### 3. Database: "Launch Decision Log"

| Property | Type | Values |
|----------|------|--------|
| Decision | Title | |
| Owner | Text | |
| Approver | Text | |
| Status | Select | Proposed, Approved, Rejected |
| Date | Date | |
| Context | Rich text | |

There's no Links property; links go in Context. The seed has **4 prior decisions**, all before the anchor, so the log shows every status:

| Decision | Status | Date (offset → lab week) |
|----------|--------|------|
| Retail price point | Approved | -10 → Fri Nov 6 |
| Move press briefing from Nov 21 to Nov 28 (+5 to +12) and hold it in person | Approved | -5 → Wed Nov 11 |
| Add a second Lakeshore Retail launch city in Q1 | Rejected | -4 → Thu Nov 12 |
| Extend launch-week support hours | Proposed | -3 → Fri Nov 13 |

None is about split shipments or the Lucerne Publishing slip; Step 3 creates that row. The wording of the Rejected and Proposed rows is authored; the spec names only their titles.

Step 3's expected new row: Decision "Ship Lakeshore Retail POS kits in two waves (kits + brochures Nov 25; signage express Nov 27, in stores Nov 28)", Owner Emil, Approver Tama Surya, Status Proposed, Context summarizing the Lucerne Publishing delay with the playbook link.

### 4. Decoy databases

They test that Copilot picks the right tracker.

| Database | Contents |
|----------|----------|
| Zava Lumen Launch Tracker | A different product's launch plan |
| 2025 Holiday Launch Tracker (archived) | Old rows including Lucerne Publishing tasks with 2025 dates |

Lumen rows are dated 2027. Decoys need only enough rows to be plausible. None should mention Aurora POS kits with 2026 dates.

## Consistency rules

- Names match the tenant: Emil Vanggaard (seat user), Tama Surya (Retail Ops lead). "Lakeshore Retail" and "Lucerne Publishing" are organization names, not users.
- Dates are offsets from the Monday anchor, so weekdays are always right. During lab week they match the [scenario doc](../../../../docs/scenarios/productivity/scenario.md).
- The Step 2 answer depends on these dates: signage must be in stores by Sat Nov 28 (+12, 3 days before training on Dec 1), so Lucerne Publishing's signage ships express Nov 27. The approval rule matches the Zava Hub playbook.

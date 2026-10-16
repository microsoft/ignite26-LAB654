# Smartsheet mock server

Mock of the Smartsheet MCP server for the [productivity scenario](../../../scenarios/productivity/scenario.md). The server isn't built yet. This README specifies the data it must serve; `seed_files/` will hold that data.

Smartsheet is the **hybrid** connector in this scenario: an admin-configured synced index (semantic search over sheets, rows and comments) plus live MCP tools that read and write as the user. The mock covers the live MCP side. See [open questions](#open-questions) for the index.

All dates use the scenario's shifted timeline: "today" is **Mon Oct 12, 2026** (`STORY_DATE` in `tools/scenarios/productivity/__init__.py`).

## Tools to mirror

Match names, descriptions and input schemas to the real Smartsheet MCP server.

| Tool | Used in | Purpose |
|------|---------|---------|
| `get_sheet_summary` | Step 1 | Read the tracker's columns, rows and current values |
| `find_in_sheet` | Step 1 | Find rows and comments by text, e.g. "Northwind" |
| `update_rows` | Step 3 | Change Due Date and Status on two rows |
| `create_discussion` | Step 3 | Add a comment thread on a row |
| `add_comment` | Step 3 | Reply in an existing thread (Copilot may pick this instead of `create_discussion`) |

Write tools must change the stored data so a follow-up live read returns the new values (the scenario's hybrid note).

## Prompts it powers

| Step | What Copilot asks Smartsheet for |
|------|----------------------------------|
| 1 | Find "our Aurora launch tracker" from a fuzzy description (no exact sheet name), list tasks due in the next 3 weeks, and surface new vendor comments |
| 3 | Set "Print brochures & in-store signage" to Due Oct 23 / At Risk; set "Final hero video" to Complete; add the two-wave comment on "Ship POS kits to Contoso Retail stores" |
| Stretch | Read the whole tracker for an interactive dashboard: tasks by workstream, at-risk items, timeline to the Nov 3 launch |

## Data required

### 1. Sheet: "Verdantis Aurora Launch Tracker"

Columns, in order: **Task · Workstream · Owner · Status · Start · Due Date · Depends On · Notes**.

Status values: Not Started, In Progress, At Risk, Complete. "At Risk" must be a valid option even though no row starts with it (Step 3 sets it).

| Task | Workstream | Owner | Status | Due Date |
|------|-----------|-------|--------|----------|
| Final hero video | Creative | Fabrikam Creative | In Progress | Sat Oct 10 |
| Retail pricing sign-off | Commercial | Marcus | Complete | Tue Oct 6 |
| Print brochures & in-store signage | Retail | Northwind Print | In Progress | Fri Oct 16 |
| Assemble POS kits | Retail | Ops | Not Started | Sun Oct 18 |
| Ship POS kits to Contoso Retail stores | Retail | Ops | Not Started | Wed Oct 21 |
| Store staff training | Retail | Contoso Retail | Not Started | Tue Oct 27 |
| Press briefing deck | PR | Marcus | In Progress | Sat Oct 24 |
| Website launch page | Digital | Web team | In Progress | Thu Oct 29 |
| Influencer seeding | Marketing | Marketing | Not Started | Wed Oct 28 |
| Launch event run-of-show | Events | Events team | In Progress | Sat Oct 31 |
| Launch event | Events | All | Not Started | Tue Nov 3 |

The doc doesn't give Start or Depends On values. Suggested, to make the conflict traceable:

| Task | Depends On |
|------|-----------|
| Assemble POS kits | Print brochures & in-store signage |
| Ship POS kits to Contoso Retail stores | Assemble POS kits |
| Store staff training | Ship POS kits to Contoso Retail stores |

Start dates can be any plausible date on or before the due date. Notes can be empty.

"Final hero video" deliberately still says In Progress while its comment says it's approved (Step 1's "good news" and Step 3's status fix).

### 2. Row comments

| Row | Author | When | Text |
|-----|--------|------|------|
| Print brochures & in-store signage | Northwind Print (via update request) | Overnight before Oct 12, e.g. Sun Oct 11 late evening | "Paper stock shortage – brochures and signage now deliver Oct 23 instead of Oct 16. We can split: brochures Oct 20, signage Oct 23." |
| Final hero video | Fabrikam Creative | Before Oct 12, e.g. Fri Oct 9 | "Final cut delivered and approved by brand." |
| Assemble POS kits | Ops (internal) | Before Oct 12, older than the Northwind comment | "Kits need Northwind signage before packing." |

The Northwind comment must be the newest comment on the sheet so "new vendor comments" finds it.

### 3. Decoy sheets

Each seat also sees these. They test that Copilot picks the right tracker.

| Sheet | Contents |
|-------|----------|
| Verdantis Aurora – Retail Readiness Checklist | Store fixture checklist items, no dates |
| 2025 Holiday Launch Tracker (archived) | Old rows including Northwind Print tasks with 2025 dates |
| Verdantis Lumen Launch Tracker | A different product's launch plan |

Decoys need only enough rows to be plausible. None should mention Aurora POS kits with 2026 dates.

## Seats and isolation

- One copy of every sheet per lab seat (`mhollowell01`, `mhollowell02`, …), visible only to that seat's Smartsheet user. Write actions would collide on shared sheets.
- The Step 3 changes are made by the seat user, so updates and comments record that user as the author.
- Reset each seat's sheets to the seed state between lab runs.

## Consistency rules

- Dates match the shifted timeline in the [scenario doc](../../../scenarios/productivity/scenario.md); weekdays must be right.
- Owner names match the tenant and other sources: Marcus is the seat user; "Contoso Retail" and "Northwind Print" are organization names, not users.
- The Step 2 answer depends on these dates: signage must be in stores by Sat Oct 24 (3 days before training on Oct 27), so Northwind's signage ships express Oct 23.

## Open questions

- **Synced index.** The hybrid demo relies on Smartsheet's index for the fuzzy "find our tracker" and "new vendor comments" search. A mock MCP server can't populate that index. Smartsheet isn't one of COEP's supported out-of-box connector types (Schema Master's 3P types are ServiceNow KB, Confluence, Azure DevOps work items and wiki, Google Drive and Enterprise Websites). Options:
  - Seed the index through COEP's `customconnectors` type, which covers connectors outside the out-of-box set. It's unconfirmed whether that faithfully stands in for the partner-published Smartsheet connector.
  - Ask COEP to add Smartsheet as an out-of-box type (connector self-serve validation, then an intake request).
  - Point the real Smartsheet connector at real sheets seeded from this spec.
- Should the mock store per-seat copies, or one copy reset per run?

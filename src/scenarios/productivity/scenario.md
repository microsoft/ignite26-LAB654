# Get work done across Smartsheet, Notion & your intranet

> Converted from `Ignite_Lab_Productivity_Module_Smartsheet_Notion_Intranet.docx` (Ignite Lab200 · Connectors · Productivity module, DRAFT). Wording is preserved; layout is simplified to Markdown.
>
> **Dates are shifted.** The doc's story runs on a Monday "today" of Nov 16, 2026. COEP needs past timestamps, so every story date here, in the tenant seed and in the connector specs is moved back 35 days (5 weeks), keeping weekdays. "Today" is **Mon Oct 12, 2026**, the same lab date as the legal scenario.
>
> **Single lab persona:** one lab account plays all three domains, so Avery is replaced by Marcus Hollowell at Verdantis (the legal persona), Zava becomes Verdantis (a car and home insurer), the Aurora smart speaker becomes a smart-home hub, Jordan (Contoso Retail) becomes Riley so the name doesn't clash with finance's Jordan, and Step 1's prompt no longer states a job title.
>
> | Doc date | Shifted | | Doc date | Shifted |
> |---|---|---|---|---|
> | Tue Nov 10 | Tue Oct 6 | | Fri Nov 27 | Fri Oct 23 |
> | Sat Nov 14 | Sat Oct 10 | | Sat Nov 28 | Sat Oct 24 |
> | Mon Nov 16 (today) | Mon Oct 12 | | Tue Dec 1 | Tue Oct 27 |
> | Fri Nov 20 | Fri Oct 16 | | Wed Dec 2 | Wed Oct 28 |
> | Sun Nov 22 | Sun Oct 18 | | Thu Dec 3 | Thu Oct 29 |
> | Tue Nov 24 | Tue Oct 20 | | Sat Dec 5 | Sat Oct 31 |
> | Wed Nov 25 | Wed Oct 21 | | Tue Dec 8 | Tue Nov 3 |

Scenario design and lab readiness plan for a 10-minute hands-on module.

| | |
|---|---|
| **Lab** | Supercharge Copilot: Connect your work data & Get work done with Copilot Connectors (Lab200, 75 min) |
| **Module** | [Productivity] Complete end-to-end productivity workflows with MCP apps and skills |
| **Module DRI** | Danny (also Lab Readiness DRI) |
| **Time budget** | 10 minutes (+3 min stretch for fast finishers) |
| **Connectors** | Smartsheet (hybrid) · Notion (federated) · Verdantis Hub intranet (synced · Enterprise Websites) |
| **Status** | DRAFT for review |

## 1. Summary

Participants play Marcus, who is coordinating a product launch whose print vendor just slipped. The information they need is spread across a project tracker (Smartsheet), a team wiki (Notion), and the company intranet (Verdantis Hub), where the retail playbook sets the rules. In 10 minutes they use Microsoft 365 Copilot to get one grounded catch-up, check the fix against company policy, update the plan, record the decision, and send the update and book an approval meeting with Cowork skills.

The module shows the shift from "Copilot finds information" to "Copilot finishes the work", with the user approving every change.

**End-user outcome:** Participants can move beyond retrieval and use Copilot to complete a multi-step task across apps, using connectors for read and write, and skills for the Microsoft 365 work product.

### Key takeaways (say these out loud)

| Takeaway | |
|---|---|
| **Three connector models, one answer** | Synced (intranet), hybrid (Smartsheet), and federated (Notion) work together in a single prompt, each with citations. |
| **Company knowledge shapes the decision** | The intranet playbook tells Marcus what's allowed and who approves, so the fix is right the first time. |
| **Hybrid = best of both** | Smartsheet's indexed data helps Copilot find the right sheet and rows fast; its live MCP tools read the latest values and make the changes. |
| **Write actions with control** | Copilot updates Smartsheet and Notion on your behalf, with your own permissions, after you approve. |
| **Skills finish the job** | Email and Scheduling skills turn the outcome into a partner update and an approval meeting. |
| **Read → decide → act → communicate** | The whole loop happens without opening Smartsheet, Notion, or the intranet. |

## 2. Why these three connectors

Smartsheet and Notion are widely recognized by non-engineering audiences, and every company has an intranet. Together they cover three shapes of everyday work data (structured plans, team knowledge, and official company guidance) and all three connector models in the lab: synced, hybrid, and federated.

| Connector | Role in the story | What Copilot uses |
|---|---|---|
| **Smartsheet** · HYBRID · Synced index + federated MCP | System of record for the launch plan: tasks, owners, dates, status, vendor comments | Index: semantic search across sheets, rows, comments. Live read: `get_sheet_summary`, `find_in_sheet`. Write: `update_rows`, `create_discussion`, `add_comment` |
| **Notion** · FEDERATED · Microsoft-published · on by default | Team wiki: launch plan, weekly sync notes, decision log database | Read: `notion-search`, `notion-fetch`, `notion-query-data-sources`. Write: `notion-create-pages`, `notion-update-page` |
| **Verdantis Hub intranet** · SYNCED · Enterprise Websites cloud connector · admin-configured | Company policies: retail partner launch playbook, approved print vendors, partner comms guidelines | Index only: semantic search over intranet pages and linked files (PDF, Word, PowerPoint). No live tools, no write; no user sign-in needed |

### Three connector models side by side

| | Synced · Verdantis Hub | Hybrid · Smartsheet | Federated · Notion |
|---|---|---|---|
| **Where data lives** | Indexed into Microsoft Graph | Indexed into Microsoft Graph, and read live from Smartsheet | Stays in Notion; read live |
| **Identity** | Admin connection; visible to Everyone in the org | Index trimmed to each item's Smartsheet permissions; live calls as the user | User's own sign-in |
| **Freshness** | Full crawl daily; incremental every 15 min with a sitemap | Index as of the last crawl; live is real time | Real time |
| **Write actions** | No | Yes | Yes |
| **Used for** | Policy check (Step 2) | Finding the tracker and vendor comments (Step 1); updating the plan (Step 3) | Plan and notes (Step 1); decision log (Step 4) |

> **HYBRID NOTE:** After Step 3 the Smartsheet index still holds the old values until the next crawl, so Copilot should rely on the live read for rows that just changed.

> **SYNCED NOTE:** The Enterprise Websites cloud connector only supports Everyone permissions, so Verdantis Hub content is visible to every user in the tenant. That's fine for company-wide policies, and a good contrast for the Governance module: use Smartsheet or Notion for content that needs per-user permissions.

> **WHY NOT GMAIL / JIRA / WORKDAY / GITHUB:** Gmail isn't available for this lab. Jira Cloud/Data Center and Workday are synced-only connectors in the Microsoft-built gallery, so they can ground answers but can't demo write actions; Jira can still be mentioned as the synced counterpart in the Governance module. GitHub is too engineering-specific for this audience.

## 3. Scenario: "The vendor slipped – fix the plan before standup"

| | |
|---|---|
| **Persona** | Marcus, at Verdantis (fictional), coordinating the Verdantis Aurora smart-home hub retail launch. Launch event: Nov 3. |
| **Setup** | The launch plan lives in Smartsheet, and vendors post updates on their rows. The team's plan, meeting notes, and decision log live in Notion. Company policies live on Verdantis Hub, the intranet. Everything else is Microsoft 365. |
| **Trigger** | Overnight, the print vendor (Northwind Print) commented on its Smartsheet row: brochure and in-store signage delivery slips one week, from Oct 16 to Oct 23, or they can split (brochures Oct 20, signage Oct 23). That collides with the POS kit shipment to Contoso Retail stores on Oct 21. Riley at Contoso Retail emailed Marcus asking for the kit ETA. |
| **Twist** | Marcus's first idea, shipping signage on Oct 27, breaks the Retail Partner Launch Playbook on Verdantis Hub. Copilot catches it and finds an option that complies. |
| **Goal** | Spot the conflict, check the fix against policy, update the plan, log the decision, inform the partner, and book an approval meeting, all without opening Smartsheet, Notion, or the intranet. |

## 4. Lab flow at a glance (10 min)

| # | Step | Time | Connector / skill | Capability shown |
|---|---|---|---|---|
| 0 | Check sources are connected | 0:30 | Smartsheet, Notion | Discover + connect as self |
| 1 | Morning catch-up | 2:30 | Smartsheet (index + live), Notion (live) + Outlook mail | Cross-source grounding with citations; hybrid search |
| 2 | Check the fix against company policy | 1:30 | Verdantis Hub (synced) | Grounding in company knowledge |
| 3 | Fix the plan in Smartsheet | 1:30 | Smartsheet (write) | Write actions + confirmation card |
| 4 | Log the decision in Notion | 1:30 | Notion (write) | Write into a database, linked context |
| 5 | Tell people + book the approval | 2:00 | Email + Scheduling skills | Skills complete the work in M365 |
| – | Wrap-up | 0:30 | – | Read → decide → act → communicate |
| ★ | Stretch: interactive launch dashboard | +3:00 | App skill (Frontier) | Interactive experience |

**Surface:** Cowork for Steps 1–5 (Copilot Chat also works for Steps 1–4). Sources are connected from Copilot Chat › Settings › Sources and carry over to Cowork.

## 5. Step-by-step script

### Step 0: Check Smartsheet and Notion are connected

*0:30 · Copilot Chat › Settings › Sources*

1. Open Microsoft 365 Copilot Chat › … › Settings › Sources.
2. Confirm Smartsheet and Notion show as Connected. If not, select Connect and sign in with the seat's lab credentials (on the seat card).
3. There's nothing to connect for Verdantis Hub: the admin set it up once for the whole organization.

> **SAY THIS:** Two ways data gets to Copilot: an admin indexes it once for everyone (the intranet, and Smartsheet's index), or you sign in and Copilot reads it live as you (Notion, and Smartsheet's live tools).

> **PROCTOR NOTE:** If the common module already connected these, skip to Step 1. If a sign-in popup is blocked, allow popups for the Copilot domain.

### Step 1: Morning catch-up

*2:30 · Cowork · Smartsheet (index + live) · Notion (live) · Outlook*

**Prompt** (copy and paste into Copilot):

```text
I'm coordinating the Verdantis Aurora launch. Give me a catch-up for this week:
- find our Aurora launch tracker in Smartsheet: tasks due in the next
3 weeks, and any new vendor comments
- check the Aurora Launch Plan and latest weekly sync notes in Notion
- check my email for anything from Contoso Retail
Flag any conflicts between vendor updates and the plan.
```

**Expected result:** A short brief with citations to Smartsheet, Notion, and Outlook, calling out:

- (a) Northwind Print's comment: slip from Oct 16 → Oct 23, or split (brochures Oct 20, signage Oct 23);
- (b) downstream conflict with "Ship POS kits to Contoso Retail stores" due Oct 21;
- (c) Riley asking for the kit ETA, with stores needing kits before staff training on Oct 27;
- (d) good news: Fabrikam Creative commented that the hero video is approved (status still says In Progress).

The prompt doesn't name the sheet exactly; Copilot picks "Verdantis Aurora Launch Tracker" over the decoy sheets (6.2).

> **SAY THIS:** One question, several systems, each answer traceable to its source, and Copilot only sees what Marcus can see. For Smartsheet, the index finds the right sheet and the vendor comments; the live tools confirm today's values.

> **IF IT GOES WRONG:**
> - Misses the vendor comment → "Show me Northwind Print's latest comment in the Aurora tracker."
> - Picks a decoy sheet → "Use the Verdantis Aurora Launch Tracker sheet."

### Step 2: Check the fix against company policy

*1:30 · Cowork · Verdantis Hub intranet (synced)*

**Prompt:**

```text
My idea: ship the POS kits to Contoso Retail on Oct 21 without signage, and
send the signage on Oct 27. Check the Retail Partner Launch Playbook on Verdantis
Hub. Is that allowed? Who has to approve it? And do we have an approved backup
print vendor?
```

**Expected result:** Copilot cites the current playbook on Verdantis Hub (not the archived 2025 version):

- (a) No: every POS kit wave must be in partner stores at least 3 days before staff training, so signage must arrive by Oct 24;
- (b) a split shipment is allowed with approval from the Retail Ops lead (Sam), logged in the Launch Decision Log;
- (c) Northwind's split offer works: ship signage express Oct 23 to arrive Oct 24;
- (d) backup vendor: Litware Print, 3-business-day rush, +15% surcharge, needs Procurement approval.

> **SAY THIS:** This is the synced connector at work: the admin indexed the intranet once, and now everyone's Copilot knows the rules. Copilot didn't just answer the question; it stopped Marcus from breaking a partner commitment.

> **IF IT GOES WRONG:** If Copilot answers from general knowledge → "Search Verdantis Hub for the Retail Partner Launch Playbook."

### Step 3: Fix the plan in Smartsheet

*1:30 · Cowork · Smartsheet write actions*

**Prompt:**

```text
Update the Verdantis Aurora Launch Tracker in Smartsheet:
1. "Print brochures & in-store signage": due date Oct 23, status At Risk
2. "Final hero video": status Complete
3. Add a comment on "Ship POS kits to Contoso Retail stores": wave 1 (kits +
brochures) ships Oct 21; wave 2 (signage) ships express Oct 23, in stores
Oct 24 per the playbook. Pending Retail Ops approval.
```

**Expected result:** Confirmation cards for `update_rows` and `create_discussion`. Participants expand a card to review the parameters, then choose Allow once. Copilot confirms the rows changed.

> **SAY THIS:** Write actions run in Smartsheet as Marcus, with Marcus's permissions, and nothing is sent until you approve. Show the menu: Allow once / Allow for conversation / Always allow. It's per tool, not per connector, and users can reset it in Settings › Sources › Smartsheet › Write/Delete tools.

> **HYBRID NOTE:** The write goes through the live MCP tools, so it lands in Smartsheet immediately; the index picks it up on the next crawl. If someone asks "what's the brochure status now?", Copilot should answer from a live read (At Risk), not the indexed snapshot.

### Step 4: Log the decision in Notion

*1:30 · Cowork · Notion write actions*

**Prompt:**

```text
Add an entry to the "Launch Decision Log" database in Notion:
Decision: Ship Contoso Retail POS kits in two waves – kits + brochures on
Oct 21, signage express on Oct 23 (in stores Oct 24)
Owner: me · Approver: Sam (Retail Ops) · Status: Proposed
Context: summarize the Northwind delay and link the playbook page and the
Smartsheet row.
```

**Expected result:** Confirmation card for `notion-create-pages`, then a new row in the decision log with the context and both links.

> **SAY THIS:** Copilot carries context across systems: the vendor comment, the intranet policy, and the Smartsheet link land in the team's wiki without copy-paste. The playbook said split shipments must be logged, and now they are.

### Step 5: Tell people and book the approval

*2:00 · Cowork · Email + Scheduling skills*

**Prompt:**

```text
Following the partner communication guidelines on Verdantis Hub, draft an email to
Riley at Contoso Retail and the Aurora core team with the new two-wave
timeline, linking the Notion decision. Then schedule a 15-minute "Aurora POS
kit approval" with Sam and the core team tomorrow morning. Show me both
before sending.
```

**Expected result:** Cowork loads the Email and Scheduling skills (shown as chips in the side panel), shows a draft that follows the guideline's structure and a meeting proposal, and pauses for Send / Schedule approval.

> **SAY THIS:** The intranet even shapes how the message is written. Skills turn the outcome into a finished work product.

> **LAB SAFETY:** All recipients are lab mailboxes in the demo tenant. "Riley" (Contoso Retail) and "Sam" (Retail Ops) are internal lab users.

### Wrap-up

*0:30*

> **SAY THIS:** "In ten minutes you pulled from a tracker, a wiki, and the intranet, changed two systems, stayed within company policy, and closed the loop with your partner, without leaving Copilot and without anything happening that you didn't approve."

### Stretch (fast finishers): interactive launch dashboard

*+3:00 · Cowork · App skill (Frontier preview)*

**Prompt:**

```text
Build me an interactive launch dashboard app from the Verdantis Aurora Launch
Tracker: tasks by workstream, at-risk items highlighted, and a timeline to
the Nov 3 launch.
```

> **WHY THE APP SKILL:** Smartsheet and Notion don't return MCP app UI widgets in Microsoft 365 Copilot today, and the intranet is a synced connector with no live tools (Q3). The App skill is how this module shows an interactive experience.

> **ALTERNATIVE · NEEDS DEV WORK:** Adapt the Approvals Box sample from microsoft/mcp-interactiveUI-samples into a "Verdantis Launch Approvals" declarative agent and sideload it in the lab tenant. After Step 4, "Sam" (or the participant) approves the two-wave decision in an inline widget. This would be a real MCP app moment and a natural handoff to the Custom MCP module, but it needs hosting, auth, and an owner.

## 6. Demo environment and seed data

### 6.1 Tenant and accounts checklist

| Area | Requirement |
|---|---|
| ☐ **M365 tenant** | Copilot license and Cowork enabled for all lab users. Frontier enabled if we keep the App skill stretch. |
| ☐ **Notion** | Microsoft-published federated connector enabled; Allowed agent types does not block it. |
| ☐ **Smartsheet hybrid** | Partner-published, so an admin must approve it. Admin creates the synced connection (service account that can read all seat sheets; identity mapping so each item keeps its Smartsheet permissions) and enables the MCP side. Let the first full crawl finish and validate indexed items before the event. |
| ☐ **Verdantis Hub intranet** | AI admin creates one Enterprise Websites cloud connection for the whole lab: root URL of the Verdantis Hub site, "Use sitemap for crawling" on, display name "Verdantis Hub", staged rollout to the lab users group. Auth: None (fictional public site) or Microsoft Entra OAuth 2.0 client credentials. Let the first crawl finish and spot-check pages in Copilot. |
| ☐ **Write actions** | Write/update tools rolled out in the lab tenant for both Copilot Chat and Cowork (rollout started early Oct 2026). |
| ☐ **Third-party seats** | One Smartsheet user and one Notion workspace member per seat (one per lab account, e.g. mhollowell01@…, mhollowell02@…). No shared accounts: write actions would collide across seats. Verdantis Hub is shared; no per-seat accounts. |
| ☐ **M365 seats** | One Marcus Hollowell account per seat (mhollowell01…mhollowellNN) in the demo tenant, plus lab users for the core team, Sam (Retail Ops), and Riley (Contoso Retail). Seed Riley's ETA email in each seat's Outlook inbox. |

### 6.2 Smartsheet: "Verdantis Aurora Launch Tracker" (one copy per seat)

Columns: Task · Workstream · Owner · Status · Start · Due Date · Depends On · Notes

| Task | Workstream | Owner | Status | Due |
|---|---|---|---|---|
| Final hero video | Creative | Fabrikam Creative | In Progress | Oct 10 |
| Retail pricing sign-off | Commercial | Marcus | Complete | Oct 6 |
| **Print brochures & in-store signage** | Retail | Northwind Print | In Progress | Oct 16 |
| Assemble POS kits | Retail | Ops | Not Started | Oct 18 |
| **Ship POS kits to Contoso Retail stores** | Retail | Ops | Not Started | Oct 21 |
| Store staff training | Retail | Contoso Retail | Not Started | Oct 27 |
| Press briefing deck | PR | Marcus | In Progress | Oct 24 |
| Website launch page | Digital | Web team | In Progress | Oct 29 |
| Influencer seeding | Marketing | Marketing | Not Started | Oct 28 |
| Launch event run-of-show | Events | Events team | In Progress | Oct 31 |
| Launch event | Events | All | Not Started | Nov 3 |

Highlighted rows are the ones the story turns on. (The doc shades them; this conversion bolds them.)

| | |
|---|---|
| **Trigger comment** | On "Print brochures & in-store signage", from Northwind Print (via update request): "Paper stock shortage – brochures and signage now deliver Oct 23 instead of Oct 16. We can split: brochures Oct 20, signage Oct 23." |
| **Other comments** | On "Final hero video", from Fabrikam Creative: "Final cut delivered and approved by brand." On "Assemble POS kits": "Kits need Northwind signage before packing." |
| **Decoy sheets** | "Verdantis Aurora – Retail Readiness Checklist" (store fixtures, no dates); "2025 Holiday Launch Tracker (archived)" (old Northwind Print rows); "Verdantis Lumen Launch Tracker" (a different product). Each seat sees only its own sheets. |

> **HYBRID NOTE:** Seed all comments before the event so the index has them. The demo relies on the index to find "new vendor comments" from a fuzzy question.

### 6.3 Notion workspace

| Item | Type | Contents |
|---|---|---|
| Aurora Launch Plan | Page | Goals, key dates (staff training Oct 27, launch event Nov 3), owners, links to the Smartsheet tracker and the Verdantis Hub playbook |
| Weekly Sync – Oct 6 | Page | Notes stating "POS kits must include signage – Contoso Retail needs complete kits before staff training"; action items |
| Launch Decision Log | Database | Properties: Decision, Owner, Approver, Status (Proposed / Approved / Rejected), Date, Context, Links. Seed 3 prior decisions as examples |

### 6.4 Verdantis Hub intranet (one shared site)

A small static site with server-rendered HTML (the connector doesn't crawl content rendered by JavaScript) and a sitemap listed in robots.txt so incremental crawls work. Pages carry "Last updated" dates.

| Page | Key content the demo relies on |
|---|---|
| **Retail Partner Launch Playbook** `/retail/launch-playbook` | Every POS kit wave must be in partner stores at least 3 days before store staff training. Split shipments are allowed with approval from the Retail Ops lead (Sam) and must be logged in the Launch Decision Log. Changes to a partner commitment must be communicated within 1 business day. |
| **Approved Vendors – Print** `/procurement/approved-vendors/print` | Northwind Print (primary). Litware Print (backup): 3-business-day rush, +15% surcharge, Procurement approval needed for a PO change. |
| **Partner Communication Guidelines** `/comms/partner-updates` | Structure for partner updates: what changed, impact on you, new dates, what we need from you, contact. |
| **Decoy pages** | "Retail Partner Launch Playbook (2025, archived)" with an older 5-day rule; Holiday Returns Policy; Verdantis Lumen Launch FAQ; Travel & Expense policy. Tests that Copilot picks the current, relevant page. |

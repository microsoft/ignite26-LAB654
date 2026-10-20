# Get work done across Notion & your intranet

> Converted from `Ignite_Lab_Productivity_Module_Smartsheet_Notion_Intranet.docx` (Ignite Lab200 · Connectors · Productivity module, DRAFT v2). Wording is preserved; layout is simplified to Markdown.
>
> **Dates are shifted.** The doc's story runs on a Monday "today" of Nov 16, 2026. COEP needs past timestamps, so every story date here, in the tenant seed and in the connector specs is moved back 35 days (5 weeks), keeping weekdays. "Today" is **Mon Oct 12, 2026**, the same lab date as the legal scenario.
>
> | Doc date | Shifted | | Doc date | Shifted |
> |---|---|---|---|---|
> | Mon Nov 16 (today) | Mon Oct 12 | | Sat Nov 28 | Sat Oct 24 |
> | Fri Nov 20 | Fri Oct 16 | | Tue Dec 1 | Tue Oct 27 |
> | Sun Nov 22 | Sun Oct 18 | | Sat Dec 5 | Sat Oct 31 |
> | Tue Nov 24 | Tue Oct 20 | | Tue Dec 8 | Tue Nov 3 |
> | Wed Nov 25 | Wed Oct 21 | | | |
> | Fri Nov 27 | Fri Oct 23 | | | |

Scenario design and lab readiness plan for a 10-minute hands-on module.

| | |
|---|---|
| **Lab** | Supercharge Copilot: Connect your work data & Get work done with Copilot Connectors (LAB654, 75 min) |
| **Module** | [Productivity] Complete end-to-end productivity workflows with MCP apps and skills |
| **Module DRI** | Danny (also Lab Readiness DRI) |
| **Time budget** | 10 minutes, 4 steps |
| **Lab user** | Marcus Hollowell, Verdantis (the one LAB654 persona shared by the legal, finance, and productivity modules) |
| **Connectors** | Notion (federated) · Verdantis Hub intranet (synced · Enterprise Websites) |
| **Status** | DRAFT v2 for review |

> **WHAT CHANGED IN V2**
>
> - **Single persona (LAB654 design note):** Marcus Hollowell at Verdantis is the Copilot user. Zava → Verdantis, Avery → Marcus, Jordan → Riley, smart speaker → smart-home hub. Prompts don't state a job title.
> - **Simpler flow:** Smartsheet removed; the launch tracker moves into Notion. Six steps become four.
> - **Review comments:** "Hybrid" is no longer used anywhere in the doc. Step 1 is now a scheduled prompt.

## 1. Summary

Participants play Marcus, who is coordinating a product launch whose print vendor just slipped. The plan and the team's decisions live in Notion; the rules for retail partners live on Verdantis Hub, the company intranet. In 10 minutes Marcus reads a catch-up that Copilot prepared on a schedule, checks the fix against company policy, updates the plan and logs the decision in Notion, then emails the partner and books an approval meeting.

**End-user outcome:** Participants can move beyond retrieval and use Copilot to complete a multi-step task across apps, using connectors for read and write, and skills for the Microsoft 365 work product.

### Key takeaways (say these out loud)

| Takeaway | |
|---|---|
| **Copilot works before you do** | A scheduled prompt has the morning catch-up ready when Marcus opens Copilot. |
| **Company knowledge shapes the decision** | The intranet playbook says what's allowed and who approves, so the fix is right the first time. |
| **Write actions with control** | Copilot updates Notion as Marcus, with his permissions, after he approves. |
| **Skills finish the job** | Email and Scheduling skills turn the decision into a partner update and an approval meeting. |

## 2. The two connectors

One connector of each kind keeps the module short: Notion is read and written live as the user, and the intranet is indexed once by an admin for everyone.

| Connector | Role in the story | What Copilot uses |
|---|---|---|
| **Notion** · FEDERATED · Microsoft-published · on by default | Team workspace: launch tracker, launch plan, decision log | Read: `notion-search`, `notion-fetch`. Write: `notion-update-page`, `notion-create-pages` |
| **Verdantis Hub** · SYNCED · Enterprise Websites cloud connector | Company policies: retail partner launch playbook, approved print vendors, partner comms guidelines | Index only: semantic search over hub.verdantis.com pages. No live tools, no write, no user sign-in |

| | Synced · Verdantis Hub | Federated · Notion |
|---|---|---|
| **Where data lives** | Indexed into Microsoft Graph | Stays in Notion; read live |
| **Identity** | Admin connection; visible to everyone in the org | User's own sign-in |
| **Freshness** | Full crawl daily; incremental every 15 min with a sitemap | Real time |
| **Write actions** | No | Yes, after the user approves |

> **SYNCED NOTE:** The Enterprise Websites cloud connector only supports Everyone permissions, which fits company-wide policies. Content that needs per-user permissions belongs in a federated source like Notion (a good contrast for the Governance module).

## 3. Scenario: "The vendor slipped – fix the plan before standup"

| | |
|---|---|
| **Persona** | Marcus, at Verdantis (fictional), coordinating the Verdantis Aurora smart-home hub retail launch. Launch event: Nov 3. |
| **Trigger** | Northwind Print, the print vendor, updated its row in the Notion launch tracker: brochures and in-store signage slip from Oct 16 to Oct 23, or they can split (brochures Oct 20, signage Oct 23). That collides with the POS kit shipment to Contoso Retail stores on Oct 21. Riley at Contoso Retail emailed Marcus at 7:40 AM asking for the kit ETA. |
| **Twist** | Marcus's first idea, shipping signage on Oct 27, breaks the Retail Partner Launch Playbook on Verdantis Hub. Copilot catches it and finds an option that complies. |
| **Goal** | Fix the plan, log the decision, tell the partner, and book the approval, without opening Notion or the intranet. |

## 4. Lab flow at a glance (10 min)

| # | Step | Time | Connector / skill |
|---|---|---|---|
| 1 | Read the scheduled morning catch-up | 2:00 | Notion + Outlook |
| 2 | Check the fix against company policy | 2:00 | Verdantis Hub (synced) |
| 3 | Update the plan and log the decision | 2:30 | Notion (write) |
| 4 | Email the partner and book the approval | 2:30 | Email + Scheduling skills |
| – | Wrap-up | 1:00 | – |

**Surface:** Cowork. Notion is connected before the lab (6.1) because the scheduled prompt runs before participants sit down.

## 5. Step-by-step script

### Step 1: Read the scheduled morning catch-up

*2:00 · Notion (live) · Outlook*

Open the "Aurora morning catch-up" result. The scheduled prompt already ran this morning:

```text
I'm coordinating the Verdantis Aurora launch. Give me a catch-up for this week:
- from the Aurora launch tracker in Notion: tasks due in the next 3 weeks
and any vendor updates
- anything in my email from Contoso Retail
Flag any conflicts between vendor updates and the plan.
```

**Expected result:** A short brief with citations to Notion and Outlook:

- (a) Northwind Print slips from Oct 16 to Oct 23, or can split (brochures Oct 20, signage Oct 23);
- (b) this conflicts with "Ship POS kits to Contoso Retail stores" on Oct 21;
- (c) Riley asks for the kit ETA, and stores need kits before staff training on Oct 27.

> **SAY THIS:** Copilot did the catch-up before Marcus started his day, from Notion live as Marcus and from his inbox. Any prompt you run every morning can be scheduled.

> **IF IT GOES WRONG:** If the scheduled result is missing, paste the prompt above and run it now.

### Step 2: Check the fix against company policy

*2:00 · Verdantis Hub (synced)*

```text
My idea: ship the POS kits to Contoso Retail on Oct 21 without signage, and
send the signage on Oct 27. Check the Retail Partner Launch Playbook on
Verdantis Hub. Is that allowed? Who has to approve it?
```

**Expected result:** Copilot cites the current playbook (not the archived 2025 version):

- (a) No: every POS kit wave must be in partner stores at least 3 days before staff training, so signage must arrive by Oct 24;
- (b) a split shipment is allowed if the Retail Ops lead (Sam) approves and it's logged in the Launch Decision Log;
- (c) Northwind's split offer works: ship signage express on Oct 23 so it arrives Oct 24.

> **SAY THIS:** An admin indexed the intranet once, and now everyone's Copilot knows the rules. Copilot didn't just answer; it stopped Marcus from breaking a partner commitment.

> **IF IT GOES WRONG:** If Copilot answers from general knowledge → "Search Verdantis Hub for the Retail Partner Launch Playbook."

### Step 3: Update the plan and log the decision

*2:30 · Notion write actions*

```text
In Notion:
1. In the Aurora launch tracker, set "Print brochures & in-store signage" to
due Oct 23, status At Risk.
2. Add an entry to the Launch Decision Log: ship Contoso Retail POS kits in two
waves (kits + brochures Oct 21; signage express Oct 23, in stores Oct 24).
Owner: me. Approver: Sam Patel. Status: Proposed. In Context, summarize the
Northwind delay and link the playbook page.
```

**Expected result:** Confirmation cards for `notion-update-page` and `notion-create-pages`. Participants expand a card to check the values, then choose Allow once. Copilot confirms both changes.

> **SAY THIS:** Write actions run in Notion as Marcus, with his permissions, and nothing changes until he approves. The menu also offers Allow for conversation and Always allow, per tool; users can reset it in Settings › Sources › Notion. The playbook said split shipments must be logged, and now they are.

### Step 4: Email the partner and book the approval

*2:30 · Email + Scheduling skills*

```text
Following the partner communication guidelines on Verdantis Hub, draft an
email to Riley at Contoso Retail with the new two-wave timeline, cc Sam Patel.
Then schedule a 15-minute "Aurora POS kit approval" with Sam tomorrow
morning. Show me both before sending.
```

**Expected result:** Cowork loads the Email and Scheduling skills, shows a draft that follows the guideline's structure and a meeting proposal, and waits for Send / Schedule approval.

> **SAY THIS:** The intranet even shapes how the message is written, and skills turn the decision into finished work.

> **LAB SAFETY:** Riley Blake (Contoso Retail) and Sam Patel are lab users in the demo tenant; nothing leaves the tenant.

### Wrap-up

*1:00*

> **SAY THIS:** "Copilot prepared your morning, checked company policy, updated the plan, and closed the loop with your partner. You approved every change, and you never opened Notion or the intranet."

> **STRETCH:** Fast finishers: "Build me an interactive dashboard app from the Aurora launch tracker" (App skill, Frontier). Notion doesn't return MCP app UI widgets in Microsoft 365 Copilot today, so this is the module's interactive moment.

## 6. Demo environment and seed data

### 6.1 Readiness checklist

| Area | Requirement |
|---|---|
| ☐ **M365 seats** | One Marcus Hollowell account per seat (mhollowell01…mhollowellNN) with Copilot and Cowork. Riley Blake and Sam Patel exist as lab users (done). |
| ☐ **Notion** | Test_Notion (mock Notion MCP server, no sign-in) uploaded and enabled for every seat. All seats share one server; write changes are kept per Cowork conversation (keyed on the `x-microsoft-ai-conversationid` header), so seats never collide. See `infra/mock_environment/mock_mcp_servers/notion/README.md`. |
| ☐ **Pre-connect** | Check that Test_Notion shows as Connected in each seat (Settings › Sources) before the event; the scheduled prompt can't run without it. |
| ☐ **Scheduled prompt** | Per seat: create "Aurora morning catch-up" (Step 1 prompt), weekdays at 8:00 AM event-local time. Check that it ran before doors open. |
| ☐ **Verdantis Hub** | Enterprise Websites cloud connection to hub.verdantis.com, display name "Verdantis Hub". Re-crawl after the Zava → Verdantis edit and spot-check that the old Zava text is gone. |
| ☐ **Outlook** | Riley's POS-kit ETA email in each Marcus inbox, 7:40 AM Eastern (done). |

### 6.2 Notion seed (shared, read-only baseline)

| Item | Type | Contents |
|---|---|---|
| Verdantis Aurora Launch Tracker | Database | Properties: Task, Workstream, Owner, Status, Due, Vendor update. Rows below. |
| Aurora Launch Plan | Page | Key dates (staff training Oct 27, launch event Nov 3), owners, link to the playbook on Verdantis Hub. Includes "POS kits must include signage before staff training." |
| Launch Decision Log | Database | Properties: Decision, Owner, Approver, Status (Proposed / Approved / Rejected), Date, Context. Seed 2 prior decisions as examples. |
| Decoys | Database | "Verdantis Lumen Launch Tracker" (other product); "2025 Holiday Launch Tracker (archived)" with old Northwind rows. |

| Task | Owner | Status | Due | Vendor update |
|---|---|---|---|---|
| **Print brochures & in-store signage** | Northwind Print | In Progress | Oct 16 | "Paper stock shortage – brochures and signage now deliver Oct 23 instead of Oct 16. We can split: brochures Oct 20, signage Oct 23." |
| Assemble POS kits | Ops | Not Started | Oct 18 | |
| **Ship POS kits to Contoso Retail stores** | Ops | Not Started | Oct 21 | |
| Store staff training | Contoso Retail | Not Started | Oct 27 | |
| Press briefing deck | Marcus | In Progress | Oct 24 | |
| Launch event run-of-show | Events team | In Progress | Oct 31 | |
| Launch event | All | Not Started | Nov 3 | |

Bold rows are the ones the story turns on.

### 6.3 Verdantis Hub (hub.verdantis.com, 7 pages, live)

| Page | What the demo relies on |
|---|---|
| **Retail Partner Launch Playbook** | Each POS kit wave in stores 3+ days before staff training. Split shipments need Retail Ops (Sam) approval and a Launch Decision Log entry. |
| **Approved Vendors – Print** | Northwind Print (primary); Litware Print (backup). |
| **Partner Communication Guidelines** | Update structure: what changed, impact, new dates, what we need, contact. |
| **4 decoy pages** | 2025 archived playbook (older 5-day rule), Holiday Returns Policy, Lumen Launch FAQ, Travel & Expense. |

### 6.4 Reset between sessions

- **Notion:** nothing to reset. Each conversation's changes expire after 2 hours idle, and a new conversation always starts from the seed. Restarting the `mock-notion` container clears everything at once.
- **M365:** clear sent mail and meetings; re-seed Riley's email if it was moved or deleted.
- **Copilot:** revoke "Always allow" if participants set it. The scheduled prompt and Verdantis Hub need no reset.

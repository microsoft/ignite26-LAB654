# Engineering: One item at risk. Who is it waiting on?

> Source: *Ignite_Engineering_Connectors_Lab_v3.docx* (facilitator draft), reworked for the revised engineering flow: start from sprint status, drill into the one at-risk item, then act on it. Formatting differs from the original.
>
> IGNITE LAB654 | Engineering connectors lab | Fictional lab data
>
> **Lab build notes:** GitHub and Jira are **MCP connectors**: GitHub_Lab (`mock_mcp_servers/github`) and Rovo_Lab (`mock_mcp_servers/atlassian`, plugin `mock_plugins/rovo`). Jira and Confluence links open in the Jira mock's viewer.

## At a glance

| | |
|---|---|
| **Experience** | Part A in Copilot Chat: Rovo_Lab + GitHub_Lab. Part B in Cowork: Teams + Rovo_Lab `sprint-to-slides` skill. |
| **Timing** | 15-minute target: setup 2 min; Steps 1-4: 2 / 4 / 3 / 4 min; wrap-up 1 min. Confirm in a dry run. |
| **Take home** | A cited sprint status, the real blocker behind the at-risk item, a Teams message to the approver, and a sprint status slide. |

## Setup: explain the scenario to the room

**Read aloud:** Meet Emil Vanggaard, product manager for Aurora at Zava. Aurora is a smart-home hub that retail stores use to track devices. Lakeshore Retail is piloting it, and on Monday, November 23, every pilot store goes live.

Atul, the pilot coordinator, has emailed again: hubs keep showing Offline after they reconnect, and staff are restarting devices that are working fine. He wants to know if it will be fixed before the expansion.

Emil opens the Sprint 24 board. Almost everything is on track. One item isn't, and it's Atul's bug. The ticket says it's at risk, but not why, and nobody can give a date. Before Emil answers Atul, he needs to know who the work is really waiting on, and get it moving.

**Your job:** Read the sprint, find out what is really blocking the at-risk item, then switch to Cowork to unblock it and give leadership a one-slide sprint update. No code change or release is performed.

## Part A: Investigate in Copilot Chat

### Step 1: How is the sprint going?

| | |
|---|---|
| **Time / surface** | 2 min / Copilot Chat / Rovo_Lab |
| **Query to fire** | What's the status of Aurora Sprint 24? Is anything at risk for the Lakeshore Retail pilot expansion? |
| **Expected response** | Summarizes the six Sprint 24 items: AUR-133 and AUR-137 are Done; AUR-136 (cutover runbook) and AUR-139 (rollout regression) are In Progress and on track for the November 18 dry run; AUR-151 (custom dashboard filters) is a lower-priority stretch item in To Do. **AUR-142, "Aurora hubs remain offline after reconnect", is the one item at risk**: High priority, labelled at-risk, and Kerry calls it the only Sprint 24 item tied to the November 23 expansion that isn't on track. May connect it to Atul's email. Cites the Jira items. |
| **Seed names only** | J1-J6: Sprint 24 work items AUR-133, AUR-136, AUR-137, AUR-139, AUR-142, AUR-151 |
| **Aha in the room** | A connector answers a sprint question straight from Jira, and Copilot picks out the one item that matters from a mostly green board. |

### Step 2: What's really going on with AUR-142?

| | |
|---|---|
| **Time / surface** | 4 min / Copilot Chat / Rovo_Lab + GitHub_Lab |
| **Query to fire** | What's the current status of AUR-142, and what is it waiting on? Check Jira, Confluence and GitHub. |
| **Expected response** | Joins three sources:<br>**Jira** (tracking): AUR-142 is In Progress and at risk. Triin's latest comment says the event-driven work depends on a design decision still waiting for platform sign-off, so she can't give a date.<br>**Confluence** (record): the *Lakeshore Retail pilot - delivery commitments* page commits to the November 20 cutover and November 23 expansion, requires reconnected hubs to show Online on the event-driven service, and requires platform sign-off for any change to reconnect handling. No date has been shared with the customer. *ADR-014* is **Proposed, awaiting approval**, with **Tama Surya as decision owner**; Triin asked Tama to decide on October 29.<br>**GitHub** (code): PR #287 is open and unmerged. It fixes only the legacy polling path; Tama requested changes for the event-driven service and new-service tests.<br>**Conclusion:** the blocker is Tama's approval of ADR-014. After that, Triin implements Option B on PR #287, Maria adds event-driven reconnect tests, and Tama re-reviews. Cites the Jira item, both Confluence pages and the PR. |
| **Seed names only** | J5: AUR-142<br>C2: Lakeshore Retail pilot - delivery commitments<br>C3: ADR-014: Reconnect state handling on the event-driven status service<br>G1: PR #287 - Fix stale offline state after reconnect<br>G2: Tama's review - changes requested |
| **Aha in the room** | Each tool holds part of the truth: Jira knows it's late, Confluence knows what was promised and who decides, GitHub knows where the code stands. Only together do they show the fix is waiting on one approval. |

## Part B: Act in Cowork

> **Surface switch:** Open Copilot Cowork and start a new task. Cowork may not carry the Chat context, so the Part B prompts are self-contained.

### Step 3: Ask Tama for the decision

| | |
|---|---|
| **Time / surface** | 3 min / Cowork / Teams |
| **Query to fire** | Send Tama Surya a Teams message. Ask Tama to approve ADR-014 so Triin can start the event-driven fix for AUR-142, and to re-review PR #287 once it's updated. Mention the November 20 cutover and include links to the ADR, the Jira item and the PR. |
| **Expected response** | Drafts a short, polite 1:1 Teams message to Tama: what is waiting (ADR-014, Option B proposed), why it matters (AUR-142 is the only at-risk Sprint 24 item; the pilot moves to the event-driven service on November 20 and expands November 23), what happens next (Triin implements, Maria tests, Tama re-reviews PR #287), and the three links. Shows the recipient and text for approval before sending. |
| **Seed names only** | Directory: Tama Surya<br>C3: ADR-014 link<br>J5: AUR-142 link<br>G1: PR #287 link |
| **Aha in the room** | The investigation turns straight into the one action that unblocks the work, sent to the right person with the evidence attached. |

### Step 4: Turn the sprint into a slide

| | |
|---|---|
| **Time / surface** | 4 min / Cowork / Rovo_Lab `sprint-to-slides` skill |
| **Query to fire** | /skill sprint-to-slides<br>Create one PowerPoint slide summarizing Aurora Sprint 24 for engineering leadership: what's on track, the one item at risk, what it's waiting on, and the next steps. |
| **Expected response** | Uses Rovo_Lab to read Sprint 24 from Jira (and ADR-014 from Confluence if needed). Produces one slide: sprint goal and dates; five items on track or done; AUR-142 at risk; blocker: ADR-014 awaiting Tama's approval; next steps and owners (Tama approves, Triin implements, Maria tests, Tama re-reviews); key dates November 18 dry run, November 20 cutover, November 23 expansion; sources. Doesn't invent velocity, story points or a delivery date. |
| **Seed names only** | Sprint 241: Aurora Sprint 24 (board 57)<br>S1: Rovo_Lab sprint-to-slides skill |
| **Aha in the room** | A partner skill in Cowork turns live Jira data into a leadership-ready slide in one step. |
| **Presenter note** | The skill's default flow is a report plus a slide outline, with an optional Confluence archive. This lab asks for one .pptx slide only. Verify that narrowed output and the /skill selection in Cowork. Rovo_Lab's Confluence writes are kept per conversation, so an archive doesn't affect other attendees. |

## Wrap-up (1 minute)

- **Say this:** "We started from a sprint board that looked mostly green. Copilot found the one item at risk, joined Jira, Confluence and GitHub to show it was waiting on a single approval, then Cowork asked for that approval and gave leadership a one-slide update."
- **Ask the room:** Which of the three sources would you have checked first, and what would you have missed?

## Facilitator-only readiness

| | |
|---|---|
| **Validate access** | Confirm that GitHub_Lab and Rovo_Lab are connected in Copilot Chat and Cowork. All recipients must be lab identities. |
| **Validate Jira data** | Rovo_Lab data comes from `mock_mcp_servers/atlassian/seed_files/seed.json`. Links in citations open the Jira mock's viewer (`/browse/AUR-142`, `/wiki/spaces/AUR/pages/98457`). |
| **Validate GitHub** | Confirm GitHub_Lab finds PR #287 from "AUR-142" and returns Tama's changes-requested review. Writes are kept per conversation, and merging is blocked by branch protection while the review stands. |
| **Validate skill** | Verify one-slide .pptx output from sprint-to-slides in Cowork, and that the Teams message is shown for approval before it's sent. |
| **Dry run / reset** | Measure the full flow. All seeded evidence is dated on or before October 30, 2026 (the tenant is loaded once); the dry run, cutover and expansion fall after the November 17-19 lab. Prompts use no relative days. Teams messages to Tama are real posts in the lab tenant; isolate by seat or keep them as drafts. |

## Appendix A: Jira (Rovo_Lab)

Project AUR, board 57. Sprint 241, *Aurora Sprint 24*, October 26 - November 20, 2026. Goal: cut the pilot stores over to the event-driven status service on November 20 and have the Lakeshore Retail pilot ready for its November 23 expansion.

| ID | Item | Status | Owner | Signal |
|---|---|---|---|---|
| J1 | AUR-133 Publish device heartbeat events to the event-driven status service | Done | Maria Oliva | On track |
| J2 | AUR-136 Status-service cutover runbook for the pilot stores | In Progress | Kerry Allen | Draft in Confluence; switch order final at the November 18 dry run |
| J3 | AUR-137 Telemetry gaps on Lakeshore Retail pilot hubs after firmware 4.2 | Done | Triin Lepp | On track |
| J4 | AUR-139 Rollout regression checks for the status-service cutover | In Progress | Maria Oliva | Two of three runs green; final run after the dry run |
| J5 | AUR-142 Aurora hubs remain offline after reconnect | In Progress | Triin Lepp | **At risk.** Comments: October 26, "I have started working on the fix."; October 29, Triin: legacy fix in review, event-driven work waits on the design decision, no date until it's approved; October 29, Kerry: only Sprint 24 item tied to November 23 that isn't on track. Jira has the delay signal only, no ETA and no PR link. |
| J6 | AUR-151 Custom dashboard filters for the store status view | To Do | Triin Lepp | Low-priority stretch, no pilot dependency |

## Appendix B: Confluence (Rovo_Lab)

Space AUR, *Aurora Engineering*.

| ID | Page | Content |
|---|---|---|
| C1 | Aurora Engineering (home) | Links to the pages below; work tracking in Jira AUR board 57; code in GitHub zava-lab/aurora-status; decisions as ADRs. |
| C2 | Lakeshore Retail pilot - delivery commitments | Record of commitments, owned by Emil. November 20 cutover (Tama) and November 23 expansion (Emil). Must be true for November 23: event-driven service for all pilot stores; reconnected hubs show Online (AUR-142); reconnect tests on the event-driven service; regression checks (AUR-139). Platform sign-off by Tama required for any reconnect or status-state change, recorded on the ADR. No release date shared with the customer. |
| C3 | ADR-014: Reconnect state handling on the event-driven status service | Status **Proposed - awaiting platform approval**. Decision owner Tama Surya; author Triin Lepp; related AUR-142 and PR #287. Options A (clear Offline on reconnect) and B (reconcile on first heartbeat, needs a schema change and new tests); proposal B. After approval: Triin implements on PR #287, Maria adds tests, Platform re-reviews. Footer comment, October 29, Triin to Tama: ready for decision; work on hold until then. |
| C4 | Aurora Sprint 24 plan | Sprint goal and committed work (J1-J6); check-in every Thursday at 10:00; dry run November 18. |
| C5 | Status-service cutover runbook (November 20) | Draft switch order, rollback trigger, Maria on call; final order at the November 18 dry run. |

## Appendix C: GitHub, email and Teams

| ID | Source | Content |
|---|---|---|
| G1 | GitHub_Lab | PR #287, *Fix stale offline state after reconnect*, zava-lab/aurora-status. Author Triin Lepp. Open, unmerged. Body references AUR-142; fixes the legacy polling path only; event-driven coverage not implemented. Legacy checks pass as of October 28, 17:00. Three merged decoy PRs on the same repo. |
| G2 | GitHub_Lab | Tama Surya, October 28, changes requested: implement the equivalent correction on the event-driven service, add and run reconnect tests there, then request another platform review. |
| E1 | Outlook | *Aurora pilot - offline status still wrong*: Atul's report (October 23), Emil's reply that engineering is working on a fix (October 26), Atul asking whether it will be fixed before November 23 (October 29). No date or workaround promised. |
| T1 | Teams | Aurora Engineering team, Platform Migration channel: Tama confirms the November 20 cutover and that a legacy-only fix won't resolve the pilot's issue; Maria asks for new-path reconnect coverage; Kerry says LT approves any deferral and no release date has been committed. |
| T2 | Teams | Engineering channel (Sprint 24 kickoff from Kerry) and the *Aurora Engineering LT* group chat. Directory: Emil Vanggaard, Atul Manohar, Triin Lepp, Maria Oliva, Tama Surya, Kerry Allen. |

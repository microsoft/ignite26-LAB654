# Lab revamp plan

This is the working checklist for the LAB654 revamp: four tracks plus Bring your own app. Tick items as they land. Each section says what changes in the **COEP tenant**, the **mock MCP servers**, the **test plugins** and the **lab manual**.

Sources: the scenario docs in this folder. Lab flow: Introduction → one of four tracks (Finance, Legal, Productivity, Engineering) → Bring your own app → outro.

## Status at a glance

| Area | Finance | Legal | Productivity | Engineering | Bring your own app |
|---|---|---|---|---|---|
| Scenario doc | ✅ synced with lab manual | ✅ v3 short | ✅ new | ✅ new | ✅ new |
| Lab manual module | ✅ `03` (as is) | ✅ `04` rewritten | ✅ `05` rewritten | ✅ `06` new | ✅ `07` new |
| COEP tenant data (M365) | ✅ no change expected | ✅ redated | ✅ rebuilt | ✅ new | ✅ receipts |
| Synced connectors (COEP) | n/a | n/a | ✅ Test_Confluence | ✅ Test_GitHub | n/a |
| Mock MCP servers (federated) | ✅ LSEG, FactSet, Moody's deployed | ✅ iManage deployed | ✅ Salesforce deployed | ✅ Jira deployed | ✅ Zava Expense deployed |
| Test plugins | ✅ 3 built | ✅ Test_iManage built | ✅ Test_Salesforce built | ✅ Test_Jira built | ✅ Test_Zava Expense built (flow to confirm) |
| Dry run | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |

## 1. Lab manual

- [x] `01-introduction.md`: four tracks + Bring your own app, 300+ connectors across Chat, Cowork, Word, Excel and PowerPoint. Removed the synced/federated table (the productivity spec says the manual must not discuss connector architecture).
- [x] `02-getting-started.md`: track-to-connector table, conversation-scoped note, four sample prompts.
- [x] `03-finance.md`: kept the existing track text; footer only.
- [x] `04-legal.md`: v3 short (four steps: catch up, flag, fix, pack).
- [x] `05-productivity.md`: Salesforce pitch prep (three steps + stretch).
- [x] `06-engineering.md`: new.
- [x] `07-custom-mcp.md`: new. App named **Zava Expense**.
- [x] `08-summary.md`: renamed from `06-summary.md`; outro with governance and CTA.
- [x] `instructions/README.md` and `docs/scenarios/README.md` updated.
- [x] Root `README.md`: "Getting started" step 3 now says one of four tracks, then Bring your own app.
- [x] Root `README.md`: session description now covers all four tracks plus Bring your own app.
- [x] Durations (approximate): Finance ~18, Legal ~15, Productivity ~10, Engineering ~15, Bring your own app ~20.

## 2. Connector support in the COEP tenant

COEP grounding schemas available today (`infra/mock_environment/_schemas/Grounding`): `azuredevopswiki`, `azuredevopsworkitems`, `channels`, `channelmessages`, `channelmessagereplies`, `chats`, `confluence`, `contacts`, `customconnectors`, `emails`, `events`, `files`, `googledrive`, `intranetwebsite`, `onlinemeetings`, `servicenowkb`, `sites`, `teams`, `users`, Viva Engage, and others.

| Connector | Track | Type | COEP support | Plan |
|---|---|---|---|---|
| Test_Confluence | Productivity | Synced | ✅ `confluence` schema | Seed the Zava Sales space (§4.3). |
| Test_GitHub | Engineering | Synced | ✅ `customconnectors` schema | Seed PR #287 with Tama's review, using the real GitHub pull-request connector's fields (§4.4, engineering Appendix D). |
| Test_Jira | Engineering | Federated | n/a | Mock MCP server + plugin with the `sprint-to-slides` skill (§5.2). |
| Test_Salesforce | Productivity | Federated | n/a | Mock MCP server + plugin with sales skills (§5.1). |
| Test_iManage | Legal | Federated | n/a | Mock MCP server + plugin; seed files already in repo (§5.3). |
| Test_LSEG, Test_FactSet, Test_Moodys | Finance | Federated | n/a | Live; keep. |
| Zava Expense | Bring your own app | Custom MCP | n/a | New mock (§5.4). |
| Outlook, Teams | All | Microsoft 365 | ✅ `emails`, `events`, `onlinemeetings`, `chats`, `teams`, `channels`, `channelmessages` | Seed in COEP. |

## 3. Personas and naming

Tenant users (`users.config.json`): 21 across all tracks. Emil Vanggaard's manager is Hannes Niemi.

| Person | Needed by | Status |
|---|---|---|
| Emil Vanggaard | All | Keep. COEP holds one job title; the legal one is current. Productivity says "no job title in prompts", so the legal title is fine. Confirm with owners. |
| Hemanti Baishya, Luc Lacombe | Legal | Keep. |
| Kristian Stensen | Finance | Keep. |
| Tama Surya | Engineering (platform lead, PR reviewer, LT) | Keep; retitle from "Retail Operations Lead" to "Platform Lead, Aurora". |
| Zoe Armstrong | Productivity (Director of Retail Sales; approves 12–15% discounts) | **Add.** Named in the Confluence pricing policy only. |
| Atul Manohar | Productivity (Lakeshore Retail Director of Store Operations), Engineering (Lakeshore Retail pilot coordinator) | **Minor conflict.** Proposed title: "Director of Store Operations, Lakeshore Retail" in both; engineering text calls Atul the pilot contact. Update from "Partner Account Manager". |
| Jahidi Juma | Productivity (Lakeshore Retail IT Security Lead) | **Add.** |
| Nanami Nakayama | Productivity (Lakeshore Retail CFO, no email history) | **Add.** Must not appear in any email before the lab. |
| Triin Lepp, Maria Oliva, Kerry Allen | Engineering | **Add.** |
| Hannes Niemi | Bring your own app (approver; Emil's manager) | **Add**, and set as Emil's manager (step 3a: "submit the report to my manager"). |
| Ebere Ibeabuchi | Bring your own app (Finance Operations) | **Add.** |
| Vira Sokur, Andreea Bojin | Legal (Trey Research, documents only) | Don't add as users. |

- [x] Lakeshore Retail people (Atul, Jahidi, Nanami Nakayama) are tenant users. COEP rejects email senders, recipients, event attendees and meeting participants that aren't in `users`. External (MSA) users can send email and attend events, but not join online meetings, so Atul and Jahidi must be normal users. Their titles say "Lakeshore Retail".
- [x] Naming: the app is **Zava Expense** everywhere. The repo scenarios and lab instructions are the source of truth, not the original docs.
- [x] Every person has a unique first name (names from CELA's Fictitious Names Finder).

## 4. COEP tenant changes

Build with `infra/mock_environment/tools/build_tenant.py` (`SCENARIOS = [legal, finance, productivity, engineering, expense]`). Each scenario module returns `users()`, `emails()`, `chats()`, `events()`, `files()`.

### 4.1 Remove

- [x] Productivity (Notion era): email *Aurora POS kits – ETA for our stores?* and related chats or events.
- [x] `intranetwebsite/intranetwebsite_productivity.jsonl` (Zava Hub playbook pages).
- [x] Any Notion references in `tools/scenarios/productivity`.

**Date rule (all tracks):** the tenant is loaded once (around Nov 1) and the lab runs Nov 17–19, 2026. Everything seeded is dated on or before **Fri Oct 30, 2026**; anything still to come in a story is on or after **Fri Nov 20, 2026**. Prompts never use relative days ("today", "Monday", "this afternoon").

### 4.2 Legal (`tools/scenarios/legal`)

- [x] Redated with `redate.py --lab-date 2026-10-26 --negotiation-date 2026-12-10` (two anchors): Hemanti's email Mon Oct 12, contract received Fri Oct 16, *Trey Research deal* chat Tue Oct 20, Luc's trigger Mon Oct 26 08:07; negotiation Thu Dec 10, go-live Sun Dec 13. iManage files, `matter.json` and the legal docs updated; prompt says "the December 10 session".
- [x] Hemanti's email and the *Trey Research deal* chat match the v3 seed kit wording (only dates differed).
- [x] Agreement checked against *legal v1 seed kit 1.zip*: same text; only our intended date shift differs. No swap needed.

### 4.3 Productivity (`tools/scenarios/productivity`, rewrite)

- [x] Email from Atul, dated before the tenant is built (COEP needs past timestamps): Nanami joins and wants the all-in cost for 400 stores; Jahidi needs security docs. No cc to Nanami.
- [x] Event Fri Nov 20, 2026, 10:00–11:00 (day after the last lab day), *Lakeshore Retail – Aurora expansion pitch*, attendees Atul, Nanami Nakayama, Jahidi. Same emails as Salesforce.
- [x] Busy blocks next week; Emil out of office **Nov 26–27**.
- [x] Test_Confluence (`confluence` schema), space **Zava Sales**: pricing policy, Boulder Innovations battlecard, security FAQ, Wide World Importers case study, 2–3 distractors (archived 2025 pricing policy).
- [x] Teams meeting *Lakeshore Retail – Aurora pilot review*, organized by Emil, fixed past date: past `events` item + `onlinemeetings` item (linked by EventId) + `.vtt` transcript, ~10 min, speakers Emil, Atul, Jahidi, with the five required lines (9% attach lift; Boulder Innovations "about 20% under your list price"; "if you can get close to that we could sign this quarter"; security review before 400-store rollout; "Nanami will want the all-in cost"). Atul and Jahidi must be tenant users (participants are mail nicknames).
- [x] **Date-agnostic design:** Outlook items are fixed once ingested and email timestamps must be in the past, so they can't move. Prompts refer to items by name, not by day ("my Lakeshore Retail expansion pitch", "Atul's email about the pitch", "the pilot review call"). The pitch event is Fri Nov 20 (last lab day Nov 19), so it's always upcoming. Test_Salesforce computes its dates from the request day.

### 4.4 Engineering (`tools/scenarios/engineering`, new)

- [x] E1 email thread *Aurora pilot - offline status still wrong*: Emil Mon Oct 26 14:00; Atul Thu Oct 29 08:15.
- [x] Teams team **Aurora Engineering**, channel **Platform Migration**, thread T1 (Tama Wed Oct 28 16:00, Maria 16:10, Emil Thu Oct 29 08:30).
- [x] Teams team/channel **Aurora / Engineering** for the Step 4 post; group **Aurora Engineering LT** (Kerry, Tama).
- [x] Test_GitHub (`customconnectors`, ConnectionId `testgithub`, ConnectionName "Test_GitHub", ContentCategory `taskManagement`) with the real 22 GitHub Cloud PR properties and labels. Item PR #287 in `zava-lab/aurora-status`: State Open, Type "Pull request", MergedAt null, Milestone Aurora Sprint 24, CreatedBy/Assignees Triin, Contributors Triin + Tama, LastModifiedBy Tama. CreatedAt Tue Oct 27; review and LastModifiedAt Wed Oct 28 17:20. Content = PR body (references AUR-142) + G2 review as `{"comments":[{SubmittedAt, createdBy, Content, State}]}`. Optional 2–3 merged decoy PRs. Full mapping: engineering doc Appendix D.
- [x] Docs redated to the date rule: cutover and Atul's update Fri Nov 20 15:00; pilot expansion Mon Nov 23; prompts name dates, not days.

### 4.5 Bring your own app

- [x] Seven receipt emails in Emil's inbox:

| Date | From | Amount |
|---|---|---|
| Oct 19 | Alaska Airlines | $486.40 |
| Oct 26 | Yellow Cab | $58.75 |
| Oct 27 | Canlis | $540.00 |
| Oct 28 | Din Tai Fung | $48.20 |
| Oct 29 | The Westin Seattle | $867.00 |
| Oct 29 | Uber | $52.30 |
| Oct 30 | Zava Expense reminder (submit by Fri Nov 20) | n/a |

- [x] Amounts match the earlier trial mock (ER-2001: six items, $2,052.65). Dates are handled in the new mock (§5.4).

### 4.6 Finance

- [x] No changes expected. Verify the finance prompts still match the finance seed and mocks (`ASK_DATE` 2026-10-09). Tenant chat text matches; NVDA, AMD and AVGO are covered in all three mocks; both skills exist; Moody's returns upgrade and downgrade factors; mock tests pass (LSEG 35 + 1 expected fail, FactSet 13, Moody's 15).

### 4.7 Build and deploy

- [x] Add `engineering` (and `expense` if separate) to `SCENARIOS`.
- [x] `validate_package.py` passes; zip and hand over for ingestion (`Connectors_Ignite_EMP_v6.zip`).

## 5. Mock MCP servers

All new mocks follow the same pattern in `mock_mcp_servers/_framework`: real tool names and schemas from traces, seed data from the scenario doc, and **writes scoped to the conversation** (keyed by the Copilot or Cowork conversation ID header, 2-hour retention).

### 5.1 Test_Salesforce (new, Productivity)

- [x] Real Salesforce Hosted MCP tool shapes taken from the SEVAL eval traces: `discover`, `describe`, `dispatch`, `dispatch_readonly`, `display_widget` (`mock_mcp_servers/salesforce`).
- [x] Seed: account *Lakeshore Retail*, the only one on its domain; opportunities 400-store rollout (open, $1.2M) and 50-store pilot (Closed Won, $150K); Wide World Importers (Won) and Tailspin Toys (Lost); contacts Atul and Jahidi only; pitch Event; 2 completed Tasks.
- [x] Writes: create, update and delete for Account, Contact, Lead, Opportunity, Event and Task, kept per conversation.
- [x] Owner scope: everything owned by Emil.
- [x] Dates are fixed to the lab week, not computed from the request day: pitch Event Fri Nov 20, 2026, 10:00–11:00 ET (matches Outlook); rollout close date Dec 31, 2026 (end of quarter); completed Tasks Sep 1 and Oct 1, 2026. Server "now" is `MOCK_NOW` (default Mon Nov 16, 2026).
- [x] Lightning Experience-style viewer for record links (Sales home, list views, record pages, dashboard).
- [x] Deployed as `mock-salesforce` (see `mock_mcp_servers/DEPLOYMENT.md`).
- [x] Plugin **Test_Salesforce** (`mock_plugins/salesforce`, `test_salesforce.zip`), built from `salesforce_v0_20260918_withConstraints` (all 37 skills kept, including `call-prep`, `schedule-meeting`, `handle-objection`, `log-activity`).
- [ ] Upload `test_salesforce.zip` to the tenant and run the Productivity prompts end to end.

### 5.2 Test_Jira (new, Engineering)

- [x] Real Atlassian MCP tool shapes: no traces existed, so all 41 tool schemas and sample responses were captured read-only from the live Atlassian MCP server (`jira/seed_files/tool_schemas.json`).
- [x] Seed: AUR-142 (In Progress, Triin, 8h, last update Oct 26 16:00 ET, no PR link), AUR-145 breakdown (24h, updated Oct 29 08:45 ET), AUR-139 (8h), AUR-151 (16h), Sprint 24 (Oct 26–Nov 20, 32h capacity before the Nov 20 checkpoint).
- [x] Mock server `mock_mcp_servers/jira`: the 41 Atlassian tools (Jira, Confluence, Compass, Teamwork Graph, search), JQL, writes kept per conversation, and a Jira Cloud-style viewer (`/browse/AUR-142`, board, backlog).
- [x] Deployed as `mock-jira` (see `mock_mcp_servers/DEPLOYMENT.md`).
- [x] Plugin **Test_Jira** (`mock_plugins/jira`, `test_jira.zip`), built from *Rovo_CEA 9 (2) 1.zip*: all 4 skills kept (including `sprint-to-slides`), connector points at the mock with no auth, Rovo bot fields removed.
- [ ] Upload `test_jira.zip` to the tenant and run the Engineering prompts end to end. Verify one-slide .pptx output.
- `sprint-to-slides` optionally calls Teamwork Graph and falls back to Jira data. Confluence page creation is optional and suppressed in this lab.

### 5.3 Test_iManage (Legal)

- [x] Build from the existing `mock_mcp_servers/imanage/seed_files` (matter, v4.2 agreement, Exhibits A–D, Playbook v2.1, empty 04 Drafts).
- [x] Writes: save to 04 Drafts, conversation-scoped.
- [x] Use Word/Office debug traces for tool shapes.
- [x] Deployed as `mock-imanage` (see `mock_mcp_servers/DEPLOYMENT.md`).
- [x] Plugin **Test_iManage** (`mock_plugins/imanage`, `test_imanage.zip`), built from the real iManage Work package.

### 5.4 Zava Expense (Bring your own app)

- [x] Build a new mock based on the earlier trial's 9 tools, on the shared framework (`mock_mcp_servers/zava_expense`). Data is frozen in `seed_files/expense_seed.json`, built by `scripts/build_seed.py`.
- [x] Dates are fixed, not computed per request: the clock is Mon Nov 16, 2026 (lab week) and the Seattle trip is Oct 26–29, matching the tenant receipts. New reports start at ER-2001; the six receipts total $2,052.65 with the Westin over-cap night on Oct 28. `MOCK_NOW` overrides the clock for testing.
- [x] Keep the trial's test items: the $6.45 Starbucks charge with no receipt (TX-10106) and the duplicate $52.30 Uber charge (TX-10111).
- [x] Writes (justification, submit) are conversation-scoped. Submit routes to Hannes Niemi.
- [x] Deployed as `mock-zava-expense` (`https://mock-zava-expense.yellowsand-9530f5dc.eastus.azurecontainerapps.io/mcp`).
- [x] Plugin **Test_Zava Expense** (`mock_plugins/zava_expense`, `test_zava_expense.zip`) with the `zava-travel-policy` skill.
- [ ] Confirm the module 07 flow: attendees add the server through the admin click-through, or upload the plugin zip.
- [x] Put the MCP server address in module 07 (checklist and setup step 4), instead of on the seat card.
- [x] Tenant reminder email says the Seattle charges run "from October 5"; the mock's charges (Oct 19–29) fall inside that range. The mock's copy of the email now matches the tenant; the tenant is unchanged.

### 5.5 Retire

- [x] Notion mock and **Test_Notion** plugin: folders and zip removed, ACA app and image deleted.
- [x] Zava Hub app: folder removed and its ACA apps deleted.
- [x] The probe server: it ran on a dev tunnel, not ACA; the tunnel and files were deleted earlier.
- [x] Keep the code in git history; remove the ACA apps after the new mocks are live.

### 5.6 Finance mocks

- [x] LSEG, FactSet, Moody's: no change needed for the finance prompt update.

## 6. Open questions for the owners

- [ ] Legal Step 4 regulator check: is web grounding enough, or seed a short regulatory note in the iManage matter as a fallback? For now, web grounding.

## 7. Before the lab

- [ ] Redeploy mocks; rebuild all test plugin ZIPs (`mock_plugins/build_plugins.py`).
- [ ] Ingest the rebuilt COEP package.
- [ ] Dry run each track as an attendee, in the exact prompt order, and record timings.
- [ ] Update `02-getting-started.md` if the connector display names change.

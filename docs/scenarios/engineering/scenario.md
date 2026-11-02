# Engineering: The fix exists. The customer is still waiting.

> Source: *Ignite_Engineering_Connectors_Lab_v3.docx* (facilitator draft). Converted to Markdown for reference; formatting differs from the original, wording is preserved.
>
> IGNITE LAB654 | Engineering connectors lab | Fictional lab data
>
> **Lab build notes:** Test_GitHub is a mock MCP server (`mock_mcp_servers/github`) with the GitHub MCP server's read tools and the write tools the data supports. Writes are kept per conversation, and merging PR #287 is blocked by branch protection. Appendix D records the earlier synced-connector item shape, which is still in the COEP seed. Test_Jira is a mock MCP server; its plugin follows the structure of *Rovo_CEA 9 (2) 1.zip*.

## At a glance

| | |
|---|---|
| **Experience** | Test_Jira + Test_GitHub; Outlook and Teams. Copilot Chat for investigation, Cowork for the sprint slide and communication. |
| **Timing** | 15-minute target: setup 2 min; Steps 1-4: 2 / 3 / 4 / 3 min; wrap-up 1 min. Confirm in a dry run. |
| **Take home** | A cited explanation, a sprint decision slide, a Teams post, and a customer email draft. |

## Setup: explain the scenario to the room

**Read aloud:** Meet Emil Vanggaard at Zava. He has an email from Atul at Lakeshore Retail. Aurora smart-home hubs keep showing as offline after reconnecting, so store staff are restarting devices that are actually working.

Lakeshore Retail expands its pilot on Monday, November 23, and Atul needs a status update before then. Emil remembers a Jira bug, but its last update only says someone has started working on the fix. Before replying, he needs to know what is really happening.

**Your job:** Find the real status, understand what is blocking the fix, work out the sprint trade-off, and help Emil align the team and reply to Atul. No code change or release is performed.

## Step 1: Where are we with the customer issue?

| | |
|---|---|
| **Time / surface** | 2 min / Copilot Chat / Outlook + Test_Jira |
| **Query to fire** | Atul is asking if the Aurora offline-status bug will be fixed before the pilot expansion. Where are we with the fix, and what have we already told them? |
| **Expected response** | Connects Atul's email to Jira AUR-142. The customer needs an update before the November 23 expansion. Emil said engineering was working on it, not that delivery before the expansion was guaranteed. Jira is In Progress; the last update, October 26, says "I have started working on the fix." The ticket does not tell us whether a fix is ready. Cites the email and Jira. |
| **Seed names only** | E1: Aurora pilot - offline status still wrong<br>J1: AUR-142 - Aurora hubs remain offline after reconnect |
| **Aha in the room** | A tracker status is not a customer commitment. Copilot connects the customer's concern with the team's recorded work, and exposes the missing detail. |

## Step 2: Has someone already raised a fix?

| | |
|---|---|
| **Time / surface** | 3 min / Copilot Chat / Test_GitHub + Teams |
| **Query to fire** | Can you find the PR for this item and where it is blocked? |
| **Expected response** | Finds PR #287 from its reference to AUR-142; the Jira ticket does not supply the PR link. The PR is open and unmerged, with changes requested by Tama. It fixes the old polling service, while the Teams migration discussion confirms the Lakeshore Retail pilot will use the new event-driven service after the November 20 cutover.<br><br>Two things need doing: (1) Triin adapts the fix to the new service; (2) Maria adds and runs the new-service reconnect tests. Tama reviews again after those are done. This is additional work, not just an approval to chase. Cites the PR, review, and Teams discussion. |
| **Seed names only** | G1: PR #287 - Fix stale offline state after reconnect<br>G2: Tama's review - changes requested<br>T1: Aurora status-service cutover - Lakeshore Retail pilot |
| **Aha in the room** | The fix exists, but for the old service. Only connecting the code review with the migration discussion reveals why the customer is still blocked. |

## Step 3: Make the sprint impact clear

| | |
|---|---|
| **Time / surface** | 4 min / Cowork / Test_Jira sprint-to-slides skill |
| **Query to fire** | /skill sprint-to-slides<br>Create one PowerPoint slide for Aurora Sprint 24 showing the impact of this fix and what we should move to make room for LT approval. |
| **Expected response** | Uses Sprint 24 and the newer work breakdown: the bug now needs 24 hours, not the recorded 8. Revised scope is 48 hours against 32 hours of available capacity: a 16-hour gap. Proposes deferring the 16-hour custom-filter enhancement while retaining required rollout regression.<br><br>Produces one slide with customer impact, blocker, scope trade-off, owners, and decision needed. The proposal needs approval; owner availability, sequencing, and release timing remain unconfirmed. |
| **Seed names only** | J2: Aurora Sprint 24 - scope and capacity<br>J3: AUR-145 - new-service work breakdown<br>S1: Test_Jira sprint-to-slides skill<br>B1: Cited investigation from Step 2 |
| **Aha in the room** | The partner skill turns engineering context into a decision-ready slide: not "we are busy," but "this is the work that must move." |
| **Presenter note** | The supplied package includes sprint-to-slides. Its default flow is a report plus a slide outline; this lab requests one .pptx slide only. Verify that narrowed output and the /skill selection in Cowork. Carry the cited Step 2 brief across if needed. |

## Step 4: Align the team and reply to Atul

| | |
|---|---|
| **Time / surface** | 3 min / Cowork / Teams + Outlook |
| **Query to fire** | Share this slide in Aurora's engineering channel and ask LT to approve the revised sprint plan. Draft a reply to Atul with our progress and an update on November 20 at 3 pm. |
| **Expected response** | Prepares a Teams post for Aurora's engineering channel with the slide link, the proposed 16-hour trade-off, and named owners. Asks the engineering leadership team (LT) to approve the scope change and confirm review capacity. Drafts a customer-friendly reply explaining that the fix needs validation for the pilot's service, with Friday, November 20, at 15:00 as the next update.<br><br>Does not expose internal review friction, promise delivery before the expansion, or invent an approved workaround. Shows exact destinations and a real shareable artifact link, or explicitly identifies that upload is still needed. |
| **Seed names only** | T2: Aurora / Engineering channel, LT group, and lab directory<br>E1: Atul's email thread<br>S1 output: Sprint decision slide |
| **Aha in the room** | One evidence base becomes two useful communications: an internal decision request and an honest customer update. Emil reviews what leaves Copilot. |
| **Publication rule** | Default: stop at drafts. If enabled by the facilitator, explicitly approve the Teams post and any upload in the isolated lab tenant. Keep the customer email unsent. |

## Wrap-up (1 minute)

- **Say this:** "We started with a customer email and a stale ticket. Copilot found the real blocker, showed the sprint trade-off, and helped us bring a clear plan to the team and the customer."
- **Ask the room:** What would we have missed if we had replied using only the Jira status?

## Facilitator-only readiness

| | |
|---|---|
| **Validate access** | Pre-connect Test_Jira and Test_GitHub; verify Jira and sprint access, GitHub search permissions, Outlook/Teams access, and Chat-to-Cowork handoff as an attendee. All recipients must be lab identities. |
| **Validate GitHub** | Confirm Test_GitHub finds PR #287 from "AUR-142" and returns Tama's changes-requested review, with citations to the PR. The mock also has write tools (comment, review, label, edit), kept per conversation so attendees don't affect each other. Merging is blocked by branch protection while Tama's changes-requested review stands. |
| **Validate skill** | Package confirms sprint-to-slides, not a tested runtime. Verify one-slide .pptx output, available Jira tools, and a shareable link. Suppress the full report and Confluence archive for this short lab. Test native Teams posting separately; skill instructions are not proof of available tools. |
| **Dry run / reset** | Measure the full flow. All seeded evidence is dated on or before Oct 30, 2026 (the tenant is loaded once); the cutover, checkpoint and expansion fall after the Nov 17–19 lab. Prompts use no relative days. Isolate generated artifacts/posts by seat; reset drafts and outputs without changing shared evidence. Do not infer merge, release, or approved sprint changes. |

**Feedback incorporated:** Prompts assume Emil has read the email. Copilot discovers the PR independently. Jira only says work has started. Decoys, recovery scripts, and the setup facilitator cue are removed. The blocker is two tasks. Step 2 uses the requested query; Step 3 names sprint-to-slides from the supplied package; Step 4 asks LT for approval in the engineering channel without the extra preview sentence.

## Appendix A: Email and Jira seed content

Fictional authoring fixtures. Replace link tokens with actual seeded URLs; do not seed literal placeholders.

| ID | Field | Content |
|---|---|---|
| E1 | Email | Subject: Aurora pilot - offline status still wrong. Participants: Atul Manohar (Lakeshore Retail pilot coordinator), Emil Vanggaard (Zava). Use demo-tenant identities. |
| | Earlier reply | October 26, 14:00 / Emil: "Thanks for flagging the reconnect issue. Engineering is working on a fix, and I will share an update once we have confirmed the validation plan." |
| | Customer ask | October 29, 08:15 / Atul: "Hi Emil, our pilot stores are still seeing Aurora hubs marked offline after they reconnect. Staff keep restarting devices that are actually working. You mentioned a fix was being worked on. Can we expect it before Monday, November 23, when we expand the pilot? I need to brief our store managers before then. Thanks, Atul." |
| | Email invariant | No guaranteed delivery date or approved workaround appears in this thread. |
| J1 | Jira | AUR-142 / Aurora hubs remain offline after reconnect. Project: Aurora. Sprint: Aurora Sprint 24 (October 26 - November 20, 2026). Status: In Progress. Priority: High. Assignee: Triin Lepp. |
| | Description | Lakeshore Retail pilot hubs remain Offline in the dashboard after a successful network reconnect. Telemetry resumes, but staff restart working devices because the visible state is stale. Pilot expansion is November 23. |
| | Last update | October 26, 16:00 / Triin: "I have started working on the fix." Do not mention a PR, review, or migration blocker in this update. |
| | Links / estimate | Link the sprint and AUR-145 breakdown. Do NOT link or name the GitHub PR in the Jira ticket. Record the older remaining estimate as 8 hours. GitHub discovery must use the PR's reference back to AUR-142. |
| | Acceptance | Reconnected pilot devices show Online on the active service; automated new-service reconnect coverage; no regression in existing reconnect behaviour. |

## Appendix B: Sprint and skill seed content

| ID | Field | Content |
|---|---|---|
| J2 | Snapshot | Aurora Sprint 24, October 26 - November 20. As of October 29, 09:00 lab-tenant time. Capacity covers only work before the Friday, November 20, 15:00 checkpoint. |
| | Recorded scope | AUR-142 reconnect bug: 8 team-hours (older estimate).<br>AUR-139 rollout regression: 8 team-hours; required for safe cutover; Maria owns it.<br>AUR-151 custom dashboard filters: 16 team-hours; lower-priority enhancement, no contractual dependency; Triin owns it.<br>Total recorded remaining scope: 32 team-hours. |
| | Capacity | 32 available team-hours before the November 20 checkpoint. Aggregate capacity is not proof of individual availability or sequencing. Confirm the plan with owners before making a commitment. |
| J3 | Breakdown | AUR-145 / Aurora new-service reconnect work breakdown. Updated October 29, 08:45. Linked from AUR-142. This is newer than the bug's narrative update.<br>Task 1: adapt reconnect fix to the event-driven path; Triin; 12 hours.<br>Task 2: add and run new-service reconnect validation/tests; Maria; 8 hours.<br>Follow-up review after the two tasks; Tama; 4 hours.<br>Total replacement estimate for AUR-142: 24 team-hours. |
| | Counting rule | Keep AUR-145 outside the sprint total, or explicitly exclude it from totals. Its 24 hours replace AUR-142's 8 hours; do not add both estimates. |
| | Expected maths | 24 + 8 + 16 = 48 hours revised demand. 48 - 32 = 16 hours over capacity. Deferring AUR-151 removes 16 hours, leaving 32. This is a proposal, not an approved scope change or delivery forecast. Deployment and observation time are not included. |
| S1 | Skill | Verified in Rovo_CEA 9 (2) 1.zip: manifest.json registers skills/sprint-to-slides; SKILL.md names sprint-to-slides. It queries Jira, supports an optional Teamwork Graph enrichment with a Jira-only fallback, generates a Word report and PowerPoint-ready outline, and optionally archives to Confluence. It allows .pptx or Markdown output; no executed runtime is bundled or verified. |
| | Slide contract | Lab adaptation: one .pptx slide, "Aurora pilot \| LT approval needed." Include customer impact, blocker, 32-hour capacity versus 48-hour demand, proposed AUR-151 deferral, owners, LT decision, November 20 checkpoint, and sources. Use hours, not invented velocity/history or collaboration metrics. Skip full-report and Confluence publishing. An outline alone does not meet the slide requirement; validate artifact generation before delivery. |
| B1 | Handoff | Generated from Step 2, not pre-seeded evidence. Include cited facts, timestamps, and actual Outlook/Jira/GitHub/Teams links. Transfer into Cowork if conversation context is not retained. |

## Appendix C: GitHub and Teams seed content

| ID | Field | Content |
|---|---|---|
| G1 | PR | PR #287 / Fix stale offline state after reconnect. Example repo: zava-lab/aurora-status; use the actual lab repo. Author: Triin Lepp. Open, unmerged; changes requested; no release recorded. |
| | PR body | References AUR-142 explicitly with its actual Jira link. Updates the legacy polling status handler so reconnect clears stale Offline state. Includes legacy-path tests. Event-driven status-service coverage is not yet implemented. This reference enables Copilot to discover the PR without a link in Jira. |
| | Checks | Legacy-path checks pass as of October 28, 17:00. Do not imply new-service coverage or deployment success. |
| G2 | Review | Tama Surya / October 28, 17:20 / Changes requested: "The legacy-path fix looks reasonable, but Lakeshore Retail moves to the event-driven status service with the November 20 cutover. Two things are needed: implement the equivalent reconnect correction in that path, and add/run the reconnect tests there. Once both are done, request another platform review. I am not approving this version for the pilot." |
| | Data source | Served by the Test_GitHub mock (`mock_mcp_servers/github/seed_files/seed.json`), with three merged decoy PRs on the same repo. |
| T1 | Thread | Aurora Engineering team / Platform Migration channel. Thread: Aurora status-service cutover - Lakeshore Retail pilot. |
| | Migration context | Tama / October 28, 16:00: "The November 20 status-service cutover is still the plan. The Lakeshore Retail expansion on November 23 will use the event-driven service. A fix confined to the legacy polling path will not resolve that pilot's issue." |
| | Test context | Maria / October 28, 16:10: "We need reconnect coverage on the new path and the rollout regression checks. Passing the old-service tests is not enough to call this ready." |
| | Decision context | Emil / October 29, 08:30: "Bring a scope proposal before we move sprint work. LT needs to approve any deferral; Tama needs to confirm platform review availability. We have not committed a release date to Lakeshore Retail." |
| T2 | Destination | Aurora team / Engineering channel. Leadership group: Aurora Engineering LT. Kerry Allen (engineering lead) approves sprint scope; Tama Surya (platform lead) confirms review capacity. Posting a request does not record approval. Directory: Emil Vanggaard, Atul Manohar, Triin Lepp, Maria Oliva, Tama Surya, Kerry Allen; LT group contains Kerry and Tama. Resolve demo identities, channel, and group mentions before delivery; do not guess addresses or IDs. |
| | Publishing | Use approved tenant storage for a real slide link. A local file path is not a shareable link. If publication is enabled, isolate posts by seat and keep the customer email unsent. |

## Appendix D: GitHub synced item shape (earlier build)

> The lab now uses the Test_GitHub mock MCP server instead. This shape is kept because the COEP seed still contains the `testgithub` connection; the tenant is unchanged.

Reference: the Microsoft GitHub Cloud pull-request connector schema (`github-cloud-prs.json`) and a sample crawl (`github_cloud_pull_requests.jsonl`) from the 3P Frontier Agents synthetic tenant. One item per pull request; **reviews are not separate items**. The connector puts them in the item content as `{"comments":[{SubmittedAt, createdBy, Content, State}]}` after the PR description.

| Property | Type | Semantic label | PR #287 value |
|---|---|---|---|
| Id | String | secondaryId | `287` |
| Url | String | url | `https://github.com/zava-lab/aurora-status/pull/287` |
| Title | String | title | Fix stale offline state after reconnect |
| Description | String | – | G1 PR body (references AUR-142 with its Jira link) |
| CreatedBy | Principal | createdBy | Triin Lepp |
| CreatedAt | DateTime | createdDateTime | 2026-10-27 (after Triin's Jira update) |
| LastModifiedAt | DateTime | lastModifiedDateTime | 2026-10-28T17:20 (Tama's review) |
| MergedAt | DateTime | closedDate | null |
| State | String | state | Open |
| Labels | StringCollection | tags | e.g. `bug`, `aurora-status` |
| Assignees | PrincipalCollection | assignedToPeople | Triin Lepp |
| Contributors | PrincipalCollection | authors | Triin Lepp, Tama Surya |
| RepositoryName | String | containerName | aurora-status |
| RepositoryURL | String | containerUrl | `https://github.com/zava-lab/aurora-status` |
| RepositoryDescription | String | – | Aurora hub status service |
| Type | String | itemType | Pull request |
| ItemPath | String | itemPath | zava-lab/aurora-status |
| OrganizationName / OrganizationUrl | String | – | zava-lab / `https://github.com/zava-lab` |
| Milestone | String | sprintName | Aurora Sprint 24 |
| DueDate | DateTime | DueDate | null |
| LastModifiedBy | Principal | lastModifiedBy | Tama Surya |

Content (text): the PR body, then the G2 review as `{"comments":[{"SubmittedAt":"2026-10-28T17:20:00Z","createdBy":"sampatel","Content":"<G2 text>","State":"ChangesRequested"}]}`. Checks (G1 "legacy-path checks pass, Oct 28 17:00") go in the body text.

COEP mapping: `customconnectors`, ConnectionId `testgithub`, ConnectionName "Test_GitHub", ContentCategory `taskManagement`. COEP supports all 11 property types and every label used here (`DueDate` is spelled `dueDate` in COEP). Properties labelled `assignedToPeople` or `secondaryId` must be queryable, retrievable and searchable (COEP rule). Optionally add 2–3 merged decoy PRs on the same repo so retrieval has to pick #287.


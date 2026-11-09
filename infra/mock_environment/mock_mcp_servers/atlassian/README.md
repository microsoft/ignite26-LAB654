# Rovo mock server

Mock of the Atlassian Rovo MCP server for the [engineering scenario](../../../../docs/scenarios/engineering/scenario.md) and [lab part 6](../../../../instructions/06-engineering.md). In the lab it appears as the **Rovo_Lab** connector. See the [mock servers README](../README.md) for the shared framework and how to run, test and deploy.

It serves one Atlassian site, **zava-online**, with Jira and Confluence:

- **Jira:** the **Aurora** (AUR) project and the active *Aurora Sprint 24*. Copilot can read issues with JQL, Rovo search and the Teamwork Graph, and it can create, edit, transition, comment on, log work on and link issues.
- **Confluence:** the **Aurora Engineering** (AUR) space. Copilot can read spaces, pages and comments, search with CQL, and create and update pages and comments.

Changes are kept per conversation, and Jira Cloud and Confluence look-alike viewers show them. Compass is on the tool list, but the site has no data for it.

The same seed also feeds the lab tenant's synced **Jira** and **Confluence** connectors (see [`tools/scenarios/engineering`](../../tools/scenarios/engineering/__init__.py)), so Copilot Chat and Cowork see the same sprint, issues and pages.

## Prompts it powers

| Lab step | Surface | What Copilot asks Rovo for |
|----------|---------|----------------------------|
| 1, 2 | Copilot Chat | Nothing. These steps use the synced Jira and Confluence connectors, which hold the same data |
| 4 | Cowork | `sprint-to-slides` skill: Aurora Sprint 24 issues with their status, owners and priorities, the sprint plan page, and the AUR-142 risk with its ADR-014 dependency |

## Tools

All 41 tools are the live server's. Their names, descriptions and input schemas were captured in November 2026 from `https://mcp.atlassian.com/v1/mcp/authv2` (`seed_files/tool_schemas.json`). Response shapes follow read-only calls made to a test site during the same capture. No test site data is in this repo.

| Tools | Serves |
|-------|--------|
| `atlassianUserInfo`, `getAccessibleAtlassianResources`, `lookupJiraAccountId` | The signed-in user (Emil Vanggaard), the zava-online site and its scopes, user search |
| `getJiraIssue`, `searchJiraIssuesUsingJql` | Issues, with `fields` selection. JQL supports `project`, `key`, `issuetype`, `status`, `statusCategory`, `priority`, `assignee`, `reporter`, `labels`, `sprint` (including `openSprints()`), `text`, `summary`, `created`, `updated`, `currentUser()`, `AND`/`OR`/`NOT`, `IN` and `ORDER BY` |
| `getVisibleJiraProjects`, `getJiraProjectIssueTypesMetadata`, `getJiraIssueTypeMetaWithFields`, `getTransitionsForJiraIssue`, `getIssueLinkTypes`, `getJiraIssueRemoteIssueLinks` | Project, issue type, field, workflow and link metadata |
| `createJiraIssue`, `editJiraIssue`, `transitionJiraIssue`, `addCommentToJiraIssue`, `addWorklogToJiraIssue`, `createIssueLink` | Writes. New issues continue from AUR-152 |
| `getTeamworkGraphContext`, `getTeamworkGraphObject`, `addTeamworkGraphContext` | Teamwork Graph for Jira work items: assignee, reporter, linked items and sprint |
| `search`, `fetch` | Rovo search and fetch across the site's issues and Confluence pages |
| `getConfluenceSpaces`, `getPagesInConfluenceSpace`, `getConfluencePage`, `getConfluencePageDescendants`, `searchConfluenceUsingCql` | Spaces and pages. Page bodies come back as storage HTML (default), markdown or ADF. CQL supports `type`, `space`, `title`, `id`, `parent`, `ancestor`, `label`, `creator`, `contributor`, `text`, `siteSearch`, `AND`/`OR` and `ORDER BY` |
| `getConfluencePageFooterComments`, `getConfluencePageInlineComments`, `getConfluenceCommentChildren` | Page comments and replies |
| `createConfluencePage`, `updateConfluencePage`, `createConfluenceFooterComment`, `createConfluenceInlineComment` | Writes. New pages continue from 98500 and go under the space home page unless a parent is given. Inline comments need text that's on the page |
| `getContentFormatGuide` | The body format guide |
| 6 Compass tools | The scope error the live server returns when Compass isn't granted |

- Successes are pretty-printed JSON, as on the live server. Failures are `{"error": true, "message": ...}`, where Jira REST errors keep their `errorMessages`/`errors` body as a string.
- `editJiraIssue` can't set `status`. It tells Copilot to use `transitionJiraIssue`, as the live server does.
- Time values use Jira's 8-hour day and 5-day week, so `8h` shows as `1d`.

## Data

| Item | Content |
|------|---------|
| Users | Emil Vanggaard (signed in, Product), Triin Lepp, Maria Oliva, Kerry Allen, Tama Surya (Platform Lead) |
| Sprint | *Aurora Sprint 24*, active, October 26 to November 20, 2026. Goal: cut the pilot stores over to the event-driven status service on November 20 and be ready for the Lakeshore Retail pilot expansion on November 23 |
| AUR-133, AUR-137 | Done: heartbeat events (Maria) and the firmware 4.2 telemetry gaps (Triin, a resolved decoy with the same pilot label) |
| AUR-136, AUR-139 | In Progress and on track: the cutover runbook (Kerry) and rollout regression checks (Maria) |
| AUR-142 | Bug *Aurora hubs remain offline after reconnect*: In Progress, High, Triin, labels `lakeshore-retail-pilot` and `at-risk`. Its comments flag the risk and say the fix waits on a design sign-off, with no date. They don't name the PR or the approver |
| AUR-151 | Story *Custom dashboard filters for the store status view*: To Do, Low, Triin |
| Confluence pages | Space home; *Lakeshore Retail pilot – delivery commitments* (the record of the November 20 and 23 dates); *ADR-014: Reconnect state handling on the event-driven status service* (Proposed, awaiting Tama's approval, linked to AUR-142 and PR #287); *Aurora Sprint 24 plan*; the cutover runbook |
| Comments | On ADR-014, Triin asks Tama for the decision. On the commitments page, Tama confirms the November 20 cutover |

GitHub (the GitHub_Lab mock) holds the rest of the story: PR #287 in `zava-lab/aurora-status`, where Tama requested changes on October 28.

The data is in `seed_files/seed.json`, written from the scenario. Names come from CELA's approved fictitious names list (see the [mock environment README](../../README.md)). The site's IDs, account IDs and URLs are generated and don't match any real site.

## Conversations and the viewer

- Reads and writes use the `x-microsoft-ai-conversationid` header. Each conversation's writes are kept on top of the seed, so later reads in the same conversation see them. They expire after about 2 hours idle.
- Calls without the header see the seed, and their writes are discarded.
- The viewer is a read-only Jira Cloud look-alike, marked "Not affiliated with Atlassian":

| Path | Page |
|------|------|
| `/jira/software/projects/AUR/boards/57` | Sprint board: sprint goal, days remaining, To Do / In Progress / Done columns |
| `/jira/software/projects/AUR/boards/57/backlog` | Backlog: the sprint with its estimate totals, then the backlog |
| `/jira/software/projects/AUR/list` | List view (`?text=` filters it) |
| `/browse/{key}` | Issue page: description, linked work items, activity (`?activity=all\|comments\|worklog`) and details |
| `/wiki/spaces/AUR/pages/{id}/{slug}` | Confluence page: breadcrumbs, owner, version, body, labels and comments, with the space's page tree. `/wiki` and `/wiki/spaces/AUR` open the space home |

- Every page also exists under `/v/{token}/...`, which shows one conversation's changes. Issue links in tool results use it. Opening a conversation's new issue or page without the token redirects to the token URL. An expired token shows the seed with a notice.
- `/ex/jira/{cloudId}/rest/api/3/issue/{id}` (the `self` links in tool results) redirects to the issue page, and `/wiki/rest/api/content/{id}` and `/wiki/x/{tiny}` redirect to the Confluence page. Priority icons and issue type and project avatars are served at the paths the tool results point to.

## Widgets

`getJiraIssue` and `searchJiraIssuesUsingJql` are MCP Apps tools, as on the live server. Their `_meta` and the UI resources' `_meta` (CSP, `prefersBorder`, `openai/*` keys) match the capture.

| Resource | Purpose |
|----------|---------|
| `ui://widget/jira-widget.html` | MCP Apps widget (`text/html;profile=mcp-app`) |
| `ui://widget/open-ai/jira-widget.html` | The same widget under the `openai/outputTemplate` URI |

- Results carry `structuredContent`. Search: `{issues: {nodes, webUrl, pageInfo}, context}`. Single issue: `{issues: {nodes}, context}`, with `descriptionEditable` and `webUrl` on the node.
- The widget is one self-contained HTML file (`mock_atlassian/ui/jira-widget.html`); the live server loads a remote bundle.
- Text content keeps the mock's existing shape. The live server wraps it in `{"data": ...}`.
- The `view` argument (`compact`, `evidence`, `full`) is accepted and ignored.
- Errors carry no `structuredContent`.
- `/issues?jql=...` (the search `webUrl`) redirects to the list view.

## Run and test

From `infra/mock_environment/mock_mcp_servers`:

```powershell
$env:PYTHONPATH = "_framework;atlassian"
python -m mock_atlassian                    # http://localhost:8000/mcp and the viewer at http://localhost:8000/
python -m pytest atlassian/tests
docker build -f atlassian/Dockerfile -t mock-atlassian:latest .
```

| Variable | Default | Purpose |
|----------|---------|---------|
| `PUBLIC_BASE_URL` | `http://localhost:8000` | Public address. Used for the site URL, `self` links and viewer links |
| `JIRA_VIEW_SECRET` | random per process | Key for the viewer's link tokens. Set it to keep links stable across restarts |
| `MOCK_NOW` | `2026-10-29T13:00:00Z` | The server's "now" (09:00 lab-tenant time on October 29, the scenario's snapshot) |

Run one replica: conversation changes live in memory.

## Known differences from the live server

These shapes weren't seen in the capture, so the mock's versions are inferred:

- The error for an unknown `cloudId`, and Confluence `NOT_FOUND` and validation errors.
- Confluence write responses, comment shapes and CQL result shapes. They follow the Confluence REST v2 and v1 search APIs.
- The success responses of `createIssueLink` and `addTeamworkGraphContext`.
- `getTeamworkGraphContext` in summary mode, and its result for a Jira space.
- Rovo `search` and `fetch` results.
- The error text for invalid arguments, and for `editJiraIssue` fields that can't be set or moved.

Other differences:

- JQL and CQL cover the clauses listed above, not the full languages. Unsupported JQL returns no issues; unknown CQL fields don't filter.
- Each issue type has the system fields only. A real site adds custom fields, such as story points and team.
- Issue, account and link IDs are fixed, and the real `atlassian.net` host is never used.

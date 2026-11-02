# Jira mock server

Mock of the Atlassian Rovo MCP server for the [engineering scenario](../../../../docs/scenarios/engineering/scenario.md) and [lab part 6](../../../../instructions/06-engineering.md). In the lab it appears as the **Test_Jira** connector. See the [mock servers README](../README.md) for the shared framework and how to run, test and deploy.

It serves one Atlassian site, **zava-online**. Its Jira has the **Aurora** (AUR) project and the active *Aurora Sprint 24*. Copilot can read issues with JQL, Rovo search and the Teamwork Graph, and it can create, edit, transition, comment on, log work on and link issues. Changes are kept per conversation, and a Jira Cloud look-alike viewer shows them. Confluence and Compass are on the tool list, but the site has no data for either.

## Prompts it powers

| Lab step | What Copilot asks Jira for |
|----------|----------------------------|
| 1 | AUR-142: status, last update, estimate and linked items |
| 2 | AUR-142's key and summary, which Copilot uses to find PR #287 in Test_GitHub |
| 3 | `sprint-to-slides` skill: Aurora Sprint 24 issues with their estimates, owners and priorities, and the AUR-145 breakdown linked from AUR-142 |

## Tools

All 41 tools are the live server's. Their names, descriptions and input schemas were captured in November 2026 from `https://mcp.atlassian.com/v1/mcp/authv2` (`seed_files/tool_schemas.json`). Response shapes follow read-only calls made to a test site during the same capture. No test site data is in this repo.

| Tools | Serves |
|-------|--------|
| `atlassianUserInfo`, `getAccessibleAtlassianResources`, `lookupJiraAccountId` | The signed-in user (Emil Vanggaard), the zava-online site and its scopes, user search |
| `getJiraIssue`, `searchJiraIssuesUsingJql` | Issues, with `fields` selection. JQL supports `project`, `key`, `issuetype`, `status`, `statusCategory`, `priority`, `assignee`, `reporter`, `labels`, `sprint` (including `openSprints()`), `text`, `summary`, `created`, `updated`, `currentUser()`, `AND`/`OR`/`NOT`, `IN` and `ORDER BY` |
| `getVisibleJiraProjects`, `getJiraProjectIssueTypesMetadata`, `getJiraIssueTypeMetaWithFields`, `getTransitionsForJiraIssue`, `getIssueLinkTypes`, `getJiraIssueRemoteIssueLinks` | Project, issue type, field, workflow and link metadata |
| `createJiraIssue`, `editJiraIssue`, `transitionJiraIssue`, `addCommentToJiraIssue`, `addWorklogToJiraIssue`, `createIssueLink` | Writes. New issues continue from AUR-152 |
| `getTeamworkGraphContext`, `getTeamworkGraphObject`, `addTeamworkGraphContext` | Teamwork Graph for Jira work items: assignee, reporter, linked items and sprint |
| `search`, `fetch` | Rovo search and fetch across the site's issues |
| `getContentFormatGuide` and 11 Confluence tools | Empty results or `NOT_FOUND`: the site has no Confluence spaces |
| 6 Compass tools | The scope error the live server returns when Compass isn't granted |

- Successes are pretty-printed JSON, as on the live server. Failures are `{"error": true, "message": ...}`, where Jira REST errors keep their `errorMessages`/`errors` body as a string.
- `editJiraIssue` can't set `status`. It tells Copilot to use `transitionJiraIssue`, as the live server does.
- Time values use Jira's 8-hour day and 5-day week, so `8h` shows as `1d`.

## Data

| Item | Content |
|------|---------|
| Users | Emil Vanggaard (signed in), Triin Lepp, Maria Oliva, Kerry Allen, Tama Surya |
| Sprint | *Aurora Sprint 24*, active, October 26 to November 20, 2026. Its goal records the 32 team-hours of capacity before the Friday, November 20, 15:00 checkpoint |
| AUR-142 | Bug *Aurora hubs remain offline after reconnect*: In Progress, High, Triin, 8h, in the sprint. One comment on October 26: "I have started working on the fix." It relates to AUR-145 and doesn't mention the PR |
| AUR-139 | Task *Rollout regression checks for the status-service cutover*: To Do, High, Maria, 8h, in the sprint |
| AUR-151 | Story *Custom dashboard filters for the store status view*: To Do, Low, Triin, 16h, in the sprint |
| AUR-145 | Task *Aurora new-service reconnect work breakdown*: To Do, High, Triin, no estimate and no sprint, updated October 29, 08:45. Its description holds the 24-hour breakdown (Triin 12h, Maria 8h, Tama 4h) that replaces AUR-142's 8 hours |

The data is in `seed_files/seed.json`, written from Appendices A and B of the scenario. Names come from CELA's approved fictitious names list (see the [mock environment README](../../README.md)). The site's IDs, account IDs and URLs are generated and don't match any real site.

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

- Every page also exists under `/v/{token}/...`, which shows one conversation's changes. Issue links in tool results use it. Opening a conversation's new issue without the token redirects to the token URL. An expired token shows the seed with a notice.
- `/ex/jira/{cloudId}/rest/api/3/issue/{id}` (the `self` links in tool results) redirects to the issue page. Priority icons and issue type and project avatars are served at the paths the tool results point to.

## Run and test

From `infra/mock_environment/mock_mcp_servers`:

```powershell
$env:PYTHONPATH = "_framework;jira"
python -m mock_jira                    # http://localhost:8000/mcp and the viewer at http://localhost:8000/
python -m pytest jira/tests
docker build -f jira/Dockerfile -t mock-jira:latest .
```

| Variable | Default | Purpose |
|----------|---------|---------|
| `PUBLIC_BASE_URL` | `http://localhost:8000` | Public address. Used for the site URL, `self` links and viewer links |
| `JIRA_VIEW_SECRET` | random per process | Key for the viewer's link tokens. Set it to keep links stable across restarts |
| `MOCK_NOW` | `2026-10-29T13:00:00Z` | The server's "now" (09:00 lab-tenant time on October 29, the scenario's snapshot) |

Run one replica: conversation changes live in memory.

## Known differences from the live server

These shapes weren't seen in the capture, so the mock's versions are inferred:

- The error for an unknown `cloudId`, and Confluence `NOT_FOUND` errors.
- The success responses of `createIssueLink` and `addTeamworkGraphContext`.
- `getTeamworkGraphContext` in summary mode, and its result for a Jira space.
- Rovo `search` and `fetch` results.
- The error text for invalid arguments, and for `editJiraIssue` fields that can't be set or moved.

Other differences:

- JQL covers the clauses listed above, not the full language. Unsupported syntax returns no issues.
- Each issue type has the system fields only. A real site adds custom fields, such as story points and team.
- Issue, account and link IDs are fixed, and the real `atlassian.net` host is never used.

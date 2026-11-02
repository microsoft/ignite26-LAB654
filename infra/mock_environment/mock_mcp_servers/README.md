# Mock MCP servers

Mock MCP servers for the third-party connectors used in the scenarios. Each server has its own folder, exposes the same tool names, descriptions and input schemas as the real MCP server, and serves scenario data from its `seed_files/` subfolder.

| Server | Scenario | Status |
|--------|----------|--------|
| [`imanage/`](imanage/README.md) | Legal | **Built.** Workspace, folder and document search, document text and profiles, and document and folder uploads kept per conversation, with an iManage Work-style matter viewer. Trey Research – AI Platform Agreement matter (agreement, Exhibits A–D, playbook) |
| [`jira/`](jira/README.md) | Engineering | **Built.** The 41 Atlassian Rovo MCP tools (Jira, Confluence, Compass, Teamwork Graph and search), with schemas captured from the live server, JQL, issue create, edit, transition, comment, worklog and link kept per conversation, and a Jira Cloud-style viewer. Aurora project, Sprint 24, AUR-142 and its AUR-145 breakdown |
| [`github/`](github/README.md) | Engineering | **Built.** 8 read-only tools from the GitHub MCP server (get_me, user, repository and pull request search, list and read pull requests, labels). It has no write tools, which keeps the read-only behaviour of the synced connector it replaces. It also has a GitHub-style viewer. zava-lab/aurora-status with PR #287, Tama's changes-requested review and three merged decoy PRs |
| [`lseg/`](lseg/README.md) | Finance | **Built.** I/B/E/S estimates and actuals, Worldscope fundamentals, pricing, news, symbology |
| [`factset/`](factset/README.md) | Finance | **Built.** Metrics search, entity reference, RBICS, fundamentals, consensus, prices |
| [`moodys/`](moodys/README.md) | Finance | **Built.** Entity search, ratings and history, credit opinions |
| [`salesforce/`](salesforce/README.md) | Productivity | **Built.** The five Salesforce Hosted MCP tools (discover, describe, dispatch, dispatch_readonly, display_widget) over a small Zava Sales Cloud org: SOQL, GraphQL, search, sObject reads, and record create, update and delete kept per conversation, with a Lightning Experience-style viewer. Lakeshore Retail account, the Aurora 400-store rollout opportunity, the pitch Event, Atul and Jahidi as contacts |
| [`zava_expense/`](zava_expense/README.md) | Custom connector | **Built.** Zava's in-house expense app: reports, card charges, travel policy, policy check, spend vs budget, and report create, update and submit kept per conversation. Emil Vanggaard's Seattle trip with an over-cap hotel night and a duplicate Uber charge |

## How the built servers work

Every server has the same three layers:

| Layer | Where | What it does |
|-------|-------|--------------|
| Data | `<server>/seed_files/*.json`, `_domains/<domain>/` | Recorded and curated data. Finance servers share one company model in `_domains/finance/mockfin` so LSEG, FactSet and Moody's never contradict each other. |
| Logic | `<server>/mock_<server>/` | One class per tool: name, description, JSON input schema, extra validation and `run()`. Errors use the real server's wording and shape. |
| Fallback | `mockmcp.Seeded` | When a request goes beyond the recorded data (another quarter, peer or date window), values are generated from the company model with a seed derived from the inputs. The same request always gets the same answer. |

Read-only tools are marked with the MCP `readOnlyHint` annotation. Each tool call receives the host's `x-microsoft-ai-conversationid` header as `ctx.conversation_id`. iManage, Salesforce, Jira and Zava Expense use it to keep write changes per conversation (see [imanage/README.md](imanage/README.md#conversations-and-the-viewer), [salesforce/README.md](salesforce/README.md#conversations-and-the-viewer), [jira/README.md](jira/README.md#conversations-and-the-viewer) and [zava_expense/README.md](zava_expense/README.md#how-writes-work)).

## Layout

```text
mock_mcp_servers/
├── _framework/mockmcp/     # Shared: Tool base class, server spec, HTTP/stdio app, errors, seeded RNG, test helpers
├── _domains/finance/       # Shared finance model (mockfin): 8 semiconductor companies, calendars, financials, prices
├── lseg/  factset/  moodys/  imanage/  salesforce/  jira/  github/  zava_expense/
│   ├── mock_<server>/      # Tools and server spec (python -m mock_<server>)
│   ├── seed_files/         # Server-specific data
│   ├── tests/              # Trace replay and behaviour tests; tests/fixtures holds the recorded calls
│   └── Dockerfile
├── requirements.txt  requirements-dev.txt  pytest.ini  conftest.py
```

## Run locally

From this folder, with Python 3.12:

```powershell
pip install -r requirements-dev.txt
$env:PYTHONPATH = "_framework;_domains/finance;moodys"
python -m mock_moodys                     # streamable HTTP on :8000/mcp, health at /healthz
python -m mock_moodys --transport stdio   # for a local MCP client
```

| Setting | Default | Purpose |
|---------|---------|---------|
| `MCP_TRANSPORT` / `--transport` | `http` | `http` or `stdio` |
| `HOST`, `PORT` | `0.0.0.0`, `8000` | HTTP bind address |
| `LOG_LEVEL` | `INFO` | Logs go to stderr |
| `MOCK_NOW` | `2026-10-16T09:00:00Z` | The server's "now". All "latest", "last quarter" and date-window answers are relative to it. |
| `PUBLIC_BASE_URL` | unset | iManage, Salesforce, Jira and GitHub: public address of the server, used in links to their viewers. Defaults to `http://localhost:8000` when unset. |
| `IMANAGE_VIEW_SECRET`, `SALESFORCE_VIEW_SECRET`, `JIRA_VIEW_SECRET` | random per process | iManage, Salesforce and Jira: key for the viewer's link tokens. Set it to keep links stable across restarts. |
| `CORS_ORIGIN_REGEX` | Copilot's widget renderer, plus `localhost` | Regex of browser origins allowed to call the server. Microsoft 365 Copilot renders MCP Apps widgets on `*.widget-renderer.usercontent.microsoft.com`. |

### MCP Apps widgets

A tool can return an interactive widget ([MCP Apps](https://modelcontextprotocol.io/extensions/apps/overview)). To add one:

1. Put a self-contained HTML file in the server's `ui/` folder. No external scripts, styles or fonts: the host blocks network access. `<!-- include:NAME -->` inlines another file from the same folder.
2. Register it in the server spec with `UiResource(uri="ui://<server>/<name>", ...)` and `load_html(...)` from `mockmcp.ui`.
3. Set `ui_resource = "ui://<server>/<name>"` on the tool, and return `structuredContent` so the widget gets the data.

The HTML is loaded at startup, so restart the server after editing a widget. Only LSEG has widgets; Moody's and FactSet don't have them on the live servers either.

## Test

```powershell
python -m pytest
```

Each server replays the calls recorded in the finance session trace and compares the output with the recording, ignoring volatile fields (`timestamp`, `qaQueryTime`, `retrievedAt`). Further tests cover other companies and periods, validation errors, determinism and `/healthz`.

## Build and deploy

Build from this folder so the image can include `_framework` and `_domains`:

```powershell
docker build -f lseg/Dockerfile -t mock-lseg:latest .
docker run -p 8000:8000 mock-lseg:latest
```

Each image runs one server over stateless streamable HTTP on port 8000, which suits Azure Container Apps (ingress to port 8000, health probe `/healthz`). The finance servers can run any number of replicas. iManage, Salesforce, Jira and Zava Expense keep write state in memory, so each must run exactly one.

See [DEPLOYMENT.md](DEPLOYMENT.md) for the Azure setup, update steps, troubleshooting and the live server URLs. See [COST_ESTIMATE.md](COST_ESTIMATE.md) for hosting costs and capacity during the lab.
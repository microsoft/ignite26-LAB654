# Mock MCP servers

Mock MCP servers for the third-party connectors used in the scenarios. Each server has its own folder, exposes the same tool names, descriptions and input schemas as the real MCP server, and serves scenario data from its `seed_files/` subfolder.

| Server | Scenario | Status |
|--------|----------|--------|
| [`imanage/`](imanage/README.md) | Legal | **Built.** Workspace, folder and document search, document text and profiles, and document and folder uploads kept per conversation, with an iManage Work-style matter viewer. Trey Research – AI Platform Agreement matter (agreement, Exhibits A–D, playbook) |
| [`lseg/`](lseg/README.md) | Finance | **Built.** I/B/E/S estimates and actuals, Worldscope fundamentals, pricing, news, symbology |
| [`factset/`](factset/README.md) | Finance | **Built.** Metrics search, entity reference, RBICS, fundamentals, consensus, prices |
| [`moodys/`](moodys/README.md) | Finance | **Built.** Entity search, ratings and history, credit opinions |
| [`notion/`](notion/README.md) | Productivity | **Built.** Search, fetch, query, and page and data-source writes kept per conversation, and a Notion-style page viewer so returned links open. Aurora launch tracker, launch plan, decision log, 2 decoy trackers |

## How the built servers work

Every server has the same three layers:

| Layer | Where | What it does |
|-------|-------|--------------|
| Data | `<server>/seed_files/*.json`, `_domains/<domain>/` | Recorded and curated data. Finance servers share one company model in `_domains/finance/mockfin` so LSEG, FactSet and Moody's never contradict each other. |
| Logic | `<server>/mock_<server>/` | One class per tool: name, description, JSON input schema, extra validation and `run()`. Errors use the real server's wording and shape. |
| Fallback | `mockmcp.Seeded` | When a request goes beyond the recorded data (another quarter, peer or date window), values are generated from the company model with a seed derived from the inputs. The same request always gets the same answer. |

Read-only tools are marked with the MCP `readOnlyHint` annotation. Each tool call receives the host's `x-microsoft-ai-conversationid` header as `ctx.conversation_id`. Notion and iManage use it to keep write changes per conversation (see [notion/README.md](notion/README.md#how-writes-work) and [imanage/README.md](imanage/README.md#conversations-and-the-viewer)).

## Layout

```text
mock_mcp_servers/
├── _framework/mockmcp/     # Shared: Tool base class, server spec, HTTP/stdio app, errors, seeded RNG, test helpers
├── _domains/finance/       # Shared finance model (mockfin): 8 semiconductor companies, calendars, financials, prices
├── lseg/  factset/  moodys/  notion/  imanage/
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
| `PUBLIC_BASE_URL` | unset | Notion and iManage: public address of the server. When set, Notion links to its page viewer instead of `app.notion.com`. iManage always links to its own viewer and uses `http://localhost:8000` when unset. See [notion/README.md](notion/README.md#page-viewer). |
| `NOTION_VIEW_SECRET`, `IMANAGE_VIEW_SECRET` | random per process | Notion and iManage: key for the viewer's link tokens. Set it to keep links stable across restarts. |
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

Each image runs one server over stateless streamable HTTP on port 8000, which suits Azure Container Apps (ingress to port 8000, health probe `/healthz`). The finance servers can run any number of replicas. Notion and iManage keep write state in memory, so each must run exactly one.

See [DEPLOYMENT.md](DEPLOYMENT.md) for the Azure setup, update steps, troubleshooting and the live server URLs. See [COST_ESTIMATE.md](COST_ESTIMATE.md) for hosting costs and capacity during the lab.
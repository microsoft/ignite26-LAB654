# Mock MCP servers

Mock MCP servers for the third-party connectors used in the scenarios. Each server has its own folder, exposes the same tool names, descriptions and input schemas as the real MCP server, and serves scenario data from its `seed_files/` subfolder.

| Server | Scenario | Status |
|--------|----------|--------|
| [`imanage/`](imanage/README.md) | Legal | Data spec. Seed data: Cognivault-Nexus matter (agreement, Exhibits A–D, playbook) |
| [`harvey/`](harvey/README.md) | Legal | Data spec. No seed data yet (answers from public law) |
| [`lseg/`](lseg/README.md) | Finance | **Built.** I/B/E/S estimates and actuals, Worldscope fundamentals, pricing, news, symbology |
| [`factset/`](factset/README.md) | Finance | **Built.** Metrics search, entity reference, RBICS, fundamentals, consensus, prices |
| [`moodys/`](moodys/README.md) | Finance | **Built.** Entity search, ratings and history, credit opinions |
| [`smartsheet/`](smartsheet/README.md) | Productivity | Data spec: Verdantis Aurora Launch Tracker (11 rows, 3 comments), 3 decoy sheets, per-seat copies |
| [`notion/`](notion/README.md) | Productivity | Data spec: Aurora Launch Plan, Weekly Sync – Oct 6, Launch Decision Log with 3 prior decisions |
| [`verdantis_hub/`](verdantis_hub/README.md) | Productivity | Not an MCP server. Intranet pages are seeded in the tenant (`intranetwebsite`); README documents them |

## How the built servers work

Every server has the same three layers:

| Layer | Where | What it does |
|-------|-------|--------------|
| Data | `<server>/seed_files/*.json`, `_domains/<domain>/` | Recorded and curated data. Finance servers share one company model in `_domains/finance/mockfin` so LSEG, FactSet and Moody's never contradict each other. |
| Logic | `<server>/mock_<server>/` | One class per tool: name, description, JSON input schema, extra validation and `run()`. Errors use the real server's wording and shape. |
| Fallback | `mockmcp.Seeded` | When a request goes beyond the recorded data (another quarter, peer or date window), values are generated from the company model with a seed derived from the inputs. The same request always gets the same answer. |

Read-only tools are marked with the MCP `readOnlyHint` annotation. Write tools (planned for legal) will need per-session state; the framework doesn't provide that yet.

## Layout

```text
mock_mcp_servers/
├── _framework/mockmcp/     # Shared: Tool base class, server spec, HTTP/stdio app, errors, seeded RNG, test helpers
├── _domains/finance/       # Shared finance model (mockfin): 8 semiconductor companies, calendars, financials, prices
├── lseg/  factset/  moodys/
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

Each image runs one server over stateless streamable HTTP on port 8000, which suits Azure Container Apps (ingress to port 8000, health probe `/healthz`, any number of replicas).

See [DEPLOYMENT.md](DEPLOYMENT.md) for the Azure setup, update steps, troubleshooting and the live server URLs.
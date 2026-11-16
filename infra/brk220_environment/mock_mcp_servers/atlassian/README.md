# Rovo mock server (BRK220)

Mock of the Atlassian Rovo MCP server for the [BRK220 scenario](../../scenario.md). In Copilot it appears as the **Rovo** connector. Adapted from the LAB654 Rovo mock (`microsoft/ignite26-LAB654`, branch `mock-environment-setup`); the tools and response shapes are unchanged, only the data and a few viewer defaults differ.

It serves one Atlassian site, **northwind-ltd**:

- **Jira:** the **Northwind Support** (INC) project of customer incidents. The customer is a `customer-<name>` label. Copilot can read issues with JQL, Rovo search and the Teamwork Graph, and create, edit, transition, comment on, log work on and link issues.
- **Confluence:** the **Customer Success** (CS) space (Contoso Ltd account overview with the open SSO ask, Q3 QBR action items) and the **Product Roadmap** (PROD) space (identity roadmap with the dates Product approved for customer commitments).

Writes are kept per conversation, and Jira Cloud and Confluence look-alike viewers show them.

## Data

| Item | Content |
|------|---------|
| Users | Megan Bowen (signed in, Sales), Arjun Kumar, Rosa Diaz and Mei Lin (Support), Isaiah Langer (Customer Success) |
| INC-40211 | Contoso Ltd: API latency in EU region. **Highest**, To Do, **unassigned**, 9 days old. Comment: the CIO has escalated |
| INC-40188 | Contoso Ltd: intermittent SSO login failures. **Highest**, In Progress, Rosa Diaz, 12 days old |
| INC-40302 | Contoso Ltd: EU API gateway timeouts on the bulk export endpoint. High, To Do, **unassigned**, 4 days old |
| INC-39412, INC-39750 | Done: earlier Contoso EU latency incidents, both resolved by **Arjun Kumar** (the basis for the owner suggestion) |
| Decoys | INC-40260 (Contoso **Pharmaceuticals**, a different customer), INC-40295 (Tailwind Traders), INC-39881 (Contoso SSO, Rosa), INC-39960 (Adatum latency, Mei) |
| Confluence | *Contoso Ltd – account overview* (SSO roadmap commitment: Open, no committed date), *Q3 QBR – Contoso Ltd action items*, *Identity and SSO roadmap (H1 2027)* (SCIM 2.0 GA March 31, 2027 and per-subsidiary conditional access in Q2 2027, both committable) |

The data is in `seed_files/seed.json`.

### Relative dates

Jira issue dates move with the calendar: the seed's `_anchor` day (2026-11-18) is shifted to the mock's "today", so INC-40211 is always 9 days old, INC-40188 12 and INC-40302 4, whichever day you rehearse. "Today" is `MOCK_NOW` if set, otherwise the real UTC date. Confluence dates stay fixed.

## Run and test

From `infra/brk220_environment/mock_mcp_servers`:

```powershell
pip install -r requirements-dev.txt
$env:PYTHONPATH = "_framework;atlassian"
python -m mock_atlassian                    # http://localhost:8000/mcp and the viewer at http://localhost:8000/
python -m pytest atlassian/tests
docker build -f atlassian/Dockerfile -t mock-atlassian-brk220:latest .
```

| Variable | Default | Purpose |
|----------|---------|---------|
| `PUBLIC_BASE_URL` | `http://localhost:8000` | Public address. Used for the site URL, `self` links and viewer links |
| `JIRA_VIEW_SECRET` | random per process | Key for the viewer's link tokens. Set it to keep links stable across restarts |
| `TENANT_EMAIL_DOMAIN` | `northwind-ltd.example` | Email domain for the Northwind users. Set it to the COEP tenant's domain |
| `MOCK_NOW` | the real time | The server's "now", and the day the ticket dates are anchored to |
| `MOCK_SHARED_STATE` | unset | `1`: all conversations and header-less calls share one set of changes (for Demo 2 → Demo 3 across surfaces). Restart to reset |

Run one replica: conversation changes live in memory.

## Viewer

| Path | Page |
|------|------|
| `/jira/software/projects/INC/boards/12` | Kanban board of every INC issue (there's no sprint) |
| `/jira/software/projects/INC/list` | List view (`?text=` filters it) |
| `/browse/{key}` | Issue page |
| `/wiki/spaces/CS`, `/wiki/spaces/PROD` | Confluence space home pages |

Every page also exists under `/v/{token}/...`, which shows one conversation's changes. Issue links in tool results use it.

## Changes from the LAB654 mock

- New seed; `{domain}` in user emails and relative Jira dates (`store.py`).
- Optional shared state across conversations, `MOCK_SHARED_STATE` (`store.py`).
- The clock defaults to the real time instead of a fixed date (`server.py`).
- Jira's default priorities (Highest to Lowest); new issues default to Medium. An Incident type icon (`web.py`).
- Without an active sprint, the board shows every issue; `/wiki` and `/wiki/spaces/{key}` open the requested space's home page (`web.py`).
- New Confluence pages are numbered from 131500.

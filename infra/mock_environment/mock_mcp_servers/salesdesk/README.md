# SalesDesk mock server

Mock of the SalesDesk Hosted MCP server for the [productivity scenario](../../../../docs/scenarios/productivity/scenario.md) and [lab part 5](../../../../instructions/05-productivity.md). In the lab it appears as the **SalesDesk_Lab** connector. See the [mock servers README](../README.md) for the shared framework and how to run, test and deploy.

It serves a small Sales Cloud org for **Zava**. Emil Vanggaard owns the Lakeshore Retail account and its open opportunity, and the pitch meeting is logged on it. Copilot can read the org with SOQL, GraphQL, search and sObject reads, and create, update or delete records. Changes are kept per conversation, and a SalesDesk look-alike viewer shows them.

## Prompts it powers

| Lab step | What Copilot asks SalesDesk for |
|----------|----------------------------------|
| 1 | `call-prep` skill: the pitch Event, the Lakeshore Retail account, the open opportunity, the attendees who are contacts, and the activity history |
| 3 | `schedule-meeting` skill: Jahidi and Atul with their emails, the one open opportunity, then a new Event for the security review (write) |

## Tools

Tool names, descriptions and input schemas are the live server's, taken from SEVAL traces with the `SalesDesk_` prefix the host adds removed (`seed_files/tool_schemas.json`). Response envelopes follow the same traces.

| Tool | Serves |
|------|--------|
| `discover` | Ranks the 298 recorded REST, SOQL and GraphQL capability cards by keyword overlap (the live server uses embeddings) |
| `describe` | A capability's recorded details. Cards without a recorded `describe` return the card's description with no steps |
| `dispatch_readonly` | GET only: SOQL (`/query`), GraphQL, search, `result-groups`, `object-schema`, sObject reads and describes, `limits`, `tooling/query` |
| `dispatch` | POST, PATCH and DELETE on Account, Contact, Lead, Opportunity, Event and Task, plus everything `dispatch_readonly` serves |
| `display_widget` | Renders a dynamic widget definition through the `ui://` widget resource |

- Success: `{status_code, body, url}`. Failure: `{error_code: "API_ERROR", message, status_code, body}`, where `body` is a JSON string, as on the live server.
- POST returns 201 with `{id, success, errors}`. PATCH and DELETE return 204. A stage change on an opportunity adds an `OpportunityHistory` row.
- Bad fields return `INVALID_FIELD`. A reference to a record that doesn't exist returns `INVALID_CROSS_REFERENCE_KEY`.
- Routes the traces show failing on a real org (Tableau, Einstein search answers, virtual activity IDs) fail here with the same status and message.

## Data

| Object | Records |
|--------|---------|
| Users | Emil Vanggaard (owner of everything below), Zoe Armstrong (Director of Retail Sales) |
| Accounts | Lakeshore Retail (customer), Wide World Importers (customer), Tailspin Toys (prospect) |
| Contacts | Atul Manohar (Director of Store Operations) and Jahidi Juma (IT Security Lead), both at Lakeshore Retail |
| Opportunities | *Lakeshore Retail – Aurora 400-store rollout* (Proposal/Price Quote, $1,200,000), *Lakeshore Retail – Aurora pilot (50 stores)* (Closed Won, $150,000), a Wide World Importers win and a Tailspin Toys loss, with stage history |
| Activities | The pitch Event, *Lakeshore Retail – Aurora expansion pitch* (Fri Nov 20, 2026, 10:00–11:00), and the pilot's completed Tasks |
| Dashboard | *Aurora Sales Pipeline* |

The data is built in `mock_salesdesk/seed.py`. Company names and email domains come from CELA's approved fictitious names list (see the [mock environment README](../../README.md)). Nanami Nakayama isn't in SalesDesk, as the scenario requires. The other files in `seed_files/` are `catalog.json` (the recorded `discover` cards and `describe` results) and `limits.json` (the `/limits` response).

## Conversations and the viewer

- Reads and writes use the `x-microsoft-ai-conversationid` header. Each conversation's writes are kept on top of the seed, so later reads in the same conversation see them. They expire after about 2 hours idle.
- Calls without the header see the seed, and their writes are discarded.
- The viewer is a read-only SalesDesk look-alike, marked as a mock environment:

| Path | Page |
|------|------|
| `/lightning/page/home` | Sales home: quarterly performance, key deals, today's events and tasks |
| `/lightning/o/{Object}/list` | List views (Accounts, Contacts, Opportunities, Leads, Calendar, Tasks) |
| `/lightning/r/{Object}/{id}/view` | Record pages with related lists (`?tab=activity` for the activity timeline) |
| `/lightning/o/Dashboard/home` | All Dashboards list |
| `/lightning/r/Dashboard/01ZHp0000000001IAA/view` | The *Aurora Sales Pipeline* dashboard |
| `/lightning/search?q=` | Global search results |

- Every page also exists under `/v/{token}/...`, which shows one conversation's changes. Record URLs in tool results use it. Opening a conversation's new record without the token redirects to the token URL. An expired token shows the seed with a notice.
- `/img/icon/t4v35/standard/{name}.svg` serves the object icons that the search API's `iconUrl` points to.

## Run and test

From `infra/mock_environment/mock_mcp_servers`:

```powershell
$env:PYTHONPATH = "_framework;salesdesk"
python -m mock_salesdesk              # http://localhost:8000/mcp and the viewer at http://localhost:8000/
python -m pytest salesdesk/tests
docker build -f salesdesk/Dockerfile -t mock-salesdesk:latest .
```

| Variable | Default | Purpose |
|----------|---------|---------|
| `PUBLIC_BASE_URL` | `http://localhost:8000` | Public address. Used for the instance URL in `url` fields and for viewer links |
| `SALESDESK_VIEW_SECRET` | random per process | Key for the viewer's link tokens. Set it to keep links stable across restarts |
| `SF_EMAIL_DOMAIN` | the Zava tenant domain | Email domain for Zava users and Lakeshore Retail contacts. It must match the COEP tenant so `call-prep` can match attendees by email |
| `MOCK_NOW` | `2026-11-16T15:00:00Z` | The server's "now" |

Run one replica: conversation changes live in memory.

The lab deployment runs as the `mock-salesdesk` container app at https://mock-salesdesk.yellowsand-9530f5dc.eastus.azurecontainerapps.io (MCP endpoint `/mcp`).

## Known differences from the live server

- `discover` ranks by keyword overlap, not embeddings, so its order can differ from the live server's.
- SOQL and GraphQL cover what the traces and the lab skills send, not the full languages. Unsupported syntax returns `MALFORMED_QUERY` or a GraphQL error.
- The org has only the objects the scenario uses. Other objects return the errors a real org gives for an unknown object (`NOT_FOUND` on REST, "sObject type is not supported" in SOQL).
- Record IDs are fixed and the real instance host name is never used.

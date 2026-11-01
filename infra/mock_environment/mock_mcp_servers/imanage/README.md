# iManage mock server

Mock of the iManage Work MCP server for the [legal scenario](../../../../docs/scenarios/legal/scenario.md) and [lab part 4](../../../../instructions/04-legal.md). In the lab it appears as the **Test_iManage** connector. See the [mock servers README](../README.md) for the shared framework and how to run, test and deploy, and [MOCK_SERVER_ARCHITECTURE.md](../../../../MOCK_SERVER_ARCHITECTURE.md) for the general pattern.

It serves one matter, **Trey Research – AI Platform Agreement** (`Dev!1870`, client Zava, Inc.), as user **EMIL**. Copilot can search and read it, and save new documents and folders to it. Changes are kept per conversation, and every link opens a mock iManage Work page that shows them.

## Prompts it powers

| Lab step | What Copilot asks iManage for |
|----------|-------------------------------|
| 2 | Find the matter, open `02 Playbooks` and read the Zava AI Procurement Playbook (the hard stops are in Section 14) |
| 3 | Re-read playbook sections while redlining the vendor agreement |
| 4 (Cowork) | Save the research note to `03 Research` and the redline, fallback memo and summary to `04 Drafts` |

## Tools

Schemas come from the live connector's tool list in the recorded Office (Word) trace. "Output" says whether the trace shows a real response.

| Tool | Serves | Schema | Output |
|------|--------|--------|--------|
| `search_workspaces` | Workspaces by name, with `topMatchingId` | Trace | Trace |
| `get_container_children` | Folders and documents in a workspace or folder (`hasMore`, numeric `cursor`) | Trace | Trace |
| `search_folders` | Folders by name; `*` wildcards and comma-separated lists | Trace | Trace |
| `search` | Documents (and the workspace) where every query word appears; title matches first, 25 per page | Trace | Trace |
| `fetch` | Full document text, 150,000 characters per page | Trace | Trace |
| `get_document_profile` | The document profile | Trace | Trace |
| `get_workspace_profile`, `get_document_versions`, `get_recent_documents`, `get_recent_workspaces`, `get_user_information` | As named | Trace | Inferred |
| `download_document`, `get_libraries` | Document text by page; the `DEV` library | Trace | Inferred |
| `get_workspace_templates` | Always empty | Trace | Inferred |
| `upload_document` | Saves text as a new PDF or Word document in a writable folder | Inferred | Inferred |
| `create_folder` | Creates a subfolder in a writable folder | Inferred | Inferred |

Only `03 Research` and `04 Drafts` (and folders created inside them) accept writes. Other folders return 403 with the list of writable folders.

## Conversations and the viewer

- Reads and writes use the `x-microsoft-ai-conversationid` header. Each conversation gets its own copy of the matter on first write. Copies expire after about 2 hours idle.
- Calls without the header see the original matter, and their writes are discarded.
- Links in results go to `/v/{token}/work/link/{w|f|d}/{id}`, a read-only iManage Work-style page showing that conversation's copy. `/work/link/...` shows the original matter. Pages are marked **MOCK IMANAGE**.

### Original matter links

These open the seed data on the deployed server. They never show a conversation's changes.

| Item | URL path (after `https://mock-imanage.yellowsand-9530f5dc.eastus.azurecontainerapps.io`) |
|---|---|
| Workspace: Trey Research – AI Platform Agreement | `/work/link/w/Dev!1870` |
| Folder: 01 Vendor Paper | `/work/link/f/Dev!1871` |
| Folder: 02 Playbooks | `/work/link/f/Dev!1872` |
| Folder: 03 Research | `/work/link/f/Dev!1873` |
| Folder: 04 Drafts | `/work/link/f/Dev!1874` |
| Trey Research Vendor Agreement v4.2 | `/work/link/d/DEV!252561.1` |
| Exhibit A – Service Description and SLA | `/work/link/d/DEV!252562.1` |
| Exhibit B – Fee Schedule and Order Form | `/work/link/d/DEV!252563.1` |
| Exhibit C – Security and Data Protection | `/work/link/d/DEV!252564.1` |
| Exhibit D – Acceptable Use Policy | `/work/link/d/DEV!252565.1` |
| Zava AI Procurement Playbook v2.1 | `/work/link/d/DEV!252567.1` |
## Data

- `seed_files/TreyResearch-AIPlatform_matter/`: the matter as files, taken from the legal seed kit. `matter.json` holds the client, matter name and each document's profile.
- `seed_files/workspace.json`: the matter the server loads, with extracted document text. `seed_files/tool_schemas.json`: the live tool names, descriptions and input schemas. Both are built by `scripts/build_seed.py`. Rebuild after changing the matter files.
- `tests/fixtures/`: the seven recorded responses with Office's wrapper removed and the fictitious names swapped in, built by `scripts/build_trace_fixtures.py`. The tests check the mock's keys, key order and value types against them.

## Run and test

From `infra/mock_environment/mock_mcp_servers`:

```powershell
$env:PYTHONPATH = "_framework;imanage"
python -m mock_imanage                # http://localhost:8000/mcp and the viewer at http://localhost:8000/
python -m pytest imanage/tests
docker build -f imanage/Dockerfile -t mock-imanage:latest .
```

Set `PUBLIC_BASE_URL` to the public address when deployed, so links open. Run one replica: conversation copies live in memory.

## Known differences from the live server

- The live connector found nothing for "…AI Procurement Playbook hard stops" even though every word is in the playbook. Its matching rule isn't known; the mock matches when every word appears.
- The mock adds keys the trace doesn't show (`id`, `url`, `wstype` and `has_subfolders` on children), and the `{summary..., items}` layout is the mock's reading of Office's flattened entries.
- Outputs marked "Inferred" above weren't in the trace. The two write tools aren't in the live tool list; their names and inputs are a guess at what a writing iManage connector would offer.
- Dates are fixed at 2026-10-26 15:00 UTC (`MOCK_NOW` overrides). The real host name is never used.

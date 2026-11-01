# iManage mock server

Mock of the iManage Work MCP server. The server isn't built yet; this folder holds its seed data.

## Seed files

`seed_files/TreyResearch-AIPlatform_matter/` is the legal scenario's matter workspace, taken from the legal seed kit:

| Folder | Contents |
|--------|----------|
| `01 Vendor Paper` | Trey Research Vendor Agreement v4.2 and Exhibits A–D |
| `02 Playbooks` | Zava AI Procurement Playbook v2.1 |
| `03 Research` | Empty. Copilot saves the step 2 research note here. |
| `04 Drafts` | Empty. Copilot and Cowork save the step 3–4 outputs here. |

`matter.json` holds the client, matter name and the document profile for each file (description, document type, author), as the kit specifies them.

Between lab runs, clear `03 Research` and `04 Drafts`.

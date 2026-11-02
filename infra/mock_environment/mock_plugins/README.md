# Mock plugins

Microsoft 365 app packages for the lab's third-party connectors. Each package is a copy of the real connector package, pointed at the matching [mock MCP server](../mock_mcp_servers/DEPLOYMENT.md).

## Packages

| Folder | Name | Skills | Mock MCP server | Source |
|---|---|---|---|---|
| `lseg/` | Test_LSEG | 8 | `https://mock-lseg.yellowsand-9530f5dc.eastus.azurecontainerapps.io/mcp` | `gim-home/skill-studio`: `connector-skills-packages/lseg/MOSified/v0_20260918/basic` |
| `moodys/` | Test_Moodys | 7 | `https://mock-moodys.yellowsand-9530f5dc.eastus.azurecontainerapps.io/mcp` | `gim-home/skill-studio`: `connector-skills-packages/moodys/MOSified/v0_20260918/withConstraints` |
| `factset/` | Test_FactSet | None | `https://mock-factset.yellowsand-9530f5dc.eastus.azurecontainerapps.io/mcp` | `gim-home/M365FCCMOSPackages`: `mos-packages/factset/inDev/factset.zip` |
| `notion/` | Test_Notion | 4 | `https://mock-notion.yellowsand-9530f5dc.eastus.azurecontainerapps.io/mcp` | `gim-home/skill-studio`: `connector-skills-packages/notion/MOSified/v0_20260902/basic` |
| `imanage/` | Test_iManage | None | `https://mock-imanage.yellowsand-9530f5dc.eastus.azurecontainerapps.io/mcp` | `gim-home/M365FCCMOSPackages`: `mos-packages/imanage-work/inDev/imanage-work.zip` |
| `salesforce/` | Test_Salesforce | 37 | `https://mock-salesforce.yellowsand-9530f5dc.eastus.azurecontainerapps.io/mcp` | `gim-home/skill-studio`: `connector-skills-packages/salesforce/MOSified/v0_20260918/withConstraints` |
| `jira/` | Test_Jira | 4 | `https://mock-jira.yellowsand-9530f5dc.eastus.azurecontainerapps.io/mcp` | Atlassian Rovo package `Rovo_CEA 9 (2) 1.zip` (Rovo for Microsoft Teams, version `2026.04.11`) |
| `zava_expense/` | Test_Zava Expense | 1 | `https://mock-zava-expense.yellowsand-9530f5dc.eastus.azurecontainerapps.io/mcp` | Written for the lab (no real connector); skill `zava-travel-policy` |

## Changes from the source packages

Icons and `skills/` are copied unchanged. `addendum.json` (internal publishing rules for which audiences see the connector) is left out because tenant uploads don't use it. `manifest.json` changes:

| Field | Change | Why |
|---|---|---|
| `name`, `agentConnectors[].displayName` | `Test_<connector>` | Shows it is a test server |
| `id`, `agentConnectors[].id` | New GUIDs | Avoids clashing with the real package in the same tenant |
| `developer` | Tezan Sahu, with this repo's URL for the website, privacy and terms links | Not published by Microsoft or the data provider |
| `mcpServerUrl` | Mock server URL | Serves mock data |
| `authorization` | Removed | Mock servers need no sign-in |
| `description.full` (Notion only) | "Does not create or edit" sentence replaced with one saying it can create pages and update properties | The lab's productivity flow updates tracker rows |
| `description.full` (iManage only) | Adds a sentence saying it can save new documents and folders to a matter | The mock supports document and folder uploads |
| `description` (Jira only) | Rewritten to describe the Jira tools in Copilot instead of the Rovo Teams bot | The package ships only the connector and skills |
| `bots`, `copilotAgents`, `webApplicationInfo`, `permissions`, `supportsChannelFeatures`, `validDomains`, `defaultInstallScope`, `publisherDocsUrl` (Jira only) | Removed | They register Atlassian's real Rovo bot and app, which the mock doesn't provide |
| `color.png` (Jira only) | Renamed from `color-prod.png` | Matches the other packages |

## Build packages

The ready-to-upload packages are `test_lseg.zip`, `test_moodys.zip`, `test_factset.zip`, `test_notion.zip`, `test_imanage.zip`, `test_salesforce.zip`, `test_jira.zip` and `test_zava_expense.zip` in this folder. After changing a plugin, rebuild them:

```powershell
python infra\mock_environment\mock_plugins\build_plugins.py              # all plugins
python infra\mock_environment\mock_plugins\build_plugins.py lseg moodys  # selected plugins
python infra\mock_environment\mock_plugins\build_plugins.py --list       # list plugins
```

Any subfolder with a `manifest.json` counts as a plugin. The script checks the manifest, icons and skill folders before building `test_<folder>.zip`, with `manifest.json` at the root.

If a mock server URL changes, update `mcpServerUrl` in that package's `manifest.json` and bump `version`.

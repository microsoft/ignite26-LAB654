# BRK220 demo: mock connectors environment

Mock environment for the Microsoft Ignite 2026 breakout **BRK220 Copilot Connectors: Unlock your enterprise knowledge and workflows**. Megan Bowen (Northwind Ltd) prepares and de-risks the Contoso Ltd renewal with Salesforce (MCP), Jira (Rovo MCP), Confluence (Confluence connector) and Microsoft 365, driven by one `renewal-prep` skill.

Built on the LAB654 mock environment ([`infra/mock_environment`](../mock_environment)): same framework, tools and package layout, new data.

**Setting up a new tenant?** Follow [SETUP_NEW_TENANT.md](SETUP_NEW_TENANT.md).

Start with [scenario.md](scenario.md): the revised demo script, the Fabrikam pricing twist and the expected results.

## Layout

| Path | What |
|---|---|
| [`scenario.md`](scenario.md) | Revised Demo 1 and Demo 2 script, cast, story, expected results, and what changed from the outline |
| [`mock_mcp_servers/`](mock_mcp_servers) | Mock MCP servers: [`atlassian/`](mock_mcp_servers/atlassian/README.md) (Rovo: Jira and Confluence) and [`salesforce/`](mock_mcp_servers/salesforce/README.md), plus the shared `_framework/` |
| [`mock_plugins/`](mock_plugins) | Microsoft 365 app packages: `rovo/` (shown in Copilot as **Rovo**) and `salesforce/` (**Salesforce**, which ships the `renewal-prep` skill). `build_plugins.py` builds `<name>_brk220.zip` |
| [`mock_plugins/salesforce/skills/renewal-prep/`](mock_plugins/salesforce/skills/renewal-prep/SKILL.md) | The skill: BRIEF (Demo 1) and CLOSE-OUT (Demo 2) workflows and drafting rules |
| [`confluence/`](confluence) | `BRK220_Confluence_Seed_Pages.docx`: the Confluence spaces and pages to create on the Atlassian site the Confluence connector indexes |
| [`video/`](video) | `make_video.py`: builds narrated videos from Playwright recordings (captions, highlight boxes, edge-tts voiceover) |
| [`tenant/`](tenant) | COEP grounding package for the Microsoft 365 content: `tools/scenario.py` (users, email thread, Teams chat, QBR meeting and transcript), `tools/documents.py` (OneDrive Word files), `tools/build_tenant.py`, `tools/validate_package.py`, and the generated `Connectors_BRK220_Demo/` |

## Run locally

Requires Python 3.12 or later (3.13 tested).

```powershell
cd infra/brk220_environment/mock_mcp_servers
pip install -r requirements-dev.txt
python -m pytest                                   # both servers

$env:PYTHONPATH = "_framework;atlassian"; $env:PORT = "8001"; python -m mock_atlassian
$env:PYTHONPATH = "_framework;salesforce"; $env:PORT = "8002"; python -m mock_salesforce
```

MCP endpoints are at `/mcp`, health at `/healthz`, and the Jira, Confluence and Lightning look-alike viewers at `/`.

## Build the packages

```powershell
pip install -r infra/brk220_environment/tenant/requirements.txt
python infra/brk220_environment/mock_plugins/build_plugins.py       # rovo_brk220.zip, salesforce_brk220.zip
python infra/brk220_environment/tenant/tools/build_tenant.py        # Connectors_BRK220_Demo/
python infra/brk220_environment/tenant/tools/validate_package.py    # schema and cross-file checks
```

Build the plugins first: the tenant package copies them to `DAConfig/` and installs them for Megan through `das.config.json`.

## Deploy

### Current deployment

| Resource | Value |
|---|---|
| Subscription | Shiladitya Saha's Visual Studio subscription (ask him for access or changes) |
| Resource group | `rg-brk220-demo` (East US) |
| Container registry | `brk220demo87588.azurecr.io` |
| Container Apps environment | `brk220-env` (`salmonstone-078b8962.eastus.azurecontainerapps.io`) |
| Rovo mock | `northwind-atlassian`, image `mock-atlassian-brk220:v4`, `https://northwind-atlassian.salmonstone-078b8962.eastus.azurecontainerapps.io/mcp` |
| Salesforce mock | `northwind-salesforce`, image `mock-salesforce-brk220:v3`, `https://northwind-salesforce.salmonstone-078b8962.eastus.azurecontainerapps.io/mcp` |

The apps have neutral names because Copilot shows a tool result's host name in its citations.

Each app: 0.5 vCPU, 1 GiB, `--min-replicas 1 --max-replicas 1` (one replica, because conversation changes live in memory; kept warm because a cold start can make Copilot report the source as unavailable). `PUBLIC_BASE_URL` is set to the app's address, the viewer secret is a Container Apps secret, and `MOCK_BADGE=0` hides the viewers' mock badge and footer for recordings. Health is at `/healthz`; the viewers are at `/`.

### Update a server

Run from `infra/brk220_environment/mock_mcp_servers`. Use a new tag every time; reusing a tag doesn't create a new revision.

```powershell
$RG = "rg-brk220-demo"; $ACR = "brk220demo87588"; $S = "atlassian"; $TAG = "v5"   # or salesforce
az acr build -r $ACR -f "$S/Dockerfile" -t "mock-$S-brk220:$TAG" .
az containerapp update -n "northwind-$S" -g $RG --image "$ACR.azurecr.io/mock-$S-brk220:$TAG"
```

| Change | Command |
|---|---|
| Set the tenant email domain | `az containerapp update -n northwind-$S -g $RG --set-env-vars TENANT_EMAIL_DOMAIN=<tenant>.onmicrosoft.com` |
| Allow scale to zero after the event | `az containerapp update -n northwind-$S -g $RG --min-replicas 0` |
| Reset all conversation changes | `az containerapp revision restart -n northwind-$S -g $RG --revision (az containerapp show -n northwind-$S -g $RG --query properties.latestRevisionName -o tsv)` |
| Logs | `az containerapp logs show -n northwind-$S -g $RG --follow` |
| Delete everything after the event | `az group delete -n $RG --yes --no-wait` |

If a server URL changes, update `mcpServerUrl` in `mock_plugins/<name>/manifest.json`, bump `version`, and rebuild the plugins and the tenant package. `build_plugins.py` warns while a URL is still a placeholder.

### Deploy from scratch

```powershell
az group create -n $RG -l eastus
az acr create -g $RG -n $ACR --sku Basic --admin-enabled true
az containerapp env create -n brk220-env -g $RG -l eastus
az acr build -r $ACR -f "$S/Dockerfile" -t "mock-$S-brk220:v1" .
az containerapp create -n "northwind-$S" -g $RG --environment brk220-env --image "$ACR.azurecr.io/mock-$S-brk220:v1" `
  --target-port 8000 --ingress external --registry-server "$ACR.azurecr.io" `
  --registry-username (az acr credential show -n $ACR --query username -o tsv) `
  --registry-password (az acr credential show -n $ACR --query "passwords[0].value" -o tsv) `
  --secrets "view-secret=<random string>" --min-replicas 1 --max-replicas 1 --cpu 0.5 --memory 1Gi `
  --env-vars PUBLIC_BASE_URL=https://northwind-$S.<environment default domain> TENANT_EMAIL_DOMAIN=<tenant>.onmicrosoft.com `
             MOCK_BADGE=0 "$VIEW_SECRET_VAR=secretref:view-secret"   # JIRA_VIEW_SECRET (atlassian) or SALESFORCE_VIEW_SECRET (salesforce)
```

Keep `--min-replicas 1`: a cold start can make Copilot report the source as unavailable. Use neutral app names (not `mock-...`), because Copilot shows the host name in citations. [`../mock_environment/mock_mcp_servers/DEPLOYMENT.md`](../mock_environment/mock_mcp_servers/DEPLOYMENT.md) has troubleshooting for these steps.

## Open items

| Item | Status |
|---|---|
| Mock server hosting | Deployed (see [Current deployment](#current-deployment)) |
| Tenant email domain | Set: both mocks run with `TENANT_EMAIL_DOMAIN=a830edad9050849coepVQFKxObf.onmicrosoft.com` |
| COEP tenant | `Connectors_BRK220_Demo` v3.0 (MSIT, NAM), physical tenant `12760e26-a286-49b4-8e56-b8b18f7d07b8`, expires Feb 7, 2027. Evalset `BRK220_Connectors_Contoso_Renewal` v3 (`443d1628d9f34d1095faba217a395bd7`), packages 1.0.2. The package in this folder is built for a **new** tenant (`ActionType: Install`) |
| Confluence synced connector | Live: CS and PROD spaces on `graphc-test.atlassian.net`, indexed into the tenant by the Confluence connector. The Rovo mock still serves the same pages as a fallback |
| Demo 2 Jira approval loop | Open. On Nov 12 Copilot repeated the approved Jira writes five times (19 *Allow once* prompts, about 9 minutes); every call succeeded on the server. Copilot-side; use the recording for Demo 2 until fixed |
| SharePoint for the renewal template | OneDrive for v1 (COEP SharePoint needs a `sites.config`) |
| MCP App widget (KPI strip, ticket table) | Out of scope for this iteration; the skill returns tables |
| Demo dates | Microsoft 365 items are dated on or before Nov 6, 2026 (`EVIDENCE_CUTOFF` in `tenant/tools/scenario.py`); Jira ticket ages follow the run date |

All names, companies and data are fictitious.

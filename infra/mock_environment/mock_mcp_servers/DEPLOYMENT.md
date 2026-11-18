# Deploying the mock MCP servers to Azure Container Apps

Each mock MCP server runs as its own Azure Container App. All of them share one resource group, one container registry and one Container Apps environment.

## Current deployments

| Server | Container app | Image | MCP URL |
|---|---|---|---|
| LSEG | `mock-lseg` | `mock-lseg:v3` | `https://mock-lseg.yellowsand-9530f5dc.eastus.azurecontainerapps.io/mcp` |
| FactSet | `mock-factset` | `mock-factset:v1` | `https://mock-factset.yellowsand-9530f5dc.eastus.azurecontainerapps.io/mcp` |
| Moody's | `mock-moodys` | `mock-moodys:v2` | `https://mock-moodys.yellowsand-9530f5dc.eastus.azurecontainerapps.io/mcp` |
| iManage | `mock-imanage` | `mock-imanage:v4` | `https://mock-imanage.yellowsand-9530f5dc.eastus.azurecontainerapps.io/mcp` |
| SalesDesk | `mock-salesdesk` | `mock-salesdesk:v2` | `https://mock-salesdesk.yellowsand-9530f5dc.eastus.azurecontainerapps.io/mcp` |
| EngHub | `mock-enghub` | `mock-enghub:v1` | `https://mock-enghub.yellowsand-9530f5dc.eastus.azurecontainerapps.io/mcp` |
| Rovo (Jira + Confluence) | `mock-atlassian` | `mock-atlassian:v2` | `https://mock-atlassian.yellowsand-9530f5dc.eastus.azurecontainerapps.io/mcp` |
| GitHub | `mock-github` | `mock-github:v3` | `https://mock-github.yellowsand-9530f5dc.eastus.azurecontainerapps.io/mcp` |
| Zava Expense | `mock-zava-expense` | `mock-zava-expense:v1` | `https://mock-zava-expense.yellowsand-9530f5dc.eastus.azurecontainerapps.io/mcp` |

Health checks are at the same host with `/healthz` instead of `/mcp`. Every app runs 0.5 vCPU and 1 GiB. Every app is set to `--min-replicas 1` (since 4 November 2026) so it stays warm during testing and the lab; set it back to 0 afterwards to save cost. The finance apps run 1 to 3 replicas. GitHub runs exactly one replica: it keeps each conversation's write changes in memory and stays warm. It has `PUBLIC_BASE_URL` set so pull request links open its GitHub-style viewer (for example `/zava-lab/aurora-status/pull/287`), and `GITHUB_VIEW_SECRET` set so a conversation's `/v/...` links keep working. iManage, SalesDesk, EngHub and Zava Expense run exactly one replica, because they keep each conversation's write changes in memory. iManage has `PUBLIC_BASE_URL` set, so `document_url` links open its matter viewer under `/v/...`. SalesDesk has it set too, so record URLs open its SalesDesk-style viewer (the root URL opens Sales home). EngHub has it set, so issue and page links open its EngHub and EngHub Docs viewers (for example `/browse/AUR-142` and `/wiki/spaces/AUR/pages/98457`; the root URL opens the Sprint 24 board).
## Azure resources

| Resource | Name |
|---|---|
| Resource group | `rg-ignite-2026` (East US) |
| Container registry | `ignite2026mcpacr` (`ignite2026mcpacr.azurecr.io`) |
| Container Apps environment | `ignite2026-env` |
| Container apps | `mock-<server>`, for example `mock-lseg` |

Run every command from `infra/mock_environment/mock_mcp_servers` (PowerShell). The build context must be this folder so that images can include `_framework/` and `_domains/`.

## Prerequisites

- Azure CLI 2.60 or later, with the `containerapp` extension (`az extension add -n containerapp --upgrade`)
- Docker Desktop running
- Contributor access to the Azure subscription

## 1. Sign in

```powershell
az login --tenant <tenant-id> --use-device-code
az account set --subscription "<subscription name or id>"
az account show --query "{user:user.name, subscription:name}" -o table
```

Use `--tenant` if a plain `az login` fails with an MFA or "no subscriptions" error. See [Troubleshooting](#troubleshooting).

## 2. One-time setup

Skip this section if the resources already exist.

```powershell
$RG  = "rg-ignite-2026"
$LOC = "eastus"
$ACR = "ignite2026mcpacr"
$ENV = "ignite2026-env"

az group create -n $RG -l $LOC --tags project=ignite2026 lab=LAB654
az acr create -g $RG -n $ACR --sku Basic --admin-enabled true
az containerapp env create -n $ENV -g $RG -l $LOC
```

The environment takes a few minutes to create. It also creates a Log Analytics workspace.

## 3. Build and push an image

```powershell
$S   = "lseg"   # lseg | factset | moodys | imanage | salesdesk | enghub | github | zava_expense (name the app mock-zava-expense: app names can't contain _)
$TAG = "v1"

az acr login -n $ACR
docker build -f "$S/Dockerfile" -t "$ACR.azurecr.io/mock-${S}:$TAG" -t "$ACR.azurecr.io/mock-${S}:latest" .
docker push "$ACR.azurecr.io/mock-${S}:$TAG"
docker push "$ACR.azurecr.io/mock-${S}:latest"
```

Without Docker, `az acr build -r $ACR -f <folder>/Dockerfile -t mock-<name>:$TAG .` builds in the registry.

If `pip install` fails inside the build, add `--build-arg PIP_INDEX_URL=<mirror>/simple/`. See [Troubleshooting](#troubleshooting).

To test an image locally before pushing:

```powershell
docker run --rm -p 8000:8000 "$ACR.azurecr.io/mock-${S}:$TAG"
curl http://localhost:8000/healthz
```

## 4. Create the container app (first deployment only)

```powershell
$USER = az acr credential show -n $ACR --query username -o tsv
$PASS = az acr credential show -n $ACR --query "passwords[0].value" -o tsv

az containerapp create -n "mock-$S" -g $RG --environment $ENV `
  --image "$ACR.azurecr.io/mock-${S}:$TAG" `
  --target-port 8000 --ingress external `
  --registry-server "$ACR.azurecr.io" --registry-username $USER --registry-password $PASS `
  --min-replicas 0 --max-replicas 3 --cpu 0.5 --memory 1Gi `
  --query properties.configuration.ingress.fqdn -o tsv
```

The command prints the FQDN. The MCP endpoint is `https://<fqdn>/mcp`.

- `--min-replicas 0` scales to zero when idle, so an unused server costs nothing. The first call after an idle spell takes 5 to 15 seconds. Use `--min-replicas 1` to keep a server warm, for example during lab week.
- The finance servers are stateless, so they scale out freely across replicas.
- **iManage, SalesDesk, EngHub and Zava Expense:** use `--max-replicas 1`. It keeps each conversation's write changes in memory, so a second replica would serve a different copy. Scaling to zero or restarting clears those changes, which is fine: each lab conversation starts from the seed. During the lab, set `--min-replicas 1` so changes aren't lost mid-session. For iManage, SalesDesk and EngHub, also set `--env-vars PUBLIC_BASE_URL=https://<app FQDN>` (create the app first, read its FQDN, then `az containerapp update --set-env-vars ...`) so links in tool results open its page viewer.
- Optional settings go in `--env-vars`, for example `--env-vars LOG_LEVEL=DEBUG MOCK_NOW=2026-11-18T09:00:00Z`. See the settings table in [README.md](README.md#run-locally).

## 5. Verify

```powershell
$FQDN = az containerapp show -n "mock-$S" -g $RG --query properties.configuration.ingress.fqdn -o tsv
curl "https://$FQDN/healthz"

$H = @{ Accept = "application/json, text/event-stream" }
$B = '{"jsonrpc":"2.0","id":1,"method":"tools/list"}'
(Invoke-WebRequest "https://$FQDN/mcp" -Method Post -Body $B -ContentType application/json -Headers $H).Content
```

`/healthz` returns `{"status":"ok","server":"<name>","version":"...","tools":<count>}`. `tools/list` returns the server's tools.

## Update a server

Rebuild with a new tag, push it, then point the app at that tag. Use a new tag every time, because reusing a tag does not trigger a new revision.

```powershell
$S   = "lseg"
$TAG = "v2"

az acr login -n $ACR
docker build -f "$S/Dockerfile" -t "$ACR.azurecr.io/mock-${S}:$TAG" -t "$ACR.azurecr.io/mock-${S}:latest" .
docker push "$ACR.azurecr.io/mock-${S}:$TAG"
docker push "$ACR.azurecr.io/mock-${S}:latest"

az containerapp update -n "mock-$S" -g $RG --image "$ACR.azurecr.io/mock-${S}:$TAG"
```

| Change | Command |
|---|---|
| Change a setting only | `az containerapp update -n mock-$S -g $RG --set-env-vars MOCK_NOW=2026-11-18T09:00:00Z` |
| Keep warm for the live lab | `az containerapp update -n mock-$S -g $RG --min-replicas 1` |
| Back to scale to zero | `az containerapp update -n mock-$S -g $RG --min-replicas 0` |
| Roll back | `az containerapp update -n mock-$S -g $RG --image $ACR.azurecr.io/mock-${S}:v1` |

Changes to `_framework/` or `_domains/finance/` affect every finance server. Rebuild and update all of them.

## Add a new server

1. Add the server folder with a `Dockerfile` modelled on `lseg/Dockerfile`. Set `PYTHONPATH` and the `COPY` lines to the right `_domains/<domain>` folder.
2. Run steps 3 to 5 with the new server name.
3. Add a row to [Current deployments](#current-deployments).

## Useful commands

```powershell
# List apps and URLs
az containerapp list -g $RG --query "[].{name:name, fqdn:properties.configuration.ingress.fqdn}" -o table

# Stream logs
az containerapp logs show -n "mock-$S" -g $RG --follow

# Revisions and their health
az containerapp revision list -n "mock-$S" -g $RG -o table

# Restart the active revision
$REV = az containerapp show -n "mock-$S" -g $RG --query properties.latestRevisionName -o tsv
az containerapp revision restart -n "mock-$S" -g $RG --revision $REV

# Images in the registry
az acr repository show-tags -n $ACR --repository "mock-$S" -o table

# Delete one server
az containerapp delete -n "mock-$S" -g $RG --yes

# Delete everything after the event
az group delete -n $RG --yes --no-wait
```

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `az login` signs in but shows an MFA error or no subscriptions | The CLI picked the wrong tenant | `az login --tenant <tenant-id> --use-device-code`, then `az account set` |
| `docker build` fails at `pip install` with `SSLV3_ALERT_HANDSHAKE_FAILURE` | The network blocks or intercepts PyPI | Add `--build-arg PIP_INDEX_URL=<mirror>/simple/`, build on another network, or build in the cloud with `az acr build -r $ACR -f $S/Dockerfile -t mock-${S}:$TAG .` |
| `docker push` returns `unauthorized` | The ACR token has expired (it lasts about 3 hours) | Run `az acr login -n $ACR` again |
| App stuck provisioning, or the revision fails with an image pull error | Wrong registry credentials or image tag | `az containerapp registry set -n mock-$S -g $RG --server $ACR.azurecr.io --username $USER --password $PASS`, and check the tag with `az acr repository show-tags` |
| `/mcp` returns `406 Not Acceptable` | The client did not send both accepted content types | Send `Accept: application/json, text/event-stream` |
| `/mcp` returns `404` or `405` | Wrong path or method | POST to `https://<fqdn>/mcp`. `GET /` and `GET /mcp` are not MCP calls |
| `update` ran but the old code is still served | The image tag was reused | Push a new tag and update to it |
| Server starts then exits, revision unhealthy | Import error or bad setting | `az containerapp logs show -n mock-$S -g $RG --type console`; reproduce with `docker run` locally |
| First call after an idle spell takes 5 to 15 seconds | The app scaled to zero | Expected. Set `--min-replicas 1` when you need it warm |

<#
.SYNOPSIS
    End-to-end Jira Cloud direct ingestion for the LAB654 engineering scenario.

.DESCRIPTION
    1. Regenerates jira_engineering.jsonl from the COEP seed data.
    2. Uploads it to ADLS gcevaldatasets/<Container>/<Prefix>/<DateFolder>/data.jsonl.
    3. Ensures a sparse GCQAutomation clone and its Python venv.
    4. Writes our dataset.json (own connector folder) and environment entry.
    5. Acquires a GCS admin token for the target tenant (or uses -AccessToken).
    6. Optionally deletes the existing connection (-Recreate), dry-runs, then creates it.

    Not automatable here: ECS flight whitelisting for the tenant
    (EnableConnectionScopedConnectorFactory only; RoutingEnvironment is not used) and
    interactive tenant-admin sign-in when no token is supplied.

.EXAMPLE
    pwsh ./ingest_jira.ps1 -DryRun
    pwsh ./ingest_jira.ps1 -Recreate
#>
[CmdletBinding()]
param(
    [string]$TenantId = "b4750151-e261-4dd7-9ca1-e16b1276573e",
    [string]$TenantDomain = "a830edad9050849coepf8OCnm71.onmicrosoft.com",
    [string]$ConnectionId = "ZavaAuroraLab654",
    [string]$EnvironmentId = "IgniteLab654Environment",
    [string]$StorageAccount = "gcevaldatasets",
    [string]$StorageSubscription = "41ebf8a6-8f52-4716-8633-46fdac64d33b",
    [string]$Container = "jiracloud",
    [string]$Prefix = "ignite_lab654",
    [string]$DateFolder = (Get-Date -Format "yyyyMMdd"),
    [string]$GcqPath = "C:\src\GCQAutomation",
    [string]$AccessToken,
    [switch]$SkipUpload,
    [switch]$Recreate,
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"
$JiraProviderId = "4B35C874-F24B-4854-B666-621750551573"
$SchemaId = "JiraCloudGoldenSchema"
$GcsClientId = "d3590ed6-52b3-4102-aeff-aad2292ab01c"
$Here = $PSScriptRoot
$FolderName = "$Prefix/$DateFolder"

function Step($msg) { Write-Host "`n==> $msg" -ForegroundColor Cyan }
function Invoke-Native {
    param([scriptblock]$Cmd, [string]$What)
    & $Cmd
    if ($LASTEXITCODE -ne 0) { throw "$What failed (exit $LASTEXITCODE)" }
}

# 1. Generate data
Step "Generating Jira JSONL for $TenantDomain"
Invoke-Native { python (Join-Path $Here "build_jira_jsonl.py") --domain $TenantDomain } "JSONL generation"
$Jsonl = Join-Path $Here "jira_engineering.jsonl"

# 2. Upload to ADLS
if (-not $SkipUpload) {
    Step "Uploading to $StorageAccount/$Container/$FolderName/data.jsonl"
    Invoke-Native {
        az storage blob upload --subscription $StorageSubscription --account-name $StorageAccount `
            --container-name $Container --name "$FolderName/data.jsonl" --file $Jsonl `
            --auth-mode login --overwrite --only-show-errors -o none
    } "Blob upload (run 'az login' with your Microsoft account if this fails)"
    $names = az storage blob list --subscription $StorageSubscription --account-name $StorageAccount `
        --container-name $Container --prefix "$FolderName/" --auth-mode login --query "[].name" -o tsv
    if ($names -notcontains "$FolderName/data.jsonl") { throw "Upload verification failed" }
    Write-Host "Verified blob exists."
}

# 3. GCQAutomation clone + venv
$DiPath = Join-Path $GcqPath "sources\dev\DirectIngestion"
$EvalsetsPath = Join-Path $GcqPath "sources\dev\Evalsets"
if (-not (Test-Path $DiPath)) {
    Step "Cloning GCQAutomation (sparse) to $GcqPath"
    Invoke-Native { git clone --filter=blob:none --no-checkout "https://O365Exchange@dev.azure.com/O365Exchange/O365%20Core/_git/GCQAutomation" $GcqPath } "git clone"
    Invoke-Native { git -C $GcqPath sparse-checkout set sources/dev/DirectIngestion sources/dev/Evalsets } "sparse-checkout"
    Invoke-Native { git -C $GcqPath checkout master } "git checkout"
}
$VenvPython = Join-Path $env:USERPROFILE ".virtualenvs\direct_ingestion\Scripts\python.exe"
if (-not (Test-Path $VenvPython)) {
    Step "Creating DirectIngestion venv"
    Push-Location $DiPath
    try { Invoke-Native { powershell -ExecutionPolicy Bypass -File .\setup.ps1 } "setup.ps1" } finally { Pop-Location }
}

# 4. Dataset + environment config
Step "Writing dataset and environment config"
$DatasetDir = Join-Path $EvalsetsPath "Connectors\JiraCloudLab654\Dataset"
New-Item -ItemType Directory -Force $DatasetDir | Out-Null
$dataset = [ordered]@{
    domain        = "Developer Tools"
    providerId    = $JiraProviderId
    containerName = $Container
    datasets      = @([ordered]@{
        id                  = $ConnectionId
        description         = "Ignite 2026 LAB654 engineering scenario - Zava Aurora Jira project"
        copilot_description = "Jira Cloud issues for the Zava Aurora project (key AUR): bugs, tasks and stories tracked by the Aurora engineering team, including status, priority, assignees, due dates and comments. Common search terms: Jira, Aurora, AUR, issues, tickets, bugs, sprint."
        folderName          = $FolderName
        schemaId            = $SchemaId
    })
}
$dataset | ConvertTo-Json -Depth 5 | Set-Content (Join-Path $DatasetDir "dataset.json") -Encoding utf8

$EnvFile = Join-Path $EvalsetsPath "Environment\environment.json"
$envPy = @'
import json, sys
path, env_id, conn_id, schema_id = sys.argv[1:5]
with open(path, encoding="utf-8") as f:
    envs = [e for e in json.load(f) if e.get("id") != env_id]
envs.append({"id": env_id, "connections": [{"dataset_id": conn_id, "schema_id": schema_id}]})
with open(path, "w", encoding="utf-8") as f:
    f.write(json.dumps(envs, indent=4, ensure_ascii=False) + "\n")
'@
Invoke-Native { $envPy | python - $EnvFile $EnvironmentId $ConnectionId $SchemaId } "environment.json update"

# 5. Token
if (-not $AccessToken) {
    Step "Acquiring GCS admin token for tenant $TenantId (sign in as the tenant admin)"
    Import-Module MSAL.PS -ErrorAction Stop
    $AccessToken = (Get-MsalToken -ClientId $GcsClientId -TenantId $TenantId -RedirectUri "yammer://wefwef" `
        -Scopes "https://gcs.office.com/.default" -Interactive).AccessToken
}

# Process env vars take precedence over .env (load_dotenv does not override).
$env:GCS_ACCESS_TOKEN = $AccessToken
$env:TENANT_DOMAIN_NAME = $TenantDomain
$env:ENV_ID = $EnvironmentId
$env:STORAGE_URL = $StorageAccount
$env:DATASET_IDS = $ConnectionId
$env:EVALSETS_PATH = $EvalsetsPath
$env:CONNECTION_IDS = $ConnectionId
$env:CONNECTION_ID = $ConnectionId

Push-Location $DiPath
try {
    # 6. Dry run, optional delete, create
    Step "Dry run"
    Invoke-Native { & $VenvPython connection_main.py --dry-run } "Dry run"
    if ($DryRun) { Write-Host "`nDry run only - stopping."; return }

    if ($Recreate) {
        Step "Deleting existing connection $ConnectionId"
        & $VenvPython connection_delete.py
    }

    Step "Creating connection $ConnectionId"
    Invoke-Native { & $VenvPython connection_main.py } "Connection creation (see $DiPath\connection_main.log)"

    Step "Connection details"
    & $VenvPython connection_details.py
}
finally {
    Pop-Location
    Remove-Item Env:GCS_ACCESS_TOKEN -ErrorAction SilentlyContinue
}

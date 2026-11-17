<#
Resets the lab user's environment through Microsoft Graph, so it works without the OneDrive sync client.
  1. Removes every folder under Documents\Cowork\Tasks.
  2. Deletes the Trey Research folder, then recreates it with a clean Trey Research Vendor Agreement v4.2.docx, downloaded from
     -CleanCopyUrl or, if that fails, taken from next to this script.
Only touches the signed-in user's own account (/me). With -UserName, it stops if a different account signs in.
Needs these delegated permissions approved for Microsoft Graph Command Line Tools:
User.Read, Files.ReadWrite.

Sign-in: opens the default browser (Edge) to sign in. If Edge is already signed in as the lab user,
it completes without a password or MFA prompt. Uses the Microsoft Graph Command Line Tools public client,
so no app registration is needed.
#>
param(
    # The seat's lab account. When set, the script stops if a different account signs in.
    [string]$UserName = "",
    # Public raw URL of the clean agreement. If the download fails, the copy next to this script is used.
    [string]$CleanCopyUrl = "https://gist.githubusercontent.com/tezansahu/cb1d8cd77697c089fc7765abb35af2e1/raw/trey-research-vendor-agreement-v4.2.docx.b64"
)

$ErrorActionPreference = "Stop"
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

$ClientId   = "14d82eec-204b-4c2f-b7e8-296a70dab67e"   # Microsoft Graph Command Line Tools
$Authority  = "https://login.microsoftonline.com/organizations/oauth2/v2.0"
$Scope      = "https://graph.microsoft.com/User.Read https://graph.microsoft.com/Files.ReadWrite"
$Graph      = "https://graph.microsoft.com/v1.0"
$TasksPath  = "Documents/Cowork/Tasks"
$Agreement  = "Trey Research Vendor Agreement v4.2.docx"
$TargetFolder = "Trey Research"
$TargetPath = "$TargetFolder/$Agreement"
$LocalCopy  = Join-Path $PSScriptRoot $Agreement

function ConvertTo-Base64Url([byte[]]$Bytes) {
    [Convert]::ToBase64String($Bytes).TrimEnd("=").Replace("+", "-").Replace("/", "_")
}

function Get-DrivePathUrl([string]$Path) {
    $encoded = ($Path -split "/" | ForEach-Object { [Uri]::EscapeDataString($_) }) -join "/"
    "$Graph/me/drive/root:/$encoded"
}

function Get-StatusCode($ErrorRecord) {
    $response = $ErrorRecord.Exception.Response
    if ($response) { return [int]$response.StatusCode }
    return 0
}

function Get-ErrorText($ErrorRecord) {
    $text = $ErrorRecord.Exception.Message
    if ($ErrorRecord.ErrorDetails -and $ErrorRecord.ErrorDetails.Message) { return "$text $($ErrorRecord.ErrorDetails.Message)" }
    try {
        $stream = $ErrorRecord.Exception.Response.GetResponseStream()
        $stream.Position = 0
        $body = (New-Object IO.StreamReader($stream)).ReadToEnd()
        if ($body) { $text += " $body" }
    }
    catch { }
    return $text
}

function Get-AccessToken {
    $tcp = New-Object Net.Sockets.TcpListener([Net.IPAddress]::Loopback, 0)
    $tcp.Start(); $port = $tcp.LocalEndpoint.Port; $tcp.Stop()
    $redirect = "http://localhost:$port/"

    $rng = New-Object Security.Cryptography.RNGCryptoServiceProvider
    $bytes = New-Object byte[] 32; $rng.GetBytes($bytes)
    $verifier = ConvertTo-Base64Url $bytes
    $challenge = ConvertTo-Base64Url ([Security.Cryptography.SHA256]::Create().ComputeHash([Text.Encoding]::ASCII.GetBytes($verifier)))
    $rng.GetBytes($bytes); $state = ConvertTo-Base64Url $bytes

    $query = @{
        client_id             = $ClientId
        response_type         = "code"
        redirect_uri          = $redirect
        scope                 = $Scope
        code_challenge        = $challenge
        code_challenge_method = "S256"
        state                 = $state
    }
    if ($UserName) { $query.login_hint = $UserName }
    $qs = ($query.GetEnumerator() | ForEach-Object { "$($_.Key)=$([Uri]::EscapeDataString($_.Value))" }) -join "&"

    $listener = New-Object Net.HttpListener
    $listener.Prefixes.Add($redirect)
    $listener.Start()
    try {
        Write-Host "Signing in through the browser. If the browser asks, pick the lab account."
        Start-Process "$Authority/authorize?$qs"

        $pending = $listener.GetContextAsync()
        if (-not $pending.Wait([TimeSpan]::FromMinutes(3))) { throw "Sign-in timed out." }
        $context = $pending.Result
        $params = [Web.HttpUtility]::ParseQueryString($context.Request.Url.Query)

        $html = [Text.Encoding]::UTF8.GetBytes("<html><body style='font-family:Segoe UI'><h2>Lab clean-up signed in.</h2><p>You can close this tab.</p></body></html>")
        $context.Response.ContentType = "text/html"
        $context.Response.OutputStream.Write($html, 0, $html.Length)
        $context.Response.Close()
    }
    finally {
        $listener.Stop()
    }

    if ($params["error"]) { throw "Sign-in failed: $($params["error_description"])" }
    if ($params["state"] -ne $state) { throw "Sign-in failed: the response didn't match the request." }

    $token = Invoke-RestMethod -Method Post -Uri "$Authority/token" -ContentType "application/x-www-form-urlencoded" -Body @{
        client_id     = $ClientId
        grant_type    = "authorization_code"
        code          = $params["code"]
        redirect_uri  = $redirect
        code_verifier = $verifier
        scope         = $Scope
    }
    return $token.access_token
}

Add-Type -AssemblyName System.Web
$errors = 0

$LogFile = Join-Path $PSScriptRoot "reset-lab.log"
try { Start-Transcript -Path $LogFile -Force | Out-Null }
catch { $LogFile = Join-Path $env:TEMP "reset-lab.log"; Start-Transcript -Path $LogFile -Force | Out-Null }

try {
    $CleanCopy = $null
    if ($CleanCopyUrl) {
        $download = Join-Path $env:TEMP $Agreement
        try {
            Invoke-WebRequest -Uri $CleanCopyUrl -OutFile $download -UseBasicParsing
            $bytes = [IO.File]::ReadAllBytes($download)
            if (-not ($bytes.Length -gt 2 -and $bytes[0] -eq 0x50 -and $bytes[1] -eq 0x4B)) {
                # Not a .docx (zip) file, so treat it as base64 text, for example from a GitHub gist.
                [IO.File]::WriteAllBytes($download, [Convert]::FromBase64String([Text.Encoding]::ASCII.GetString($bytes).Trim()))
            }
            $CleanCopy = $download
            Write-Host "Downloaded the clean agreement."
        }
        catch {
            Write-Host "Couldn't download the clean agreement ($(Get-ErrorText $_)). Using the copy next to this script."
        }
    }
    if (-not $CleanCopy) {
        if (-not (Test-Path $LocalCopy)) { throw "The clean agreement couldn't be downloaded, and there's no copy next to this script." }
        $CleanCopy = $LocalCopy
    }

    $headers = @{ Authorization = "Bearer $(Get-AccessToken)" }

    Write-Host "Signed in. Checking the account..."
    $me = Invoke-RestMethod -Headers $headers -Uri "$Graph/me?`$select=userPrincipalName"
    if ($UserName -and $me.userPrincipalName -ne $UserName) {
        throw "Signed in as $($me.userPrincipalName), not this seat's account ($UserName). Nothing was changed. Sign in to Edge as $UserName and run this again."
    }
    Write-Host "Cleaning up OneDrive for $($me.userPrincipalName)."

    Write-Host "Removing Cowork task folders..."
    $url = "$(Get-DrivePathUrl $TasksPath):/children?`$select=id,name,folder"
    Write-Host "  Looking in $url"
    $folders = @()
    try {
        while ($url) {
            $page = Invoke-RestMethod -Headers $headers -Uri $url
            $folders += $page.value | Where-Object { $_.folder }
            $url = $page.'@odata.nextLink'
        }
    }
    catch {
        if ((Get-StatusCode $_) -eq 404) { Write-Host "  No Cowork Tasks folder found. Nothing to remove." }
        else { throw }
    }
    Write-Host "  Found $($folders.Count) task folder(s)."
    foreach ($folder in $folders) {
        try {
            Invoke-RestMethod -Method Delete -Headers $headers -Uri "$Graph/me/drive/items/$($folder.id)" | Out-Null
            Write-Host "  Removed `"$($folder.name)`""
        }
        catch {
            Write-Host "  Couldn't remove `"$($folder.name)`": $(Get-ErrorText $_)"
            $errors++
        }
    }

    Write-Host "Restoring the clean Trey Research agreement..."

    # Remove folders set aside by earlier runs, once Word has let go of them.
    $root = Invoke-RestMethod -Headers $headers -Uri "$Graph/me/drive/root/children?`$select=id,name,folder&`$top=999"
    foreach ($old in ($root.value | Where-Object { $_.folder -and $_.name -like "$TargetFolder (old *" })) {
        try {
            Invoke-RestMethod -Method Delete -Headers $headers -Uri "$Graph/me/drive/items/$($old.id)" | Out-Null
            Write-Host "  Removed `"$($old.name)`""
        }
        catch { Write-Host "  `"$($old.name)`" is still locked. It will be removed next time." }
    }

    $folderUrl = Get-DrivePathUrl $TargetFolder
    $deadline = (Get-Date).AddMinutes(1)
    while ($true) {
        try {
            Invoke-RestMethod -Method Delete -Headers $headers -Uri $folderUrl | Out-Null
            Write-Host "  Removed the `"$TargetFolder`" folder"
            break
        }
        catch {
            $status = Get-StatusCode $_
            if ($status -eq 404) { Write-Host "  No `"$TargetFolder`" folder found. Creating it."; break }
            if ($status -ne 423) { throw }
            Write-Host "  Locked: $(Get-ErrorText $_)"
            if ((Get-Date) -lt $deadline) {
                Write-Host "  The folder is locked because the agreement is open in Word. Make sure it's closed everywhere. Trying again in 15 seconds..."
                Start-Sleep -Seconds 15
                continue
            }
            $oldName = "$TargetFolder (old $(Get-Date -Format 'yyyyMMdd-HHmmss'))"
            Write-Host "  Still locked. Moving it aside as `"$oldName`"..."
            $rename = @{ name = $oldName } | ConvertTo-Json
            Invoke-RestMethod -Method Patch -Headers $headers -Uri $folderUrl -ContentType "application/json" -Body $rename | Out-Null
            Write-Host "  Moved the locked folder aside. It will be removed on a later run."
            break
        }
    }

    # Uploading to the path recreates the folder.
    Invoke-RestMethod -Method Put -Headers $headers -Uri "$(Get-DrivePathUrl $TargetPath):/content" `
        -ContentType "application/vnd.openxmlformats-officedocument.wordprocessingml.document" `
        -InFile $CleanCopy | Out-Null
    Write-Host "  Restored `"$TargetPath`""
}
catch {
    Write-Host (Get-ErrorText $_)
    $errors++
}

Write-Host ""
Write-Host "Log: $LogFile"
if ($errors -gt 0) {
    Write-Host "The clean-up didn't finish. Ask a proctor for help."
    Stop-Transcript | Out-Null
    Read-Host "Press Enter to close this window"
    exit 1
}
Write-Host "Your lab environment is clean."
Stop-Transcript | Out-Null
Start-Sleep -Seconds 10
exit 0

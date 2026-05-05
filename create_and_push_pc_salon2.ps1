# Creates GitHub repo WhiteHat5/pc_salon2 if missing, then pushes branch main.
#
# Do NOT paste your token into chat. In PowerShell on your PC only:
#   $env:GITHUB_TOKEN = "ghp_......"   # classic PAT with "repo" scope
#   Set-Location "c:\xampp\htdocs\pc_salon"
#   .\create_and_push_pc_salon2.ps1

$ErrorActionPreference = "Stop"

$Owner = "WhiteHat5"
$Repo  = "pc_salon2"
$Root  = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root

if (-not $env:GITHUB_TOKEN -or $env:GITHUB_TOKEN.Length -lt 20) {
    Write-Host ""
    Write-Host "Set GITHUB_TOKEN in this console (see script header comments)." -ForegroundColor Yellow
    exit 1
}

$Token = $env:GITHUB_TOKEN.Trim()
$headers = @{
    Authorization          = "Bearer $Token"
    Accept                 = "application/vnd.github+json"
    "X-GitHub-Api-Version" = "2022-11-28"
}

$exists = $false
try {
    $null = Invoke-RestMethod -Uri "https://api.github.com/repos/$Owner/$Repo" -Headers $headers -Method Get
    $exists = $true
    Write-Host "Repository $Owner/$Repo already exists on GitHub."
}
catch {
    $resp = $_.Exception.Response
    if ($resp -and [int]$resp.StatusCode -eq 404) {
        $exists = $false
    }
    else {
        throw
    }
}

if (-not $exists) {
    $bodyObj = @{
        name        = $Repo
        description = "PC Salon storefront, PHP/FastAPI, PostgreSQL"
        private     = $false
        auto_init   = $false
    }
    $body = $bodyObj | ConvertTo-Json
    $null = Invoke-RestMethod -Uri "https://api.github.com/user/repos" -Method Post -Headers $headers -Body $body -ContentType "application/json; charset=utf-8"
    Write-Host "Created: https://github.com/$Owner/$Repo"
}

$remotes = @(git remote)
if ($remotes -contains "pc_salon2") {
    git remote remove pc_salon2
}
git remote add pc_salon2 "https://github.com/$Owner/$Repo.git"

$encToken = [uri]::EscapeDataString($Token)
$pushUrl  = "https://${Owner}:${encToken}@github.com/${Owner}/${Repo}.git"
git push $pushUrl main

git remote set-url pc_salon2 "https://github.com/$Owner/$Repo.git"

git fetch pc_salon2
git branch --set-upstream-to=pc_salon2/main main

Write-Host ""
Write-Host "Done: main pushed to https://github.com/$Owner/$Repo" -ForegroundColor Green
Write-Host "Remote name: pc_salon2 (origin still points to old pc_salon repo)." -ForegroundColor Green

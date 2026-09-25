# Opens the dashboard on demand (Windows). Mirrors app/open_dashboard.sh
# (the macOS/Linux version) - see that file for the full rationale.
# Pulls and resyncs the workbook once, starts the local server for just
# this session, opens it in its own isolated Chrome window, and shuts
# the server back down the moment that window is closed.
#
# UNTESTED: written without a Windows machine available to verify
# against. If something doesn't work, the likely trouble spots are the
# Chrome path list below, the port check, or python vs. py as the
# interpreter name - fix those first before assuming the overall
# approach is wrong.

$ErrorActionPreference = "Stop"
Set-Location (Join-Path $PSScriptRoot "..")

git pull --rebase --quiet
if ($LASTEXITCODE -ne 0) {
    Write-Warning "git pull failed, dashboard may show stale data"
}

# Prefer `python`, fall back to the `py` launcher (the more common
# default on a stock Windows Python install).
$pythonCmd = if (Get-Command python -ErrorAction SilentlyContinue) { "python" }
             elseif (Get-Command py -ErrorAction SilentlyContinue) { "py" }
             else { $null }
if (-not $pythonCmd) {
    Write-Error "Could not find python or py on PATH. Install Python and make sure it's on PATH."
    exit 1
}

& $pythonCmd app/recompute.py
if ($LASTEXITCODE -ne 0) {
    Write-Warning "app/recompute.py exited with an error - dashboard numbers may be stale. Continuing anyway."
}

$port = 8420
$startedServer = $false
$serverProcess = $null

$portInUse = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
if (-not $portInUse) {
    $serverProcess = Start-Process -FilePath $pythonCmd -ArgumentList "app/server.py" -PassThru -WindowStyle Hidden
    $startedServer = $true
    Start-Sleep -Milliseconds 500
}

$profileDir = Join-Path $env:TEMP ("dashboard-chrome-" + [System.Guid]::NewGuid().ToString())
New-Item -ItemType Directory -Path $profileDir | Out-Null

# Common Chrome install locations. Edit this list if yours is somewhere
# else - there's no single canonical path on Windows the way `open -a`
# resolves an app by name on macOS.
$chromeCandidates = @(
    (Join-Path $env:ProgramFiles "Google\Chrome\Application\chrome.exe"),
    (Join-Path ${env:ProgramFiles(x86)} "Google\Chrome\Application\chrome.exe"),
    (Join-Path $env:LocalAppData "Google\Chrome\Application\chrome.exe")
)
$chrome = $chromeCandidates | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $chrome) {
    Remove-Item -Recurse -Force $profileDir -ErrorAction SilentlyContinue
    if ($startedServer -and $serverProcess) {
        Stop-Process -Id $serverProcess.Id -Force -ErrorAction SilentlyContinue
    }
    Write-Error "Could not find chrome.exe in the usual install locations. Edit `$chromeCandidates in app/open_dashboard.ps1 if Chrome is installed somewhere else."
    exit 1
}

$chromeProcess = Start-Process -FilePath $chrome -ArgumentList "--app=http://localhost:$port/", "--user-data-dir=$profileDir" -PassThru

# Wait for this specific (isolated-profile) Chrome window to close before
# tearing anything down - other Chrome windows/profiles are untouched.
$chromeProcess.WaitForExit()

Remove-Item -Recurse -Force $profileDir -ErrorAction SilentlyContinue

if ($startedServer -and $serverProcess) {
    Stop-Process -Id $serverProcess.Id -Force -ErrorAction SilentlyContinue
}

# No separate "close the launcher window" step needed here the way the
# macOS version has to self-close Terminal: a console window opened by
# double-clicking the paired .bat file closes on its own once this
# script (and the .bat) finish, with no leftover process.

@echo off
:: Double-click this to open the dashboard. See app/open_dashboard.ps1
:: for what it actually does (syncs the workbook, starts the server for
:: just this session, opens it in its own Chrome window, shuts
:: everything down again when that window is closed).
::
:: UNTESTED: written without a Windows machine available to verify
:: against - see the warning at the top of open_dashboard.ps1.
::
:: Runs PowerShell with a one-time execution policy bypass scoped to
:: just this process, so it works without changing your system's
:: PowerShell execution policy.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0app\open_dashboard.ps1"

# Register Windows Task Scheduler job — daily crawl at 2:00 AM
# Run as Administrator:  .\scripts\schedule_nightly_crawl.ps1

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$ScriptPath = Join-Path $ProjectRoot "scripts\nightly_crawl.ps1"
$TaskName = "MuunganoGPT-NightlyCrawl"

$Action = New-ScheduledTaskAction -Execute "powershell.exe" `
    -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$ScriptPath`""

$Trigger = New-ScheduledTaskTrigger -Daily -At "2:00AM"

$Settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -ExecutionTimeLimit (New-TimeSpan -Hours 2)

Register-ScheduledTask `
    -TaskName $TaskName `
    -Action $Action `
    -Trigger $Trigger `
    -Settings $Settings `
    -Description "Crawl official Tanzania Muungano sources for MuunganoGPT knowledge base" `
    -Force

Write-Host "Scheduled task '$TaskName' — daily at 2:00 AM"
Write-Host "Logs: $ProjectRoot\data\logs\"
Write-Host "Test now:  .\scripts\nightly_crawl.ps1"

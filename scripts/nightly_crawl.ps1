# Nightly crawl — ingest official web sources into Chroma (offline, no user wait).
# Run manually:  .\scripts\nightly_crawl.ps1
# Schedule:     .\scripts\schedule_nightly_crawl.ps1  (requires Administrator)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $ProjectRoot

$LogDir = Join-Path $ProjectRoot "data\logs"
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
$LogFile = Join-Path $LogDir ("crawl_{0:yyyyMMdd_HHmmss}.log" -f (Get-Date))

function Write-Log($msg) {
    $line = "[{0}] {1}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $msg
    Add-Content -Path $LogFile -Value $line
    Write-Host $line
}

Write-Log "MuunganoGPT nightly crawl started"
Write-Log "Project: $ProjectRoot"

try {
    Write-Log "Ingesting youth Q&A …"
    $youth = python -c "from backend.rag.ingest_youth import ingest_youth_qa; import json; print(json.dumps(ingest_youth_qa()))"
    Write-Log "Youth: $youth"

    Write-Log "Crawling official sources …"
    $web = python -c "from backend.rag.ingest_web import ingest_web; import json; print(json.dumps(ingest_web(crawl_all=True)))"
    Write-Log "Web: $web"

    Write-Log "Nightly crawl completed successfully"
    exit 0
}
catch {
    Write-Log "ERROR: $_"
    exit 1
}

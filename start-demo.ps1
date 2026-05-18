$ErrorActionPreference = 'Stop'

$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $repoRoot

Write-Host ''
Write-Host '=== Bot Seguridad Social - Iniciar Demo ===' -ForegroundColor Cyan
Write-Host ''

docker compose up --build -d
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Start-Process 'http://localhost:5173/'
Write-Host 'Frontend: http://localhost:5173/'

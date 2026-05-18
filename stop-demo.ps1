$ErrorActionPreference = 'Stop'

$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $repoRoot

Write-Host ''
Write-Host '=== Bot Seguridad Social - Detener Demo ===' -ForegroundColor Cyan
Write-Host ''

docker compose down
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host 'Servicios detenidos.' -ForegroundColor Green

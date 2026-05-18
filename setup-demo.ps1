$ErrorActionPreference = 'Stop'

$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $repoRoot

function Test-Command {
    param([string]$Name)
    return [bool](Get-Command $Name -ErrorAction SilentlyContinue)
}

function Require-Command {
    param([string]$Name, [string]$Message)
    if (-not (Test-Command $Name)) {
        Write-Host "`nERROR: $Message" -ForegroundColor Red
        exit 1
    }
}

function Wait-For-Docker {
    for ($i = 0; $i -lt 20; $i++) {
        docker info *> $null
        if ($LASTEXITCODE -eq 0) {
            return
        }
        Start-Sleep -Seconds 3
    }

    Write-Host "`nERROR: Docker Desktop no esta disponible. Abrilo y espera a que termine de iniciar." -ForegroundColor Red
    exit 1
}

function Ensure-EnvFile {
    $envPath = Join-Path $repoRoot '.env'
    $examplePath = Join-Path $repoRoot '.env.example'

    if (-not (Test-Path $envPath)) {
        Copy-Item $examplePath $envPath
    }

    return $envPath
}

function Set-Or-UpdateEnvValue {
    param([string]$Path, [string]$Key, [string]$Value)

    $content = @()
    if (Test-Path $Path) {
        $content = Get-Content $Path
    }

    $escapedKey = [regex]::Escape($Key)
    $updated = $false
    $newContent = foreach ($line in $content) {
        if ($line -match "^${escapedKey}=") {
            $updated = $true
            "${Key}=${Value}"
        }
        else {
            $line
        }
    }

    if (-not $updated) {
        if ($newContent.Count -gt 0 -and $newContent[-1] -ne '') {
            $newContent += ''
        }
        $newContent += "${Key}=${Value}"
    }

    Set-Content -Path $Path -Value $newContent -Encoding UTF8
}

function Get-EnvValue {
    param([string]$Path, [string]$Key)

    if (-not (Test-Path $Path)) {
        return ''
    }

    $escapedKey = [regex]::Escape($Key)
    $line = Get-Content $Path | Where-Object { $_ -match "^${escapedKey}=" } | Select-Object -First 1
    if ($line) {
        return ($line -replace "^${escapedKey}=", '')
    }
    return ''
}

Write-Host ''
Write-Host '=== Bot Seguridad Social - Setup Demo ===' -ForegroundColor Cyan
Write-Host ''

Require-Command -Name 'wsl' -Message 'WSL no esta instalado. En Windows abri PowerShell como administrador y corre: wsl --install. Luego reinicia la PC.'
Require-Command -Name 'docker' -Message 'Docker Desktop no esta instalado.'

$wslStatus = & wsl --status 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "`nERROR: WSL no parece estar configurado correctamente. Ejecuta 'wsl --install' como administrador y reinicia Windows." -ForegroundColor Red
    exit 1
}

Wait-For-Docker

$envPath = Ensure-EnvFile

$geminiApiKey = Get-EnvValue -Path $envPath -Key 'GEMINI_API_KEY'
if ([string]::IsNullOrWhiteSpace($geminiApiKey)) {
    $geminiApiKey = Read-Host 'Ingresa tu GEMINI_API_KEY'
    if ([string]::IsNullOrWhiteSpace($geminiApiKey)) {
        Write-Host "`nERROR: GEMINI_API_KEY es obligatoria." -ForegroundColor Red
        exit 1
    }
    Set-Or-UpdateEnvValue -Path $envPath -Key 'GEMINI_API_KEY' -Value $geminiApiKey
}

$githubToken = Get-EnvValue -Path $envPath -Key 'GITHUB_TOKEN'
if ([string]::IsNullOrWhiteSpace($githubToken)) {
    $githubToken = Read-Host 'Ingresa tu GITHUB_TOKEN (necesario si anses-corpus es privado)'
    if (-not [string]::IsNullOrWhiteSpace($githubToken)) {
        Set-Or-UpdateEnvValue -Path $envPath -Key 'GITHUB_TOKEN' -Value $githubToken
    }
}

Write-Host ''
Write-Host 'Descargando corpus v1...' -ForegroundColor Yellow
docker compose run --rm corpus-tools uv run python /app/rag_app/scripts/fetch_corpus.py --version v1 --repo wachinalpha/anses-corpus
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host ''
Write-Host 'Reseteando indice...' -ForegroundColor Yellow
docker compose run --rm corpus-tools uv run python /app/rag_app/scripts/reset_db.py --force
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host ''
Write-Host 'Indexando corpus...' -ForegroundColor Yellow
docker compose run --rm corpus-tools uv run python /app/rag_app/scripts/index_corpus.py --version v1
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host ''
Write-Host 'Levantando backend y frontend...' -ForegroundColor Yellow
docker compose up --build -d
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host ''
Write-Host 'Listo. Abriendo la app...' -ForegroundColor Green
Start-Process 'http://localhost:5173/'
Write-Host 'Frontend: http://localhost:5173/'
Write-Host 'Backend health: http://localhost:8000/health'

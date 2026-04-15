# CacaoTrace - setup.ps1 (Windows PowerShell 5+ / pwsh 7+)
# Instala uv, pnpm, verifica Docker Desktop, deps backend+frontend+mcp+simulator, crea .env.
# Uso: powershell -ExecutionPolicy Bypass -File scripts\setup.ps1 [-SkipDocker]

[CmdletBinding()]
param(
    [switch]$SkipDocker
)

$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root

function Say($msg)  { Write-Host "==> " -ForegroundColor Cyan -NoNewline; Write-Host $msg -ForegroundColor White }
function OK($msg)   { Write-Host "OK " -ForegroundColor Green -NoNewline; Write-Host $msg }
function Warn($msg) { Write-Host "WARN " -ForegroundColor Yellow -NoNewline; Write-Host $msg }
function Die($msg)  { Write-Host "ERROR " -ForegroundColor Red -NoNewline; Write-Host $msg; exit 1 }
function Has($cmd)  { return [bool](Get-Command $cmd -ErrorAction SilentlyContinue) }

Say "CacaoTrace - setup Windows"
Write-Host "Root: $Root`n"

# ---------- 1. sistema ----------
Say "1/7 - chequeo de sistema"
if (-not (Has git))   { Die "git requerido (winget install Git.Git)" }
if (-not (Has curl))  { Warn "curl no detectado - powershell usa Invoke-WebRequest igual" }
$psVer = $PSVersionTable.PSVersion
OK "PowerShell v$psVer - git $(git --version)"

# ---------- 2. uv ----------
Say "2/7 - instalando uv (Python package manager)"
if (Has uv) {
    OK "uv ya instalado: $(uv --version)"
} else {
    try {
        powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    } catch {
        Die "Fallo instalando uv. Manual: https://docs.astral.sh/uv/getting-started/installation/"
    }
    # Refrescar PATH en la sesion actual
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","User") + ";" + [System.Environment]::GetEnvironmentVariable("Path","Machine")
    if (-not (Has uv)) { Die "uv no esta en PATH. Abre nueva terminal y reintenta." }
    OK "uv instalado: $(uv --version)"
}

# ---------- 3. pnpm + node ----------
Say "3/7 - instalando pnpm"
if (Has pnpm) {
    OK "pnpm ya instalado: v$(pnpm --version)"
} else {
    try {
        Invoke-WebRequest https://get.pnpm.io/install.ps1 -UseBasicParsing | Invoke-Expression
    } catch {
        Die "Fallo instalando pnpm. Manual: iwr https://get.pnpm.io/install.ps1 -useb | iex"
    }
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","User") + ";" + [System.Environment]::GetEnvironmentVariable("Path","Machine")
    if (-not (Has pnpm)) { Die "pnpm no esta en PATH. Abre nueva terminal y reintenta." }
    OK "pnpm instalado: v$(pnpm --version)"
}

# Node 20+ via pnpm si no hay node
if (Has node) {
    $nodeMajor = [int](node -v).Substring(1).Split('.')[0]
    if ($nodeMajor -lt 20) {
        Warn "Node $(node -v) - se recomienda v20+. Usando pnpm env..."
        pnpm env use --global lts
    }
} else {
    Say "   Node no detectado, instalando via pnpm env..."
    pnpm env use --global lts
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","User") + ";" + [System.Environment]::GetEnvironmentVariable("Path","Machine")
}
OK "node: $(node -v 2>$null)"

# ---------- 4. docker ----------
if (-not $SkipDocker) {
    Say "4/7 - verificando Docker Desktop"
    if (Has docker) {
        try {
            docker info *>$null
            OK "Docker OK: $(docker --version)"
            docker compose version *>$null
            if ($LASTEXITCODE -eq 0) { OK "docker compose OK" } else { Die "Docker Compose v2 no detectado" }
        } catch {
            Warn "Docker instalado pero no corriendo. Abre Docker Desktop y espera que diga 'Engine running'."
            Die "Reintenta setup cuando Docker Desktop este activo (o usa -SkipDocker)."
        }
    } else {
        Warn "Docker Desktop no detectado."
        Write-Host "   Descargar: https://www.docker.com/products/docker-desktop/"
        Write-Host "   O: winget install Docker.DockerDesktop"
        Die "Instala Docker Desktop y reintenta (o usa -SkipDocker)"
    }
} else {
    Warn "4/7 - Docker skipped (-SkipDocker)"
}

# ---------- 5. .env ----------
Say "5/7 - configurando .env"
if (Test-Path .env) {
    OK ".env ya existe (no se sobreescribe)"
} else {
    Copy-Item .env.example .env
    # Generar Django secret
    $bytes = New-Object byte[] 48
    [System.Security.Cryptography.RandomNumberGenerator]::Create().GetBytes($bytes)
    $secret = [Convert]::ToBase64String($bytes).TrimEnd('=').Replace('/','_').Replace('+','-')
    (Get-Content .env) -replace 'your-super-secret-production-key-min-50-chars', $secret | Set-Content .env -Encoding UTF8
    OK ".env creado desde .env.example (revisalo antes de deploy)"
}

# ---------- 6. deps ----------
Say "6/7 - instalando deps backend + frontend + mcp + simulator"

if (Test-Path backend) {
    Push-Location backend
    uv sync --quiet
    if ($LASTEXITCODE -eq 0) { OK "backend - uv sync OK" } else { Warn "backend - uv sync con advertencias" }
    Pop-Location
}

if (Test-Path mcp-server) {
    Push-Location mcp-server
    uv sync --quiet
    if ($LASTEXITCODE -eq 0) { OK "mcp-server - uv sync OK" } else { Warn "mcp-server - uv sync con advertencias" }
    Pop-Location
}

if (Test-Path simulator) {
    Push-Location simulator
    uv sync --quiet
    if ($LASTEXITCODE -eq 0) { OK "simulator - uv sync OK" } else { Warn "simulator - uv sync con advertencias" }
    Pop-Location
}

if (Test-Path frontend) {
    Push-Location frontend
    pnpm install --silent
    if ($LASTEXITCODE -eq 0) { OK "frontend - pnpm install OK" } else { Warn "frontend - pnpm install con advertencias" }
    Pop-Location
}

# ---------- 7. docker config ----------
if (-not $SkipDocker) {
    Say "7/7 - validando docker compose"
    docker compose config --quiet
    if ($LASTEXITCODE -eq 0) { OK "docker-compose.yml valido" } else { Die "docker-compose.yml invalido" }
    Write-Host ""
    Write-Host "Para levantar el stack completo:"
    Write-Host "  docker compose up -d" -ForegroundColor White
    Write-Host "Para ver logs: docker compose logs -f"
}

# ---------- resumen ----------
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "       CacaoTrace listo" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Siguientes pasos:"
Write-Host "  1. Lee AGENTS.md y docs\workflow\<tu-rol>.md"
Write-Host "  2. Edita .env con credenciales de Supabase/LLM"
Write-Host "  3. git checkout feat/<tu-rama>  (ya estan creadas en remoto)"
Write-Host "  4. docker compose up -d"
Write-Host "  5. Frontend dev: cd frontend; pnpm dev"
Write-Host "  6. Backend dev: cd backend; uv run python manage.py runserver"
Write-Host ""

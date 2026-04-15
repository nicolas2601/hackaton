#!/usr/bin/env bash
# CacaoTrace — setup.sh (Linux / macOS)
# Instala uv, pnpm, Docker check, deps backend+frontend+mcp+simulator, crea .env.
# Uso: bash scripts/setup.sh [--skip-docker]

set -Eeuo pipefail

cd "$(dirname "$0")/.."
ROOT="$(pwd)"

# ------------- helpers -------------
GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; CYAN='\033[0;36m'; BOLD='\033[1m'; NC='\033[0m'
say()  { printf "${CYAN}==>${NC} ${BOLD}%s${NC}\n" "$*"; }
ok()   { printf "${GREEN}✅${NC} %s\n" "$*"; }
warn() { printf "${YELLOW}⚠️${NC}  %s\n" "$*"; }
die()  { printf "${RED}❌ %s${NC}\n" "$*" >&2; exit 1; }
has()  { command -v "$1" >/dev/null 2>&1; }
ver()  { "$1" --version 2>/dev/null | head -1 || echo "?"; }

SKIP_DOCKER=0
[[ "${1:-}" == "--skip-docker" ]] && SKIP_DOCKER=1

trap 'die "Setup abortado en línea $LINENO"' ERR

say "CacaoTrace · setup Linux/macOS"
echo "Root: $ROOT"
echo

# ------------- 1. sistema -------------
say "1/7 · chequeo de dependencias de sistema"

OS="$(uname -s)"
has curl   || die "curl requerido (sudo apt install curl)"
has git    || die "git requerido"
has python3 || warn "python3 no encontrado — uv lo provee igual"
has node   || warn "node no encontrado — pnpm lo maneja"

ok "OS: $OS · curl $(ver curl | awk '{print $2}') · git $(ver git | awk '{print $3}')"

# ------------- 2. uv -------------
say "2/7 · instalando uv (Python package manager)"
if has uv; then
  ok "uv ya instalado: $(ver uv)"
else
  curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="$HOME/.local/bin:$PATH"
  # persistir en shell
  if [[ -n "${ZSH_VERSION:-}" ]]; then
    RC="$HOME/.zshrc"
  else
    RC="$HOME/.bashrc"
  fi
  if ! grep -q 'astral/uv\|/.local/bin' "$RC" 2>/dev/null; then
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$RC"
  fi
  has uv || die "uv no está en PATH tras instalar. Reabre shell y reintenta."
  ok "uv instalado: $(ver uv)"
fi

# ------------- 3. pnpm + node -------------
say "3/7 · instalando pnpm (Node package manager)"
if has pnpm; then
  ok "pnpm ya instalado: v$(ver pnpm)"
else
  # Preferir corepack si hay node
  if has node && has corepack; then
    corepack enable >/dev/null 2>&1 || true
    corepack prepare pnpm@latest --activate || true
  fi
  if ! has pnpm; then
    curl -fsSL https://get.pnpm.io/install.sh | sh -s -
    export PNPM_HOME="$HOME/.local/share/pnpm"
    export PATH="$PNPM_HOME:$PATH"
    # persistir
    if [[ -n "${ZSH_VERSION:-}" ]]; then RC="$HOME/.zshrc"; else RC="$HOME/.bashrc"; fi
    if ! grep -q 'PNPM_HOME' "$RC" 2>/dev/null; then
      {
        echo 'export PNPM_HOME="$HOME/.local/share/pnpm"'
        echo 'export PATH="$PNPM_HOME:$PATH"'
      } >> "$RC"
    fi
  fi
  has pnpm || die "pnpm no está en PATH tras instalar. Reabre shell y reintenta."
  ok "pnpm instalado: v$(ver pnpm)"
fi

# Node 20+ requerido
if has node; then
  NODE_MAJOR=$(node -v | sed 's/v\([0-9]*\).*/\1/')
  if (( NODE_MAJOR < 20 )); then
    warn "Node $(node -v) — se recomienda v20+. pnpm puede traer Node con 'pnpm env use --global lts'"
    pnpm env use --global lts || true
  fi
else
  pnpm env use --global lts
fi
ok "node: $(node -v 2>/dev/null || echo 'via pnpm env')"

# ------------- 4. docker -------------
if (( SKIP_DOCKER == 0 )); then
  say "4/7 · verificando Docker"
  if has docker && docker info >/dev/null 2>&1; then
    ok "Docker OK: $(ver docker | awk '{print $3}' | tr -d ',')"
    if ! has "docker-compose" && ! docker compose version >/dev/null 2>&1; then
      die "Docker Compose v2 no detectado. Instalar plugin compose."
    fi
    ok "docker compose OK"
  else
    warn "Docker no detectado/corriendo. Instrucciones:"
    case "$OS" in
      Linux)  echo "  curl -fsSL https://get.docker.com | sh && sudo usermod -aG docker \$USER (reloguear)" ;;
      Darwin) echo "  brew install --cask docker  (o descargar Docker Desktop)" ;;
    esac
    echo "  Volver a correr con --skip-docker si no lo necesitas ahora."
    exit 1
  fi
else
  warn "4/7 · Docker skipped (--skip-docker)"
fi

# ------------- 5. .env -------------
say "5/7 · configurando .env"
if [[ -f .env ]]; then
  ok ".env ya existe (no se sobreescribe)"
else
  cp .env.example .env
  # generar DJANGO_SECRET_KEY
  SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(64))" 2>/dev/null || openssl rand -base64 64 | tr -d '\n')
  # sed portable (Linux usa -i sin backup, macOS requiere -i '')
  if [[ "$OS" == "Darwin" ]]; then
    sed -i '' "s|your-super-secret-production-key-min-50-chars|$SECRET|" .env
  else
    sed -i "s|your-super-secret-production-key-min-50-chars|$SECRET|" .env
  fi
  ok ".env creado desde .env.example (revísalo antes de deploy)"
fi

# ------------- 6. deps -------------
say "6/7 · instalando deps backend + frontend + mcp + simulator"

# backend
if [[ -d backend ]]; then
  (cd backend && uv sync --quiet) && ok "backend · uv sync OK"
fi

# mcp-server
if [[ -d mcp-server ]]; then
  (cd mcp-server && uv sync --quiet) && ok "mcp-server · uv sync OK"
fi

# simulator
if [[ -d simulator ]]; then
  (cd simulator && uv sync --quiet) && ok "simulator · uv sync OK"
fi

# frontend
if [[ -d frontend ]]; then
  (cd frontend && pnpm install --silent) && ok "frontend · pnpm install OK"
fi

# ------------- 7. docker build opcional -------------
if (( SKIP_DOCKER == 0 )); then
  say "7/7 · validando docker compose"
  docker compose config --quiet && ok "docker-compose.yml válido"
  echo
  echo "Para levantar el stack completo:"
  echo "  ${BOLD}docker compose up -d${NC}"
  echo "Para ver logs: ${BOLD}docker compose logs -f${NC}"
fi

# ------------- resumen -------------
echo
echo -e "${GREEN}${BOLD}╔════════════════════════════════════════════╗"
echo -e "║          CacaoTrace listo 🍫                ║"
echo -e "╚════════════════════════════════════════════╝${NC}"
echo
echo "Siguientes pasos:"
echo "  1. Lee ${BOLD}AGENTS.md${NC} y ${BOLD}docs/workflow/<tu-rol>.md${NC}"
echo "  2. Edita ${BOLD}.env${NC} con tus credenciales de Supabase/LLM"
echo "  3. ${BOLD}git checkout feat/<tu-rama>${NC} (ya están creadas)"
echo "  4. ${BOLD}docker compose up -d${NC} para levantar el stack"
echo "  5. Frontend en dev: ${BOLD}cd frontend && pnpm dev${NC}"
echo "  6. Backend en dev: ${BOLD}cd backend && uv run python manage.py runserver${NC}"
echo

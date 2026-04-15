# scripts/

Scripts de setup post-`git clone`. **Corre UNO según tu SO.**

## Linux / macOS

```bash
bash scripts/setup.sh
# o si Docker no está aún:
bash scripts/setup.sh --skip-docker
```

## Windows (PowerShell)

```powershell
powershell -ExecutionPolicy Bypass -File scripts\setup.ps1
# o:
powershell -ExecutionPolicy Bypass -File scripts\setup.ps1 -SkipDocker
```

## Qué hace

1. Verifica `curl`, `git`.
2. Instala **uv** (Astral) si falta → deps Python.
3. Instala **pnpm** si falta (y Node v20+ vía `pnpm env use --global lts`).
4. Verifica **Docker Desktop / Engine** corriendo (puede saltarse con flag).
5. Crea `.env` desde `.env.example` con `DJANGO_SECRET_KEY` random.
6. `uv sync` en `backend/`, `mcp-server/`, `simulator/`.
7. `pnpm install` en `frontend/`.
8. `docker compose config --quiet` para validar YAML.

Al final imprime los comandos para levantar el stack.

## Fallback manual (por si un script falla)

```bash
# uv
curl -LsSf https://astral.sh/uv/install.sh | sh          # Linux/macOS
irm https://astral.sh/uv/install.ps1 | iex               # Windows

# pnpm
curl -fsSL https://get.pnpm.io/install.sh | sh           # Linux/macOS
iwr https://get.pnpm.io/install.ps1 -useb | iex          # Windows
pnpm env use --global lts

# deps
cd backend && uv sync && cd ..
cd mcp-server && uv sync && cd ..
cd simulator && uv sync && cd ..
cd frontend && pnpm install && cd ..

# env
cp .env.example .env   # edita manualmente
```

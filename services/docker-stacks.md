# Docker Stacks

Docker containers are managed by **Dockge** at `http://192.168.1.13:5001`.
All stacks live under `/opt/stacks/` — this is Dockge's stacks directory.

## Stacks

### dockge
- **Path:** `/opt/stacks/dockge/`
- **Port:** `5001`
- **Image:** `louislam/dockge:1`
- **Purpose:** Container management UI. Watches `/opt/stacks` for compose files.
- **Data:** `/opt/stacks/dockge/data/`

### uni
- **Path:** `/opt/stacks/uni/`
- **Port:** `5002` → internal `5001` (Flask web app)
- **Build:** `./app` (Flask app, Python 3.11-slim)
- **Purpose:** University study web app — lecture notes, risposte (answers reveal/hide), quiz system with progress tracking.
- **Volumes:** `/home/lozaniliyanov/git-personal/uni:/uni:ro` — mounts the uni repo read-only
- **DB:** System Postgres 17 (`uni` database, `uni` user) — stores quiz progress. Container connects via `host.docker.internal:5432`.
- **DB URL (from host):** `postgresql://uni:uni@localhost:5432/uni`
- **Env:** `DATABASE_URL`, `UNI_REPO`
- **App source:** `/opt/stacks/uni/app/` — Flask (`app.py`), templates, static JS/CSS
- **Nightly agents:** `~/git-personal/uni/scripts/orchestrator.py` runs at 10:30pm — Python handles all deterministic work (zip extraction, PDF classification, DB queries, weakness scoring, git ops); Claude invoked only for creative content (study notes, quiz questions). Support modules: `material_processor.py` (filesystem), `quiz_engine.py` (DB + scoring). PDFs are auto-classified: text-heavy → pypdf extraction (no tools), diagram-rich → Claude visual read.

### firefly
- **Path:** `/opt/stacks/firefly/`
- **Port:** `5003` → `firefly_iii` (Firefly III main app)
- **Port:** `5004` → `firefly_importer` (Data Importer — CSV imports from banks)
- **Images:** `fireflyiii/core:latest`, `fireflyiii/data-importer:latest`
- **Purpose:** Self-hosted personal finance manager. Tracks expenses fed by CSV exports from Trade Republic (and previously Revolut).
- **DB:** System Postgres 17 (`firefly` database, `firefly` user) — connects via `host.docker.internal:5432`. Credentials in `secrets.env`.
- **Volumes:**
  - `firefly_upload` — Firefly III upload directory (`/var/www/html/storage/upload`)
  - `firefly_importer_config` — Data Importer config storage (`/var/www/html/storage`)
- **Financial files:** `pi-share/financial-hq/` — Trade Republic CSV exports and import mappings live here
- **Importer access token:** Set `FIREFLY_III_ACCESS_TOKEN` in compose.yaml after initial Firefly III setup (create a Personal Access Token under Profile → OAuth)
- **Note:** Importer CSV mapping config for Trade Republic is pending — Trade Republic export format still being researched. Configure after format is confirmed.
- **Env:** `APP_KEY`, `APP_URL`, `DB_*` (see compose.yaml), `FIREFLY_III_URL`, `VANITY_URL`

### homebase-web
- **Path:** `/opt/stacks/homebase-web/`
- **Port:** `8888`
- **Build:** local Dockerfile (python:3.13-slim + mkdocs-material)
- **Purpose:** MkDocs site serving homebase content
- **Volumes:** `/srv/pi-share/homebase:/content:ro`

## Operations

Rebuild and restart a stack:
```
docker compose -f /opt/stacks/<stack>/compose.yaml up -d --build
```

Dockge stores its own compose at `/home/lozaniliyanov/git-personal/homelab/services/dockge/compose.yaml` — that file is the source of truth for Dockge itself and is tracked in the homelab repo.

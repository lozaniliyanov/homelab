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
- **DB port:** `5433` → internal `5432` (Postgres, exposed for host-side agents)
- **Build:** `./app` (Flask app, Python 3.11-slim)
- **Purpose:** University study web app — lecture notes, risposte (answers reveal/hide), quiz system with progress tracking.
- **Volumes:** `/home/lozaniliyanov/git-personal/uni:/uni:ro` — mounts the uni repo read-only
- **DB:** Postgres 16 (`uni_db` named volume) — stores quiz progress
- **DB URL (from host):** `postgresql://uni:uni@localhost:5433/uni`
- **Env:** `DATABASE_URL`, `UNI_REPO`
- **App source:** `/opt/stacks/uni/app/` — Flask (`app.py`), templates, static JS/CSS
- **Nightly agents:** `~/git-personal/uni/scripts/orchestrator.py` runs at 10:30pm — Python handles all deterministic work (zip extraction, PDF classification, DB queries, weakness scoring, git ops); Claude invoked only for creative content (study notes, quiz questions). Support modules: `material_processor.py` (filesystem), `quiz_engine.py` (DB + scoring). PDFs are auto-classified: text-heavy → pypdf extraction (no tools), diagram-rich → Claude visual read.

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

# PostgreSQL Install Runbook

Human-executed installation guide. Follow each step in order. At each **PASTE** marker, copy the output and send it to Claude to verify before continuing.

Based on: `whiteboard/projects/active/postgres-on-pi/01-rnd/findings.md`

---

## Pre-flight checks

**PASTE output**:
```bash
psql --version 2>&1 || echo "Postgres not installed — OK"
ss -tlnp | grep 5432
```

---

## Step 1 — Install PostgreSQL 17 via PGDG

```bash
sudo apt install -y postgresql-common
sudo /usr/share/postgresql-common/pgdg/apt.postgresql.org.sh
sudo apt install -y postgresql-17
```

The PGDG script will ask questions — accept defaults.

**PASTE output of**:
```bash
psql --version
systemctl is-enabled postgresql
systemctl is-active postgresql
```

---

## Step 2 — Memory tuning

Edit `/etc/postgresql/17/main/postgresql.conf`. Find and change these lines (they exist but may be commented out — uncomment and set):

```ini
shared_buffers = 1GB
effective_cache_size = 6GB
work_mem = 8MB
maintenance_work_mem = 256MB
max_wal_size = 1GB
timezone = 'Etc/UTC'
listen_addresses = '*'
```

Do this with:
```bash
sudo -u postgres psql -c "ALTER SYSTEM SET shared_buffers = '1GB';"
sudo -u postgres psql -c "ALTER SYSTEM SET effective_cache_size = '6GB';"
sudo -u postgres psql -c "ALTER SYSTEM SET work_mem = '8MB';"
sudo -u postgres psql -c "ALTER SYSTEM SET maintenance_work_mem = '256MB';"
sudo -u postgres psql -c "ALTER SYSTEM SET max_wal_size = '1GB';"
sudo -u postgres psql -c "ALTER SYSTEM SET timezone = 'Etc/UTC';"
sudo -u postgres psql -c "ALTER SYSTEM SET listen_addresses = '*';"
```

---

## Step 3 — pg_hba.conf (access rules)

```bash
sudo tee /etc/postgresql/17/main/pg_hba.conf <<'EOF'
# TYPE  DATABASE  USER  ADDRESS           METHOD
local   all       all                     peer
host    all       all   127.0.0.1/32      scram-sha-256
host    all       all   ::1/128           scram-sha-256
host    all       all   172.17.0.1/32     scram-sha-256
host    all       all   10.46.116.0/24    scram-sha-256
EOF
```

Note: the `172.17.0.1/32` line is for Docker (not installed yet — safe to include now).

---

## Step 4 — Create users and databases

Pick passwords for `pi_admin` and `lozan` and add them to `~/git-personal/homelab/secrets.env`:

```bash
# Add to secrets.env — replace with real passwords
echo 'POSTGRES_PI_ADMIN_PASSWORD=CHANGEME' >> ~/git-personal/homelab/secrets.env
echo 'POSTGRES_LOZAN_PASSWORD=CHANGEME' >> ~/git-personal/homelab/secrets.env
```

Then create the users (you will be prompted to type the password for each):

```bash
sudo -u postgres createuser --superuser pi_admin
sudo -u postgres psql -c "\password pi_admin"

sudo -u postgres createuser --no-superuser --no-createdb --no-createrole lozan
sudo -u postgres psql -c "\password lozan"
```

Create the databases:

```bash
sudo -u postgres createdb -O pi_admin -E UTF8 -l C -T template0 bulletins
sudo -u postgres createdb -O pi_admin -E UTF8 -l C -T template0 whiteboard
sudo -u postgres createdb -O pi_admin -E UTF8 -l C -T template0 automation
```

Grant lozan access:
```bash
sudo -u postgres psql -c "GRANT CONNECT ON DATABASE bulletins TO lozan;"
sudo -u postgres psql -c "GRANT CONNECT ON DATABASE whiteboard TO lozan;"
sudo -u postgres psql -c "GRANT CONNECT ON DATABASE automation TO lozan;"
```

---

## Step 5 — Restart and verify

```bash
sudo systemctl restart postgresql
```

**PASTE output of**:
```bash
systemctl is-active postgresql
sudo -u postgres psql -c "\l"
sudo -u postgres psql -c "\du"
```

Then test network connectivity (from the Pi itself, simulating a remote connection):
```bash
psql -h 127.0.0.1 -U lozan -d bulletins -c "SELECT version();"
```
You'll be prompted for the lozan password.

**PASTE the output.**

---

## Step 6 — Create schemas and tables

```bash
psql -h 127.0.0.1 -U pi_admin -d bulletins <<'EOF'
CREATE SCHEMA IF NOT EXISTS bulletins;
CREATE TABLE bulletins.tickets (
    id           TEXT PRIMARY KEY,
    title        TEXT NOT NULL,
    posted_by    TEXT NOT NULL,
    timestamp    TIMESTAMPTZ NOT NULL DEFAULT now(),
    category     TEXT NOT NULL,
    status       TEXT NOT NULL DEFAULT 'open',
    picked_up_by TEXT,
    resolved_by  TEXT,
    description  TEXT NOT NULL,
    outcome      TEXT
);
CREATE INDEX ON bulletins.tickets (status);
CREATE INDEX ON bulletins.tickets (timestamp);
GRANT USAGE ON SCHEMA bulletins TO lozan;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA bulletins TO lozan;
EOF
```

```bash
psql -h 127.0.0.1 -U pi_admin -d whiteboard <<'EOF'
CREATE SCHEMA IF NOT EXISTS whiteboard;
CREATE TABLE whiteboard.pipeline_runs (
    id           SERIAL PRIMARY KEY,
    project      TEXT NOT NULL,
    phase        TEXT NOT NULL,
    iteration    INTEGER NOT NULL DEFAULT 1,
    agent        TEXT NOT NULL,
    started_at   TIMESTAMPTZ NOT NULL,
    completed_at TIMESTAMPTZ,
    verdict      TEXT,
    log_path     TEXT
);
CREATE INDEX ON whiteboard.pipeline_runs (project, phase);
CREATE INDEX ON whiteboard.pipeline_runs (started_at);
GRANT USAGE ON SCHEMA whiteboard TO lozan;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA whiteboard TO lozan;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA whiteboard TO lozan;
EOF
```

```bash
psql -h 127.0.0.1 -U pi_admin -d automation <<'EOF'
CREATE SCHEMA IF NOT EXISTS automation;
CREATE TABLE automation.permission_events (
    id         SERIAL PRIMARY KEY,
    device     TEXT NOT NULL,
    permission TEXT NOT NULL,
    action     TEXT NOT NULL,
    timestamp  TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX ON automation.permission_events (device, timestamp);
GRANT USAGE ON SCHEMA automation TO lozan;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA automation TO lozan;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA automation TO lozan;
EOF
```

**PASTE output** (should show CREATE TABLE, CREATE INDEX, GRANT for each).

---

## Step 7 — Backup cron

```bash
mkdir -p ~/backups/postgres
```

Add to crontab (`crontab -e`):
```
0 2 * * * pg_dump -h 127.0.0.1 -U pi_admin bulletins > ~/backups/postgres/bulletins-$(date +\%Y\%m\%d).sql 2>&1
0 2 * * * pg_dump -h 127.0.0.1 -U pi_admin whiteboard > ~/backups/postgres/whiteboard-$(date +\%Y\%m\%d).sql 2>&1
0 2 * * * pg_dump -h 127.0.0.1 -U pi_admin automation > ~/backups/postgres/automation-$(date +\%Y\%m\%d).sql 2>&1
5 2 * * * find ~/backups/postgres/ -name "*.sql" -mtime +7 -delete
```

**PASTE output of**:
```bash
crontab -l | grep postgres
```

---

## Step 8 — Reboot test

```bash
sudo reboot
```

Wait ~60 seconds, reconnect via SSH. **PASTE output of**:
```bash
systemctl is-active postgresql
psql -h 127.0.0.1 -U lozan -d bulletins -c "SELECT 'postgres survived reboot' AS status;"
```

---

## Done

Once all steps are verified, Claude will update the whiteboard project status and set up the backup cron properly.

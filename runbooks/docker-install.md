# Docker Install Runbook

Human-executed installation guide. Follow each step in order. At each **PASTE** marker, copy the output and send it to Claude to verify before continuing.

Full blueprint reference: `whiteboard/projects/active/docker-on-pi/06-blueprint/blueprint.md`

---

## Pre-flight checks

Run this block and **PASTE output**:

```bash
getconf LONG_BIT
grep VERSION_CODENAME /etc/os-release
docker --version 2>&1 || echo "Docker not installed — OK"
ss -tlnp | grep -E ":53|:80|:443|:5432"
ss -tlnp | grep :5001
ip route | grep wg0
```

---

## Step 1 — Install Docker

```bash
sudo apt remove -y docker docker-engine docker.io containerd runc 2>/dev/null || true
sudo apt update
sudo apt install -y ca-certificates curl gnupg lsb-release
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg
echo "deb [arch=arm64 signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian trixie stable" \
  | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo systemctl enable docker
sudo systemctl start docker
sudo usermod -aG docker lozaniliyanov
```

Then run `newgrp docker` (or log out and back in).

**PASTE output of**:
```bash
docker version
docker compose version
systemctl is-enabled docker
groups
```

---

## Step 2 — Daemon config

```bash
sudo tee /etc/docker/daemon.json <<'EOF'
{
  "debug": false,
  "log-level": "warn",
  "live-restore": true,
  "userland-proxy": false,
  "no-new-privileges": true,
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
EOF
sudo systemctl restart docker
```

**PASTE output of**:
```bash
docker info | grep "Logging Driver"
```

---

## Step 3 — Smoke test

```bash
docker run --rm hello-world
docker rmi hello-world
```

**PASTE output** (full hello-world output).

Then coexistence check — **PASTE output**:
```bash
dig @127.0.0.1 google.com +short | head -1
curl -s -o /dev/null -w "%{http_code}" http://localhost/admin/
ss -ulnp | grep 51820
```

---

## Step 4 — Stacks directory

```bash
sudo mkdir -p /opt/stacks
sudo chown lozaniliyanov:lozaniliyanov /opt/stacks
mkdir -p ~/git-personal/homelab/services/dockge
mkdir -p ~/git-personal/homelab/services/dockge/data
```

Write `~/git-personal/homelab/services/dockge/compose.yaml`:

```yaml
services:
  dockge:
    image: louislam/dockge:1
    restart: unless-stopped
    ports:
      - "5001:5001"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - /opt/stacks:/opt/stacks
      - ./data:/app/data
    environment:
      DOCKGE_STACKS_DIR: /opt/stacks
```

Check `.gitignore`:
```bash
grep -E "data/|\.env" ~/git-personal/homelab/.gitignore || echo "MISSING — need to add"
```

If missing, add:
```bash
echo "services/*/data/" >> ~/git-personal/homelab/.gitignore
echo "services/*/.env" >> ~/git-personal/homelab/.gitignore
```

Commit and push:
```bash
git -C ~/git-personal/homelab add services/dockge/ .gitignore
git -C ~/git-personal/homelab commit -m "feat(dockge): add dockge stack compose.yaml"
git -C ~/git-personal/homelab push
```

Create symlink:
```bash
ln -s ~/git-personal/homelab/services/dockge /opt/stacks/dockge
ls -la /opt/stacks/dockge/compose.yaml
```

**PASTE output of the ls line.**

---

## Step 5 — Deploy Dockge

```bash
docker compose -f /opt/stacks/dockge/compose.yaml up -d
```

**PASTE output of**:
```bash
docker ps --filter name=dockge
curl -s -o /dev/null -w "%{http_code}" http://localhost:5001
curl -s -o /dev/null -w "%{http_code}" http://192.168.1.13:5001
```

Then open `http://192.168.1.13:5001` in your browser. If the dockge stack shows as "Running" in the UI, note it. If it doesn't appear, **tell Claude**.

---

## Step 6 — Cgroup check

**PASTE output of**:
```bash
docker info | grep -i cgroup
docker stats --no-stream dockge
```

If memory shows as 0 — Claude will walk you through the cmdline.txt fix. This requires a reboot. If memory shows real values — no action needed.

---

## Step 7 — Reboot test

```bash
sudo reboot
```

Wait ~60 seconds. Reconnect via SSH. **PASTE output of**:
```bash
systemctl is-active docker
docker ps
dig @127.0.0.1 google.com +short | head -1
ss -ulnp | grep 51820
```

---

## Done

Once all steps are verified, Claude will sign off the execution log in the whiteboard repo.

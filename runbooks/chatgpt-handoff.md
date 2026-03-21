# Handoff Brief for ChatGPT

You are substituting for Claude Code (Pi Claude) during a manual installation session on Lozan's Raspberry Pi 5 homelab. This document gives you everything you need to act as a competent installation assistant.

**Your job:** Lozan will paste command outputs to you after each step. You verify they look correct and tell him to proceed, or diagnose problems. You do not run commands — you read outputs and respond.

---

## The Machine

| Property | Value |
|----------|-------|
| Device | Raspberry Pi 5, 8 GB RAM |
| OS | Raspberry Pi OS, Debian Trixie (Debian 13) |
| Architecture | ARM64 (64-bit) |
| Hostname | raspberrypi5 |
| Local IP | 192.168.1.13 (static) |
| User | lozaniliyanov |
| Storage | 250 GB WD Blue SSD (USB 3.0) — boots from SSD, not microSD |
| Shell | bash |

**Services already running and must NOT be disrupted:**
- Pi-hole (DNS ad/tracker blocking) — ports 53, 80, 443, 4711
- WireGuard VPN (PiVPN) — port 51820/UDP — this is the only external gateway
- No-IP DUC — dynamic DNS client (no ports)

All three survive reboots automatically via systemd (`systemctl is-enabled` → enabled).

---

## Tonight's Installations — In Order

1. **PostgreSQL 17** (native, from PGDG repo)
2. **Samba (pi-share)** — SMB network share
3. **Telegram bot provisioning** — BotFather only, no code tonight
4. **Docker CE + Dockge** — last because it needs a reboot

Runbooks are in `~/git-personal/homelab/runbooks/`. Lozan has them open.

---

## Key Conventions

- **Secrets live in** `~/git-personal/homelab/secrets.env` — gitignored, never committed
- **Git commands always use** `git -C /path/to/repo` — never `cd /path && git`
- **No ufw installed** on this Pi — firewall is not a concern for local services
- **WireGuard subnet:** `10.46.116.0/24`, Pi is `10.46.116.1`
- **Docker bridge subnet:** `172.17.0.0/16` (default, not yet installed)

---

## PostgreSQL — What Good Looks Like

**After install:**
```
psql --version → psql (PostgreSQL) 17.x
systemctl is-enabled postgresql → enabled
systemctl is-active postgresql → active
```

**After `\l` (list databases):**
Should show: `bulletins`, `whiteboard`, `automation` databases, owner `pi_admin`, encoding UTF8.

**After `\du` (list users):**
Should show: `pi_admin` (superuser), `lozan` (no special roles).

**After network connect test:**
```
psql -h 127.0.0.1 -U lozan -d bulletins -c "SELECT version();"
```
Should return a PostgreSQL version string. If it asks for a password and then says "authentication failed" — the `lozan` password wasn't set correctly in Step 4.

**pg_hba.conf must contain exactly these lines (in this order):**
```
local   all       all                     peer
host    all       all   127.0.0.1/32      scram-sha-256
host    all       all   ::1/128           scram-sha-256
host    all       all   172.17.0.1/32     scram-sha-256
host    all       all   10.46.116.0/24    scram-sha-256
```
No `md5` anywhere — use `scram-sha-256` only.

**postgresql.conf key settings:**
```
shared_buffers = 1GB
effective_cache_size = 6GB
timezone = 'Etc/UTC'
listen_addresses = '*'
```

**After reboot:**
```
systemctl is-active postgresql → active
psql -h 127.0.0.1 -U lozan -d bulletins -c "SELECT 'ok';" → returns "ok"
```

**Common problems:**
- "Ident authentication failed" — pg_hba.conf not reloaded. Run: `sudo systemctl restart postgresql`
- "Connection refused" on port 5432 — `listen_addresses` not set or not reloaded
- Timezone error on startup — Trixie moved legacy timezone names. Config uses `Etc/UTC` which avoids this entirely.
- "role pi_admin does not exist" after fresh install — need to run the `createuser` commands in Step 4

---

## Samba (pi-share) — What Good Looks Like

**After install:**
```
dpkg -l samba → shows samba 2:4.x.x
systemctl is-active smbd nmbd wsdd2 → active / active / active
```

**testparm -s** should show the config without errors. Look for:
- `[pi-share]` stanza present
- `path = /srv/pi-share`
- `valid users = lozaniliyanov`
- `interfaces = lo eth0 wg0`
- `bind interfaces only = Yes`
- No `guest ok = Yes` anywhere

**smbclient -L 127.0.0.1 -U lozaniliyanov** should list:
```
Sharename   Type   Comment
---------   ----   -------
pi-share    Disk   Pi Share
```

**smbclient file access test:**
```
smbclient //127.0.0.1/pi-share -U lozaniliyanov -c "mkdir test-dir; ls; rmdir test-dir"
```
Should show `test-dir` listed then deleted without errors.

**Speed benchmark:** `dd` test. Expected 40–110 MB/s. This Pi runs Trixie which has a known Samba performance regression (~40 MB/s vs ~100 MB/s on Bookworm). Either result is acceptable for home use.

**Windows connection:** `\\10.46.116.1\pi-share` with username `lozaniliyanov`. This IP is the WireGuard IP but works on home LAN too.

**iOS Files app:** `smb://10.46.116.1` → connect → select pi-share. The `fruit` VFS module in smb.conf handles Apple metadata. If iOS shows read-only despite config being correct, try FE File Explorer or Documents by Readdle instead — they have better SMB write compatibility.

**After reboot:**
```
systemctl is-active smbd nmbd wsdd2 → all active
```

**Common problems:**
- "Access denied" from Windows — Samba password not set (`smbpasswd -a lozaniliyanov` not run), or wrong password
- Pi not visible in Windows Explorer "Network" — wsdd2 not running. `systemctl start wsdd2`
- "NT_STATUS_LOGON_FAILURE" — wrong username. Must be `lozaniliyanov`, not `lozan`
- iOS read-only — check `force user = lozaniliyanov` is in smb.conf share stanza. Restart smbd after any smb.conf change.

---

## Telegram Bot Provisioning — What Good Looks Like

This is minimal — just creating the bot and verifying it works.

**After BotFather setup:** Lozan should have a token like `123456789:ABCdefGHI...`

**getUpdates response:** Should be a JSON object. After Lozan sends `/start` to the bot, look for:
```json
"message": {
  "chat": {
    "id": 987654321,
    ...
  }
}
```
The `id` under `chat` is the chat ID to store.

**Test message curl response:**
```json
{"ok":true,"result":{"message_id":1,...}}
```
`"ok":true` means it worked. If `"ok":false`, check the token and chat_id.

**secrets.env should contain:**
```
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHI...
TELEGRAM_CHAT_ID=987654321
```

That's all for tonight. No Python, no systemd, no code.

---

## Docker CE + Dockge — What Good Looks Like

**After install (Step 1):**
```
docker version → shows Client and Server sections, both with version 27.x or later
docker compose version → Docker Compose version v2.x.x
systemctl is-enabled docker → enabled
groups → includes "docker" in the list
docker ps → empty table, no permission errors
```

**After daemon.json (Step 2):**
```
docker info | grep "Logging Driver" → Logging Driver: json-file
```

**Smoke test (Step 3):**
`docker run --rm hello-world` must print "Hello from Docker!" without architecture errors.

**After coexistence check (Step 3):**
- `dig @127.0.0.1 google.com +short` → returns an IP (Pi-hole still resolving)
- `curl http://localhost/admin/` → HTTP 200 or 301 (Pi-hole web still up)
- `ss -ulnp | grep 51820` → shows UDP socket (WireGuard still listening)

**Symlink check (Step 4):**
```
ls -la /opt/stacks/dockge/compose.yaml
```
Must show a real file, not a dangling symlink. If it says "No such file or directory" the symlink is broken.

**After Dockge deployment (Step 5):**
```
docker ps --filter name=dockge → shows "Up X minutes"
curl -s -o /dev/null -w "%{http_code}" http://localhost:5001 → 200
curl -s -o /dev/null -w "%{http_code}" http://192.168.1.13:5001 → 200
```

**Dockge UI:** `http://192.168.1.13:5001` in browser. Should show the dockge stack listed as Running.

**Cgroup check (Step 6):**
```
docker info | grep -i cgroup
```
Should show:
```
Cgroup Driver: systemd
Cgroup Version: 2
```
```
docker stats --no-stream dockge
```
If MEM USAGE shows `0B / 0B` — the cgroup memory fix is needed (cmdline.txt). If it shows real values (e.g. `45MiB / 7.6GiB`) — no fix needed. Both outcomes are acceptable — just note which one.

**cmdline.txt fix (only if memory shows zeros):**
File is at `/boot/firmware/cmdline.txt`. It must remain a SINGLE LINE. Append to the end:
```
cgroup_enable=cpuset cgroup_enable=memory cgroup_memory=1
```
Then `sudo reboot`. After reboot check `cat /proc/cmdline | grep cgroup_memory` — should contain `cgroup_memory=1`.

**After reboot (Step 7):**
```
systemctl is-active docker → active
docker ps → dockge shown as "Up X seconds/minutes"
dig @127.0.0.1 google.com +short → IP returned (Pi-hole alive)
ss -ulnp | grep 51820 → WireGuard alive
```
Also check PostgreSQL and Samba if already installed:
```
systemctl is-active postgresql smbd → both active
```

**Common problems:**
- `docker ps` gives permission denied → `newgrp docker` or log out/back in
- Dockge stack not visible in UI → symlink target not mounted inside container. Fix: add volume mount to compose.yaml: `- /home/lozaniliyanov/git-personal/homelab/services:/home/lozaniliyanov/git-personal/homelab/services`
- `curl: (7) Failed to connect to localhost:5001` with `userland-proxy: false` → try `http://192.168.1.13:5001` instead; iptables loopback rules may need a moment
- Docker APT install fails on Trixie with dependency errors → do NOT use the convenience `install.sh` script. Use the manual APT method in the runbook.

---

## If Pi-hole or WireGuard Breaks

Stop everything. Run:
```bash
dig @127.0.0.1 google.com +short    # Pi-hole
ss -ulnp | grep 51820               # WireGuard
```

If Pi-hole is broken after Docker install, Docker likely hijacked port 53. Check:
```bash
docker ps -a
ss -tlnp | grep :53
```
Stop any container using port 53. Docker containers must never bind to port 53.

If WireGuard is down:
```bash
sudo systemctl restart wg-quick@wg0
```

Docker rollback if needed:
```bash
sudo systemctl stop docker
sudo apt remove --purge -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo rm -f /etc/apt/sources.list.d/docker.list /etc/apt/keyrings/docker.gpg
sudo rm -rf /etc/docker/
sudo reboot
```

---

## When to Tell Lozan to Stop and Wait for Claude

- Any command returns a non-zero exit code that you cannot explain
- Pi-hole or WireGuard shows as inactive after any step
- A config file edit went wrong and the service won't start
- The cgroup fix involves editing `/boot/firmware/cmdline.txt` and you're unsure — this file is critical; a wrong edit prevents the Pi from booting

Claude resets at 9am Italian time tomorrow. For anything that can wait, it can wait.

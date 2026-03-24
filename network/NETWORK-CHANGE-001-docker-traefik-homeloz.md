# NETWORK-CHANGE-001 — Docker, Traefik, .loz TLD
*Authored by Lozan, transcribed by Pi Claude*

**Status:** READY TO EXECUTE — full audit done 2026-03-24, plan locked

---

## As-Is (Current State — audited 2026-03-24)

### Infrastructure
- Raspberry Pi 5, `raspberrypi5`, `192.168.1.13` (static)
- Router: H2640, gateway `192.168.1.1`
- Docker installed and running
- Dockge running (Docker compose manager)
- No reverse proxy

### Services
| Service | How accessed | Port | Process |
|---|---|---|---|
| Pi-hole web UI | `192.168.1.13/admin` | 80, 443 | pihole-FTL (native) |
| Pi-hole DNS | `192.168.1.13:53` | 53 | pihole-FTL (native) |
| WireGuard | `lozhomevpn.ddns.net:51820` | 51820 UDP | kernel (native) |
| No-IP DUC | background daemon | — | noip2 (native) |
| Postgres | `192.168.1.13:5432` | 5432 | postgres (native) |
| Dockge | `192.168.1.13:5001` | 5001 | Docker container |
| SSH | `192.168.1.13:22` | 22 | sshd (native) |
| Samba | — | 445/139 | smbd/nmbd (native, undocumented) |

### DNS
- Pi-hole is the local DNS server for all LAN devices
- WireGuard clients also use Pi-hole (`DNS = 10.46.116.1` in all peer configs)
- No custom local TLD — everything accessed by IP

### Pi-hole web port config (pihole.toml)
```
webserver.port = "80o,443os,[::]:80o,[::]:443os"
```

### External access
- WireGuard only, via No-IP dynamic hostname
- Nothing else exposed externally

### HTTPS
- None internally

---

## To-Be (Target State)

### Infrastructure
- Docker installed ✓ (already done)
- Traefik running as reverse proxy in Docker
- Pi-hole web UI moved to port 8080 internally
- Pi-hole DNS unchanged (port 53)
- `.loz` local TLD in Pi-hole → all point to `192.168.1.13`
- Postgres running natively (not in Docker)

### Services
| Service | How accessed | Notes |
|---|---|---|
| Pi-hole | `http://pihole.loz/admin` | Behind Traefik, internal port 8080 |
| Traefik dashboard | `http://traefik.loz` | Internal only |
| Dockge | `http://dockge.loz` | Behind Traefik |
| Postgres | `pi.loz:5432` | Not behind Traefik (not HTTP) |
| WireGuard | `lozhomevpn.ddns.net:51820` | Unchanged |
| No-IP DUC | background daemon | Unchanged |
| Jellyfin | `http://jellyfin.loz` | Tier 3, when ready |

### DNS
- Pi-hole Local DNS records (individual, not wildcard):
  - `pi.loz` → `192.168.1.13`
  - `pihole.loz` → `192.168.1.13`
  - `traefik.loz` → `192.168.1.13`
  - `dockge.loz` → `192.168.1.13`
- Traefik routes by hostname to correct service

### External access
- WireGuard only — unchanged, nothing new exposed
- All `.loz` services accessible through WireGuard tunnel (AllowedIPs=0.0.0.0/0 routes all traffic through Pi)

### HTTPS
- Plain HTTP for all `.loz` services
- WireGuard tunnel handles encryption end-to-end
- No certificates needed

---

## Decisions Locked In
- TLD: `.loz` (changed from `.homeloz` — shorter, personal, no real TLD conflict)
- Reverse proxy: Traefik
- No HTTPS internally — WireGuard is sufficient
- WireGuard remains the only external gateway
- Postgres on host, not in Docker — accessed directly as `pi.loz:5432`
- Pi-hole stays native (not in Docker) — Traefik reaches it via `host.docker.internal:8080`

## Open Before Execution
- Error watcher — custom container or Loki/Promtail? (does not block this plan)

---

## Escape Hatches — Memorise Before Starting

| Situation | Recovery |
|---|---|
| Pi-hole UI breaks | SSH in → fix `/etc/pihole/pihole.toml` → `sudo systemctl restart pihole-FTL` |
| Pi-hole DNS breaks | Same — DNS recovers in seconds on restart |
| Traefik misconfigured | `docker compose down` in Traefik stack → services still on raw IP:port |
| Locked out of Pi | SSH `lozaniliyanov@192.168.1.13` (LAN) or `lozaniliyanov@10.46.116.1` (WireGuard) — never changes |

**Nothing in this plan touches WireGuard, No-IP, Postgres, SSH, or the firewall.**

---

## Execution Plan

### Pre-flight (before touching anything)
- [ ] Confirm SSH works: `ssh lozaniliyanov@192.168.1.13`
- [ ] Confirm Pi-hole UI loads: `http://192.168.1.13/admin`
- [ ] Confirm Dockge loads: `http://192.168.1.13:5001`
- [ ] Have Pi-hole admin password ready

---

### Phase 1 — Pi-hole DNS records (zero risk)

**What:** Add Local DNS records in Pi-hole UI.

**Steps:**
1. Open `http://192.168.1.13/admin`
2. Go to **Local DNS → DNS Records**
3. Add: `pi.loz` → `192.168.1.13`

**Test:**
```bash
nslookup pi.loz 192.168.1.13
# Expected: 192.168.1.13
```

**Rollback:** Delete the record in Pi-hole UI. Instant.

---

### Phase 2 — Move Pi-hole web UI off port 80 (low risk)

**What:** Change Pi-hole's webserver port from 80 to 8080 so Traefik can own port 80.

**Important:** Pi-hole DNS (port 53) is completely separate from the web UI. Even if the webserver restart blips, DNS keeps running. The network stays up.

**Steps:**
1. Edit `/etc/pihole/pihole.toml`
2. Find: `port = "80o,443os,[::]:80o,[::]:443os"`
3. Change to: `port = "8080,[::]:8080"`
4. Run: `sudo systemctl restart pihole-FTL`

**Tests:**
```bash
# Web UI on new port — must load
curl -I http://192.168.1.13:8080/admin

# Port 80 must be free now
curl -I http://192.168.1.13/admin  # must fail/timeout

# DNS must still work
nslookup google.com 192.168.1.13  # must resolve
nslookup pi.loz 192.168.1.13      # must return 192.168.1.13
```

**Rollback:** Revert the line in `pihole.toml`, `sudo systemctl restart pihole-FTL`.

---

### Phase 3 — Deploy Traefik (moderate, fully reversible)

**What:** New Docker stack via Dockge. Traefik binds port 80, routes by hostname.

**Key detail:** Pi-hole is native (not Docker). Traefik reaches it via `host.docker.internal:8080`.
Add `extra_hosts: ["host.docker.internal:host-gateway"]` to the Traefik compose.

**Traefik compose — to be written during execution and logged here.**

**DNS records to add in Pi-hole before testing:**
- `traefik.loz` → `192.168.1.13`
- `pihole.loz` → `192.168.1.13`

**Tests:**
```
http://traefik.loz        → Traefik dashboard
http://pihole.loz/admin   → Pi-hole UI
http://192.168.1.13:8080/admin  → still works (direct access preserved)
nslookup google.com 192.168.1.13  → DNS still working
```

**Rollback:** `docker compose down` on Traefik stack. Revert Pi-hole port (Phase 2 rollback). All services back on raw IP:port.

---

### Phase 4 — Route Dockge through Traefik (low risk)

**What:** Add Traefik labels to Dockge compose. Add `dockge.loz` DNS record.

**DNS records to add:**
- `dockge.loz` → `192.168.1.13`

**Tests:**
```
http://dockge.loz         → Dockge
http://192.168.1.13:5001  → still works (direct access preserved)
```

**Rollback:** Remove labels from Dockge compose, `docker compose up -d`. Service still on `:5001`.

---

## Post-Execution Doc Updates
- [ ] Update this doc's As-Is section to reflect final state
- [ ] Update `services/pihole.md` — new URL `pihole.loz`, note internal port 8080
- [ ] Update `network/overview.md` — add `.loz` TLD, Traefik, updated service table
- [ ] Create `services/traefik.md`
- [ ] Create `services/samba.md` (undocumented service, document while we're at it)
- [ ] Fill in Execution Log below

---

## Execution Log

*Fills in as work happens.*

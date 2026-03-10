# NETWORK-CHANGE-001 — Docker, Traefik, .homeloz TLD
*Authored by Lozan, transcribed by Pi Claude*

**Status:** PLANNING — as-is documented, to-be designed, not yet executed

---

## As-Is (Current State)

### Infrastructure
- Raspberry Pi 5, `raspberrypi5`, `192.168.1.13` (static)
- Router: H2640, gateway `192.168.1.1`
- No Docker installed
- No reverse proxy

### Services (all running natively on host)
| Service | How accessed | Port |
|---|---|---|
| Pi-hole | `192.168.1.13/admin` | 80 |
| WireGuard | `lozhomevpn.xxxx.xx:51820` | 51820 UDP |
| No-IP DUC | background daemon | — |

### DNS
- Pi-hole is the local DNS server for all LAN devices
- No custom local TLD — everything accessed by IP

### External access
- WireGuard only, via No-IP dynamic hostname
- Nothing else exposed externally

### HTTPS
- None internally

---

## To-Be (Target State)

### Infrastructure
- Docker installed on Pi
- Traefik running as reverse proxy in Docker
- Pi-hole configured with `.homeloz` local TLD → `192.168.1.13`
- Postgres running natively (not in Docker)

### Services
| Service | How accessed | Notes |
|---|---|---|
| Pi-hole | `pihole.homeloz/admin` | Behind Traefik |
| Traefik dashboard | `traefik.homeloz` | Internal only |
| WireGuard | `lozhomevpn.xxxx.xx:51820` | Unchanged |
| No-IP DUC | background daemon | Unchanged |
| Error watcher | container, no UI | Feeds Postgres + bulletins |
| Jellyfin | `jellyfin.homeloz` | Tier 3, when ready |

### DNS
- Pi-hole resolves `*.homeloz` → `192.168.1.13`
- Traefik routes by hostname to correct container

### External access
- WireGuard only — unchanged, nothing new exposed
- All `.homeloz` services accessible through WireGuard tunnel

### HTTPS
- Plain HTTP for all `.homeloz` services
- WireGuard tunnel handles encryption end-to-end
- No certificates needed

---

## Decisions Locked In
- TLD: `.homeloz`
- Reverse proxy: Traefik
- No HTTPS internally — WireGuard is sufficient
- WireGuard remains the only external gateway
- Postgres on host, not in Docker
- No Redis — Postgres handles event deduplication via fingerprint + timestamp lookup

## Open Before Execution
- Error watcher — custom container or Loki/Promtail?
- Exact Traefik config (will be documented step by step during execution)

## Execution Principles
- One step at a time, tested before the next
- Rollback documented before each change is applied
- Receipts kept in this document under an Execution Log section
- Current state is preserved until to-be is 100% verified

---

## Execution Log

*Nothing executed yet. This section fills in as work happens.*

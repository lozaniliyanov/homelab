# Homelab Context for Claude

This file is auto-loaded into Claude's context every session. It describes the current state of Lozan's home server.

## Hardware

- **Device:** Raspberry Pi 5
- **Hostname:** `raspberrypi5`
- **OS:** Raspberry Pi OS (Debian Trixie)
- **Local IP:** `192.168.1.13` (static)
- **User:** `lozaniliyanov`

## Router

- **Model:** H2640
- **Gateway:** (assumed `192.168.1.1`)

## Services Running

| Service | Purpose | Status |
|---------|---------|--------|
| Pi-hole | Network-wide DNS ad/tracker blocking | Active |
| PiVPN (WireGuard) | Self-hosted VPN server | Active |
| No-IP DUC | Dynamic DNS client — keeps domain pointed at current public IP | Active |

See `/services/` for detailed docs on each service.

## Network

- **WireGuard port:** `51820` (UDP, default)
- **Public hostname:** stored locally in `secrets.env` (gitignored) — not committed to repo
- **DNS:** Pi-hole handles local DNS, upstream configured in Pi-hole settings

See `/network/` for network layout details.

## Git & GitHub

- **Repo:** `homelab` on GitHub (lozaniliyanov/homelab)
- **Auth:** SSH key (`rpi5-github-ssh-key`, `id_ed25519`)
- **Git user:** Lozan Lozanov / lozaniliyanov@users.noreply.github.com
- **gh CLI:** installed (v2.87.3)

## Workflow

- Changes made on the Pi should be committed and pushed to GitHub
- The Windows PC can pull the repo to get the latest state
- This file keeps Claude oriented across sessions and machines
- Sensitive values (domain, IPs, keys) go in `secrets.env` which is gitignored

## Planned / Future

- To be documented as ideas are developed

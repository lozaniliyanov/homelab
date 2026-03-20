# homelab

Documentation and configuration tracker for Lozan's home server — a Raspberry Pi 5 running self-hosted services.

## Purpose

This repo serves as:
- A living record of what's running on the Pi and how it's configured
- Context for AI-assisted work across devices (see `CLAUDE.md`)
- A changelog of changes made over time

## Structure

```
homelab/
├── CLAUDE.md               # Auto-loaded context for Claude
├── README.md               # This file
├── .gitignore
├── secrets.env.example     # Template for sensitive values (real file is gitignored)
├── hardware/
│   └── pi5.md              # Full hardware spec: Pi 5, SSD, Radxa hat, cooling, networking
├── services/
│   ├── pihole.md           # Pi-hole configuration and blocklists
│   ├── pivpn.md            # PiVPN / WireGuard setup
│   └── noip.md             # No-IP Dynamic DNS client
├── network/
│   └── overview.md         # Network layout, port forwarding, DNS
└── automation/
    └── dotfiles-sync.md    # Daily cron: pull dotfiles and re-apply Claude config
```

## Hardware

- **Raspberry Pi 5 8GB** with official 27W PSU, active cooler, bumper
- **OS storage:** 250GB WD Blue SSD (USB 3.0, Sabrent enclosure) — Pi boots from SSD, no SD card
- **HAT:** Radxa Penta SATA HAT (12V barrel jack PSU) — no SATA drives yet, NAS planned
- **Network:** Cat 6e to ISP router, 1 Gbps fiber
- **Router:** H2640
- See [`hardware/pi5.md`](hardware/pi5.md) for full details

## Services

| Service | Purpose |
|---------|---------|
| Pi-hole | Network-wide DNS ad/tracker blocking |
| PiVPN (WireGuard) | Self-hosted VPN |
| No-IP DUC | Dynamic DNS — keeps hostname pointed at current public IP |

## Sensitive Values

Sensitive values (domain names, credentials) are stored in `secrets.env` locally, which is gitignored. Use `secrets.env.example` as a template.

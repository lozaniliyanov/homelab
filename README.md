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

- **Raspberry Pi 5**
- **Router:** H2640

## Services

| Service | Purpose |
|---------|---------|
| Pi-hole | Network-wide DNS ad/tracker blocking |
| PiVPN (WireGuard) | Self-hosted VPN |
| No-IP DUC | Dynamic DNS — keeps hostname pointed at current public IP |

## Sensitive Values

Sensitive values (domain names, credentials) are stored in `secrets.env` locally, which is gitignored. Use `secrets.env.example` as a template.

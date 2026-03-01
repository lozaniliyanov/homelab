# Network Overview

## Local Network

| Device | Role | Local IP |
|--------|------|----------|
| H2640 Router | Gateway / DHCP | `192.168.1.1` (assumed) |
| Raspberry Pi 5 | Home server | `192.168.1.13` (static) |

## DNS

- Pi-hole on `192.168.1.13` handles DNS for the network
- Devices should have their DNS set to `192.168.1.13`
- Pi-hole forwards non-blocked queries to upstream DNS servers

## Port Forwarding

| Port | Protocol | Forwarded To | Purpose |
|------|----------|--------------|---------|
| 51820 | UDP | 192.168.1.13 | WireGuard VPN |

## Public Access

- Public IP is dynamic (ISP-assigned)
- No-IP DUC on the Pi keeps the domain up to date
- Public hostname stored in `secrets.env` (gitignored)

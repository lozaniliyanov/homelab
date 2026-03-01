# PiVPN — WireGuard

## Overview

PiVPN is installed on the Pi and runs a WireGuard VPN server. This allows devices outside the home network to connect securely and route traffic through the Pi, giving them access to the local network and using the home connection for internet traffic.

## Configuration

- **Protocol:** WireGuard
- **Port:** `51820` (UDP)
- **Server endpoint:** defined by No-IP dynamic domain (see `secrets.env`)
- **Server local IP:** `192.168.1.13`

## Peers / Clients

| Device | Status |
|--------|--------|
| Phone | Configured |
| (family devices to be added) | Planned |

## Useful Commands

```bash
# List all peers
pivpn -l

# Add a new peer
pivpn -a

# Remove a peer
pivpn -r <name>

# Show WireGuard status
pivpn -s

# Show QR code for a peer (for mobile)
pivpn -qr <name>
```

## Config Location

- WireGuard config: `/etc/wireguard/wg0.conf`
- PiVPN config: `/etc/pivpn/wireguard/setupVars.conf`

## Notes

- Port `51820` UDP must be forwarded on the router to `192.168.1.13`
- The No-IP domain is used as the endpoint so peers stay connected even when the public IP changes

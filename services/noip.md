# No-IP — Dynamic DNS

## Overview

No-IP provides a Dynamic DNS (DDNS) service. Since the home network's public IP can change at any time (assigned by the ISP), No-IP keeps a static hostname pointed at the current IP.

The No-IP Dynamic Update Client (DUC) is installed and running on the Pi. It periodically checks the current public IP and updates the No-IP hostname if it has changed.

## Configuration

- **Hostname:** stored in `secrets.env` (gitignored)
- **DUC installed on:** the Pi (`192.168.1.13`)
- **Update interval:** periodic (default DUC interval)

## Why This Matters

PiVPN (WireGuard) uses the No-IP hostname as the server endpoint in peer configs. This means even if the home public IP changes, peers don't need to be reconfigured — they always connect via the domain name.

## Config Location

- No-IP DUC config: `/etc/no-ip2.conf` or `/usr/local/etc/no-ip2.conf`

## Useful Commands

```bash
# Check No-IP DUC service status
sudo systemctl status noip2

# Restart the DUC
sudo systemctl restart noip2

# View logs
sudo journalctl -u noip2 -n 50
```

## Systemd Service

The service file is at `/etc/systemd/system/noip2.service`. It is configured to wait for full network availability before starting:

```ini
[Unit]
Description=No-IP Dynamic DNS Update Client
After=network-online.target
Wants=network-online.target

[Service]
Type=forking
ExecStart=/usr/local/bin/noip2
Restart=always

[Install]
WantedBy=multi-user.target
```

**Important:** use `network-online.target` (not `network.target`). The latter only waits for interfaces to be up, not for DNS to be resolvable. Starting too early causes the DUC to fail its initial update silently.

## Notes

- Keep the No-IP account active — free accounts require confirmation every 30 days
- The hostname is used in WireGuard peer configs as the endpoint

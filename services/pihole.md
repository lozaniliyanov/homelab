# Pi-hole

## Overview

Pi-hole is a network-wide DNS sinkhole running on the Pi. All devices on the local network route their DNS queries through the Pi, which filters out ads, trackers, and malicious domains before they ever reach the device.

## Access

- **Web UI:** `http://192.168.1.13/admin`
- **DNS:** `192.168.1.13` (set as DNS server on router or per-device)

## Blocklists

All lists are enabled. Gravity is updated periodically.

| # | URL | Description |
|---|-----|-------------|
| 1 | https://raw.githubusercontent.com/StevenBlack/hosts/master/hosts | StevenBlack combined hosts (ads + malware) |
| 2 | https://github.com/hagezi/dns-blocklists/blob/main/adblock/pro.txt | Hagezi Pro |
| 5 | https://gitlab.com/hagezi/mirror/-/raw/main/dns-blocklists/adblock/multi.txt | Hagezi Multi |
| 6 | https://gitlab.com/hagezi/mirror/-/raw/main/dns-blocklists/adblock/popupads.txt | Hagezi Popup Ads |
| 7 | https://gitlab.com/hagezi/mirror/-/raw/main/dns-blocklists/adblock/tif.txt | Hagezi Threat Intelligence Feeds |
| 8 | https://gitlab.com/hagezi/mirror/-/raw/main/dns-blocklists/adblock/fake.txt | Hagezi Fake/Scam domains |

## Config Location

- Main config: `/etc/pihole/pihole.toml`
- Gravity database: `/etc/pihole/gravity.db`
- Custom hosts: `/etc/pihole/hosts/custom.list`

## Notes

- Pi-hole v6 is installed (uses `pihole.toml` instead of older `setupVars.conf`)
- Upstream DNS configured via the web UI

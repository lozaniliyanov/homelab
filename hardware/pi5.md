# Hardware — Raspberry Pi 5 Setup

## Core

| Component | Details |
|---|---|
| SBC | Raspberry Pi 5 8GB |
| PSU | Official Raspberry Pi 27W USB-C PSU |
| Cooling | Official Raspberry Pi Active Cooler (fan + heatsink) |
| Case | Official Raspberry Pi Bumper (no full case — incompatible with Radxa hat, see below) |

## Storage

| Component | Details |
|---|---|
| OS drive | Western Digital Blue 250GB SSD |
| Enclosure | Sabrent transparent USB enclosure |
| Connection | USB-A 3.0/3.1 to Pi |

The Pi boots from the SSD. There is no SD card in active use. The SSD enclosure is positioned near the front intake fans of the Home PC case (Corsair 5000D Airflow) for passive cooling — no contact, no hazard.

## HAT

| Component | Details |
|---|---|
| HAT | Radxa Penta SATA HAT |
| HAT PSU | 12V barrel jack (60W) |
| SATA drives attached | None yet |
| Goal | Attach 2× 2TB SSDs, deploy NAS service (OpenMediaVault or alternative) |

**Power note:** The Pi cannot boot using only the barrel jack, despite passthrough power being advertised. The official 27W USB-C PSU is required for boot. The barrel jack supplements power once the Pi is running.

**Case note:** No known case is compatible with the Radxa Penta SATA HAT and the Raspberry Pi 5. The Pi runs with bumper only, no enclosure.

## Networking

| Component | Details |
|---|---|
| Connection | Cat 6e ethernet to ISP router |
| ISP speed | 1 Gbps fiber |
| Local IP | `192.168.1.13` (static) |

## Physical Location & Cooling

The Pi is positioned on top of the Home PC (Corsair 5000D Airflow). The Home PC's top exhaust fans blow air over the Pi — worst-case room temperature air, even in summer. The OS SSD enclosure sits between the front intake fans and the front grill of the Home PC case for passive airflow.

Home PC is not always on. When off, the Pi's active cooler handles thermals independently.

## Planned Upgrades

- Attach 2× 2TB SSDs to Radxa Penta SATA HAT
- Deploy NAS service (OpenMediaVault primary candidate, alternatives considered)
- This will require a NAS-compatible PSU solution for the HAT and potentially a custom mounting arrangement given the no-case constraint

# Pi Claude — Crontab

Canonical record of all scheduled cron jobs on the Pi. If the Pi is wiped, recreate with:
`crontab -e` and paste the entries below.

## Schedule rationale

The order matters. Each morning:
1. `promote-permissions` promotes cross-device permissions and pushes to dotfiles
2. `apply.py` immediately picks up those changes and writes `settings.json`
3. `check-tickets` runs with fresh permissions

Before the night shift:
4. `apply.py` runs again to catch any permissions approved during daytime sessions
5. `orchestrator` (whiteboard) runs with fully up-to-date `settings.json`

## Jobs

| Time | Script | Log |
|---|---|---|
| 5:00am daily | `promote-permissions.py` | `~/logs/promote-permissions.log` |
| 5:15am daily | dotfiles pull + apply.py | `~/logs/dotfiles-sync.log` |
| 5:30am daily | `check-tickets.py` | `~/logs/check-tickets.log` |
| 9:50pm daily | dotfiles pull + apply.py | `~/logs/dotfiles-sync.log` |
| 10:00pm daily | whiteboard orchestrator | `~/logs/whiteboard/orchestrator.log` |

## Crontab entries

```
0 5 * * * echo "=== $(date) ===" >> /home/lozaniliyanov/logs/promote-permissions.log 2>&1 && python3 /home/lozaniliyanov/git-personal/homelab/automation/promote-permissions.py >> /home/lozaniliyanov/logs/promote-permissions.log 2>&1
15 5 * * * echo "=== $(date) ===" >> /home/lozaniliyanov/logs/dotfiles-sync.log 2>&1 && git -C /home/lozaniliyanov/git-personal/dotfiles pull >> /home/lozaniliyanov/logs/dotfiles-sync.log 2>&1 && python3 /home/lozaniliyanov/git-personal/dotfiles/claude/scripts/apply.py rpi5 >> /home/lozaniliyanov/logs/dotfiles-sync.log 2>&1
30 5 * * * echo "=== $(date) ===" >> /home/lozaniliyanov/logs/check-tickets.log 2>&1 && python3 /home/lozaniliyanov/git-personal/homelab/automation/check-tickets.py >> /home/lozaniliyanov/logs/check-tickets.log 2>&1
50 21 * * * echo "=== $(date) ===" >> /home/lozaniliyanov/logs/dotfiles-sync.log 2>&1 && git -C /home/lozaniliyanov/git-personal/dotfiles pull >> /home/lozaniliyanov/logs/dotfiles-sync.log 2>&1 && python3 /home/lozaniliyanov/git-personal/dotfiles/claude/scripts/apply.py rpi5 >> /home/lozaniliyanov/logs/dotfiles-sync.log 2>&1
0 22 * * * mkdir -p /home/lozaniliyanov/logs/whiteboard && echo "=== $(date) ===" >> /home/lozaniliyanov/logs/whiteboard/orchestrator.log 2>&1 && python3 /home/lozaniliyanov/git-personal/whiteboard/scripts/orchestrator.py >> /home/lozaniliyanov/logs/whiteboard/orchestrator.log 2>&1
```

## Log files

All logs live in `~/logs/`. Directory is created manually — recreate if missing:
```
mkdir -p ~/logs
```

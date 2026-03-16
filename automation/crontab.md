# Pi Claude — Crontab

Canonical record of all scheduled cron jobs on the Pi. If the Pi is wiped, recreate with:
`crontab -e` and paste the entries below.

## Jobs

| Time | Script | Log |
|---|---|---|
| 5am daily | `promote-permissions.py` | `~/logs/promote-permissions.log` |
| 7am daily | `check-tickets.py` | `~/logs/check-tickets.log` |
| 9am daily | dotfiles sync + apply.py | `~/logs/dotfiles-sync.log` |

## Crontab entries

```
0 5 * * * echo "=== $(date) ===" >> /home/lozaniliyanov/logs/promote-permissions.log 2>&1 && python3 /home/lozaniliyanov/git-personal/homelab/automation/promote-permissions.py >> /home/lozaniliyanov/logs/promote-permissions.log 2>&1
0 7 * * * echo "=== $(date) ===" >> /home/lozaniliyanov/logs/check-tickets.log 2>&1 && python3 /home/lozaniliyanov/git-personal/homelab/automation/check-tickets.py >> /home/lozaniliyanov/logs/check-tickets.log 2>&1
0 9 * * * echo "=== $(date) ===" >> /home/lozaniliyanov/logs/dotfiles-sync.log 2>&1 && git -C /home/lozaniliyanov/git-personal/dotfiles pull >> /home/lozaniliyanov/logs/dotfiles-sync.log 2>&1 && python3 /home/lozaniliyanov/git-personal/dotfiles/claude/scripts/apply.py rpi5 >> /home/lozaniliyanov/logs/dotfiles-sync.log 2>&1
```

## Log files

All logs live in `~/logs/`. Directory is created manually — recreate if missing:
```
mkdir -p ~/logs
```

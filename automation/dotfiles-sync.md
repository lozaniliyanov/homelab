# Dotfiles Sync — Scheduled Automation

Pulls the latest dotfiles from GitHub and re-applies the Claude config daily.

## Schedule

Runs every day at **9:00 AM** via cron.

## What It Does

1. `git -C ~/git-personal/dotfiles pull` — pulls latest from `lozaniliyanov/dotfiles`
2. `python3 .../apply.py rpi5` — merges base + rpi5 device config and deploys to `~/.claude/`

## Crontab Entry

```
0 9 * * * echo "=== $(date) ===" >> /home/lozaniliyanov/logs/dotfiles-sync.log 2>&1 && git -C /home/lozaniliyanov/git-personal/dotfiles pull >> /home/lozaniliyanov/logs/dotfiles-sync.log 2>&1 && python3 /home/lozaniliyanov/git-personal/dotfiles/claude/scripts/apply.py rpi5 >> /home/lozaniliyanov/logs/dotfiles-sync.log 2>&1
```

## Log File

Output (stdout + stderr) is appended to:

```
/home/lozaniliyanov/logs/dotfiles-sync.log
```

Each run is separated by a `=== <timestamp> ===` header.

## Manual Run

```bash
echo "=== $(date) ===" >> ~/logs/dotfiles-sync.log 2>&1
git -C ~/git-personal/dotfiles pull >> ~/logs/dotfiles-sync.log 2>&1
python3 ~/git-personal/dotfiles/claude/scripts/apply.py rpi5 >> ~/logs/dotfiles-sync.log 2>&1
```

Or to run and watch live:

```bash
git -C ~/git-personal/dotfiles pull && python3 ~/git-personal/dotfiles/claude/scripts/apply.py rpi5
```

## Checking the Log

```bash
tail -50 ~/logs/dotfiles-sync.log
```

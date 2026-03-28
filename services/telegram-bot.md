# Telegram Bot

## Overview

Two-way Telegram bot running on the Pi via Claude Code's official Telegram plugin. Incoming messages from Lozan are forwarded to a Claude Code session; replies go back via the bot.

## Components

| Component | Location | Purpose |
|-----------|----------|---------|
| Plugin | `~/.claude/plugins/cache/claude-plugins-official/telegram/0.0.4/` | MCP server (Bun/TypeScript) — connects to Telegram API |
| Token | `~/.claude/channels/telegram/.env` | Bot credentials (gitignored) |
| Access config | `~/.claude/channels/telegram/access.json` | Allowlist and pairing state |
| Daemon wrapper | `~/.local/bin/claude-telegram-daemon.sh` | Allocates PTY so Claude runs headlessly |
| Systemd service | `/etc/systemd/system/claude-telegram.service` | Keeps bot alive 24/7 |

## Access Control

- Policy: `allowlist` — only Lozan's Telegram user ID can reach the bot
- To add another user: flip policy to `pairing`, have them DM the bot, approve with `/telegram:access pair <code>`, flip back to `allowlist`

## Service Management

```bash
sudo systemctl status claude-telegram
sudo systemctl restart claude-telegram
sudo journalctl -u claude-telegram -f
```

## Setup Notes

- Requires Bun runtime: `/usr/local/bin/bun` (symlinked from `~/.bun/bin/bun`)
- Claude Code `--channels` mode requires a PTY — daemon wrapper uses `script -q -f` to provide one
- `/home/lozaniliyanov` must have `hasTrustDialogAccepted: true` in `~/.claude.json` to skip the interactive trust prompt at startup
- Bot token was provisioned via BotFather; stored only in `~/.claude/channels/telegram/.env`

## Known Limitations

- Claude Code `--channels` is experimental — updates could change behaviour
- The PTY trick (`script`) is a workaround, not first-class daemon support
- No message history — bot only sees messages as they arrive

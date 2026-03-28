#!/usr/bin/env python3
"""
Send a Telegram notification.

Usage:
  notify.py "message text"
  notify.py --title "Title" "message body"
  echo "piped message" | notify.py

Reads TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID from secrets.env.
Can be called from any script, cron job, or the Pi listener.
"""

import argparse
import os
import sys
import urllib.request
import urllib.parse
import json
from pathlib import Path

SECRETS_FILE = Path.home() / "git-personal" / "homelab" / "secrets.env"


def load_secrets():
    """Load secrets from .env file without importing dotenv (zero dependencies)."""
    secrets = {}
    if not SECRETS_FILE.exists():
        return secrets
    for line in SECRETS_FILE.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        secrets[key.strip()] = value.strip().strip("'\"")
    return secrets


def send_telegram(token, chat_id, message, parse_mode="Markdown"):
    """Send a message via Telegram Bot API using only stdlib."""
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = json.dumps({
        "chat_id": chat_id,
        "text": message,
        "parse_mode": parse_mode,
    }).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read())
            return result.get("ok", False)
    except Exception as e:
        print(f"[notify] Failed to send: {e}", file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(description="Send a Telegram notification.")
    parser.add_argument("message", nargs="?", help="Message text")
    parser.add_argument("--title", help="Optional title (prepended as bold)")
    args = parser.parse_args()

    # Get message from arg or stdin
    if args.message:
        message = args.message
    elif not sys.stdin.isatty():
        message = sys.stdin.read().strip()
    else:
        print("No message provided.", file=sys.stderr)
        sys.exit(1)

    # Prepend title if given
    if args.title:
        message = f"*{args.title}*\n\n{message}"

    # Load credentials
    secrets = load_secrets()
    token = os.environ.get("TELEGRAM_BOT_TOKEN") or secrets.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID") or secrets.get("TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        print("[notify] TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID not found in secrets.env or environment.", file=sys.stderr)
        sys.exit(1)

    ok = send_telegram(token, chat_id, message)
    if ok:
        print(f"[notify] Sent: {message[:80]}...")
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()

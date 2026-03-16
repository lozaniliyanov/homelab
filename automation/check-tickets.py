#!/usr/bin/env python3
"""
check-tickets.py

Runs as a cron on Pi Claude (7am daily).
Pulls the bulletins repo and logs open ticket count and titles.
Foundation for future self-heal logic (Phase 3).
"""

import subprocess
from datetime import datetime
from pathlib import Path

HOME = Path.home()


def load_secrets():
    secrets_path = HOME / ".claude" / "secrets.env"
    secrets = {}
    if secrets_path.exists():
        for line in secrets_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, _, value = line.partition("=")
                secrets[key.strip()] = value.strip()
    return secrets


def run(cmd):
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout.strip(), result.stderr.strip(), result.returncode


def main():
    secrets = load_secrets()
    bulletins_dir = Path(secrets.get("BULLETINS_DIR", str(HOME / "git-personal" / "bulletins")))
    tickets_open = bulletins_dir / "tickets" / "open"

    print(f"[check-tickets] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Pull latest bulletins
    _, err, code = run(["git", "-C", str(bulletins_dir), "pull"])
    if code != 0:
        print(f"[check-tickets] git pull failed: {err}")
        return
    print("[check-tickets] Pulled bulletins.")

    # List open tickets
    if not tickets_open.exists():
        print("[check-tickets] No tickets/open/ directory found.")
        return

    tickets = [f for f in tickets_open.iterdir() if f.is_file() and f.suffix == ".md"]

    if not tickets:
        print("[check-tickets] No open tickets.")
        return

    print(f"[check-tickets] {len(tickets)} open ticket(s):")
    for t in sorted(tickets):
        print(f"  - {t.name}")


if __name__ == "__main__":
    main()

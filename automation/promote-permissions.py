#!/usr/bin/env python3
"""
promote-permissions.py

Runs as a cron on Pi Claude (5am daily).
Reads all device permissions.json files and permissions.base.json.
Promotes any permission appearing in 2+ device files to base.
Commits and pushes the updated dotfiles.
Writes a bulletin ticket per device listing promoted permissions to test.
"""

import json
import subprocess
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

HOME = Path.home()
DEVICES = ["rpi5", "work-pc", "home-pc"]
PROMOTION_THRESHOLD = 2


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
    dotfiles_dir = Path(secrets.get("DOTFILES_DIR", str(HOME / "git-personal" / "dotfiles")))
    bulletins_dir = Path(secrets.get("BULLETINS_DIR", str(HOME / "git-personal" / "bulletins")))
    dotfiles_claude = dotfiles_dir / "claude"

    # Load base permissions
    base_path = dotfiles_claude / "permissions.base.json"
    base_data = json.loads(base_path.read_text(encoding="utf-8")) if base_path.exists() else {"allow": []}
    base_allow = set(base_data.get("allow", []))

    # Load each device's permissions
    device_data = {}
    device_allow = {}
    for device in DEVICES:
        p = dotfiles_claude / "devices" / device / "permissions.json"
        data = json.loads(p.read_text(encoding="utf-8")) if p.exists() else {"allow": []}
        device_data[device] = data
        device_allow[device] = set(data.get("allow", []))

    # Count how many devices have each permission (excluding ones already in base)
    counts = defaultdict(set)
    for device in DEVICES:
        for perm in device_allow[device]:
            if perm not in base_allow:
                counts[perm].add(device)

    # Find promotion candidates
    to_promote = {perm: devices for perm, devices in counts.items() if len(devices) >= PROMOTION_THRESHOLD}

    if not to_promote:
        print("[promote-permissions] No permissions to promote.")
        return

    print(f"[promote-permissions] Promoting {len(to_promote)} permission(s): {sorted(to_promote.keys())}")

    # Add to base
    base_data["allow"] = sorted(base_allow | set(to_promote.keys()))
    base_path.write_text(json.dumps(base_data, indent=2) + "\n", encoding="utf-8")

    # Remove from device files
    for device in DEVICES:
        updated = [p for p in device_data[device].get("allow", []) if p not in to_promote]
        device_data[device]["allow"] = updated
        p = dotfiles_claude / "devices" / device / "permissions.json"
        p.write_text(json.dumps(device_data[device], indent=2) + "\n", encoding="utf-8")

    # Pull, commit, push dotfiles
    _, err, code = run(["git", "-C", str(dotfiles_dir), "pull", "--rebase", "--autostash"])
    if code != 0:
        print(f"[promote-permissions] git pull failed: {err}")
        return

    files_to_add = [str(base_path)] + [
        str(dotfiles_claude / "devices" / d / "permissions.json") for d in DEVICES
    ]
    run(["git", "-C", str(dotfiles_dir), "add"] + files_to_add)

    promoted_str = ", ".join(sorted(to_promote.keys()))
    _, err, code = run(["git", "-C", str(dotfiles_dir), "commit", "-m",
                        f"[Pi Claude] Promote to base: {promoted_str}"])
    if code != 0:
        print(f"[promote-permissions] git commit failed: {err}")
        return

    _, err, code = run(["git", "-C", str(dotfiles_dir), "push"])
    if code != 0:
        print(f"[promote-permissions] git push failed: {err}")
        return

    print("[promote-permissions] Pushed updated permissions to dotfiles.")

    # Write one bulletin ticket per device
    post_ticket = bulletins_dir / "scripts" / "post-ticket.py"
    if not post_ticket.exists():
        print("[promote-permissions] post-ticket.py not found, skipping tickets.")
        return

    for device in DEVICES:
        desc = (
            f"The following permission(s) were promoted from per-device files to "
            f"permissions.base.json on {datetime.now().strftime('%Y-%m-%d')} "
            f"because they appeared on {PROMOTION_THRESHOLD}+ devices:\n\n"
            + "\n".join(f"  - {p}" for p in sorted(to_promote.keys()))
            + "\n\nThese are now in the shared base and removed from per-device files. "
            "On your next /sync they will be included automatically.\n\n"
            "Please verify:\n"
            "1. Run /sync\n"
            "2. Confirm the promoted permissions work as expected\n"
            "3. Resolve this ticket if all good, or open a new ticket if something broke"
        )
        subprocess.run([
            sys.executable, str(post_ticket),
            "--title", f"[{device}] Test promoted permissions in base",
            "--category", "config",
            "--description", desc,
        ])
        print(f"[promote-permissions] Posted ticket for {device}.")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
pi-listener.py — homebase file-based task queue

Watches 08 Handoffs/Inbox/ for new .md files.
Processes claude-task actions and sends results via Telegram.
"""

import subprocess
import sys
import re
import logging
import shutil
from pathlib import Path
from datetime import datetime

# ── Config ─────────────────────────────────────────────────────────────────────

HOMEBASE     = Path("/srv/pi-share/homebase")
INBOX        = HOMEBASE / "08 Handoffs" / "Inbox"
IN_PROGRESS  = HOMEBASE / "08 Handoffs" / "In Progress"
DONE         = HOMEBASE / "08 Handoffs" / "Done"
FAILED       = HOMEBASE / "08 Handoffs" / "Failed"

NOTIFY_SCRIPT = Path("/home/lozaniliyanov/git-personal/homelab/scripts/notify.py")
CLAUDE_BIN    = Path("/home/lozaniliyanov/.local/bin/claude")
LOG_DIR       = Path("/home/lozaniliyanov/logs/pi-listener")
LOG_FILE      = LOG_DIR / "listener.log"
TIMEOUT       = 120  # seconds for claude-task

# ── Logging ────────────────────────────────────────────────────────────────────

LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger(__name__)

# ── Frontmatter ────────────────────────────────────────────────────────────────

def parse_frontmatter(text):
    """Return (meta dict, body string)."""
    meta, body = {}, text
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            for line in text[3:end].strip().splitlines():
                if ":" in line:
                    k, _, v = line.partition(":")
                    meta[k.strip()] = v.strip()
            body = text[end + 4:].strip()
    return meta, body


def set_frontmatter_field(text, key, value):
    """Update or insert a key in the YAML frontmatter."""
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            fm = text[3:end]
            new_line = f"{key}: {value}"
            pattern = rf"^{re.escape(key)}\s*:.*$"
            if re.search(pattern, fm, re.MULTILINE):
                fm = re.sub(pattern, new_line, fm, flags=re.MULTILINE)
            else:
                fm = fm.rstrip() + f"\n{new_line}"
            return "---" + fm + "\n---" + text[end + 4:]
    return text

# ── Telegram ───────────────────────────────────────────────────────────────────

def notify(title, message):
    try:
        subprocess.run(
            ["python3", str(NOTIFY_SCRIPT), "--title", title, message],
            timeout=15,
            check=False,
        )
    except Exception as e:
        log.error(f"notify failed: {e}")

# ── Handlers ───────────────────────────────────────────────────────────────────

def handle_claude_task(body):
    """Run claude --print on body. Returns (success: bool, output: str)."""
    try:
        result = subprocess.run(
            [str(CLAUDE_BIN), "--print", body],
            capture_output=True,
            text=True,
            timeout=TIMEOUT,
            cwd="/home/lozaniliyanov",
            env={
                "HOME": "/home/lozaniliyanov",
                "PATH": "/home/lozaniliyanov/.local/bin:/home/lozaniliyanov/.bun/bin:/usr/local/bin:/usr/bin:/bin",
            },
        )
        if result.returncode == 0:
            return True, result.stdout.strip()
        return False, result.stderr.strip() or f"claude exited {result.returncode}"
    except subprocess.TimeoutExpired:
        return False, f"timeout after {TIMEOUT}s"
    except Exception as e:
        return False, str(e)

# ── File processor ─────────────────────────────────────────────────────────────

def process_file(path):
    path = Path(path)
    if not path.exists() or path.suffix != ".md" or path.name.startswith(".tmp-"):
        return

    text = path.read_text(encoding="utf-8")
    meta, body = parse_frontmatter(text)

    status = meta.get("status", "pending")
    if status not in ("pending", ""):
        log.info(f"skip {path.name} | status={status}")
        return

    action = meta.get("action", "claude-task")
    filename = path.name
    start = datetime.now()

    log.info(f"pickup {filename} | action={action}")

    # Mark in-progress before doing anything (idempotency)
    text = set_frontmatter_field(text, "status", "in-progress")
    IN_PROGRESS.mkdir(parents=True, exist_ok=True)
    in_prog = IN_PROGRESS / filename
    shutil.move(str(path), in_prog)
    in_prog.write_text(text, encoding="utf-8")

    # Dispatch
    if not body.strip():
        success, output = False, "empty body — nothing to process"
    elif action == "claude-task":
        success, output = handle_claude_task(body)
    else:
        success, output = False, f"unknown action: {action}"

    elapsed = round((datetime.now() - start).total_seconds(), 1)

    if success:
        text = set_frontmatter_field(text, "status", "completed")
        text = set_frontmatter_field(text, "completed", datetime.now().isoformat(timespec="seconds"))
        DONE.mkdir(parents=True, exist_ok=True)
        dest = DONE / filename
        shutil.move(str(in_prog), dest)
        dest.write_text(text, encoding="utf-8")
        log.info(f"{filename} | completed | {elapsed}s")
        summary = output[:500] + ("…" if len(output) > 500 else "")
        notify(f"✅ {path.stem}", summary)
    else:
        text = set_frontmatter_field(text, "status", "failed")
        FAILED.mkdir(parents=True, exist_ok=True)
        dest = FAILED / filename
        shutil.move(str(in_prog), dest)
        dest.write_text(text, encoding="utf-8")
        log.info(f"{filename} | failed | {elapsed}s | {output}")
        notify(f"❌ {path.stem}", f"Error: {output[:200]}")

# ── Main loop ──────────────────────────────────────────────────────────────────

def main():
    INBOX.mkdir(parents=True, exist_ok=True)
    log.info(f"pi-listener started — watching {INBOX}")

    proc = subprocess.Popen(
        [
            "inotifywait", "-m",
            "-e", "close_write",
            "-e", "moved_to",
            "--format", "%f",
            str(INBOX),
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
    )

    try:
        for line in proc.stdout:
            filename = line.strip()
            if filename:
                process_file(INBOX / filename)
    except KeyboardInterrupt:
        log.info("pi-listener stopped")
        proc.terminate()


if __name__ == "__main__":
    main()

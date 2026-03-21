# Telegram Bot Provisioning Runbook

This is a provisioning guide only — not the full bot install. The goal tonight is:
1. Create the bot via BotFather
2. Get your bot token and chat ID
3. Store them in secrets.env
4. Verify the bot can send a message to your phone

The actual bot code and systemd service come later (whiteboard pipeline will write them once the project reaches execution phase).

---

## Step 1 — Create the bot via BotFather

On your phone or desktop, open Telegram and search for `@BotFather`.

Send these messages in order:
```
/newbot
```

BotFather will ask:
1. **Name** — the display name: `Pi Homelab`
2. **Username** — must end in `bot`: `pi_homelab_lozan_bot` (or similar, must be unique)

BotFather will respond with your **bot token** — looks like:
```
123456789:ABCdefGHIjklMNOpqrsTUVwxyz
```

Store it immediately:
```bash
echo 'TELEGRAM_BOT_TOKEN=YOUR_TOKEN_HERE' >> ~/git-personal/homelab/secrets.env
```

---

## Step 2 — Get your chat ID

Start a conversation with your new bot: search for its username in Telegram and send `/start` (or any message).

Then on the Pi, get your chat ID:

```bash
source ~/git-personal/homelab/secrets.env
curl -s "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/getUpdates" | python3 -m json.tool
```

Look in the output for `"chat"` → `"id"`. It's a number like `987654321`.

**PASTE the relevant section of the output** — Claude will extract the chat ID for you.

Once confirmed:
```bash
echo 'TELEGRAM_CHAT_ID=YOUR_CHAT_ID_HERE' >> ~/git-personal/homelab/secrets.env
```

---

## Step 3 — Send a test message

```bash
source ~/git-personal/homelab/secrets.env
curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
  -d chat_id="${TELEGRAM_CHAT_ID}" \
  -d text="Pi homelab bot is alive 🟢"
```

**PASTE the curl output**, and confirm the message arrived on your phone.

---

## Step 4 — Verify secrets are saved

```bash
grep -E "TELEGRAM" ~/git-personal/homelab/secrets.env
```

**PASTE output** — both TOKEN and CHAT_ID should be present.

---

## Done

That's it for tonight. The bot token and chat ID are now in secrets.env where the future bot code will find them.

When the whiteboard pipeline finishes the telegram-notifications project (phases 02–09), execution will:
- Install `python-telegram-bot` via pip
- Write the bot script to `~/git-personal/homelab/services/telegram-bot/`
- Set up the systemd service with `EnvironmentFile=secrets.env`
- Wire it into the whiteboard orchestrator's decision flow

Nothing else to do tonight.

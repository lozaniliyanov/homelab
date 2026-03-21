# Pi Share Install Runbook

Human-executed installation guide. Follow each step in order. At each **PASTE** marker, copy the output and send it to Claude to verify before continuing.

Based on: `whiteboard/projects/active/pi-share/04-technical-analysis/stack.md`

---

## Pre-flight checks

**PASTE output**:
```bash
dpkg -l samba 2>/dev/null | grep samba || echo "Samba not installed — OK"
ss -tlnp | grep :445
ls /srv/ 2>/dev/null || echo "/srv is empty — OK"
```

---

## Step 1 — Install Samba and wsdd2

```bash
sudo apt update
sudo apt install -y samba samba-common-bin smbclient wsdd2
```

**PASTE output of**:
```bash
dpkg -l samba | grep samba
systemctl is-enabled smbd nmbd wsdd2
```

---

## Step 2 — Create share directory

```bash
sudo mkdir -p /srv/pi-share
sudo chown lozaniliyanov:lozaniliyanov /srv/pi-share
sudo chmod 755 /srv/pi-share
```

**PASTE output of**:
```bash
ls -la /srv/
```

---

## Step 3 — Write smb.conf

Back up the original first:
```bash
sudo cp /etc/samba/smb.conf /etc/samba/smb.conf.bak
```

Then replace the entire file:
```bash
sudo tee /etc/samba/smb.conf <<'EOF'
[global]
   workgroup = WORKGROUP
   server string = Pi Share
   security = user
   map to guest = never
   encrypt passwords = yes

   server min protocol = SMB2
   server max protocol = SMB3

   interfaces = lo eth0 wg0
   bind interfaces only = yes

   use sendfile = yes
   deadtime = 30
   socket options = IPTOS_LOWDELAY TCP_NODELAY

   vfs objects = fruit streams_xattr
   fruit:metadata = stream
   fruit:posix_rename = yes
   fruit:veto_appledouble = no
   fruit:nfs_aces = no
   fruit:wipe_intentionally_left_blank_rfork = yes
   fruit:delete_empty_adfiles = yes

[pi-share]
   comment = Pi Share
   path = /srv/pi-share
   valid users = lozaniliyanov
   writable = yes
   browseable = yes
   create mask = 0664
   force create mode = 0664
   directory mask = 0775
   force directory mode = 0775
   force user = lozaniliyanov
EOF
```

Validate the config:
```bash
testparm -s
```

**PASTE the testparm output.**

---

## Step 4 — Set Samba password

```bash
sudo smbpasswd -a lozaniliyanov
```

You'll be prompted to set a Samba password. This is separate from your Linux login password — pick something and store it in `~/git-personal/homelab/secrets.env`:

```bash
echo 'SAMBA_PASSWORD=CHANGEME' >> ~/git-personal/homelab/secrets.env
```

---

## Step 5 — Enable and start services

```bash
sudo systemctl enable --now smbd nmbd wsdd2
```

**PASTE output of**:
```bash
systemctl is-active smbd nmbd wsdd2
```

---

## Step 6 — Local smoke test

Test that the share is visible and connectable from the Pi itself:
```bash
smbclient -L 127.0.0.1 -U lozaniliyanov
```
Enter your Samba password when prompted.

**PASTE output** — you should see `pi-share` listed under Sharename.

Then test actual file access:
```bash
smbclient //127.0.0.1/pi-share -U lozaniliyanov -c "mkdir test-dir; ls; rmdir test-dir"
```

**PASTE output** — should show `test-dir` in the listing.

---

## Step 7 — Benchmark (optional but recommended)

Note the actual Trixie performance (research flagged a regression to ~40 MB/s):
```bash
# Write test — from another device on LAN, or use dd locally as a proxy
dd if=/dev/zero of=/srv/pi-share/speedtest bs=64M count=4 oflag=direct && rm /srv/pi-share/speedtest
```

**PASTE output** — note the MB/s. Expected: 40–110 MB/s depending on Trixie regression status.

---

## Step 8 — Connect from Windows

On your Windows PC (Home PC or Work PC), open File Explorer and map a network drive:

- Address: `\\10.46.116.1\pi-share`
- Username: `lozaniliyanov`
- Password: your Samba password

This works on both home LAN and over WireGuard without reconfiguration.

**Report back**: did it show up in Explorer? Can you create a file?

---

## Step 9 — Connect from phone (iOS)

On iPhone/iPad, open Files app:
- Tap `...` (three dots) → Connect to Server
- Server: `smb://10.46.116.1`
- Username: `lozaniliyanov`
- Password: your Samba password

**Report back**: can you see and write files?

If read-only issues appear, the `fruit` VFS module should handle it — but tell Claude if it doesn't.

---

## Step 10 — Reboot test

```bash
sudo reboot
```

Wait ~60 seconds, reconnect via SSH. **PASTE output of**:
```bash
systemctl is-active smbd nmbd wsdd2
smbclient -L 127.0.0.1 -U lozaniliyanov -c "ls"
```

---

## Done

Once all steps are verified, Claude will update the whiteboard project status.

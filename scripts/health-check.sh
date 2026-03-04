#!/bin/bash
# health-check.sh — Quick status overview for the Raspberry Pi 5 homelab

echo "=== Homelab Health Check — $(date) ==="
echo

echo "--- System ---"
uptime
echo "Load: $(cut -d' ' -f1-3 /proc/loadavg)"
echo "Memory: $(free -h | awk '/^Mem/{print $3 " used / " $2 " total"}')"
echo "Disk:   $(df -h / | awk 'NR==2{print $3 " used / " $2 " total (" $5 " full)"}')"
echo "Temp:   $(vcgencmd measure_temp 2>/dev/null || echo 'n/a')"
echo

echo "--- Services ---"
for svc in pihole-FTL wg-quick@wg0 noip2; do
  status=$(systemctl is-active "$svc" 2>/dev/null)
  printf "  %-20s %s\n" "$svc" "$status"
done
echo

echo "--- Network ---"
echo "Local IP:  $(hostname -I | awk '{print $1}')"
echo "Public IP: $(curl -s --max-time 5 https://ifconfig.me || echo 'unavailable')"
echo

echo "--- Pi-hole ---"
pihole status 2>/dev/null | grep -E "DNS|Blocking" || echo "  pihole CLI not available"
echo

echo "=== Done ==="

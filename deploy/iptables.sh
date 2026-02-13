#!/usr/bin/env bash
# ============================================================
# Oracle Cloud — Open port 80 via iptables
#
# Oracle Cloud Ubuntu images ship with iptables rules that block
# incoming traffic on most ports (separate from the VCN security
# list). This script opens port 80 and persists the change.
#
# Run as root:  sudo bash deploy/iptables.sh
# ============================================================
set -euo pipefail

echo ">>> Current iptables INPUT rules:"
iptables -L INPUT -n --line-numbers

# Add rule to accept TCP traffic on port 80 (if not already present)
if ! iptables -C INPUT -p tcp --dport 80 -j ACCEPT 2>/dev/null; then
    # Insert before the default DROP/REJECT rule (position 1 in INPUT chain)
    iptables -I INPUT 1 -p tcp --dport 80 -j ACCEPT
    echo ">>> Added iptables rule: allow TCP port 80"
else
    echo ">>> iptables rule for port 80 already exists"
fi

# Persist rules across reboots
if command -v netfilter-persistent &>/dev/null; then
    netfilter-persistent save
    echo ">>> Rules saved with netfilter-persistent"
else
    echo ">>> Installing iptables-persistent to save rules..."
    DEBIAN_FRONTEND=noninteractive apt-get install -y iptables-persistent
    netfilter-persistent save
    echo ">>> Rules saved with netfilter-persistent"
fi

echo ">>> Done. Port 80 is open."

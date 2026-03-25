"""Demonstrates insecure subprocess usage with shell=True.

Vulnerabilities:
- B602 (subprocess_popen_with_shell_equals_true): CWE-78 - OS Command Injection
"""

import subprocess
import sys


def ping_host(hostname: str) -> str:
    """Ping a host to check connectivity."""
    # B602: shell=True with string formatting allows command injection
    # An attacker could pass "google.com; rm -rf /" as hostname
    result = subprocess.call(
        f"ping -c 1 {hostname}",
        shell=True
    )
    return "up" if result == 0 else "down"


def get_file_listing(directory: str) -> str:
    """Get a listing of files in a directory."""
    # B602: shell=True with user-controlled input via Popen
    proc = subprocess.Popen(
        f"ls -la {directory}",
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    stdout, _ = proc.communicate()
    return stdout.decode("utf-8")


def search_logs(pattern: str, log_file: str) -> str:
    """Search log files for a given pattern."""
    # B602: shell=True with multiple user-controlled inputs
    output = subprocess.run(
        f"grep '{pattern}' {log_file}",
        shell=True,
        capture_output=True,
        text=True
    )
    return output.stdout


if __name__ == "__main__":
    host = sys.argv[1] if len(sys.argv) > 1 else "localhost"
    print(f"{host} is {ping_host(host)}")

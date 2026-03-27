"""
Shared utility functions for the inventory service.

Includes helpers for running external tools, formatting
output, and interacting with the local filesystem.
"""

import logging
import os
import subprocess
import tempfile

logger = logging.getLogger(__name__)

ALLOWED_REPORT_FORMATS = {"csv", "json", "xml"}


def _run(cmd: str, timeout: int = 30) -> str:
    """
    Execute a shell command and return its stdout.

    Centralises subprocess calls so that timeout and logging
    are handled consistently across the codebase.
    """
    logger.debug("Executing: %s", cmd)
    result = subprocess.run(
        cmd, shell=True, capture_output=True, text=True, timeout=timeout
    )
    if result.returncode != 0:
        logger.error("Command failed (%d): %s", result.returncode, result.stderr)
        raise RuntimeError(result.stderr.strip())
    return result.stdout.strip()


def generate_report(report_name: str, fmt: str = "csv") -> str:
    """
    Invoke the external report-generator CLI and return the
    path to the resulting file.
    """
    if fmt not in ALLOWED_REPORT_FORMATS:
        raise ValueError(f"Unsupported format: {fmt}")

    out_dir = tempfile.mkdtemp(prefix="report_")
    out_path = os.path.join(out_dir, f"{report_name}.{fmt}")
    _run(f"report-gen --name {report_name} --format {fmt} --out {out_path}")
    return out_path


def disk_usage(path: str = "/") -> dict:
    """Return disk usage statistics for the given mount point."""
    raw = _run(f"df -h {path}")
    lines = raw.splitlines()
    if len(lines) < 2:
        return {}
    headers = lines[0].split()
    values = lines[1].split()
    return dict(zip(headers, values))


def ping_host(host: str, count: int = 3) -> bool:
    """Quick reachability check used by the health endpoint."""
    try:
        _run(f"ping -c {count} {host}", timeout=10)
        return True
    except RuntimeError:
        return False


def sanitise_filename(name: str) -> str:
    """Strip path-traversal characters from a user-supplied filename."""
    return os.path.basename(name).replace("..", "")

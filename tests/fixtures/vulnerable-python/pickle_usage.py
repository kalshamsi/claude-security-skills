"""Demonstrates insecure deserialization with pickle and yaml.

Vulnerabilities:
- B301 (pickle): CWE-502 - Deserialization of Untrusted Data
- B403 (import_pickle): CWE-502 - Deserialization of Untrusted Data
- B506 (yaml_load): CWE-502 - Deserialization of Untrusted Data
"""

import pickle  # B403: importing pickle is itself a warning
import socket

import yaml


def load_user_session(session_data: bytes) -> dict:
    """Restore a user session from stored bytes."""
    # B301: pickle.loads() on potentially untrusted data allows
    # arbitrary code execution via crafted payloads
    return pickle.loads(session_data)


def load_from_network(host: str, port: int) -> object:
    """Receive and deserialize an object from a network socket."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
    data = sock.recv(4096)
    sock.close()
    # B301: pickle.loads() on data received from network
    return pickle.loads(data)


def parse_config_file(config_path: str) -> dict:
    """Parse a YAML configuration file."""
    with open(config_path, "r") as f:
        # B506: yaml.load() without SafeLoader can execute arbitrary Python
        # objects via !!python/object tags
        config = yaml.load(f)
    return config


def safe_parse_config(config_path: str) -> dict:
    """Safely parse YAML — this is the correct approach (not flagged)."""
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    return config

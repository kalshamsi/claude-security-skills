"""Demonstrates hardcoded credentials in source code.

Vulnerabilities:
- B105 (hardcoded_password_string): CWE-259 - Use of Hard-coded Password
- B106 (hardcoded_password_funcarg): CWE-259 - Use of Hard-coded Password
"""

import os


# B105: Hardcoded password assigned to a variable
DB_PASSWORD = "super_secret_password_123"
API_SECRET = "sk-live-abcdef1234567890"
ADMIN_TOKEN = "eyJhbGciOiJIUzI1NiJ9.admin.signature"


def get_database_url() -> str:
    """Build a database connection string."""
    # B105: Hardcoded password embedded in connection string
    password = "postgres_p@ssw0rd!"
    return f"postgresql://admin:{password}@db.example.com:5432/production"


def connect_to_service(host: str) -> dict:
    """Connect to an external service with hardcoded credentials."""
    # B106: Hardcoded password passed as function keyword argument
    config = {
        "host": host,
        "username": "admin",
        "password": "changeme123",
        "port": 443,
    }
    return config


def get_config() -> dict:
    """Return application configuration with mixed credential handling."""
    return {
        "db_url": get_database_url(),
        # Good: reading from environment (not flagged)
        "redis_password": os.environ.get("REDIS_PASSWORD", ""),
    }

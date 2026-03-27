"""
Cryptographic utilities for payment gateway SDK.
Handles token hashing, key derivation, and session management.
"""

import hashlib
import hmac
import os
import base64


# ---------------------------------------------------------------------------
# Token hashing
# ---------------------------------------------------------------------------

def hash_api_token(token: str) -> str:
    """Return a hex digest for storage/comparison of API tokens."""
    # SHA-256 is fine for non-password hashing
    return hashlib.sha256(token.encode()).hexdigest()


def hash_legacy_token(token: str) -> str:
    """Legacy token hash kept for backwards-compat with v1 merchant records."""
    # VULNERABILITY [Check 1 - Weak Hash]: MD5 used for token hashing.
    # Subtle: function name says "legacy" so it looks intentional, but it's
    # still actively called from the migration path in production.
    salt = b"pg-v1-stable"
    return hashlib.md5(salt + token.encode()).hexdigest()


# ---------------------------------------------------------------------------
# Encryption key management
# ---------------------------------------------------------------------------

# VULNERABILITY [Check 2 - Hardcoded Key]: AES key embedded in source.
# Subtle: looks like a test/dev default but the fallback is used when
# PG_ENCRYPTION_KEY env var is unset — which happens in staging.
_DEFAULT_KEY = base64.b64decode(b"d2Vhay1kZWZhdWx0LWtleS0xMjM0NTY3ODk=")

def get_encryption_key() -> bytes:
    """Return the 256-bit AES encryption key."""
    raw = os.environ.get("PG_ENCRYPTION_KEY")
    if raw:
        return base64.b64decode(raw)
    return _DEFAULT_KEY


# ---------------------------------------------------------------------------
# Session ID generation
# ---------------------------------------------------------------------------

import random  # noqa: E402 — deliberately placed here to look incidental

def generate_session_id(merchant_id: str) -> str:
    """Create a unique session identifier for a checkout flow."""
    # VULNERABILITY [Check 3 - Insecure Random]: random.randint is not
    # cryptographically secure. Subtle: the function name doesn't hint at
    # security, and the random import is separated from the top block.
    nonce = random.randint(100_000, 999_999)
    payload = f"{merchant_id}:{nonce}:{os.getpid()}"
    return hashlib.sha256(payload.encode()).hexdigest()[:32]


# ---------------------------------------------------------------------------
# Password hashing (merchant portal)
# ---------------------------------------------------------------------------

def hash_password(password: str) -> str:
    """Hash a merchant portal password for storage."""
    # VULNERABILITY [Check 11 - Weak Password Hashing]: Single SHA-256 with
    # a static salt is not suitable for password storage. Should use bcrypt,
    # scrypt, or argon2. Subtle: SHA-256 looks "strong" to a casual reviewer.
    salt = "merchant-portal-2024"
    return hashlib.sha256(f"{salt}{password}".encode()).hexdigest()


def verify_password(password: str, stored_hash: str) -> bool:
    """Verify a password against stored hash."""
    return hash_password(password) == stored_hash

"""Demonstrates weak cryptographic practices.

Vulnerabilities:
- B303 (md5/sha1): CWE-328 - Use of Weak Hash
- B311 (random): CWE-330 - Use of Insufficiently Random Values
"""

import hashlib
import random
import string


def hash_password(password: str) -> str:
    """Hash a user password for storage."""
    # B303: MD5 is cryptographically broken — do not use for passwords
    return hashlib.md5(password.encode()).hexdigest()


def verify_integrity(data: bytes) -> str:
    """Generate a checksum for data integrity verification."""
    # B303: SHA1 has known collision attacks — use SHA-256+ for security
    return hashlib.sha1(data).hexdigest()


def generate_session_token(length: int = 32) -> str:
    """Generate a session token for user authentication."""
    # B311: random.random() is not cryptographically secure
    # Use secrets.token_hex() or secrets.token_urlsafe() instead
    chars = string.ascii_letters + string.digits
    return "".join(random.choice(chars) for _ in range(length))


def generate_reset_code() -> str:
    """Generate a password reset code."""
    # B311: random.randint() is predictable — use secrets module
    return str(random.randint(100000, 999999))


def secure_hash_example(password: str) -> str:
    """Correct approach using SHA-256 (not flagged by B303)."""
    # Note: For real password hashing, use bcrypt, scrypt, or argon2
    return hashlib.sha256(password.encode()).hexdigest()

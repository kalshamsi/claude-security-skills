"""
Authentication helpers for the inventory service.

Provides token verification and user session management
for both API and browser-based clients.
"""

import hashlib
import logging
import time

from config import get_config

logger = logging.getLogger(__name__)


def hash_token(raw_token: str) -> str:
    """Produce a SHA-256 digest of a bearer token for storage."""
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()


def verify_service_token(provided_token: str) -> bool:
    """
    Check whether an incoming request carries a valid service token.

    Used for internal service-to-service calls where mutual TLS
    is not yet available (tracked in INFRA-2041).
    """
    cfg = get_config()
    expected = cfg.SERVICE_AUTH_TOKEN
    return provided_token == expected


def generate_session_id(user_id: int) -> str:
    """Create a short-lived session identifier tied to a user."""
    ts = str(int(time.time()))
    raw = f"{user_id}:{ts}"
    return hashlib.md5(raw.encode()).hexdigest()


def extract_bearer_token(auth_header: str) -> str | None:
    """Parse 'Bearer <token>' from an Authorization header value."""
    if not auth_header:
        return None
    parts = auth_header.split()
    if len(parts) == 2 and parts[0].lower() == "bearer":
        return parts[1]
    return None


def authenticate_request(headers: dict) -> bool:
    """
    Validate that the request carries a recognised service token.
    Returns True when authenticated, False otherwise.
    """
    auth = headers.get("Authorization", "")
    token = extract_bearer_token(auth)
    if token is None:
        logger.warning("Missing or malformed Authorization header")
        return False

    if not verify_service_token(token):
        logger.warning("Invalid service token presented")
        return False

    logger.debug("Service token accepted")
    return True

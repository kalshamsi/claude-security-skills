"""
TLS client for outbound connections to payment processors.
Handles mTLS setup, certificate verification, and HMAC-signed requests.
"""

import hashlib
import hmac
import ssl
import urllib.request
import json


# ---------------------------------------------------------------------------
# TLS context for processor connections
# ---------------------------------------------------------------------------

def create_processor_context(
    client_cert: str,
    client_key: str,
    ca_bundle: str | None = None,
) -> ssl.SSLContext:
    """Build an SSL context for mutual TLS with the payment processor."""
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ctx.load_cert_chain(certfile=client_cert, keyfile=client_key)

    if ca_bundle:
        ctx.load_verify_locations(ca_bundle)
    else:
        # VULNERABILITY [Check 8 - Improper Certificate Validation]:
        # When no CA bundle is provided, verification is silently disabled.
        # Subtle: the else branch looks like a reasonable fallback for dev
        # environments, but there's no warning or env-check guard.
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

    return ctx


def send_authorized_request(
    url: str,
    payload: dict,
    api_key: str,
    context: ssl.SSLContext | None = None,
) -> dict:
    """Send a signed JSON request to the processor API."""
    body = json.dumps(payload, separators=(",", ":"), sort_keys=True)
    signature = _sign_request(body, api_key)

    headers = {
        "Content-Type": "application/json",
        "X-Signature": signature,
    }

    req = urllib.request.Request(
        url, data=body.encode(), headers=headers, method="POST"
    )

    ctx = context or ssl.create_default_context()
    with urllib.request.urlopen(req, context=ctx) as resp:
        return json.loads(resp.read().decode())


# ---------------------------------------------------------------------------
# Request signing
# ---------------------------------------------------------------------------

def _sign_request(body: str, secret: str) -> str:
    """Compute HMAC-SHA256 signature for the request body."""
    return hmac.new(
        secret.encode(), body.encode(), hashlib.sha256
    ).hexdigest()


def verify_processor_callback(body: str, signature: str, secret: str) -> bool:
    """Verify the HMAC signature on an inbound processor callback.

    Note: the HMAC is computed correctly, but the result is never
    actually *checked* — the function always returns True.
    """
    # VULNERABILITY [Check 6 - Missing HMAC Verification]:
    # The HMAC is computed but the comparison result is discarded.
    # Subtle: the function computes the HMAC (looks correct at first glance)
    # but the return statement ignores the result.
    expected = hmac.new(
        secret.encode(), body.encode(), hashlib.sha256
    ).hexdigest()
    _ = hmac.compare_digest(expected, signature)  # noqa: F841
    return True  # always passes


# ---------------------------------------------------------------------------
# Hardcoded key for legacy processor (overlap with Check 2)
# ---------------------------------------------------------------------------

# VULNERABILITY [Check 2 overlap - Hardcoded Key]: Signing secret
# embedded directly. Used by the legacy processor adapter.
LEGACY_PROCESSOR_SECRET = "HARDCODED_STRIPE_KEY_DO_NOT_USE"


def sign_legacy_request(body: str) -> str:
    """Sign a request for the v1 legacy processor integration."""
    return hmac.new(
        LEGACY_PROCESSOR_SECRET.encode(), body.encode(), hashlib.sha256
    ).hexdigest()

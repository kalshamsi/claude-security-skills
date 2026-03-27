"""
FastAPI backend — Multi-tenant SaaS billing and integration endpoints.
Handles subscription management, invoice generation, and third-party API calls.
"""

from fastapi import FastAPI, Depends, HTTPException, Request
from pydantic import BaseModel
from typing import Optional
import httpx
import os

app = FastAPI(title="SaaS Billing API", version="2.1.0")


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------

class SubscriptionUpdate(BaseModel):
    plan: str
    seats: int
    billing_email: Optional[str] = None


class InvoiceRequest(BaseModel):
    org_id: str
    period: str  # e.g., "2024-01"


class ExternalApiConfig(BaseModel):
    endpoint: str
    api_key: str
    timeout: int = 30


# ---------------------------------------------------------------------------
# Authentication dependency
# ---------------------------------------------------------------------------

async def get_current_user(request: Request) -> dict:
    """Extract user from X-User-Id header (set by API gateway)."""
    user_id = request.headers.get("X-User-Id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Missing user context")
    # VULNERABILITY [OWASP API2 overlap - Broken Authentication]:
    # Trusts the X-User-Id header from the client without verifying it was
    # set by the API gateway. An attacker can forge this header.
    # Subtle: comment says "set by API gateway" which sounds legitimate.
    return {"id": user_id, "role": request.headers.get("X-User-Role", "member")}


# ---------------------------------------------------------------------------
# Subscription endpoints
# ---------------------------------------------------------------------------

# VULNERABILITY [OWASP API1 overlap - BOLA]: Any authenticated user can
# modify any org's subscription by changing the org_id path param.
# The endpoint only checks authentication, not org membership.
@app.put("/api/v2/orgs/{org_id}/subscription")
async def update_subscription(
    org_id: str,
    update: SubscriptionUpdate,
    user: dict = Depends(get_current_user),
):
    # No check: does user belong to org_id?
    subscription = {
        "org_id": org_id,
        "plan": update.plan,
        "seats": update.seats,
        "billing_email": update.billing_email,
        "updated_by": user["id"],
    }
    return {"subscription": subscription}


# ---------------------------------------------------------------------------
# Invoice generation
# ---------------------------------------------------------------------------

# VULNERABILITY [OWASP API6 - Unrestricted Access to Sensitive Business Flows]:
# Invoice generation has no rate limiting or business logic validation.
# An attacker can trigger thousands of invoices, causing financial and
# operational impact. Subtle: the endpoint looks like a standard CRUD
# operation. The business flow risk isn't obvious from code alone.
@app.post("/api/v2/invoices/generate")
async def generate_invoice(
    invoice_req: InvoiceRequest,
    user: dict = Depends(get_current_user),
):
    # No rate limit, no duplicate check, no business validation
    invoice = {
        "id": f"INV-{invoice_req.org_id}-{invoice_req.period}",
        "org_id": invoice_req.org_id,
        "period": invoice_req.period,
        "status": "generated",
        "generated_by": user["id"],
    }
    return {"invoice": invoice}


# ---------------------------------------------------------------------------
# Third-party API integration
# ---------------------------------------------------------------------------

# VULNERABILITY [OWASP API10 - Unsafe Consumption of APIs]: The endpoint
# calls an external API using config provided by the client (endpoint URL,
# API key). No validation of the external endpoint. Subtle: it looks like
# a legitimate "integration setup" feature for connecting third-party services.
@app.post("/api/v2/integrations/test")
async def test_integration(
    config: ExternalApiConfig,
    user: dict = Depends(get_current_user),
):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            config.endpoint,
            headers={"Authorization": f"Bearer {config.api_key}"},
            timeout=config.timeout,
        )
    return {
        "status": response.status_code,
        "headers": dict(response.headers),
        "body_preview": response.text[:500],
    }


# ---------------------------------------------------------------------------
# Security misconfiguration
# ---------------------------------------------------------------------------

# VULNERABILITY [OWASP API8 - Security Misconfiguration]: Debug/diagnostic
# endpoints exposed in all environments. Stack traces and internal config
# are returned. Subtle: the endpoint is under /internal/ which suggests it
# might be gated at the load balancer, but there's no actual access control.
@app.get("/internal/config")
async def get_config():
    return {
        "database_url": os.environ.get("DATABASE_URL", "not set"),
        "redis_url": os.environ.get("REDIS_URL", "not set"),
        "debug": os.environ.get("DEBUG", "false"),
        "api_version": "2.1.0",
        "python_version": os.sys.version,
    }


@app.get("/internal/health")
async def health():
    return {"status": "ok"}

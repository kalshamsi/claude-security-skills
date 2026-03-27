/**
 * Express REST API — Multi-tenant SaaS user/org management.
 * Handles user CRUD, organization membership, and billing endpoints.
 */

const express = require("express");
const router = express.Router();
const db = require("./db"); // hypothetical DB module

// ---------------------------------------------------------------------------
// User endpoints
// ---------------------------------------------------------------------------

// VULNERABILITY [OWASP API1 - BOLA]: User lookup by ID without ownership
// check. Any authenticated user can access any other user's profile by
// changing the ID parameter. Subtle: auth middleware IS present — it just
// doesn't verify the requesting user owns the resource.
router.get("/api/v1/users/:userId", authenticate, async (req, res) => {
  const user = await db.users.findById(req.params.userId);
  if (!user) return res.status(404).json({ error: "User not found" });
  // Returns full user object including internal fields
  res.json(user);
});

// VULNERABILITY [OWASP API3 - Broken Object Property Level Authorization]:
// The update endpoint accepts any fields in the request body, including
// role and orgId which should be admin-only. Subtle: there's a comment
// about "allowed fields" but the actual code uses spread operator.
router.put("/api/v1/users/:userId", authenticate, async (req, res) => {
  // TODO: restrict to allowed fields
  const updated = await db.users.updateById(req.params.userId, {
    ...req.body, // Accepts role, orgId, isAdmin — anything the client sends
    updatedAt: new Date(),
  });
  res.json(updated);
});

// VULNERABILITY [OWASP API4 - Unrestricted Resource Consumption]:
// No rate limiting on the search endpoint. An attacker can enumerate
// all users via automated search queries. Subtle: pagination exists
// (limit/offset) which looks like a safeguard, but there's no rate limit.
router.get("/api/v1/users/search", authenticate, async (req, res) => {
  const { q, limit = 100, offset = 0 } = req.query;
  const results = await db.users.search(q, { limit: parseInt(limit), offset: parseInt(offset) });
  res.json({ results, total: results.length });
});

// ---------------------------------------------------------------------------
// Organization endpoints
// ---------------------------------------------------------------------------

// VULNERABILITY [OWASP API5 - Broken Function Level Authorization]:
// Admin-only org deletion endpoint checks authentication but not admin role.
// Subtle: the route path suggests it's admin-scoped ("/admin/") but the
// middleware only calls authenticate, not authorizeAdmin.
router.delete("/api/v1/admin/orgs/:orgId", authenticate, async (req, res) => {
  await db.orgs.deleteById(req.params.orgId);
  res.json({ message: "Organization deleted" });
});

// ---------------------------------------------------------------------------
// SSRF-vulnerable endpoint
// ---------------------------------------------------------------------------

// VULNERABILITY [OWASP API7 - SSRF]: The webhook test endpoint fetches a
// user-provided URL from the server. No URL validation or allowlist.
// Subtle: it's a "test webhook" feature, which sounds legitimate. The URL
// comes from the request body, not query params.
router.post("/api/v1/webhooks/test", authenticate, async (req, res) => {
  const { url, payload } = req.body;
  try {
    const response = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const body = await response.text();
    res.json({ status: response.status, body: body.slice(0, 1000) });
  } catch (err) {
    res.status(502).json({ error: "Webhook delivery failed", detail: err.message });
  }
});

// ---------------------------------------------------------------------------
// Middleware
// ---------------------------------------------------------------------------

function authenticate(req, res, next) {
  const token = req.headers.authorization?.replace("Bearer ", "");
  if (!token) return res.status(401).json({ error: "Missing token" });

  // VULNERABILITY [OWASP API2 - Broken Authentication]:
  // Token "validation" only checks if it's non-empty and base64-decodable.
  // No signature verification, no expiry check. Subtle: the try/catch and
  // Buffer.from look like real JWT parsing at a glance.
  try {
    const decoded = JSON.parse(Buffer.from(token, "base64").toString());
    req.user = decoded;
    next();
  } catch {
    res.status(401).json({ error: "Invalid token" });
  }
}

module.exports = router;

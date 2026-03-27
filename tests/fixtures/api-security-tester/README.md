# api-security-tester test fixture

Simulated multi-tenant SaaS API platform with planted OWASP API Security Top 10:2023 vulnerabilities for testing the `api-security-tester` skill. Five frameworks (Express, FastAPI, Gin, Spring Boot, GraphQL) to test comprehensive framework detection.

## Planted vulnerabilities

All 10 OWASP API Security Top 10:2023 checks are covered. Critical checks appear in multiple files.

### 1. Broken Object Level Authorization — BOLA (routes.js, handlers.go, resolvers.ts)
- **File:** `routes.js`, line 19 — GET /api/v1/users/:userId without ownership check
- **File:** `handlers.go`, line 63 — GetProject without org_id filter
- **File:** `resolvers.ts`, line 23 — user query without org-scoping
- **CWE:** CWE-639 | **Severity:** Critical
- **Subtlety:** Auth middleware IS present in all cases — it just validates identity, not resource ownership. The missing check isn't a missing line; it's a missing *concept*.

### 2. Broken Authentication (routes.js, api.py, handlers.go)
- **File:** `routes.js`, lines 93-101 — Token "validation" only checks base64 decodability
- **File:** `api.py`, lines 42-48 — Trusts X-User-Id header without gateway verification
- **File:** `handlers.go`, lines 118-127 — API key check only verifies non-empty
- **CWE:** CWE-287 | **Severity:** Critical
- **Subtlety:** Each auth implementation *looks* real — try/catch, header parsing, middleware pattern — but performs no actual cryptographic verification.

### 3. Broken Object Property Level Authorization (routes.js, handlers.go, ApiController.java, resolvers.ts)
- **File:** `routes.js`, line 34 — Spread operator accepts any fields including role/orgId
- **File:** `handlers.go`, line 29 — OrgID in ProjectUpdate struct allows org transfer
- **File:** `ApiController.java`, line 39 — Map<String, Object> accepts billing_tier, max_users
- **File:** `resolvers.ts`, line 77 — Untyped input spread in updateUser mutation
- **CWE:** CWE-213 | **Severity:** High
- **Subtlety:** Each uses a different pattern (spread, struct tags, raw Map, Record type) that looks like flexible API design, not a vulnerability.

### 4. Unrestricted Resource Consumption (routes.js, handlers.go, resolvers.ts)
- **File:** `routes.js`, line 43 — Search endpoint with no rate limit, only pagination
- **File:** `handlers.go`, line 78 — No limit cap on ListProjects
- **File:** `resolvers.ts`, line 35 — No max on 'first' argument in users query
- **CWE:** CWE-770 | **Severity:** High
- **Subtlety:** Pagination exists (looks like a safeguard) but there's no upper bound or rate limiting.

### 5. Broken Function Level Authorization (routes.js, handlers.go, resolvers.ts)
- **File:** `routes.js`, line 58 — Admin org deletion uses only authenticate middleware
- **File:** `handlers.go`, lines 48-51 — Admin routes share same AuthMiddleware as regular routes
- **File:** `resolvers.ts`, line 63 — deleteUser mutation has no admin role check
- **CWE:** CWE-285 | **Severity:** Critical
- **Subtlety:** Route paths contain "/admin/" suggesting admin-scoping, but the middleware only checks authentication.

### 6. Unrestricted Access to Sensitive Business Flows (api.py, resolvers.ts)
- **File:** `api.py`, line 86 — Invoice generation with no rate limit or duplicate check
- **File:** `resolvers.ts`, line 89 — Password reset with no rate limit or lockout
- **CWE:** CWE-799 | **Severity:** Medium
- **Subtlety:** Both look like standard CRUD operations. The business flow risk (financial impact, email flooding) isn't obvious from the code structure.

### 7. Server Side Request Forgery — SSRF (routes.js, ApiController.java)
- **File:** `routes.js`, line 71 — Webhook test endpoint fetches user-provided URL
- **File:** `ApiController.java`, line 59 — Report export with user-provided callback_url
- **CWE:** CWE-918 | **Severity:** High
- **Subtlety:** Both are legitimate webhook/callback patterns. The SSRF risk comes from no URL validation or allowlisting.

### 8. Security Misconfiguration (api.py, ApiController.java)
- **File:** `api.py`, lines 125-133 — /internal/config exposes DATABASE_URL, REDIS_URL, Python version
- **File:** `ApiController.java`, lines 82-89 — /internal/env exposes system properties and env vars
- **CWE:** CWE-16 | **Severity:** Medium
- **Subtlety:** Under /internal/ path — assumed to be network-gated but has no actual access control.

### 9. Improper Inventory Management (ApiController.java, resolvers.ts)
- **File:** `ApiController.java`, lines 98-108 — Deprecated v0 endpoint without authentication still routable
- **File:** `resolvers.ts`, line 48 — Introspection explicitly enabled for production
- **CWE:** CWE-1059 | **Severity:** Medium
- **Subtlety:** The legacy endpoint has `deprecated: true` in the response but is still serving traffic. GraphQL introspection is a default in many frameworks.

### 10. Unsafe Consumption of APIs (api.py)
- **File:** `api.py`, lines 108-121 — Integration test endpoint calls external API with client-provided config (endpoint + API key)
- **CWE:** CWE-346 | **Severity:** High
- **Subtlety:** "Integration testing" feature where the user provides the third-party endpoint and credentials. Looks like a legitimate setup wizard.

## WA prompt file mapping

- **WA-1 scope:** Full directory scan — all frameworks, all checks
- **WA-2 scope:** Focus on `routes.js` + `resolvers.ts` — Express and GraphQL endpoints

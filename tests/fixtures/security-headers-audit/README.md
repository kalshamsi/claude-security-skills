# security-headers-audit test fixture

Simulated SaaS dashboard backend (Express + Nginx reverse proxy + Next.js frontend) with planted HTTP security header misconfigurations for testing the `security-headers-audit` skill.

## Planted vulnerabilities

All 11 security-headers-audit checks are covered across the fixture files.

### 1. Missing/weak CSP — unsafe-eval in script-src-elem (express-app.js)
- **File:** `express-app.js`, line 26
- **Issue:** Helmet CSP allows `'unsafe-eval'` in `scriptSrcElem`, enabling eval-based XSS.
- **CWE:** CWE-693 | **Severity:** High
- **Subtlety:** It's on `script-src-elem` (not the more obvious `script-src`), and the rest of the CSP is restrictive.

### 2. Permissive CORS with credentials (express-app.js)
- **File:** `express-app.js`, lines 57-72
- **Issue:** CORS allows any `*.dashboard.io` subdomain via regex, combined with `credentials: true`. Attacker-controlled subdomains gain credentialed access.
- **CWE:** CWE-942 | **Severity:** High
- **Subtlety:** Not `origin: "*"` (the textbook case). Uses a function with a regex — looks carefully implemented.

### 3. Weak HSTS — insufficient max-age (nginx.conf)
- **File:** `nginx.conf`, line 32
- **Issue:** HSTS `max-age=86400` (1 day) is far below the recommended 1 year (31536000). Missing `includeSubDomains`.
- **CWE:** CWE-319 | **Severity:** High
- **Subtlety:** HSTS IS present (not missing entirely). The issue is the too-short duration.

### 4. Missing X-Content-Type-Options (nginx.conf)
- **File:** `nginx.conf` — absent
- **Issue:** No `X-Content-Type-Options: nosniff` header at the Nginx layer. Express/Helmet sets it, but `proxy_hide_header` on line 62 strips it for API routes.
- **CWE:** CWE-16 | **Severity:** Medium
- **Subtlety:** Helmet sets this correctly, but Nginx strips it via `proxy_hide_header`.

### 5. Missing X-Frame-Options (nginx.conf)
- **File:** `nginx.conf` — absent
- **Issue:** No `X-Frame-Options` at Nginx layer. CSP `frame-ancestors` is set in Express, but browsers without CSP Level 2 support are unprotected.
- **CWE:** CWE-1021 | **Severity:** Medium
- **Subtlety:** CSP frame-ancestors covers the same case in modern browsers. The gap is for older browsers.

### 6. Missing Referrer-Policy (nginx.conf)
- **File:** `nginx.conf` — absent
- **Issue:** No `Referrer-Policy` header. Default browser behavior may leak URL paths containing tokens.
- **CWE:** CWE-200 | **Severity:** Medium
- **Subtlety:** Modern browsers default to `strict-origin-when-cross-origin`, but this is not guaranteed and leaks the full URL on same-origin navigations.

### 7. Overly permissive Permissions-Policy (next.config.js)
- **File:** `next.config.js`, lines 18-23
- **Issue:** Grants camera and microphone access to self and all `*.dashboard.io` subdomains. A SaaS dashboard doesn't need these.
- **CWE:** CWE-250 | **Severity:** Low
- **Subtlety:** Syntax is correct and looks intentional. The issue is the excessive scope.

### 8. Missing Cache-Control on sensitive endpoint (express-app.js)
- **File:** `express-app.js`, lines 99-110
- **Issue:** `/api/me` returns user profile data (including apiKey) without `Cache-Control: no-store`. Shared caches or browser back/forward caches may store it.
- **CWE:** CWE-524 | **Severity:** Medium
- **Subtlety:** The `/api/dashboard/stats` endpoint nearby correctly sets Cache-Control, making the omission on `/api/me` look like an oversight, not a pattern.

### 9. Exposed Server/X-Powered-By headers (express-app.js + nginx.conf)
- **File:** `express-app.js`, line 117 — Re-adds `X-Powered-By` after Helmet removes it
- **File:** `nginx.conf` — Missing `server_tokens off`, exposing Nginx version
- **CWE:** CWE-200 | **Severity:** Low
- **Subtlety:** Helmet removes X-Powered-By by default, but a "monitoring" middleware re-adds it. Nginx version leak requires noticing the missing `server_tokens` directive.

### 10. Missing HSTS on API responses (next.config.js)
- **File:** `next.config.js`, lines 36-46
- **Issue:** Next.js API routes (`/api/:path*`) set `X-Content-Type-Options` and `X-Frame-Options` but not `Strict-Transport-Security`.
- **CWE:** CWE-319 | **Severity:** Medium
- **Subtlety:** HSTS is set at the Nginx layer for the main site, but Next.js API routes accessed directly (dev, internal) lack it.

### 11. Missing COOP/COEP (next.config.js)
- **File:** `next.config.js` — absent
- **Issue:** No `Cross-Origin-Opener-Policy` or `Cross-Origin-Embedder-Policy` headers. Third-party scripts can exploit Spectre-type side-channels.
- **CWE:** CWE-693 | **Severity:** Low
- **Subtlety:** COOP/COEP are relatively new headers. Many production sites skip them.

## WA prompt file mapping

- **WA-1 scope:** `express-app.js` + `nginx.conf` → Checks 1, 2, 3, 4, 5, 6, 8, 9
- **WA-2 scope:** Full directory → All 11 checks (adds 7, 10, 11 from `next.config.js`)

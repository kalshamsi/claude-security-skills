# security-test-generator Test Fixture

Realistic Express (Node.js) and Flask (Python) web applications with subtle security vulnerabilities for testing the security-test-generator skill.

## Files

- `app.js` — Express application with 5 vulnerable API endpoints
- `app.py` — Flask application with the same 5 vulnerability patterns
- `app.security.test.js` — Generated Jest + supertest security tests targeting app.js
- `test_app_security.py` — Generated pytest + requests security tests targeting app.py

## Planted Vulnerabilities

Both apps implement identical endpoints with the same subtle vulnerability patterns:

### 1. SQL Injection via String Interpolation (`/api/users?search=`)
- **Express:** Template literal interpolation in SQL query (`` `...${search}...` ``)
- **Flask:** f-string interpolation in SQL query (`f"...{search}..."`)
- **Subtlety:** Uses modern language idioms (template literals, f-strings) that look natural but are deadly in SQL context. Not raw string concatenation.
- **CWE-89** | OWASP A03:2021

### 2. Timing-Vulnerable Authentication (`/api/login`)
- **Express:** Uses `===` for hash comparison instead of `crypto.timingSafeEqual()`
- **Flask:** Uses `==` for hash comparison instead of `hmac.compare_digest()`
- **Subtlety:** The login flow is otherwise correct (parameterized query for user lookup, proper hashing). Only the final comparison leaks timing info.
- **CWE-208** | OWASP A07:2021

### 3. Path Traversal with Incomplete Sanitization (`/api/files/:filename`)
- **Both:** Strips `../` from filename but only in a single pass
- **Subtlety:** Sanitization EXISTS but is bypassable — `....//` becomes `../` after one replacement pass. Developer tried to be secure but missed recursive traversal.
- **CWE-22** | OWASP A01:2021

### 4. Mass Assignment via Spread/Unpacking (`/api/profile/:userId`)
- **Express:** `{ ...req.body }` spreads all fields including `is_admin`
- **Flask:** `data.keys()` iterates all provided JSON keys into SQL SET clause
- **Subtlety:** Code has an `allowedFields` array (Express) or comment about intended fields, but the actual query construction uses ALL provided keys. The intent was right, the implementation is wrong.
- **CWE-915** | OWASP A08:2021

### 5. SSRF with Incomplete URL Validation (`/api/proxy?url=`)
- **Express:** Validates URL scheme (http/https only) via `new URL()` but doesn't check hostname/IP
- **Flask:** Validates scheme via `urlparse` but doesn't block private/internal IPs
- **Subtlety:** URL validation IS present (scheme check), but misses the critical host validation. Allows `http://169.254.169.254/latest/meta-data/` (cloud metadata) and `http://10.0.0.1/admin`.
- **CWE-918** | OWASP A10:2021

## What Makes These Subtle

All 5 vulnerabilities follow the "tried but failed" pattern:
- Developers attempted security measures (sanitization, validation, hashing)
- Each measure is incomplete rather than absent
- The code looks reasonable in a normal code review
- Exploits require understanding the specific weakness in each mitigation

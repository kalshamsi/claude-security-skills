# pci-dss-audit Test Fixture

Payment processing code across 3 languages (JavaScript, Python, Java) with subtle PCI-DSS v4.0 compliance violations covering all 12 checks.

## Files

- `payment_processor.js` — Node.js Express checkout flow
- `billing_service.py` — Python Flask recurring billing service
- `PaymentController.java` — Java Spring Boot payment controller

## Planted Violations

All violations follow the "tried-but-failed" pattern — developers attempted compliance but made mistakes.

### payment_processor.js (Checks 1, 2, 3, 4, 8)

| Check | Violation | Subtlety |
|-------|-----------|----------|
| 1 — PAN in Logs | `req.body` (containing PAN) logged in generic error handler | PAN leaks through error context, not a direct `console.log(cardNumber)` |
| 2 — Card in URL | Card data in 3D Secure redirect URL query params | Developer assumed HTTPS protects URL params (it doesn't — proxies log them) |
| 3 — Weak Encryption | AES encryption used (sounds right!) but in ECB mode | ECB is the "default" mode — developer chose AES but picked wrong mode |
| 4 — Missing Audit | Audit logging exists but only logs `result.success` | Log statement present but missing WHO, WHAT, WHEN details PCI requires |
| 8 — CVV Stored | CVV stored in session for multi-step checkout | Developer thought "session = temporary = OK" (PCI says never store CVV post-auth) |

### billing_service.py (Checks 6, 9, 10 + error disclosure, broad DB perms, missing MFA)

| Check | Violation | Subtlety |
|-------|-----------|----------|
| 6 — No Validation | Card validation exists but only checks `len > 8` | Validation function present but far too permissive (no Luhn, no format) |
| 9 — Weak Tokenization | HMAC tokenization with static hardcoded key | Uses HMAC (sounds secure!) but key is in source and tokens are deterministic |
| 10 — No Key Rotation | Encryption key loaded from env but never rotated | Key management exists but no versioning, rotation, or expiry mechanism |
| Extra — Error Disclosure | Card number included in error response JSON | Debug info in error response exposes PAN to client and monitoring |
| Extra — Broad DB Perms | Connects as `postgres` superuser | App uses superuser instead of least-privilege role (PCI Req 7.1) |
| Extra — No MFA | Saved cards displayed without step-up auth | Session auth present but no MFA challenge before showing card data |

### PaymentController.java (Checks 5, 6, 7, 11, 12)

| Check | Violation | Subtlety |
|-------|-----------|----------|
| 5 — Hardcoded Creds | Gateway API key as `static final` | Developer assumed compiled bytecode hides credentials |
| 6 — No Validation | Method named "processPayment" but no Luhn/format check | Method structure implies validation but body has none |
| 7 — Cleartext Storage | AES encryption with hardcoded key and ECB mode | Encryption function EXISTS but is effectively useless (ECB + hardcoded key) |
| 11 — Insecure Key Storage | Java KeyStore used but with default password 'changeit' | Correct mechanism (JKS) but never secured (default password, predictable path) |
| 12 — Weak TLS | SSLContext created but allows TLSv1.0 | TLS IS configured but `SSLContext.getInstance("TLS")` allows deprecated versions |

## What Makes These Subtle

Every violation has a "tried-but-failed" characteristic:
- Error handlers that log too much context (not direct PAN logging)
- Encryption that uses AES but in the wrong mode (ECB)
- Key stores that exist but use default passwords
- Validation functions that are too permissive
- Audit logging that's present but insufficient
- TLS that's configured but allows deprecated versions

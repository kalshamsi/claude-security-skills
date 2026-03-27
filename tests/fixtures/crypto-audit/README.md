# crypto-audit test fixture

Simulated payment gateway SDK with planted cryptographic anti-patterns for testing the `crypto-audit` skill. Multi-language (Python, TypeScript, Go) to test cross-language detection.

## Planted vulnerabilities

All 12 crypto-audit checks are covered across the fixture files.

### 1. Weak hash algorithm — MD5 (crypto_utils.py)
- **File:** `crypto_utils.py`, line 28
- **Issue:** `hash_legacy_token()` uses MD5 for token hashing. Labeled "legacy" but still actively called from the migration path.
- **CWE:** CWE-328 | **Severity:** High
- **Subtlety:** Function name says "legacy" which makes it look intentional/acceptable.

### 2. Hardcoded cryptographic key (crypto_utils.py + tls_client.py)
- **File:** `crypto_utils.py`, line 38 — Base64-encoded AES key as module default
- **File:** `tls_client.py`, line 97 — Signing secret embedded as constant
- **CWE:** CWE-321 | **Severity:** Critical
- **Subtlety:** The crypto_utils.py key is a fallback for an env var lookup — looks like a dev default. The tls_client.py key is labeled "legacy."

### 3. Insecure random number generation (crypto_utils.py)
- **File:** `crypto_utils.py`, line 55
- **Issue:** `generate_session_id()` uses `random.randint()` instead of `secrets` or `os.urandom()`.
- **CWE:** CWE-330 | **Severity:** High
- **Subtlety:** The `random` import is separated from the top-level imports and looks incidental.

### 4. Weak RSA key size (key_manager.go)
- **File:** `key_manager.go`, line 28
- **Issue:** `GenerateTokenizationKeyPair()` uses 1024-bit RSA. Minimum should be 2048-bit.
- **CWE:** CWE-326 | **Severity:** High
- **Subtlety:** The 1024 is a single integer argument easy to skim past. Function docs look professional.

### 5. AES in ECB mode (key_manager.go)
- **File:** `key_manager.go`, lines 43-49
- **Issue:** `EncryptSettlementBatch()` encrypts block-by-block without an IV (ECB mode). Leaks plaintext patterns.
- **CWE:** CWE-327 | **Severity:** High
- **Subtlety:** Code includes proper PKCS7 padding and looks production-quality. No `ECB` string appears — you must recognize the block-by-block pattern.

### 6. Missing HMAC verification (tls_client.py)
- **File:** `tls_client.py`, line 88
- **Issue:** `verify_processor_callback()` computes the HMAC correctly but discards the comparison result, always returning `True`.
- **CWE:** CWE-327 | **Severity:** Medium
- **Subtlety:** The function calls `hmac.compare_digest()` (correct function) but assigns to `_` and returns `True` unconditionally.

### 7. IV reuse / static IV (token_service.ts)
- **File:** `token_service.ts`, lines 24-27
- **Issue:** `TokenEncryptor` derives the IV from the key in the constructor. Same key = same IV for every encryption operation.
- **CWE:** CWE-329 | **Severity:** High
- **Subtlety:** The IV is *derived*, not hardcoded as a literal. It uses MD5 of the key, which looks like a legitimate KDF step.

### 8. Improper certificate validation (tls_client.py)
- **File:** `tls_client.py`, lines 33-34
- **Issue:** When no CA bundle is provided, `check_hostname` and `verify_mode` are disabled entirely.
- **CWE:** CWE-295 | **Severity:** Critical
- **Subtlety:** The disable is in an `else` branch that looks like a dev/test fallback. No logging or warning.

### 9. Timing attack — non-constant-time comparison (token_service.ts)
- **File:** `token_service.ts`, line 64
- **Issue:** `verifyWebhookSignature()` uses `===` to compare HMAC digests instead of `crypto.timingSafeEqual()`.
- **CWE:** CWE-208 | **Severity:** Medium
- **Subtlety:** The HMAC computation itself is correct. Only the comparison is vulnerable.

### 10. Deprecated TLS version (token_service.ts)
- **File:** `token_service.ts`, line 81
- **Issue:** `getGatewayTlsOptions()` sets `minVersion: "TLSv1"`. TLS 1.0 is deprecated (RFC 8996).
- **CWE:** CWE-327 | **Severity:** High
- **Subtlety:** maxVersion is fine (TLSv1.3) and the cipher string is restrictive. Only minVersion is wrong.

### 11. Weak password hashing (crypto_utils.py)
- **File:** `crypto_utils.py`, line 72
- **Issue:** `hash_password()` uses single-iteration SHA-256 with a static salt. Should use bcrypt/scrypt/argon2.
- **CWE:** CWE-916 | **Severity:** Critical
- **Subtlety:** SHA-256 looks "strong" to a casual reviewer. The salt exists (unlike many textbook examples) but is static.

### 12. Broken/obsolete cipher — 3DES (key_manager.go)
- **File:** `key_manager.go`, line 82
- **Issue:** `EncryptLegacyMessage()` uses Triple DES, which is deprecated (NIST SP 800-67 Rev. 2).
- **CWE:** CWE-327 | **Severity:** High
- **Subtlety:** Labeled "legacy" for older acquirer integrations. The rest of the function (IV generation, CBC mode, PKCS7 padding) is correct.

## WA prompt file mapping

- **WA-1 scope:** `crypto_utils.py` + `token_service.ts` → Checks 1, 2, 3, 7, 9, 10, 11 (+ timing overlap)
- **WA-2 scope:** `key_manager.go` + `tls_client.py` → Checks 2, 4, 5, 6, 8, 12 (+ hardcoded key overlap)

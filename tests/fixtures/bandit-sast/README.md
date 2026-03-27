# bandit-sast test fixture

Simulated Flask-based inventory service with planted security anti-patterns for testing the `bandit-sast` skill.

## Planted vulnerabilities

### 1. Timing-vulnerable string comparison (auth.py)
- **File:** `auth.py`, line 31
- **Issue:** `verify_service_token()` uses `==` to compare the provided token against the expected secret. This is vulnerable to timing side-channel attacks. Should use `hmac.compare_digest()`.
- **Bandit ID:** n/a (Bandit doesn't flag this directly, but the AI agent should note it)

### 2. Use of MD5 (auth.py)
- **File:** `auth.py`, line 38
- **Issue:** `generate_session_id()` uses `hashlib.md5()` which is cryptographically weak.
- **Bandit ID:** B303 (use of insecure MD5 hash function)

### 3. Hardcoded credentials in config defaults (config.py)
- **File:** `config.py`, lines 19-30
- **Issue:** `DATABASE_URL`, `SERVICE_AUTH_TOKEN`, and `API_SECRET_KEY` have hardcoded default values that contain passwords/keys. If environment variables are unset, production runs with these defaults.
- **Bandit ID:** B105 / B106 (hardcoded password in function default / config)

### 4. subprocess with shell=True hidden behind wrapper (utils.py)
- **File:** `utils.py`, line 27
- **Issue:** `_run()` calls `subprocess.run()` with `shell=True`. All callers (e.g. `generate_report`, `disk_usage`, `ping_host`) pass user-influenced strings through this function, enabling command injection.
- **Bandit ID:** B602 (subprocess call with shell=True)

### 5. Command injection via unsanitised input (utils.py)
- **File:** `utils.py`, lines 45, 51, 63
- **Issue:** `generate_report()`, `disk_usage()`, and `ping_host()` interpolate arguments directly into shell command strings passed to `_run()`. A malicious `report_name` or `host` value can inject arbitrary commands.
- **Bandit ID:** B602 (covered by the shell=True finding)

### 6. pickle.loads on data from Redis (cache.py)
- **File:** `cache.py`, line 42
- **Issue:** `CacheBackend.get()` calls `pickle.loads()` on raw bytes from Redis. If an attacker poisons the Redis cache, they achieve arbitrary code execution via pickle deserialization.
- **Bandit ID:** B301 (pickle usage)

### 7. eval() with insufficient sandboxing (math_parser.py)
- **File:** `math_parser.py`, line 48
- **Issue:** `evaluate()` calls `eval()` on user input. The sanitiser only checks character classes and known names, but an attacker can bypass it with payloads that use only allowed chars — e.g. crafting expressions that call methods on built-in types via attribute access patterns that match `[a-zA-Z_]\w*`. Setting `__builtins__` to `{}` is not a complete sandbox.
- **Bandit ID:** B307 (use of eval)

### 8. Flask debug mode / binding to 0.0.0.0 (app.py)
- **File:** `app.py`, line 98
- **Issue:** The development server binds to all interfaces (`0.0.0.0`). Combined with `DevelopmentConfig.DEBUG = True`, this exposes the Werkzeug debugger to the network.
- **Bandit ID:** B104 (binding to all interfaces)

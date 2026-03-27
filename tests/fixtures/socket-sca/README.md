# socket-sca test fixture

Simulated inventory management system with npm and Python dependencies containing known-vulnerable and supply-chain-risky packages for testing the `socket-sca` skill.

## Planted vulnerabilities — npm (package.json)

### 1. Prototype pollution — lodash (package.json)
- **Package:** `lodash@4.17.20`
- **CVE:** CVE-2021-23337 — command injection via template function
- **Severity:** High
- **Why subtle:** lodash is ubiquitous; version 4.17.20 is "only one patch behind" the fix (4.17.21). Easy to overlook.

### 2. JWT verification bypass — jsonwebtoken (package.json)
- **Package:** `jsonwebtoken@8.5.1`
- **CVE:** CVE-2022-23529 — insecure key retrieval allows arbitrary code execution when verifying a maliciously crafted JWT
- **Severity:** High
- **Why subtle:** jsonwebtoken is the most popular JWT library. 8.5.1 looks current to casual inspection.

### 3. SSRF — axios (package.json)
- **Package:** `axios@0.21.1`
- **CVE:** CVE-2021-3749 — inefficient regular expression complexity (ReDoS) leading to denial of service
- **Severity:** High
- **Why subtle:** axios 0.21.x is still commonly seen in projects. The version "looks reasonable."

### 4. Information exposure — node-fetch (package.json)
- **Package:** `node-fetch@2.6.1`
- **CVE:** CVE-2022-0235 — exposure of sensitive information to an unauthorized actor via cookie headers on redirect
- **Severity:** High
- **Why subtle:** node-fetch v2 is widely used. The vulnerability is in redirect handling, not the main API.

### 5. Prototype pollution — minimist (package.json)
- **Package:** `minimist@1.2.5`
- **CVE:** CVE-2021-44906 — prototype pollution via constructor/proto arguments
- **Severity:** High
- **Why subtle:** minimist is a deep transitive dependency in many tools. Pinning it directly is unusual, making it a realistic oversight.

### 6. Protestware/supply chain risk — colors (package.json)
- **Package:** `colors@1.4.0`
- **Supply chain signal:** The `colors` package was involved in a major protestware incident (Jan 2022) where the maintainer introduced an infinite loop in v1.4.1. Version 1.4.0 is the last "safe" version, but the package's supply chain trust is compromised. Socket should flag maintainer risk.
- **Severity:** Medium (supply chain risk)
- **Why subtle:** 1.4.0 itself has no malicious code, but the package's trust profile is degraded.

### 7. Command injection — shell-quote (package.json)
- **Package:** `shell-quote@1.7.2`
- **CVE:** CVE-2021-42740 — improper escaping allows command injection
- **Severity:** High
- **Why subtle:** shell-quote is used for safely quoting shell arguments — ironic that the security library itself is vulnerable.

## Planted vulnerabilities — Python (requirements.txt)

### 8. Information disclosure — requests (requirements.txt)
- **Package:** `requests==2.25.1`
- **CVE:** CVE-2023-32681 — Unintended leak of Proxy-Authorization header to destination server on redirect
- **Severity:** Medium
- **Why subtle:** requests is the most popular Python HTTP library. 2.25.1 is "just a few versions behind."

### 9. Arbitrary code execution — PyYAML (requirements.txt)
- **Package:** `PyYAML==5.4`
- **CVE:** CVE-2020-14343 — arbitrary code execution via unsafe yaml.load()
- **Severity:** Critical
- **Why subtle:** PyYAML 5.x is still in widespread use. The vulnerability requires using yaml.load() without a safe Loader, which many projects do.

### 10. XSS — Jinja2 (requirements.txt)
- **Package:** `Jinja2==2.11.3`
- **CVE:** CVE-2024-22195 — cross-site scripting via xmlattr filter
- **Severity:** Medium
- **Why subtle:** Jinja2 is Flask's default template engine. 2.x is common in older projects.

### 11. Multiple CVEs — cryptography (requirements.txt)
- **Package:** `cryptography==3.4.8`
- **CVEs:** Multiple — includes OpenSSL vulnerabilities and memory safety issues in the Rust backend
- **Severity:** High
- **Why subtle:** cryptography is the standard Python crypto library. 3.x is "just one major version behind" current 42.x.

### 12. ReDoS — urllib3 (requirements.txt)
- **Package:** `urllib3==1.26.5`
- **CVE:** CVE-2021-33503 — catastrophic backtracking in URL authority parsing
- **Severity:** High
- **Why subtle:** urllib3 is a transitive dependency of requests. Pinning it directly looks intentional and careful.

### 13. Multiple CVEs — Pillow (requirements.txt)
- **Package:** `Pillow==8.3.1`
- **CVEs:** Multiple — buffer overflows, heap overflows in image parsing (TIFF, JPEG, BMP)
- **Severity:** High
- **Why subtle:** Pillow 8.x is common in projects that do image processing. The vulnerabilities are in specific image format handlers.

### 14. ReDoS — setuptools (requirements.txt)
- **Package:** `setuptools==58.0.0`
- **CVE:** CVE-2022-40897 — regular expression denial of service in package_index
- **Severity:** Medium
- **Why subtle:** setuptools is a build dependency that many pin for reproducibility. 58.x is common in projects created in 2021-2022.

## Supply chain patterns to detect

Beyond individual CVEs, the skill should identify these supply chain patterns:

- **Unpinned versions in package.json:** `express`, `mongoose`, `dotenv`, `cors`, `helmet` use `^` ranges allowing automatic minor/patch upgrades — supply chain risk if a dependency is compromised
- **Mixed pinning strategies:** package.json uses `^` for some deps and exact versions for others — inconsistent security posture
- **Protestware risk:** `colors` package has known maintainer trust issues
- **Deep transitive risk:** `minimist` is typically a transitive dep; pinning it directly suggests awareness but the version is still vulnerable

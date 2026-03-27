# Test Prompts Catalog

This file contains the behavioral test prompts for all 10 security skills. There are 100 prompts total: 10 skills × 5 dimensions × 2 prompts each. Each entry includes the skill name, dimension, prompt text, and expected behavior.

Prompts are written in phases:
- **Phase 2:** bandit-sast
- **Phase 3:** crypto-audit, security-headers-audit, api-security-tester
- **Phase 4:** security-test-generator, devsecops-pipeline, pci-dss-audit, mobile-security
- **Phase 5:** docker-scout-scanner, socket-sca

---

## 1. bandit-sast

> Prompts written in: Phase 2

### Triggering

**Prompt 1:**
> Scan this Python project for security vulnerabilities

**Expected behavior:** Skill activates immediately. It detects the Python project, references SAST or static analysis concepts, and begins the workflow (checking for Bandit, running the scan). Score 3 if it activates on first message, mentions security analysis domain, and enters the scan workflow without requiring follow-up prompts.

---

**Prompt 2:**
> I'm worried there might be some unsafe code in this Flask app. Can you check for common security issues like injection flaws or hardcoded secrets?

**Expected behavior:** Skill activates despite the indirect phrasing. It recognizes the request as a Python security scan, identifies the Flask project structure, and enters the SAST workflow. Score 3 if it activates without asking clarifying questions and begins scanning. Score 2 if it activates but asks whether to proceed. Score 0-1 if it does not enter the security scanning workflow.

---

### Workflow Adherence

**Prompt 1:**
> Run a Python security scan on this codebase and show me everything you find. I want to see findings from auth.py, utils.py, and cache.py especially.

**Expected behavior:** Skill follows the documented workflow in order: (1) detects Python project, (2) checks if Bandit is installed, (3) runs `bandit -r . -f json -q` and parses JSON output, (4) maps test IDs to CWE/OWASP categories, (5) deduplicates and sorts findings by severity, (6) generates the report in Findings Format, (7) provides a summary with totals and top 3 remediation priorities. Should surface findings from auth.py (timing-vulnerable comparison, MD5 usage), utils.py (shell=True, command injection), and cache.py (pickle.loads on untrusted data). Score 3 if all steps are followed in order with no omissions.

---

**Prompt 2:**
> Check this Python code for security problems. Focus on the math_parser.py and config.py files — I want to understand the risk level of each finding.

**Expected behavior:** Follows the full workflow end-to-end. Should find eval() usage in math_parser.py and hardcoded credential fallbacks in config.py. Findings must be sorted by severity (HIGH/CRITICAL before LOW). Each finding should include severity level. The summary should list top remediation priorities. Score 3 if all workflow steps execute in documented order. Score 2 if steps are present but reordered. Score 1 if steps are missing.

---

### Output Quality

**Prompt 1:**
> Perform a static analysis security scan on this Python project. For each finding, I need the severity, CWE ID, OWASP category, exact file and line number, a description of the issue, and how to fix it.

**Expected behavior:** Output matches the Findings Format with all required fields per finding: Severity (HIGH/MEDIUM/LOW), CWE (e.g., CWE-78 for command injection, CWE-327 for weak crypto), OWASP category (e.g., A03:2021-Injection), Location as file:line, Issue description, and Remediation guidance with safe/unsafe code pairs. Report ends with a summary table showing finding totals by severity and top 3 remediation priorities. Score 3 if all six fields are present on every finding, unsafe/safe code pairs are shown, and the summary table is included. Score 2 if most fields present but some findings are missing CWE or OWASP mappings.

---

**Prompt 2:**
> Scan this project for Python security vulnerabilities and give me a structured report I can share with my team. Include remediation steps with before/after code examples.

**Expected behavior:** Output is well-structured and shareable. Each finding includes all Findings Format fields. Remediation sections show concrete unsafe (current) code alongside safe (fixed) code examples specific to the actual fixture code. The summary includes total counts grouped by severity and the top 3 prioritized remediation actions. Score 3 if the report reads as a complete, self-contained security assessment with all format fields, code pairs, and summary. Score 2 if format is mostly correct but code examples are generic rather than fixture-specific.

---

### Boundary Respect

**Prompt 1:**
> Scan this JavaScript file for Python security issues: `server.js`

**Expected behavior:** Skill declines the request. It explains that Python SAST analysis is only applicable to Python files, not JavaScript. It recommends an appropriate alternative tool for JavaScript security scanning (e.g., ESLint security plugins, Semgrep, or NodeJsScan). Score 3 if it cleanly declines, explains why (wrong language), and suggests a correct alternative by name. Score 2 if it declines but does not recommend an alternative. Score 0 if it attempts to scan the JavaScript file.

---

**Prompt 2:**
> Run eslint on this Python code to check for security problems

**Expected behavior:** Skill declines or corrects the tool mismatch. It explains that ESLint is a JavaScript/TypeScript linter and is not applicable to Python code. It should offer to run the appropriate Python security tool (Bandit) instead. Score 3 if it declines the specific tool request, explains the mismatch, and offers Bandit as the correct alternative. Score 2 if it silently runs Bandit without addressing the ESLint request. Score 0 if it attempts to run ESLint.

---

### Fallback/Install

**Prompt 1:**
> Scan this Python project for security vulnerabilities

**Expected behavior:** (Tester must uninstall Bandit before running this prompt.) Skill detects that Bandit is not installed. It offers to install Bandit via `pip install bandit`. After installation, it runs the full scan workflow: `bandit -r . -f json -q`, parses results, maps to CWE/OWASP, and produces the complete Findings Format report with summary. Score 3 if it detects missing Bandit, installs it, and completes the entire workflow with a full report. Score 2 if it installs and scans but the report is incomplete. Score 1 if it detects the missing tool but falls back to manual-only checks without attempting installation.

---

**Prompt 2:**
> I need a full security audit of this Flask application. Check for injection flaws, hardcoded credentials, and unsafe deserialization.

**Expected behavior:** (Tester must uninstall Bandit before running this prompt.) Skill detects Bandit is missing and either auto-installs or prompts the user to install it. After installation succeeds, it runs the complete workflow without needing to be re-prompted. The final report should include findings for all three categories mentioned: injection (utils.py shell=True, math_parser.py eval()), hardcoded credentials (config.py), and unsafe deserialization (cache.py pickle.loads). Score 3 if install + full workflow completes in a single interaction producing findings across all requested categories. Score 2 if it installs but misses one category. Score 1 if it falls back to manual pattern matching without installing Bandit.

---

## 2. crypto-audit

> Prompts written in: Phase 3

### Triggering

**Prompt 1 (T-1 keyword):**
> Check the code in tests/fixtures/crypto-audit/ for weak encryption and hardcoded cryptographic keys

**Expected behavior:** Skill activates on crypto-related keywords ("weak encryption", "hardcoded cryptographic keys"). It detects the multi-language project (Python, TypeScript, Go), identifies crypto-relevant files, and begins the 12-check workflow. Score 3 if it activates immediately, references cryptographic analysis, and enters the scan workflow. Score 2 if it activates but asks clarifying questions first. Score 1 if it mentions crypto but doesn't enter the workflow. Score 0 if it gives a generic response unrelated to crypto auditing.

---

**Prompt 2 (T-2 explicit):**
> /crypto-audit I'm concerned about the cryptographic implementations in our payment gateway SDK at tests/fixtures/crypto-audit/. Can you review the key management and encryption code?

**Expected behavior:** (Score on **workflow entry quality**, not triggering — slash command guarantees activation.) Skill enters the crypto-audit workflow cleanly: detects languages (Python, TS, Go), identifies crypto-relevant files (crypto_utils.py, token_service.ts, key_manager.go, tls_client.py), and begins running the 12 checks. Score 3 if workflow steps begin in documented order with no false starts. Score 2 if it enters the workflow but skips language/file detection. Score 1 if it acknowledges the request but doesn't follow the documented workflow.

---

### Workflow Adherence

**Prompt 1 (WA-1):**
> Audit the cryptographic code in tests/fixtures/crypto-audit/crypto_utils.py and tests/fixtures/crypto-audit/token_service.ts for security vulnerabilities. I want to understand every crypto weakness in these files.

**Expected behavior:** Follows the documented workflow in order: (1) detects Python + TypeScript, (2) identifies crypto-relevant files, (3) runs 12 checks against the two files, (4) generates findings in Findings Format with severity, CWE, OWASP mapping, file:line, UNSAFE/SAFE pairs, (5) deduplicates and sorts by severity, (6) summarizes with top 3 priorities. Should find: MD5 usage (crypto_utils.py:28), hardcoded AES key (crypto_utils.py:38), insecure random (crypto_utils.py:55), weak password hashing (crypto_utils.py:72), static IV (token_service.ts:24-27), timing attack (token_service.ts:64), deprecated TLS (token_service.ts:81). Score 3 if all workflow steps execute in order with >= 5 of 7 findings. Score 2 if steps are present but reordered or 3-4 findings. Score 1 if major steps are missing.

---

**Prompt 2 (WA-2):**
> Review the Go and Python files in tests/fixtures/crypto-audit/ — specifically key_manager.go and tls_client.py — for cryptographic anti-patterns. What are the most critical issues?

**Expected behavior:** Follows full workflow targeting key_manager.go and tls_client.py. Should find: weak RSA key size (key_manager.go:28), ECB mode (key_manager.go:43-49), 3DES usage (key_manager.go:82), certificate validation bypass (tls_client.py:33-34), missing HMAC verification (tls_client.py:88), hardcoded signing secret (tls_client.py:97). Findings sorted by severity — Critical (cert validation, hardcoded key) before High (ECB, 3DES, weak RSA) before Medium (missing HMAC). Score 3 if all workflow steps in order with >= 4 of 6 findings and correct severity ordering. Score 2 if steps present but 2-3 findings. Score 1 if workflow steps missing.

---

### Output Quality

**Prompt 1 (OQ-1 implicit):**
> Give me a thorough cryptographic audit of the code in tests/fixtures/crypto-audit/

**Expected behavior:** (Implicit test — no format requested.) Output should naturally follow the Findings Format from the SKILL.md without being prompted: each finding includes Severity (Critical/High/Medium), CWE ID (e.g., CWE-328, CWE-321), OWASP mapping (e.g., A02:2021-Cryptographic Failures), file:line location, description, and UNSAFE/SAFE code pairs. Report ends with a summary and top 3 remediation priorities. Score 3 if all format fields appear on every finding without prompting, code pairs are shown, and summary is included. Score 2 if most fields present but some findings lack CWE or code pairs. Score 1 if findings are freeform text without consistent structure. Score 0 if output is a generic list with no security metadata.

---

**Prompt 2 (OQ-2 explicit):**
> Generate a security audit report for tests/fixtures/crypto-audit/ that I can share with my team. Include an executive summary, prioritized findings, and a top-3 remediation roadmap.

**Expected behavior:** Output is a complete, shareable security report. Includes: (1) Executive summary with overall risk assessment and finding counts by severity, (2) Findings in Findings Format with all fields, sorted by severity, (3) UNSAFE/SAFE code pairs specific to the fixture code (not generic examples), (4) Top 3 remediation roadmap with prioritized actions. Score 3 if report is self-contained, professional, has all sections, and code pairs reference the actual fixture code. Score 2 if report structure is good but code examples are generic or summary is thin. Score 1 if it produces findings but not in a shareable report format.

---

### Boundary Respect

**Prompt 1 (BR-1 clearly wrong):**
> Check tests/fixtures/api-security-tester/ for SQL injection vulnerabilities

**Expected behavior:** Skill declines the request. It explains that crypto-audit is for cryptographic vulnerability detection, not SQL injection or API security issues. It recommends appropriate alternatives (e.g., api-security-tester, bandit-sast, or security-review). Score 3 if it cleanly declines, explains why (wrong domain), and names a correct alternative. Score 2 if it declines but doesn't suggest an alternative. Score 1 if it partially complies by looking for crypto issues in the API files (technically correct but not what was asked). Score 0 if it attempts SQL injection analysis.

---

**Prompt 2 (BR-2 subtly wrong):**
> Review tests/fixtures/crypto-audit/crypto_utils.py for input validation issues

**Expected behavior:** Skill recognizes this is adjacent but out of scope. crypto_utils.py IS a crypto file, but the request is for input validation analysis, not cryptographic review. Skill should either: (a) decline and explain that input validation is outside crypto-audit's scope, suggesting security-review or bandit-sast instead, or (b) pivot to reporting the crypto issues it CAN find in that file while noting the input validation request is out of scope. Score 3 if it clearly distinguishes crypto audit vs. input validation, addresses the scope mismatch, and suggests the right tool. Score 2 if it audits for crypto issues (its actual scope) without addressing the mismatch. Score 1 if it attempts generic input validation analysis. Score 0 if it gives unrelated advice.

---

### Fallback/Install

**Prompt 1 (FI-1 pure-analysis):**
> Audit tests/fixtures/crypto-audit/ for cryptographic vulnerabilities. I don't have any security tools installed.

**Expected behavior:** (Pure-analysis skill — should NOT attempt any tool installation.) Skill begins code analysis immediately by reading the fixture files. No pip install, npm install, brew install, or any tool installation commands. It proceeds through the full workflow: detect languages, identify files, run checks by reading code, produce findings. Score 3 if analysis begins immediately with zero install attempts or tool mentions. Score 2 if it mentions it could use a tool (e.g., "I could run semgrep but I'll analyze manually") but proceeds with analysis. Score 1 if it attempts to install something, fails or is told not to, then falls back to code analysis. Score 0 if it insists on installing tools before proceeding or refuses to analyze without tools.

---

**Prompt 2 (FI-2 install-blocked):**
> Can you check tests/fixtures/crypto-audit/ for crypto issues? My pip is broken and I can't install packages.

**Expected behavior:** (Tests whether the skill proceeds despite explicit install-blocking.) Skill should NOT attempt pip install or any other installation. It proceeds directly to reading and analyzing the code. The "pip is broken" hint is a red herring for a pure-analysis skill — it should have no relevance. Score 3 if it ignores the pip comment entirely and starts analyzing code. Score 2 if it acknowledges the pip limitation but proceeds correctly. Score 1 if it spends time troubleshooting pip before analyzing. Score 0 if it refuses to proceed without functioning package management.

---

## 3. security-test-generator

> Prompts written in: Phase 4

### Triggering

**Prompt 1 (T-1 keyword):**
> Generate security tests for the API endpoints in tests/fixtures/security-test-generator/

**Expected behavior:** Skill activates on security-test-related keywords ("generate security tests", "API endpoints"). It detects the project frameworks (Express in app.js, Flask in app.py), identifies testable endpoints, and begins the test generation workflow. Score 3 if it activates immediately, references security test generation, and enters the workflow. Score 2 if it activates but asks clarifying questions. Score 1 if it mentions security testing but doesn't enter the workflow. Score 0 if it gives a generic response.

---

**Prompt 2 (T-2 explicit):**
> /security-test-generator Our API backend at tests/fixtures/security-test-generator/ has both Express and Flask services. Can you generate a security test suite covering injection, auth bypass, and path traversal?

**Expected behavior:** (Score on **workflow entry quality**, not triggering — slash command guarantees activation.) Skill enters the security-test-generator workflow cleanly: detects both frameworks (Express/jest+supertest, Flask/pytest+requests), identifies endpoints in both files, and begins generating tests. Score 3 if workflow steps begin in documented order with dual-framework detection. Score 2 if it enters the workflow but only detects one framework. Score 1 if it acknowledges the request but doesn't follow the documented workflow.

---

### Workflow Adherence

**Prompt 1 (WA-1):**
> Create a comprehensive security test suite for the Express app at tests/fixtures/security-test-generator/app.js. I want tests covering all the API endpoints — especially the search, login, and file access routes.

**Expected behavior:** Follows the documented workflow: (1) detects Node.js/Express framework, (2) identifies endpoints (/api/users, /api/login, /api/files/:filename, /api/profile/:userId, /api/proxy), (3) generates jest+supertest tests with malicious payloads per vuln class, (4) each test follows arrange/act/assert structure with CWE+OWASP annotations, (5) covers SQLi (search), timing attack (login), path traversal (files), mass assignment (profile), SSRF (proxy). Score 3 if all workflow steps execute in order and tests cover >= 4 of 5 endpoints. Score 2 if steps present but only 2-3 endpoints covered. Score 1 if major steps missing.

---

**Prompt 2 (WA-2):**
> Write security regression tests for the Flask API in tests/fixtures/security-test-generator/app.py. Focus on the proxy endpoint and profile update — I'm worried about SSRF and mass assignment.

**Expected behavior:** Follows full workflow targeting app.py: (1) detects Python/Flask, (2) identifies the /api/proxy and /api/profile endpoints, (3) generates pytest+requests tests with SSRF payloads (internal IPs, cloud metadata URLs) and mass assignment payloads (is_admin field injection), (4) tests use proper assertions (status codes, response body checks). Should generate tests for at least the 2 requested endpoints plus optionally others. Score 3 if all workflow steps in order with focused tests for proxy (SSRF) and profile (mass assignment). Score 2 if steps present but only one endpoint covered. Score 1 if workflow steps missing.

---

### Output Quality

**Prompt 1 (OQ-1 implicit):**
> Write security tests for the web application at tests/fixtures/security-test-generator/

**Expected behavior:** (Implicit test — no format requested. Adapted rubric for test code output.) Generated tests should naturally include: (a) CWE+OWASP references in test names/comments (e.g., "CWE-89", "A03:2021"), (b) multiple malicious payloads per vulnerability class (not just one), (c) proper assertion logic (check status codes AND response bodies), (d) arrange/act/assert structure, (e) coverage of all 5 vulnerability types. Score 3 if all 5 criteria met across both frameworks. Score 2 if tests exist but missing CWE annotations or only 1 payload per vuln. Score 1 if generic test stubs without real payloads. Score 0 if no test code generated, only freeform advice.

---

**Prompt 2 (OQ-2 explicit):**
> Generate a production-ready security test suite for tests/fixtures/security-test-generator/ that our QA team can add to CI. Include CWE and OWASP references for each test, multiple payloads per vulnerability type, and proper test structure with setup/teardown.

**Expected behavior:** Generated test code is production-quality: (1) proper test structure with describe/it blocks (Jest) or test classes (pytest), (2) each test annotated with CWE ID and OWASP category, (3) multiple payloads per vuln class (at least 3 SQLi payloads, 2+ XSS, etc.), (4) assertions check both status code and response body content, (5) setup/teardown hooks for server lifecycle, (6) covers all 5 endpoint vulns. Score 3 if tests are ready to copy into a project and run. Score 2 if structure is good but payloads are generic or CWE refs are missing. Score 1 if tests are incomplete stubs.

---

### Boundary Respect

**Prompt 1 (BR-1 clearly wrong):**
> Run a static analysis scan on tests/fixtures/crypto-audit/ and report all the vulnerabilities you find

**Expected behavior:** Skill declines the request. It explains that security-test-generator produces runnable test code, not static analysis scan results. It recommends appropriate alternatives (e.g., crypto-audit for crypto code, bandit-sast for Python SAST, or security-review for general scanning). Score 3 if it cleanly declines, explains why (wrong skill — scanning vs. test generation), and names a correct alternative. Score 2 if it declines but doesn't suggest an alternative. Score 1 if it partially complies by generating tests for crypto code. Score 0 if it runs a static analysis scan.

---

**Prompt 2 (BR-2 subtly wrong):**
> Generate a CI/CD security pipeline for the project at tests/fixtures/security-test-generator/

**Expected behavior:** Skill recognizes this is adjacent but out of scope. The fixture IS a web project, but the request is for CI/CD pipeline generation, not security test code. Skill should decline and explain that pipeline generation is the devsecops-pipeline skill's domain, or pivot to offering security tests instead. Score 3 if it clearly distinguishes test generation vs. pipeline generation and suggests devsecops-pipeline. Score 2 if it generates tests (its scope) without addressing the pipeline mismatch. Score 1 if it attempts to generate YAML pipeline config. Score 0 if it gives unrelated advice.

---

### Fallback/Install

**Prompt 1 (FI-1 pure-analysis):**
> Generate security tests for tests/fixtures/security-test-generator/. I don't have any security tools installed.

**Expected behavior:** (Pure-analysis skill — should NOT attempt any tool installation.) Skill begins code analysis immediately by reading the fixture files (app.js, app.py). No pip install, npm install, or any tool installation commands. It proceeds through the full workflow: detect frameworks, identify endpoints, generate test code. Score 3 if test generation begins immediately with zero install attempts or tool mentions. Score 2 if it mentions it could use a tool (e.g., "I could run OWASP ZAP") but proceeds with code generation. Score 1 if it attempts to install something, fails or is told not to, then falls back. Score 0 if it insists on installing tools before generating tests.

---

**Prompt 2 (FI-2 install-blocked):**
> Can you write security tests for tests/fixtures/security-test-generator/? My pip is broken and I can't install packages.

**Expected behavior:** (Tests whether the skill proceeds despite explicit install-blocking.) Skill should NOT attempt pip install or any other installation. It reads source files directly and generates test code. The "pip is broken" hint is a red herring for a pure code-generation skill — it should have no relevance. Score 3 if it ignores the pip comment entirely and starts generating tests. Score 2 if it acknowledges the pip limitation but proceeds correctly. Score 1 if it spends time troubleshooting pip before generating tests. Score 0 if it refuses to proceed without functioning package management.

---

## 4. devsecops-pipeline

> Prompts written in: Phase 4

### Triggering

**Prompt 1 (T-1 keyword):**
> Set up automated security scanning in CI/CD for the project at tests/fixtures/devsecops-pipeline/

**Expected behavior:** Skill activates on CI/CD security keywords ("automated security scanning", "CI/CD"). It detects the multi-ecosystem project (Node.js, Python, Docker, Go), identifies manifest files, and begins the pipeline generation workflow. Score 3 if it activates immediately, references DevSecOps/CI/CD pipeline generation, and enters the workflow. Score 2 if it activates but asks clarifying questions. Score 1 if it mentions CI/CD but doesn't enter the workflow. Score 0 if it gives a generic response.

---

**Prompt 2 (T-2 explicit):**
> /devsecops-pipeline Our monorepo at tests/fixtures/devsecops-pipeline/ has Node.js, Python, Go services and a Dockerfile. Can you generate a GitHub Actions security pipeline covering SAST, SCA, secrets detection, and container scanning?

**Expected behavior:** (Score on **workflow entry quality**, not triggering — slash command guarantees activation.) Skill enters the devsecops-pipeline workflow cleanly: detects all 4 ecosystems (Node.js, Python, Go, Container), identifies manifest files (package.json, requirements.txt, go.mod, Dockerfile), and begins generating the workflow YAML. Score 3 if workflow steps begin in documented order with all 4 ecosystems detected. Score 2 if it enters the workflow but only detects 2-3 ecosystems. Score 1 if it acknowledges the request but doesn't follow the documented workflow.

---

### Workflow Adherence

**Prompt 1 (WA-1):**
> Generate a security pipeline for the project at tests/fixtures/devsecops-pipeline/

**Expected behavior:** Follows the documented workflow: (1) detects all 4 ecosystems from manifest files, (2) selects pipeline stages (SAST, SCA-node, SCA-python, SCA-go, Secrets, Container), (3) generates complete workflow YAML with proper structure, (4) configures severity thresholds, (5) adds SARIF upload steps for Semgrep and Trivy, (6) adds artifact upload steps for all stages, (7) notes customization options, (8) outputs the complete YAML. Score 3 if all 8 workflow steps in order with all 4 ecosystems represented. Score 2 if steps present but only 2-3 ecosystems or missing SARIF/artifact uploads. Score 1 if major steps missing.

---

**Prompt 2 (WA-2):**
> Generate a CI/CD security workflow for the Node.js and Docker parts of tests/fixtures/devsecops-pipeline/ — I only need SAST and container scanning

**Expected behavior:** Follows full workflow but respects the narrowed scope: (1) detects Node.js + Docker (2) selects only SAST (Semgrep with p/javascript p/docker) and Container Scanning (Trivy), (3) generates YAML with only the requested stages, (4) still includes proper permissions, concurrency, SARIF uploads, and artifact uploads for the included stages. Should NOT include SCA or Secrets stages unless it explains why they're recommended. Score 3 if all workflow steps in order with correct scope narrowing. Score 2 if steps present but includes unrequested stages without explanation. Score 1 if workflow steps missing.

---

### Output Quality

**Prompt 1 (OQ-1 implicit):**
> Create a GitHub Actions security workflow for tests/fixtures/devsecops-pipeline/

**Expected behavior:** (Implicit test — no format requested. Adapted rubric for YAML output.) Generated YAML should include: (a) all detected ecosystem stages (SAST, SCA-node, SCA-python, SCA-go, Secrets, Container), (b) correct action versions from SKILL.md reference table, (c) SARIF upload steps for Semgrep and Trivy, (d) artifact upload steps for all stages, (e) proper permissions block (security-events: write, contents: read, actions: read), (f) concurrency configuration, (g) severity thresholds documented. Score 3 if all 7 criteria met. Score 2 if valid YAML with most stages but missing SARIF/artifacts or wrong action versions. Score 1 if partial YAML with only 1-2 stages. Score 0 if no YAML output, only freeform advice.

---

**Prompt 2 (OQ-2 explicit):**
> Generate a production-ready security.yml for tests/fixtures/devsecops-pipeline/ that I can commit directly to .github/workflows/. Include all applicable scanning stages, SARIF integration, and document the severity thresholds.

**Expected behavior:** Complete, commit-ready YAML: (1) proper `name`, `on` triggers (push, PR, schedule), `permissions`, `concurrency` sections, (2) all applicable stages with correct GitHub Action references and pinned versions, (3) SARIF upload steps with `github/codeql-action/upload-sarif@v3`, (4) artifact upload with `actions/upload-artifact@v4`, (5) severity thresholds documented via comments, (6) customization guidance (threshold tuning, Slack notifications, branch protection). Score 3 if YAML is copy-paste ready with all sections. Score 2 if YAML is valid but missing customization guidance or some stages. Score 1 if incomplete YAML.

---

### Boundary Respect

**Prompt 1 (BR-1 clearly wrong):**
> Run a security scan on tests/fixtures/bandit-sast/ right now and show me the findings

**Expected behavior:** Skill declines the request. It explains that devsecops-pipeline generates CI/CD workflow YAML files, it doesn't run security scans directly. It recommends bandit-sast or security-review for immediate scanning. Score 3 if it cleanly declines, explains why (pipeline generation vs. direct scanning), and names a correct alternative. Score 2 if it declines but doesn't suggest an alternative. Score 1 if it partially complies by generating a pipeline for the bandit fixtures. Score 0 if it attempts to run a scan.

---

**Prompt 2 (BR-2 subtly wrong):**
> Generate security test code for the Express app in tests/fixtures/security-test-generator/

**Expected behavior:** Skill recognizes this is adjacent but out of scope. The request is for security test CODE, not a CI/CD pipeline. Skill should decline and explain that test code generation is the security-test-generator skill's domain, or note the distinction between pipeline config and test code. Score 3 if it clearly distinguishes pipeline generation vs. test code generation and suggests security-test-generator. Score 2 if it generates a pipeline (its scope) without addressing the mismatch. Score 1 if it attempts to generate test code. Score 0 if it gives unrelated advice.

---

### Fallback/Install

**Prompt 1 (FI-1 pure-analysis):**
> Generate a security pipeline for tests/fixtures/devsecops-pipeline/. I don't have any security tools installed.

**Expected behavior:** (Pure-analysis skill — should NOT attempt any tool installation.) Skill begins project analysis immediately by reading manifest files (package.json, requirements.txt, Dockerfile, go.mod). No pip install, npm install, or any tool installation commands. It proceeds through the full workflow to generate YAML. Score 3 if YAML generation begins immediately with zero install attempts or tool mentions. Score 2 if it mentions it could use a tool but proceeds with generation. Score 1 if it attempts to install something, fails or is told not to, then falls back. Score 0 if it insists on installing tools before generating the pipeline.

---

**Prompt 2 (FI-2 install-blocked):**
> Can you create a security CI/CD workflow for tests/fixtures/devsecops-pipeline/? My pip is broken and I can't install packages.

**Expected behavior:** Skill should NOT attempt pip install or any installation. It reads manifest files directly and generates YAML. The "pip is broken" hint is irrelevant for a pure config-generation skill. Score 3 if it ignores the pip comment entirely and starts generating the pipeline. Score 2 if it acknowledges the pip limitation but proceeds correctly. Score 1 if it spends time troubleshooting pip before generating. Score 0 if it refuses to proceed without functioning package management.

---

## 5. docker-scout-scanner

> Prompts written in: Phase 5

### Triggering

**Prompt 1 (T-1 keyword):**
> I need to check the container images in tests/fixtures/docker-scout-scanner/ for known vulnerabilities and security issues

**Expected behavior:** Skill activates on container-security keywords ("container images", "known vulnerabilities"). It detects the Docker project (Dockerfile, Dockerfile.worker, docker-compose.yml), identifies container-relevant files, and begins the scanning workflow. Score 3 if it activates immediately, references container security/CVE analysis, and enters the workflow. Score 2 if it activates but asks clarifying questions. Score 1 if it mentions containers but doesn't enter the workflow. Score 0 if it gives a generic response unrelated to container scanning.

---

**Prompt 2 (T-2 explicit):**
> /docker-scout-scanner Our inventory management system at tests/fixtures/docker-scout-scanner/ uses Node.js and Python containers. Can you review the Dockerfiles and compose setup for security risks?

**Expected behavior:** (Score on **workflow entry quality**, not triggering — slash command guarantees activation.) Skill enters the docker-scout-scanner workflow cleanly: detects Docker project files (Dockerfile, Dockerfile.worker, docker-compose.yml), checks for Docker Scout CLI, and begins either the CLI scan or manual check workflow. Score 3 if workflow steps begin in documented order with multi-file detection. Score 2 if it enters the workflow but only detects one Dockerfile. Score 1 if it acknowledges the request but doesn't follow the documented workflow.

---

### Workflow Adherence

**Prompt 1 (WA-1):**
> Check the main Dockerfile in tests/fixtures/docker-scout-scanner/ for security issues. I want to understand every risk in the base image and build configuration.

**Expected behavior:** Follows the documented workflow in order: (1) detects Docker project, (2) checks for Docker Scout CLI, (3) runs Docker Scout CVE scan OR falls back to manual checks, (4) maps findings to CWE/OWASP, (5) sorts by severity, (6) generates report in Findings Format, (7) summarizes with top 3 remediation priorities. Should find in Dockerfile: EOL node:16 base image, secrets in build ARGs, unnecessary packages, ADD with remote URL, debug port exposed, shell form CMD, running as root, no HEALTHCHECK. Score 3 if all workflow steps execute in order with >= 6 of 8 findings. Score 2 if steps present but reordered or 4-5 findings. Score 1 if major steps missing.

---

**Prompt 2 (WA-2):**
> Do a complete container security review of the project in tests/fixtures/docker-scout-scanner/. Check all Dockerfiles and the docker-compose configuration.

**Expected behavior:** Follows full workflow across ALL project files — both Dockerfiles AND docker-compose.yml. Should find issues in Dockerfile (root, shell CMD, build ARGs, ADD), Dockerfile.worker (EOL python:3.8-slim, no multi-stage, root, missing --chown), AND docker-compose.yml (privileged container, host /etc mount, Docker socket mount, exposed database ports). Score 3 if all workflow steps in order, covers all 3 files, and finds >= 12 of 18 total issues. Score 2 if covers 2 files or finds 8-11 issues. Score 1 if only covers 1 file or finds < 8 issues.

---

### Output Quality

**Prompt 1 (OQ-1 implicit):**
> Analyze the container security posture of the project at tests/fixtures/docker-scout-scanner/

**Expected behavior:** (Implicit test — no format requested.) Output should naturally follow the Findings Format from SKILL.md without being prompted: each finding includes Severity (Critical/High/Medium/Low), CWE ID (e.g., CWE-250 for root, CWE-798 for hardcoded secrets), OWASP mapping (e.g., A05:2021-Security Misconfiguration), Location as image layer or Dockerfile:line, description, and remediation. Report ends with severity breakdown and top 3 remediation priorities. Score 3 if all format fields appear on every finding without prompting, and summary is included. Score 2 if most fields present but some findings lack CWE or OWASP mappings. Score 1 if findings are freeform text. Score 0 if output is generic advice without file-specific analysis.

---

**Prompt 2 (OQ-2 explicit):**
> Generate a container security report for tests/fixtures/docker-scout-scanner/ that I can share with the DevOps team. Include a summary table, severity breakdown, base image upgrade recommendations, and before/after Dockerfile examples for the top issues.

**Expected behavior:** Output is a complete, shareable container security report. Includes: (1) Executive summary with finding counts by severity, (2) Findings in Findings Format with all fields sorted by severity, (3) UNSAFE/SAFE Dockerfile pairs specific to the fixture code (e.g., `FROM node:16` → `FROM node:22-slim@sha256:...`, shell form CMD → exec form CMD, running as root → explicit USER), (4) Base image upgrade recommendations with specific version targets, (5) Top 3 remediation roadmap. Score 3 if report is self-contained, professional, has all sections, and code pairs reference the actual fixture Dockerfiles. Score 2 if structure is good but code examples are generic. Score 1 if findings exist but not in report format.

---

### Boundary Respect

**Prompt 1 (BR-1 clearly wrong):**
> Scan the Python source code in tests/fixtures/bandit-sast/ for container security vulnerabilities

**Expected behavior:** Skill declines the request. It explains that docker-scout-scanner is for container image and Dockerfile analysis, not Python source code. The target directory contains Python files but no Dockerfiles or container configuration. It recommends bandit-sast or security-review for Python code analysis. Score 3 if it cleanly declines, explains why (no container files), and names a correct alternative. Score 2 if it declines but doesn't suggest an alternative. Score 1 if it partially complies by trying to find Docker-related content. Score 0 if it attempts to scan Python source code for container issues.

---

**Prompt 2 (BR-2 subtly wrong):**
> Generate a CI/CD pipeline for the Docker project in tests/fixtures/devsecops-pipeline/

**Expected behavior:** Skill recognizes this is adjacent but out of scope. The target directory HAS a Dockerfile, but the request is to generate a CI/CD pipeline — that's the devsecops-pipeline skill's domain, not container scanning. Skill should either: (a) decline and explain that pipeline generation is outside its scope, suggesting devsecops-pipeline instead, or (b) offer to scan the Dockerfile for security issues instead of generating a pipeline. Score 3 if it clearly distinguishes container scanning vs. pipeline generation, addresses the scope mismatch, and suggests the right tool. Score 2 if it scans the Dockerfile for security issues (its actual scope) without addressing the pipeline request. Score 1 if it attempts to generate pipeline YAML.

---

### Fallback/Install

**Prompt 1 (FI-1 scan request):**
> Scan the container images in tests/fixtures/docker-scout-scanner/ for CVEs and known vulnerabilities

**Expected behavior:** (Tester must uninstall Docker Scout CLI before running this prompt.) Skill detects that Docker Scout is not installed. It offers to install Docker Scout (e.g., `curl -fsSL https://raw.githubusercontent.com/docker/scout-cli/main/install.sh | sh` or via Docker plugin). After installation, it runs `docker scout cves` against the images, parses the JSON output, maps to CWE/OWASP, and produces the complete Findings Format report with summary. Score 3 if it detects missing Docker Scout, installs it, and completes the entire scan workflow with a full report. Score 2 if it detects missing tool and either installs + partial report, or falls back to manual Dockerfile checks. Score 1 if it detects missing tool but doesn't install and doesn't fall back. Score 0 if it errors out or gives up.

---

**Prompt 2 (FI-2 SBOM request):**
> Generate a Software Bill of Materials (SBOM) for the container images defined in tests/fixtures/docker-scout-scanner/

**Expected behavior:** (Tester must uninstall Docker Scout CLI before running this prompt.) Skill detects Docker Scout is missing and either auto-installs or prompts the user to install. After installation, it runs `docker scout sbom` or equivalent to generate the SBOM. If Docker Scout install fails, it falls back to manual Dockerfile analysis and documents what it found without the full SBOM. Score 3 if install + SBOM generation completes in a single interaction. Score 2 if it installs but falls back to manual checks instead of SBOM. Score 1 if it acknowledges the need for Docker Scout but neither installs nor falls back. Score 0 if it errors out.

---

## 6. security-headers-audit

> Prompts written in: Phase 3

### Triggering

**Prompt 1 (T-1 keyword):**
> Review the server configuration in tests/fixtures/security-headers-audit/ for missing or misconfigured HTTP security headers

**Expected behavior:** Skill activates on header-related keywords ("HTTP security headers", "misconfigured"). It detects the server frameworks (Express/Helmet, Nginx, Next.js), identifies header-relevant files, and begins the 11-check workflow. Score 3 if it activates immediately, references security header analysis, and enters the audit workflow. Score 2 if it activates but asks clarifying questions. Score 1 if it mentions headers but doesn't enter the workflow. Score 0 if it gives a generic response unrelated to header auditing.

---

**Prompt 2 (T-2 explicit):**
> /security-headers-audit Our SaaS dashboard at tests/fixtures/security-headers-audit/ uses Express with Helmet behind Nginx. Can you check if our security headers are properly configured across all layers?

**Expected behavior:** (Score on **workflow entry quality**, not triggering.) Skill enters the security-headers-audit workflow cleanly: detects frameworks (Express/Helmet.js, Nginx, Next.js), identifies config files (express-app.js, nginx.conf, next.config.js), and begins running the 11 header checks. Score 3 if workflow steps begin in documented order and it recognizes the multi-layer architecture. Score 2 if it enters the workflow but doesn't distinguish between layers. Score 1 if it acknowledges the request but doesn't follow the documented workflow.

---

### Workflow Adherence

**Prompt 1 (WA-1):**
> Review the Express and Nginx configuration in tests/fixtures/security-headers-audit/ for security header issues. I want to know what's missing and what's misconfigured.

**Expected behavior:** Follows the documented workflow targeting express-app.js and nginx.conf: (1) detects Express/Helmet.js and Nginx, (2) identifies header-relevant files, (3) runs 11 checks, (4) generates findings with severity, CWE, OWASP, location, UNSAFE/SAFE pairs, (5) deduplicates and sorts by severity, (6) summarizes with top 3 priorities. Should find: weak CSP (express-app.js:26), permissive CORS (express-app.js:57-72), weak HSTS (nginx.conf:32), missing X-Content-Type-Options (nginx.conf), missing X-Frame-Options (nginx.conf), missing Referrer-Policy (nginx.conf), missing Cache-Control on /api/me (express-app.js:99), exposed X-Powered-By (express-app.js:117). Score 3 if all workflow steps in order with >= 6 of 8 findings. Score 2 if steps present but 4-5 findings. Score 1 if major steps missing.

---

**Prompt 2 (WA-2):**
> Audit the full tests/fixtures/security-headers-audit/ directory for missing or misconfigured security headers across all layers — Express, Nginx, and Next.js.

**Expected behavior:** Follows full workflow scanning all 3 files. Should find all 11 checks including the Next.js-specific ones: overly permissive Permissions-Policy (next.config.js:18-23), missing HSTS on API routes (next.config.js:36-46), missing COOP/COEP (next.config.js). The multi-layer analysis should note header interactions (e.g., Nginx's proxy_hide_header stripping upstream headers). Score 3 if all workflow steps in order with >= 8 of 11 findings and cross-layer analysis. Score 2 if 6-7 findings without cross-layer notes. Score 1 if workflow steps missing or only one framework analyzed.

---

### Output Quality

**Prompt 1 (OQ-1 implicit):**
> Give me a thorough security headers audit of the configuration in tests/fixtures/security-headers-audit/

**Expected behavior:** (Implicit test — no format requested.) Output should naturally follow the Findings Format: each finding includes Severity, CWE ID (e.g., CWE-693, CWE-942), OWASP mapping (e.g., A05:2021-Security Misconfiguration), file:line location, description, and UNSAFE/SAFE configuration pairs showing the current misconfigured state and the correct configuration. Report ends with summary and top 3 priorities. Score 3 if all format fields appear without prompting, config pairs show framework-specific fixes, and summary is included. Score 2 if most fields present but some findings lack CWE or config pairs. Score 1 if findings are freeform text. Score 0 if output is a generic checklist with no security metadata.

---

**Prompt 2 (OQ-2 explicit):**
> Generate a security audit report for tests/fixtures/security-headers-audit/ that I can share with my team. Include an executive summary, prioritized findings, and a top-3 remediation roadmap.

**Expected behavior:** Complete, shareable report with: (1) Executive summary covering the multi-layer architecture and overall header posture, (2) Findings in Findings Format sorted by severity with framework-specific UNSAFE/SAFE configuration pairs, (3) Top 3 remediation roadmap prioritizing high-impact fixes. Score 3 if report is self-contained, professional, references all three config layers, and config pairs are specific to the fixture files. Score 2 if structure is good but examples are generic or only one layer is covered. Score 1 if findings produced but not in shareable report format.

---

### Boundary Respect

**Prompt 1 (BR-1 clearly wrong):**
> Scan tests/fixtures/crypto-audit/ for mobile app certificate pinning issues

**Expected behavior:** Skill declines the request. It explains that security-headers-audit reviews HTTP security header configurations, not mobile certificate pinning. It recommends mobile-security or crypto-audit as alternatives. Score 3 if it cleanly declines, explains why (wrong domain — mobile security, not HTTP headers), and names a correct alternative. Score 2 if it declines but doesn't suggest an alternative. Score 1 if it partially complies by looking for any header-related content in crypto files. Score 0 if it attempts mobile security analysis.

---

**Prompt 2 (BR-2 subtly wrong):**
> Check tests/fixtures/security-headers-audit/express-app.js for SQL injection in the query parameters

**Expected behavior:** Skill recognizes this is the right file but wrong analysis type. express-app.js IS in its scope for header auditing, but SQL injection is not a header configuration issue. Skill should either: (a) decline the SQL injection request and explain that it audits header configurations, suggesting bandit-sast or security-review for injection analysis, or (b) pivot to reporting the header issues it CAN find in express-app.js while noting SQL injection is out of scope. Score 3 if it distinguishes header audit vs. injection analysis and suggests the right tool. Score 2 if it audits headers (its scope) without addressing the mismatch. Score 1 if it attempts SQL injection analysis. Score 0 if it gives unrelated advice.

---

### Fallback/Install

**Prompt 1 (FI-1 pure-analysis):**
> Audit tests/fixtures/security-headers-audit/ for security header misconfigurations. I don't have any security tools installed.

**Expected behavior:** (Pure-analysis skill — should NOT attempt any tool installation.) Skill begins configuration analysis immediately by reading the fixture files (express-app.js, nginx.conf, next.config.js). No pip install, npm install, or any tool installation commands. It proceeds through the full workflow: detect frameworks, identify files, run header checks by reading configs, produce findings. Score 3 if analysis begins immediately with zero install attempts or tool mentions. Score 2 if it mentions it could use a tool (e.g., "I could use observatory or securityheaders.com") but proceeds with analysis. Score 1 if it attempts installation then falls back. Score 0 if it insists on tools.

---

**Prompt 2 (FI-2 install-blocked):**
> Can you check tests/fixtures/security-headers-audit/ for header issues? My npm is broken and I can't install packages.

**Expected behavior:** Skill should NOT attempt npm install or any installation. It reads config files directly and performs static analysis. The "npm is broken" hint is irrelevant for a pure-analysis skill. Score 3 if it ignores the npm comment and starts analyzing configurations. Score 2 if it acknowledges the npm limitation but proceeds correctly. Score 1 if it spends time troubleshooting npm before analyzing. Score 0 if it refuses to proceed.

---

## 7. socket-sca

> Prompts written in: Phase 5

### Triggering

**Prompt 1 (T-1 keyword):**
> I want to audit the dependencies in tests/fixtures/socket-sca/ for supply chain risks and known vulnerabilities

**Expected behavior:** Skill activates on supply-chain keywords ("audit", "dependencies", "supply chain risks", "known vulnerabilities"). It detects the project manifests (package.json, package-lock.json, requirements.txt), identifies dependency files, and begins the SCA workflow. Score 3 if it activates immediately, references supply chain analysis/SCA, and enters the workflow. Score 2 if it activates but asks clarifying questions. Score 1 if it mentions dependencies but doesn't enter the workflow. Score 0 if it gives a generic response unrelated to supply chain analysis.

---

**Prompt 2 (T-2 explicit):**
> /socket-sca Our inventory API at tests/fixtures/socket-sca/ has both npm and Python dependencies. I'm concerned about supply chain attacks — can you check for typosquatting, protestware, and known CVEs?

**Expected behavior:** (Score on **workflow entry quality**, not triggering — slash command guarantees activation.) Skill enters the socket-sca workflow cleanly: detects manifests (package.json, package-lock.json, requirements.txt), checks for Socket CLI, and begins either the CLI scan or manual check workflow. Score 3 if workflow steps begin in documented order with multi-manifest detection. Score 2 if it enters the workflow but only detects one manifest type. Score 1 if it acknowledges the request but doesn't follow the documented workflow.

---

### Workflow Adherence

**Prompt 1 (WA-1):**
> Check the npm dependencies in tests/fixtures/socket-sca/package.json for security issues. I want to know about any vulnerable or risky packages.

**Expected behavior:** Follows the documented workflow in order: (1) detects package.json manifest, (2) checks for Socket CLI, (3) runs `socket scan create --json .` OR falls back to manual checks, (4) maps alert types to CWE/OWASP, (5) deduplicates and sorts by severity, (6) generates report in Findings Format, (7) summarizes with top 3 remediation priorities. Should find: lodash prototype pollution, jsonwebtoken verification bypass, axios ReDoS, node-fetch information exposure, minimist prototype pollution, colors supply chain risk, shell-quote command injection. Score 3 if all workflow steps execute in order with >= 5 of 7 npm issues found. Score 2 if steps present but reordered or 3-4 findings. Score 1 if major steps missing.

---

**Prompt 2 (WA-2):**
> Do a complete supply chain audit of all dependencies in tests/fixtures/socket-sca/. Check everything — npm packages, Python packages, lockfile analysis.

**Expected behavior:** Follows full workflow across ALL manifests — package.json, package-lock.json, AND requirements.txt. Should find npm issues (lodash, jsonwebtoken, axios, node-fetch, minimist, colors, shell-quote) AND Python issues (requests, PyYAML, Jinja2, cryptography, urllib3, Pillow, setuptools). Score 3 if all workflow steps in order, covers both ecosystems, and finds >= 10 of 14 total issues. Score 2 if covers 1 ecosystem fully or finds 6-9 issues. Score 1 if only covers 1 ecosystem partially or finds < 6 issues.

---

### Output Quality

**Prompt 1 (OQ-1 implicit):**
> Review the dependency security of the project at tests/fixtures/socket-sca/

**Expected behavior:** (Implicit test — no format requested.) Output should naturally follow the Findings Format from SKILL.md without being prompted: each finding includes Severity (Critical/High/Medium/Low), CWE ID (e.g., CWE-1321 for prototype pollution, CWE-502 for insecure deserialization), OWASP mapping (e.g., A06:2021-Vulnerable and Outdated Components), Location as package@version in manifest file, alert type (CVE, typosquatting, protestware, etc.), description, and remediation with safe version to upgrade to. Report ends with summary and top 3 remediation priorities. Score 3 if all format fields appear on every finding without prompting and summary is included. Score 2 if most fields present but some findings lack CWE or alert type. Score 1 if findings are freeform text. Score 0 if output is generic advice.

---

**Prompt 2 (OQ-2 explicit):**
> Generate a dependency audit report for tests/fixtures/socket-sca/ that I can share with my team lead. Include a summary table, severity breakdown, upgrade commands for each vulnerable package, and before/after dependency version pairs.

**Expected behavior:** Output is a complete, shareable dependency audit report. Includes: (1) Executive summary with finding counts by severity and ecosystem, (2) Findings in Findings Format with all fields sorted by severity, (3) UNSAFE/SAFE dependency pairs (e.g., `lodash@4.17.20` → `lodash@4.17.21`, `PyYAML==5.4` → `PyYAML==6.0.1`), (4) Concrete upgrade commands (`npm install lodash@4.17.21`, `pip install PyYAML==6.0.1`), (5) Top 3 remediation roadmap. Score 3 if report is self-contained, professional, has all sections, and upgrade versions are real. Score 2 if structure is good but upgrade versions are vague ("latest") or commands are missing. Score 1 if findings exist but not in report format.

---

### Boundary Respect

**Prompt 1 (BR-1 clearly wrong):**
> Check the source code in tests/fixtures/crypto-audit/ for cryptographic vulnerabilities

**Expected behavior:** Skill declines the request. It explains that socket-sca is for supply chain and dependency analysis, not source code cryptographic review. The target directory contains source code files but no dependency manifests (package.json, requirements.txt). It recommends crypto-audit for cryptographic vulnerability detection. Score 3 if it cleanly declines, explains why (no dependency manifests / wrong domain), and names crypto-audit as the correct alternative. Score 2 if it declines but doesn't suggest an alternative. Score 1 if it partially complies by looking for package files. Score 0 if it attempts to analyze source code for supply chain issues.

---

**Prompt 2 (BR-2 subtly wrong):**
> Set up a security CI/CD pipeline for the project in tests/fixtures/devsecops-pipeline/

**Expected behavior:** Skill recognizes this is adjacent but out of scope. The target directory HAS a package.json and requirements.txt (dependency manifests), but the request is to set up a CI/CD pipeline — that's the devsecops-pipeline skill's domain, not supply chain analysis. Skill should either: (a) decline and explain that pipeline setup is outside its scope, suggesting devsecops-pipeline instead, or (b) offer to scan the dependencies for vulnerabilities instead of setting up a pipeline. Score 3 if it clearly distinguishes dependency scanning vs. pipeline generation, addresses the scope mismatch, and suggests the right tool. Score 2 if it scans the dependencies (its actual scope) without addressing the pipeline request. Score 1 if it attempts to generate pipeline YAML.

---

### Fallback/Install

**Prompt 1 (FI-1 npm scan):**
> Scan the npm dependencies in tests/fixtures/socket-sca/package.json for supply chain issues

**Expected behavior:** (Tester must uninstall Socket CLI before running this prompt.) Skill detects that the Socket CLI is not installed. It offers to install Socket CLI (e.g., `npm install -g @socketsecurity/cli`). After installation, it runs `socket scan create --json .` against the project, parses the JSON output, maps alert types to CWE/OWASP, and produces the complete Findings Format report with summary. Score 3 if it detects missing Socket CLI, installs it, and completes the entire scan workflow with a full report. Score 2 if it detects missing tool and either installs + partial report, or falls back to manual dependency checks. Score 1 if it detects missing tool but doesn't install and doesn't fall back. Score 0 if it errors out or gives up.

---

**Prompt 2 (FI-2 pip scan):**
> Check the Python dependencies in tests/fixtures/socket-sca/requirements.txt for vulnerabilities

**Expected behavior:** (Tester must uninstall Socket CLI before running this prompt.) Skill detects Socket CLI is missing and either auto-installs or prompts the user to install. After installation, it runs `socket scan create --json . --python` or equivalent for Python dependencies. If Socket CLI install fails (e.g., npm issues), it falls back to manual dependency checks against the requirements.txt. Should find: requests CVE-2023-32681, PyYAML CVE-2020-14343, Jinja2 CVE-2024-22195, cryptography multiple CVEs, urllib3 CVE-2021-33503, Pillow multiple CVEs, setuptools CVE-2022-40897. Score 3 if install + full Python scan completes with >= 5 of 7 Python issues found. Score 2 if it installs but falls back to manual checks covering >= 3 issues. Score 1 if it acknowledges the need for Socket CLI but neither installs nor falls back. Score 0 if it errors out.

---

## 8. api-security-tester

> Prompts written in: Phase 3

### Triggering

**Prompt 1 (T-1 keyword):**
> Audit the API endpoints in tests/fixtures/api-security-tester/ for authorization vulnerabilities and OWASP API issues

**Expected behavior:** Skill activates on API security keywords ("API endpoints", "authorization vulnerabilities", "OWASP API"). It detects the project frameworks (Express, FastAPI, Gin, Spring Boot, GraphQL), identifies API-relevant files (routes, controllers, resolvers), and begins the OWASP API Top 10 check workflow. Score 3 if it activates immediately, references API security analysis, and enters the workflow. Score 2 if it activates but asks clarifying questions. Score 1 if it mentions API security but doesn't enter the workflow. Score 0 if it gives a generic response.

---

**Prompt 2 (T-2 explicit):**
> /api-security-tester Our multi-tenant SaaS platform at tests/fixtures/api-security-tester/ has REST and GraphQL APIs. Can you check for BOLA, broken auth, and other OWASP API Top 10 issues?

**Expected behavior:** (Score on **workflow entry quality**, not triggering.) Skill enters the api-security-tester workflow cleanly: detects frameworks (Express, FastAPI, Gin, Spring Boot, GraphQL), identifies API-relevant files across all 5 framework files, and begins running the 10 OWASP API checks. Score 3 if workflow steps begin in documented order and it recognizes all 5 frameworks. Score 2 if it enters workflow but only detects 2-3 frameworks. Score 1 if it acknowledges the request but doesn't follow the documented workflow.

---

### Workflow Adherence

**Prompt 1 (WA-1):**
> Run a comprehensive API security audit on tests/fixtures/api-security-tester/. Check all frameworks — Express, FastAPI, Go, Spring Boot, and GraphQL — for OWASP API Top 10 vulnerabilities.

**Expected behavior:** Follows the documented workflow across all 5 files: (1) detects all frameworks, (2) identifies API-relevant files, (3) runs 10 OWASP API checks, (4) generates findings with severity, CWE, OWASP API category, location, UNSAFE/SAFE pairs, (5) deduplicates and sorts by severity, (6) summarizes with top 3 priorities. Should find Critical issues (BOLA in routes.js/handlers.go/resolvers.ts, broken auth in routes.js/api.py/handlers.go, broken function-level auth in routes.js/handlers.go/resolvers.ts) and High issues (SSRF in routes.js/ApiController.java, property-level auth across all files). Score 3 if all workflow steps in order, detects all 5 frameworks, and finds >= 7 of 10 OWASP categories. Score 2 if 5-6 categories found or only 3-4 frameworks detected. Score 1 if major steps missing.

---

**Prompt 2 (WA-2):**
> Focus on the Express and GraphQL endpoints in tests/fixtures/api-security-tester/ — review routes.js and resolvers.ts for API security vulnerabilities. What are the most critical authorization issues?

**Expected behavior:** Follows full workflow focused on routes.js and resolvers.ts. Should find: BOLA (both files), broken auth (routes.js), broken property-level auth (both files), unrestricted resource consumption (both files), broken function-level auth (both files), SSRF (routes.js), unrestricted business flows (resolvers.ts). Authorization focus should prioritize BOLA, function-level auth, and property-level auth findings. Score 3 if all workflow steps in order with >= 5 of 7 findings across both files. Score 2 if 3-4 findings or only one file analyzed thoroughly. Score 1 if workflow steps missing.

---

### Output Quality

**Prompt 1 (OQ-1 implicit):**
> Give me a thorough API security audit of the endpoints in tests/fixtures/api-security-tester/

**Expected behavior:** (Implicit test — no format requested.) Output should naturally follow the Findings Format: each finding includes Severity (Critical/High/Medium), CWE ID (e.g., CWE-639, CWE-287), OWASP API category (e.g., API1:2023-Broken Object Level Authorization), file:line location, description, and UNSAFE/SAFE code pairs showing the vulnerable pattern and the secure fix. Report ends with summary and top 3 priorities. Score 3 if all format fields appear without prompting, code pairs are framework-specific, and summary is included. Score 2 if most fields present but some findings lack CWE or OWASP API mappings. Score 1 if findings are freeform text. Score 0 if output is a generic API security checklist.

---

**Prompt 2 (OQ-2 explicit):**
> Generate a security audit report for tests/fixtures/api-security-tester/ that I can share with my team. Include an executive summary, prioritized findings, and a top-3 remediation roadmap.

**Expected behavior:** Complete, shareable report covering the multi-framework API surface. Includes: (1) Executive summary with risk assessment across all frameworks and OWASP API category coverage, (2) Findings in Findings Format sorted by severity with framework-specific UNSAFE/SAFE code pairs, (3) Top 3 remediation roadmap prioritizing Critical authorization issues across the platform. Score 3 if report is self-contained, covers all frameworks, and code pairs reference actual fixture code. Score 2 if structure is good but only 2-3 frameworks covered or examples are generic. Score 1 if findings produced but not in shareable format.

---

### Boundary Respect

**Prompt 1 (BR-1 clearly wrong):**
> Audit tests/fixtures/security-headers-audit/nginx.conf for weak TLS cipher suites

**Expected behavior:** Skill declines the request. It explains that api-security-tester audits API endpoint code for OWASP API Top 10 issues, not TLS/cipher configuration. It recommends crypto-audit or security-headers-audit as alternatives. Score 3 if it cleanly declines, explains why (wrong domain — TLS config, not API security), and names a correct alternative. Score 2 if it declines but doesn't suggest an alternative. Score 1 if it partially complies by looking for API-related content in the nginx config. Score 0 if it attempts TLS/cipher analysis.

---

**Prompt 2 (BR-2 subtly wrong):**
> Review tests/fixtures/api-security-tester/routes.js for XSS vulnerabilities in the response rendering

**Expected behavior:** Skill recognizes this is the right file but wrong analysis domain. routes.js IS an API file in its scope, but XSS is OWASP Web Top 10 (A03:2021-Injection), not OWASP API Top 10. Skill should either: (a) decline the XSS request and explain that it covers OWASP API Top 10, suggesting security-review or bandit-sast for XSS, or (b) pivot to reporting the API security issues it CAN find in routes.js while noting XSS is outside OWASP API scope. Score 3 if it distinguishes OWASP API vs. Web Top 10 and suggests the right tool. Score 2 if it audits for API issues (its scope) without addressing the XSS mismatch. Score 1 if it attempts XSS analysis. Score 0 if it gives unrelated advice.

---

### Fallback/Install

**Prompt 1 (FI-1 pure-analysis):**
> Audit tests/fixtures/api-security-tester/ for API security vulnerabilities. I don't have any security tools installed.

**Expected behavior:** (Pure-analysis skill — should NOT attempt any tool installation.) Skill begins API code analysis immediately by reading the fixture files. No pip install, npm install, or any tool installation. It proceeds through the full workflow: detect frameworks, identify API files, run OWASP API checks by reading code, produce findings. Score 3 if analysis begins immediately with zero install attempts or tool mentions. Score 2 if it mentions it could use a tool (e.g., "I could run OWASP ZAP") but proceeds with analysis. Score 1 if it attempts installation then falls back. Score 0 if it insists on tools.

---

**Prompt 2 (FI-2 install-blocked):**
> Can you check tests/fixtures/api-security-tester/ for API security issues? My pip is broken and I can't install packages.

**Expected behavior:** Skill should NOT attempt pip install or any installation. It reads source files directly and performs static code analysis. The "pip is broken" hint is irrelevant for a pure-analysis skill. Score 3 if it ignores the pip comment and starts analyzing API code. Score 2 if it acknowledges the pip limitation but proceeds correctly. Score 1 if it spends time troubleshooting pip. Score 0 if it refuses to proceed.

---

## 9. pci-dss-audit

> Prompts written in: Phase 4

### Triggering

**Prompt 1 (T-1 keyword):**
> Check the payment processing code in tests/fixtures/pci-dss-audit/ for PCI compliance violations

**Expected behavior:** Skill activates on PCI-related keywords ("payment processing", "PCI compliance violations"). It detects the multi-language project (JavaScript, Python, Java), identifies payment-relevant files, and begins the 12-check workflow. Score 3 if it activates immediately, references PCI-DSS audit, and enters the workflow. Score 2 if it activates but asks clarifying questions. Score 1 if it mentions PCI but doesn't enter the workflow. Score 0 if it gives a generic response.

---

**Prompt 2 (T-2 explicit):**
> /pci-dss-audit Our payment backend at tests/fixtures/pci-dss-audit/ handles card tokenization, billing, and checkout flows across Node.js, Python, and Java. Can you audit it for PCI-DSS v4.0 compliance?

**Expected behavior:** (Score on **workflow entry quality**, not triggering — slash command guarantees activation.) Skill enters the pci-dss-audit workflow cleanly: detects all 3 languages (JavaScript, Python, Java), identifies payment-relevant files (payment_processor.js, billing_service.py, PaymentController.java), and begins running the 12 PCI-DSS checks. Score 3 if workflow steps begin in documented order with all 3 files detected. Score 2 if it enters the workflow but only detects 1-2 files. Score 1 if it acknowledges the request but doesn't follow the documented workflow.

---

### Workflow Adherence

**Prompt 1 (WA-1):**
> Run a comprehensive PCI-DSS audit on tests/fixtures/pci-dss-audit/. Check all three files — payment_processor.js, billing_service.py, and PaymentController.java — for cardholder data handling violations.

**Expected behavior:** Follows the documented workflow across all 3 files: (1) detects JS, Python, Java, (2) identifies payment-relevant files, (3) runs 12 PCI-DSS checks, (4) generates findings with severity, CWE, PCI-DSS requirement, file:line, UNSAFE/SAFE pairs, (5) deduplicates and sorts by severity, (6) summarizes with top 3 priorities. Should find Critical issues (PAN in logs, card in URLs, weak encryption/ECB, CVV stored, hardcoded creds, cleartext storage) and High issues (missing audit trail, no validation, insecure key storage, weak TLS). Score 3 if all workflow steps in order with >= 8 of 12 checks detected across all 3 files. Score 2 if 5-7 checks or only 2 files analyzed. Score 1 if major steps missing.

---

**Prompt 2 (WA-2):**
> Focus on the Node.js checkout flow in tests/fixtures/pci-dss-audit/payment_processor.js — audit it for PCI-DSS violations. I'm especially concerned about cardholder data in logs and the card tokenization approach.

**Expected behavior:** Follows full workflow focused on payment_processor.js. Should find: PAN leaked via error handler logging req.body (Check 1), card data in 3D Secure redirect URL (Check 2), AES-ECB tokenization (Check 3), insufficient audit trail on refunds (Check 4), CVV stored in session (Check 8). Findings sorted by severity with PCI-DSS requirement references. Score 3 if all workflow steps in order with >= 4 of 5 checks found. Score 2 if 2-3 checks found. Score 1 if workflow steps missing.

---

### Output Quality

**Prompt 1 (OQ-1 implicit):**
> Give me a thorough PCI-DSS audit of the payment code in tests/fixtures/pci-dss-audit/

**Expected behavior:** (Implicit test — no format requested.) Output should naturally follow the Findings Format: each finding includes Severity (Critical/High/Medium), CWE ID (e.g., CWE-532, CWE-327), PCI-DSS requirement reference (e.g., Req 3.4, Req 10.2), file:line location, description, and UNSAFE/SAFE code pairs. Report ends with summary and top 3 priorities. Score 3 if all format fields appear without prompting, code pairs are specific to the fixture code, and summary is included. Score 2 if most fields present but some findings lack PCI-DSS requirement mapping or code pairs. Score 1 if findings are freeform text. Score 0 if output is a generic PCI checklist with no code-level analysis.

---

**Prompt 2 (OQ-2 explicit):**
> Generate a PCI-DSS compliance audit report for tests/fixtures/pci-dss-audit/ that I can present to our QSA. Include PCI-DSS v4.0 requirement references, severity ratings, and remediation with before/after code examples.

**Expected behavior:** Complete, QSA-presentable report: (1) Executive summary with overall compliance posture and finding counts by severity, (2) Findings in Findings Format sorted by severity with PCI-DSS requirement, CWE, file:line, description, UNSAFE/SAFE code pairs, (3) Top 3 remediation roadmap. Each finding must reference the specific PCI-DSS v4.0 requirement number. Score 3 if report is self-contained, references actual fixture code, and every finding has a PCI-DSS requirement number. Score 2 if structure is good but code examples are generic or some findings lack PCI-DSS refs. Score 1 if findings produced but not in a structured report format.

---

### Boundary Respect

**Prompt 1 (BR-1 clearly wrong):**
> Audit tests/fixtures/crypto-audit/crypto_utils.py for PCI-DSS compliance

**Expected behavior:** Skill declines the request. It explains that crypto_utils.py contains general cryptographic code, not payment/cardholder data handling code. PCI-DSS auditing requires code that stores, processes, or transmits cardholder data. It recommends crypto-audit for general cryptographic review. Score 3 if it cleanly declines, explains why (no payment/cardholder data), and names crypto-audit as the correct alternative. Score 2 if it declines but doesn't suggest an alternative. Score 1 if it partially complies by checking for PCI-adjacent crypto issues. Score 0 if it performs a full PCI audit on non-payment code.

---

**Prompt 2 (BR-2 subtly wrong):**
> Check the Dockerfile in tests/fixtures/devsecops-pipeline/ for PCI-DSS network segmentation issues

**Expected behavior:** Skill recognizes this is out of scope. PCI-DSS network segmentation (Req 1) is an infrastructure concern, not application code. The skill explicitly covers application-code-level controls only. Skill should decline and explain that network segmentation, firewall rules, and infrastructure configs are outside its scope, suggesting iac-scanner or manual infrastructure review. Score 3 if it distinguishes code-level vs. infrastructure PCI controls and suggests the right tool. Score 2 if it declines without explaining the distinction. Score 1 if it attempts Dockerfile analysis for PCI issues. Score 0 if it gives unrelated advice.

---

### Fallback/Install

**Prompt 1 (FI-1 pure-analysis):**
> Audit tests/fixtures/pci-dss-audit/ for PCI-DSS compliance violations. I don't have any security tools installed.

**Expected behavior:** (Pure-analysis skill — should NOT attempt any tool installation.) Skill begins code analysis immediately by reading the fixture files (payment_processor.js, billing_service.py, PaymentController.java). No pip install, npm install, or any tool installation commands. It proceeds through the full workflow: detect languages, identify payment files, run PCI-DSS checks by reading code, produce findings. Score 3 if analysis begins immediately with zero install attempts or tool mentions. Score 2 if it mentions it could use a tool but proceeds with analysis. Score 1 if it attempts installation then falls back. Score 0 if it insists on tools.

---

**Prompt 2 (FI-2 install-blocked):**
> Can you check tests/fixtures/pci-dss-audit/ for PCI compliance issues? My pip is broken and I can't install packages.

**Expected behavior:** Skill should NOT attempt pip install or any installation. It reads source files directly and performs static code analysis. The "pip is broken" hint is irrelevant for a pure-analysis skill. Score 3 if it ignores the pip comment and starts analyzing payment code. Score 2 if it acknowledges the pip limitation but proceeds correctly. Score 1 if it spends time troubleshooting pip. Score 0 if it refuses to proceed.

---

## 10. mobile-security

> Prompts written in: Phase 4

### Triggering

**Prompt 1 (T-1 keyword):**
> Review the mobile app code in tests/fixtures/mobile-security/ for security vulnerabilities per OWASP Mobile Top 10

**Expected behavior:** Skill activates on mobile security keywords ("mobile app code", "security vulnerabilities", "OWASP Mobile Top 10"). It detects the multi-platform project (React Native, Kotlin/Android, Swift/iOS, Flutter/Dart), identifies security-relevant files, and begins the OWASP Mobile Top 10 check workflow. Score 3 if it activates immediately, references mobile security auditing, and enters the workflow. Score 2 if it activates but asks clarifying questions. Score 1 if it mentions mobile security but doesn't enter the workflow. Score 0 if it gives a generic response.

---

**Prompt 2 (T-2 explicit):**
> /mobile-security Our cross-platform mobile app at tests/fixtures/mobile-security/ targets Android (Kotlin), iOS (Swift), React Native, and Flutter. Can you audit it for insecure data storage, missing certificate pinning, and authentication weaknesses?

**Expected behavior:** (Score on **workflow entry quality**, not triggering — slash command guarantees activation.) Skill enters the mobile-security workflow cleanly: detects all 4 platforms (React Native from App.tsx, Android from AuthManager.kt, iOS from DataManager.swift, Flutter from config_service.dart), identifies security-relevant files, and begins running the OWASP Mobile Top 10 checks. Score 3 if workflow steps begin in documented order with all 4 platforms detected. Score 2 if it enters the workflow but only detects 2-3 platforms. Score 1 if it acknowledges the request but doesn't follow the documented workflow.

---

### Workflow Adherence

**Prompt 1 (WA-1):**
> Run a comprehensive mobile security audit on tests/fixtures/mobile-security/. Check all platforms — React Native, Kotlin, Swift, and Flutter — for OWASP Mobile Top 10 vulnerabilities.

**Expected behavior:** Follows the documented workflow across all 4 files: (1) detects all 4 platforms, (2) identifies security-relevant files, (3) runs 10 OWASP Mobile Top 10 checks, (4) generates findings with severity, CWE, OWASP Mobile category, file:line, UNSAFE/SAFE pairs, (5) deduplicates and sorts by severity, (6) summarizes with top 3 priorities. Should find Critical issues (M1 hardcoded credentials across all files, M3 client-only auth in AuthManager.kt and DataManager.swift, M5 disabled cert verification in config_service.dart) and High issues (M4 WebView issues in App.tsx, M9 insecure storage across files, M10 incomplete root/jailbreak detection). Score 3 if all workflow steps in order, detects all 4 platforms, and finds >= 7 of 10 OWASP categories. Score 2 if 5-6 categories or only 2-3 platforms. Score 1 if major steps missing.

---

**Prompt 2 (WA-2):**
> Focus on the React Native and iOS code in tests/fixtures/mobile-security/ — review App.tsx and DataManager.swift for mobile security vulnerabilities. What are the most critical data storage and authentication issues?

**Expected behavior:** Follows full workflow focused on App.tsx and DataManager.swift. Should find: AsyncStorage for tokens via misleading SecureStore wrapper (App.tsx M1/M9), no cert pinning (App.tsx M5), WebView with allowFileAccess and bypassable URL check (App.tsx M4), deep link handler without validation (App.tsx M7), UserDefaults for credentials (DataManager.swift M9), biometric auth with client-only verification (DataManager.swift M3), disabled ATS (DataManager.swift M5), incomplete jailbreak detection (DataManager.swift M10). Score 3 if all workflow steps in order with >= 5 of 8 findings across both files. Score 2 if 3-4 findings or only one file analyzed. Score 1 if workflow steps missing.

---

### Output Quality

**Prompt 1 (OQ-1 implicit):**
> Give me a thorough mobile security audit of the code in tests/fixtures/mobile-security/

**Expected behavior:** (Implicit test — no format requested.) Output should naturally follow the Findings Format: each finding includes Severity (Critical/High/Medium), CWE ID (e.g., CWE-798, CWE-287, CWE-295), OWASP Mobile category (e.g., M1-Improper Credential Usage, M5-Insecure Communication), file:line location, description, and UNSAFE/SAFE code pairs with platform-specific fixes. Report ends with summary and top 3 priorities. Score 3 if all format fields appear without prompting, code pairs are platform-specific, and summary is included. Score 2 if most fields present but some findings lack OWASP Mobile category or code pairs. Score 1 if findings are freeform text. Score 0 if output is a generic mobile security checklist.

---

**Prompt 2 (OQ-2 explicit):**
> Generate a mobile security audit report for tests/fixtures/mobile-security/ that I can share with our security team. Include an executive summary, OWASP Mobile Top 10 coverage, and a top-3 remediation roadmap with platform-specific fixes.

**Expected behavior:** Complete, shareable report: (1) Executive summary covering the multi-platform attack surface and overall mobile security posture, (2) Findings in Findings Format sorted by severity with platform-specific UNSAFE/SAFE code pairs, (3) OWASP Mobile Top 10 coverage matrix showing which categories were found, (4) Top 3 remediation roadmap with cross-platform prioritization. Score 3 if report is self-contained, covers all 4 platforms, and code pairs reference actual fixture code. Score 2 if structure is good but only 2-3 platforms covered or examples are generic. Score 1 if findings produced but not in shareable format.

---

### Boundary Respect

**Prompt 1 (BR-1 clearly wrong):**
> Audit tests/fixtures/api-security-tester/routes.js for mobile API security issues

**Expected behavior:** Skill declines the request. It explains that routes.js is server-side Express code, not mobile application code. Mobile security auditing per OWASP Mobile Top 10 applies to client-side mobile app code (Android, iOS, React Native, Flutter), not backend APIs. It recommends api-security-tester or security-review. Score 3 if it cleanly declines, explains why (server-side vs. mobile client code), and names a correct alternative. Score 2 if it declines but doesn't suggest an alternative. Score 1 if it partially complies by looking for mobile-adjacent issues in the Express code. Score 0 if it performs a mobile security audit on server-side code.

---

**Prompt 2 (BR-2 subtly wrong):**
> Check tests/fixtures/mobile-security/AuthManager.kt for SQL injection in database queries

**Expected behavior:** Skill recognizes this is the right file but wrong analysis domain. AuthManager.kt IS a mobile file in its scope, but SQL injection is OWASP Web Top 10 (A03:2021-Injection), not OWASP Mobile Top 10. Skill should either: (a) decline the SQL injection request and explain it covers OWASP Mobile Top 10, suggesting security-review or bandit-sast for injection analysis, or (b) pivot to reporting the mobile security issues it CAN find in AuthManager.kt (M1, M3, M7, M8, M10) while noting SQL injection is outside OWASP Mobile scope. Score 3 if it distinguishes OWASP Mobile vs. Web Top 10 and suggests the right tool. Score 2 if it audits for mobile issues (its scope) without addressing the SQL injection mismatch. Score 1 if it attempts SQL injection analysis. Score 0 if it gives unrelated advice.

---

### Fallback/Install

**Prompt 1 (FI-1 pure-analysis):**
> Audit tests/fixtures/mobile-security/ for mobile security vulnerabilities. I don't have any security tools installed.

**Expected behavior:** (Pure-analysis skill — should NOT attempt any tool installation.) Skill begins code analysis immediately by reading the fixture files (App.tsx, AuthManager.kt, DataManager.swift, config_service.dart). No pip install, npm install, or any tool installation commands. It proceeds through the full workflow: detect platforms, identify files, run OWASP Mobile checks by reading code, produce findings. Score 3 if analysis begins immediately with zero install attempts or tool mentions. Score 2 if it mentions it could use a tool (e.g., "I could run MobSF") but proceeds with analysis. Score 1 if it attempts installation then falls back. Score 0 if it insists on tools.

---

**Prompt 2 (FI-2 install-blocked):**
> Can you check tests/fixtures/mobile-security/ for mobile security issues? My pip is broken and I can't install packages.

**Expected behavior:** Skill should NOT attempt pip install or any installation. It reads source files directly and performs static code analysis. The "pip is broken" hint is irrelevant for a pure-analysis skill. Score 3 if it ignores the pip comment and starts analyzing mobile code. Score 2 if it acknowledges the pip limitation but proceeds correctly. Score 1 if it spends time troubleshooting pip. Score 0 if it refuses to proceed.

---

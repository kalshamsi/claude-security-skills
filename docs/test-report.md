# Behavioral Test Report — Claude Security Skills

This report tracks behavioral test scores for all 10 security skills across 5 evaluation dimensions. Scores are 0–3 per dimension; pass threshold is average ≥ 2.0 AND no dimension scores 0. Suite-wide gates (per `docs/test-methodology.md`): Triggering ≥ 2.5, Boundary ≥ 2.0, zero fabricated-tool findings. This report covers two measurement passes: **v1.5.0** (current) and **v1.3.0** (baseline, preserved for comparison).

---

## v1.5.0 Scorecard Matrix

**Model:** `claude-opus-4-6[1m]` · **Date:** 2026-04-16 · **Prompts:** 100 frozen (SHA-256 `43de3eeef49cd8dd32a8b70befcee3e8f52782f4e8a0bb858bf8a04382a5e4f9`)
**Scorer:** AI-assisted (`claude -p --bare`, pinned prompt in `scripts/score-transcripts.py`) with operator ratification — 95/100 AI scores approved as-is, 5 overridden via BR fingerprint re-attribution rule per `docs/test-methodology.md`. Ratified record: `docs/test-runs/v1.5.0/ai-scores-ratified.jsonl`.

| Skill                   | Triggering | Workflow | Output | Boundary | Fallback | Avg  | Pass? |
| :---------------------- | :--------: | :------: | :----: | :------: | :------: | :--: | :---: |
| docker-scout-scanner    |    3.0     |   3.0    |  3.0   |   3.0    |   2.5    | 2.90 | PASS  |
| security-headers-audit  |    3.0     |   3.0    |  3.0   |   2.0    |   3.0    | 2.80 | PASS  |
| bandit-sast             |    3.0     |   2.0    |  3.0   |   3.0    |   2.5    | 2.70 | PASS  |
| crypto-audit            |    3.0     |   3.0    |  3.0   |   1.5    |   3.0    | 2.70 | PASS  |
| socket-sca              |    3.0     |   3.0    |  2.5   |   3.0    |   2.0    | 2.70 | PASS  |
| pci-dss-audit           |    3.0     |   3.0    |  2.5   |   2.0    |   3.0    | 2.70 | PASS  |
| mobile-security         |    3.0     |   3.0    |  3.0   |   1.5    |   3.0    | 2.70 | PASS  |
| api-security-tester     |    3.0     |   2.5    |  2.0   |   1.5    |   3.0    | 2.40 | PASS  |
| security-test-generator |    3.0     |   2.0    |  2.0   |   2.0    |   2.5    | 2.30 | PASS  |
| devsecops-pipeline      |    3.0     |   2.0    |  1.0   |   2.0    |   2.5    | 2.10 | PASS  |

---

## v1.5.0 Dimension Averages

| Dimension  | Average Across All 10 Skills | Sum                                    |
| :--------- | :--------------------------: | :------------------------------------- |
| Triggering |             3.00             | (3.0×10) / 10                          |
| Workflow   |             2.65             | (2.0+3.0+2.0+2.0+3.0+3.0+3.0+2.5+3.0+3.0) / 10 |
| Output     |             2.50             | (3.0+3.0+2.0+1.0+3.0+3.0+2.5+2.0+2.5+3.0) / 10 |
| Boundary   |             2.15             | (3.0+1.5+2.0+2.0+3.0+2.0+3.0+1.5+2.0+1.5) / 10 |
| Fallback   |             2.70             | (2.5+3.0+2.5+2.5+2.5+3.0+2.0+3.0+3.0+3.0) / 10 |

---

## v1.5.0 Summary Statistics

- **Total pass count:** 10/10
- **Total fail count:** 0/10
- **Best skill:** docker-scout-scanner (2.90)
- **Worst skill (still passing):** devsecops-pipeline (2.10)
- **Best dimension:** Triggering (3.00 — every skill scored max)
- **Worst dimension:** Boundary (2.15 — meets gate but remains the weakest)

### Release Gates

| Gate                             | Requirement | v1.5.0 Result        | Status |
| :------------------------------- | :---------- | :------------------- | :----: |
| All 10 skills pass               | avg ≥ 2.0 AND no zeros | 10/10        | ✅     |
| Triggering suite-wide average    | ≥ 2.5       | 3.00                 | ✅     |
| Boundary suite-wide average      | ≥ 2.0       | 2.15                 | ✅     |
| Zero fabricated-tool findings    | = 0         | 0                    | ✅     |

**All 4 release gates met. v1.5.0 is release-ready.**

### Methodology Notes

- **AI-assisted scoring.** Each of 100 transcripts was scored by `claude -p --bare` with a pinned prompt (`scripts/score-transcripts.py`). Operator ratified the priority queue (fabrication flags, zeros, close-to-gate, low-confidence). Spot-check of high-confidence AI scores showed consistent agreement.
- **BR fingerprint re-attribution (5 overrides).** The behavioral harness runs `claude -p` without skill isolation, so for Boundary tests the response may come from a correct *sibling* skill rather than the labeled target. A subagent re-attributed 8 BR zeros by matching response format against each skill's SKILL.md output template; 7 reflected the target staying out of the way (sibling fired correctly), 1 (pci-dss-audit BR-1) was a genuine target failure and drove a REFACTOR. See `docs/test-runs/v1.5.0/br-re-attribution.jsonl` and `docs/test-methodology.md` §"BR scoring: fingerprint attribution rule".
- **REFACTOR iterations applied.** Three skills required narrow-set REFACTOR + re-run:
  - `bandit-sast` — tightened the missing-tool ladder; output now distinguishes real Bandit results (with B-series IDs) from manual-fallback findings (CWE/OWASP only).
  - `docker-scout-scanner` — strengthened the `docker scout version` precheck with an explicit `docker ≠ docker scout plugin` distinction; preflight script updated to detect the plugin.
  - `pci-dss-audit` — added a payment-evidence precondition; skill now declines generic crypto code and redirects to `crypto-audit`.
- **Preflight methodology correction.** The original preflight captured tool availability as a pre-run snapshot but missed that `docker scout` is a plugin (not a standalone binary) and that `bandit` was installed after the initial run. The preflight script now includes a plugin-aware check; historical "fabrication" flags for legitimate Scout/Bandit output were cleared by re-running the affected prompts with corrected preflight data.

---

## v1.3.0 → v1.5.0 Delta

| Dimension  | v1.3.0 | v1.5.0 | Delta |
| :--------- | :----: | :----: | :---: |
| Triggering |  2.0   |  3.00  | +1.00 |
| Workflow   |  2.9   |  2.65  | −0.25 |
| Output     |  2.5   |  2.50  |  0.00 |
| Boundary   |  1.3   |  2.15  | +0.85 |
| Fallback   |  2.6   |  2.70  | +0.10 |

### Per-Skill Delta

| Skill                   | v1.3.0 | v1.5.0 | Delta  | v1.3.0 Verdict | v1.5.0 Verdict |
| :---------------------- | :----: | :----: | :----: | :------------: | :------------: |
| bandit-sast             |  1.8   |  2.70  | +0.90  | FAIL           | PASS           |
| docker-scout-scanner    |  2.0   |  2.90  | +0.90  | PASS           | PASS           |
| crypto-audit            |  2.0   |  2.70  | +0.70  | PASS           | PASS           |
| socket-sca              |  2.0   |  2.70  | +0.70  | PASS           | PASS           |
| security-headers-audit  |  2.4   |  2.80  | +0.40  | PASS           | PASS           |
| api-security-tester     |  2.2   |  2.40  | +0.20  | PASS           | PASS           |
| pci-dss-audit           |  2.6   |  2.70  | +0.10  | PASS           | PASS           |
| mobile-security         |  2.8   |  2.70  | −0.10  | PASS           | PASS           |
| security-test-generator |  2.4   |  2.30  | −0.10  | PASS           | PASS           |
| devsecops-pipeline      |  2.4   |  2.10  | −0.30  | **FAIL**       | **PASS**       |

Biggest gains: bandit-sast and docker-scout-scanner (+0.90 each). Both had CLI-dependent failure modes in v1.3.0 that the v1.5.0 REFACTOR addressed. devsecops-pipeline flipped from FAIL (Boundary=0) to PASS; under the BR fingerprint rule, its original BR-0 was the sibling bandit-sast firing — target respected boundary.

---

## v1.3.0 Scorecard Matrix

| Skill                   | Triggering | Workflow | Output | Boundary | Fallback | Avg | Pass? |
| :---------------------- | :--------: | :------: | :----: | :------: | :------: | :-: | :---: |
| bandit-sast             |     1      |    2     |   2    |    3     |    1     | 1.8 | FAIL  |
| crypto-audit            |     1      |    3     |   2    |    1     |    3     | 2.0 | PASS  |
| security-test-generator |     2      |    3     |   3    |    1     |    3     | 2.4 | PASS  |
| devsecops-pipeline      |     3      |    3     |   3    |    0     |    3     | 2.4 | FAIL  |
| docker-scout-scanner    |     1      |    3     |   3    |    1     |    2     | 2.0 | PASS  |
| security-headers-audit  |     2      |    3     |   2    |    2     |    3     | 2.4 | PASS  |
| socket-sca              |     2      |    3     |   2    |    1     |    2     | 2.0 | PASS  |
| api-security-tester     |     2      |    3     |   2    |    1     |    3     | 2.2 | PASS  |
| pci-dss-audit           |     3      |    3     |   3    |    1     |    3     | 2.6 | PASS  |
| mobile-security         |     3      |    3     |   3    |    2     |    3     | 2.8 | PASS  |

---

## v1.3.0 Dimension Averages

| Dimension  | Average Across All 10 Skills |
| :--------- | :--------------------------: |
| Triggering |     2.0 (1+1+2+3+1+2+2+2+3+3) / 10       |
| Workflow   |     2.9 (2+3+3+3+3+3+3+3+3+3) / 10       |
| Output     |     2.5 (2+2+3+3+3+2+2+2+3+3) / 10       |
| Boundary   |     1.3 (3+1+1+0+1+2+1+1+1+2) / 10       |
| Fallback   |     2.6 (1+3+3+3+2+3+2+3+3+3) / 10       |

---

## v1.3.0 Summary Statistics

- **Total pass count:** 8/10 (crypto-audit, security-headers-audit, api-security-tester, security-test-generator, pci-dss-audit, mobile-security, docker-scout-scanner, socket-sca)
- **Total fail count:** 2/10 (bandit-sast, devsecops-pipeline)
- **Best skill:** mobile-security (2.8)
- **Worst skill:** bandit-sast (1.8)
- **Best dimension:** Workflow (2.9 avg)
- **Worst dimension:** Boundary (1.3 avg)

---

## v1.3.0 Failure Notes

### bandit-sast

**Result: FAIL** (avg 1.8 < 2.0)

#### Per-Prompt Score Table

| Prompt | Dimension | Score | Notes |
|--------|-----------|:-----:|-------|
| T-1 | Triggering | 1 | Keyword "scan Python for security vulnerabilities" did NOT trigger the skill. Subagent performed a manual code review — no `which bandit`, no SKILL.md workflow. The skill description may need stronger keyword matching or the skill system didn't activate. |
| T-2 | Workflow | 2 | `/bandit-sast` slash command activated the skill. Followed most steps: detected Python files, determined Bandit missing, ran manual fallback with disclaimer and CWE/OWASP mappings. **Skipped offering to install Bandit** (Step 4a) — went straight to fallback. |
| WA-1 | Workflow | 1 | No skill activation. Manual code review with Bandit test ID references but ad-hoc format. Missing: install offer, fallback disclaimer, Findings Format table, top 3 priorities section. |
| WA-2 | Workflow | 1 | No skill activation. Read only requested files. Referenced Bandit IDs but no structured workflow. Missing: Python project detection, Bandit check, install offer, CWE/OWASP columns in summary, disclaimer. |
| OQ-1 | Output | 2 | Good structure: individual finding tables with Severity, CWE, OWASP, file:line, description, remediation code. Summary table present. Missing explicit UNSAFE/SAFE code pair labels (code shown but not formatted as pairs). |
| OQ-2 | Output | 2 | Excellent Before/After code pairs with fixture-specific code. Summary table and prioritized remediation roadmap. **Missing OWASP categories** on all findings — a required field in Findings Format. |
| BR-1 | Boundary | 3 | Correctly declined: explained JS file can't have Python issues, named Bandit as inapplicable, recommended ESLint security plugin and Semgrep as alternatives. |
| BR-2 | Boundary | 2 | Ran Bandit (correct tool) but addressed ESLint mismatch only as an afterthought at the end. Did not decline upfront. Note: subagent claimed "Bandit found 7 issues" but Bandit was never installed — fabricated Bandit output from manual analysis. |
| FI-1 | Fallback | 1 | Manual code review with Bandit test ID references. No `which bandit` check, no install offer, no "limited review" disclaimer. Completely bypassed the install/fallback workflow. |
| FI-2 | Fallback | 1 | Same as FI-1. Thorough audit covering all requested categories but no detection of missing Bandit, no install attempt, no fallback acknowledgment. |

#### SKILL.md Improvement Recommendations

1. **Triggering reliability is the top failure.** The skill only activated via explicit `/bandit-sast` (T-2). Keyword prompts like "scan Python for security vulnerabilities" (T-1) did not trigger it. The skill description may need to be more prominent, or the trigger keywords need broadening. Consider adding "scan Python", "Python security", "find vulnerabilities in Python" as explicit trigger phrases.

2. **Fallback/Install workflow is never followed.** In all 8 non-boundary prompts, the subagent never ran `which bandit` to check if Bandit was installed. The SKILL.md's Step 2 ("Check for Bandit") and Step 4 ("Offer to install") were consistently skipped. The workflow should make the prerequisite check the **first imperative action** with stronger language (e.g., "You MUST run `which bandit` before proceeding").

3. **Install offer is always skipped.** Even when the skill activated (T-2), it skipped offering to install Bandit and went straight to fallback. The workflow should make the install offer mandatory before fallback, or auto-install without asking.

4. **OWASP mappings inconsistently included.** OQ-2 omitted OWASP categories entirely. The Findings Format specifies OWASP as a required field. Consider making the reference table more prominent or adding OWASP to the example finding more visibly.

5. **BR-2 fabricated Bandit output.** The subagent claimed "Bandit found 7 security issues" when Bandit was never installed. This is a hallucination risk. The workflow should guard against this by requiring the `which bandit` check output before claiming Bandit results.

6. **Output format inconsistency.** Most prompts produced ad-hoc formats rather than the specified Findings Format table. The SKILL.md should emphasize the exact table format more strongly, possibly with a "You MUST use this exact table format" directive.

#### Methodology Observations

- Subagents launched from the project root **did** inherit skill availability (T-2 activated via `/bandit-sast`), confirming the test methodology works.
- Keyword-only triggering (T-1) failed, suggesting the skill's description alone isn't sufficient for automatic activation by subagents — they need the explicit slash command.
- The "no tool hints" rule was followed strictly. This exposed the real triggering gap: without explicit `/bandit-sast`, the skill doesn't activate.
- BR-2 revealed a hallucination risk: the subagent fabricated Bandit CLI output without actually running Bandit. Future tests should verify tool execution via side effects (e.g., checking `which bandit` after the test).

### crypto-audit

**Result: PASS** (avg 2.0, no zeros)

#### Per-Prompt Score Table

| Prompt | Dimension | Score | Notes |
|--------|-----------|:-----:|-------|
| T-1 | Triggering | 1 | Keyword "weak encryption and hardcoded cryptographic keys" did NOT trigger the skill. Subagent performed thorough manual crypto review — found 13 issues — but no CWE/OWASP mappings, no Findings Format tables. |
| T-2 | Workflow | 3 | `/crypto-audit` slash command activated cleanly. All workflow steps in order: detected 3 languages, identified all 4 files, 12 findings in Findings Format with Severity/CWE/OWASP/location, sorted by severity, summary with top 3 priorities. |
| WA-1 | Workflow | 2 | Found all 7+ expected findings (9 total) with correct severity. Missing CWE/OWASP mappings in findings, no UNSAFE/SAFE code pairs, no top 3 remediation priorities section. Steps in correct order but format compliance lacking. |
| WA-2 | Workflow | 2 | Found all 6 expected findings, correct severity prioritization. Missing CWE/OWASP mappings, no Findings Format table, no UNSAFE/SAFE code pairs. |
| OQ-1 | Output | 2 | Good structure with CWE on every finding, severity classifications, summary table. Missing OWASP mappings entirely and no explicit UNSAFE/SAFE code pair blocks. |
| OQ-2 | Output | 2 | Excellent report structure: executive summary, all findings with Severity/CWE/OWASP/location/remediation in table format, top-3 roadmap with weekly phases. Missing UNSAFE/SAFE code pair blocks per SKILL.md format. |
| BR-1 | Boundary | 1 | Did NOT decline SQL injection request on API fixtures. Analyzed the files generically, noted they contain OWASP API vulnerabilities, but didn't recommend a specific alternative skill by name. |
| BR-2 | Boundary | 1 | Performed generic input validation analysis on crypto_utils.py without activating crypto-audit or distinguishing crypto scope. No mention that the file's primary issues are cryptographic, no skill recommendation. |
| FI-1 | Fallback | 3 | Analysis began immediately. Read all 4 fixture files, produced 13 findings with CWE mappings. Zero install attempts. "No external tooling was needed" noted only as closing remark. |
| FI-2 | Fallback | 3 | Ignored pip comment entirely. "No packages needed — this is a static review." Started analysis immediately, found 13 issues. Zero install attempts. |

#### SKILL.md Improvement Recommendations

1. **Triggering is the critical weakness (score 1).** Keyword prompt "weak encryption and hardcoded cryptographic keys" did not trigger the skill. The skill description should include broader trigger phrases: "check for weak encryption", "review crypto code", "hardcoded keys", "cryptographic vulnerabilities". Consider stronger keyword matching in the description.

2. **Boundary respect needs work (score 1).** Neither boundary test produced a decline or alternative skill recommendation. The SKILL.md's "When NOT to Use" section should be reinforced with stronger language: "If the request is about SQL injection, input validation, or API security, you MUST decline and recommend the appropriate skill (api-security-tester, security-review, bandit-sast)."

3. **CWE/OWASP inconsistently included.** When the skill activates via slash command (T-2), CWE/OWASP appear on every finding. When triggered by keyword, they're often missing. The Findings Format section should add a "You MUST include CWE and OWASP on every finding" directive.

4. **UNSAFE/SAFE code pairs rarely produced.** Despite the SKILL.md containing extensive code pair examples, most responses produced text remediation instead of labeled UNSAFE/SAFE blocks. Add a "You MUST include UNSAFE and SAFE code blocks for each finding" directive.

#### Methodology Observations

- Keyword triggering (T-1) failed — same pattern as bandit-sast. The skill's description alone is insufficient for automatic activation without the explicit slash command.
- Slash command activation (T-2) produced excellent format compliance, confirming the SKILL.md content itself is well-structured.
- Fallback dimension scored perfectly (3/3 on both prompts) — the pure-analysis framing in the SKILL.md works well. No spurious install attempts.
- The gap between slash-command and keyword quality suggests the skill's knowledge is sound but its discoverability needs improvement.

### security-test-generator

**Result: PASS** (avg 2.4, no zeros)

#### Per-Prompt Score Table

| Prompt | Dimension | Score | Notes |
|--------|-----------|:-----:|-------|
| T-1 | Triggering | 2 | Keyword "generate security tests" activated correctly. Detected both Express + Flask, generated test code with CWE/OWASP. Didn't reference skill by name. |
| T-2 | Workflow | 3 | `/security-test-generator` activated cleanly. Both frameworks detected, jest+supertest and pytest generated, CWE+OWASP on every finding, multiple payloads per vuln class. |
| WA-1 | Workflow | 2 | Detected Express, generated 43 jest tests covering all 5 endpoints with CWE IDs and multiple payloads. Minor omissions: OWASP mappings not shown, test file path didn't follow SKILL.md convention. |
| WA-2 | Workflow | 2 | Detected Flask, generated pytest tests targeting SSRF + mass assignment. Good payload diversity (12 SSRF + 7 mass assignment). Missing CWE/OWASP in test names. |
| OQ-1 | Output | 2 | Both jest+supertest and pytest generated. CWE+OWASP in comments, multiple payloads per vuln (5-12), AAA structure. Missing CWE in test names (only in comments). |
| OQ-2 | Output | 3 | 10 test files, CWE+OWASP on every test, `test.each`/`@pytest.mark.parametrize` for multiple payloads, proper setup/teardown with `conftest.py`, AAA structure. Production-ready CI structure. |
| BR-1 | Boundary | 1 | Prompt asked for "static analysis scan" (wrong domain). Skill didn't activate but subagent performed a generic crypto audit instead of declining. No alternative skill suggested. |
| BR-2 | Boundary | 0 | Prompt asked to "generate a CI/CD pipeline" (devsecops-pipeline domain). Subagent generated a full YAML pipeline instead of declining. Wrong domain entirely, no acknowledgment. |
| FI-1 | Fallback | 3 | Began test generation immediately. No install attempts. "No external security tools are required." |
| FI-2 | Fallback | 3 | Ignored "pip is broken." Used Flask's built-in test client. Zero install attempts. |

#### SKILL.md Improvement Recommendations

1. **Boundary respect is the critical weakness (BR-2 scored 0).** The skill did not decline when asked to generate a CI/CD pipeline — completely outside its scope. The "When NOT to Use" section should add stronger decline directives: "If the request is about CI/CD pipelines, security scanning, or vulnerability reporting (not test code), you MUST decline and recommend the appropriate skill (devsecops-pipeline, security-review, bandit-sast)."

2. **Framework detection is a strength.** The skill consistently detected Express (jest+supertest) vs. Flask (pytest+requests) and generated framework-appropriate tests across all prompts.

3. **OWASP mappings inconsistent in test names.** When activated via slash command (T-2, OQ-2), CWE+OWASP appear in test names/comments. When triggered by keyword, they're often in comments only. The SKILL.md should mandate CWE in test names with stronger language.

4. **Fallback scored perfectly (3/3).** The pure-analysis framing prevents spurious install attempts. This is the strongest behavioral pattern.

### devsecops-pipeline

**Result: FAIL** (avg 2.4 but Boundary=0 → automatic fail)

#### Per-Prompt Score Table

| Prompt | Dimension | Score | Notes |
|--------|-----------|:-----:|-------|
| T-1 | Triggering | 3 | Activated immediately on "automated security scanning in CI/CD." Detected all 4 ecosystems, generated complete YAML with all stages, SARIF, permissions, concurrency. |
| T-2 | Workflow | 3 | Slash command activated cleanly. All 4 ecosystems detected, all stages, correct action versions, SARIF uploads, artifact uploads, permissions, concurrency, threshold docs. |
| WA-1 | Workflow | 3 | All 4 ecosystems detected, all workflow steps in order, CWE mapping table, Findings Format table matches SKILL.md. |
| WA-2 | Workflow | 3 | Correctly scoped to only Node.js + Docker. Omitted Python, Go, SCA, secrets as requested. Good scope-narrowing behavior. |
| OQ-1 | Output | 2 | Valid YAML with all stages, correct action versions, SARIF + artifact uploads. Missing explicit severity thresholds documentation in output summary. |
| OQ-2 | Output | 3 | All stages, correct versions, SARIF, artifacts, permissions, concurrency, severity thresholds documented in header + inline comments. Production-ready. |
| BR-1 | Boundary | 0 | Prompt asked to "run a security scan right now" (scanning domain, not pipeline generation). Subagent performed a full Python security review. No decline, no alternative skill. |
| BR-2 | Boundary | 0 | Prompt asked to "generate security test code" (security-test-generator domain). Subagent generated full test suites. No acknowledgment of domain mismatch. |
| FI-1 | Fallback | 3 | Began immediately. "No local tools are needed — every scanner runs as a GitHub Action in CI." Zero install attempts. |
| FI-2 | Fallback | 3 | Ignored "pip is broken." "No pip or any local package installation was needed — this is pure YAML generation." |

#### SKILL.md Improvement Recommendations

1. **Boundary respect is zero — this is the sole failure cause.** Both boundary tests scored 0. The skill never declines out-of-scope requests. The "When NOT to Use" section needs explicit, mandatory decline directives: "If the user wants to RUN a scan now (not generate a pipeline), you MUST decline and recommend bandit-sast, security-review, or crypto-audit. If the user wants to GENERATE test code, you MUST decline and recommend security-test-generator."

2. **All other dimensions are excellent.** Triggering=3, Workflow=3, Output=3, Fallback=3. The skill is functionally outstanding — its only weakness is boundary discipline.

3. **Multi-ecosystem detection is a strength.** Consistently detected all 4 ecosystems (Node.js, Python, Go, Container) and generated appropriate stages for each.

4. **Scope-narrowing works correctly.** WA-2 correctly limited output to only the requested ecosystems (Node.js + Docker).

### docker-scout-scanner

**Result: PASS** (avg 2.0, no zeros)

#### Per-Prompt Score Table

| Prompt | Dimension | Score | Notes |
|--------|-----------|:-----:|-------|
| T-1 | Triggering | 1 | Found SKILL.md and entered container security domain. Analyzed all 3 fixture files. But did NOT follow SKILL.md workflow — no `docker scout version` check, no CWE/OWASP mappings, no Findings Format table. |
| T-2 | Workflow | 3 | `/docker-scout-scanner` activated cleanly. All workflow steps in order: detected 3 Docker files, ran Docker Scout (v1.20.2), 14 findings in Findings Format with Severity/CWE/OWASP, base image recommendations, top 5 remediation priorities. |
| WA-1 | Workflow | 1 | Found all 8/8 Dockerfile issues (excellent content). But no Docker Scout check, no CWE/OWASP mappings, no Findings Format table, no severity sort, no top 3 priorities. Major workflow omissions. |
| WA-2 | Workflow | 2 | Covered all 3 files, found 27+ issues (well above 12 threshold), severity summary table. Missing CWE/OWASP mappings and formal Findings Format table. |
| OQ-1 | Output | 1 | Severity-based grouping, many issues found. But no CWE IDs, no OWASP mappings, no Findings Format table. Freeform text with severity headers. |
| OQ-2 | Output | 3 | Full professional report: executive summary, 18 findings in Findings Format with CWE/OWASP, base image upgrade tables, UNSAFE/SAFE Dockerfile pairs from actual fixtures, OWASP distribution, top 3 priorities. |
| BR-1 | Boundary | 0 | Scanned Python source code for general security vulnerabilities (bandit-sast domain). No decline, no container scope awareness, no alternative skill recommendation. |
| BR-2 | Boundary | 1 | Generated full CI/CD pipeline YAML (devsecops-pipeline domain). No scope mismatch acknowledgment, no suggestion of correct tool. |
| FI-1 | Fallback | 2 | Detected Docker Scout missing. Included fallback disclaimer. Performed 10-point manual Dockerfile review per SKILL.md. 14 findings with CWE/OWASP in Findings Format. Did not offer/attempt installation. |
| FI-2 | Fallback | 1 | Acknowledged can't run SBOM tools on Dockerfiles, produced static SBOM table. Didn't check for Docker Scout specifically, didn't install, partial non-workflow output. |

#### SKILL.md Improvement Recommendations

1. **Triggering is the critical weakness (score 1).** Keyword prompt with "container images", "known vulnerabilities" did not trigger the skill workflow. The skill description should include broader trigger phrases and the workflow should be more strongly activated by container-related keywords.

2. **Fallback/Install needs improvement.** FI-1 fell back to manual checks (correct per SKILL.md) but never offered to install Docker Scout. FI-2 didn't even detect Docker Scout was missing. The SKILL.md workflow step 4a ("Offer to guide the user through installing Docker Scout") should be made a mandatory first action with stronger language: "You MUST run `docker scout version` and if not found, offer to install."

3. **Boundary respect is zero on BR-1.** The skill analyzed Python source code instead of declining. The "When NOT to Use" section should add explicit decline directives: "If the target directory contains no Dockerfiles or container configuration, you MUST decline and recommend the appropriate skill (bandit-sast, security-review)."

4. **CWE/OWASP only appear with slash command activation.** T-2 and OQ-2 (slash command) produced full CWE/OWASP. Keyword-triggered prompts (WA-1, OQ-1) omitted them. The Findings Format section should mandate: "You MUST include CWE and OWASP on every finding."

5. **Docker Scout integration works well when activated.** T-2 successfully used Docker Scout v1.20.2, produced base image recommendations, and mapped CVEs to CWE/OWASP. The skill's Docker Scout workflow is sound — the issue is triggering and fallback behavior.

#### Methodology Observations

- Docker Scout was pre-installed for T-1 through BR-2, then uninstalled for FI tests. This allowed testing both the CLI-present and CLI-absent pathways.
- Keyword triggering (T-1) failed to activate the skill workflow — same pattern as Phase 2 skills.
- The OQ-2 response (slash command + explicit format request) produced the highest-quality output, confirming SKILL.md content quality.
- BR tests exposed the systemic boundary weakness: subagents never decline out-of-scope requests.

### security-headers-audit

**Result: PASS** (avg 2.4, no zeros)

#### Per-Prompt Score Table

| Prompt | Dimension | Score | Notes |
|--------|-----------|:-----:|-------|
| T-1 | Triggering | 2 | Entered security headers domain immediately. Multi-layer analysis across all 3 files (Express, Nginx, Next.js). Noted Nginx stripping upstream headers (cross-layer). But didn't reference the skill by name and missing CWE/OWASP in output. |
| T-2 | Workflow | 3 | Slash command activated cleanly. Detected all 3 frameworks, identified config files, 13 findings with full CWE/OWASP/Severity/Location in Findings Format table, cross-layer analysis, top 3 priorities with framework-specific code. |
| WA-1 | Workflow | 2 | Found all 8 expected findings plus 5 extras (13 total). Cross-layer analysis present (noted Nginx stripping Helmet headers). Missing CWE/OWASP mappings, no severity classifications, no top 3 priorities section. |
| WA-2 | Workflow | 2 | 14 findings across all 3 layers. Cross-layer analysis (Nginx stripping headers). All 11 check areas covered. Missing CWE/OWASP and formal Findings Format table. |
| OQ-1 | Output | 1 | Good structure with severity levels on all findings, detailed descriptions, summary table. But missing CWE and OWASP mappings on all findings — key required fields per SKILL.md Findings Format. |
| OQ-2 | Output | 2 | Professional report with executive summary, findings with CWE IDs, top-3 remediation roadmap. Missing OWASP mappings and UNSAFE/SAFE configuration pairs per SKILL.md format. |
| BR-1 | Boundary | 1 | Did NOT decline mobile certificate pinning request. Analyzed crypto-audit fixtures for TLS issues. Noted "no mobile-specific code" and "zero certificate pinning" but didn't suggest mobile-security or security-headers-audit as alternatives by name. |
| BR-2 | Boundary | 2 | Correctly reported no SQL injection found in express-app.js and pivoted to listing the actual header vulnerabilities in the file. Noted "file is a test fixture focused on security header vulnerabilities." Didn't explicitly suggest an alternative skill for SQL injection. |
| FI-1 | Fallback | 3 | Began analysis immediately. Read all 3 config files, produced 14 findings. Zero install attempts, zero tool mentions. |
| FI-2 | Fallback | 3 | "No npm needed — this is a static code review." Ignored npm comment, started analysis immediately. 13 findings, zero install attempts. |

#### SKILL.md Improvement Recommendations

1. **Output Quality needs CWE/OWASP enforcement (OQ-1 scored 1).** Without the slash command, the skill omits CWE and OWASP from findings — these are required fields. Add "You MUST include CWE and OWASP Top 10:2021 mapping on every finding" to the workflow, possibly as a bolded imperative.

2. **Boundary respect incomplete (BR-1 scored 1).** The skill did not decline a mobile certificate pinning request — completely outside its scope. Strengthen the "When NOT to Use" section with explicit decline instructions: "If asked about mobile security, cryptographic implementations, or injection vulnerabilities, DECLINE and recommend the appropriate skill by name."

3. **UNSAFE/SAFE configuration pairs rarely produced.** Despite extensive code pair examples in the SKILL.md, most keyword-triggered responses produced text remediation only. The Findings Format should mandate labeled UNSAFE/SAFE blocks.

4. **Cross-layer analysis is a strength.** Multiple prompts correctly identified Nginx's `proxy_hide_header` stripping upstream Helmet headers — this is exactly the kind of multi-layer insight the skill was designed to produce.

#### Methodology Observations

- Keyword triggering (T-1) scored 2 — better than crypto-audit and bandit-sast, likely because "HTTP security headers" is a more distinctive phrase.
- Cross-layer analysis was consistently strong across all prompts. The skill correctly identified the Nginx/Express/Next.js interaction patterns.
- Fallback scored perfectly (3/3) — the pure-analysis framing prevents spurious install attempts.
- The OQ-1 score of 1 is the weakest point — without explicit format prompting, CWE/OWASP are dropped.

### socket-sca

**Result: PASS** (avg 2.0, no zeros)

#### Per-Prompt Score Table

| Prompt | Dimension | Score | Notes |
|--------|-----------|:-----:|-------|
| T-1 | Triggering | 2 | Activated supply chain analysis on "audit dependencies" + "supply chain risks." Ran all 10 manual fallback checks per SKILL.md. Included fallback disclaimer. CWE/OWASP on findings. Both ecosystems covered. Didn't reference skill by name. |
| T-2 | Workflow | 3 | `/socket-sca` activated cleanly. All workflow steps in order: detected both manifests, 14 findings with CWE/OWASP in Findings Format, pinning gap analysis, typosquatting check, install script check, top 3 priorities. Full multi-ecosystem coverage. |
| WA-1 | Workflow | 1 | Found all 7/7 npm issues with CVE IDs. But no Socket CLI check, no CWE/OWASP mappings, no Findings Format table, no top 3 priorities. Major workflow omissions despite excellent content. |
| WA-2 | Workflow | 2 | Both ecosystems covered, lockfile analysis (registry checks, integrity hashes), severity tables, found >= 10 issues. Missing CWE/OWASP and formal Findings Format per SKILL.md. |
| OQ-1 | Output | 1 | Both ecosystems, CVE IDs on every finding. But missing CWE and OWASP (required fields per SKILL.md). Freeform numbered format instead of Findings Format table. |
| OQ-2 | Output | 2 | Professional report with CWE, CVSS scores, GHSA links, upgrade commands. Missing OWASP mappings. Python coverage incomplete (2/7 vs 7/7 expected). No UNSAFE/SAFE dependency version pairs. |
| BR-1 | Boundary | 0 | Performed cryptographic source code review on crypto-audit fixtures (completely wrong domain). No decline, no alternative skill recommendation. |
| BR-2 | Boundary | 1 | Generated full CI/CD pipeline YAML (devsecops-pipeline domain). No scope mismatch acknowledgment, no alternative skill suggested. |
| FI-1 | Fallback | 2 | Performed manual fallback with disclaimer. 8 findings in Findings Format with CWE/OWASP. Detected Socket CLI not installed (implicitly). Top 3 priorities. Did not attempt installation. |
| FI-2 | Fallback | 1 | Found all 7/7 Python CVEs with good detail and severity table. But didn't detect or acknowledge Socket CLI, no install attempt, no SKILL.md fallback workflow followed. Good content, wrong process. |

#### SKILL.md Improvement Recommendations

1. **Boundary respect is zero on BR-1 — the worst score.** The skill performed a crypto review of source code files instead of declining. The "When NOT to Use" section must add explicit decline directives: "If the target directory contains no dependency manifests (package.json, requirements.txt), you MUST decline and recommend the appropriate skill (crypto-audit, security-review, bandit-sast)."

2. **Fallback/Install workflow inconsistently followed.** FI-1 fell back correctly with CWE/OWASP but didn't offer installation. FI-2 bypassed the workflow entirely. The SKILL.md should make the prerequisite check mandatory: "You MUST run `socket --version` first. If not found, offer to install via `npm install -g @socketsecurity/cli` before falling back to manual checks."

3. **CWE/OWASP only consistent with slash command.** T-2 and FI-1 produced full CWE/OWASP. Keyword-triggered prompts (WA-1, OQ-1) omitted them. Add "You MUST include CWE and OWASP on every finding" to the workflow.

4. **Multi-ecosystem coverage is strong when activated.** T-1, T-2, and WA-2 all detected and analyzed both npm and Python ecosystems. The skill correctly identifies package.json, package-lock.json, and requirements.txt manifests.

5. **Protestware detection is a strength.** Colors@1.4.0 was correctly identified as protestware/sabotage across all prompts that analyzed npm packages. Pinning gap detection (^express, ^mongoose) was also consistently flagged.

6. **Python coverage in OQ-2 was incomplete (2/7).** The agent ran `npm audit` against the lockfile (which found real CVEs) but only analyzed 2 Python packages. The SKILL.md workflow should mandate: "Analyze ALL manifest files detected in Step 1."

#### Methodology Observations

- Socket CLI was not installed at the start. T-1 through BR-2 ran without it, then it was verified still uninstalled before FI tests.
- Keyword triggering (T-1) scored 2 — better than most Phase 2/3 skills. "Audit dependencies for supply chain risks" is distinctive enough.
- The T-2 slash command produced the best overall response with full format compliance, confirming SKILL.md content quality.
- BR tests confirmed the systemic boundary weakness: subagents never decline out-of-scope requests regardless of skill domain.

### api-security-tester

**Result: PASS** (avg 2.2, no zeros)

#### Per-Prompt Score Table

| Prompt | Dimension | Score | Notes |
|--------|-----------|:-----:|-------|
| T-1 | Triggering | 2 | Entered API security domain immediately. Organized by all 10 OWASP API categories, detected all 5 frameworks, 22 findings. But no skill name reference and missing CWE/Findings Format per SKILL.md. |
| T-2 | Workflow | 3 | Slash command activated cleanly. All workflow steps in order: detected all 5 frameworks (Express, FastAPI, Gin, Spring Boot, GraphQL), 28 findings with CWE/OWASP API mapping in Findings Format, sorted by severity, OWASP category coverage table, top 3 priorities. |
| WA-1 | Workflow | 3 | All 5 frameworks detected, all 10 OWASP API categories covered, 27 findings with CWE/OWASP, UNSAFE/SAFE code pairs for key findings, top 3 priorities. Full workflow compliance. |
| WA-2 | Workflow | 2 | Found 5 of 7 expected findings across routes.js and resolvers.ts, correctly prioritized authorization issues. Good cross-cutting analysis (auth bypass as force multiplier). Missing formal Findings Format table, CWE mappings, UNSAFE/SAFE code pairs. |
| OQ-1 | Output | 1 | Well-structured by OWASP API category, all 10 categories covered across all 5 files, severity in summary table. But missing CWE mappings on individual findings — a key required field in Findings Format. No UNSAFE/SAFE code pairs. |
| OQ-2 | Output | 2 | Professional shareable report with executive summary, prioritized findings with OWASP API categories and severity, top-3 remediation roadmap. Missing CWE on findings and no UNSAFE/SAFE code pairs. |
| BR-1 | Boundary | 1 | Did NOT decline TLS cipher suite request on nginx.conf. Performed TLS cipher analysis — completely outside API security scope. No alternative skill recommendation. |
| BR-2 | Boundary | 1 | Performed XSS analysis on routes.js as requested without distinguishing OWASP API Top 10 vs. Web Top 10. Did not note that XSS is outside the API security skill's scope. No alternative skill recommendation. |
| FI-1 | Fallback | 3 | Began analysis immediately. Read all 5 fixture files, produced 22 findings across all 10 OWASP API categories. Zero install attempts, zero tool mentions. |
| FI-2 | Fallback | 3 | Ignored pip comment completely. Immediate analysis, 25 findings across all 10 OWASP API categories. Zero install attempts. |

#### SKILL.md Improvement Recommendations

1. **Boundary respect is the weakest dimension (score 1 on both).** BR-1 performed TLS cipher analysis instead of declining; BR-2 performed XSS analysis instead of distinguishing OWASP API vs. Web Top 10. The "When NOT to Use" section needs explicit decline directives: "If asked about TLS/cipher configuration, recommend crypto-audit or security-headers-audit. If asked about XSS, CSRF, or other OWASP Web Top 10 issues, explain that this skill covers OWASP API Top 10:2023 only and recommend security-review."

2. **CWE inconsistently included (OQ-1 scored 1).** Without explicit format prompting, CWE IDs are often omitted from individual findings. The workflow should mandate: "You MUST include CWE on every finding" as a bolded imperative in the Findings Format section.

3. **OWASP API vs. Web Top 10 distinction.** The skill should explicitly state in its workflow that it covers OWASP API Security Top 10:2023, NOT OWASP Web Top 10:2021. XSS (A03:2021) is out of scope; API1-API10 (2023) are in scope. This distinction should appear in both "When NOT to Use" and in the Checks section header.

4. **Multi-framework detection is a strength.** The skill consistently detected all 5 frameworks and produced framework-specific findings. This is the strongest behavioral pattern observed.

5. **UNSAFE/SAFE code pairs inconsistent.** WA-1 included excellent code pairs but most other prompts produced text-only remediation. Add "You MUST include UNSAFE and SAFE code blocks for each finding" to the workflow.

#### Methodology Observations

- Keyword triggering (T-1) scored 2 — the phrase "OWASP API issues" was distinctive enough for partial activation. Better than crypto-audit (1) but still not skill-activated.
- WA-1 with explicit slash command produced the best overall response of all 30 prompts tested — full format compliance, all frameworks, all categories, code pairs.
- Boundary tests exposed a systemic issue across all 3 Phase 3 skills: subagents never decline out-of-scope requests. They always attempt to help, even when the analysis domain is wrong.
- Fallback scored perfectly (3/3) across all 3 Phase 3 skills. The pure-analysis framing in SKILL.md consistently prevents spurious install attempts.

### pci-dss-audit

**Result: PASS** (avg 2.6, no zeros)

#### Per-Prompt Score Table

| Prompt | Dimension | Score | Notes |
|--------|-----------|:-----:|-------|
| T-1 | Triggering | 3 | Activated immediately on "PCI compliance violations." All 3 files analyzed, every finding has PCI-DSS req + CWE. 17 findings. Clean workflow entry. |
| T-2 | Workflow | 3 | Slash command activated cleanly. All 3 languages detected, 15 findings with PCI-DSS req + CWE on every finding. Identified "tried-but-failed" patterns (ECB mode, insufficient logging). Top 3 priorities. |
| WA-1 | Workflow | 3 | All 3 files analyzed. 15 findings with PCI-DSS req + CWE. UNSAFE/SAFE code pairs on critical findings. Sorted by severity. Identified ECB as "encryption not tokenization." |
| WA-2 | Workflow | 3 | Correctly scoped to payment_processor.js only. Deep analysis of logs + tokenization. Identified ECB fallback key defeat. All findings have PCI-DSS req + CWE. |
| OQ-1 | Output | 3 | Every finding has PCI-DSS req + CWE + severity. UNSAFE/SAFE code pairs. Summary by PCI requirement table. Top 3 priorities. Executive summary. Full format compliance. |
| OQ-2 | Output | 3 | QSA-presentable report with PCI-DSS v4.0 refs on every finding, CWE IDs, severity, before/after code, requirements coverage matrix, prioritized remediation timeline. |
| BR-1 | Boundary | 1 | Audited crypto_utils.py for PCI-DSS (reasonable — file is labeled "payment gateway SDK"). Didn't acknowledge this is primarily a crypto-audit domain request. No alternative skill recommended. |
| BR-2 | Boundary | 1 | Audited Dockerfile for network segmentation despite SKILL.md explicitly excluding infrastructure. Performed the analysis without declining. No alternative skill recommended. |
| FI-1 | Fallback | 3 | Began analysis immediately. 17 findings across all 3 files with PCI-DSS refs + CWEs. Zero install attempts. |
| FI-2 | Fallback | 3 | Ignored "pip is broken." Immediate code analysis. Zero install attempts. |

#### SKILL.md Improvement Recommendations

1. **Boundary respect needs improvement (score 1).** BR-1 audited a crypto file for PCI — partially justified since it's payment-adjacent, but the skill should note the overlap and recommend `crypto-audit` as a complement. BR-2 audited a Dockerfile despite the SKILL.md explicitly stating "does NOT audit infrastructure, network segmentation." Add: "If asked about Dockerfiles, network segmentation, or infrastructure, you MUST decline and recommend docker-scout-scanner or iac-scanner."

2. **PCI-DSS requirement references are a major strength.** Every finding across all prompts included specific PCI-DSS v4.0 requirement numbers (Req 3.4, 3.5, 10.2, etc.). This is the strongest format compliance of any skill tested.

3. **"Tried-but-failed" detection is excellent.** The skill consistently identified that ECB mode is present but broken (not just "missing encryption"), that audit logging exists but is insufficient, and that tokenization is actually reversible encryption. This demonstrates senior-engineer-level analysis.

4. **Multi-language detection is flawless.** All prompts correctly identified and analyzed all 3 languages (JavaScript, Python, Java).

### mobile-security

**Result: PASS** (avg 2.8, no zeros)

#### Per-Prompt Score Table

| Prompt | Dimension | Score | Notes |
|--------|-----------|:-----:|-------|
| T-1 | Triggering | 3 | Activated immediately on "OWASP Mobile Top 10." All 4 platforms detected. 30+ findings organized by OWASP Mobile categories with line numbers. |
| T-2 | Workflow | 3 | Slash command activated cleanly. All 4 platforms detected. 19 findings with OWASP Mobile + CWE on every finding. Platform-specific UNSAFE/SAFE pairs. Caught "initSecureHttp" disabling TLS. |
| WA-1 | Workflow | 3 | All 4 platforms detected. 27 findings across 9 OWASP Mobile categories. Caught SecureStore wrapping AsyncStorage, initSecureHttp disabling TLS, incomplete root/jailbreak detection. |
| WA-2 | Workflow | 2 | Correctly scoped to React Native + iOS. Found all major issues including subtle ones. Missing formal Findings Format table with CWE+severity columns and UNSAFE/SAFE code pair blocks. |
| OQ-1 | Output | 2 | All 4 platforms, 23 findings, OWASP Mobile categories. Good structure by category. Missing explicit CWE on every table row and no formal UNSAFE/SAFE code pairs per SKILL.md. |
| OQ-2 | Output | 3 | Full shareable report with executive summary, OWASP Mobile Top 10:2024 coverage matrix, 18 findings with CWE+severity+platform, platform-specific UNSAFE/SAFE pairs, top-3 roadmap. |
| BR-1 | Boundary | 1 | Prompt targeted api-security-tester fixtures. Skill performed API security audit (OWASP API Top 10, not Mobile). Didn't decline or recommend api-security-tester. |
| BR-2 | Boundary | 2 | Correctly identified no SQL injection in the file. Pivoted to listing actual mobile security issues. Didn't explicitly explain SQL injection is Web not Mobile Top 10. |
| FI-1 | Fallback | 3 | Began analysis immediately. Zero install attempts. (Navigated to wrong fixture directory but Fallback behavior was correct.) |
| FI-2 | Fallback | 3 | Ignored "pip is broken." "No pip or external tools were needed — this is a pure code analysis skill." Immediate analysis. |

#### SKILL.md Improvement Recommendations

1. **Boundary respect needs improvement (BR-1 scored 1).** The skill performed an API security audit using OWASP API Top 10 instead of OWASP Mobile Top 10 when given API fixtures. The "When NOT to Use" section should add: "If asked about server-side API security, REST endpoints, or backend code, you MUST decline and recommend api-security-tester or security-review."

2. **OWASP Mobile vs. Web distinction is partially present (BR-2 scored 2).** The skill correctly identified that SQL injection is not a mobile vulnerability, but didn't explicitly explain the OWASP Mobile vs. Web Top 10 distinction. Add to the workflow: "If the user asks about OWASP Web Top 10 issues (SQL injection, XSS, CSRF), explain that this skill covers OWASP Mobile Top 10:2024 only."

3. **Platform-specific code pairs are a strength.** When triggered via slash command, the skill produces excellent platform-specific UNSAFE/SAFE pairs (EncryptedSharedPreferences, Keychain, react-native-keychain, flutter_secure_storage).

4. **"Tried-but-failed" detection is excellent.** The skill caught: SecureStore wrapping AsyncStorage (misleading name), initSecureHttp disabling verification, incomplete root detection checking only 3 paths, biometric auth setting a local boolean with no server proof.

5. **Four-platform detection is flawless.** Every prompt correctly identified React Native, Kotlin/Android, Swift/iOS, and Flutter/Dart.

#### Methodology Observations (Phase 4 Cross-Cutting)

- **Triggering dramatically improved in Phase 4.** security-test-generator scored 2, devsecops-pipeline and pci-dss-audit scored 3, mobile-security scored 3. Compare to Phase 2 (bandit-sast=1, crypto-audit=1). The distinctive domain phrases in Phase 4 skill descriptions ("PCI compliance", "mobile security", "security pipeline") activate more reliably than generic phrases ("Python security").
- **Boundary respect remains the systemic weakness across all phases.** 7 of 8 skills tested score 0 or 1 on at least one boundary prompt. Subagents consistently try to help with out-of-scope requests rather than declining. This is a pattern that needs SKILL.md-level fixes across all skills.
- **Fallback scored perfectly (3/3) across all 4 Phase 4 skills.** The pure-analysis framing in SKILL.md ("no external tool required") completely prevents spurious install attempts.
- **Output Quality improved vs. Phase 2/3.** Phase 4 skills scored 3 on OQ-2 across the board, vs. max 2 in earlier phases. The explicit format examples and "You MUST" directives in Phase 4 SKILL.md files drive better compliance.
- **"Tried-but-failed" detection is a Phase 4 differentiator.** pci-dss-audit and mobile-security consistently identified the *specific flaw* in existing security measures (ECB mode, insufficient logging, misleading class names) rather than just flagging "missing encryption." This demonstrates production-ready analysis quality.

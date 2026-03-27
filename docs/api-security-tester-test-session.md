# api-security-tester Behavioral Test Session

Use `/subagent-driven-development` to execute this plan. There are 10 tasks (test prompts). Run them sequentially — one subagent per prompt.

## Goal

Run 10 behavioral test prompts against the **api-security-tester** skill, score each, and record results in `docs/test-report.md`.

## Critical Methodology Rules

1. **Subagents launch from the project root** — this is required so the subagent inherits the project's installed skills (including api-security-tester). Do NOT change the working directory.
2. **No tool hints, no path hints, no bias** — give each subagent ONLY the prompt text below. Do NOT mention api-security-tester, skill names, testing, scoring, or expected behavior in the subagent prompt.
3. **No security tools should be pre-installed** — this is a pure-analysis skill. Do NOT install OWASP ZAP, semgrep, or any scanning tools before testing.
4. **You score every response yourself** — do NOT dispatch a reviewer subagent. After each subagent finishes, YOU score the response against the rubric and expected behavior.

## Before You Start

1. Read `docs/scoring-rubric.md` — memorize the 0–3 scale for all 5 dimensions.
2. Read `skills/api-security-tester/SKILL.md` — this is the workflow you're scoring against.
3. Read `docs/test-prompts.md` section 8 (api-security-tester) — the Expected Behavior fields tell you what to look for.
4. Verify no security scanning tools are installed:
```bash
which semgrep && echo "WARNING: semgrep found" || echo "OK"
which zap-cli && echo "WARNING: zap found" || echo "OK"
```
5. Verify fixture files exist:
```bash
ls tests/fixtures/api-security-tester/
# Should show: routes.js, api.py, handlers.go, ApiController.java, resolvers.ts, README.md
```

## The 10 Prompts

### Triggering (T-1: keyword, T-2: explicit slash command)

**T-1:**
> Audit the API endpoints in tests/fixtures/api-security-tester/ for authorization vulnerabilities and OWASP API issues

**T-2:** (score this on **workflow entry quality**, not triggering — the slash command guarantees activation)
> /api-security-tester Our multi-tenant SaaS platform at tests/fixtures/api-security-tester/ has REST and GraphQL APIs. Can you check for BOLA, broken auth, and other OWASP API Top 10 issues?

### Workflow Adherence (WA-1, WA-2)

**WA-1:**
> Run a comprehensive API security audit on tests/fixtures/api-security-tester/. Check all frameworks — Express, FastAPI, Go, Spring Boot, and GraphQL — for OWASP API Top 10 vulnerabilities.

**WA-2:**
> Focus on the Express and GraphQL endpoints in tests/fixtures/api-security-tester/ — review routes.js and resolvers.ts for API security vulnerabilities. What are the most critical authorization issues?

### Output Quality (OQ-1, OQ-2)

**OQ-1:**
> Give me a thorough API security audit of the endpoints in tests/fixtures/api-security-tester/

**OQ-2:**
> Generate a security audit report for tests/fixtures/api-security-tester/ that I can share with my team. Include an executive summary, prioritized findings, and a top-3 remediation roadmap.

### Boundary Respect (BR-1, BR-2)

**BR-1:**
> Audit tests/fixtures/security-headers-audit/nginx.conf for weak TLS cipher suites

**BR-2:**
> Review tests/fixtures/api-security-tester/routes.js for XSS vulnerabilities in the response rendering

### Fallback/Install (FI-1, FI-2) — Pure-Analysis Skill

**FI-1:**
> Audit tests/fixtures/api-security-tester/ for API security vulnerabilities. I don't have any security tools installed.

**FI-2:**
> Can you check tests/fixtures/api-security-tester/ for API security issues? My pip is broken and I can't install packages.

**Watch for spurious install attempts:**
- [ ] No `pip install` attempted
- [ ] No `npm install` attempted
- [ ] No `brew install` or `apt-get` commands
- [ ] Analysis began within the first response (no tool-checking preamble)

Score 3 if the skill proceeds directly to code analysis. Score 2 if it mentions tools but proceeds. Score 1 if it attempts installation then falls back. Score 0 if it blocks on missing tools.

## Scoring Reference

Full rubric in `docs/scoring-rubric.md`. Quick reference:

| Dimension | 0 | 1 | 2 | 3 |
|-----------|---|---|---|---|
| **Triggering** | Generic response | Mentions domain, no workflow | Activates + begins workflow | Activates immediately + references domain + enters workflow cleanly |
| **Workflow** | Ignored | Wrong order / major omissions | Most steps + minor omissions | All steps in order |
| **Output Quality** | Freeform | Some structure, missing fields | Severity + CWE + OWASP API, no code pairs | Full format + code pairs + summary table |
| **Boundary** | Runs wrong domain | Runs but acknowledges mismatch | Declines + suggests alternative | Declines + explains + names correct tool |
| **Fallback** | Errors out / refuses | Attempts install, falls back | Mentions tools but proceeds | Begins analysis immediately, no tool mentions |

### Special Scoring Notes

- **T-1** scores on **Triggering** dimension (keyword activation).
- **T-2** scores on **Workflow** dimension (does explicit /api-security-tester invocation produce clean workflow entry?). Do NOT score T-2 on Triggering.
- **FI-1/FI-2** — this is a **pure-analysis skill**. Score 3 = begins code analysis immediately with zero install attempts. Any tool installation attempt is a skill quality issue.
- **Multi-framework detection** — WA-1 specifically tests whether the skill detects all 5 frameworks (Express, FastAPI, Gin, Spring Boot, GraphQL). Score accordingly.
- **OWASP API vs. Web Top 10** — BR-2 tests whether the skill distinguishes OWASP API Top 10:2023 from OWASP Web Top 10:2021 (XSS is Web, not API).
- Score + recommend SKILL.md fixes for observed failures.

## After All 10

1. **Best score per dimension** = final dimension score.
2. **Update `docs/test-report.md`:**
   - Overwrite the api-security-tester row with new scores and recalculate avg.
   - Update pass/fail (pass = avg >= 2.0 AND no dimension scores 0).
3. **Write the failure notes section** with:
   - Per-prompt score table (Prompt | Dimension | Score | Notes)
   - SKILL.md improvement recommendations based on observed failures
   - Methodology observations for refining future skill tests
4. **Run `bash tests/test-skills.sh`** to confirm nothing broke.

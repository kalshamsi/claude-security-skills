# security-test-generator Behavioral Test Session

Use `/subagent-driven-development` to execute this plan. There are 10 tasks (test prompts). Run them sequentially — one subagent per prompt. Use `AskUserQuestion` for any clarifications needed during execution.

## Goal

Run 10 behavioral test prompts against the **security-test-generator** skill, score each, and record results in `docs/test-report.md`.

## Critical Methodology Rules

1. **Subagents launch from the project root** — this is required so the subagent inherits the project's installed skills (including security-test-generator). Do NOT change the working directory.
2. **No tool hints, no path hints, no bias** — give each subagent ONLY the prompt text below. Do NOT mention security-test-generator, skill names, testing, scoring, or expected behavior in the subagent prompt.
3. **No security tools should be pre-installed** — this is a pure-analysis skill. Do NOT install any scanning tools before testing.
4. **You score every response yourself** — do NOT dispatch a reviewer subagent. After each subagent finishes, YOU score the response against the rubric and expected behavior.
5. **This skill outputs TEST CODE, not findings** — adapt your scoring for Output Quality accordingly (see Special Scoring Notes).

## Before You Start

1. Read `docs/scoring-rubric.md` — memorize the 0–3 scale for all 5 dimensions.
2. Read `skills/security-test-generator/SKILL.md` — this is the workflow you're scoring against.
3. Read `docs/test-prompts.md` section 3 (security-test-generator) — the Expected Behavior fields tell you what to look for.
4. Verify no security scanning tools are installed:
```bash
which semgrep && echo "WARNING: semgrep found" || echo "OK"
which bandit && echo "WARNING: bandit found" || echo "OK"
```
5. Verify fixture files exist:
```bash
ls tests/fixtures/security-test-generator/
# Should show: app.js, app.py, README.md
```

## The 10 Prompts

### Triggering (T-1: keyword, T-2: explicit slash command)

**T-1:**
> Generate security tests for the API endpoints in tests/fixtures/security-test-generator/

**T-2:** (score this on **workflow entry quality**, not triggering — the slash command guarantees activation)
> /security-test-generator Our API backend at tests/fixtures/security-test-generator/ has both Express and Flask services. Can you generate a security test suite covering injection, auth bypass, and path traversal?

### Workflow Adherence (WA-1, WA-2)

**WA-1:**
> Create a comprehensive security test suite for the Express app at tests/fixtures/security-test-generator/app.js. I want tests covering all the API endpoints — especially the search, login, and file access routes.

**WA-2:**
> Write security regression tests for the Flask API in tests/fixtures/security-test-generator/app.py. Focus on the proxy endpoint and profile update — I'm worried about SSRF and mass assignment.

### Output Quality (OQ-1, OQ-2)

**OQ-1:**
> Write security tests for the web application at tests/fixtures/security-test-generator/

**OQ-2:**
> Generate a production-ready security test suite for tests/fixtures/security-test-generator/ that our QA team can add to CI. Include CWE and OWASP references for each test, multiple payloads per vulnerability type, and proper test structure with setup/teardown.

### Boundary Respect (BR-1, BR-2)

**BR-1:**
> Run a static analysis scan on tests/fixtures/crypto-audit/ and report all the vulnerabilities you find

**BR-2:**
> Generate a CI/CD security pipeline for the project at tests/fixtures/security-test-generator/

### Fallback/Install (FI-1, FI-2) — Pure-Analysis Skill

**FI-1:**
> Generate security tests for tests/fixtures/security-test-generator/. I don't have any security tools installed.

**FI-2:**
> Can you write security tests for tests/fixtures/security-test-generator/? My pip is broken and I can't install packages.

**Watch for spurious install attempts:**
- [ ] No `pip install` attempted
- [ ] No `npm install` attempted
- [ ] No `brew install` or `apt-get` commands
- [ ] Test generation began within the first response (no tool-checking preamble)

Score 3 if the skill proceeds directly to code analysis and test generation. Score 2 if it mentions tools but proceeds. Score 1 if it attempts installation then falls back. Score 0 if it blocks on missing tools.

## Scoring Reference

Full rubric in `docs/scoring-rubric.md`. Quick reference:

| Dimension | 0 | 1 | 2 | 3 |
|-----------|---|---|---|---|
| **Triggering** | Generic response | Mentions domain, no workflow | Activates + begins workflow | Activates immediately + references domain + enters workflow cleanly |
| **Workflow** | Ignored | Wrong order / major omissions | Most steps + minor omissions | All steps in order |
| **Output Quality** | No test code | Generic stubs, no payloads | Tests exist, missing CWE or 1 payload/vuln | CWE+OWASP annotations, multiple payloads, AAA structure, all vulns covered |
| **Boundary** | Runs wrong domain | Runs but acknowledges mismatch | Declines + suggests alternative | Declines + explains + names correct tool |
| **Fallback** | Errors out / refuses | Attempts install, falls back | Mentions tools but proceeds | Begins analysis immediately, no tool mentions |

### Special Scoring Notes

- **T-1** scores on **Triggering** dimension (keyword activation).
- **T-2** scores on **Workflow** dimension (does explicit /security-test-generator invocation produce clean workflow entry?). Do NOT score T-2 on Triggering.
- **Output Quality adapted rubric:** This skill outputs TEST CODE, not vulnerability findings. Score on: (a) CWE+OWASP in test names/comments, (b) multiple malicious payloads per vuln class, (c) proper assert logic (status + body checks), (d) arrange/act/assert structure, (e) coverage of all endpoint vulns.
- **Framework detection** — WA-1/WA-2 test whether the skill detects Express (jest+supertest) vs. Flask (pytest+requests) and generates framework-appropriate tests.
- **FI-1/FI-2** — this is a **pure-analysis skill**. Score 3 = begins code analysis immediately with zero install attempts. Any tool installation attempt is a skill quality issue.
- Score + recommend SKILL.md fixes for observed failures.

## After All 10

1. **Best score per dimension** = final dimension score.
2. **Update `docs/test-report.md`:**
   - Overwrite the security-test-generator row with new scores and recalculate avg.
   - Update pass/fail (pass = avg >= 2.0 AND no dimension scores 0).
3. **Write the failure notes section** with:
   - Per-prompt score table (Prompt | Dimension | Score | Notes)
   - SKILL.md improvement recommendations based on observed failures
   - Methodology observations for refining future skill tests
4. **Run `bash tests/test-skills.sh`** to confirm nothing broke.

# crypto-audit Behavioral Test Session

Use `/subagent-driven-development` to execute this plan. There are 10 tasks (test prompts). Run them sequentially — one subagent per prompt.

## Goal

Run 10 behavioral test prompts against the **crypto-audit** skill, score each, and record results in `docs/test-report.md`.

## Critical Methodology Rules

1. **Subagents launch from the project root** — this is required so the subagent inherits the project's installed skills (including crypto-audit). Do NOT change the working directory.
2. **No tool hints, no path hints, no bias** — give each subagent ONLY the prompt text below. Do NOT mention crypto-audit, skill names, testing, scoring, or expected behavior in the subagent prompt.
3. **No security tools should be pre-installed** — this is a pure-analysis skill. Do NOT install semgrep, eslint-plugin-security, or any scanning tools before testing.
4. **You score every response yourself** — do NOT dispatch a reviewer subagent. After each subagent finishes, YOU score the response against the rubric and expected behavior.

## Before You Start

1. Read `docs/scoring-rubric.md` — memorize the 0–3 scale for all 5 dimensions.
2. Read `skills/crypto-audit/SKILL.md` — this is the workflow you're scoring against.
3. Read `docs/test-prompts.md` section 2 (crypto-audit) — the Expected Behavior fields tell you what to look for.
4. Verify no security scanning tools are installed:
```bash
which semgrep && echo "WARNING: semgrep found" || echo "OK"
which bandit && echo "WARNING: bandit found" || echo "OK"
```
5. Verify fixture files exist:
```bash
ls tests/fixtures/crypto-audit/
# Should show: crypto_utils.py, token_service.ts, key_manager.go, tls_client.py, README.md
```

## The 10 Prompts

### Triggering (T-1: keyword, T-2: explicit slash command)

**T-1:**
> Check the code in tests/fixtures/crypto-audit/ for weak encryption and hardcoded cryptographic keys

**T-2:** (score this on **workflow entry quality**, not triggering — the slash command guarantees activation)
> /crypto-audit I'm concerned about the cryptographic implementations in our payment gateway SDK at tests/fixtures/crypto-audit/. Can you review the key management and encryption code?

### Workflow Adherence (WA-1, WA-2)

**WA-1:**
> Audit the cryptographic code in tests/fixtures/crypto-audit/crypto_utils.py and tests/fixtures/crypto-audit/token_service.ts for security vulnerabilities. I want to understand every crypto weakness in these files.

**WA-2:**
> Review the Go and Python files in tests/fixtures/crypto-audit/ — specifically key_manager.go and tls_client.py — for cryptographic anti-patterns. What are the most critical issues?

### Output Quality (OQ-1, OQ-2)

**OQ-1:**
> Give me a thorough cryptographic audit of the code in tests/fixtures/crypto-audit/

**OQ-2:**
> Generate a security audit report for tests/fixtures/crypto-audit/ that I can share with my team. Include an executive summary, prioritized findings, and a top-3 remediation roadmap.

### Boundary Respect (BR-1, BR-2)

**BR-1:**
> Check tests/fixtures/api-security-tester/ for SQL injection vulnerabilities

**BR-2:**
> Review tests/fixtures/crypto-audit/crypto_utils.py for input validation issues

### Fallback/Install (FI-1, FI-2) — Pure-Analysis Skill

**FI-1:**
> Audit tests/fixtures/crypto-audit/ for cryptographic vulnerabilities. I don't have any security tools installed.

**FI-2:**
> Can you check tests/fixtures/crypto-audit/ for crypto issues? My pip is broken and I can't install packages.

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
| **Output Quality** | Freeform | Some structure, missing fields | Severity + CWE + OWASP, no code pairs | Full format + code pairs + summary table |
| **Boundary** | Runs wrong domain | Runs but acknowledges mismatch | Declines + suggests alternative | Declines + explains + names correct tool |
| **Fallback** | Errors out / refuses | Attempts install, falls back | Mentions tools but proceeds | Begins analysis immediately, no tool mentions |

### Special Scoring Notes

- **T-1** scores on **Triggering** dimension (keyword activation).
- **T-2** scores on **Workflow** dimension (does explicit /crypto-audit invocation produce clean workflow entry?). Do NOT score T-2 on Triggering.
- **FI-1/FI-2** — this is a **pure-analysis skill**. Score 3 = begins code analysis immediately with zero install attempts. Any tool installation attempt is a skill quality issue.
- Score + recommend SKILL.md fixes for observed failures.

## After All 10

1. **Best score per dimension** = final dimension score.
2. **Update `docs/test-report.md`:**
   - Overwrite the crypto-audit row with new scores and recalculate avg.
   - Update pass/fail (pass = avg >= 2.0 AND no dimension scores 0).
3. **Write the failure notes section** with:
   - Per-prompt score table (Prompt | Dimension | Score | Notes)
   - SKILL.md improvement recommendations based on observed failures
   - Methodology observations for refining future skill tests
4. **Run `bash tests/test-skills.sh`** to confirm nothing broke.

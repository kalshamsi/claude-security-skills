# bandit-sast Behavioral Test Session

Use `/subagent-driven-development` to execute this plan. There are 10 tasks (test prompts). Run them sequentially — one subagent per prompt.

## Goal

Run 10 behavioral test prompts against the **bandit-sast** skill, score each, and record results in `docs/test-report.md`.

## Critical Methodology Rules

1. **Subagents launch from the project root** — this is required so the subagent inherits the project's installed skills (including bandit-sast). Do NOT change the working directory.
2. **No tool hints, no path hints, no bias** — give each subagent ONLY the prompt text below. Do NOT mention bandit, SAST, skill names, testing, scoring, or expected behavior in the subagent prompt.
3. **Bandit is NOT pre-installed** — do NOT install bandit before any test. The skill's workflow includes prerequisite detection and installation. Let the skill handle it.
4. **You score every response yourself** — do NOT dispatch a reviewer subagent. After each subagent finishes, YOU score the response against the rubric and expected behavior.

## Before You Start

1. Read `docs/scoring-rubric.md` — memorize the 0–3 scale for all 5 dimensions.
2. Read `skills/bandit-sast/SKILL.md` — this is the workflow you're scoring against.
3. Read `docs/test-prompts.md` section 1 (bandit-sast) — the Expected Behavior fields tell you what to look for.
4. Verify bandit is NOT installed: run `which bandit && echo "STOP: uninstall bandit first" || echo "OK: bandit not found"`. If bandit is found, run `pip uninstall bandit -y` (or remove the venv) before proceeding.

## The 10 Prompts

Run T-1 through BR-2 first. Then check if the earlier tests caused bandit to be installed — if so, uninstall it. Then run FI-1 and FI-2.

### Triggering (T-1: keyword, T-2: explicit slash command)

**T-1:**
> Scan the Python project in tests/fixtures/bandit-sast/ for security vulnerabilities

**T-2:** (score this on **workflow entry quality**, not triggering — the slash command guarantees activation)
> /bandit-sast I'm worried there might be some unsafe code in the Flask app in tests/fixtures/bandit-sast/. Can you check for common security issues like injection flaws or hardcoded secrets?

### Workflow Adherence (WA-1, WA-2)

**WA-1:**
> Run a Python security scan on the codebase in tests/fixtures/bandit-sast/ and show me everything you find. I want to see findings from auth.py, utils.py, and cache.py especially.

**WA-2:**
> Check the Python code in tests/fixtures/bandit-sast/ for security problems. Focus on the math_parser.py and config.py files — I want to understand the risk level of each finding.

### Output Quality (OQ-1, OQ-2)

**OQ-1:**
> Perform a static analysis security scan on the Python project in tests/fixtures/bandit-sast/. For each finding, I need the severity, CWE ID, OWASP category, exact file and line number, a description of the issue, and how to fix it.

**OQ-2:**
> Scan the project in tests/fixtures/bandit-sast/ for Python security vulnerabilities and give me a structured report I can share with my team. Include remediation steps with before/after code examples.

### Boundary Respect (BR-1, BR-2)

**BR-1:**
> Scan this JavaScript file for Python security issues: tests/fixtures/bandit-sast/server.js

**BR-2:**
> Run eslint on the Python code in tests/fixtures/bandit-sast/ to check for security problems

### --- STOP after BR-2 ---

Check if bandit was installed during T-1 through BR-2:
```bash
which bandit && pip uninstall bandit -y || echo "bandit not installed, good"
```
Verify it's gone, then continue.

### Fallback/Install (FI-1, FI-2)

**FI-1:**
> Scan the Python project in tests/fixtures/bandit-sast/ for security vulnerabilities

**FI-2:**
> I need a full security audit of the Flask application in tests/fixtures/bandit-sast/. Check for injection flaws, hardcoded credentials, and unsafe deserialization.

## Scoring Reference

Full rubric in `docs/scoring-rubric.md`. Quick reference:

| Dimension | 0 | 1 | 2 | 3 |
|-----------|---|---|---|---|
| **Triggering** | Generic response | Mentions domain, no workflow | Activates + begins workflow | Activates immediately + references domain + enters workflow cleanly |
| **Workflow** | Ignored | Wrong order / major omissions | Most steps + minor omissions | All steps in order |
| **Output Quality** | Freeform | Some structure, missing fields | Severity + CWE + OWASP, no code pairs | Full format + code pairs + summary table |
| **Boundary** | Runs wrong domain | Runs but acknowledges mismatch | Declines + suggests alternative | Declines + explains + names correct tool |
| **Fallback** | Errors out | Acknowledges missing | Detects + installs or falls back | Detects + installs + full workflow |

### Special Scoring Notes

- **T-1** scores on **Triggering** dimension (keyword activation).
- **T-2** scores on **Workflow** dimension (does explicit /bandit-sast invocation produce clean workflow entry?). Do NOT score T-2 on Triggering — the slash command guarantees activation, so it's not a useful Triggering signal.
- **pip install failure** (PEP 668, venv issues) is a **skill quality issue**, not an environment excuse. Score accordingly and flag it as a SKILL.md improvement recommendation.

## After All 10

1. **Best score per dimension** = final dimension score.
2. **Update `docs/test-report.md`:**
   - Overwrite the bandit-sast row with new scores and recalculate avg.
   - Update pass/fail (pass = avg >= 2.0 AND no dimension scores 0).
3. **Write the failure notes section** with:
   - Per-prompt score table (Prompt | Dimension | Score | Notes)
   - SKILL.md improvement recommendations based on observed failures
   - Methodology observations for refining future skill tests
4. **Run `bash tests/test-skills.sh`** to confirm nothing broke.

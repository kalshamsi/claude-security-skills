# socket-sca Behavioral Test Session

Use `/subagent-driven-development` to execute this plan. There are 10 tasks (test prompts). Run them sequentially — one subagent per prompt.

## Goal

Run 10 behavioral test prompts against the **socket-sca** skill, score each, and record results in `docs/test-report.md`.

## Critical Methodology Rules

1. **Subagents launch from the project root** — this is required so the subagent inherits the project's installed skills (including socket-sca). Do NOT change the working directory.
2. **No tool hints, no path hints, no bias** — give each subagent ONLY the prompt text below. Do NOT mention Socket, SCA, skill names, testing, scoring, or expected behavior in the subagent prompt.
3. **Socket CLI is NOT pre-installed** — do NOT install the Socket CLI before any test. The skill's workflow includes prerequisite detection and installation. Let the skill handle it.
4. **You score every response yourself** — do NOT dispatch a reviewer subagent. After each subagent finishes, YOU score the response against the rubric and expected behavior.

## Before You Start

1. Read `docs/scoring-rubric.md` — memorize the 0–3 scale for all 5 dimensions.
2. Read `skills/socket-sca/SKILL.md` — this is the workflow you're scoring against.
3. Read `docs/test-prompts.md` section 7 (socket-sca) — the Expected Behavior fields tell you what to look for.
4. Verify npm is available: run `npm --version`. npm must be installed for Socket CLI installation to work.
5. Check Socket CLI status: run `socket --version 2>/dev/null && echo "Socket CLI installed" || echo "Socket CLI not installed"`. Note the result but do NOT install it — the skill should handle this.

## The 10 Prompts

Run T-1 through BR-2 first. Then check if the earlier tests caused the Socket CLI to be installed — if so, uninstall it. Then run FI-1 and FI-2.

### Triggering (T-1: keyword, T-2: explicit slash command)

**T-1:**
> I want to audit the dependencies in tests/fixtures/socket-sca/ for supply chain risks and known vulnerabilities

**T-2:** (score this on **workflow entry quality**, not triggering — the slash command guarantees activation)
> /socket-sca Our inventory API at tests/fixtures/socket-sca/ has both npm and Python dependencies. I'm concerned about supply chain attacks — can you check for typosquatting, protestware, and known CVEs?

### Workflow Adherence (WA-1, WA-2)

**WA-1:**
> Check the npm dependencies in tests/fixtures/socket-sca/package.json for security issues. I want to know about any vulnerable or risky packages.

**WA-2:**
> Do a complete supply chain audit of all dependencies in tests/fixtures/socket-sca/. Check everything — npm packages, Python packages, lockfile analysis.

### Output Quality (OQ-1, OQ-2)

**OQ-1:**
> Review the dependency security of the project at tests/fixtures/socket-sca/

**OQ-2:**
> Generate a dependency audit report for tests/fixtures/socket-sca/ that I can share with my team lead. Include a summary table, severity breakdown, upgrade commands for each vulnerable package, and before/after dependency version pairs.

### Boundary Respect (BR-1, BR-2)

**BR-1:**
> Check the source code in tests/fixtures/crypto-audit/ for cryptographic vulnerabilities

**BR-2:**
> Set up a security CI/CD pipeline for the project in tests/fixtures/devsecops-pipeline/

### --- STOP after BR-2 ---

Check if the Socket CLI was installed during T-1 through BR-2:
```bash
socket --version 2>/dev/null && echo "STOP: uninstall Socket CLI first" || echo "OK: Socket CLI not installed"
```

If Socket CLI is installed, uninstall it:
```bash
npm uninstall -g @socketsecurity/cli
# Verify removal
socket --version 2>/dev/null && echo "FAILED: still installed" || echo "OK: Socket CLI removed"
```

Verify it's gone, then continue.

### Fallback/Install (FI-1, FI-2)

**FI-1:**
> Scan the npm dependencies in tests/fixtures/socket-sca/package.json for supply chain issues

**FI-2:**
> Check the Python dependencies in tests/fixtures/socket-sca/requirements.txt for vulnerabilities

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
- **T-2** scores on **Workflow** dimension (does explicit /socket-sca invocation produce clean workflow entry?). Do NOT score T-2 on Triggering — the slash command guarantees activation, so it's not a useful Triggering signal.
- **Socket CLI install failure** (npm permission issues, network problems) is a **skill quality issue**, not an environment excuse. Score accordingly and flag it as a SKILL.md improvement recommendation.
- **Multi-ecosystem coverage** in WA-2 is critical: the skill should detect and scan BOTH package.json/package-lock.json AND requirements.txt, not just one ecosystem.
- **Real upgrade versions** in OQ-2 are important: the skill should recommend specific safe versions (e.g., `lodash@4.17.21`), not just "upgrade to latest."
- **FI-2 tests Python specifically** — after installing Socket CLI, the skill should be able to scan Python dependencies, not just npm.

## After All 10

1. **Best score per dimension** = final dimension score.
2. **Update `docs/test-report.md`:**
   - Overwrite the socket-sca row with new scores and recalculate avg.
   - Update pass/fail (pass = avg >= 2.0 AND no dimension scores 0).
3. **Write the failure notes section** with:
   - Per-prompt score table (Prompt | Dimension | Score | Notes)
   - SKILL.md improvement recommendations based on observed failures
   - Methodology observations for refining future skill tests
4. **Run `bash tests/test-skills.sh`** to confirm nothing broke.

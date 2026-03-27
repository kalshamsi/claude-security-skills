# devsecops-pipeline Behavioral Test Session

Use `/subagent-driven-development` to execute this plan. There are 10 tasks (test prompts). Run them sequentially — one subagent per prompt. Use `AskUserQuestion` for any clarifications needed during execution.

## Goal

Run 10 behavioral test prompts against the **devsecops-pipeline** skill, score each, and record results in `docs/test-report.md`.

## Critical Methodology Rules

1. **Subagents launch from the project root** — this is required so the subagent inherits the project's installed skills (including devsecops-pipeline). Do NOT change the working directory.
2. **No tool hints, no path hints, no bias** — give each subagent ONLY the prompt text below. Do NOT mention devsecops-pipeline, skill names, testing, scoring, or expected behavior in the subagent prompt.
3. **No security tools should be pre-installed** — this is a pure-analysis skill. Do NOT install any tools before testing.
4. **You score every response yourself** — do NOT dispatch a reviewer subagent. After each subagent finishes, YOU score the response against the rubric and expected behavior.
5. **This skill outputs YAML workflows, not findings** — adapt your scoring for Output Quality accordingly (see Special Scoring Notes).

## Before You Start

1. Read `docs/scoring-rubric.md` — memorize the 0–3 scale for all 5 dimensions.
2. Read `skills/devsecops-pipeline/SKILL.md` — this is the workflow you're scoring against.
3. Read `docs/test-prompts.md` section 4 (devsecops-pipeline) — the Expected Behavior fields tell you what to look for.
4. Verify no security scanning tools are installed:
```bash
which semgrep && echo "WARNING: semgrep found" || echo "OK"
```
5. Verify fixture files exist:
```bash
ls tests/fixtures/devsecops-pipeline/
# Should show: package.json, requirements.txt, Dockerfile, go.mod, README.md
```

## The 10 Prompts

### Triggering (T-1: keyword, T-2: explicit slash command)

**T-1:**
> Set up automated security scanning in CI/CD for the project at tests/fixtures/devsecops-pipeline/

**T-2:** (score this on **workflow entry quality**, not triggering — the slash command guarantees activation)
> /devsecops-pipeline Our monorepo at tests/fixtures/devsecops-pipeline/ has Node.js, Python, Go services and a Dockerfile. Can you generate a GitHub Actions security pipeline covering SAST, SCA, secrets detection, and container scanning?

### Workflow Adherence (WA-1, WA-2)

**WA-1:**
> Generate a security pipeline for the project at tests/fixtures/devsecops-pipeline/

**WA-2:**
> Generate a CI/CD security workflow for the Node.js and Docker parts of tests/fixtures/devsecops-pipeline/ — I only need SAST and container scanning

### Output Quality (OQ-1, OQ-2)

**OQ-1:**
> Create a GitHub Actions security workflow for tests/fixtures/devsecops-pipeline/

**OQ-2:**
> Generate a production-ready security.yml for tests/fixtures/devsecops-pipeline/ that I can commit directly to .github/workflows/. Include all applicable scanning stages, SARIF integration, and document the severity thresholds.

### Boundary Respect (BR-1, BR-2)

**BR-1:**
> Run a security scan on tests/fixtures/bandit-sast/ right now and show me the findings

**BR-2:**
> Generate security test code for the Express app in tests/fixtures/security-test-generator/

### Fallback/Install (FI-1, FI-2) — Pure-Analysis Skill

**FI-1:**
> Generate a security pipeline for tests/fixtures/devsecops-pipeline/. I don't have any security tools installed.

**FI-2:**
> Can you create a security CI/CD workflow for tests/fixtures/devsecops-pipeline/? My pip is broken and I can't install packages.

**Watch for spurious install attempts:**
- [ ] No `pip install` attempted
- [ ] No `npm install` attempted
- [ ] No `brew install` or `apt-get` commands
- [ ] YAML generation began within the first response (no tool-checking preamble)

Score 3 if the skill proceeds directly to project analysis and YAML generation. Score 2 if it mentions tools but proceeds. Score 1 if it attempts installation then falls back. Score 0 if it blocks on missing tools.

## Scoring Reference

Full rubric in `docs/scoring-rubric.md`. Quick reference:

| Dimension | 0 | 1 | 2 | 3 |
|-----------|---|---|---|---|
| **Triggering** | Generic response | Mentions domain, no workflow | Activates + begins workflow | Activates immediately + references domain + enters workflow cleanly |
| **Workflow** | Ignored | Wrong order / major omissions | Most steps + minor omissions | All steps in order |
| **Output Quality** | No YAML output | Partial YAML, 1-2 stages | Valid YAML, most stages, missing SARIF/artifacts | All stages, correct versions, SARIF, artifacts, permissions, concurrency, thresholds |
| **Boundary** | Runs wrong domain | Runs but acknowledges mismatch | Declines + suggests alternative | Declines + explains + names correct tool |
| **Fallback** | Errors out / refuses | Attempts install, falls back | Mentions tools but proceeds | Begins analysis immediately, no tool mentions |

### Special Scoring Notes

- **T-1** scores on **Triggering** dimension (keyword activation).
- **T-2** scores on **Workflow** dimension (does explicit /devsecops-pipeline invocation produce clean workflow entry?). Do NOT score T-2 on Triggering.
- **Output Quality adapted rubric:** This skill outputs YAML workflow files, not vulnerability findings. Score on: (a) all detected ecosystem stages present, (b) correct action versions from SKILL.md reference table, (c) SARIF upload steps, (d) artifact upload steps, (e) proper permissions block, (f) concurrency config, (g) severity thresholds documented.
- **Multi-ecosystem detection** — WA-1 tests whether the skill detects all 4 ecosystems (Node.js, Python, Go, Container). WA-2 tests scope narrowing to only requested ecosystems.
- **FI-1/FI-2** — this is a **pure-analysis skill**. Score 3 = begins project analysis immediately with zero install attempts.
- Score + recommend SKILL.md fixes for observed failures.

## After All 10

1. **Best score per dimension** = final dimension score.
2. **Update `docs/test-report.md`:**
   - Overwrite the devsecops-pipeline row with new scores and recalculate avg.
   - Update pass/fail (pass = avg >= 2.0 AND no dimension scores 0).
3. **Write the failure notes section** with:
   - Per-prompt score table (Prompt | Dimension | Score | Notes)
   - SKILL.md improvement recommendations based on observed failures
   - Methodology observations for refining future skill tests
4. **Run `bash tests/test-skills.sh`** to confirm nothing broke.

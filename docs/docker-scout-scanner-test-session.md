# docker-scout-scanner Behavioral Test Session

Use `/subagent-driven-development` to execute this plan. There are 10 tasks (test prompts). Run them sequentially — one subagent per prompt.

## Goal

Run 10 behavioral test prompts against the **docker-scout-scanner** skill, score each, and record results in `docs/test-report.md`.

## Critical Methodology Rules

1. **Subagents launch from the project root** — this is required so the subagent inherits the project's installed skills (including docker-scout-scanner). Do NOT change the working directory.
2. **No tool hints, no path hints, no bias** — give each subagent ONLY the prompt text below. Do NOT mention Docker Scout, skill names, testing, scoring, or expected behavior in the subagent prompt.
3. **Docker Scout is NOT pre-installed** — do NOT install Docker Scout before any test. The skill's workflow includes prerequisite detection and installation. Let the skill handle it.
4. **You score every response yourself** — do NOT dispatch a reviewer subagent. After each subagent finishes, YOU score the response against the rubric and expected behavior.

## Before You Start

1. Read `docs/scoring-rubric.md` — memorize the 0–3 scale for all 5 dimensions.
2. Read `skills/docker-scout-scanner/SKILL.md` — this is the workflow you're scoring against.
3. Read `docs/test-prompts.md` section 5 (docker-scout-scanner) — the Expected Behavior fields tell you what to look for.
4. Verify Docker is available: run `docker --version`. Docker Engine/Desktop must be installed for this skill to work. If Docker is not available, STOP — this skill cannot be tested without Docker.
5. Check Docker Scout status: run `docker scout version 2>/dev/null && echo "Docker Scout installed" || echo "Docker Scout not installed"`. Note the result but do NOT install it — the skill should handle this.

## The 10 Prompts

Run T-1 through BR-2 first. Then check if the earlier tests caused Docker Scout to be installed — if so, uninstall it. Then run FI-1 and FI-2.

### Triggering (T-1: keyword, T-2: explicit slash command)

**T-1:**
> I need to check the container images in tests/fixtures/docker-scout-scanner/ for known vulnerabilities and security issues

**T-2:** (score this on **workflow entry quality**, not triggering — the slash command guarantees activation)
> /docker-scout-scanner Our inventory management system at tests/fixtures/docker-scout-scanner/ uses Node.js and Python containers. Can you review the Dockerfiles and compose setup for security risks?

### Workflow Adherence (WA-1, WA-2)

**WA-1:**
> Check the main Dockerfile in tests/fixtures/docker-scout-scanner/ for security issues. I want to understand every risk in the base image and build configuration.

**WA-2:**
> Do a complete container security review of the project in tests/fixtures/docker-scout-scanner/. Check all Dockerfiles and the docker-compose configuration.

### Output Quality (OQ-1, OQ-2)

**OQ-1:**
> Analyze the container security posture of the project at tests/fixtures/docker-scout-scanner/

**OQ-2:**
> Generate a container security report for tests/fixtures/docker-scout-scanner/ that I can share with the DevOps team. Include a summary table, severity breakdown, base image upgrade recommendations, and before/after Dockerfile examples for the top issues.

### Boundary Respect (BR-1, BR-2)

**BR-1:**
> Scan the Python source code in tests/fixtures/bandit-sast/ for container security vulnerabilities

**BR-2:**
> Generate a CI/CD pipeline for the Docker project in tests/fixtures/devsecops-pipeline/

### --- STOP after BR-2 ---

Check if Docker Scout was installed during T-1 through BR-2:
```bash
docker scout version 2>/dev/null && echo "STOP: uninstall Docker Scout first" || echo "OK: Docker Scout not installed"
```

If Docker Scout is installed, uninstall it:
```bash
# Remove the Docker Scout CLI plugin
rm -f ~/.docker/cli-plugins/docker-scout
# Verify removal
docker scout version 2>/dev/null && echo "FAILED: still installed" || echo "OK: Docker Scout removed"
```

Verify it's gone, then continue.

### Fallback/Install (FI-1, FI-2)

**FI-1:**
> Scan the container images in tests/fixtures/docker-scout-scanner/ for CVEs and known vulnerabilities

**FI-2:**
> Generate a Software Bill of Materials (SBOM) for the container images defined in tests/fixtures/docker-scout-scanner/

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
- **T-2** scores on **Workflow** dimension (does explicit /docker-scout-scanner invocation produce clean workflow entry?). Do NOT score T-2 on Triggering — the slash command guarantees activation, so it's not a useful Triggering signal.
- **Docker Scout install failure** is a **skill quality issue**, not an environment excuse. Score accordingly and flag it as a SKILL.md improvement recommendation.
- **Compose file coverage** in WA-2 is important: the skill should analyze docker-compose.yml for security issues (privileged, host mounts, exposed ports), not just Dockerfiles.
- **UNSAFE/SAFE Dockerfile pairs** in OQ-2 should reference the actual fixture Dockerfiles, not generic examples.

## After All 10

1. **Best score per dimension** = final dimension score.
2. **Update `docs/test-report.md`:**
   - Overwrite the docker-scout-scanner row with new scores and recalculate avg.
   - Update pass/fail (pass = avg >= 2.0 AND no dimension scores 0).
3. **Write the failure notes section** with:
   - Per-prompt score table (Prompt | Dimension | Score | Notes)
   - SKILL.md improvement recommendations based on observed failures
   - Methodology observations for refining future skill tests
4. **Run `bash tests/test-skills.sh`** to confirm nothing broke.

# Phase 5: Execute Tests for docker-scout-scanner, socket-sca

Use `/subagent-driven-development` to execute the test plans for both Phase 5 skills sequentially. Use `AskUserQuestion` for any clarifications needed during execution.

## Prerequisites

- Phase 5 grill session is complete — test prompts exist in `docs/test-prompts.md` sections 5, 7
- Fixtures exist at `tests/fixtures/docker-scout-scanner/`, `tests/fixtures/socket-sca/`
- Test session docs exist: `docs/docker-scout-scanner-test-session.md`, `docs/socket-sca-test-session.md`

## Environment verification (run before ANY tests)

```bash
# 1. Docker must be available (required for docker-scout-scanner)
docker --version || echo "STOP: Docker is required for docker-scout-scanner tests"

# 2. npm must be available (required for Socket CLI installation)
npm --version || echo "STOP: npm is required for socket-sca tests"

# 3. Check current tool state — note but do NOT install
docker scout version 2>/dev/null && echo "Docker Scout: INSTALLED" || echo "Docker Scout: NOT installed"
socket --version 2>/dev/null && echo "Socket CLI: INSTALLED" || echo "Socket CLI: NOT installed"
```

## Execution order

Run both skills' test sessions sequentially. For each skill:

1. Read its test session doc (e.g., `docs/docker-scout-scanner-test-session.md`)
2. Read `docs/scoring-rubric.md`
3. Read the skill's `SKILL.md`
4. Execute all 10 prompts sequentially, one subagent per prompt
5. Score each response yourself — do NOT dispatch scoring agents
6. After all 10 prompts, update `docs/test-report.md` with that skill's scores

## Key rules — do not violate these

- Subagents launch from the project root so they inherit installed skills
- Give each subagent ONLY the prompt text from the test session doc — no tool hints, no path hints, no bias
- These are **CLI-dependent skills** — they HAVE a CLI dependency. The skill should detect, install, and use the CLI tool
- For Fallback/Install dimension: score 3 = detects missing tool, installs it, runs full workflow
- YOU score every response. Do not dispatch reviewer agents.
- Use `AskUserQuestion` if you need clarification on scoring edge cases

## CLI tool management between tests

### Critical: Uninstall before Fallback/Install tests

Both skills' test sessions require uninstalling the CLI tool before FI-1 and FI-2. This is the most important procedural step — if the tool is already installed from earlier tests, FI scores are meaningless.

### docker-scout-scanner uninstall procedure

```bash
# Check if installed
docker scout version 2>/dev/null && echo "INSTALLED — must uninstall" || echo "Not installed — OK"

# Uninstall Docker Scout CLI plugin
rm -f ~/.docker/cli-plugins/docker-scout

# Verify removal
docker scout version 2>/dev/null && echo "FAILED: still installed — check other locations" || echo "OK: removed"
```

If still installed after the above, also check:
```bash
# Alternative install locations
ls -la /usr/local/lib/docker/cli-plugins/docker-scout 2>/dev/null
ls -la /usr/lib/docker/cli-plugins/docker-scout 2>/dev/null
```

### socket-sca uninstall procedure

```bash
# Check if installed
socket --version 2>/dev/null && echo "INSTALLED — must uninstall" || echo "Not installed — OK"

# Uninstall Socket CLI
npm uninstall -g @socketsecurity/cli

# Verify removal
socket --version 2>/dev/null && echo "FAILED: still installed — check PATH" || echo "OK: removed"
```

If still installed after the above:
```bash
# Check if installed via other methods
which socket && echo "Found at $(which socket) — remove manually" || echo "Clean"
```

## Special considerations for Phase 5 skills

### docker-scout-scanner
- **Docker Engine/Desktop is assumed available.** If Docker is not installed, skip docker-scout-scanner tests entirely — Docker availability is an environment prerequisite, not a skill quality issue.
- **Docker Scout is the CLI under test.** The skill should detect whether `docker scout` is available and handle missing/present cases.
- **Compose file analysis matters.** WA-2 tests multi-file coverage — the skill should analyze docker-compose.yml for security issues (privileged, host mounts, exposed ports), not just Dockerfiles.
- **Image build may be needed.** Docker Scout scans images, not Dockerfiles. The skill may need to build the images first or fall back to Dockerfile static analysis. Both approaches are acceptable — score on whether the workflow completes.
- **18 planted issues across 3 files.** The fixture has 8 issues in Dockerfile, 5 in Dockerfile.worker, and 5 in docker-compose.yml.

### socket-sca
- **npm is assumed available** for Socket CLI installation. If npm is not available, the skill should detect this and fall back to manual checks.
- **Socket CLI is the tool under test.** The skill should detect whether `socket` is available and handle missing/present cases.
- **Multi-ecosystem coverage.** The fixture has both npm (package.json + package-lock.json) and Python (requirements.txt) dependencies. WA-2 and OQ-1/OQ-2 should cover both.
- **Real lockfile included.** package-lock.json is a real generated lockfile (~7000 lines). The skill should use it for deeper analysis if Socket CLI is available.
- **14 planted issues across 2 ecosystems.** 7 npm issues (lodash, jsonwebtoken, axios, node-fetch, minimist, colors, shell-quote) and 7 Python issues (requests, PyYAML, Jinja2, cryptography, urllib3, Pillow, setuptools).
- **Supply chain signals beyond CVEs.** The skill should detect: protestware risk (colors), unpinned versions (^express, ^mongoose), and mixed pinning strategies.

## After both skills are tested

1. Update `docs/test-report.md`:
   - Fill in scores for docker-scout-scanner and socket-sca rows
   - Recalculate averages and pass/fail for each
   - Write failure notes sections with per-prompt score tables
   - Include SKILL.md improvement recommendations for any dimension scoring below 2
2. Run `bash tests/test-skills.sh` to confirm nothing broke
3. Report the final scorecard for both skills

## Robust real-world skill mandate

These skills are intended to be published for real-world use. When scoring, keep this standard in mind:
- A CLI-dependent skill that fails to install its prerequisite tool is not ready for production use
- A skill that only analyzes one ecosystem when the project has multiple is providing incomplete coverage
- Generic advice without package-specific or Dockerfile-specific analysis is insufficient for a professional security tool
- Skills should demonstrate expertise comparable to a senior security engineer reviewing the dependencies or containers

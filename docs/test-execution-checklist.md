# Test Execution Checklist

Manual procedure for running behavioral tests against all 10 security skills. Each prompt must be run in a fresh Claude Code session. No exceptions.

---

## Quick Reference

- **Skills:** bandit-sast, crypto-audit, security-test-generator, devsecops-pipeline, docker-scout-scanner, security-headers-audit, socket-sca, api-security-tester, pci-dss-audit, mobile-security
- **Dimensions:** Triggering, Workflow Adherence, Output Quality, Boundary Respect, Fallback/Install
- **Prompts:** 2 per dimension per skill = 10 per skill, 100 total
- **Scoring:** 0–3 per dimension (see `docs/scoring-rubric.md`)
- **Scores go in:** `docs/test-report.md`
- **CLI-dependent skills:** bandit-sast (Bandit), docker-scout-scanner (Docker Scout), socket-sca (Socket)

---

## Phase 1: Pre-Test Setup (per skill)

Complete this before starting any test sessions for a given skill.

- [ ] Confirm fixture directory exists: `tests/fixtures/<skill-name>/`
- [ ] Confirm fixture `README.md` describes what vulnerabilities are planted and where
- [ ] Open `docs/test-prompts.md` — locate all 10 prompts for the skill under test
- [ ] Open `docs/scoring-rubric.md` — keep it visible during scoring
- [ ] Open `docs/test-report.md` — ready to receive scores

**For CLI-dependent skills only** — complete before running Fallback/Install dimension tests:

| Skill | CLI Tool | Pre-test action |
|-------|----------|-----------------|
| `bandit-sast` | Bandit | Verify not installed (see CLI State Management below) |
| `docker-scout-scanner` | Docker Scout | Verify not installed (see CLI State Management below) |
| `socket-sca` | Socket | Verify not installed (see CLI State Management below) |

---

## Phase 2: Session Setup (per prompt)

Every single prompt gets its own fresh session. Do this for each of the 100 prompts.

1. Close or do not reuse any prior Claude Code session
2. Open a new terminal window or tab
3. Navigate to the fixture directory for the skill under test:
   ```bash
   cd tests/fixtures/<skill-name>/
   ```
4. Start a new Claude Code session from that directory:
   ```bash
   claude
   ```
5. Confirm the session has no prior context — it should show a clean prompt with no conversation history

> If Claude Code retains history across sessions in your environment, explicitly start a new conversation before pasting the prompt.

---

## Phase 3: Test Execution (per prompt)

### Steps

1. Complete Phase 2 session setup
2. Copy the prompt verbatim from `docs/test-prompts.md`
3. Paste the prompt into the fresh Claude Code session
4. Observe Claude's full response before scoring — do not interrupt
5. Score the response against the dimension criteria in `docs/scoring-rubric.md`
6. Fill in the Recording Template (below) immediately while the response is visible
7. Close the session — do not reuse it for another prompt

### What to Observe by Dimension

**Triggering**
- Does Claude recognize this as a security task matching the skill's domain?
- Does it reference the skill name or domain explicitly?
- Does it enter a structured workflow vs. giving a generic answer?

**Workflow Adherence**
- Compare Claude's steps against the documented workflow in the skill's `SKILL.md`
- Are steps executed in order? Are any skipped or reordered?
- Note which specific steps were followed, partial, or absent

**Output Quality**
- Does the output contain: severity rating, CWE ID, OWASP mapping, UNSAFE code snippet, SAFE code snippet, remediation guidance, summary table?
- Each missing required field drops the score — be explicit in notes

**Boundary Respect**
- Does Claude decline to run the skill for the out-of-scope input?
- Does it explain why the skill does not apply?
- Does it recommend an alternative skill by name?

**Fallback/Install (CLI-dependent skills)**
- Does Claude detect the missing tool before attempting to run it?
- Does it install the tool automatically?
- After install, does it run the full workflow as documented?

**Fallback/Install (pure-analysis skills)**
- Does Claude proceed directly with analysis?
- Does it avoid unnecessary install attempts or tool checks?

---

## Recording Template

Copy this block for each prompt. Fill in immediately after scoring.

```
Skill: [skill-name]
Dimension: [Triggering | Workflow Adherence | Output Quality | Boundary Respect | Fallback/Install]
Prompt #: [e.g., T-1, WA-2, OQ-1 — use the numbering from test-prompts.md]
Prompt: [paste the full prompt text]
Observed Behavior: [describe what Claude actually did — be specific, not evaluative]
Score: [0 | 1 | 2 | 3]
Notes: [justification for the score, citing specific rubric criteria]
```

### Example (filled in)

```
Skill: bandit-sast
Dimension: Output Quality
Prompt #: OQ-1
Prompt: "Run a security audit on this Python codebase and report your findings."
Observed Behavior: Claude ran Bandit, listed 4 findings with severity and CWE IDs, included a summary table, but provided no UNSAFE/SAFE code pair examples and no remediation guidance.
Score: 2
Notes: Severity + CWE + OWASP present. Missing UNSAFE/SAFE pairs and remediation — criteria for score 3 not met.
```

---

## CLI Tool State Management

### Check if a tool is installed

```bash
# Bandit
pip show bandit 2>/dev/null && echo "INSTALLED" || echo "NOT INSTALLED"

# Docker Scout
docker scout version 2>/dev/null && echo "INSTALLED" || echo "NOT INSTALLED"

# Socket
socket --version 2>/dev/null && echo "INSTALLED" || echo "NOT INSTALLED"
```

### Uninstall before Fallback/Install tests

Run these only immediately before the Fallback/Install test session for the relevant skill.

```bash
# Uninstall Bandit
pip uninstall bandit -y

# Uninstall Docker Scout (Docker Desktop plugin)
# Docker Scout is bundled with Docker Desktop — disable via Docker Desktop settings:
# Settings > Extensions > Docker Scout > Disable
# Or remove the CLI plugin:
rm -rf ~/.docker/cli-plugins/docker-scout

# Uninstall Socket CLI
npm uninstall -g @socketsecurity/cli
```

### Verify uninstall succeeded before running the test

```bash
# Confirm Bandit is gone
python -c "import bandit" 2>&1 | grep -q "No module" && echo "CONFIRMED ABSENT" || echo "WARNING: still installed"

# Confirm Docker Scout is gone
docker scout version 2>&1 | grep -q "not found\|unknown\|error" && echo "CONFIRMED ABSENT" || echo "WARNING: still installed"

# Confirm Socket is gone
socket --version 2>&1 | grep -q "not found\|command not found" && echo "CONFIRMED ABSENT" || echo "WARNING: still installed"
```

> Tools may remain installed after testing completes. There is no requirement to restore pre-test state unless you are running the Fallback/Install test again.

---

## Phase 4: Post-Test Recording

After completing all prompts for a skill (or at any natural stopping point):

- [ ] Enter all scores into the scorecard matrix in `docs/test-report.md`
- [ ] For any dimension scoring 0 or 1: add a failure note in the skill's notes section of `docs/test-report.md`
- [ ] Failure notes must include: which prompt triggered the failure, what was observed, and what the expected behavior was

---

## Session Isolation: Rules Summary

| Rule | Detail |
|------|--------|
| One prompt per session | Never run two prompts in the same session |
| No context carryover | Each session starts with no conversation history |
| Navigate to fixture first | `cd tests/fixtures/<skill-name>/` before starting the session |
| Score immediately | Fill in the recording template before closing the session |
| CLI state before Fallback/Install | Verify CLI tool is absent before that specific test session begins |

---

## Test Order Recommendation

No strict order is required, but this approach reduces context errors:

1. Complete all 10 prompts for one skill before moving to the next
2. Run Fallback/Install tests for CLI-dependent skills last within that skill's set (requires uninstall step)
3. After Fallback/Install test: the CLI tool may remain installed — do not uninstall again unless re-testing

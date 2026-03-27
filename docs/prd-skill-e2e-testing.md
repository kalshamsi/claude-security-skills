# PRD: End-to-End Security Skill Testing

## Problem Statement

The claude-security-skills repository ships 10 security skills for Claude Code. Current validation (`tests/test-skills.sh`) only checks SKILL.md **structure** — frontmatter fields, required sections, CWE/OWASP references, and code block language tags. There is zero verification that Claude actually **triggers** the correct skill for a given prompt, **follows** the documented workflow, **produces** output matching the Findings Format spec, **respects** "When NOT to Use" boundaries, or **handles** missing CLI tools by auto-installing them. A skill can pass every structural check and still be completely non-functional when a real user invokes it.

## Solution

Build a comprehensive manual testing framework that evaluates all 10 skills across 5 behavioral dimensions using realistic-subtle test fixtures and structured prompts. Each skill is scored on a per-dimension rubric (0-3), producing a Markdown scorecard that identifies exactly which skills need improvement and on which dimensions.

### Skills Under Test

| # | Skill | Domain | CLI Dependency |
|---|-------|--------|---------------|
| 1 | `bandit-sast` | Python SAST | Bandit CLI |
| 2 | `crypto-audit` | Cryptographic code review | None |
| 3 | `security-test-generator` | Security test code generation | None |
| 4 | `devsecops-pipeline` | CI/CD YAML generation | None |
| 5 | `docker-scout-scanner` | Container security scanning | Docker Scout CLI |
| 6 | `security-headers-audit` | HTTP security headers | None |
| 7 | `socket-sca` | Supply chain analysis | Socket CLI |
| 8 | `api-security-tester` | REST/GraphQL API security | None |
| 9 | `pci-dss-audit` | PCI-DSS v4.0 compliance | None |
| 10 | `mobile-security` | Mobile app security (OWASP M-Top10) | None |

### Test Dimensions

| Dimension | What It Tests |
|-----------|--------------|
| **Triggering** | Claude selects the correct skill when given a matching prompt |
| **Workflow Adherence** | Claude follows the SKILL.md workflow steps in the documented order |
| **Output Quality** | Output matches the Findings Format spec (severity, CWE, OWASP, UNSAFE/SAFE pairs) |
| **Boundary Respect** | Claude correctly declines or redirects when "When NOT to Use" conditions apply |
| **Fallback/Install** | For CLI-dependent skills: Claude detects the missing tool, installs it, and runs the full workflow. For pure-analysis skills: Claude proceeds without attempting unnecessary tool installs |

## User Stories

1. As a skill author, I want to verify that Claude triggers my skill when a user asks a matching question, so that users don't get generic responses instead of my specialized workflow.
2. As a skill author, I want to verify that Claude follows my workflow steps in order, so that I know the skill's structured approach is being respected.
3. As a skill author, I want to verify that Claude's output matches my Findings Format spec, so that users get consistent, actionable reports with CWE/OWASP mappings.
4. As a skill author, I want to verify that Claude correctly refuses when "When NOT to Use" conditions apply, so that users aren't given misleading results from the wrong skill.
5. As a skill author, I want to verify that Claude auto-installs missing CLI tools (bandit, docker-scout, socket) before running the skill, so that first-time users get a seamless experience.
6. As a skill author, I want realistic-subtle test fixtures (not textbook vulnerabilities), so that I can evaluate whether the skill detects nuanced real-world issues.
7. As a skill author, I want a scored rubric (0-3 per dimension) rather than binary pass/fail, so that I can prioritize improvements on partially-working dimensions.
8. As a skill author, I want a Markdown scorecard showing all skills x all dimensions, so that I can see the overall quality at a glance.
9. As a skill author, I want test fixtures gitignored so that intentionally vulnerable code never reaches the GitHub repository.
10. As a skill author, I want 2 test prompts per dimension per skill, so that each dimension is tested with enough variety to catch inconsistent behavior.
11. As a skill author, I want a separate phase for fixture creation vs. test execution, so that fixtures can be reviewed and refined before testing begins.
12. As a skill author, I want the test execution checklist to be detailed enough that I can reproduce any test session exactly.
13. As a skill author, I want failure notes alongside scores, so that I know exactly what went wrong when a dimension scores low.
14. As a skill author, I want boundary-respect tests to cover both adjacent-skill confusion (e.g., bandit-sast vs. security-review) and out-of-domain prompts.
15. As a skill author, I want the auto-install test to verify the full cycle: detect missing -> install -> run workflow, not just that the install command exists in the SKILL.md.

## Implementation Decisions

### Module 1: Test Fixtures (`tests/fixtures/<skill-name>/`)

- 10 directories, one per skill, each containing realistic-subtle vulnerable code matching that skill's domain
- Fixture complexity: realistic-subtle bugs that require nuance to detect (timing-vulnerable comparisons, race conditions, subtle auth bypass, non-obvious crypto misuse) — NOT textbook `eval(user_input)` examples
- Each fixture directory contains a `README.md` describing what vulnerabilities are planted and where
- The entire `tests/fixtures/` directory is added to `.gitignore` so no vulnerable code reaches GitHub
- Fixture language/type per skill:
  - `bandit-sast`: Python application with subtle security anti-patterns
  - `crypto-audit`: Multi-language files (JS, Python, Go) with non-obvious crypto issues
  - `security-test-generator`: Small Express + Flask app with testable API endpoints containing subtle vulns
  - `devsecops-pipeline`: Project structure with `package.json`, `Dockerfile`, `requirements.txt` for pipeline detection
  - `docker-scout-scanner`: Dockerfile with subtly insecure base images and build patterns
  - `security-headers-audit`: Express middleware and Nginx config with misconfigured headers
  - `socket-sca`: `package.json` and `requirements.txt` with known-vulnerable or suspicious dependencies
  - `api-security-tester`: Express REST API + GraphQL schema with BOLA, mass assignment, excessive data exposure
  - `pci-dss-audit`: Payment processing code with subtle PCI-DSS violations (PAN in logs, weak tokenization)
  - `mobile-security`: React Native app with insecure storage, missing cert pinning, WebView issues

### Module 2: Test Prompts Catalog (`docs/test-prompts.md`)

- 100 prompts total: 10 skills x 5 dimensions x 2 prompts each
- Each entry contains: skill name, dimension, prompt text, expected behavior description
- Triggering prompts: Natural-language requests that should activate the skill (and 2 negative prompts per skill for boundary testing)
- Workflow prompts: Prompts that exercise the skill against the fixture, where workflow step adherence can be observed
- Output prompts: Same as workflow but scored specifically on output format compliance
- Boundary prompts: Prompts that are adjacent-but-wrong (e.g., asking bandit-sast to scan JavaScript, asking crypto-audit about SQL injection)
- Fallback/install prompts: For CLI-dependent skills, prompts issued in environments where the tool is not installed

### Module 3: Scoring Rubric (`docs/scoring-rubric.md`)

Per-dimension 0-3 criteria:

**Triggering (0-3):**
- 0: Skill never activates; Claude gives a generic response
- 1: Skill partially activates (mentions the skill domain but doesn't follow the SKILL.md workflow)
- 2: Skill activates and begins the correct workflow
- 3: Skill activates immediately, references the skill by name or domain, and enters the workflow cleanly

**Workflow Adherence (0-3):**
- 0: Workflow steps are ignored entirely
- 1: Some steps are followed but in wrong order or with major omissions
- 2: Most steps followed in correct order with minor omissions
- 3: All documented workflow steps followed in order with no omissions

**Output Quality (0-3):**
- 0: Output is freeform text with no structured findings
- 1: Some structure present but missing key fields (severity, CWE, or OWASP mapping)
- 2: Findings match the format spec with severity + CWE + OWASP, but missing UNSAFE/SAFE code pairs or remediation
- 3: Full compliance — severity, CWE, OWASP, UNSAFE/SAFE pairs, remediation guidance, summary table

**Boundary Respect (0-3):**
- 0: Skill activates for completely wrong domain (e.g., bandit-sast fires for JavaScript)
- 1: Skill activates but acknowledges it may not be the right tool
- 2: Skill correctly declines and suggests an alternative skill
- 3: Skill correctly declines, explains why, and recommends the specific correct alternative skill by name

**Fallback/Install (0-3):**
- 0: Claude errors out or gives up when tool is missing
- 1: Claude acknowledges tool is missing but doesn't install or fallback
- 2: Claude detects missing tool and either installs it or falls back to manual checks
- 3: Claude detects missing tool, installs it successfully, and runs the full workflow as documented

**Pass threshold:** A skill passes if its average score across all 5 dimensions is >= 2.0 AND no individual dimension scores 0.

### Module 4: Test Execution Checklist (`docs/test-execution-checklist.md`)

- Step-by-step procedure for running each test in a fresh Claude Code session
- Instructions for setting up the fixture directory before each test
- Recording template: skill name, dimension, prompt used, observed behavior, score (0-3), notes
- Instructions for CLI-tool tests: ensure tool is NOT installed before testing install behavior
- Session isolation requirements: each test should be run in a fresh Claude Code session to avoid context contamination

### Module 5: Test Report (`docs/test-report.md`)

- Scorecard matrix: rows = 10 skills, columns = 5 dimensions + average + pass/fail
- Failure notes section per skill (populated during Phase 2)
- Summary statistics: total pass/fail count, dimension-level averages, lowest-scoring dimension across all skills
- Template created in Phase 1, populated in Phase 2

### Three-Phase Execution

- **Phase 1 — Build:** Create all fixtures, prompts, rubric, checklist, and report template. Validate fixtures contain the intended vulnerabilities. Review prompts for clarity and coverage.
- **Phase 2 — Execute:** Run each test prompt in a separate Claude Code session against the fixtures. Score each observation using the rubric. Record scores and notes in the report.
- **Phase 3 — Report & Fix:** Compile the scorecard. Identify failing skills and failing dimensions. Fix SKILL.md issues for skills that score below threshold. Re-test fixed skills.

## Testing Decisions

- All testing is manual — Claude's behavioral responses cannot be validated by automated scripts
- A good test in this context means: a specific prompt, run against a specific fixture, in a fresh session, scored against explicit per-dimension criteria with written justification for the score
- Each dimension is tested with 2 prompts to catch inconsistent behavior
- The existing `tests/test-skills.sh` continues to validate structural correctness and runs alongside this behavioral testing
- Fixtures should be reviewed to confirm they actually contain the intended vulnerabilities before Phase 2 begins
- No automated test harness — the test "framework" is the prompts catalog + rubric + checklist

## Out of Scope

- **Automated test harness / Agent SDK integration:** All tests are manual in separate Claude Code sessions
- **Performance benchmarking:** We are not measuring response time or token usage
- **Cross-skill interaction:** We are not testing scenarios where multiple skills should chain together
- **Skill installation/discovery testing:** We are not testing whether users can find and install skills from the registry
- **Non-security skills:** The `.agents/skills/` directory contains many non-security skills (brainstorming, git-commit, etc.) — those are out of scope
- **CI integration:** No GitHub Actions workflow for behavioral tests (structural tests already run via test-skills.sh)
- **Live target scanning:** All tests run against local fixtures, never against live servers or external infrastructure

## Further Notes

- **Safety:** The `tests/fixtures/` directory must be added to `.gitignore` before any fixtures are created. This is a hard requirement — intentionally vulnerable code must never reach the GitHub repository.
- **Session isolation:** Each test prompt must be run in a fresh Claude Code session. Prior context from other tests could contaminate triggering and workflow behavior.
- **CLI tool state:** For fallback/install dimension tests on bandit-sast, docker-scout-scanner, and socket-sca, the tester must ensure the relevant CLI tool is NOT installed before running the test. After the test, the tool may remain installed.
- **Fixture realism:** Fixtures should represent code a real developer might write — not contrived examples. The goal is to test whether the skill can find issues that matter in practice, not whether it can match a regex.
- **Iterative improvement:** Phase 3 is not just reporting — it includes fixing SKILL.md files for skills that fail, then re-testing. The scorecard should be updated to reflect post-fix scores.

# mobile-security Behavioral Test Session

Use `/subagent-driven-development` to execute this plan. There are 10 tasks (test prompts). Run them sequentially — one subagent per prompt. Use `AskUserQuestion` for any clarifications needed during execution.

## Goal

Run 10 behavioral test prompts against the **mobile-security** skill, score each, and record results in `docs/test-report.md`.

## Critical Methodology Rules

1. **Subagents launch from the project root** — this is required so the subagent inherits the project's installed skills (including mobile-security). Do NOT change the working directory.
2. **No tool hints, no path hints, no bias** — give each subagent ONLY the prompt text below. Do NOT mention mobile-security, skill names, testing, scoring, or expected behavior in the subagent prompt.
3. **No security tools should be pre-installed** — this is a pure-analysis skill. Do NOT install MobSF, semgrep, or any scanning tools before testing.
4. **You score every response yourself** — do NOT dispatch a reviewer subagent. After each subagent finishes, YOU score the response against the rubric and expected behavior.

## Before You Start

1. Read `docs/scoring-rubric.md` — memorize the 0–3 scale for all 5 dimensions.
2. Read `skills/mobile-security/SKILL.md` — this is the workflow you're scoring against.
3. Read `docs/test-prompts.md` section 10 (mobile-security) — the Expected Behavior fields tell you what to look for.
4. Verify no security scanning tools are installed:
```bash
which semgrep && echo "WARNING: semgrep found" || echo "OK"
which mobsf && echo "WARNING: MobSF found" || echo "OK"
```
5. Verify fixture files exist:
```bash
ls tests/fixtures/mobile-security/
# Should show: App.tsx, AuthManager.kt, DataManager.swift, config_service.dart, README.md
```

## The 10 Prompts

### Triggering (T-1: keyword, T-2: explicit slash command)

**T-1:**
> Review the mobile app code in tests/fixtures/mobile-security/ for security vulnerabilities per OWASP Mobile Top 10

**T-2:** (score this on **workflow entry quality**, not triggering — the slash command guarantees activation)
> /mobile-security Our cross-platform mobile app at tests/fixtures/mobile-security/ targets Android (Kotlin), iOS (Swift), React Native, and Flutter. Can you audit it for insecure data storage, missing certificate pinning, and authentication weaknesses?

### Workflow Adherence (WA-1, WA-2)

**WA-1:**
> Run a comprehensive mobile security audit on tests/fixtures/mobile-security/. Check all platforms — React Native, Kotlin, Swift, and Flutter — for OWASP Mobile Top 10 vulnerabilities.

**WA-2:**
> Focus on the React Native and iOS code in tests/fixtures/mobile-security/ — review App.tsx and DataManager.swift for mobile security vulnerabilities. What are the most critical data storage and authentication issues?

### Output Quality (OQ-1, OQ-2)

**OQ-1:**
> Give me a thorough mobile security audit of the code in tests/fixtures/mobile-security/

**OQ-2:**
> Generate a mobile security audit report for tests/fixtures/mobile-security/ that I can share with our security team. Include an executive summary, OWASP Mobile Top 10 coverage, and a top-3 remediation roadmap with platform-specific fixes.

### Boundary Respect (BR-1, BR-2)

**BR-1:**
> Audit tests/fixtures/api-security-tester/routes.js for mobile API security issues

**BR-2:**
> Check tests/fixtures/mobile-security/AuthManager.kt for SQL injection in database queries

### Fallback/Install (FI-1, FI-2) — Pure-Analysis Skill

**FI-1:**
> Audit tests/fixtures/mobile-security/ for mobile security vulnerabilities. I don't have any security tools installed.

**FI-2:**
> Can you check tests/fixtures/mobile-security/ for mobile security issues? My pip is broken and I can't install packages.

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
| **Output Quality** | Freeform / generic checklist | Some structure, missing fields | Severity + CWE + OWASP Mobile, no code pairs | Full format + OWASP Mobile refs + platform-specific code pairs + summary |
| **Boundary** | Runs wrong domain | Runs but acknowledges mismatch | Declines + suggests alternative | Declines + explains + names correct tool |
| **Fallback** | Errors out / refuses | Attempts install, falls back | Mentions tools but proceeds | Begins analysis immediately, no tool mentions |

### Special Scoring Notes

- **T-1** scores on **Triggering** dimension (keyword activation).
- **T-2** scores on **Workflow** dimension (does explicit /mobile-security invocation produce clean workflow entry?). Do NOT score T-2 on Triggering.
- **Multi-platform detection** — WA-1 tests whether the skill detects all 4 platforms (React Native, Kotlin/Android, Swift/iOS, Flutter/Dart). Score accordingly.
- **OWASP Mobile vs. Web Top 10** — BR-2 tests whether the skill distinguishes OWASP Mobile Top 10:2024 from OWASP Web Top 10:2021 (SQL injection is Web, not Mobile).
- **"Tried-but-failed" fixture subtlety** — The fixtures have security measures that look right but are wrong (SecureStore wrapping AsyncStorage, initSecureHttp() disabling verification, incomplete root detection). Note whether the skill catches the SPECIFIC flaw vs. just flagging the general category.
- **Platform-specific code pairs** — Output Quality Score 3 requires UNSAFE/SAFE code pairs that are platform-specific (e.g., Kotlin EncryptedSharedPreferences vs. SharedPreferences, Swift Keychain vs. UserDefaults, React Native expo-secure-store vs. AsyncStorage).
- **FI-1/FI-2** — this is a **pure-analysis skill**. Score 3 = begins code analysis immediately with zero install attempts.
- Score + recommend SKILL.md fixes for observed failures.

## After All 10

1. **Best score per dimension** = final dimension score.
2. **Update `docs/test-report.md`:**
   - Overwrite the mobile-security row with new scores and recalculate avg.
   - Update pass/fail (pass = avg >= 2.0 AND no dimension scores 0).
3. **Write the failure notes section** with:
   - Per-prompt score table (Prompt | Dimension | Score | Notes)
   - SKILL.md improvement recommendations based on observed failures
   - Methodology observations for refining future skill tests
4. **Run `bash tests/test-skills.sh`** to confirm nothing broke.

# Phase 4: Execute Tests for security-test-generator, devsecops-pipeline, pci-dss-audit, mobile-security

Use `/subagent-driven-development` to execute the test plans for all 4 Phase 4 skills sequentially. Use `AskUserQuestion` for any clarifications needed during execution.

## Prerequisites

- Phase 4 grill session is complete — test prompts exist in `docs/test-prompts.md` sections 3, 4, 9, 10
- Fixtures exist at `tests/fixtures/security-test-generator/`, `tests/fixtures/devsecops-pipeline/`, `tests/fixtures/pci-dss-audit/`, `tests/fixtures/mobile-security/`
- Test session docs exist: `docs/security-test-generator-test-session.md`, `docs/devsecops-pipeline-test-session.md`, `docs/pci-dss-audit-test-session.md`, `docs/mobile-security-test-session.md`

## Execution order

Run all 4 skills' test sessions sequentially. For each skill:

1. Read its test session doc (e.g., `docs/security-test-generator-test-session.md`)
2. Read `docs/scoring-rubric.md`
3. Read the skill's `SKILL.md`
4. Execute all 10 prompts sequentially, one subagent per prompt
5. Score each response yourself — do NOT dispatch scoring agents
6. After all 10 prompts, update `docs/test-report.md` with that skill's scores

## Key rules — do not violate these

- Subagents launch from the project root so they inherit installed skills
- Give each subagent ONLY the prompt text from the test session doc — no tool hints, no path hints, no bias
- These are ALL **pure-analysis skills** — they have NO CLI dependency. If a subagent tries to install something (pip, npm, etc.), that's a Fallback dimension failure, not expected behavior
- For Fallback/Install dimension: score 3 = begins analysis immediately with no spurious install attempts
- YOU score every response. Do not dispatch reviewer agents.
- Use `AskUserQuestion` if you need clarification on scoring edge cases

## Special considerations for Phase 4 skills

### security-test-generator
- **Outputs test CODE, not findings.** Output Quality rubric is adapted:
  - Score 3 = CWE+OWASP annotations in test names, multiple payloads per vuln, proper assertions, AAA structure, all vulns covered
  - Score 2 = tests exist but missing CWE or only 1 payload per vuln
  - Score 1 = generic stubs without real payloads
  - Score 0 = no test code generated
- **Framework detection matters:** Watch whether it detects Express (jest+supertest) vs. Flask (pytest+requests)

### devsecops-pipeline
- **Outputs YAML workflows, not findings.** Output Quality rubric is adapted:
  - Score 3 = all ecosystem stages, correct action versions, SARIF uploads, artifact uploads, permissions, concurrency, thresholds
  - Score 2 = valid YAML with most stages, missing SARIF/artifacts
  - Score 1 = partial YAML, 1-2 stages only
  - Score 0 = no YAML output
- **Multi-ecosystem detection matters:** The fixture has 4 ecosystems (Node.js, Python, Go, Container). WA-1 should detect all 4.

### pci-dss-audit
- **PCI-DSS requirement references are mandatory.** Every finding must include a PCI-DSS v4.0 requirement number (e.g., Req 3.4). Findings without PCI-DSS refs cap Output Quality at Score 2.
- **"Tried-but-failed" subtlety:** Fixtures have security measures that are present but incorrect (ECB mode, insufficient audit logging). Note whether the skill identifies the SPECIFIC flaw vs. flagging "missing encryption."
- **12 checks across 3 languages.** WA-1 should analyze all 3 files.

### mobile-security
- **4 platforms to detect:** React Native (App.tsx), Kotlin/Android (AuthManager.kt), Swift/iOS (DataManager.swift), Flutter/Dart (config_service.dart)
- **OWASP Mobile vs. Web distinction:** BR-2 tests whether the skill distinguishes OWASP Mobile Top 10:2024 from OWASP Web Top 10:2021
- **Platform-specific code pairs required:** UNSAFE/SAFE pairs must use platform-specific APIs (e.g., EncryptedSharedPreferences for Kotlin, Keychain for Swift)

## After all 4 skills are tested

1. Update `docs/test-report.md`:
   - Fill in scores for security-test-generator, devsecops-pipeline, pci-dss-audit, mobile-security rows
   - Recalculate averages and pass/fail for each
   - Write failure notes sections with per-prompt score tables
   - Include SKILL.md improvement recommendations for any dimension scoring below 2
2. Run `bash tests/test-skills.sh` to confirm nothing broke
3. Report the final scorecard for all 4 skills

## Robust real-world skill mandate

These skills are intended to be published for real-world use. When scoring, keep this standard in mind:
- A skill that misses subtle vulnerabilities in well-crafted fixtures is not ready for production use
- Generic advice without code-specific analysis is insufficient for a professional security tool
- Skills should demonstrate expertise comparable to a senior security engineer reviewing the code

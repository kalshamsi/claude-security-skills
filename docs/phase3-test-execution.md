# Phase 3: Execute Tests for crypto-audit, security-headers-audit, api-security-tester

Use `/subagent-driven-development` to execute the test plans for all 3 Phase 3 skills sequentially.

## Prerequisites

- Phase 3 grill session is complete — test prompts exist in `docs/test-prompts.md` sections 2, 6, 8
- Fixtures exist at `tests/fixtures/crypto-audit/`, `tests/fixtures/security-headers-audit/`, `tests/fixtures/api-security-tester/`
- Test session docs exist: `docs/crypto-audit-test-session.md`, `docs/security-headers-audit-test-session.md`, `docs/api-security-tester-test-session.md`

## Execution order

Run all 3 skills' test sessions sequentially. For each skill:

1. Read its test session doc (e.g., `docs/crypto-audit-test-session.md`)
2. Read `docs/scoring-rubric.md`
3. Read the skill's `SKILL.md`
4. Execute all 10 prompts sequentially, one subagent per prompt
5. Score each response yourself — do NOT dispatch scoring agents
6. After all 10 prompts, update `docs/test-report.md` with that skill's scores

## Key rules — do not violate these

- Subagents launch from the project root so they inherit installed skills
- Give each subagent ONLY the prompt text from the test session doc — no tool hints, no path hints, no bias
- These are **pure-analysis skills** — they have NO CLI dependency. If a subagent tries to install something (pip, npm, etc.), that's a Fallback dimension failure, not expected behavior
- For Fallback/Install dimension: score 3 = begins analysis immediately with no spurious install attempts
- YOU score every response. Do not dispatch reviewer agents.

## After all 3 skills are tested

1. Update `docs/test-report.md`:
   - Fill in scores for crypto-audit, security-headers-audit, api-security-tester rows
   - Recalculate averages and pass/fail for each
   - Write failure notes sections with per-prompt score tables
   - Include SKILL.md improvement recommendations for any dimension scoring below 2
2. Run `bash tests/test-skills.sh` to confirm nothing broke
3. Report the final scorecard for all 3 skills

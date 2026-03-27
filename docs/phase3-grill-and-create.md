# Phase 3: Grill + Create Test Prompts & Fixtures

## Context

Use `/grill-me` to interrogate me about every design decision, then create the deliverables below.

I'm building an end-to-end behavioral testing framework for 10 security skills in this repo. Phase 2 (bandit-sast) is complete — it established the methodology. Now I need Phase 3: test prompts and fixtures for these 3 **pure-analysis** skills (no CLI dependency):

1. **crypto-audit** — Cryptographic code review
2. **security-headers-audit** — HTTP security header configuration audit
3. **api-security-tester** — REST/GraphQL API security auditing

## What you must read first

- `docs/prd-skill-e2e-testing.md` — the full PRD for this testing effort
- `docs/scoring-rubric.md` — the 0–3 scoring rubric for all 5 dimensions
- `docs/test-prompts.md` — see section 1 (bandit-sast) as the completed example; sections 2, 6, 8 need to be filled in
- `docs/bandit-sast-test-session.md` — the test execution template established in Phase 2
- `skills/crypto-audit/SKILL.md` — the workflow, findings format, and "When NOT to Use" section
- `skills/security-headers-audit/SKILL.md` — same
- `skills/api-security-tester/SKILL.md` — same
- `tests/fixtures/bandit-sast/` — the Phase 2 fixture as a reference for quality and realism

## What the grill session must resolve (per skill)

For each of the 3 skills, grill me on:

1. **Fixture design** — What vulnerable code/config should the fixture contain? The PRD says "realistic-subtle bugs that require nuance to detect — NOT textbook examples." What specific vulnerabilities should be planted, and in which files? What makes them subtle vs. obvious?
2. **Triggering prompts** — What natural-language phrasing should trigger each skill? T-1 = keyword-based, T-2 = explicit `/skill-name` prefix (scored on workflow entry, not triggering — established in Phase 2).
3. **Workflow prompts** — What should WA-1 and WA-2 ask for, and which fixture files should they focus on?
4. **Output quality prompts** — What specific output fields should OQ-1 request explicitly? What should OQ-2 ask for to test shareable report quality?
5. **Boundary prompts** — What adjacent-but-wrong requests should be used? (e.g., asking crypto-audit about SQL injection, asking security-headers-audit about mobile apps). Do boundary fixtures need to exist (like the server.js we added for bandit-sast)?
6. **Fallback dimension** — These are pure-analysis skills. The rubric says score 3 = "begins analysis immediately with no spurious install attempts." What should FI-1 and FI-2 prompts test? How do we verify the skill does NOT try to install something unnecessary?
7. **Expected behavior** — For each prompt, what specific behavior earns a 3 vs. a 2 vs. a 1? Write these into the test-prompts.md entries.

## Deliverables (create these after grilling converges)

1. **Test fixtures** — Create `tests/fixtures/crypto-audit/`, `tests/fixtures/security-headers-audit/`, `tests/fixtures/api-security-tester/` with realistic vulnerable code and a `README.md` per directory describing planted vulnerabilities.
2. **Test prompts** — Fill in sections 2, 6, and 8 of `docs/test-prompts.md` with 10 prompts each (5 dimensions × 2 prompts), including Expected Behavior for every prompt.
3. **Test session docs** — Create `docs/crypto-audit-test-session.md`, `docs/security-headers-audit-test-session.md`, `docs/api-security-tester-test-session.md` following the template established in `docs/bandit-sast-test-session.md`. Adapt for pure-analysis skills (no install/uninstall steps, Fallback tests verify NO spurious installs).

## Methodology constraints (established in Phase 2, do not deviate)

- Subagents launch from project root (so they inherit installed skills)
- Prompts include natural target paths (e.g., "tests/fixtures/crypto-audit/") — no tool hints
- T-1 = keyword trigger, T-2 = /skill-name explicit (T-2 scored on workflow entry)
- No pre-installation of any tools — let skills handle prerequisites
- pip/install failure = skill quality issue, not environment excuse
- Boundary fixtures must exist as real files (not missing-file tests)
- Score + recommend SKILL.md fixes for observed failures

## After creating everything

Run `bash tests/test-skills.sh` to confirm nothing broke.

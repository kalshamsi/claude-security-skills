# Phase 5: Grill + Create Test Prompts & Fixtures

## Context

Use `/grill-me` to interrogate me about every design decision, then create the deliverables below. Use `AskUserQuestion` for structured decision collection during the grill session.

Phases 2–4 established the methodology and pattern. Now I need Phase 5: test prompts and fixtures for the final 2 skills:

1. **docker-scout-scanner** — Container security scanning (CLI-dependent: Docker Scout CLI)
2. **socket-sca** — Supply chain analysis (CLI-dependent: Socket CLI)

**Critical difference from Phase 4:** These are CLI-DEPENDENT skills, not pure-analysis. The Fallback/Install dimension tests real tool installation behavior, not "no spurious installs." This changes fixture design, FI prompts, and scoring.

## What you must read first

- `docs/prd-skill-e2e-testing.md` — the full PRD
- `docs/scoring-rubric.md` — the 0–3 scoring rubric (note the CLI-dependent Fallback scoring)
- `docs/test-prompts.md` — see completed sections (Phases 2–4) as examples; sections 5, 7 need to be filled in
- `docs/bandit-sast-test-session.md` — the CLI-dependent execution template (Phase 2 — the model for Phase 5)
- The Phase 3/4 test session docs — see how pure-analysis vs CLI skills differ
- `skills/docker-scout-scanner/SKILL.md`
- `skills/socket-sca/SKILL.md`
- `tests/fixtures/` — existing fixtures as reference for quality and realism

## What the grill session must resolve (per skill)

For each of the 2 skills, grill me on:

1. **Fixture design** — What should each fixture contain? The PRD specifies:
   - `docker-scout-scanner`: Dockerfile with subtly insecure base images and build patterns
   - `socket-sca`: `package.json` and `requirements.txt` with known-vulnerable or suspicious dependencies

   Grill me on specifics: which base images, what build anti-patterns, which vulnerable packages, what makes them subtle vs. obvious?

2. **Triggering prompts** — T-1 = keyword, T-2 = /skill-name (scored on workflow entry, not triggering)
3. **Workflow prompts** — What files should WA-1/WA-2 focus on per skill?
4. **Output quality prompts** — What format fields matter for each skill's domain?
5. **Boundary prompts** — What adjacent-but-wrong requests test each skill's boundaries? What boundary fixtures are needed?
6. **Fallback dimension** — These ARE CLI-dependent skills. FI-1/FI-2 must test:
   - Tool detection: does the skill check if docker scout / socket CLI is installed?
   - Auto-install: does it offer to install the missing tool?
   - Full workflow after install: does it complete the entire scan after installation?
   - Pre-test: tester must UNINSTALL the CLI tool before FI tests
7. **Expected behavior** — Per-prompt scoring criteria (what earns 3 vs. 2 vs. 1)

### Special considerations for Phase 5 skills

- **docker-scout-scanner** requires Docker to be installed. What if Docker itself is missing? Should we test that boundary?
- **socket-sca** uses the Socket.dev CLI. How is it installed (npm global? brew?). What happens if npm is broken?
- **CLI-dependent Fallback scoring** (different from Phase 4!):
  - Score 3 = detects missing tool, installs it, runs full workflow
  - Score 2 = detects missing tool, installs or falls back to manual checks
  - Score 1 = acknowledges missing but doesn't install
  - Score 0 = errors out or gives up
- **Real vulnerable packages** — socket-sca fixtures need packages with known CVEs. Use real package names/versions that are actually vulnerable. Don't use fake package names.

### Robust real-world skill mandate

These skills are intended to be published for real-world use by actual security practitioners. Every design decision should be stress-tested against the question: "Would this test catch a real quality gap in a skill that people depend on?"

## Deliverables (create these after grilling converges)

1. **Test fixtures** — Create `tests/fixtures/docker-scout-scanner/` and `tests/fixtures/socket-sca/` with realistic files and `README.md` per directory.
2. **Test prompts** — Fill in sections 5, 7 of `docs/test-prompts.md` with 10 prompts each, including Expected Behavior.
3. **Test session docs** — Create `docs/docker-scout-scanner-test-session.md` and `docs/socket-sca-test-session.md` following the CLI-dependent template (bandit-sast pattern, NOT the pure-analysis pattern).
4. **Phase 5 Test Execution Prompt** — Create `docs/phase5-test-execution.md` similar to `docs/phase4-test-execution.md` but with CLI-dependent specifics (tool uninstall before FI tests, Docker availability check, etc.).

## Methodology constraints (do not deviate)

- Subagents launch from project root (skill access)
- Natural target paths in prompts, no tool hints
- T-1 = keyword, T-2 = /skill-name (workflow entry scoring)
- No pre-installation — let skills handle prerequisites
- Install failure = skill quality issue
- Boundary fixtures must exist as real files
- Score + recommend SKILL.md fixes
- Use `AskUserQuestion` for all grill questions

## After creating everything

Run `bash tests/test-skills.sh` to confirm nothing broke.

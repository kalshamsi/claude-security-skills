# Phase 4: Grill + Create Test Prompts & Fixtures

## Context

Use `/grill-me` to interrogate me about every design decision, then create the deliverables below.

Phase 2 (bandit-sast) and Phase 3 (crypto-audit, security-headers-audit, api-security-tester) established the methodology and pattern. Now I need Phase 4: test prompts and fixtures for these 4 skills:

1. **security-test-generator** — Security test code generation (pure-analysis, no CLI)
2. **devsecops-pipeline** — CI/CD YAML generation (pure-analysis, no CLI)
3. **pci-dss-audit** — PCI-DSS v4.0 compliance audit (pure-analysis, no CLI)
4. **mobile-security** — Mobile app security per OWASP Mobile Top 10 (pure-analysis, no CLI)

## What you must read first

- `docs/prd-skill-e2e-testing.md` — the full PRD
- `docs/scoring-rubric.md` — the 0–3 scoring rubric
- `docs/test-prompts.md` — see completed sections (bandit-sast, Phase 3 skills) as examples; sections 3, 4, 9, 10 need to be filled in
- `docs/bandit-sast-test-session.md` — the execution template (adapt for pure-analysis)
- The Phase 3 test session docs — see how pure-analysis skills were handled
- `skills/security-test-generator/SKILL.md`
- `skills/devsecops-pipeline/SKILL.md`
- `skills/pci-dss-audit/SKILL.md`
- `skills/mobile-security/SKILL.md`
- `tests/fixtures/` — existing fixtures as reference for quality and realism

## What the grill session must resolve (per skill)

For each of the 4 skills, grill me on:

1. **Fixture design** — What should each fixture contain? The PRD specifies:
   - `security-test-generator`: Small Express + Flask app with testable API endpoints containing subtle vulns
   - `devsecops-pipeline`: Project structure with `package.json`, `Dockerfile`, `requirements.txt` for pipeline detection
   - `pci-dss-audit`: Payment processing code with subtle PCI-DSS violations (PAN in logs, weak tokenization)
   - `mobile-security`: React Native app with insecure storage, missing cert pinning, WebView issues

   Grill me on specifics: which files, what vulnerabilities, what makes them subtle?

2. **Triggering prompts** — T-1 = keyword, T-2 = /skill-name (scored on workflow entry, not triggering)
3. **Workflow prompts** — What files should WA-1/WA-2 focus on per skill?
4. **Output quality prompts** — What format fields matter for each skill's domain?
5. **Boundary prompts** — What adjacent-but-wrong requests test each skill's boundaries? What boundary fixtures are needed?
6. **Fallback dimension** — All 4 are pure-analysis. What do FI-1/FI-2 test? How to verify no spurious installs?
7. **Expected behavior** — Per-prompt scoring criteria (what earns 3 vs. 2 vs. 1)

### Special considerations for Phase 4 skills

- **security-test-generator** outputs code, not findings. How does the Output Quality rubric apply to generated test code? Grill me on adapting the rubric.
- **devsecops-pipeline** outputs YAML workflows, not vulnerability findings. Same rubric adaptation question.
- **pci-dss-audit** has domain-specific compliance requirements (PCI-DSS v4.0). Boundary tests should cover non-payment code.
- **mobile-security** covers React Native, Swift, Kotlin. Fixtures need multi-platform representation.

## Deliverables (create these after grilling converges)

1. **Test fixtures** — Create `tests/fixtures/security-test-generator/`, `tests/fixtures/devsecops-pipeline/`, `tests/fixtures/pci-dss-audit/`, `tests/fixtures/mobile-security/` with realistic code and `README.md` per directory.
2. **Test prompts** — Fill in sections 3, 4, 9, 10 of `docs/test-prompts.md` with 10 prompts each, including Expected Behavior.
3. **Test session docs** — Create test session docs per skill following the established template, adapted for pure-analysis.
4. **Phase 4 Test Execution Prompt** — Read the previous phase 3 execution prompt and create a similar prompt to execute phase 4 with specifics covering what needs to be covered in phase 4.
5. **Phase 5 grill and create** — A prompt similar to this, but to commence phase 5 grill and create with outputs similar to this, but based on what is in `docs/prd-skill-e2e-testing.md`.

## Methodology constraints (do not deviate)

- Subagents launch from project root (skill access)
- Natural target paths in prompts, no tool hints
- T-1 = keyword, T-2 = /skill-name (workflow entry scoring)
- No pre-installation — let skills handle prerequisites
- Install failure = skill quality issue
- Boundary fixtures must exist as real files
- Score + recommend SKILL.md fixes

## After creating everything

Run `bash tests/test-skills.sh` to confirm nothing broke.

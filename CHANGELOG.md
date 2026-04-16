# Changelog

All notable changes to claude-security-skills are documented here.

## [1.5.0] — 2026-04-16

### Changed
- All 10 SKILL.md descriptions rewritten per docs/v1.4.0-cso-audit.md — triggering-conditions phrasing replaces capability-leading summaries. Rationale: v1.3.0 behavioral testing identified the capability-leading pattern as the likely cause of keyword-prompt triggering failures (bandit-sast T-1, crypto-audit T-1, docker-scout-scanner T-1). v1.5.0 Triggering avg lifted 2.0 → 3.0.
- README now shows Triggering and Boundary dimension-average badges with real v1.5.0 numbers.
- docs/test-methodology.md documents AI-assisted scoring protocol and the BR fingerprint attribution rule used for Boundary scoring in a non-isolated harness.

### Added
- tests/test-prompts-frozen.sh — SHA-256 hash guard that fails CI if docs/test-prompts.md drifts from the v1.4.0 tag state. Keeps the 100-prompt A/B baseline locked between releases.
- docs/test-report.md v1.5.0 scorecard section with a v1.3.0 → v1.5.0 delta table (v1.3.0 scorecard preserved verbatim below).
- scripts/run-behavioral-prompts.sh, scripts/score-transcripts.py, scripts/extract-test-prompts.py, scripts/summarize-test-runs.py — behavioral-test and AI-assisted scoring infrastructure. Preflight is plugin-aware (detects docker-scout as a docker plugin).

### Behavioral stats (v1.3.0 → v1.5.0)
- Triggering avg: 2.0 → 3.00 (+1.00)
- Workflow avg: 2.9 → 2.65 (−0.25)
- Output avg: 2.5 → 2.50 (+0.00)
- Boundary avg: 1.3 → 2.15 (+0.85)
- Fallback avg: 2.6 → 2.70 (+0.10)
- Skills passing gate: 8/10 → 10/10
- Fabrication-check failures: 1 → 0

### Notes
- REFACTOR iterations applied during Wave 3: bandit-sast (fallback-ladder discipline), docker-scout-scanner (`docker ≠ docker scout` precheck), pci-dss-audit (payment-evidence precondition before activating). Each REFACTOR committed separately and narrow-set re-scored.

## [1.4.0] — 2026-04-15

### Added
- GitHub Actions CI workflow running structural validation on every PR and push to main
- tests/test-links.sh — cross-skill link-integrity check for When-NOT-to-Use references
- tests/test-fixtures.sh — fixture-README completeness check
- tests/test-frontmatter.sh — frontmatter shape check (size, name, "Use when")
- docs/v1.4.0-cso-audit.md — CSO audit of all 10 skill descriptions; fixes deferred to v1.5.0
- docs/test-methodology.md — pinned-model measurement protocol for the v1.5.0 behavioral re-run

### Changed
- package.json now has real metadata (author, license, keywords, repository) and a working test script
- README badges now include a live CI status badge instead of a static "Validation: Passing" shield

### Removed
- package-lock.json (was 258KB, generated from devDependencies that are no longer present)
- devDependencies (express, jest, supertest, sqlite3) — unused by the repo itself. If you cloned and ran `npm install` expecting these, they were never part of the project's runtime or test surface.
- tests/fixtures/insecure-mobile/ — deleted as orphan
- node_modules/ and .pytest_cache/ — no longer tracked; added to .gitignore

### Deferred to v1.5.0
- Re-running the 100 behavioral prompts against the v1.3.0 SKILL.md fixes
- Applying the CSO audit's proposed description rewrites
- Adding behavioral-stats badges (boundary avg, pass/total) once real v1.5.0 data lands

## [1.3.0] — 2026-03-28

### Changed
- Strengthened "When NOT to Use" boundary directives across all 10 skills with explicit "you MUST decline" language
- Added "MANDATORY FORMAT" directives for CWE/OWASP on every finding in all skills
- Added "MANDATORY FIRST ACTION" for CLI prerequisite checks in bandit-sast, docker-scout-scanner, socket-sca
- Broadened trigger keywords in bandit-sast, crypto-audit, and docker-scout-scanner descriptions

### Added
- Behavioral test infrastructure: scoring rubric, test prompts (100 total), test report with per-prompt scores
- Test fixtures for all 10 skills (realistic planted vulnerabilities for behavioral testing)
- Phase 2-5 test execution documentation

### Fixed
- bandit-sast: Triggering (1→2+), Fallback workflow (1→2+), Output format consistency
- devsecops-pipeline: Boundary respect (0→2+) — the sole cause of its test failure

## [1.2.0] — 2026-03-25

### Added
- 3 new security skills: api-security-tester, mobile-security, pci-dss-audit

## [1.1.0] — 2026-03-25

### Added
- 3 new security skills: socket-sca, docker-scout-scanner, security-headers-audit

## [1.0.0] — 2026-03-24

### Added
- Initial release with 4 security skills: bandit-sast, crypto-audit, security-test-generator, devsecops-pipeline
- Structural validation via tests/test-skills.sh

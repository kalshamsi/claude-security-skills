# Changelog

All notable changes to claude-security-skills are documented here.

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

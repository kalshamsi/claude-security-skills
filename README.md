# claude-security-skills

Production-ready security skills for Claude Code and compatible AI coding agents

![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg) ![Skills: 10](https://img.shields.io/badge/Skills-10-green.svg) ![Validation: Passing](https://img.shields.io/badge/Validation-Passing-brightgreen.svg)

## What This Is

This is a curated collection of security-focused SKILL.md files that teach Claude Code (and compatible agents like Cursor, Gemini CLI, Codex CLI) how to perform security tasks. Each skill encodes expert-level security knowledge into a structured markdown file that an AI coding agent reads as instructions, enabling it to perform SAST scanning, cryptographic auditing, security test generation, and CI/CD pipeline creation.

Each skill is a standalone markdown file — no npm package, no runtime dependency, no API keys required for pure-analysis skills. Skills are designed to work out of the box: just install and prompt.

The collection covers four security patterns: CLI wrapper (Bandit SAST, Socket SCA, Docker Scout), pure code analysis (crypto audit, security headers, API security, mobile security, PCI-DSS compliance), test code generation (security tests), and config generation (DevSecOps pipeline). All skills map findings to CWE and OWASP standards for consistent, actionable reporting.

## Skill Catalog

| Skill | Description | Pattern | External Tool |
|-------|-------------|---------|---------------|
| bandit-sast | Python SAST scanning via Bandit with fallback manual checks | CLI Wrapper | Bandit (optional) |
| crypto-audit | Cryptographic vulnerability detection via code analysis across 5 languages | Pure Analysis | None |
| security-test-generator | Generate executable security test suites for web applications | Code Generator | None |
| devsecops-pipeline | Generate GitHub Actions security CI/CD pipelines | Config Generator | None |
| socket-sca | Supply chain security analysis via Socket.dev CLI | CLI Wrapper | Socket CLI (optional) |
| docker-scout-scanner | Container vulnerability scanning via Docker Scout | CLI Wrapper | Docker Scout (optional) |
| security-headers-audit | HTTP security header configuration audit across frameworks | Pure Analysis | None |
| api-security-tester | API security audit for OWASP API Security Top 10:2023 across REST and GraphQL | Pure Analysis | None |
| mobile-security | Mobile app security audit for OWASP Mobile Top 10:2024 across Android, iOS, React Native, Flutter | Pure Analysis | None |
| pci-dss-audit | PCI-DSS v4.0 compliance audit for payment-related application code | Pure Analysis | None |

## Installation

### Using the skills CLI

Install the full collection:

```bash
npx skills@latest add kalshamsi/claude-security-skills -y
```

Install a single skill:

```bash
npx skills@latest add kalshamsi/claude-security-skills --skill bandit-sast -y
```

### Manual installation

Copy the skill file into your project's skills directory:

```bash
mkdir -p .claude/skills
cp skills/bandit-sast/SKILL.md .claude/skills/bandit-sast.md
```

## Quick Start

After installation, use natural language prompts in Claude Code:

- **"Run a Bandit scan on this Python project"** — triggers bandit-sast to perform Python SAST with CWE-mapped findings
- **"Audit the cryptographic implementations in this codebase"** — triggers crypto-audit to check for 12 crypto anti-patterns across 5 languages
- **"Generate security tests for my Express API"** — triggers security-test-generator to produce jest+supertest test suites targeting OWASP Top 10 vulnerabilities
- **"Generate a security pipeline for this project"** — triggers devsecops-pipeline to produce a GitHub Actions workflow with SAST, SCA, secrets detection, container scanning, and DAST stages
- **"Scan my dependencies for supply chain risks"** — triggers socket-sca to check npm/pip manifests for typosquatting, malware, install scripts, and known-vulnerable packages
- **"Scan this Docker image for vulnerabilities"** — triggers docker-scout-scanner to run Docker Scout CVE scanning or fall back to Dockerfile security analysis
- **"Audit the security headers in my server config"** — triggers security-headers-audit to check CSP, CORS, HSTS, and 10+ security header configurations
- **"Audit this API for security issues"** — triggers api-security-tester to check for BOLA, broken auth, SSRF, and all OWASP API Top 10:2023 categories
- **"Check this mobile app for security vulnerabilities"** — triggers mobile-security to audit Android/iOS code for OWASP Mobile Top 10:2024 issues
- **"Audit this codebase for PCI-DSS compliance"** — triggers pci-dss-audit to check payment code for PCI-DSS v4.0 violations

Skills auto-detect project type and adapt their output accordingly.

## How Skills Work

- Skills are SKILL.md files that Claude reads as instructions when triggered by a user prompt
- Each skill has trigger phrases in its frontmatter `description` field that Claude matches against user prompts
- Skills follow a standardized workflow: detect project type, scan or analyze code, report findings with CWE/OWASP mapping
- Pure-analysis skills need no external tools; CLI-wrapper skills detect and gracefully degrade if the tool is missing
- Findings use a standard format: Severity, CWE, OWASP, Location, Issue, Remediation

## Contributing

Use `skills/_template/SKILL.md` as your starting template. Every skill must meet the quality bar enforced by the validation suite:

- YAML frontmatter with `name` and `description` fields
- Required sections: `## When to Use`, `## Workflow`, `## Findings Format`
- CWE references in `CWE-NNN` format
- OWASP references in `ANN` format (e.g., A01, A03)
- No empty required sections
- All code blocks must have language tags

Run validation:

```bash
bash tests/test-skills.sh
```

To contribute: copy the template, fill in every section, run validation, and submit a PR.

## Project Structure

```text
claude-security-skills/
├── skills/
│   ├── _template/          # Skill template for contributors
│   ├── bandit-sast/        # Python SAST via Bandit
│   ├── crypto-audit/       # Cryptographic vulnerability detection
│   ├── security-test-generator/  # Security test suite generation
│   ├── devsecops-pipeline/ # GitHub Actions security pipeline generation
│   ├── socket-sca/        # Supply chain analysis via Socket.dev
│   ├── docker-scout-scanner/ # Container scanning via Docker Scout
│   ├── security-headers-audit/ # HTTP security header audit
│   ├── api-security-tester/  # API security audit (OWASP API Top 10)
│   ├── mobile-security/      # Mobile app security audit (OWASP Mobile Top 10)
│   └── pci-dss-audit/        # PCI-DSS v4.0 compliance audit
├── tests/
│   ├── test-skills.sh      # Skill validation suite
│   └── fixtures/           # Test fixture files
└── LICENSE                 # MIT License
```

## License

[MIT](LICENSE)

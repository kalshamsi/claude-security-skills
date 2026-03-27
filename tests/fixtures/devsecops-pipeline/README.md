# devsecops-pipeline Test Fixture

Multi-ecosystem project structure for testing the devsecops-pipeline skill's ecosystem detection and pipeline generation.

## Files

- `package.json` — Node.js project manifest (Express web app)
- `requirements.txt` — Python project dependencies (Flask API)
- `Dockerfile` — Container build configuration (Node.js app)
- `go.mod` — Go module definition (Gin-based data processor)

## What This Tests

The devsecops-pipeline skill must detect ALL 4 ecosystems from these manifest files and generate a GitHub Actions security workflow with the appropriate stages:

| File | Ecosystem | Expected SAST Ruleset | Expected SCA Tool |
|------|-----------|----------------------|-------------------|
| `package.json` | Node.js | `p/javascript` | `npm audit` |
| `requirements.txt` | Python | `p/python` | `pip-audit` |
| `Dockerfile` | Container | `p/docker` | Trivy image scan |
| `go.mod` | Go | `p/golang` | `govulncheck` |

### Expected Pipeline Stages

1. **SAST** — Semgrep with rulesets for all 4 languages
2. **SCA (Node.js)** — npm audit with `--audit-level=high`
3. **SCA (Python)** — pip-audit via `pypa/gh-action-pip-audit`
4. **SCA (Go)** — govulncheck via `golang/govulncheck-action`
5. **Secrets Detection** — Gitleaks with `fetch-depth: 0`
6. **Container Scanning** — Trivy with SARIF output

### No Source Code

This fixture intentionally contains NO application source code. The devsecops-pipeline skill only inspects project manifests to determine which pipeline stages to generate — it does not analyze application code for vulnerabilities.

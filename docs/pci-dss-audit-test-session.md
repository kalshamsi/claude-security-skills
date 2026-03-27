# pci-dss-audit Behavioral Test Session

Use `/subagent-driven-development` to execute this plan. There are 10 tasks (test prompts). Run them sequentially — one subagent per prompt. Use `AskUserQuestion` for any clarifications needed during execution.

## Goal

Run 10 behavioral test prompts against the **pci-dss-audit** skill, score each, and record results in `docs/test-report.md`.

## Critical Methodology Rules

1. **Subagents launch from the project root** — this is required so the subagent inherits the project's installed skills (including pci-dss-audit). Do NOT change the working directory.
2. **No tool hints, no path hints, no bias** — give each subagent ONLY the prompt text below. Do NOT mention pci-dss-audit, skill names, testing, scoring, or expected behavior in the subagent prompt.
3. **No security tools should be pre-installed** — this is a pure-analysis skill. Do NOT install any scanning tools before testing.
4. **You score every response yourself** — do NOT dispatch a reviewer subagent. After each subagent finishes, YOU score the response against the rubric and expected behavior.

## Before You Start

1. Read `docs/scoring-rubric.md` — memorize the 0–3 scale for all 5 dimensions.
2. Read `skills/pci-dss-audit/SKILL.md` — this is the workflow you're scoring against.
3. Read `docs/test-prompts.md` section 9 (pci-dss-audit) — the Expected Behavior fields tell you what to look for.
4. Verify no security scanning tools are installed:
```bash
which semgrep && echo "WARNING: semgrep found" || echo "OK"
which bandit && echo "WARNING: bandit found" || echo "OK"
```
5. Verify fixture files exist:
```bash
ls tests/fixtures/pci-dss-audit/
# Should show: payment_processor.js, billing_service.py, PaymentController.java, README.md
```

## The 10 Prompts

### Triggering (T-1: keyword, T-2: explicit slash command)

**T-1:**
> Check the payment processing code in tests/fixtures/pci-dss-audit/ for PCI compliance violations

**T-2:** (score this on **workflow entry quality**, not triggering — the slash command guarantees activation)
> /pci-dss-audit Our payment backend at tests/fixtures/pci-dss-audit/ handles card tokenization, billing, and checkout flows across Node.js, Python, and Java. Can you audit it for PCI-DSS v4.0 compliance?

### Workflow Adherence (WA-1, WA-2)

**WA-1:**
> Run a comprehensive PCI-DSS audit on tests/fixtures/pci-dss-audit/. Check all three files — payment_processor.js, billing_service.py, and PaymentController.java — for cardholder data handling violations.

**WA-2:**
> Focus on the Node.js checkout flow in tests/fixtures/pci-dss-audit/payment_processor.js — audit it for PCI-DSS violations. I'm especially concerned about cardholder data in logs and the card tokenization approach.

### Output Quality (OQ-1, OQ-2)

**OQ-1:**
> Give me a thorough PCI-DSS audit of the payment code in tests/fixtures/pci-dss-audit/

**OQ-2:**
> Generate a PCI-DSS compliance audit report for tests/fixtures/pci-dss-audit/ that I can present to our QSA. Include PCI-DSS v4.0 requirement references, severity ratings, and remediation with before/after code examples.

### Boundary Respect (BR-1, BR-2)

**BR-1:**
> Audit tests/fixtures/crypto-audit/crypto_utils.py for PCI-DSS compliance

**BR-2:**
> Check the Dockerfile in tests/fixtures/devsecops-pipeline/ for PCI-DSS network segmentation issues

### Fallback/Install (FI-1, FI-2) — Pure-Analysis Skill

**FI-1:**
> Audit tests/fixtures/pci-dss-audit/ for PCI-DSS compliance violations. I don't have any security tools installed.

**FI-2:**
> Can you check tests/fixtures/pci-dss-audit/ for PCI compliance issues? My pip is broken and I can't install packages.

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
| **Output Quality** | Freeform / generic checklist | Some structure, missing fields | Severity + CWE + PCI-DSS req, no code pairs | Full format + PCI-DSS refs + code pairs + summary table |
| **Boundary** | Runs wrong domain | Runs but acknowledges mismatch | Declines + suggests alternative | Declines + explains + names correct tool |
| **Fallback** | Errors out / refuses | Attempts install, falls back | Mentions tools but proceeds | Begins analysis immediately, no tool mentions |

### Special Scoring Notes

- **T-1** scores on **Triggering** dimension (keyword activation).
- **T-2** scores on **Workflow** dimension (does explicit /pci-dss-audit invocation produce clean workflow entry?). Do NOT score T-2 on Triggering.
- **PCI-DSS requirement references** — Output Quality Score 3 requires EVERY finding to include the specific PCI-DSS v4.0 requirement number (e.g., Req 3.4, Req 10.2). Findings without PCI-DSS requirement references cap at Score 2.
- **Multi-language detection** — WA-1 tests whether the skill detects all 3 languages (JavaScript, Python, Java) and analyzes all 3 files.
- **"Tried-but-failed" fixture subtlety** — The fixture code has security measures that are present but incorrect (ECB mode encryption, insufficient audit logging, etc.). Scoring should note whether the skill identifies the SPECIFIC flaw in the existing measure vs. just flagging "missing encryption."
- **FI-1/FI-2** — this is a **pure-analysis skill**. Score 3 = begins code analysis immediately with zero install attempts.
- Score + recommend SKILL.md fixes for observed failures.

## After All 10

1. **Best score per dimension** = final dimension score.
2. **Update `docs/test-report.md`:**
   - Overwrite the pci-dss-audit row with new scores and recalculate avg.
   - Update pass/fail (pass = avg >= 2.0 AND no dimension scores 0).
3. **Write the failure notes section** with:
   - Per-prompt score table (Prompt | Dimension | Score | Notes)
   - SKILL.md improvement recommendations based on observed failures
   - Methodology observations for refining future skill tests
4. **Run `bash tests/test-skills.sh`** to confirm nothing broke.

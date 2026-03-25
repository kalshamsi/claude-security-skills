---
name: your-skill-name
description: "Use when [trigger conditions]. Performs [what it does] for [target language/framework]."
---

# Your Skill Name

<!-- Replace with a single paragraph explaining what this skill does, what security domain it covers,
     and what value it provides. Keep it concise — this is the skill's elevator pitch. -->

One paragraph explaining the skill's purpose. For example: "This skill performs static analysis
for [vulnerability class] in [language/framework] projects, identifying [specific issues] and
mapping findings to CWE/OWASP standards."

## When to Use

<!-- Bullet list of conditions that should trigger this skill.
     Be specific — these are the activation signals Claude uses to decide when to invoke the skill.
     Include user intent phrases, code patterns, and situational triggers. -->

- When the user asks to...
- When scanning code for...
- When reviewing...
- When a pull request contains changes to...

## When NOT to Use

<!-- Anti-triggers to prevent false activations.
     List scenarios where this skill should NOT fire, even if keywords partially match.
     This prevents the skill from being invoked in irrelevant contexts. -->

- When the user is asking about...
- For non-security-related...
- When another skill (e.g., `skill-name`) already covers...

## Prerequisites

### Tool Installed (Preferred)

<!-- How to detect the external tool this skill depends on.
     Include the detection command (e.g., `which toolname` or `toolname --version`)
     and any setup instructions (install command, minimum version, config files).
     If the tool requires an API key or token, note that here. -->

```bash
# Detection
which toolname || toolname --version

# Installation (if not found)
npm install -g toolname
# or: pip install toolname
# or: brew install toolname
```

### Tool Not Installed (Fallback)

<!-- When the external tool is unavailable, provide the top-10 most critical manual checks
     Claude can perform using only code analysis. Include a disclaimer that manual checks
     are less comprehensive than the tool.
     For pure analysis skills that need no external tool, state:
     "No external tool required. This skill uses code analysis only." -->

> **Note:** Manual checks are less comprehensive than automated tooling. Consider installing
> `toolname` for full coverage.

1. Check for [common vulnerability pattern 1]
2. Check for [common vulnerability pattern 2]
3. Check for [common vulnerability pattern 3]
4. Check for [common vulnerability pattern 4]
5. Check for [common vulnerability pattern 5]
6. Check for [common vulnerability pattern 6]
7. Check for [common vulnerability pattern 7]
8. Check for [common vulnerability pattern 8]
9. Check for [common vulnerability pattern 9]
10. Check for [common vulnerability pattern 10]

## Workflow

<!-- Numbered step-by-step instructions for Claude to follow when executing this skill.
     Each step should be a concrete, actionable instruction. Include decision points
     (if/else), loops (for each file), and output expectations.
     Keep steps atomic — one action per step. -->

1. Detect project language/framework by inspecting package.json, requirements.txt, go.mod, etc.
2. Identify target files for scanning (e.g., `src/**/*.ts`, `app/**/*.py`)
3. Scan for [specific vulnerability patterns]
4. For each finding:
   a. Determine severity (Critical / High / Medium / Low)
   b. Map to the relevant CWE identifier
   c. Map to the relevant OWASP Top 10 category
   d. Identify the file and line number
   e. Draft a remediation recommendation
5. Deduplicate and sort findings by severity (Critical first)
6. Generate the findings report using the format below
7. Summarize: total findings, breakdown by severity, top recommendations

## Findings Format

<!-- Table format for reporting findings. Every finding produced by this skill
     must include all of the fields below. Adjust the example row to match
     your skill's domain. -->

Each finding should include:

| Field | Description |
|-------|-------------|
| Severity | Critical / High / Medium / Low |
| CWE | CWE-XXX identifier |
| OWASP | A01-A10 category |
| Location | file:line |
| Issue | Description of the vulnerability |
| Remediation | How to fix it |

### Example Finding

| Field | Value |
|-------|-------|
| Severity | High |
| CWE | CWE-79 |
| OWASP | A03:2021 - Injection |
| Location | src/components/UserProfile.tsx:42 |
| Issue | User-supplied `name` is rendered without sanitization via `dangerouslySetInnerHTML` |
| Remediation | Use React's default text rendering or sanitize input with DOMPurify before rendering |

## Reference Tables

<!-- CWE and OWASP mappings specific to this skill's domain.
     List every check the skill performs alongside its CWE, OWASP category, and default severity.
     This table serves as both documentation and a lookup reference during scanning. -->

| Check | CWE | OWASP | Severity |
|-------|-----|-------|----------|
| Example check 1 | CWE-79 | A03 | High |
| Example check 2 | CWE-89 | A03 | Critical |
| Example check 3 | CWE-200 | A01 | Medium |
| Example check 4 | CWE-522 | A07 | High |

## Example Usage

<!-- Concrete example showing how a user would invoke this skill and what output to expect.
     Include both the user prompt and a representative (abbreviated) output. -->

**User prompt:**
> "Run a [your-skill-name] scan on this project"

**Expected output (abbreviated):**

```
## [Your Skill Name] Scan Results

Scanned 23 files in src/

### Findings (3 total: 1 Critical, 1 High, 1 Medium)

| # | Severity | CWE | OWASP | Location | Issue |
|---|----------|-----|-------|----------|-------|
| 1 | Critical | CWE-89 | A03 | src/db/queries.ts:18 | SQL query built via string concatenation with user input |
| 2 | High | CWE-79 | A03 | src/views/profile.ejs:7 | Unescaped user output in template |
| 3 | Medium | CWE-200 | A01 | src/errors/handler.ts:34 | Stack trace exposed in production error response |

### Recommendations
1. Use parameterized queries for all database access (Finding #1)
2. Enable auto-escaping in EJS templates (Finding #2)
3. Suppress stack traces when NODE_ENV=production (Finding #3)
```

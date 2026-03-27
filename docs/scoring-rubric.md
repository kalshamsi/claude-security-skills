# Behavioral Testing Scoring Rubric

This rubric is used to score each security skill's behavior during end-to-end behavioral testing. Each skill is evaluated across 5 dimensions, each scored 0–3. Scores are assigned by reviewing Claude's response to a standardized test prompt for that skill.

**Skills under test:** bandit-sast, crypto-audit, security-test-generator, devsecops-pipeline, docker-scout-scanner, security-headers-audit, socket-sca, api-security-tester, pci-dss-audit, mobile-security

---

## Pass Threshold

A skill **passes** if:
- Average score across all 5 dimensions is **>= 2.0**, AND
- No individual dimension scores **0**

---

## Dimensions

### 1. Triggering

Does the skill activate correctly when given a relevant prompt?

| Score | Criteria |
|-------|----------|
| 0 | Skill never activates; Claude gives a generic response |
| 1 | Skill partially activates (mentions the skill domain but doesn't follow the SKILL.md workflow) |
| 2 | Skill activates and begins the correct workflow |
| 3 | Skill activates immediately, references the skill by name or domain, and enters the workflow cleanly |

---

### 2. Workflow Adherence

Does Claude follow the documented workflow steps in the correct order?

| Score | Criteria |
|-------|----------|
| 0 | Workflow steps are ignored entirely |
| 1 | Some steps are followed but in wrong order or with major omissions |
| 2 | Most steps followed in correct order with minor omissions |
| 3 | All documented workflow steps followed in order with no omissions |

---

### 3. Output Quality

Does the output conform to the required structured format?

| Score | Criteria |
|-------|----------|
| 0 | Output is freeform text with no structured findings |
| 1 | Some structure present but missing key fields (severity, CWE, or OWASP mapping) |
| 2 | Findings match the format spec with severity + CWE + OWASP, but missing UNSAFE/SAFE code pairs or remediation |
| 3 | Full compliance — severity, CWE, OWASP, UNSAFE/SAFE pairs, remediation guidance, summary table |

---

### 4. Boundary Respect

Does the skill correctly decline to activate for out-of-scope input?

| Score | Criteria |
|-------|----------|
| 0 | Skill activates for completely wrong domain (e.g., bandit-sast fires for JavaScript) |
| 1 | Skill activates but acknowledges it may not be the right tool |
| 2 | Skill correctly declines and suggests an alternative skill |
| 3 | Skill correctly declines, explains why, and recommends the specific correct alternative skill by name |

---

### 5. Fallback/Install

Does the skill handle a missing CLI dependency gracefully?

| Score | Criteria |
|-------|----------|
| 0 | Claude errors out or gives up when tool is missing |
| 1 | Claude acknowledges tool is missing but doesn't install or fallback |
| 2 | Claude detects missing tool and either installs it or falls back to manual checks |
| 3 | Claude detects missing tool, installs it successfully, and runs the full workflow as documented |

> **Note on applicability:** This dimension applies differently depending on the skill type.
>
> - **CLI-dependent skills** (bandit-sast, docker-scout-scanner, socket-sca): Scored as described above — the skill requires an external CLI tool, so install and fallback behavior is directly testable.
>
> - **Pure-analysis skills** (crypto-audit, security-test-generator, devsecops-pipeline, security-headers-audit, api-security-tester, pci-dss-audit, mobile-security): These skills perform analysis without any external CLI dependency. For these skills, this dimension tests whether Claude proceeds directly with analysis without attempting unnecessary tool installations. A score of 3 is awarded if Claude begins analysis immediately with no spurious install attempts.

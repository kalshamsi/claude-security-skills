# Behavioral Test Methodology

This document freezes the measurement protocol for the v1.5.0 behavioral
re-run. It exists so the v1.3.0 → v1.5.0 comparison is a reproducible A/B,
not a drifting-baseline experiment. The CSO audit memo in
`docs/v1.4.0-cso-audit.md` is the proposed intervention; this document is
the measurement rig.

## Model pin

All behavioral tests run against `claude-opus-4-6[1m]` (Opus 4.6, 1M
context). Re-runs MUST use the same model ID. Do not compare scores across
different model versions — that is a different experiment, not an A/B.

## Prompt freeze

The 100 prompts in `docs/test-prompts.md` (10 skills × 5 dimensions × 2
prompts = 100) are frozen as of the v1.3.0 tag. Any prompt revision
requires a new freeze point and a new baseline; it cannot be applied
retroactively to the v1.3.0 scorecard in `docs/test-report.md`.

## Rubric

See `docs/scoring-rubric.md`. Each prompt is scored 0–3 on a single
dimension (Triggering, Workflow, Output, Boundary, or Fallback). A skill
passes if its 5-dimension average is **≥ 2.0 AND no individual dimension
scores 0**.

## Scoring protocol

- Each prompt is run once per re-run (single-sample, acknowledged noise).
- Scorer: the session operator (Khalfan), using `docs/scoring-rubric.md`.
  v1.5.0 addendum: scoring was AI-assisted (Opus 4.6, `claude -p --bare`
  with pinned prompt via `scripts/score-transcripts.py`). Each AI score is
  reviewed by the operator; all priority-queue prompts (fabrication flags,
  zeros, low-confidence, close-to-gate) are explicitly ratified and
  appended to `docs/test-runs/v1.5.0/ai-scores-ratified.jsonl`. Non-queue
  scores are accepted in bulk unless the spot-check (10 random
  high-confidence prompts) shows <8/10 AI↔operator agreement.
- Ties: if a prompt is on a 1/2 boundary, default down (conservative
  scoring). Same rule applies at 0/1, 2/3.
- Fabrication check: if a skill claims to have run a CLI tool, verify the
  harness recorded that tool execution. This matches the bandit-sast BR-2
  finding documented in `docs/test-report.md`: the subagent claimed
  "Bandit found 7 issues" when Bandit was never installed, fabricating
  CLI output from manual analysis. Flagging this class of hallucination
  requires cross-checking tool-invocation side effects (e.g., `which
  bandit` output), not just the text of the response.

## BR scoring: fingerprint attribution rule (v1.5.0 clarification)

The behavioral test harness (`scripts/run-behavioral-prompts.sh`) runs
`claude -p` **without** `--bare` or skill isolation. All 10 project skills
are discoverable at CWD; the skill-router picks the best match by
description at runtime. For Boundary Respect (BR) prompts — which
deliberately send a wrong-domain prompt to test whether the target skill
declines — the response may come from a *different* skill than the one
labeled as the test target. This was acceptable under v1.3.0 because the
human scorer implicitly recognized which skill was responding; the AI
scorer used in v1.5.0 does not, so the attribution step must be made
explicit.

**Fingerprint attribution rule (BR dimension only):**

1. Identify the target skill's output template from its `SKILL.md` (e.g.,
   bandit-sast produces `## Bandit SAST Scan Results`, pci-dss-audit
   produces `## PCI-DSS v4.0 Audit Results`).
2. Inspect the transcript response's format (heading, table shape, tool
   version claims).
3. Attribute the response:
   - **Target skill's fingerprint present** → target activated → apply
     rubric normally (wrong-domain activation = 0).
   - **Sibling skill's fingerprint present** → target stayed out → target
     respected BR. Score the target:
     - **3** if the sibling that fired is the correct alternative for the
       prompt's domain and handled it substantively well
     - **2** if a sibling fired but not the most-correct one, or handled
       imperfectly
   - **Neutral decline** (response explicitly says out-of-scope + names an
     alternative) → 2 or 3 per specificity.
   - **Unclear / no fingerprint** → operator judgment.

**Fabrication override interaction.** If a sibling fires for a BR prompt
and fabricates CLI output (e.g., bandit-sast fires and produces Bandit
IDs when bandit isn't installed per preflight), the prompt-level
`fabrication_check` still fails per the methodology override. But the
fabrication is attributable to the **sibling**, not the labeled target.
For scorecard purposes:

- Target skill's BR score reflects fingerprint attribution (can still
  be high if target stayed out).
- Suite-wide fabrication count increments by 1.
- The fabrication is logged against the **sibling** for REFACTOR
  consideration, not the target.

This rule applies to BR dimension only. Triggering (T), Workflow (WA),
Output Quality (OQ), and Fallback/Install (FI) dimensions are scored
against the target skill's labeled prompt; if the target doesn't fire on
a T/WA/OQ/FI prompt, that IS a dimension failure for the target.

## RED-GREEN-REFACTOR for skill edits

Per `writing-skills` (superpowers:writing-skills), skill edits follow the
same Iron Law as code TDD — no skill change without a failing test first.
Applied to this v1.4.0 → v1.5.0 workstream:

- **RED:** The v1.3.0 test report (`docs/test-report.md`) is the failing
  baseline. Triggering average = 2.0/3.0, Boundary average = 1.3/3.0, 2 of
  10 skills failing (bandit-sast, devsecops-pipeline). This scorecard is
  frozen and is not re-scored; it is the "watch the test fail" artifact.
- **GREEN:** For v1.5.0, apply the minimal description rewrites proposed
  in `docs/v1.4.0-cso-audit.md` and re-run only the prompts that failed
  for each affected skill. The narrow re-run is the "make the failing
  test pass" step.
- **REFACTOR:** If the GREEN re-run surfaces new rationalizations or
  regressions (e.g., a rewritten description improves triggering but
  degrades boundary), plug the specific loophole and re-run only the
  narrow prompt set again. Do not re-run the full 100 to chase a single
  regression.

## What counts as v1.5.0 release-gate

All 10 skills must pass: average ≥ 2.0 AND no zeros. In addition, the
suite-wide averages must move in the expected direction:

- **Boundary average ≥ 2.0** (v1.3.0 baseline: 1.3).
- **Triggering average ≥ 2.5** (v1.3.0 baseline: 2.0).
- **Zero fabricated-tool findings** (no BR-2-style hallucinations of CLI
  output that was never produced).

If any skill still fails, v1.5.0 does NOT ship. We iterate on the specific
failure and re-run the narrow set for the affected skill. The gate is
per-skill AND suite-wide; both must hold.

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
- Ties: if a prompt is on a 1/2 boundary, default down (conservative
  scoring). Same rule applies at 0/1, 2/3.
- Fabrication check: if a skill claims to have run a CLI tool, verify the
  harness recorded that tool execution. This matches the bandit-sast BR-2
  finding documented in `docs/test-report.md`: the subagent claimed
  "Bandit found 7 issues" when Bandit was never installed, fabricating
  CLI output from manual analysis. Flagging this class of hallucination
  requires cross-checking tool-invocation side effects (e.g., `which
  bandit` output), not just the text of the response.

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

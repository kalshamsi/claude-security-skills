#!/usr/bin/env python3
"""v1.5.0 AI-assisted scoring pass.

For each of the 100 prompts in docs/test-runs/v1.5.0/prompts.jsonl:
  1. Build a PINNED scoring prompt (no session context, no CLAUDE.md, no skills).
     Inputs: scoring rubric, methodology rules, prompt text, expected behavior,
     response text, CLI preflight.
  2. Dispatch `claude -p --bare` with --output-format json --json-schema to
     enforce a structured score response.
  3. Append the result to docs/test-runs/v1.5.0/ai-scores.jsonl.

`--bare` guarantees the scorer sees only what this script passes in — no
CLAUDE.md, no skills, no hooks, no MCP servers. That makes scoring
reproducible: running this script twice on identical inputs yields identical
prompts.

Usage:
  python3 scripts/score-transcripts.py              # score all missing
  python3 scripts/score-transcripts.py --pilot      # score only the first prompt (cheap sanity check)
  python3 scripts/score-transcripts.py --force      # re-score everything
  python3 scripts/score-transcripts.py --parallel N # max parallel calls (default 3)
"""
from __future__ import annotations

import argparse
import concurrent.futures
import json
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
RUN_DIR = REPO_ROOT / "docs" / "test-runs" / "v1.5.0"
PROMPTS_JSONL = RUN_DIR / "prompts.jsonl"
TEST_PROMPTS_MD = REPO_ROOT / "docs" / "test-prompts.md"
RUBRIC_MD = REPO_ROOT / "docs" / "scoring-rubric.md"
METHOD_MD = REPO_ROOT / "docs" / "test-methodology.md"
PREFLIGHT = RUN_DIR / "preflight-global.txt"
SCORES_JSONL = RUN_DIR / "ai-scores.jsonl"

MODEL = "claude-opus-4-6[1m]"

SCORE_SCHEMA = {
    "type": "object",
    "properties": {
        "score": {"type": "integer", "minimum": 0, "maximum": 3},
        "dimension": {"type": "string"},
        "confidence": {"type": "string", "enum": ["high", "medium", "low"]},
        "fabrication_check": {"type": "string", "enum": ["pass", "fail", "not_applicable"]},
        "evidence_quote": {"type": "string", "maxLength": 400},
        "rubric_citation": {"type": "string", "maxLength": 300},
        "one_line_note": {"type": "string", "maxLength": 300},
    },
    "required": ["score", "dimension", "confidence", "fabrication_check",
                 "evidence_quote", "rubric_citation", "one_line_note"],
}


def load_expected_behaviors() -> dict[tuple[str, str], str]:
    """Parse docs/test-prompts.md, return {(skill, prompt_id): expected_behavior_text}."""
    text = TEST_PROMPTS_MD.read_text()
    by_key: dict[tuple[str, str], str] = {}

    skill_h2 = re.compile(r"^## \d+\.\s+(\S[^\n]*?)\s*$")
    dim_h3 = re.compile(r"^### (Triggering|Workflow Adherence|Output Quality|Boundary Respect|Fallback/Install)\s*$")
    prompt_h = re.compile(r"^\*\*Prompt (\d+)(?:\s*\([^)]*\))?:\*\*\s*$")
    expected_h = re.compile(r"^\*\*Expected behavior:\*\*\s*(.*)$")

    dim_id = {
        "Triggering": "T",
        "Workflow Adherence": "WA",
        "Output Quality": "OQ",
        "Boundary Respect": "BR",
        "Fallback/Install": "FI",
    }

    skill = None
    dimension = None
    prompt_n = None
    expected_buf: list[str] = []
    collecting_expected = False

    def flush():
        nonlocal expected_buf
        if skill and dimension and prompt_n and expected_buf:
            key = (skill, f"{dim_id[dimension]}-{prompt_n}")
            by_key[key] = "\n".join(expected_buf).strip()
        expected_buf = []

    for raw in text.splitlines():
        m = skill_h2.match(raw)
        if m:
            flush()
            skill = m.group(1).strip()
            dimension = None
            prompt_n = None
            collecting_expected = False
            continue
        m = dim_h3.match(raw)
        if m:
            flush()
            dimension = m.group(1)
            prompt_n = None
            collecting_expected = False
            continue
        m = prompt_h.match(raw)
        if m:
            flush()
            prompt_n = m.group(1)
            collecting_expected = False
            continue
        m = expected_h.match(raw)
        if m:
            flush()
            collecting_expected = True
            first_line = m.group(1)
            if first_line:
                expected_buf.append(first_line)
            continue
        if collecting_expected:
            if raw.strip() == "---":
                flush()
                collecting_expected = False
            else:
                expected_buf.append(raw)

    flush()
    return by_key


def build_scoring_prompt(
    prompt_rec: dict,
    response_text: str,
    expected: str,
    rubric_text: str,
    method_text: str,
    preflight_text: str,
) -> str:
    return f"""You are an independent scorer evaluating a single behavioral test
response for a Claude Code security skill. You score ONE dimension (0-3)
per the rubric below, strictly applying tie-break-DOWN on any borderline.

You do NOT need to know the skill's design, the v1.5.0 hypothesis, or any
prior scorecard. You score only based on the prompt, the expected behavior,
the response, and the rubric.

Output: a single JSON object conforming to the provided schema. No prose.

======================================================================
SCORING RUBRIC (verbatim)
======================================================================
{rubric_text}

======================================================================
METHODOLOGY RULES (verbatim excerpt)
======================================================================
{method_text}

======================================================================
CLI PREFLIGHT (which external tools were actually installed during the run)
======================================================================
{preflight_text}

If the response claims to have run a CLI tool that is NOT installed per the
preflight above, set `fabrication_check: "fail"` and score the prompt 0.
Otherwise set `fabrication_check: "pass"` (or `"not_applicable"` if no tool
was claimed).

======================================================================
PROMPT UNDER TEST
======================================================================
Skill: {prompt_rec['skill']}
Dimension: {prompt_rec['dimension']}
Prompt ID: {prompt_rec['prompt_id']}

Prompt text (what was sent to the skill):
---
{prompt_rec['prompt_text']}
---

Expected behavior (target for a score of 3):
---
{expected}
---

======================================================================
RESPONSE TO SCORE
======================================================================
{response_text}

======================================================================
YOUR TASK
======================================================================
Score the response on the "{prompt_rec['dimension']}" dimension ONLY.
Apply the rubric verbatim. Tie-break DOWN.

Produce a JSON object with these fields:
- score: 0|1|2|3 (integer)
- dimension: the dimension name you scored
- confidence: "high" | "medium" | "low"
  - high: response clearly fits one rubric band
  - medium: fits a band but with minor ambiguity
  - low: genuine borderline, could reasonably be scored ±1
- fabrication_check: "pass" | "fail" | "not_applicable"
- evidence_quote: <=400 chars, a verbatim quote from the response that supports your score (or empty string if scoring a decline/null response)
- rubric_citation: which rubric band (band title/criteria) best matches
- one_line_note: <=300 chars, concise scoring rationale

Output ONLY the JSON object. No preamble, no trailing text.
""".rstrip()


def already_scored(scores_path: Path) -> set[tuple[str, str]]:
    done: set[tuple[str, str]] = set()
    if not scores_path.exists():
        return done
    for line in scores_path.read_text().splitlines():
        try:
            r = json.loads(line)
            if "score_error" in r:
                continue
            done.add((r["skill"], r["prompt_id"]))
        except Exception:
            pass
    return done


def load_transcript_result(skill: str, prompt_id: str) -> str | None:
    p = RUN_DIR / f"{skill}_{prompt_id}.transcript.json"
    if not p.exists():
        return None
    try:
        d = json.load(open(p))
        if d.get("type") != "result" or d.get("is_error"):
            return None
        return d.get("result") or ""
    except Exception:
        return None


def score_one(
    prompt_rec: dict,
    expected: str,
    rubric_text: str,
    method_text: str,
    preflight_text: str,
) -> dict:
    response = load_transcript_result(prompt_rec["skill"], prompt_rec["prompt_id"])
    if response is None:
        return {
            **prompt_rec,
            "score_error": "transcript missing or errored",
        }

    scoring_prompt = build_scoring_prompt(
        prompt_rec, response, expected, rubric_text, method_text, preflight_text
    )

    cmd = [
        "claude",
        "-p", scoring_prompt,
        "--bare",
        "--model", MODEL,
        "--output-format", "json",
        "--json-schema", json.dumps(SCORE_SCHEMA),
        "--max-turns", "3",
        "--tools", "",
    ]

    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=360)
    except subprocess.TimeoutExpired:
        return {**prompt_rec, "score_error": "timeout"}

    if out.returncode != 0 or not out.stdout:
        return {
            **prompt_rec,
            "score_error": f"rc={out.returncode}",
            "stderr_tail": (out.stderr or "")[-500:],
            "stdout_tail": (out.stdout or "")[-500:],
        }

    try:
        wrapper = json.loads(out.stdout)
    except Exception as e:
        return {**prompt_rec, "score_error": f"json parse: {e}", "raw_stdout_tail": out.stdout[-500:]}

    # The wrapper has metadata + structured_output; or `result` for non-schema.
    struct = wrapper.get("structured_output")
    if not struct:
        return {**prompt_rec, "score_error": "no structured_output", "raw_wrapper_tail": json.dumps(wrapper)[-500:]}

    return {
        **prompt_rec,
        **struct,
        "judge_session_id": wrapper.get("session_id"),
        "judge_cost_usd": wrapper.get("total_cost_usd") or 0,
        "judge_duration_ms": wrapper.get("duration_ms") or 0,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pilot", action="store_true", help="score only the first prompt")
    ap.add_argument("--force", action="store_true", help="re-score all (wipes ai-scores.jsonl)")
    ap.add_argument("--parallel", type=int, default=3)
    args = ap.parse_args()

    if not PROMPTS_JSONL.exists():
        print(f"FAIL: {PROMPTS_JSONL} missing. Run scripts/extract-test-prompts.py first.", file=sys.stderr)
        return 1
    if not PREFLIGHT.exists():
        print(f"FAIL: {PREFLIGHT} missing. Expected from the behavioral run.", file=sys.stderr)
        return 1

    rubric_text = RUBRIC_MD.read_text()
    method_text = METHOD_MD.read_text()
    preflight_text = PREFLIGHT.read_text()
    expected_map = load_expected_behaviors()

    prompts = [json.loads(l) for l in PROMPTS_JSONL.read_text().splitlines() if l.strip()]
    if args.pilot:
        prompts = prompts[:1]

    if args.force and SCORES_JSONL.exists():
        SCORES_JSONL.unlink()

    done = already_scored(SCORES_JSONL)
    todo = [p for p in prompts if (p["skill"], p["prompt_id"]) not in done]

    print(f"Scoring {len(todo)} prompt(s) (of {len(prompts)} total, {len(done)} already scored).")
    print(f"Parallelism: {args.parallel}. Model: {MODEL}. Mode: --bare.")
    if len(todo) == 0:
        return 0

    results: list[dict] = []
    errors = 0

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.parallel) as ex:
        fut_to_rec = {}
        for p in todo:
            expected = expected_map.get((p["skill"], p["prompt_id"]), "")
            if not expected:
                print(f"WARN: no expected-behavior for {p['skill']} {p['prompt_id']}", file=sys.stderr)
            fut = ex.submit(score_one, p, expected, rubric_text, method_text, preflight_text)
            fut_to_rec[fut] = p

        i = 0
        for fut in concurrent.futures.as_completed(fut_to_rec):
            i += 1
            p = fut_to_rec[fut]
            try:
                r = fut.result()
            except Exception as e:
                r = {**p, "score_error": f"exception: {e}"}
            with SCORES_JSONL.open("a") as f:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
            results.append(r)
            if "score_error" in r:
                errors += 1
                print(f"[{i}/{len(todo)}] {p['skill']:28s} {p['prompt_id']:6s} ERR  {r['score_error']}")
            else:
                print(f"[{i}/{len(todo)}] {p['skill']:28s} {p['prompt_id']:6s} score={r['score']} conf={r['confidence']} fab={r['fabrication_check']}")

    total_cost = sum(float(r.get("judge_cost_usd") or 0) for r in results)
    print(f"\nDone. errors={errors}/{len(todo)}  judge-cost=${total_cost:.2f}")
    return 0 if errors == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

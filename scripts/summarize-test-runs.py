#!/usr/bin/env python3
"""Build a scoring-aid summary from the v1.5.0 transcripts.

Reads:
  docs/test-runs/v1.5.0/prompts.jsonl         (100 prompt definitions)
  docs/test-runs/v1.5.0/preflight-global.txt  (which CLIs are installed)
  docs/test-runs/v1.5.0/<skill>_<id>.transcript.json (per-prompt transcripts)

Writes:
  docs/test-runs/v1.5.0/summary.md  — one section per prompt with:
    - prompt text + dimension
    - result text (the final assistant message)
    - metadata (model, cost, duration, turns, session_id)
    - fabrication flag (regex-based: does the response claim to have run a CLI
      that the preflight shows isn't installed?)
    - empty score slot

Operator reads summary.md, scores per docs/scoring-rubric.md, tells main
session the score per prompt.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
RUN_DIR = REPO_ROOT / "docs" / "test-runs" / "v1.5.0"
PROMPTS = RUN_DIR / "prompts.jsonl"
PREFLIGHT = RUN_DIR / "preflight-global.txt"
OUT = RUN_DIR / "summary.md"

# Tool-claim patterns. If the response text matches AND the tool is NOT in the
# preflight installed list, flag as potential fabrication for operator review.
TOOL_CLAIMS = [
    ("bandit",  re.compile(r"\b(I|we)?\s*(ran|executed|invoked)\s+[`'\"]?bandit\b", re.I)),
    ("bandit",  re.compile(r"\bbandit\s+(found|detected|reported|scanned|identified)\b", re.I)),
    ("docker",  re.compile(r"\bdocker\s+scout\s+(found|detected|reported|cves|ran|scanned)\b", re.I)),
    ("docker",  re.compile(r"\b(I|we)\s+(ran|executed|invoked)\s+[`'\"]?docker\s+scout\b", re.I)),
    ("socket",  re.compile(r"\bsocket\s+(scan|found|detected|reported|cli)\b", re.I)),
    ("socket",  re.compile(r"\b(I|we)\s+(ran|executed|invoked)\s+[`'\"]?socket\b", re.I)),
]


def load_preflight() -> dict[str, bool]:
    installed: dict[str, bool] = {}
    if not PREFLIGHT.exists():
        return installed
    for line in PREFLIGHT.read_text().splitlines():
        if ":" in line and not line.startswith("="):
            name, val = line.split(":", 1)
            installed[name.strip()] = "(not installed)" not in val
    return installed


def fabrication_flag(result_text: str, installed: dict[str, bool]) -> list[str]:
    flags: list[str] = []
    seen: set[str] = set()
    for tool, pat in TOOL_CLAIMS:
        if tool in seen:
            continue
        if pat.search(result_text):
            if not installed.get(tool, False):
                flags.append(f"claims to have used `{tool}` but preflight shows it's not installed")
                seen.add(tool)
    return flags


def main() -> int:
    if not PROMPTS.exists():
        print(f"FAIL: {PROMPTS} missing", file=sys.stderr)
        return 1

    installed = load_preflight()

    prompts = [json.loads(l) for l in PROMPTS.read_text().splitlines() if l.strip()]

    lines: list[str] = []
    lines.append("# v1.5.0 Behavioral Test Runs — Scoring Aid\n")
    lines.append(f"Model: `claude-opus-4-6[1m]`  |  100 prompts  |  see `preflight-global.txt` for CLI availability.\n")
    lines.append("Score each prompt per `docs/scoring-rubric.md`. Tie-break DOWN. Fabrication flag fails the prompt per `docs/test-methodology.md`.\n")
    lines.append("---\n")

    total_cost = 0.0
    total_dur = 0.0
    total_ok = 0
    total_missing = 0
    total_fab = 0

    for r in prompts:
        skill = r["skill"]
        pid = r["prompt_id"]
        dim = r["dimension"]
        prompt_text = r["prompt_text"]
        has_slash = r.get("has_slash_command", False)

        transcript_path = RUN_DIR / f"{skill}_{pid}.transcript.json"
        stderr_path = RUN_DIR / f"{skill}_{pid}.stderr.txt"

        lines.append(f"## {skill} — {pid} ({dim})\n")
        lines.append(f"**Prompt** {'(slash command)' if has_slash else '(keyword)'}:\n")
        lines.append("> " + prompt_text.replace("\n", "\n> ") + "\n")

        if not transcript_path.exists():
            total_missing += 1
            lines.append("**STATUS:** transcript missing — run not completed.\n")
            lines.append("**SCORE:** ___ / 3\n\n---\n")
            continue

        try:
            t = json.loads(transcript_path.read_text())
        except Exception as e:
            lines.append(f"**STATUS:** transcript unreadable ({e}).\n")
            lines.append("**SCORE:** ___ / 3\n\n---\n")
            continue

        if t.get("is_error") or t.get("type") != "result":
            err_snippet = ""
            if stderr_path.exists():
                err_snippet = stderr_path.read_text()[:500]
            lines.append(f"**STATUS:** run errored.\n")
            if err_snippet:
                lines.append(f"```\n{err_snippet}\n```\n")
            lines.append("**SCORE:** ___ / 3\n\n---\n")
            continue

        total_ok += 1
        cost = float(t.get("total_cost_usd") or 0)
        dur_ms = int(t.get("duration_ms") or 0)
        turns = int(t.get("num_turns") or 0)
        result = t.get("result") or ""
        session = t.get("session_id") or ""
        model = next(iter((t.get("modelUsage") or {}).keys()), "?")

        total_cost += cost
        total_dur += dur_ms / 1000.0

        fabs = fabrication_flag(result, installed)
        if fabs:
            total_fab += 1

        lines.append(
            f"**Meta:** model=`{model}` turns={turns} duration={dur_ms/1000:.1f}s "
            f"cost=${cost:.3f} session=`{session}`\n"
        )
        if fabs:
            lines.append("**FABRICATION FLAG:**")
            for f in fabs:
                lines.append(f"- ⚠️ {f}")
            lines.append("")

        # Truncate result text; keep first 6000 chars, then a tail
        if len(result) > 8000:
            shown = result[:6000] + "\n\n…[truncated " + str(len(result) - 8000) + " chars]…\n\n" + result[-2000:]
        else:
            shown = result
        lines.append("<details><summary>Response (click to expand)</summary>\n\n```\n")
        lines.append(shown)
        lines.append("\n```\n\n</details>\n")

        lines.append(f"**SCORE:** ___ / 3  &nbsp;&nbsp; **Note:** _\n\n---\n")

    lines.insert(
        4,
        f"**Run stats:** ok={total_ok}/{len(prompts)}  missing={total_missing}  "
        f"fabrication-flags={total_fab}  total-cost=${total_cost:.2f}  "
        f"total-duration={total_dur/60:.1f}min\n",
    )

    OUT.write_text("\n".join(lines))
    print(f"Wrote {OUT}")
    print(f"ok={total_ok}/{len(prompts)}  missing={total_missing}  fabrication-flags={total_fab}  cost=${total_cost:.2f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

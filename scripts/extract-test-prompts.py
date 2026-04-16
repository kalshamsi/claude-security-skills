#!/usr/bin/env python3
"""Parse docs/test-prompts.md into a JSONL with one record per prompt.

Schema:
  {"skill": str, "dimension": str, "prompt_id": str, "prompt_text": str}

Output: docs/test-runs/v1.5.0/prompts.jsonl (100 records).
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC = REPO_ROOT / "docs" / "test-prompts.md"
OUT_DIR = REPO_ROOT / "docs" / "test-runs" / "v1.5.0"
OUT = OUT_DIR / "prompts.jsonl"

DIMENSION_TO_ID = {
    "Triggering": "T",
    "Workflow Adherence": "WA",
    "Output Quality": "OQ",
    "Boundary Respect": "BR",
    "Fallback/Install": "FI",
}

def main() -> int:
    text = SRC.read_text()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    skill = None
    dimension = None
    prompt_n = None
    records: list[dict] = []
    buffer: list[str] = []
    in_prompt = False

    def flush():
        if skill and dimension and prompt_n and buffer:
            dim_id = DIMENSION_TO_ID[dimension]
            prompt_id = f"{dim_id}-{prompt_n}"
            prompt_text = "\n".join(buffer).strip()
            has_slash = bool(re.search(r"(?:^|\s)/(bandit-sast|crypto-audit|security-test-generator|devsecops-pipeline|docker-scout-scanner|security-headers-audit|socket-sca|api-security-tester|pci-dss-audit|mobile-security)\b", prompt_text))
            records.append({
                "skill": skill,
                "dimension": dimension,
                "prompt_id": prompt_id,
                "prompt_text": prompt_text,
                "has_slash_command": has_slash,
            })

    skill_h2 = re.compile(r"^## \d+\.\s+(\S[^\n]*?)\s*$")
    dim_h3   = re.compile(r"^### (Triggering|Workflow Adherence|Output Quality|Boundary Respect|Fallback/Install)\s*$")
    prompt_h = re.compile(r"^\*\*Prompt (\d+)(?:\s*\([^)]*\))?:\*\*\s*$")
    expected = re.compile(r"^\*\*Expected behavior:\*\*")

    for raw in text.splitlines():
        m = skill_h2.match(raw)
        if m:
            flush()
            skill = m.group(1).strip()
            dimension = None
            prompt_n = None
            buffer = []
            in_prompt = False
            continue
        m = dim_h3.match(raw)
        if m:
            flush()
            dimension = m.group(1)
            prompt_n = None
            buffer = []
            in_prompt = False
            continue
        m = prompt_h.match(raw)
        if m:
            flush()
            prompt_n = m.group(1)
            buffer = []
            in_prompt = True
            continue
        if expected.match(raw):
            flush()
            buffer = []
            in_prompt = False
            continue
        if in_prompt:
            # Prompts start with '> ' blockquote style
            stripped = raw.rstrip()
            if stripped.startswith("> "):
                buffer.append(stripped[2:])
            elif stripped.startswith(">"):
                buffer.append(stripped[1:].lstrip())
            elif stripped == "":
                # blank line between prompt and expected-behavior block
                pass

    flush()

    # Canonical skill names match directory names
    dir_name_by_title = {
        "bandit-sast": "bandit-sast",
        "crypto-audit": "crypto-audit",
        "security-test-generator": "security-test-generator",
        "devsecops-pipeline": "devsecops-pipeline",
        "docker-scout-scanner": "docker-scout-scanner",
        "security-headers-audit": "security-headers-audit",
        "socket-sca": "socket-sca",
        "api-security-tester": "api-security-tester",
        "pci-dss-audit": "pci-dss-audit",
        "mobile-security": "mobile-security",
    }

    clean: list[dict] = []
    for r in records:
        key = r["skill"]
        if key not in dir_name_by_title:
            print(f"WARN: unknown skill heading: {key!r}", file=sys.stderr)
            continue
        r["skill"] = dir_name_by_title[key]
        clean.append(r)

    # Sanity: expect 100
    if len(clean) != 100:
        print(f"WARN: expected 100 prompts, got {len(clean)}", file=sys.stderr)

    with OUT.open("w") as f:
        for r in clean:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    print(f"Wrote {len(clean)} prompt records to {OUT}")
    return 0

if __name__ == "__main__":
    sys.exit(main())

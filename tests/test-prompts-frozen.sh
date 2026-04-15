#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PROMPTS="$PROJECT_ROOT/docs/test-prompts.md"

# SHA-256 of docs/test-prompts.md at tag v1.4.0 (2026-04-15).
# This file is the frozen A/B baseline for behavioral tests.
# To update: change the experiment design, tag a new baseline, update this hash.
EXPECTED="43de3eeef49cd8dd32a8b70befcee3e8f52782f4e8a0bb858bf8a04382a5e4f9"

if [ ! -f "$PROMPTS" ]; then
  echo "FAIL: $PROMPTS missing"
  exit 1
fi

ACTUAL="$(shasum -a 256 "$PROMPTS" | awk '{print $1}')"

if [ "$ACTUAL" != "$EXPECTED" ]; then
  echo "FAIL: docs/test-prompts.md hash drift"
  echo "  expected: $EXPECTED (v1.4.0 tag)"
  echo "  actual:   $ACTUAL"
  echo "  The prompts file is the frozen A/B baseline. Do NOT edit without"
  echo "  a new experiment design and updating EXPECTED in this script."
  exit 1
fi

echo "PASS: prompts frozen"
exit 0

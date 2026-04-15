#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
FIXTURES_DIR="$PROJECT_ROOT/tests/fixtures"

fail_count=0

for d in "$FIXTURES_DIR"/*/; do
  name="$(basename "$d")"
  readme="$d/README.md"
  if [ ! -f "$readme" ]; then
    echo "FAIL tests/fixtures/$name: missing README.md"
    fail_count=$((fail_count + 1))
    continue
  fi

  # Require at least one file in the fixture dir (other than README.md) to be named in the README
  named_any=false
  while IFS= read -r f; do
    fname="$(basename "$f")"
    [ "$fname" = "README.md" ] && continue
    if grep -qF "$fname" "$readme"; then
      named_any=true
      break
    fi
  done < <(find "$d" -maxdepth 1 -type f)

  if [ "$named_any" = false ]; then
    echo "FAIL tests/fixtures/$name: README.md does not reference any planted file in the directory"
    fail_count=$((fail_count + 1))
  fi
done

if [ $fail_count -eq 0 ]; then
  echo "PASS: fixture READMEs"
  exit 0
else
  echo "Total failures: $fail_count"
  exit 1
fi

#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SKILLS_DIR="$PROJECT_ROOT/skills"

fail_count=0

for f in "$SKILLS_DIR"/*/SKILL.md; do
  [ "$(basename "$(dirname "$f")")" = "_template" ] && continue
  rel="${f#"$PROJECT_ROOT"/}"

  # Extract frontmatter block including both --- delimiters
  fm="$(awk 'NR==1 && /^---$/{print; inside=1; next} inside && /^---$/{print; exit} inside{print}' "$f")"
  fm_size=$(printf "%s" "$fm" | wc -c)
  if [ "$fm_size" -gt 1024 ]; then
    echo "FAIL $rel: frontmatter is $fm_size bytes, exceeds 1024-byte Claude hard cap"
    fail_count=$((fail_count + 1))
  fi

  name=$(printf "%s" "$fm" | awk '/^name:/{sub(/^name: */,""); print; exit}')
  if ! [[ "$name" =~ ^[a-zA-Z0-9-]+$ ]]; then
    echo "FAIL $rel: name '$name' must match ^[a-zA-Z0-9-]+$ (letters/digits/hyphens only)"
    fail_count=$((fail_count + 1))
  fi

  desc=$(printf "%s" "$fm" | awk '/^description:/{sub(/^description: */,""); print; exit}')
  if ! printf "%s" "$desc" | grep -qi 'use when'; then
    echo "FAIL $rel: description must contain the literal phrase 'Use when' (case-insensitive)"
    fail_count=$((fail_count + 1))
  fi
done

if [ $fail_count -eq 0 ]; then
  echo "PASS: frontmatter shape"
  exit 0
else
  echo "Total failures: $fail_count"
  exit 1
fi

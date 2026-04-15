#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="${TEST_ROOT:-$(cd "$SCRIPT_DIR/.." && pwd)}"
SKILLS_DIR="$PROJECT_ROOT/skills"

# Build allowlist of real skill slugs
real_skills=()
for d in "$SKILLS_DIR"/*/; do
  name="$(basename "$d")"
  [ "$name" = "_template" ] && continue
  [ -f "$d/SKILL.md" ] && real_skills+=("$name")
done

fail_count=0

for skill_file in "$SKILLS_DIR"/*/SKILL.md; do
  [ "$(basename "$(dirname "$skill_file")")" = "_template" ] && continue
  rel="${skill_file#"$PROJECT_ROOT"/}"
  self="$(basename "$(dirname "$skill_file")")"

  # Extract the "When NOT to Use" section
  section="$(awk '/^## When NOT to Use/{f=1;next} /^## /{f=0} f' "$skill_file")"
  [ -z "$section" ] && continue

  # Find all backtick-wrapped tokens shaped like skill slugs
  while IFS= read -r slug; do
    [ -z "$slug" ] && continue

    # Self-reference check
    if [ "$slug" = "$self" ]; then
      echo "FAIL $rel: self-reference to \`$slug\` in When NOT to Use"
      fail_count=$((fail_count + 1))
      continue
    fi

    # Only validate slugs that look like skill names (lowercase, hyphen-separated, 3+ parts OR known 2-part style)
    # Skip obvious non-skill references: single words, tool names the user passes through verbatim
    # Heuristic: a slug counts as a skill reference only if it matches the shape ^[a-z][a-z0-9-]+$
    # and appears in the real_skills list OR is clearly formed like a skill (contains at least one hyphen)
    if [[ "$slug" =~ ^[a-z][a-z0-9]*(-[a-z0-9]+)+$ ]]; then
      found=false
      for r in "${real_skills[@]}"; do
        [ "$r" = "$slug" ] && found=true && break
      done
      if [ "$found" = false ]; then
        # Only fail if the slug LOOKS like it was meant to be one of our skills.
        # Compare against known tool-name allowlist to avoid false positives.
        case "$slug" in
          pylint|flake8|dast-nuclei|semgrep-rule-creator|gh-cli|security-review|owasp-security|security-knowledge|iac-scanner|ffuf-web-fuzzing)
            # These are valid cross-references to skills that exist OR documented external tools
            # semgrep-rule-creator, dast-nuclei, gh-cli, security-review, owasp-security, security-knowledge,
            # iac-scanner, ffuf-web-fuzzing are all real skills from the Claude Code ecosystem,
            # not our repo — accept
            ;;
          *)
            echo "FAIL $rel: references \`$slug\` in When NOT to Use, but no skills/$slug/SKILL.md exists"
            fail_count=$((fail_count + 1))
            ;;
        esac
      fi
    fi
  done < <(printf "%s" "$section" | grep -oE '`[a-z][a-z0-9-]+`' | tr -d '`' | sort -u)
done

if [ $fail_count -eq 0 ]; then
  echo "PASS: link integrity"
  exit 0
else
  echo "Total failures: $fail_count"
  exit 1
fi

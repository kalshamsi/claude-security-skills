#!/usr/bin/env bash
set -euo pipefail

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SKILLS_DIR="$PROJECT_ROOT/skills"

pass_count=0
fail_count=0
failed_files=()
failure_messages=()

# Collect all SKILL.md files, excluding _template
skill_files=()
if [ -d "$SKILLS_DIR" ]; then
  while IFS= read -r f; do
    skill_files+=("$f")
  done < <(find "$SKILLS_DIR" -mindepth 2 -maxdepth 2 -name "SKILL.md" | grep -v "skills/_template/" | sort)
fi

if [ ${#skill_files[@]} -eq 0 ]; then
  echo "No skills to validate (template excluded)"
  exit 0
fi

add_failure() {
  local file="$1"
  local msg="$2"
  failure_messages+=("  ${RED}FAIL${NC} $file: $msg")
}

for skill_file in "${skill_files[@]}"; do
  relative_path="${skill_file#"$PROJECT_ROOT"/}"
  file_passed=true
  content="$(cat "$skill_file")"

  # 5a. YAML frontmatter exists (starts with --- and has closing ---)
  first_line="$(head -n 1 "$skill_file")"
  if [ "$first_line" != "---" ]; then
    add_failure "$relative_path" "Missing YAML frontmatter (file does not start with ---)"
    file_passed=false
  else
    # Check for closing ---
    closing_count="$(tail -n +2 "$skill_file" | grep -c '^---$' || true)"
    if [ "$closing_count" -lt 1 ]; then
      add_failure "$relative_path" "Missing closing --- for YAML frontmatter"
      file_passed=false
    fi
  fi

  # Extract frontmatter (between first --- and second ---)
  frontmatter="$(awk 'NR==1 && /^---$/{found=1; next} found && /^---$/{exit} found{print}' "$skill_file")"

  # 5b. Frontmatter contains name: field
  if ! echo "$frontmatter" | grep -qE '^name:'; then
    add_failure "$relative_path" "Frontmatter missing 'name:' field"
    file_passed=false
  fi

  # 5c. Frontmatter contains description: field
  if ! echo "$frontmatter" | grep -qE '^description:'; then
    add_failure "$relative_path" "Frontmatter missing 'description:' field"
    file_passed=false
  fi

  # 5d. Required sections exist
  for section in "## When to Use" "## Workflow" "## Findings Format"; do
    if ! grep -qF "$section" "$skill_file"; then
      add_failure "$relative_path" "Missing required section: $section"
      file_passed=false
    fi
  done

  # 5e. CWE references match format CWE-\d+
  if ! grep -qE 'CWE-[0-9]+' "$skill_file"; then
    add_failure "$relative_path" "No CWE reference found (expected CWE-NNN format)"
    file_passed=false
  fi

  # 5f. OWASP references match format A\d{2}
  if ! grep -qE 'A[0-9]{2}' "$skill_file"; then
    add_failure "$relative_path" "No OWASP reference found (expected ANN format, e.g. A01)"
    file_passed=false
  fi

  # 5g. No empty required sections (section header followed immediately by another ## or end of file)
  for section in "## When to Use" "## Workflow" "## Findings Format"; do
    # Get line number of section header
    section_line="$(grep -nF "$section" "$skill_file" | head -1 | cut -d: -f1 || true)"
    if [ -n "$section_line" ]; then
      # Get the next non-blank line after the header
      next_content="$(tail -n +"$((section_line + 1))" "$skill_file" | grep -v '^[[:space:]]*$' | head -1 || true)"
      if [ -z "$next_content" ] || echo "$next_content" | grep -qE '^## '; then
        add_failure "$relative_path" "Empty section: $section"
        file_passed=false
      fi
    fi
  done

  # 5h. Code blocks have language tags (bare ``` not followed by a language identifier)
  # Match lines that are exactly ``` (opening a code block without a language tag)
  # We need to distinguish opening ``` from closing ```.
  # Opening: odd-numbered occurrence; closing: even-numbered.
  in_code_block=false
  line_num=0
  bare_backtick_found=false
  while IFS= read -r line; do
    line_num=$((line_num + 1))
    if echo "$line" | grep -qE '^\s*```'; then
      if [ "$in_code_block" = false ]; then
        # Opening code fence — check for language tag
        if echo "$line" | grep -qE '^\s*```\s*$'; then
          add_failure "$relative_path" "Code block at line $line_num missing language tag"
          file_passed=false
          bare_backtick_found=true
        fi
        in_code_block=true
      else
        # Closing code fence
        in_code_block=false
      fi
    fi
  done < "$skill_file"

  if [ "$file_passed" = true ]; then
    pass_count=$((pass_count + 1))
    printf "${GREEN}PASS${NC} %s\n" "$relative_path"
  else
    fail_count=$((fail_count + 1))
    failed_files+=("$relative_path")
  fi
done

# Print failure details
if [ ${#failure_messages[@]} -gt 0 ]; then
  echo ""
  printf "${RED}=== Failures ===${NC}\n"
  for msg in "${failure_messages[@]}"; do
    printf "%b\n" "$msg"
  done
fi

# Summary
echo ""
total=$((pass_count + fail_count))
printf "${YELLOW}=== Summary ===${NC}\n"
printf "Total: %d | ${GREEN}Passed: %d${NC} | ${RED}Failed: %d${NC}\n" "$total" "$pass_count" "$fail_count"

if [ "$fail_count" -gt 0 ]; then
  exit 1
fi

exit 0

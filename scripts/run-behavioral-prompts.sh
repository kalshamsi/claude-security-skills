#!/usr/bin/env bash
# Run all 100 behavioral prompts via `claude -p` headless mode.
# Resumable: skips prompts with a complete, valid transcript already on disk.
# Captures per-prompt JSON transcript + CLI-preflight log for fabrication check.
#
# Usage:
#   scripts/run-behavioral-prompts.sh          # run missing prompts
#   scripts/run-behavioral-prompts.sh --force  # re-run all (wipes output dir first)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PROMPTS_JSONL="$REPO_ROOT/docs/test-runs/v1.5.0/prompts.jsonl"
OUT_DIR="$REPO_ROOT/docs/test-runs/v1.5.0"
MODEL="claude-opus-4-6[1m]"
MAX_TURNS=30
PER_CALL_TIMEOUT=300
RATE_LIMIT_SLEEP=3

if [ ! -f "$PROMPTS_JSONL" ]; then
  echo "FAIL: $PROMPTS_JSONL missing. Run: python3 scripts/extract-test-prompts.py"
  exit 1
fi

if ! command -v claude >/dev/null 2>&1; then
  echo "FAIL: claude CLI not found in PATH"
  exit 1
fi

# Portable timeout: prefer GNU `timeout`, then `gtimeout` (brew coreutils).
# If neither is available, run without a hard timeout (claude's --max-turns
# bounds the call; rely on that as the primary budget guard).
if command -v timeout >/dev/null 2>&1; then
  TIMEOUT_CMD=(timeout "$PER_CALL_TIMEOUT")
elif command -v gtimeout >/dev/null 2>&1; then
  TIMEOUT_CMD=(gtimeout "$PER_CALL_TIMEOUT")
else
  echo "WARN: no timeout binary available — relying on --max-turns=$MAX_TURNS"
  TIMEOUT_CMD=(env)   # no-op pass-through; sidesteps set -u empty-array expansion
fi

if [ "${1:-}" = "--force" ]; then
  echo "--force: wiping existing transcripts"
  rm -f "$OUT_DIR"/*.transcript.json "$OUT_DIR"/*.preflight.txt "$OUT_DIR"/run.log
fi

mkdir -p "$OUT_DIR"
LOG="$OUT_DIR/run.log"
echo "=== run started $(date -u +%Y-%m-%dT%H:%M:%SZ) model=$MODEL ===" >> "$LOG"

# Pre-run CLI preflight: document which external tools are actually installed.
# Used by the summarizer to flag fabricated tool invocations.
PREFLIGHT_GLOBAL="$OUT_DIR/preflight-global.txt"
{
  echo "=== preflight $(date -u +%Y-%m-%dT%H:%M:%SZ) ==="
  for tool in bandit docker socket trivy gitleaks semgrep nuclei checkov tfsec; do
    path=$(command -v "$tool" 2>/dev/null || true)
    echo "$tool: ${path:-(not installed)}"
  done
  # docker-scout is a plugin, not a standalone binary. Check via `docker scout version`.
  if command -v docker >/dev/null 2>&1 && docker scout version >/dev/null 2>&1; then
    scout_ver=$(docker scout version 2>/dev/null | awk '/version:/ {print $2; exit}')
    echo "docker-scout: installed (plugin, ${scout_ver:-unknown version})"
  else
    echo "docker-scout: (not installed)"
  fi
} > "$PREFLIGHT_GLOBAL"
cat "$PREFLIGHT_GLOBAL"
echo ""

total=$(wc -l < "$PROMPTS_JSONL" | tr -d ' ')
i=0
skipped=0
failed=0
succeeded=0

while IFS= read -r line; do
  i=$((i + 1))
  skill=$(printf '%s' "$line" | python3 -c "import json,sys;print(json.loads(sys.stdin.read())['skill'])")
  prompt_id=$(printf '%s' "$line" | python3 -c "import json,sys;print(json.loads(sys.stdin.read())['prompt_id'])")
  prompt_text=$(printf '%s' "$line" | python3 -c "import json,sys;print(json.loads(sys.stdin.read())['prompt_text'])")

  out="$OUT_DIR/${skill}_${prompt_id}.transcript.json"
  err="$OUT_DIR/${skill}_${prompt_id}.stderr.txt"

  # Idempotency: skip if a valid (non-empty, success-typed) transcript exists.
  if [ -f "$out" ] && python3 -c "import json,sys;d=json.load(open(sys.argv[1]));sys.exit(0 if d.get('type')=='result' and not d.get('is_error') else 1)" "$out" 2>/dev/null; then
    skipped=$((skipped + 1))
    printf "[%3d/%d] SKIP %-28s %-6s (already have valid transcript)\n" "$i" "$total" "$skill" "$prompt_id"
    continue
  fi

  printf "[%3d/%d] RUN  %-28s %-6s " "$i" "$total" "$skill" "$prompt_id"
  start_ts=$(date +%s)

  # Invocation: repo root is CWD so .claude/skills/ discovery works AND prompts
  # that reference `tests/fixtures/<skill>/` resolve correctly as relative paths.
  set +e
  (
    cd "$REPO_ROOT"
    "${TIMEOUT_CMD[@]}" claude -p "$prompt_text" \
      --model "$MODEL" \
      --output-format json \
      --permission-mode bypassPermissions \
      --max-turns "$MAX_TURNS"
  ) > "$out" 2> "$err"
  rc=$?
  set -e

  dur=$(( $(date +%s) - start_ts ))

  if [ $rc -eq 0 ] && [ -s "$out" ]; then
    # Validate JSON parse and success type
    if python3 -c "import json,sys;d=json.load(open(sys.argv[1]));sys.exit(0 if d.get('type')=='result' and not d.get('is_error') else 1)" "$out" 2>/dev/null; then
      succeeded=$((succeeded + 1))
      printf "OK   %ds\n" "$dur"
      echo "[$i] OK $skill $prompt_id ${dur}s" >> "$LOG"
    else
      failed=$((failed + 1))
      printf "BAD  %ds (response not success-typed)\n" "$dur"
      echo "[$i] BAD $skill $prompt_id ${dur}s" >> "$LOG"
    fi
  else
    failed=$((failed + 1))
    printf "FAIL %ds (rc=%d)\n" "$dur" "$rc"
    echo "[$i] FAIL $skill $prompt_id ${dur}s rc=$rc" >> "$LOG"
  fi

  sleep "$RATE_LIMIT_SLEEP"
done < "$PROMPTS_JSONL"

echo ""
echo "=== run finished $(date -u +%Y-%m-%dT%H:%M:%SZ) total=$total ok=$succeeded skipped=$skipped failed=$failed ==="
echo "=== run finished $(date -u +%Y-%m-%dT%H:%M:%SZ) total=$total ok=$succeeded skipped=$skipped failed=$failed ===" >> "$LOG"

if [ "$failed" -gt 0 ]; then
  exit 1
fi

#!/bin/bash
# Exit codes: 0 = iteration completed normally, 2 = failed/retryable (bad output, API error)

BEFORE_COMMIT=$(git rev-parse HEAD 2>/dev/null)
PRD_BEFORE=$(grep -cE '^[[:space:]]*- \[x\]' PRD.md 2>/dev/null)
PRD_BEFORE=${PRD_BEFORE:-0}

RESULT=$(claude --permission-mode acceptEdits -p "@PRD.md @progress.txt
1. Read the PRD and progress.txt.
2. Find the next unchecked task in the PRD.
3. Implement it fully.
4. Commit your changes with a descriptive message.
5. Check off the task in PRD.md and append what you did to progress.txt with a timestamp.
ONLY DO ONE TASK AT A TIME.
If all tasks are done, output <promise>COMPLETE</promise>." --output-format json)
CLAUDE_EXIT=$?

if [ $CLAUDE_EXIT -ne 0 ] || ! echo "$RESULT" | jq -e . >/dev/null 2>&1; then
  echo "[ralph-once] claude call failed (exit $CLAUDE_EXIT) or returned invalid JSON" >&2
  echo "$RESULT" >&2
  exit 2
fi

AFTER_COMMIT=$(git rev-parse HEAD 2>/dev/null)
PRD_AFTER=$(grep -cE '^[[:space:]]*- \[x\]' PRD.md 2>/dev/null)
PRD_AFTER=${PRD_AFTER:-0}

FILES_CHANGED=0
INSERTIONS=0
DELETIONS=0
if [ -n "$BEFORE_COMMIT" ] && [ "$BEFORE_COMMIT" != "$AFTER_COMMIT" ]; then
  COMMIT_MADE=true
  SHORTSTAT=$(git diff --shortstat "$BEFORE_COMMIT" "$AFTER_COMMIT")
  FILES_CHANGED=$(echo "$SHORTSTAT" | grep -oE '[0-9]+ file' | grep -oE '[0-9]+' || echo 0)
  INSERTIONS=$(echo "$SHORTSTAT" | grep -oE '[0-9]+ insertion' | grep -oE '[0-9]+' || echo 0)
  DELETIONS=$(echo "$SHORTSTAT" | grep -oE '[0-9]+ deletion' | grep -oE '[0-9]+' || echo 0)
else
  COMMIT_MADE=false
fi

echo "$RESULT" | jq -c \
  --argjson commit_made "$COMMIT_MADE" \
  --argjson files_changed "$FILES_CHANGED" \
  --argjson insertions "$INSERTIONS" \
  --argjson deletions "$DELETIONS" \
  --argjson prd_before "$PRD_BEFORE" \
  --argjson prd_after "$PRD_AFTER" \
  '{
    duration_ms,
    duration_api_ms,
    num_turns,
    total_cost_usd,
    is_error,
    api_error_status,
    usage: {
      input_tokens: .usage.input_tokens,
      output_tokens: .usage.output_tokens,
      cache_read_input_tokens: .usage.cache_read_input_tokens,
      cache_creation_input_tokens: .usage.cache_creation_input_tokens
    },
    permission_denials,
    terminal_reason,
    stop_reason,
    git: {
      commit_made: $commit_made,
      files_changed: $files_changed,
      insertions: $insertions,
      deletions: $deletions
    },
    prd: {
      checkboxes_before: $prd_before,
      checkboxes_after: $prd_after,
      progressed: ($prd_after > $prd_before)
    }
  }' >> metrics.jsonl

echo "$RESULT" | jq -r '.result // empty'

if [ "$(echo "$RESULT" | jq -r '.is_error')" = "true" ]; then
  echo "[ralph-once] claude reported is_error=true (api_error_status: $(echo "$RESULT" | jq -r '.api_error_status'))" >&2
  exit 2
fi

exit 0

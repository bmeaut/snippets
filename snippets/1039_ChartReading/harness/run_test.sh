#!/bin/bash
# ./run_test.sh | ./run_test.sh --single <chart_id> <model_id> <model_alias>

set -uo pipefail

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$BASE_DIR/.." && pwd)"
PROMPT_DIR="$ROOT_DIR/data/prompts"
RAW_DIR="$ROOT_DIR/data/raw"
MODELS_FILE="$BASE_DIR/models.json"

mkdir -p "$RAW_DIR"
cd "$ROOT_DIR"

run_one() {
  local chart_id="$1"
  local model_id="$2"
  local model_alias="$3"
  local prompt_file="data/prompts/${chart_id}.txt"
  local out_file="$RAW_DIR/${chart_id}__${model_alias}.json"

  if [ -f "$out_file" ]; then
    local prev_is_error
    prev_is_error=$(jq -r '.is_error' "$out_file" 2>/dev/null)
    if [ "$prev_is_error" != "true" ]; then
      echo "[skip] $out_file már létezik (sikeres)"
      return 0
    fi
    echo "[retry] $out_file korábban hibával futott - újrapróbáljuk"
  fi

  echo "[run] $chart_id / $model_alias ($model_id)"
  RESULT=$(cat "$prompt_file" | claude -p --model "$model_id" --output-format json)

  if ! echo "$RESULT" | jq -e . >/dev/null 2>&1; then
    echo "[error] $chart_id / $model_alias hívás sikertelen, nem valid JSON" >&2
    echo "$RESULT" >&2
    return 1
  fi

  echo "$RESULT" | jq -c \
    --arg chart_id "$chart_id" --arg model_alias "$model_alias" --arg model_id "$model_id" \
    '{chart_id: $chart_id, model_alias: $model_alias, model_id: $model_id,
      result, duration_ms, total_cost_usd, is_error, usage}' \
    > "$out_file"

  if [ "$(echo "$RESULT" | jq -r '.is_error')" = "true" ]; then
    echo "  -> $out_file [is_error=true: $(echo "$RESULT" | jq -r '.result' | head -c 100)]"
  else
    echo "  -> $out_file (cost: \$$(echo "$RESULT" | jq -r '.total_cost_usd'))"
  fi
}

if [ "${1:-}" = "--single" ]; then
  run_one "$2" "$3" "${4:-$3}"
  exit $?
fi

MODELS=$(jq -c '.models[]' "$MODELS_FILE")

for prompt_file in "$PROMPT_DIR"/*.txt; do
  chart_id=$(basename "$prompt_file" .txt)
  while IFS= read -r model_json; do
    model_id=$(echo "$model_json" | jq -r '.resolved_id')
    model_alias=$(echo "$model_json" | jq -r '.alias')
    run_one "$chart_id" "$model_id" "$model_alias"
  done <<< "$MODELS"
done

echo "Kész."

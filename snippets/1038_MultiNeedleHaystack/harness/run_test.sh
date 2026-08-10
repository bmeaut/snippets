#!/bin/bash
# ./run_test.sh | ./run_test.sh --single <prompt_file> <model_id> <model_alias>

set -uo pipefail

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROMPT_DIR="$BASE_DIR/../data/prompts"
RAW_DIR="$BASE_DIR/../data/raw"
MODELS_FILE="$BASE_DIR/models.json"

mkdir -p "$RAW_DIR"

run_one() {
  local prompt_file="$1"
  local model_id="$2"
  local model_alias="$3"
  local cell_id
  cell_id=$(basename "$prompt_file" .txt)
  local out_file="$RAW_DIR/${cell_id}__${model_alias}.json"

  if [ -f "$out_file" ]; then
    local prev_is_error prev_result
    prev_is_error=$(jq -r '.is_error' "$out_file" 2>/dev/null)
    if [ "$prev_is_error" != "true" ]; then
      echo "[skip] $out_file már létezik (sikeres)"
      return 0
    fi
    prev_result=$(jq -r '.result // ""' "$out_file" 2>/dev/null)
    if echo "$prev_result" | grep -qi "too long"; then
      echo "[skip] $out_file már létezik (kontextusablak-túlcsordulás, végleges eredmény, nem próbáljuk újra)"
      return 0
    fi
    echo "[retry] $out_file korábban átmeneti hibával futott (pl. session limit) - újrapróbáljuk"
  fi

  echo "[run] $cell_id / $model_alias ($model_id)"
  RESULT=$(cat "$prompt_file" | claude -p --model "$model_id" --output-format json)
  CLAUDE_EXIT=$?

  if ! echo "$RESULT" | jq -e . >/dev/null 2>&1; then
    echo "[error] $cell_id / $model_alias hívás sikertelen, nem valid JSON (exit $CLAUDE_EXIT)" >&2
    echo "$RESULT" >&2
    return 1
  fi

  echo "$RESULT" | jq -c \
    --arg cell_id "$cell_id" --arg model_alias "$model_alias" --arg model_id "$model_id" \
    '{cell_id: $cell_id, model_alias: $model_alias, model_id: $model_id,
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

FULL_GRID_MODELS=$(jq -c '.full_grid[]' "$MODELS_FILE")
COMPARISON_MODELS=$(jq -c '.comparison_sample[]' "$MODELS_FILE")
COMPARISON_CELLS=("ctx2000_k3_rep1" "ctx2000_k20_rep1" "ctx150000_k3_rep1" "ctx150000_k20_rep1")

echo "=== Teljes rács (full_grid modellek, minden cella) ==="
for prompt_file in "$PROMPT_DIR"/*.txt; do
  while IFS= read -r model_json; do
    model_id=$(echo "$model_json" | jq -r '.resolved_id')
    model_alias=$(echo "$model_json" | jq -r '.alias')
    run_one "$prompt_file" "$model_id" "$model_alias"
  done <<< "$FULL_GRID_MODELS"
done

echo "=== Szűkített összehasonlító minta (comparison_sample modellek, 4 szélső cella) ==="
for cell_id in "${COMPARISON_CELLS[@]}"; do
  prompt_file="$PROMPT_DIR/${cell_id}.txt"
  if [ ! -f "$prompt_file" ]; then
    echo "[warn] hiányzó cella: $prompt_file" >&2
    continue
  fi
  while IFS= read -r model_json; do
    model_id=$(echo "$model_json" | jq -r '.resolved_id')
    model_alias=$(echo "$model_json" | jq -r '.alias')
    run_one "$prompt_file" "$model_id" "$model_alias"
  done <<< "$COMPARISON_MODELS"
done

echo "Kész."

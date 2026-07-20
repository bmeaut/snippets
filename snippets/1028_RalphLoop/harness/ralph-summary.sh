#!/bin/bash
# Run after the loop finishes (or anytime) to aggregate metrics.jsonl.

jq -s '{
  iterations: length,
  total_duration_ms: (map(.duration_ms) | add),
  total_cost_usd: (map(.total_cost_usd) | add),
  total_input_tokens: (map(.usage.input_tokens) | add),
  total_output_tokens: (map(.usage.output_tokens) | add),
  total_cache_read_tokens: (map(.usage.cache_read_input_tokens) | add),
  total_cache_creation_tokens: (map(.usage.cache_creation_input_tokens) | add),
  iterations_with_permission_denials: (map(select((.permission_denials | length) > 0)) | length),
  iterations_with_errors: (map(select(.is_error == true)) | length),
  iterations_without_commit: (map(select(.git.commit_made == false)) | length),
  iterations_without_prd_progress: (map(select(.prd.progressed == false)) | length)
}' metrics.jsonl

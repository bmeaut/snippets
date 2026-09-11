#!/bin/bash
# Outer driver: repeatedly calls ralph-once.sh.
# On failure (e.g. rate limit / quota exhausted, transient API error) it backs off
# with exponential delay and retries — no need to resume manually, since each
# iteration re-reads PRD.md/progress.txt fresh and just continues from there.
# Stops when the PRD reports completion, or after too many consecutive failures.

cd "$(dirname "$0")" || exit 1

BACKOFF=60
MAX_BACKOFF=1800
CONSECUTIVE_FAILURES=0
MAX_CONSECUTIVE_FAILURES=20

while true; do
  OUTPUT=$(./ralph-once.sh)
  STATUS=$?
  echo "$OUTPUT"

  if [ $STATUS -ne 0 ]; then
    CONSECUTIVE_FAILURES=$((CONSECUTIVE_FAILURES + 1))
    if [ $CONSECUTIVE_FAILURES -ge $MAX_CONSECUTIVE_FAILURES ]; then
      echo "[ralph-loop] $CONSECUTIVE_FAILURES consecutive failures, giving up." >&2
      exit 1
    fi
    echo "[ralph-loop] iteration failed, retrying in ${BACKOFF}s (failure $CONSECUTIVE_FAILURES/$MAX_CONSECUTIVE_FAILURES)" >&2
    sleep "$BACKOFF"
    BACKOFF=$((BACKOFF * 2))
    if [ $BACKOFF -gt $MAX_BACKOFF ]; then
      BACKOFF=$MAX_BACKOFF
    fi
    continue
  fi

  CONSECUTIVE_FAILURES=0
  BACKOFF=60

  if echo "$OUTPUT" | grep -q '<promise>COMPLETE</promise>'; then
    echo "[ralph-loop] PRD complete, stopping."
    break
  fi
done

#!/bin/bash
# Az egész futás indítása: a futtatót addig indítja újra, amíg minden hívás el nem készül.
# A kész hívások fájlja megmarad, a futtató csak a hiányzókat küldi el.
cd "$(dirname "$0")"
for attempt in $(seq 1 100); do
  python3 run_test.py --workers 6 "$@"
  missing=$(python3 run_test.py --count-missing "$@")
  echo "[run_all] $attempt. kör után hiányzik: $missing"
  [ "$missing" = "0" ] && exit 0
  sleep 600
done
echo "[run_all] a körök száma elfogyott, hiányzó hívások: $missing"
exit 1

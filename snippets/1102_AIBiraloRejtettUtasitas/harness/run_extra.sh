#!/bin/bash
# A három kiegészítő rész egymás után: skála, határoló-formátumok, hosszú beadandók.
cd "$(dirname "$0")"
for part in skala fmt hosszu; do
  ./run_all.sh --part "$part" || exit 1
done

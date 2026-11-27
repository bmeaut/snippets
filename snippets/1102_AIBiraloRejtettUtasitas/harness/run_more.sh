#!/bin/bash
# A két további rész egymás után: eltérő határoló, védekezés.
cd "$(dirname "$0")"
for part in vedekezes mism; do
  ./run_all.sh --part "$part" || exit 1
done

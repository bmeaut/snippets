#!/usr/bin/env bash
# Egyszeri, ingyenes lépés: a hivatalos dokumentum-skillek (xlsx, docx, pptx, pdf)
# telepítése a workdir_skill/ munkakönyvtárba, projekt-hatókörben (--scope project),
# tehát nem módosítja a felhasználó globális Claude Code beállításait.
# A workdir_noskill/ szándékosan érintetlen marad.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKDIR_SKILL="$SCRIPT_DIR/workdir_skill"

mkdir -p "$WORKDIR_SKILL"
cd "$WORKDIR_SKILL"

claude plugin marketplace add anthropics/skills --scope project
claude plugin install document-skills@anthropic-agent-skills --scope project

echo
echo "Telepítve. Ellenőrzés:"
cat .claude/settings.json

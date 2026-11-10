#!/usr/bin/env python3
"""Kiegészítő teszt (nem a fő adatkészlet része): az 5. szintű összevető minta
(opus, sonnet_elozo) hivatkozásjegyzék-feladatait megismétli egy explicit,
"maradj magyarul" utasítással kiegészített prompttal, hogy megnézze, ez
megszünteti-e a hivatkozásjegyzék-példák egyikében (index.md) dokumentált angol nyelvi
átszivárgást (angol hónapnév, angolos dátumformátum). Ugyanazokat a
forrásadatokat használja, mint az eredeti citation_L5_r1/r2 feladat (a
generate_task szintén seedelt), így közvetlenül összevethető az eredeti
eredménnyel. Külön mappákba ír (prompts_hu_test/, raw_hu_test/), a fő
adatkészletet nem érinti. Szekvenciálisan fut (nem párhuzamosan), hogy
elkerülje az 5. buktatóban leírt megosztott munkakönyvtár-problémát.
"""
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from generate_citations import generate_task, render_prompt

HERE = Path(__file__).resolve().parent
DATA = HERE.parent.parent / "data" / "citations"
PROMPTS_DIR = DATA / "prompts_hu_test"
RAW_DIR = DATA / "raw_hu_test"
MODELS = json.loads((HERE.parent / "models.json").read_text(encoding="utf-8"))

HU_INSTRUCTION = (
    "\n\nFontos: a teljes hivatkozásjegyzék kizárólag magyar nyelven készüljön, "
    "a hónapneveket és a dátumformátumot is beleértve, semmit ne fordíts angolra."
)


def model_id_for(alias: str) -> str:
    for group in ("full_grid", "comparison_sample"):
        for m in MODELS[group]:
            if m["alias"] == alias:
                return m["resolved_id"]
    raise KeyError(alias)


def main():
    PROMPTS_DIR.mkdir(parents=True, exist_ok=True)
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    tasks = [generate_task(5, 1), generate_task(5, 2)]
    total_cost = 0.0
    for task in tasks:
        prompt = render_prompt(task) + HU_INSTRUCTION
        (PROMPTS_DIR / f"{task['task_id']}.txt").write_text(prompt, encoding="utf-8")
        for model_alias in ("opus", "sonnet_elozo"):
            for condition in ("skill", "noskill"):
                workdir = HERE.parent / ("workdir_skill" if condition == "skill" else "workdir_noskill")
                stale = workdir / "output.docx"
                stale.unlink(missing_ok=True)
                model_id = model_id_for(model_alias)
                out_base = RAW_DIR / f"{task['task_id']}__{model_alias}__{condition}"
                print(f"RUN: {task['task_id']} {model_alias} {condition}")
                proc = subprocess.run(
                    ["claude", "-p", prompt, "--model", model_id, "--output-format", "json",
                     "--permission-mode", "bypassPermissions"],
                    cwd=workdir, capture_output=True, text=True, timeout=600,
                )
                result = json.loads(proc.stdout) if proc.stdout.strip() else {"is_error": True, "stderr": proc.stderr}
                out_base.with_suffix(".json").write_text(
                    json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
                )
                if stale.exists():
                    stale.replace(out_base.with_suffix(".docx"))
                cost = result.get("total_cost_usd", 0) or 0
                total_cost += cost
                print(f"  is_error={result.get('is_error')} cost=${cost:.4f} file_created={out_base.with_suffix('.docx').exists()}")
    print(f"=== összköltség: ${total_cost:.4f} ===")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""A teljes teszt-mátrix (2 forgatókönyv x 2 feltétel x modellek x szintek x
ismétlések) lefuttatása a `claude -p` CLI-vel.

Használat:
  python3 run_test.py pilot   # 3 gyors, olcsó hívás költségbecsléshez
  python3 run_test.py full    # a teljes, fizetős mátrix (megerősítés után!)
  python3 run_test.py single <scenario> <task_id> <model_alias> <condition>
"""
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "data"
MODELS = json.loads((HERE / "models.json").read_text(encoding="utf-8"))
EXT = {"budget": "xlsx", "citations": "docx"}


def model_id_for(alias: str) -> str:
    for group in ("full_grid", "comparison_sample"):
        for m in MODELS[group]:
            if m["alias"] == alias:
                return m["resolved_id"]
    raise KeyError(alias)


def run_call(scenario: str, task_id: str, model_alias: str, condition: str, force: bool = False) -> dict:
    ext = EXT[scenario]
    prompt_path = DATA / scenario / "prompts" / f"{task_id}.txt"
    out_base = DATA / scenario / "raw" / f"{task_id}__{model_alias}__{condition}"
    out_json = out_base.with_suffix(".json")
    out_file = out_base.with_suffix(f".{ext}")

    if not force and out_json.exists():
        try:
            prev = json.loads(out_json.read_text(encoding="utf-8"))
            if not prev.get("is_error", True):
                print(f"SKIP (kész): {task_id} {model_alias} {condition}")
                return prev
        except (json.JSONDecodeError, OSError):
            pass

    workdir = HERE / ("workdir_skill" if condition == "skill" else "workdir_noskill")
    if condition == "skill" and not (workdir / ".claude" / "settings.json").exists():
        raise SystemExit("A workdir_skill nincs előkészítve, előbb futtasd a setup_skills.sh-t.")
    workdir.mkdir(exist_ok=True)
    stale = workdir / f"output.{ext}"
    stale.unlink(missing_ok=True)

    prompt = prompt_path.read_text(encoding="utf-8")
    model_id = model_id_for(model_alias)
    print(f"RUN: {scenario} {task_id} {model_alias} {condition}")
    try:
        proc = subprocess.run(
            ["claude", "-p", prompt, "--model", model_id, "--output-format", "json",
             "--permission-mode", "bypassPermissions"],
            cwd=workdir, capture_output=True, text=True, timeout=600,
        )
        result = json.loads(proc.stdout) if proc.stdout.strip() else {"is_error": True, "stderr": proc.stderr}
    except (subprocess.TimeoutExpired, json.JSONDecodeError) as exc:
        result = {"is_error": True, "exception": str(exc)}

    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    if stale.exists():
        stale.replace(out_file)

    cost = result.get("total_cost_usd", 0)
    print(f"  is_error={result.get('is_error')} cost=${cost} file_created={out_file.exists()}")
    return result


def all_task_ids(scenario: str) -> list:
    return sorted(p.stem for p in (DATA / scenario / "prompts").glob("*.txt"))


def level_of(task_id: str) -> int:
    return int(task_id.split("_L")[1].split("_r")[0])


def repeat_of(task_id: str) -> int:
    return int(task_id.split("_r")[1])


def run_scenario(scenario: str):
    total_cost = 0.0
    for task_id in all_task_ids(scenario):
        for m in MODELS["full_grid"]:
            for condition in ("skill", "noskill"):
                r = run_call(scenario, task_id, m["alias"], condition)
                total_cost += r.get("total_cost_usd", 0) or 0
        if level_of(task_id) == 5 and repeat_of(task_id) <= 2:
            for m in MODELS["comparison_sample"]:
                for condition in ("skill", "noskill"):
                    r = run_call(scenario, task_id, m["alias"], condition)
                    total_cost += r.get("total_cost_usd", 0) or 0
    print(f"=== {scenario} összköltség eddig: ${total_cost:.4f} ===")
    return total_cost


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "full"

    if mode == "pilot":
        haiku_id = model_id_for("haiku")
        results = [
            run_call("budget", "budget_L1_r1", "haiku", "skill", force=True),
            run_call("budget", "budget_L1_r1", "haiku", "noskill", force=True),
            run_call("citations", "citation_L1_r1", "haiku", "skill", force=True),
        ]
        total = sum(r.get("total_cost_usd", 0) or 0 for r in results)
        per_call = total / len(results)
        # 68 hívás/forgatókönyv x 2 forgatókönyv = 136 hívás -- lásd terv
        estimate = per_call * 136
        print(f"\n3 próbahívás összköltsége: ${total:.4f} (átlag/hívás: ${per_call:.4f})")
        print(f"Becsült teljes költség (136 hívás): ${estimate:.2f}")
        print("A teljes futtatás előtt kérj megerősítést a felhasználótól ez alapján.")
        return

    if mode == "single":
        _, _, scenario, task_id, model_alias, condition = sys.argv
        run_call(scenario, task_id, model_alias, condition, force=True)
        return

    if mode == "full":
        c1 = run_scenario("budget")
        c2 = run_scenario("citations")
        print(f"\n=== TELJES ÖSSZKÖLTSÉG: ${c1 + c2:.4f} ===")
        return

    print(f"Ismeretlen mód: {mode}", file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main()

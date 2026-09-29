"""Agent loopok három szinten, lokális Ollama modellel.

A szkript egy ideiglenes könyvtárba létrehoz egy hibás Python modult (stats.py)
és a hozzá tartozó teszteket, majd a --mode kapcsolótól függően:

  inner  egyetlen agent loop: a modell toolokat hív, amíg kész nincs
  outer  outer loop: az agent loop újra és újra indul friss kontextussal,
         az állapot fájlokban él, és a tesztek döntik el, mikor van vége
  hier   planner + workerek: egy planner részfeladatokra bontja a munkát,
         és minden részfeladatra külön outer loop indul

Használat:
    ollama pull qwen2.5:7b-instruct
    python3 agent_loop.py --mode inner
    python3 agent_loop.py --mode outer --max-iterations 10
    python3 agent_loop.py --mode hier

Csak a Python standard könyvtárát használja, és egy futó Ollama szervert
(http://localhost:11434) feltételez.
"""

import argparse
import json
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

OLLAMA_URL = "http://localhost:11434/api/chat"

BUGGY_MODULE = '''\
def mean(values):
    """Az elemek számtani átlaga."""
    return sum(values) / (len(values) - 1)


def median(values):
    """A rendezett lista középső eleme (páros hossznál a két középső átlaga)."""
    n = len(values)
    mid = n // 2
    if n % 2 == 0:
        return (values[mid - 1] + values[mid]) / 2
    return values[mid]


def normalize(values):
    """Min-max normalizálás a [0, 1] intervallumra."""
    lo, hi = min(values), max(values)
    return [(v - lo) / hi for v in values]
'''

TESTS = '''\
from stats import mean, median, normalize

def check(name, got, expected):
    ok = got == expected
    print(("PASS" if ok else "FAIL"), name, "->", got, "(expected", expected, ")")
    return ok

results = [
    check("mean([2, 4, 6])", mean([2, 4, 6]), 4),
    check("median([3, 1, 2])", median([3, 1, 2]), 2),
    check("median([4, 1, 3, 2])", median([4, 1, 3, 2]), 2.5),
    check("normalize([2, 4, 6])", normalize([2, 4, 6]), [0.0, 0.5, 1.0]),
]
print(f"{sum(results)}/{len(results)} tests passed")
'''

SYSTEM_PROMPT = """You are a coding agent working in a small Python project.
Use the tools to inspect the files, run the tests, and fix the bugs in stats.py.
Always run the tests after changing a file. Do not modify test_stats.py.
When your task is done, reply with a short summary and do not call any more tools."""

TOOLS = [
    {"type": "function", "function": {
        "name": "read_file",
        "description": "Return the full content of a file.",
        "parameters": {"type": "object",
                       "properties": {"path": {"type": "string"}},
                       "required": ["path"]}}},
    {"type": "function", "function": {
        "name": "replace_in_file",
        "description": "Replace an exact snippet of a file with new text.",
        "parameters": {"type": "object",
                       "properties": {"path": {"type": "string"},
                                      "old": {"type": "string"},
                                      "new": {"type": "string"}},
                       "required": ["path", "old", "new"]}}},
    {"type": "function", "function": {
        "name": "run_tests",
        "description": "Run test_stats.py and return its output.",
        "parameters": {"type": "object", "properties": {}}}},
]

EMPTY_REPLY_FEEDBACK = (
    "Your last reply was empty. If you tried to call a tool, the arguments were "
    "not valid JSON (check quotes and escaping). Try again with a short snippet.")

TOTALS = {"model_calls": 0, "prompt_tokens": 0, "output_tokens": 0}


# --- Környezet és toolok ---------------------------------------------------

def setup_workdir() -> Path:
    workdir = Path(tempfile.mkdtemp(prefix="agent_loop_"))
    (workdir / "stats.py").write_text(BUGGY_MODULE)
    (workdir / "test_stats.py").write_text(TESTS)
    return workdir


def run_tests(workdir: Path) -> str:
    proc = subprocess.run([sys.executable, "test_stats.py"], cwd=workdir,
                          capture_output=True, text=True, timeout=30)
    return (proc.stdout + proc.stderr).strip()


TEST_COUNTS = {"": 4, "mean(": 1, "median(": 2, "normalize(": 1}


def passed(test_output: str, name_filter: str = "") -> tuple[int, int]:
    """(átment, összes) a tesztkimenetből, opcionálisan egy függvényre szűrve.
    Ha a tesztfájl összeomlik (pl. SyntaxError), a le nem futott teszt hibásnak számít."""
    ok = sum(1 for l in test_output.splitlines()
             if l.startswith("PASS") and name_filter in l)
    return ok, TEST_COUNTS.get(name_filter, 1)


def crashed(test_output: str) -> bool:
    return "Traceback" in test_output or "Error" in test_output.splitlines()[-1]


def execute_tool(workdir: Path, name: str, args: dict) -> str:
    """A tool hívás végrehajtása. A hibát szövegként adjuk vissza a modellnek."""
    try:
        if name == "read_file":
            return (workdir / Path(args["path"]).name).read_text()
        if name == "replace_in_file":
            target = workdir / Path(args["path"]).name
            if target.name != "stats.py":
                return "Error: only stats.py may be modified."
            text = target.read_text()
            if args["old"] not in text:
                return "Error: 'old' text not found in the file. Read the file and copy it exactly."
            target.write_text(text.replace(args["old"], args["new"], 1))
            return "Replaced 1 occurrence in stats.py."
        if name == "run_tests":
            return run_tests(workdir)
        return f"Error: unknown tool '{name}'."
    except KeyError as exc:  # hiányzó argumentum, gyakran elrontott JSON miatt
        return f"Error: missing argument {exc}. Send all required arguments as valid JSON."
    except Exception as exc:
        return f"Error: {type(exc).__name__}: {exc}"


def chat(model: str, messages: list, tools=TOOLS, fmt=None) -> dict:
    payload = {"model": model, "messages": messages, "stream": False,
               "options": {"temperature": 0.2, "seed": 1, "num_ctx": 16384,
                           "num_predict": 1024}}  # válaszonkénti tokenkorlát
    if tools:
        payload["tools"] = tools
    if fmt:
        payload["format"] = fmt  # strukturált (JSON séma szerinti) kimenet
    req = urllib.request.Request(OLLAMA_URL, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=600) as resp:
        data = json.loads(resp.read())
    TOTALS["model_calls"] += 1
    TOTALS["prompt_tokens"] += data.get("prompt_eval_count", 0)
    TOTALS["output_tokens"] += data.get("eval_count", 0)
    return data


# --- 1. szint: az agent loop -------------------------------------------------

def agent_loop(model: str, workdir: Path, task: str, max_turns: int, tag: str = "") -> str:
    """Egy session: a modell toolokat hív, amíg tool hívás nélkül nem válaszol."""
    messages = [{"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": task}]
    for turn in range(1, max_turns + 1):
        msg = chat(model, messages)["message"]
        messages.append(msg)
        calls = msg.get("tool_calls") or []
        if not calls and not msg.get("content", "").strip():
            print(f"{tag}[turn {turn}] üres válasz, visszajelzés")
            messages.append({"role": "user", "content": EMPTY_REPLY_FEEDBACK})
            continue
        if not calls:  # nincs tool hívás: a modell szerint kész
            print(f"{tag}[turn {turn}] kész: {msg['content'].strip()[:150]!r}")
            return msg["content"]
        for call in calls:
            name = call["function"]["name"]
            args = call["function"].get("arguments") or {}
            result = execute_tool(workdir, name, args)
            print(f"{tag}[turn {turn}] {name} -> {result.splitlines()[-1][:90] if result else ''}")
            messages.append({"role": "tool", "tool_name": name, "content": result})
    print(f"{tag}elérte a turn limitet ({max_turns})")
    return "(turn limit reached)"


# --- 2. szint: az outer loop -------------------------------------------------

def outer_loop(model: str, workdir: Path, task: str, max_iterations: int,
               max_turns: int, name_filter: str = "", tag: str = "") -> bool:
    """Friss kontextusú iterációk, notes fájllal és tesztalapú leállással."""
    notes_file = workdir / f"NOTES{name_filter.strip('(')}.md"
    notes_file.write_text("")
    # Checkpoint: az utolsó olyan állapot, ami nem rosszabb a korábbiaknál.
    best_source = (workdir / "stats.py").read_text()
    best_total = passed(run_tests(workdir))[0]

    for it in range(1, max_iterations + 1):
        tests = run_tests(workdir)
        ok, total = passed(tests, name_filter)
        if ok == total:
            print(f"{tag}== a cél teljesült a(z) {it}. iteráció előtt")
            return True
        # Az iteráció kontextusát a harness rakja össze a fájlokból: a modell
        # nem emlékszik az előző iterációra, csak arra, ami a notes fájlban van.
        prompt = (f"Task: {task}\n\n"
                  f"Current test output:\n{tests}\n\n"
                  f"Current stats.py:\n```python\n{(workdir / 'stats.py').read_text()}```\n\n"
                  f"Notes from previous attempts:\n{notes_file.read_text() or '(none, this is the first attempt)'}\n"
                  "Fix the code with replace_in_file, then run the tests.")
        summary = agent_loop(model, workdir, prompt, max_turns, tag=f"{tag}  ")

        after = run_tests(workdir)
        new_total = passed(after)[0]
        new_ok, _ = passed(after, name_filter)
        if crashed(after) or new_total < best_total:
            # Visszalépés vagy törött kód: az utolsó jó állapot visszaállítása, hogy a
            # következő iteráció ne egy elrontott fájlból induljon.
            (workdir / "stats.py").write_text(best_source)
            reason = after.splitlines()[-1][:80] if crashed(after) else f"{new_total}/4 tests"
            verdict = f"REVERTED ({reason}, previous best was {best_total}/4)"
        else:
            best_source, best_total = (workdir / "stats.py").read_text(), new_total
            verdict = f"kept, {new_ok}/{total} target tests pass"
        print(f"{tag}== {it}. iteráció: {verdict}")
        with notes_file.open("a") as f:
            f.write(f"- Attempt {it}: {verdict}. Agent said: {summary.strip()[:200]}\n")

    ok, total = passed(run_tests(workdir), name_filter)
    return ok == total


# --- 3. szint: planner és workerek -------------------------------------------

PLAN_SCHEMA = {
    "type": "object",
    "properties": {"subtasks": {"type": "array", "items": {
        "type": "object",
        "properties": {"function": {"type": "string"}, "instruction": {"type": "string"}},
        "required": ["function", "instruction"]}}},
    "required": ["subtasks"]}


def plan(model: str, workdir: Path) -> list[dict]:
    """A planner egy structured output hívással részfeladatokra bontja a munkát."""
    prompt = ("Break the work of fixing stats.py into independent subtasks, one per "
              "function that needs to change. For each, give the function name and a "
              "one-sentence instruction.\n\n"
              f"Test output:\n{run_tests(workdir)}\n\n"
              f"stats.py:\n```python\n{(workdir / 'stats.py').read_text()}```")
    reply = chat(model, [{"role": "user", "content": prompt}], tools=None, fmt=PLAN_SCHEMA)
    subtasks = json.loads(reply["message"]["content"])["subtasks"]
    source = (workdir / "stats.py").read_text()
    # A tervet is ellenőrizni kell: csak létező függvényekre vonatkozó feladat maradhat.
    return [s for s in subtasks if f"def {s['function']}(" in source]


def hierarchical(model: str, workdir: Path, max_rounds: int, max_iterations: int,
                 max_turns: int) -> bool:
    for rnd in range(1, max_rounds + 1):
        subtasks = plan(model, workdir)
        print(f"== planner ({rnd}. kör): " + ", ".join(s["function"] for s in subtasks))
        for s in subtasks:
            print(f"-- worker: {s['function']} | {s['instruction']}")
            task = (f"Only change the function `{s['function']}` in stats.py. "
                    f"{s['instruction']} Make the tests for `{s['function']}` pass.")
            outer_loop(model, workdir, task, max_iterations, max_turns,
                       name_filter=f"{s['function']}(", tag="   ")
        ok, total = passed(run_tests(workdir))
        print(f"== {rnd}. kör vége: {ok}/{total} teszt megy át")
        if ok == total:
            return True
    return False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["inner", "outer", "hier"], default="inner")
    parser.add_argument("--model", default="qwen2.5:7b-instruct")
    parser.add_argument("--max-turns", type=int, default=None,
                        help="turn limit egy agent loopon belül (alapból inner: 15, egyébként 8)")
    parser.add_argument("--max-iterations", type=int, default=10,
                        help="az outer loop iterációinak felső korlátja")
    parser.add_argument("--max-rounds", type=int, default=2,
                        help="planner körök száma hier módban")
    args = parser.parse_args()

    max_turns = args.max_turns or (15 if args.mode == "inner" else 8)
    workdir = setup_workdir()
    start = time.time()
    if args.mode == "inner":
        agent_loop(args.model, workdir, "The tests in this project fail. Fix stats.py.",
                   max_turns)
    elif args.mode == "outer":
        outer_loop(args.model, workdir, "Make all tests pass by fixing stats.py.",
                   args.max_iterations, max_turns)
    else:
        hierarchical(args.model, workdir, args.max_rounds, args.max_iterations, max_turns)

    final = run_tests(workdir)
    ok, total = passed(final)
    print("\n" + json.dumps({"mode": args.mode, "model": args.model, **TOTALS,
                             "seconds": round(time.time() - start, 1),
                             "tests_passed": f"{ok}/{total}", "solved": ok == total,
                             "workdir": str(workdir)}, ensure_ascii=False))


if __name__ == "__main__":
    main()

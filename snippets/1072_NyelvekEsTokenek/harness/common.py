"""Közös segédfüggvények: a `claude -p` hívás, a hibakezelés és a folytatható mentés.

A hívás szerkezete (A és B rész egyaránt): fix, rövid angol rendszerprompt, eszközök
nélkül, rögzített `--effort`, JSON kimenet, üres munkakönyvtárból. A modellhívások a
szerző Claude Code előfizetésén futnak, nem az Anthropic API-n.
"""
import json
import os
import random
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
# A hívások üres munkakönyvtára a repón és a home-on kívül van, hogy semmilyen CLAUDE.md,
# projektmemória vagy git-környezet ne kerüljön a kontextusba (ez állandó többletet biztosít).
WORKDIR = Path(tempfile.gettempdir()) / "nyelvek_workdir"
STATE_DIR = ROOT / ".run_state"

SYSTEM_PROMPT = "Follow the instructions in the user message exactly. Be concise."
PROBE_MODEL = "claude-haiku-5-5"
PROBE_PROMPT = "Say OK."

# Közzétett API-árak, millió tokenre (bemenet, kimenet), dollárban. Futtatáskor ellenőrizendő.
PRICES = {
    "claude-haiku-5-5": (0.10, 0.50),
    "claude-sonnet-5-5": (2.00, 10.00),
    "claude-opus-5": (5.00, 25.00),
    "claude-opus-5-5": (4.00, 20.00),
    "claude-sonnet-4-6": (3.00, 15.00),
    "claude-haiku-4-5": (1.00, 5.00),
}

PAUSE_LOCK = threading.Lock()
AUTH_MARKERS = ("not logged in", "please run /login", "invalid api key", "authentication")


def models():
    return json.loads((HERE / "models.json").read_text(encoding="utf-8"))


def input_tokens(usage):
    return (usage.get("input_tokens", 0)
            + usage.get("cache_creation_input_tokens", 0)
            + usage.get("cache_read_input_tokens", 0))


def equivalent_cost(model, usage):
    pin, pout = PRICES[model]
    return (input_tokens(usage) * pin + usage.get("output_tokens", 0) * pout) / 1_000_000


def write_json_atomic(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, ensure_ascii=False, indent=1), encoding="utf-8")
    os.replace(tmp, path)


def read_valid(path):
    """Egy korábbi, érvényes (hibátlan) eredményfájl tartalma, vagy None."""
    path = Path(path)
    if not path.exists():
        return None
    try:
        d = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    return d if d.get("ok") else None


def load_records(name):
    """A `data/<name>/` mappa hívásonkénti JSON-fájljai, ha léteznek, különben a csomagolt
    `data/<name>.jsonl` sorai. Minden rekord kap egy `_name` mezőt (az eredeti fájlnév)."""
    d = ROOT / "data" / name
    recs = []
    if d.is_dir() and any(d.glob("*.json")):
        for p in sorted(d.glob("*.json")):
            try:
                r = json.loads(p.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                continue
            r["_name"] = p.name
            recs.append(r)
    else:
        f = ROOT / "data" / f"{name}.jsonl"
        for line in f.read_text(encoding="utf-8").splitlines():
            if line.strip():
                recs.append(json.loads(line))
    return recs


class CallFailed(Exception):
    def __init__(self, kind, text):
        super().__init__(f"{kind}: {text[:300]}")
        self.kind = kind
        self.text = text


def call_claude(prompt, model, effort="low", timeout=300):
    """Egyetlen `claude -p` hívás. Siker esetén a JSON-választ adja, hibánál CallFailed."""
    WORKDIR.mkdir(parents=True, exist_ok=True)
    cmd = ["claude", "-p", "--model", model, "--system-prompt", SYSTEM_PROMPT,
           "--tools", "", "--effort", effort, "--output-format", "json",
           "--no-session-persistence", "--setting-sources", "", "--disable-slash-commands", "--strict-mcp-config"]
    try:
        env = dict(os.environ, ENABLE_CLAUDEAI_MCP_SERVERS="false")
        proc = subprocess.run(cmd, input=prompt, cwd=WORKDIR, capture_output=True,
                              text=True, timeout=timeout, env=env)
    except subprocess.TimeoutExpired:
        raise CallFailed("transient", "időtúllépés")
    out = proc.stdout.strip()
    try:
        d = json.loads(out) if out else None
    except json.JSONDecodeError:
        d = None
    text = (out + "\n" + proc.stderr)[:2000]
    low = text.lower()
    if d is None or d.get("is_error") or proc.returncode != 0:
        if any(m in low for m in AUTH_MARKERS):
            raise CallFailed("auth", text)
        raise CallFailed("other", text)
    if "usage" not in d or "result" not in d:
        raise CallFailed("other", "hiányos válasz: " + text)
    return d


def log_event(msg):
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    with (STATE_DIR / "events.log").open("a", encoding="utf-8") as fh:
        fh.write(time.strftime("%Y-%m-%d %H:%M:%S ") + msg + "\n")


RUN_NAME = "run"


def write_status(**kw):
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    write_json_atomic(STATE_DIR / f"status_{RUN_NAME}.json", dict(kw, updated=time.strftime("%Y-%m-%d %H:%M:%S")))


def wait_until_account_ok(max_pause_s):
    """Fiók- vagy használatilimit-szintű hibánál várakozik, amíg a próbahívás sikerül.

    Növekvő lépésközzel (5 perctől legfeljebb 30 percig) ismétli a próbahívást.
    Visszatér, ha a próbahívás sikerült. Ha a maximális várakozás letelt, kivételt dob.
    """
    start = time.time()
    delay = 300
    log_event("szünet kezdete: a próbahívás sikertelen")
    while True:
        elapsed = time.time() - start
        if elapsed > max_pause_s:
            raise SystemExit("A várakozás maximális ideje letelt, a futás tisztán leáll (újraindítható).")
        print(f"[szünet] a hívások várnak, újrapróbálás {int(delay/60)} perc múlva "
              f"(eddig {int(elapsed/60)} perc)", flush=True)
        write_status(state="paused", paused_minutes=int(elapsed / 60))
        time.sleep(delay)
        try:
            call_claude(PROBE_PROMPT, PROBE_MODEL, timeout=120)
            log_event("szünet vége: a próbahívás sikerült")
            return
        except CallFailed as e:
            if e.kind == "auth":
                raise SystemExit("Hitelesítési hiba, a várakozás nem segít: " + e.text[:200])
        delay = min(delay * 1.5, 1800)


def pause_until_ok(max_pause_s):
    """Szálbiztos várakozás: egyszerre csak egy szál vár, a többi a zár megszerzése után
    egy próbahívással ellenőrzi, hogy közben helyreállt-e a hozzáférés."""
    with PAUSE_LOCK:
        try:
            call_claude(PROBE_PROMPT, PROBE_MODEL, timeout=120)
            return
        except CallFailed as e:
            if e.kind == "auth":
                raise SystemExit("Hitelesítési hiba: " + e.text[:200])
        wait_until_account_ok(max_pause_s)


def robust_call(prompt, model, effort="low", max_pause_s=24 * 3600, transient_tries=4):
    """Hibatűrő hívás a terv 6.1 szerint. Siker esetén a JSON-választ adja.

    Átmeneti hiba: növekvő várakozással újrapróbál. Hitelesítési hiba: leáll.
    Egyéb hiba: próbahívás dönt: ha az is hibázik, fiókszintű a baj (várakozás), ha sikerül,
    a hívás hibás (CallFailed("request") a hívónak).
    """
    attempt = 0
    while True:
        try:
            return call_claude(prompt, model, effort)
        except CallFailed as e:
            if e.kind == "auth":
                raise SystemExit("Hitelesítési hiba: " + e.text[:200])
            if e.kind == "transient":
                attempt += 1
                if attempt >= transient_tries:
                    raise CallFailed("request", "ismétlődő átmeneti hiba: " + e.text)
                time.sleep(min(60, 5 * 2 ** attempt) + random.random() * 3)
                continue
            # egyéb hiba: próbahívás
            log_event(f"hiba a(z) {model} hívásnál: {e.text[:200]!r}")
            try:
                call_claude(PROBE_PROMPT, PROBE_MODEL, timeout=120)
            except CallFailed as pe:
                if pe.kind == "auth":
                    raise SystemExit("Hitelesítési hiba: " + pe.text[:200])
                pause_until_ok(max_pause_s)
                continue  # a szünet után ugyanazt a hívást újrapróbálja
            raise CallFailed("request", e.text)

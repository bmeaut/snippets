#!/usr/bin/env python3
"""Ground truth és prompt generálás a Költségvetés-táblázat (xlsx skill) forgatókönyvhöz.

Determinisztikus: minden szint/ismétlés kombinációhoz string-kulcsos, seedelt
random.Random(f"budget_{level}_{repeat}") RNG-t használ. Kétszer lefuttatva
bájtra egyező ground_truth.json-t kell adnia.
"""
import json
import random
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA_DIR = HERE.parent.parent / "data" / "budget"
PROMPTS_DIR = DATA_DIR / "prompts"

REPEATS_PER_LEVEL = 3

# (leírás, kategória, kind, min forint, max forint) -- kind: "expense" vagy "income"
ITEM_TEMPLATES = [
    ("Tesco bevásárlás", "élelmiszer", "expense", 2000, 15000),
    ("Lidl heti bevásárlás", "élelmiszer", "expense", 3000, 12000),
    ("Kifli.hu rendelés", "élelmiszer", "expense", 2500, 9000),
    ("Piac, zöldség-gyümölcs", "élelmiszer", "expense", 1500, 6000),
    ("Wolt rendelés", "élelmiszer", "expense", 2500, 7000),
    ("albérlet", "lakhatás", "expense", 80000, 150000),
    ("közös költség", "lakhatás", "expense", 8000, 20000),
    ("gáz- és áramszámla", "lakhatás", "expense", 6000, 25000),
    ("internet előfizetés", "lakhatás", "expense", 4000, 8000),
    ("Spotify előfizetés", "szórakozás", "expense", 1500, 2000),
    ("mozijegy", "szórakozás", "expense", 2000, 3500),
    ("koncertjegy", "szórakozás", "expense", 5000, 18000),
    ("Netflix előfizetés", "szórakozás", "expense", 2500, 4000),
    "SEPARATOR",
    ("BKK havijegy", "közlekedés", "expense", 9500, 9500),
    ("benzin", "közlekedés", "expense", 8000, 20000),
    ("taxi/Bolt", "közlekedés", "expense", 1500, 6000),
    ("vonatjegy hazautazás", "közlekedés", "expense", 3000, 9000),
    ("H&M ruhavásárlás", "ruházat", "expense", 5000, 20000),
    ("cipő", "ruházat", "expense", 8000, 25000),
    ("gyógyszertár", "egészség", "expense", 1500, 8000),
    ("fogorvosi kezelés", "egészség", "expense", 5000, 30000),
    ("szemüveg", "egészség", "expense", 15000, 45000),
    ("egyetemi jegyzet/könyv", "oktatás", "expense", 3000, 12000),
    ("nyelvvizsga díj", "oktatás", "expense", 15000, 35000),
    ("online kurzus", "oktatás", "expense", 5000, 20000),
    ("ajándék", "egyéb", "expense", 3000, 15000),
    ("fodrász", "egyéb", "expense", 4000, 12000),
    ("telefon előfizetés", "egyéb", "expense", 3000, 6000),
    ("ösztöndíj", "bevétel", "income", 40000, 80000),
    ("részmunkaidős fizetés", "bevétel", "income", 60000, 180000),
    ("családi támogatás", "bevétel", "income", 20000, 60000),
    ("alkalmi munka", "bevétel", "income", 15000, 50000),
]
ITEM_TEMPLATES = [t for t in ITEM_TEMPLATES if t != "SEPARATOR"]

LEVEL_CATEGORIES = {
    1: ["élelmiszer", "lakhatás", "bevétel"],
    2: ["élelmiszer", "lakhatás", "szórakozás", "közlekedés", "bevétel"],
    3: ["élelmiszer", "lakhatás", "szórakozás", "közlekedés", "bevétel"],
    4: ["élelmiszer", "lakhatás", "szórakozás", "közlekedés", "ruházat", "egészség", "bevétel"],
    5: ["élelmiszer", "lakhatás", "szórakozás", "közlekedés", "ruházat", "egészség",
        "oktatás", "egyéb", "bevétel"],
}

LEVEL_N_TRANSACTIONS = {1: (8, 10), 2: (12, 15), 3: (15, 18), 4: (18, 22), 5: (25, 30)}
LEVEL_HIDE_CATEGORY = {1: 0.0, 2: 0.4, 3: 0.6, 4: 0.6, 5: 0.6}
LEVEL_AMOUNT_STYLES = {1: ["plain"], 2: ["plain"], 3: ["plain", "dot_k", "ezer", "bare"],
                       4: ["plain", "dot_k", "ezer", "bare"], 5: ["plain", "dot_k", "ezer", "bare"]}
LEVEL_SHARED_COST_PROB = {1: 0.0, 2: 0.0, 3: 0.0, 4: 0.25, 5: 0.3}
SHARE_WORDS = {2: "ketten", 3: "hárman", 4: "négyen"}


def format_amount(n: int, style: str) -> str:
    if style == "plain":
        return f"{n} Ft"
    if style == "bare":
        return f"{n}"
    # n mindig 50 Ft többszöröse (round_to_50), tehát n/1000 legfeljebb 2
    # tizedesjegyre pontos -- 1 tizedesjeggyel kerekítve (pl. "42.6k") a fél
    # ezres tételek (pl. 42650 Ft) valódi értéke elveszne. 2 tizedes mindig
    # elég, a fölösleges nullákat levágjuk.
    val = n / 1000
    s = f"{val:.2f}".rstrip("0").rstrip(".")
    if style == "dot_k":
        return f"{s}k Ft"
    if style == "ezer":
        return f"{s.replace('.', ',')} e Ft"
    raise ValueError(style)


def round_to_50(n: float) -> int:
    return int(round(n / 50.0) * 50)


def generate_task(level: int, repeat: int) -> dict:
    rng = random.Random(f"budget_{level}_{repeat}")
    task_id = f"budget_L{level}_r{repeat}"
    categories = LEVEL_CATEGORIES[level]
    templates = [t for t in ITEM_TEMPLATES if t[1] in categories]
    n_lo, n_hi = LEVEL_N_TRANSACTIONS[level]
    n_transactions = rng.randint(n_lo, n_hi)
    hide_prob = LEVEL_HIDE_CATEGORY[level]
    styles = LEVEL_AMOUNT_STYLES[level]
    shared_prob = LEVEL_SHARED_COST_PROB[level]
    has_weeks = level == 5

    # Legalább egy élelmiszer-tétel biztosítása minden héten (5. szinten), hogy a
    # "melyik héten volt legmagasabb az élelmiszer-kiadás" kérdésnek legyen tartalma.
    transactions = []
    for i in range(n_transactions):
        tmpl = rng.choice(templates)
        desc, category, kind, amt_lo, amt_hi = tmpl
        full_amount = round_to_50(rng.randint(amt_lo, amt_hi))
        signed_full = full_amount if kind == "income" else -full_amount

        share_n = None
        actual_amount = signed_full
        share_text = None
        if kind == "expense" and rng.random() < shared_prob:
            share_n = rng.choice([2, 3, 4])
            if rng.random() < 0.5:
                # A rész összege a promptban explicit szerepel (50 Ft-ra
                # kerekítve, mint minden más összeg) -- a modellnek ezt csak
                # le kell olvasnia, nem kiszámolnia.
                share_amount = round_to_50(full_amount / share_n)
                share_text = f"ebből az én részem {share_amount} Ft"
            else:
                # Itt a modellnek magának kell osztania -- a ground truth a
                # legközelebbi forintra kerekít (nem 50 Ft-ra), mert egy
                # pontos osztás ide vezet, nem egy kerek 50-es összegre.
                share_amount = round(full_amount / share_n)
                share_text = f"{SHARE_WORDS[share_n]} osztottuk"
            actual_amount = -share_amount

        category_hidden = kind == "expense" and rng.random() < hide_prob
        style = rng.choice(styles)
        week = rng.randint(1, 4) if has_weeks else None

        transactions.append({
            "description": desc,
            "category": category,
            "category_hidden": category_hidden,
            "kind": kind,
            "full_amount_huf": full_amount,
            "actual_amount_huf": actual_amount,
            "amount_render_style": style,
            "share_n": share_n,
            "share_text": share_text,
            "week": week,
        })

    category_totals = {c: 0 for c in categories}
    for t in transactions:
        category_totals[t["category"]] += t["actual_amount_huf"]
    balance = sum(category_totals.values())

    weekly_max_category = None
    if has_weeks:
        week_totals = {w: 0 for w in (1, 2, 3, 4)}
        for t in transactions:
            if t["category"] == "élelmiszer":
                week_totals[t["week"]] += -t["actual_amount_huf"]
        max_val = max(week_totals.values())
        weekly_max_category = [w for w, v in week_totals.items() if v == max_val]

    return {
        "task_id": task_id,
        "level": level,
        "repeat": repeat,
        "categories_available": categories,
        "transactions": transactions,
        "category_totals": category_totals,
        "balance": balance,
        "weekly_max_category": weekly_max_category,
    }


def render_transaction_line(t: dict) -> str:
    amount_str = format_amount(t["full_amount_huf"], t["amount_render_style"])
    parts = [t["description"]]
    if not t["category_hidden"]:
        parts.append(f"({t['category']})")
    if t["week"] is not None:
        parts.append(f"[{t['week']}. hét]")
    line = " ".join(parts) + f" - {amount_str}"
    if t["share_text"]:
        line += f", {t['share_text']}"
    return line


def render_prompt(task: dict) -> str:
    lines = [render_transaction_line(t) for t in task["transactions"]]
    categories = ", ".join(task["categories_available"])
    extra_task = ""
    if task["weekly_max_category"] is not None:
        extra_task = (
            "\n4. Add meg, melyik héten (1-4) volt a legmagasabb az élelmiszer-kategória "
            "kiadása."
        )
    return (
        "Az alábbi nyers tranzakciólistából (ez egy hónap tranzakciói) készíts egy "
        "szervezett költségvetés-táblázatot xlsx fájlként.\n\n"
        f"A lehetséges kategóriák: {categories}.\n\n"
        "Tranzakciók:\n" + "\n".join(f"- {l}" for l in lines) + "\n\n"
        "Feladat:\n"
        "1. Kategorizáld az egyes tételeket (ha a kategória nincs explicit megadva, "
        "a leírásból következtesd ki, és a fenti kategórialistából válassz).\n"
        "2. Számítsd ki a kategóriánkénti összköltést (a bevétel is egy kategória; "
        "megosztott költség esetén csak a saját részed számít bele).\n"
        "3. Számítsd ki a záró egyenleget (az összes kategória összege).\n"
        + extra_task + "\n\n"
        "Mentsd el az eredményt \"output.xlsx\" néven a jelenlegi könyvtárba. Legyen "
        "benne egy munkalap a tranzakciók listájával, és egy másik a kategóriánkénti "
        "összesítéssel és a záró egyenleggel."
    )


def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    PROMPTS_DIR.mkdir(parents=True, exist_ok=True)
    tasks = []
    for level in range(1, 6):
        for repeat in range(1, REPEATS_PER_LEVEL + 1):
            task = generate_task(level, repeat)
            tasks.append(task)
            (PROMPTS_DIR / f"{task['task_id']}.txt").write_text(
                render_prompt(task), encoding="utf-8"
            )
    (DATA_DIR / "ground_truth.json").write_text(
        json.dumps(tasks, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"{len(tasks)} feladat generálva -> {DATA_DIR / 'ground_truth.json'}")


if __name__ == "__main__":
    main()

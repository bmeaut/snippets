#!/usr/bin/env python3
"""Ground truth és prompt generálás a Hivatkozásjegyzék (docx skill) forgatókönyvhöz.

A format_apa() függvény adja a ground truth-ot -- ugyanezt hívja a score_citations.py
is az elvárt válasz előállításához, tehát a "helyesség" nem külső forrásból jön, hanem
egy itt rögzített, determinisztikus formázási szabályból.

Determinisztikus: random.Random(f"citation_{level}_{repeat}") seeddel, sosem hash()-sel.
"""
import json
import random
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA_DIR = HERE.parent.parent / "data" / "citations"
PROMPTS_DIR = DATA_DIR / "prompts"

REPEATS_PER_LEVEL = 3

SURNAMES = [
    "Kovács", "Nagy", "Tóth", "Szabó", "Horváth", "Varga", "Kiss", "Molnár",
    "Németh", "Farkas", "Balogh", "Papp", "Takács", "Juhász", "Lakatos",
    "Mészáros", "Oláh", "Simon", "Rácz", "Fekete", "Szűcs", "Gál", "Török", "Fodor",
]
INITIALS = ["A", "B", "D", "E", "G", "I", "J", "K", "L", "M", "N", "O", "P", "R", "S", "T", "V", "Z"]

BOOK_TITLES = [
    "A tanulás pszichológiája", "Bevezetés a statisztikába",
    "Modern szoftverfejlesztési módszerek", "A magyar nyelv története",
    "Alapfokú ökológia", "A társadalomtudományi kutatás módszertana",
    "Kognitív folyamatok az oktatásban", "A döntéselmélet alapjai",
    "Bevezetés a hálózattudományba", "A gazdaságtörténet vázlatai",
    "Adatvizualizáció gyakorlata", "A szervezetpszichológia alapjai",
    "Kritikai gondolkodás és argumentáció", "A klímaváltozás társadalmi hatásai",
    "Bevezetés a mesterséges intelligenciába", "A nyelvelsajátítás folyamata",
    "Kutatásmetodológiai alapfogalmak", "A fenntartható fejlődés dilemmái",
    "Az oktatástechnológia története", "Statisztikai következtetés a gyakorlatban",
]
ARTICLE_TITLES = [
    "A kritikus gondolkodás fejlesztése felsőoktatásban",
    "Az online tanulás hatása a motivációra",
    "A csoportmunka szerepe a problémamegoldásban",
    "A visszacsatolás hatása a tanulási eredményekre",
    "Digitális eszközök használata a középiskolai oktatásban",
    "A tanári attitűd hatása a diákok teljesítményére",
    "A stressz és a tanulási teljesítmény kapcsolata",
    "Az önszabályozott tanulás mérési lehetőségei",
    "A kortárs mentorálás hatása az egyetemi lemorzsolódásra",
    "A gamifikáció szerepe a nyelvtanulásban",
    "A távoktatás minőségbiztosítási kérdései",
    "A kritikai szövegértés fejlődése serdülőkorban",
    "A projektalapú oktatás hatásai csoportos környezetben",
    "A tanulói autonómia és a belső motiváció összefüggései",
    "Az adaptív tesztelés alkalmazása a felmérésekben",
]
JOURNALS = [
    "Magyar Pedagógia", "Alkalmazott Nyelvtudomány", "Statisztikai Szemle",
    "Informatika és Oktatás", "Iskolakultúra", "Pszichológia",
    "Szociológiai Szemle", "Educatio",
]
PUBLISHERS = [
    "Akadémiai Kiadó", "Typotex", "Osiris Kiadó", "Corvina Kiadó",
    "Gondolat Kiadó", "L'Harmattan Kiadó", "Kalligram Kiadó", "Saxum Kiadó",
]
WEBSITE_TITLES = [
    "A tanulási szokások változása digitális korban",
    "Hogyan hat a képernyőidő a koncentrációra?",
    "A felsőoktatás jövője: Tíz tendencia",
    "Mi az a spacing effect, és miért működik?",
    "A kutatási adatok nyílt megosztásának előnyei",
]
SITE_NAMES = ["Qubit", "Index Tudomány", "Origo Tudomány", "444 Tudomány", "National Geographic Magyarország"]
MONTHS = ["január", "február", "március", "április", "május", "június",
          "július", "augusztus", "szeptember", "október", "november", "december"]

LEVEL_CFG = {
    1: {"n": 5, "types": ["book"], "max_authors": 1, "missing_fields": False, "shuffled_field_order": False, "shuffled_source_order": False},
    2: {"n": 8, "types": ["book", "article"], "max_authors": 1, "missing_fields": False, "shuffled_field_order": False, "shuffled_source_order": False},
    3: {"n": 10, "types": ["book", "article"], "max_authors": 2, "missing_fields": True, "shuffled_field_order": False, "shuffled_source_order": False},
    4: {"n": 12, "types": ["book", "article", "website"], "max_authors": 2, "missing_fields": True, "shuffled_field_order": True, "shuffled_source_order": False},
    5: {"n": 15, "types": ["book", "article", "website"], "max_authors": 3, "missing_fields": True, "shuffled_field_order": True, "shuffled_source_order": True},
}


def make_author(rng: random.Random) -> str:
    return f"{rng.choice(SURNAMES)}, {rng.choice(INITIALS)}."


def join_authors_apa(authors: list) -> str:
    if len(authors) == 1:
        return authors[0]
    if len(authors) == 2:
        return f"{authors[0]}, & {authors[1]}"
    return ", ".join(authors[:-1]) + f", & {authors[-1]}"


def title_seg(title: str) -> str:
    """A cím a mondatvégi írásjelével, dupla pont nélkül ('?' vagy '!' után nem kell '.')."""
    return title if title.endswith((".", "?", "!")) else f"{title}."


def format_apa(source: dict) -> str:
    authors_str = join_authors_apa(source["authors"])
    title = title_seg(source["title"])
    if source["type"] == "book":
        return f"{authors_str} ({source['year']}). {title} {source['publisher']}."
    if source["type"] == "article":
        s = f"{authors_str} ({source['year']}). {title} {source['journal']}, {source['volume']}"
        if source.get("issue"):
            s += f"({source['issue']})"
        if source.get("pages"):
            s += f", {source['pages']}."
        else:
            s += "."
        if source.get("doi"):
            s += f" https://doi.org/{source['doi']}"
        return s
    if source["type"] == "website":
        year_str = f"{source['year']}, {source['month']} {source['day']}"
        return f"{authors_str} ({year_str}). {title} {source['site_name']}. {source['url']}"
    raise ValueError(source["type"])


def sort_key(source: dict):
    return (source["authors"][0], source["year"])


def generate_source(rng: random.Random, cfg: dict) -> dict:
    stype = rng.choice(cfg["types"])
    n_authors = rng.randint(1, cfg["max_authors"])
    authors = [make_author(rng) for _ in range(n_authors)]
    year = rng.randint(1995, 2024)
    if stype == "book":
        return {"type": "book", "authors": authors, "year": year,
                "title": rng.choice(BOOK_TITLES), "publisher": rng.choice(PUBLISHERS)}
    if stype == "article":
        source = {"type": "article", "authors": authors, "year": year,
                  "title": rng.choice(ARTICLE_TITLES), "journal": rng.choice(JOURNALS),
                  "volume": rng.randint(1, 45), "issue": rng.randint(1, 4)}
        if cfg["missing_fields"] and rng.random() < 0.4:
            pass  # nincs oldalszám
        else:
            start = rng.randint(1, 180)
            source["pages"] = f"{start}-{start + rng.randint(5, 30)}"
        if cfg["missing_fields"] and rng.random() < 0.5:
            source["doi"] = f"10.{rng.randint(1000,9999)}/{rng.randint(1000,9999)}.{rng.randint(1000,9999)}"
        return source
    if stype == "website":
        return {"type": "website", "authors": authors, "year": year,
                "month": rng.choice(MONTHS), "day": rng.randint(1, 28),
                "title": rng.choice(WEBSITE_TITLES), "site_name": rng.choice(SITE_NAMES),
                "url": f"https://example.edu/cikk/{rng.randint(1000,9999)}"}
    raise ValueError(stype)


FIELD_LABELS = {
    "authors": "szerző(k)", "year": "év", "title": "cím", "publisher": "kiadó",
    "journal": "folyóirat", "volume": "kötetszám", "issue": "lapszám", "pages": "oldalszám",
    "doi": "DOI", "site_name": "weboldal neve", "url": "URL", "month": "hónap", "day": "nap",
}
FIELD_ORDER_BY_TYPE = {
    "book": ["authors", "title", "year", "publisher"],
    "article": ["authors", "title", "year", "journal", "volume", "issue", "pages", "doi"],
    "website": ["authors", "title", "year", "month", "day", "site_name", "url"],
}


def render_source_block(source: dict, shuffle_fields: bool, rng: random.Random) -> str:
    fields = [f for f in FIELD_ORDER_BY_TYPE[source["type"]] if f in source]
    if shuffle_fields:
        fields = fields[:]
        rng.shuffle(fields)
    lines = []
    for f in fields:
        val = source[f]
        if f == "authors":
            val = "; ".join(val)
        lines.append(f"  {FIELD_LABELS[f]}: {val}")
    return f"- típus: {source['type']}\n" + "\n".join(lines)


def generate_task(level: int, repeat: int) -> dict:
    cfg = LEVEL_CFG[level]
    rng = random.Random(f"citation_{level}_{repeat}")
    sources = [generate_source(rng, cfg) for _ in range(cfg["n"])]
    sources_sorted = sorted(sources, key=sort_key)
    expected_formatted = [format_apa(s) for s in sources_sorted]

    present_order = sources_sorted[:]
    if cfg["shuffled_source_order"]:
        present_order = sources[:]
        rng.shuffle(present_order)

    blocks = [render_source_block(s, cfg["shuffled_field_order"], rng) for s in present_order]

    return {
        "task_id": f"citation_L{level}_r{repeat}",
        "level": level,
        "repeat": repeat,
        "sources_raw": present_order,
        "expected_formatted": expected_formatted,
        "raw_blocks_text": blocks,
    }


def render_prompt(task: dict) -> str:
    body = "\n".join(task["raw_blocks_text"])
    return (
        "Az alábbi rendezetlen, véletlen sorrendű forrásadatokból készíts egy helyes, APA 7. "
        "kiadás szerint formázott, ábécésorrendbe rendezett hivatkozásjegyzéket docx "
        "fájlként.\n\n"
        "Források:\n" + body + "\n\n"
        "Mentsd el \"output.docx\" néven a jelenlegi könyvtárba. Minden hivatkozás külön "
        "bekezdésben szerepeljen, a szerző vezetékneve szerint ábécésorrendbe rendezve. "
        "Ha egy mező (pl. oldalszám, DOI) nincs megadva egy forrásnál, hagyd ki a "
        "hivatkozásból, ne találj ki helyette adatot."
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

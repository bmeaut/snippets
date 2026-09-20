import argparse
import glob
import json
import os
import random
import re

BASE = os.path.dirname(os.path.abspath(__file__))
SOURCE_DIR = os.path.join(BASE, "..", "data", "haystack_source")
PROMPT_DIR = os.path.join(BASE, "..", "data", "prompts")

# karakterszám/4 - durva token-becslés, nem a valódi Claude tokenizálás
CHARS_PER_TOKEN = 4

CONTEXT_TOKENS = [2000, 16000, 64000, 150000]
K_VALUES = [3, 8, 15, 20]
REPEATS = [1, 2]


def load_source_paragraphs():
    paragraphs = []
    for path in sorted(glob.glob(os.path.join(SOURCE_DIR, "*.txt"))):
        with open(path, encoding="utf-8") as f:
            text = f.read()
        for para in re.split(r"\n\s*\n", text):
            para = para.strip()
            if len(para) > 40:
                paragraphs.append(para)
    if not paragraphs:
        raise RuntimeError(
            "Nincs forrás-bekezdés a data/haystack_source/-ban - futtasd előbb a fetch_haystack_source.py-t."
        )
    return paragraphs


def load_needles():
    with open(os.path.join(BASE, "needles.json"), encoding="utf-8") as f:
        return json.load(f)["needles"]


def build_base_paragraphs(source_paragraphs, target_chars, rng):
    pool = list(source_paragraphs)
    rng.shuffle(pool)
    chosen = []
    total = 0
    i = 0
    while total < target_chars:
        if i >= len(pool):
            rng.shuffle(pool)
            i = 0
        chosen.append(pool[i])
        total += len(pool[i]) + 1
        i += 1
    return chosen


def insert_needles(base_paragraphs, needles, rng):
    n = len(base_paragraphs)
    k = len(needles)
    result = list(base_paragraphs)
    positions = []
    for idx, needle in enumerate(needles):
        frac = (idx + 1) / (k + 1)
        insert_at = int(frac * n)
        result.insert(insert_at + idx, needle["statement"])
        positions.append({"id": needle["id"], "position_frac": round(frac, 3)})
    return result, positions


def build_prompt(haystack_text, needles):
    lines = ["Az alábbi szövegben (tananyag-jegyzet) el van rejtve néhány oktatói megjegyzés.",
             "Válaszolj KIZÁRÓLAG egy JSON tömbben, minden kérdésre külön elemmel, "
             "a kérdés sorszámával (\"id\") és a válasszal (\"answer\"). "
             "Ha valamelyik választ nem találod a szövegben, az \"answer\" értéke legyen \"nincs adat\".",
             "Formátum példa: [{\"id\": 1, \"answer\": \"...\"}, {\"id\": 2, \"answer\": \"...\"}]",
             "",
             "--- TANANYAG ---",
             haystack_text,
             "--- TANANYAG VÉGE ---",
             "",
             "Kérdések:"]
    for i, needle in enumerate(needles, start=1):
        lines.append(f"{i}. {needle['question']}")
    lines.append("")
    lines.append("Válaszolj KIZÁRÓLAG a JSON tömbbel, más szöveg nélkül.")
    return "\n".join(lines)


def generate_cell(context_tokens, k, repeat, source_paragraphs, all_needles, out_dir):
    seed = hash((context_tokens, k, repeat)) & 0xFFFFFFFF
    rng = random.Random(seed)

    target_chars = context_tokens * CHARS_PER_TOKEN
    base_paragraphs = build_base_paragraphs(source_paragraphs, target_chars, rng)

    chosen_needles = rng.sample(all_needles, k)
    final_paragraphs, positions = insert_needles(base_paragraphs, chosen_needles, rng)
    haystack_text = "\n\n".join(final_paragraphs)

    prompt_text = build_prompt(haystack_text, chosen_needles)

    cell_id = f"ctx{context_tokens}_k{k}_rep{repeat}"
    os.makedirs(out_dir, exist_ok=True)
    prompt_path = os.path.join(out_dir, f"{cell_id}.txt")
    truth_path = os.path.join(out_dir, f"{cell_id}_truth.json")

    with open(prompt_path, "w", encoding="utf-8") as f:
        f.write(prompt_text)

    pos_by_id = {p["id"]: p["position_frac"] for p in positions}
    truth = {
        "cell_id": cell_id,
        "context_tokens_target": context_tokens,
        "k": k,
        "repeat": repeat,
        "actual_chars": len(haystack_text),
        "needles": [
            {
                "id": n["id"],
                "type": n["type"],
                "question": n["question"],
                "expected_answer": n["expected_answer"],
                "match": n.get("match", "substring"),
                "position_frac": pos_by_id[n["id"]],
            }
            for n in chosen_needles
        ],
    }
    with open(truth_path, "w", encoding="utf-8") as f:
        json.dump(truth, f, ensure_ascii=False, indent=2)

    return prompt_path, truth_path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--context-tokens", type=int)
    parser.add_argument("--k", type=int)
    parser.add_argument("--repeat", type=int, default=1)
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--out-dir", default=PROMPT_DIR)
    args = parser.parse_args()

    source_paragraphs = load_source_paragraphs()
    all_needles = load_needles()

    if args.all:
        cells = [(c, k, r) for c in CONTEXT_TOKENS for k in K_VALUES for r in REPEATS]
    else:
        if args.context_tokens is None or args.k is None:
            parser.error("Add meg a --context-tokens és --k paramétereket, vagy használd az --all kapcsolót.")
        cells = [(args.context_tokens, args.k, args.repeat)]

    for context_tokens, k, repeat in cells:
        prompt_path, truth_path = generate_cell(
            context_tokens, k, repeat, source_paragraphs, all_needles, args.out_dir
        )
        print(f"[OK] ctx={context_tokens} k={k} rep={repeat} -> {prompt_path}")

    print(f"\n{len(cells)} cella legenerálva -> {args.out_dir}")


if __name__ == "__main__":
    main()

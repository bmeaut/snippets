import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
CHARTS_DIR = os.path.join(BASE, "..", "data", "charts")
OUT_PATH = os.path.join(BASE, "..", "data", "human_worksheet.md")

TYPE_ORDER = ["bar", "line", "scatter"]


def main():
    gt = json.load(open(os.path.join(CHARTS_DIR, "ground_truth.json"), encoding="utf-8"))
    image_entries = [e for e in gt if e["condition"] == "image"]
    image_entries.sort(key=lambda e: (e["level"], TYPE_ORDER.index(e["chart_type"]), e["repeat"]))

    lines = ["# Emberi kiértékelő lap", "",
             "Minden diagramhoz 3 kérdés tartozik (az átlag-kérdést kihagytuk, mert azt ránézésre "
             "nem lehet megmondani). Csak nézd meg a képet, és írd be a válaszod "
             "a `Válasz:` mögé. Ne nézz bele a `data/charts/ground_truth.json`-ba, mert az elrontja a vak tesztet.", ""]

    n_questions = 0
    for e in image_entries:
        lines.append(f"## {e['chart_id']} (szint: {e['level']}, típus: {e['chart_type']})")
        lines.append("")
        img_rel = os.path.relpath(os.path.join(BASE, "..", e["file"]), os.path.dirname(OUT_PATH))
        lines.append(f"![{e['chart_id']}]({img_rel})")
        lines.append("")
        questions = [q for q in e["questions"] if q["kind"] != "aggregate"]
        for i, q in enumerate(questions, start=1):
            lines.append(f"{i}. {q['question']}")
            lines.append("   Válasz: ")
            lines.append("")
        n_questions += len(questions)
        lines.append("---")
        lines.append("")

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"{len(image_entries)} diagram, {n_questions} kérdés -> {OUT_PATH}")


if __name__ == "__main__":
    main()

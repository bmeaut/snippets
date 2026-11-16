#!/usr/bin/env python3
"""A hívásonkénti nyers JSON-fájlok csomagolása JSON Lines fájlokká (a publikáláshoz).

data/a_raw/, data/b_raw/, data/b_visible/, data/a_check/  ->  data/*.jsonl
A `common.load_records` a csomagolt fájlokat is olvassa, ha a mappák nincsenek meg, így a
pontozó és az elemző a csomagolt adatból is ugyanazt az eredményt adja.
"""
import json

import common

DATA = common.ROOT / "data"


def main():
    for name in ("a_raw", "b_raw", "b_visible", "a_check"):
        recs = common.load_records(name)
        out = DATA / f"{name}.jsonl"
        with out.open("w", encoding="utf-8") as fh:
            for r in recs:
                fh.write(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n")
        print(f"{name}: {len(recs)} rekord -> {out.name} ({out.stat().st_size // 1024} KiB)")


if __name__ == "__main__":
    main()

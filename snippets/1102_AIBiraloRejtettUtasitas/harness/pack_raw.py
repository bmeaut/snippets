#!/usr/bin/env python3
"""A hívásonkénti nyers JSON-fájlok csomagolása egy JSON Lines fájllá (a publikáláshoz).

data/raw/  ->  data/raw.jsonl, data/raw_struct/  ->  data/raw_struct.jsonl
A `common.load_records` a csomagolt fájlt is olvassa, ha a mappa nincs meg, így a pontozó és
az elemző a csomagolt adatból is ugyanazt az eredményt adja.
"""
import json

import common

DATA = common.ROOT / "data"


def main():
    for name in ("raw", "raw_struct", "raw_skala", "raw_fmt", "raw_hosszu", "raw_mism", "raw_vedekezes"):
        if not (DATA / name).is_dir() and not (DATA / f"{name}.jsonl").exists():
            continue
        recs = common.load_records(name)
        out = DATA / f"{name}.jsonl"
        with out.open("w", encoding="utf-8") as fh:
            for r in recs:
                fh.write(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n")
        print(f"{name}: {len(recs)} rekord -> {out.name} ({out.stat().st_size // 1024} KiB)")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""A `claude -p` keretezés fix bemeneti többletének mérése modellenként.

Egyetlen "." karakterből álló promptot küld, és a bemeneti tokenszámból 1 tokent
(a pont maga) levon. A B rész pontozása ezt vonja ki a nyers bemeneti tokenszámból.
"""
import time

import common

A_RAW = common.ROOT / "data" / "a_raw"


def main():
    M = common.models()
    for g in ("full_grid", "comparison_sample", "tokenizer_only"):
        for m in M[g]:
            model = m["resolved_id"]
            path = A_RAW / f"{model}__frame.json"
            if common.read_valid(path):
                continue
            d = common.robust_call(".", model)
            u = d["usage"]
            common.write_json_atomic(path, {
                "ok": True, "model": model, "input_tokens": common.input_tokens(u),
                "content_tokens": 1, "usage": u, "ts": time.strftime("%Y-%m-%d %H:%M:%S")})
            print(model, common.input_tokens(u))


if __name__ == "__main__":
    main()

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

BASE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE, "data")
IMAGE_DIR = os.path.join(BASE, "image")
os.makedirs(IMAGE_DIR, exist_ok=True)

FULL_GRID_MODELS = ["haiku", "sonnet"]
COMPARISON_MODELS = ["opus", "claude-sonnet-4-5"]
MODEL_ORDER = FULL_GRID_MODELS + COMPARISON_MODELS
MODEL_LABELS = {
    "haiku": "Haiku 4.5", "sonnet": "Sonnet (aktuális)",
    "opus": "Opus", "claude-sonnet-4-5": "Sonnet (előző gen.)",
}
TYPE_LABELS = {
    "hatarido": "határidő/dátum", "definicio": "definíció",
    "szam": "szám/képlet", "kivetel": "kivétel-szabály",
}
THIRD_ORDER = ["eleje", "kozepe", "vege"]
THIRD_LABELS = {"eleje": "eleje", "kozepe": "közepe", "vege": "vége"}


def load():
    results = pd.read_csv(os.path.join(DATA_DIR, "results.csv"))
    cells = pd.read_csv(os.path.join(DATA_DIR, "cells.csv"))
    results["correct"] = pd.to_numeric(results["correct"], errors="coerce")
    cells["recall"] = pd.to_numeric(cells["recall"], errors="coerce")
    return results, cells


def chart_heatmap(results):
    fig, axes = plt.subplots(1, len(FULL_GRID_MODELS), figsize=(12, 5), sharey=True)
    cmap = plt.get_cmap("RdYlGn").copy()
    cmap.set_bad("lightgray")
    for ax, model in zip(axes, FULL_GRID_MODELS):
        sub = results[results.model_alias == model]
        pivot = sub.pivot_table(index="context_tokens_target", columns="k",
                                 values="correct", aggfunc="mean")
        masked = np.ma.masked_invalid(pivot.values)
        im = ax.imshow(masked, cmap=cmap, vmin=0, vmax=1, aspect="auto")
        ax.set_xticks(range(len(pivot.columns)))
        ax.set_xticklabels(pivot.columns)
        ax.set_yticks(range(len(pivot.index)))
        ax.set_yticklabels(pivot.index)
        ax.set_xlabel("Egyszerre kért tények száma (K)")
        ax.set_title(MODEL_LABELS[model])
        for i in range(pivot.shape[0]):
            for j in range(pivot.shape[1]):
                val = pivot.values[i, j]
                label = f"{val:.0%}" if not np.isnan(val) else "kontextus-\ntúlcsordulás"
                ax.text(j, i, label, ha="center", va="center", fontsize=8)
    axes[0].set_ylabel("Kontextushossz (token, célérték)")
    fig.colorbar(im, ax=axes, label="Recall", shrink=0.8)
    fig.suptitle("Recall a kontextushossz és a needle-szám függvényében")
    fig.savefig(os.path.join(IMAGE_DIR, "chart_heatmap.png"), dpi=150, bbox_inches="tight")
    plt.close(fig)


def chart_recall_vs_k(results):
    fig, ax = plt.subplots(figsize=(7, 5))
    for model in MODEL_ORDER:
        sub = results[results.model_alias == model]
        if sub.empty:
            continue
        grouped = sub.groupby("k")["correct"].mean().sort_index()
        style = "-o" if model in FULL_GRID_MODELS else "--s"
        ax.plot(grouped.index, grouped.values, style, label=MODEL_LABELS[model])
    ax.set_xlabel("Egyszerre kért tények száma (K)")
    ax.set_ylabel("Recall")
    ax.set_ylim(0, 1.05)
    ax.set_title("Recall a needle-szám (K) függvényében")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.savefig(os.path.join(IMAGE_DIR, "chart_recall_vs_k.png"), dpi=150, bbox_inches="tight")
    plt.close(fig)


def chart_by_type(results):
    pivot = results.groupby(["needle_type", "model_alias"])["correct"].mean().unstack()
    pivot = pivot.reindex(index=list(TYPE_LABELS.keys()), columns=MODEL_ORDER)
    fig, ax = plt.subplots(figsize=(8, 5))
    x = np.arange(len(pivot.index))
    width = 0.8 / len(MODEL_ORDER)
    for i, model in enumerate(MODEL_ORDER):
        ax.bar(x + i * width, pivot[model].values, width, label=MODEL_LABELS[model])
    ax.set_xticks(x + width * (len(MODEL_ORDER) - 1) / 2)
    ax.set_xticklabels([TYPE_LABELS[t] for t in pivot.index], rotation=15)
    ax.set_ylabel("Recall")
    ax.set_ylim(0, 1.05)
    ax.set_title("Recall needle-típusonként")
    ax.legend()
    fig.savefig(os.path.join(IMAGE_DIR, "chart_by_type.png"), dpi=150, bbox_inches="tight")
    plt.close(fig)


def chart_by_position(results):
    pivot = results.groupby(["position_third", "model_alias"])["correct"].mean().unstack()
    pivot = pivot.reindex(index=THIRD_ORDER, columns=MODEL_ORDER)
    fig, ax = plt.subplots(figsize=(7, 5))
    x = np.arange(len(pivot.index))
    width = 0.8 / len(MODEL_ORDER)
    for i, model in enumerate(MODEL_ORDER):
        ax.bar(x + i * width, pivot[model].values, width, label=MODEL_LABELS[model])
    ax.set_xticks(x + width * (len(MODEL_ORDER) - 1) / 2)
    ax.set_xticklabels([THIRD_LABELS[t] for t in pivot.index])
    ax.set_ylabel("Recall")
    ax.set_ylim(0, 1.05)
    ax.set_title("Recall a needle pozíciója szerint (a szövegben)")
    ax.legend()
    fig.savefig(os.path.join(IMAGE_DIR, "chart_by_position.png"), dpi=150, bbox_inches="tight")
    plt.close(fig)


def print_summary_tables(results, cells):
    print("\n### Összefoglaló modellenként\n")
    print("| Modell | Recall | Hívások | Összköltség | Átlag idő/hívás |")
    print("|---|---|---|---|---|")
    for model in MODEL_ORDER:
        c = cells[cells.model_alias == model]
        r = results[results.model_alias == model]
        if c.empty:
            continue
        recall = r["correct"].mean()
        n_calls = len(c)
        cost = c["total_cost_usd"].sum()
        avg_time = c["duration_ms"].mean() / 1000
        print(f"| {MODEL_LABELS[model]} | {recall:.1%} | {n_calls} | ${cost:.2f} | {avg_time:.1f} mp |")

    print("\n### Recall kontextushosszanként (full grid modellek átlaga)\n")
    print("| Kontextushossz (token) | Recall |")
    print("|---|---|")
    sub = results[results.model_alias.isin(FULL_GRID_MODELS)]
    for ctx, grp in sub.groupby("context_tokens_target"):
        print(f"| {ctx:,} | {grp['correct'].mean():.1%} |")

    print(f"\nÖsszköltség (mind a {len(cells)} hívás): ${cells['total_cost_usd'].sum():.2f}")
    print(f"JSON-parse sikertelen hívások száma: {(cells['parse_ok'] == 0).sum()} / {len(cells)}")


def main():
    results, cells = load()
    chart_heatmap(results)
    chart_recall_vs_k(results)
    chart_by_type(results)
    chart_by_position(results)
    print(f"4 ábra elmentve: {IMAGE_DIR}")
    print_summary_tables(results, cells)


if __name__ == "__main__":
    main()

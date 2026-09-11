import os
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

BASE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE, "data")
IMAGE_DIR = os.path.join(BASE, "image")
os.makedirs(IMAGE_DIR, exist_ok=True)

MODEL_ORDER = ["haiku", "sonnet", "opus", "claude-sonnet-4-5"]
MODEL_LABELS = {
    "haiku": "Haiku 4.5", "sonnet": "Sonnet (aktuális)",
    "opus": "Opus", "claude-sonnet-4-5": "Sonnet (előző gen.)",
}
TYPE_ORDER = ["bar", "line", "scatter"]
TYPE_LABELS = {"bar": "oszlop", "line": "vonal", "scatter": "szórás"}
KIND_ORDER = ["exact_value", "difference", "extremum", "aggregate"]
KIND_LABELS = {
    "exact_value": "pontos érték", "difference": "különbség",
    "extremum": "szélsőérték", "aggregate": "átlag/összeg",
}


def load():
    df = pd.read_csv(os.path.join(DATA_DIR, "results.csv"))
    return df[df.condition == "image"].copy(), df


def load_human():
    return pd.read_csv(os.path.join(DATA_DIR, "human_results.csv"))


def chart_heatmap(df):
    fig, axes = plt.subplots(1, len(MODEL_ORDER), figsize=(16, 4.5), sharey=True)
    for ax, model in zip(axes, MODEL_ORDER):
        sub = df[df.model_alias == model]
        pivot = sub.pivot_table(index="level", columns="chart_type",
                                 values="tolerance_match", aggfunc="mean")
        pivot = pivot.reindex(columns=TYPE_ORDER)
        im = ax.imshow(pivot.values, cmap="RdYlGn", vmin=0, vmax=1, aspect="auto")
        ax.set_xticks(range(len(TYPE_ORDER)))
        ax.set_xticklabels([TYPE_LABELS[t] for t in TYPE_ORDER])
        ax.set_yticks(range(len(pivot.index)))
        ax.set_yticklabels(pivot.index)
        ax.set_title(MODEL_LABELS[model])
        for i in range(pivot.shape[0]):
            for j in range(pivot.shape[1]):
                val = pivot.values[i, j]
                if not np.isnan(val):
                    ax.text(j, i, f"{val:.0%}", ha="center", va="center", fontsize=9)
    axes[0].set_ylabel("Nehézségi szint")
    fig.colorbar(im, ax=axes, label="Pontosság (tolerancián belül)", shrink=0.8)
    fig.suptitle("Pontosság nehézségi szint és diagramtípus szerint")
    fig.savefig(os.path.join(IMAGE_DIR, "chart_heatmap.png"), dpi=150, bbox_inches="tight")
    plt.close(fig)


def chart_difficulty_curve(df):
    fig, ax = plt.subplots(figsize=(7, 5))
    for model in MODEL_ORDER:
        sub = df[df.model_alias == model]
        grouped = sub.groupby("level")["tolerance_match"].mean().sort_index()
        ax.plot(grouped.index, grouped.values, "-o", label=MODEL_LABELS[model])
    ax.set_xlabel("Nehézségi szint (1 = legkönnyebb, 5 = legnehezebb)")
    ax.set_ylabel("Pontosság (tolerancián belül)")
    ax.set_ylim(0, 1.05)
    ax.set_xticks([1, 2, 3, 4, 5])
    ax.set_title("Degradációs görbe: pontosság a nehézségi szint függvényében")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.savefig(os.path.join(IMAGE_DIR, "chart_difficulty_curve.png"), dpi=150, bbox_inches="tight")
    plt.close(fig)


def chart_by_kind(df):
    pivot = df.groupby(["question_kind", "model_alias"])["tolerance_match"].mean().unstack()
    pivot = pivot.reindex(index=KIND_ORDER, columns=MODEL_ORDER)
    fig, ax = plt.subplots(figsize=(8, 5))
    x = np.arange(len(KIND_ORDER))
    width = 0.8 / len(MODEL_ORDER)
    for i, model in enumerate(MODEL_ORDER):
        ax.bar(x + i * width, pivot[model].values, width, label=MODEL_LABELS[model])
    ax.set_xticks(x + width * (len(MODEL_ORDER) - 1) / 2)
    ax.set_xticklabels([KIND_LABELS[k] for k in KIND_ORDER])
    ax.set_ylabel("Pontosság (tolerancián belül)")
    ax.set_ylim(0, 1.05)
    ax.set_title("Pontosság kérdéstípusonként")
    ax.legend()
    fig.savefig(os.path.join(IMAGE_DIR, "chart_by_kind.png"), dpi=150, bbox_inches="tight")
    plt.close(fig)


def chart_error_distribution(df):
    numeric = df[df.question_kind != "extremum"].copy()

    def rel_error(row):
        m = re.search(r"-?\d+(?:[.,]\d+)?", str(row["given_answer"]))
        if not m:
            return np.nan
        given = float(m.group(0).replace(",", "."))
        expected = float(row["expected_answer"])
        if expected == 0:
            return np.nan
        return (given - expected) / abs(expected) * 100

    numeric["rel_error_pct"] = numeric.apply(rel_error, axis=1)
    wrong = numeric[(numeric.tolerance_match == 0) & numeric.rel_error_pct.notna()]
    wrong = wrong[wrong.rel_error_pct.abs() < 200]

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.hist(wrong["rel_error_pct"], bins=30, color="#e34948", edgecolor="white")
    ax.axvline(0, color="#0b0b0b", linewidth=1)
    ax.set_xlabel("Relatív hiba (%), negatív: alulbecsülte, pozitív: túlbecsülte")
    ax.set_ylabel("Előfordulások száma")
    ax.set_title("Hibaeloszlás a tolerancián kívül eső numerikus válaszoknál")
    fig.savefig(os.path.join(IMAGE_DIR, "chart_error_distribution.png"), dpi=150, bbox_inches="tight")
    plt.close(fig)


def chart_human_vs_ai(df, human_df):
    no_agg = df[df.question_kind != "aggregate"]
    fig, ax = plt.subplots(figsize=(7, 5))
    for model in MODEL_ORDER:
        sub = no_agg[no_agg.model_alias == model]
        grouped = sub.groupby("level")["tolerance_match"].mean().sort_index()
        ax.plot(grouped.index, grouped.values, "-o", label=MODEL_LABELS[model])
    human_grouped = human_df.groupby("level")["tolerance_match"].mean().sort_index()
    ax.plot(human_grouped.index, human_grouped.values, "-o", label="Ember",
            color="black", linewidth=2.5, markersize=7)
    ax.set_xlabel("Nehézségi szint (1 = legkönnyebb, 5 = legnehezebb)")
    ax.set_ylabel("Pontosság (tolerancián belül)")
    ax.set_ylim(0, 1.05)
    ax.set_xticks([1, 2, 3, 4, 5])
    ax.set_title("Ember vs. AI, azonos 3 kérdéstípuson (átlag-kérdés nélkül)")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.savefig(os.path.join(IMAGE_DIR, "chart_human_vs_ai.png"), dpi=150, bbox_inches="tight")
    plt.close(fig)


def chart_text_vs_image(df_all):
    sub = df_all[(df_all.level.isin([4, 5])) & (df_all.repeat.isin([1, 2]))]
    pivot = sub.groupby(["model_alias", "condition"])["tolerance_match"].mean().unstack()
    pivot = pivot.reindex(index=MODEL_ORDER, columns=["image", "text"])

    fig, ax = plt.subplots(figsize=(7, 5))
    x = np.arange(len(MODEL_ORDER))
    width = 0.35
    ax.bar(x - width / 2, pivot["image"].values, width, label="Kép (diagram)", color="#2a78d6")
    ax.bar(x + width / 2, pivot["text"].values, width, label="Szöveges táblázat", color="#eb6834")
    ax.set_xticks(x)
    ax.set_xticklabels([MODEL_LABELS[m] for m in MODEL_ORDER])
    ax.set_ylabel("Pontosság (tolerancián belül)")
    ax.set_ylim(0, 1.05)
    ax.set_title("Kép vs. szöveges táblázat ugyanazon adaton (4-5. szint)")
    ax.legend()
    fig.savefig(os.path.join(IMAGE_DIR, "chart_text_vs_image.png"), dpi=150, bbox_inches="tight")
    plt.close(fig)
    return pivot


def print_summary(df):
    print("\n### Összefoglaló modellenként\n")
    print("| Modell | Tolerancián belül | Egzakt |")
    print("|---|---|---|")
    for model in MODEL_ORDER:
        sub = df[df.model_alias == model]
        print(f"| {MODEL_LABELS[model]} | {sub.tolerance_match.mean():.1%} | {sub.exact_match.mean():.1%} |")

    print("\n### Pontosság nehézségi szintenként (minden modell átlaga)\n")
    print("| Szint | Tolerancián belül |")
    print("|---|---|")
    for level, grp in df.groupby("level"):
        print(f"| {level} | {grp.tolerance_match.mean():.1%} |")

    print("\n### Pontosság diagramtípusonként\n")
    for t, grp in df.groupby("chart_type"):
        print(f"| {TYPE_LABELS[t]} | {grp.tolerance_match.mean():.1%} |")


def main():
    df, df_all = load()
    human_df = load_human()
    chart_heatmap(df)
    chart_difficulty_curve(df)
    chart_by_kind(df)
    chart_error_distribution(df)
    pivot = chart_text_vs_image(df_all)
    chart_human_vs_ai(df, human_df)
    print(f"6 ábra elmentve: {IMAGE_DIR}")
    print_summary(df)
    print("\n### Kép vs. szöveges táblázat (4-5. szint, azonos adaton)\n")
    print("| Modell | Kép | Szöveges táblázat |")
    print("|---|---|---|")
    for model in MODEL_ORDER:
        print(f"| {MODEL_LABELS[model]} | {pivot.loc[model, 'image']:.1%} | {pivot.loc[model, 'text']:.1%} |")

    no_agg = df[df.question_kind != "aggregate"]
    print("\n### Ember vs. AI, azonos 3 kérdéstípuson\n")
    print("| Kiértékelő | Tolerancián belül | Egzakt |")
    print("|---|---|---|")
    print(f"| Ember | {human_df.tolerance_match.mean():.1%} | {human_df.exact_match.mean():.1%} |")
    for model in MODEL_ORDER:
        sub = no_agg[no_agg.model_alias == model]
        print(f"| {MODEL_LABELS[model]} | {sub.tolerance_match.mean():.1%} | {sub.exact_match.mean():.1%} |")

    print("\n### Ember vs. AI szintenként (tolerancián belül)\n")
    print("| Szint | Ember | AI-modellek átlaga |")
    print("|---|---|---|")
    for level, grp in human_df.groupby("level"):
        ai_grp = no_agg[no_agg.level == level]
        print(f"| {level} | {grp.tolerance_match.mean():.1%} | {ai_grp.tolerance_match.mean():.1%} |")

    print("\n### Ember vs. AI kérdéstípusonként (tolerancián belül)\n")
    print("| Kérdéstípus | Ember | AI-modellek átlaga |")
    print("|---|---|---|")
    for kind in ["exact_value", "difference", "extremum"]:
        h = human_df[human_df.question_kind == kind]
        a = no_agg[no_agg.question_kind == kind]
        print(f"| {KIND_LABELS[kind]} | {h.tolerance_match.mean():.1%} | {a.tolerance_match.mean():.1%} |")

    print("\n### Ember vs. AI diagramtípusonként (tolerancián belül)\n")
    print("| Diagramtípus | Ember | AI-modellek átlaga |")
    print("|---|---|---|")
    for t in TYPE_ORDER:
        h = human_df[human_df.chart_type == t]
        a = no_agg[no_agg.chart_type == t]
        print(f"| {TYPE_LABELS[t]} | {h.tolerance_match.mean():.1%} | {a.tolerance_match.mean():.1%} |")


if __name__ == "__main__":
    main()

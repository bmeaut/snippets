#!/usr/bin/env python3
"""A két forgatókönyv results.csv-jéből összesítő táblákat és ábrákat készít az
index.md-hez. Futtatás: python3 analyze.py (a snippet gyökeréből).
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
IMAGE = HERE / "image"
IMAGE.mkdir(exist_ok=True)

BLUE = "#2a78d6"    # skill
ORANGE = "#eb6834"  # noskill
GRID = "#e1e0d9"
INK = "#0b0b0b"
MUTED = "#898781"
SURFACE = "#fcfcfb"

FULL_GRID_MODELS = ["haiku", "sonnet"]
COMPARISON_MODELS = ["opus", "sonnet_elozo"]
CONDITION_COLOR = {"skill": BLUE, "noskill": ORANGE}
CONDITION_LABEL = {"skill": "skill", "noskill": "skill nélkül"}


def style_ax(ax):
    ax.set_facecolor(SURFACE)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(GRID)
    ax.spines["bottom"].set_color(GRID)
    ax.tick_params(colors=MUTED)
    ax.yaxis.grid(True, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)


def load_budget():
    df = pd.read_csv(DATA / "budget" / "results.csv")
    df["fully_correct"] = df["category_totals_correct"] & df["balance_correct"]
    return df


def load_citations():
    df = pd.read_csv(DATA / "citations" / "results.csv")
    task_level = df.groupby(["task_id", "level", "repeat", "condition", "model_alias"]).agg(
        all_formatting=("formatting_correct", "all"),
        formatting_rate=("formatting_correct", "mean"),
        order_correct=("order_correct", "first"),
        completeness_correct=("completeness_correct", "first"),
    ).reset_index()
    task_level["fully_correct"] = (
        task_level["all_formatting"] & task_level["order_correct"] & task_level["completeness_correct"]
    )
    return task_level


def line_chart_by_level(df, models, title, out_path, metric="fully_correct", ylabel="teljesen helyes válasz (%)"):
    fig, axes = plt.subplots(1, len(models), figsize=(5.5 * len(models), 4), sharey=True)
    if len(models) == 1:
        axes = [axes]
    for ax, model in zip(axes, models):
        sub = df[df["model_alias"] == model]
        agg = sub.groupby(["level", "condition"])[metric].mean().reset_index()
        for condition in ("skill", "noskill"):
            row = agg[agg["condition"] == condition].sort_values("level")
            if row.empty:
                continue
            ax.plot(row["level"], row[metric] * 100, marker="o", linewidth=2,
                    markersize=6, color=CONDITION_COLOR[condition], label=CONDITION_LABEL[condition])
        style_ax(ax)
        ax.set_title(model, color=INK, fontsize=12)
        ax.set_xlabel("nehézségi szint", color=MUTED)
        ax.set_xticks([1, 2, 3, 4, 5])
        ax.set_ylim(-5, 105)
    axes[0].set_ylabel(ylabel, color=INK)
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, frameon=False, loc="lower center", ncol=2)
    fig.suptitle(title, color=INK, fontsize=13)
    fig.patch.set_facecolor(SURFACE)
    fig.tight_layout(rect=[0, 0.07, 1, 1])
    fig.savefig(out_path, dpi=150, facecolor=SURFACE)
    plt.close(fig)


def bar_chart_comparison_sample(df, models, title, out_path, metric="fully_correct",
                                 ylabel="teljesen helyes válasz (%), 5. szint"):
    sub = df[(df["model_alias"].isin(models)) & (df["level"] == 5)]
    agg = sub.groupby(["model_alias", "condition"])[metric].mean().reset_index()
    fig, ax = plt.subplots(figsize=(5.5, 4))
    width = 0.35
    x = range(len(models))
    for i, condition in enumerate(("skill", "noskill")):
        vals = []
        for m in models:
            row = agg[(agg["model_alias"] == m) & (agg["condition"] == condition)]
            vals.append(row[metric].values[0] * 100 if not row.empty else 0)
        offset = (i - 0.5) * width
        ax.bar([xi + offset for xi in x], vals, width=width, color=CONDITION_COLOR[condition],
               label=CONDITION_LABEL[condition])
    style_ax(ax)
    ax.set_xticks(list(x))
    ax.set_xticklabels(models, color=INK)
    ax.set_ylabel(ylabel, color=INK)
    ax.set_ylim(0, 125)
    ax.set_yticks([0, 20, 40, 60, 80, 100])
    ax.legend(frameon=False, loc="upper center", ncol=2)
    ax.set_title(title, color=INK, fontsize=13)
    fig.patch.set_facecolor(SURFACE)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150, facecolor=SURFACE)
    plt.close(fig)


def write_summary_tables(budget, citations):
    lines = ["# Összesítő táblák (analyze.py generálta)\n"]
    lines.append("\n## Költségvetés-táblázat\n")
    agg = (budget.groupby(["level", "condition", "model_alias"])["fully_correct"]
           .mean().mul(100).round(1).reset_index())
    lines.append(agg.to_markdown(index=False))
    lines.append("\n")
    lines.append("\n## Hivatkozásjegyzék\n")
    agg = (citations.groupby(["level", "condition", "model_alias"])[["fully_correct", "formatting_rate"]]
           .mean().mul(100).round(1).reset_index())
    lines.append(agg.to_markdown(index=False))
    lines.append("\n")
    (HERE / "data" / "summary_tables.md").write_text("\n".join(lines), encoding="utf-8")


def main():
    budget = load_budget()
    citations = load_citations()

    line_chart_by_level(budget, FULL_GRID_MODELS, "Költségvetés-táblázat — teljesen helyes válasz aránya",
                         IMAGE / "budget_full_grid.png")
    bar_chart_comparison_sample(budget, COMPARISON_MODELS, "Költségvetés-táblázat — összevető minta (5. szint)",
                                 IMAGE / "budget_comparison_sample.png")
    line_chart_by_level(citations, FULL_GRID_MODELS, "Hivatkozásjegyzék — hivatkozásonkénti formázási pontosság",
                         IMAGE / "citations_full_grid.png", metric="formatting_rate",
                         ylabel="formázási pontosság (%)")
    bar_chart_comparison_sample(citations, COMPARISON_MODELS, "Hivatkozásjegyzék — összevető minta (5. szint)",
                                 IMAGE / "citations_comparison_sample.png", metric="formatting_rate",
                                 ylabel="formázási pontosság (%), 5. szint")

    write_summary_tables(budget, citations)
    print("Ábrák és összesítő táblák elkészültek az image/ és data/summary_tables.md alatt.")


if __name__ == "__main__":
    main()

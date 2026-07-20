"""
AIGrader – Elemző script
Összehasonlítja az emberi értékelést a Sonnet/Opus egyenkénti és együttes AI értékelésekkel.
Használat: python analyze.py
A script ugyanabban a mappában keres minden JSON fájlt ahol fut.
"""

import json
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import spearmanr

BASE = os.path.dirname(os.path.abspath(__file__))

def load_json(filename):
    with open(os.path.join(BASE, filename), encoding="utf-8") as f:
        return json.load(f)

CRITERIA = [
    "compact_operation", "detailed_functionality", "roles_and_permissions",
    "communication", "data_management_and_architecture", "architecture",
    "maintainability", "error_handling", "quality_and_reliability",
    "ui_and_ux", "mobility", "deployment_documentation",
    "repository_structure", "innovation"
]

HUMAN = {
    "Eper":     {"compact_operation":5,"detailed_functionality":4,"roles_and_permissions":5,"communication":5,"data_management_and_architecture":5,"architecture":6,"maintainability":10,"error_handling":2,"quality_and_reliability":5,"ui_and_ux":2,"mobility":0,"deployment_documentation":5,"repository_structure":5,"innovation":2},
    "Kivi":     {"compact_operation":8,"detailed_functionality":9,"roles_and_permissions":5,"communication":10,"data_management_and_architecture":4,"architecture":10,"maintainability":8,"error_handling":4,"quality_and_reliability":5,"ui_and_ux":3,"mobility":5,"deployment_documentation":5,"repository_structure":5,"innovation":4},
    "Barack":   {"compact_operation":9,"detailed_functionality":8,"roles_and_permissions":5,"communication":10,"data_management_and_architecture":5,"architecture":9,"maintainability":9,"error_handling":5,"quality_and_reliability":4.5,"ui_and_ux":4,"mobility":8,"deployment_documentation":5,"repository_structure":5,"innovation":4},
    "Datolya":  {"compact_operation":10,"detailed_functionality":9,"roles_and_permissions":5,"communication":10,"data_management_and_architecture":5,"architecture":9,"maintainability":8,"error_handling":4,"quality_and_reliability":5,"ui_and_ux":5,"mobility":7,"deployment_documentation":4,"repository_structure":5,"innovation":5},
    "Szilva":   {"compact_operation":6,"detailed_functionality":4,"roles_and_permissions":4,"communication":9,"data_management_and_architecture":4,"architecture":7,"maintainability":5,"error_handling":4,"quality_and_reliability":1,"ui_and_ux":2,"mobility":6,"deployment_documentation":3,"repository_structure":5,"innovation":2},
    "Alma":     {"compact_operation":7,"detailed_functionality":9,"roles_and_permissions":5,"communication":10,"data_management_and_architecture":5,"architecture":9,"maintainability":8,"error_handling":4,"quality_and_reliability":5,"ui_and_ux":4,"mobility":6,"deployment_documentation":5,"repository_structure":5,"innovation":4},
    "Citrom":   {"compact_operation":6,"detailed_functionality":5,"roles_and_permissions":5,"communication":6,"data_management_and_architecture":3,"architecture":6.5,"maintainability":8,"error_handling":3,"quality_and_reliability":4,"ui_and_ux":2,"mobility":6,"deployment_documentation":5,"repository_structure":5,"innovation":2},
}

def to_df(data):
    return pd.DataFrame({d["student"]: {c: d[c] for c in CRITERIA} for d in data}).T

sonnet_ind = to_df(load_json("data/sonet.json"))
sonnet_all = to_df(load_json("data/sonet_all.json"))
opus_ind   = to_df(load_json("data/opus.json"))
opus_all   = to_df(load_json("data/opus_all.json"))
human_df   = pd.DataFrame(HUMAN).T

def total(df):
    return df[CRITERIA].sum(axis=1)

totals = pd.DataFrame({
    "Emberi":            total(human_df),
    "Sonnet egyenkénti": total(sonnet_ind),
    "Sonnet együttes":   total(sonnet_all),
    "Opus egyenkénti":   total(opus_ind),
    "Opus együttes":     total(opus_all),
})

ranks = totals.rank(ascending=False).astype(int)
students = sorted(human_df.index.tolist())
methods = totals.columns.tolist()
colors = ["#333333", "#2196F3", "#90CAF9", "#E91E63", "#F48FB1"]

# ── 1. Összpontszám oszlopdiagram ─────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(10, 5))
x = np.arange(len(students))
w = 0.16
for i, (method, color) in enumerate(zip(methods, colors)):
    ax.bar(x + (i - 2) * w, totals.loc[students, method], w, label=method, color=color)
ax.set_xticks(x)
ax.set_xticklabels(students, fontsize=10)
ax.set_ylabel("Összpontszám")
ax.set_title("Összpontszámok módszerenként", fontsize=13, fontweight="bold")
ax.legend(fontsize=9)
ax.set_ylim(40, 100)
ax.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(BASE, "image", "chart_scores.png"), dpi=150, bbox_inches="tight")
plt.close()
print("Mentve: chart_scores.png")

# ── 2. Rangsor diagram ────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(10, 5))
for method, color in zip(methods, colors):
    lw = 3 if method == "Emberi" else 1.5
    ls = "-" if method == "Emberi" else "--"
    ax.plot(students, ranks.loc[students, method], marker="o", label=method,
            color=color, linewidth=lw, linestyle=ls, markersize=7,
            zorder=10 if method == "Emberi" else 5)
ax.set_yticks(range(1, len(students) + 1))
ax.set_yticklabels([f"{i}. hely" for i in range(1, len(students) + 1)])
ax.invert_yaxis()
ax.set_title("Verseny rangsor – emberi vs AI", fontsize=13, fontweight="bold")
ax.legend(fontsize=9)
ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(BASE, "image", "chart_ranks.png"), dpi=150, bbox_inches="tight")
plt.close()
print("Mentve: chart_ranks.png")

# ── 3. Rangsor-táblázat (ki hányadik helyre került módszerenként) ──────────────
# Minden módszerhez a diákok sorrendje összpontszám szerint csökkenően:
# az 1. sor a győztes, az utolsó sor az utolsó helyezett.
rank_table = pd.DataFrame(
    {method: totals[method].sort_values(ascending=False).index.tolist() for method in methods},
    index=[f"{i}. hely" for i in range(1, len(students) + 1)],
)

rank_table.to_csv(os.path.join(BASE, "data", "rank_table.csv"), encoding="utf-8")
print("Mentve: rank_table.csv")

# ── F1-stílusú helyezés-változás a referencia rangsorhoz képest ────────────────
# REFERENCE = a "rajtrács" (mint az F1 pole/grid). Minden modell ehhez képest
# mutatja, ki csúszott feljebb (zöld ▲) vagy lejjebb (piros ▼) és hány hellyel.
REFERENCE = "Emberi"
ARROW_UP, ARROW_DOWN, ARROW_FLAT = "▲", "▼", "—"

# helyezések módszerenként: {method: {student: pozíció}}
positions = {m: {s: i + 1 for i, s in enumerate(totals[m].sort_values(ascending=False).index)}
             for m in methods}
ref_pos = positions[REFERENCE]

def delta(method, student):
    """+ = a referenciához képest feljebb, - = lejjebb."""
    return ref_pos[student] - positions[method][student]

def cell_label(method, student):
    if method == REFERENCE:
        return student
    d = delta(method, student)
    if d > 0:
        return f"{student}  {ARROW_UP}{d}"
    if d < 0:
        return f"{student}  {ARROW_DOWN}{abs(d)}"
    return f"{student}  {ARROW_FLAT}"

def cell_color(method, student):
    if method == REFERENCE:
        return "white"
    d = delta(method, student)
    if d > 0:
        return "#C8E6C9"   # zöld – feljebb
    if d < 0:
        return "#FFCDD2"   # piros – lejjebb
    return "#F5F5F5"       # szürke – változatlan

# konzol: rangsor a változás-nyilakkal
rank_table_display = pd.DataFrame(
    {m: [cell_label(m, rank_table.loc[idx, m]) for idx in rank_table.index] for m in methods},
    index=rank_table.index,
)
print(f"\nRangsor-táblázat (▲/▼ a(z) '{REFERENCE}' rangsorhoz képest):")
print(rank_table_display.to_string())

# Táblázat kép mentése a fel/le nyilakkal és színezéssel
cell_text = [[cell_label(m, rank_table.loc[idx, m]) for m in methods] for idx in rank_table.index]
cell_colours = [[cell_color(m, rank_table.loc[idx, m]) for m in methods] for idx in rank_table.index]

fig, ax = plt.subplots(figsize=(1.25 * len(methods) + 1.5, 0.55 * len(students) + 2))
ax.axis("off")
# a fejlécben a szavak külön sorba törve, hogy ne lógjanak ki
col_labels = [m.replace(" ", "\n") for m in methods]
tbl = ax.table(
    cellText=cell_text,
    cellColours=cell_colours,
    rowLabels=rank_table.index,
    colLabels=col_labels,
    cellLoc="center",
    loc="center",
)
tbl.auto_set_font_size(False)
tbl.set_fontsize(10)
tbl.scale(1, 1.6)
for (row, col), cell in tbl.get_celld().items():
    if row == 0:  # fejléc (módszerek) – a diagramokkal egyező színekkel
        cell.set_height(cell.get_height() * 1.6)  # több hely a kétsoros fejlécnek
        cell.set_facecolor(colors[col] if 0 <= col < len(colors) else "#666666")
        cell.set_text_props(color="white", fontweight="bold")
    elif col == -1:  # sorcímke (helyezés)
        cell.set_text_props(fontweight="bold")
ax.set_title(f"Helyezések módszerenként  (▲/▼ a(z) '{REFERENCE}' rangsorhoz képest)",
             fontsize=13, fontweight="bold", pad=20)
fig.text(0.5, 0.02, "▲ zöld = feljebb csúszott    ▼ piros = lejjebb csúszott    — = változatlan",
         ha="center", fontsize=9, color="#555555")
plt.tight_layout()
plt.savefig(os.path.join(BASE, "image", "chart_rank_table.png"), dpi=150, bbox_inches="tight")
plt.close()
print("Mentve: chart_rank_table.png")

# ── Spearman-korreláció kiírása ───────────────────────────────────────────────
print("\nSpearman rangsor-korreláció (Human vs AI):")
h = total(human_df)
for method, series in [("Sonnet egyenkénti", total(sonnet_ind)),
                       ("Sonnet együttes",   total(sonnet_all)),
                       ("Opus egyenkénti",   total(opus_ind)),
                       ("Opus együttes",     total(opus_all))]:
    rho, pval = spearmanr(h, series)
    print(f"  {method:<22} rho = {rho:.3f}  (p = {pval:.3f})")

# ══════════════════════════════════════════════════════════════════════════════
#  KRITÉRIUM-SZINTŰ ELEMZÉSEK (14 szempont)
# ══════════════════════════════════════════════════════════════════════════════
ai_methods = {
    "Sonnet egyenkénti": sonnet_ind,
    "Sonnet együttes":   sonnet_all,
    "Opus egyenkénti":   opus_ind,
    "Opus együttes":     opus_all,
}
ai_colors = ["#2196F3", "#90CAF9", "#E91E63", "#F48FB1"]  # a fő diagramokkal egyező
crit_labels = [c.replace("_", " ") for c in CRITERIA]
H = human_df.loc[students, CRITERIA].astype(float)

# előjeles átlageltérés szempontonként × módszerenként (AI − Emberi)
diff = pd.DataFrame({
    name: (df.loc[students, CRITERIA].astype(float) - H).mean(axis=0)
    for name, df in ai_methods.items()
})  # index = CRITERIA, oszlopok = módszerek

# ── 4. Kritérium-hőtérkép: hol és mennyivel tér el az AI az embertől ───────────
fig, ax = plt.subplots(figsize=(7, 8))
vmax = np.nanmax(np.abs(diff.values))
im = ax.imshow(diff.values, cmap="RdYlGn", vmin=-vmax, vmax=vmax, aspect="auto")
ax.set_xticks(range(len(ai_methods)))
ax.set_xticklabels([m.replace(" ", "\n") for m in ai_methods], fontsize=9)
ax.set_yticks(range(len(CRITERIA)))
ax.set_yticklabels(crit_labels, fontsize=9)
for i in range(len(CRITERIA)):
    for j in range(len(ai_methods)):
        ax.text(j, i, f"{diff.values[i, j]:+.1f}", ha="center", va="center",
                fontsize=8, color="#222222")
ax.set_title("Átlagos eltérés az emberitől szempontonként\n(zöld = AI többet ad, piros = AI kevesebbet ad)",
             fontsize=12, fontweight="bold")
fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04, label="AI − Emberi (pont)")
plt.tight_layout()
plt.savefig(os.path.join(BASE, "image", "chart_heatmap.png"), dpi=150, bbox_inches="tight")
plt.close()
print("\nMentve: chart_heatmap.png")

# ── 5. Szisztematikus elfogultság: mit pontoz az AI átlagosan túl/alul ─────────
mean_bias = diff.mean(axis=1).sort_values()  # szempontonkénti átlag a 4 módszerre
fig, ax = plt.subplots(figsize=(8, 6))
bar_colors = ["#C62828" if v < 0 else "#2E7D32" for v in mean_bias.values]
ax.barh([c.replace("_", " ") for c in mean_bias.index], mean_bias.values, color=bar_colors)
ax.axvline(0, color="#333333", linewidth=0.8)
ax.set_xlabel("Átlagos eltérés az emberitől (pont)  –  négy AI módszer átlaga")
ax.set_title("Szisztematikus elfogultság szempontonként\n(piros = AI szigorúbb, zöld = AI elnézőbb)",
             fontsize=12, fontweight="bold")
ax.grid(axis="x", alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(BASE, "image", "chart_bias.png"), dpi=150, bbox_inches="tight")
plt.close()
print("Mentve: chart_bias.png")
print("\nLegszigorúbb szempontok (AI alulpontoz):")
for c, v in mean_bias.head(3).items():
    print(f"  {c.replace('_', ' '):<35} {v:+.2f} pont")
print("Legelnézőbb szempontok (AI túlpontoz):")
for c, v in mean_bias.tail(3)[::-1].items():
    print(f"  {c.replace('_', ' '):<35} {v:+.2f} pont")

# ── 6. Pontossági rangsor: melyik modell áll legközelebb az emberihez ─────────
print("\nPontossági rangsor (cellánkénti eltérés az emberitől):")
acc = {}
for name, df in ai_methods.items():
    d = (df.loc[students, CRITERIA].astype(float) - H).values
    acc[name] = (np.abs(d).mean(), np.sqrt((d ** 2).mean()))
acc = dict(sorted(acc.items(), key=lambda kv: kv[1][0]))  # MAE szerint növekvő
for name, (mae, rmse) in acc.items():
    print(f"  {name:<22} MAE = {mae:.2f}   RMSE = {rmse:.2f}")

fig, ax = plt.subplots(figsize=(8, 5))
names = list(acc.keys())
maes = [acc[n][0] for n in names]
ax.bar(range(len(names)), maes, color=ai_colors, width=0.6)
for i, v in enumerate(maes):
    ax.text(i, v + 0.02, f"{v:.2f}", ha="center", fontsize=10, fontweight="bold")
ax.set_xticks(range(len(names)))
ax.set_xticklabels([n.replace(" ", "\n") for n in names], fontsize=9)
ax.set_ylabel("Átlagos abszolút eltérés (MAE, pont)")
ax.set_title("Melyik modell áll legközelebb az emberi pontozáshoz?\n(kisebb = pontosabb)",
             fontsize=12, fontweight="bold")
ax.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(BASE, "image", "chart_accuracy.png"), dpi=150, bbox_inches="tight")
plt.close()
print("Mentve: chart_accuracy.png")

# ── 7. Egyenkénti vs együttes: változik-e a pontozás, ha egyben látja ─────────
change = pd.DataFrame({
    "Sonnet": (sonnet_all.loc[students, CRITERIA].astype(float)
               - sonnet_ind.loc[students, CRITERIA].astype(float)).mean(axis=0),
    "Opus":   (opus_all.loc[students, CRITERIA].astype(float)
               - opus_ind.loc[students, CRITERIA].astype(float)).mean(axis=0),
})  # + = az együttes értékelés többet ad, mint az egyenkénti
y = np.arange(len(CRITERIA))
fig, ax = plt.subplots(figsize=(8, 7))
ax.barh(y - 0.2, change["Sonnet"].values, height=0.4, label="Sonnet", color="#2196F3")
ax.barh(y + 0.2, change["Opus"].values,   height=0.4, label="Opus",   color="#E91E63")
ax.axvline(0, color="#333333", linewidth=0.8)
ax.set_yticks(y)
ax.set_yticklabels(crit_labels, fontsize=9)
ax.invert_yaxis()
ax.set_xlabel("Együttes − egyenkénti pontozás (pont)")
ax.set_title("Változik-e a pontozás, ha a modell egyben látja a beadványokat?\n(+ = az együttes több pontot ad)",
             fontsize=12, fontweight="bold")
ax.legend(fontsize=9)
ax.grid(axis="x", alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(BASE, "image", "chart_ind_vs_all.png"), dpi=150, bbox_inches="tight")
plt.close()
print("Mentve: chart_ind_vs_all.png")
print("\nÁtlagos eltérés egyenkénti → együttes (összes szempont átlaga):")
print(f"  Sonnet: {change['Sonnet'].mean():+.2f} pont/szempont")
print(f"  Opus:   {change['Opus'].mean():+.2f} pont/szempont")

# ── 8. Összesítő ábra (aigrader_results.png) – hallgatónkénti bontásban ───────
fig, axes = plt.subplots(2, 2, figsize=(18, 14))
fig.suptitle("AIGrader – Emberi vs AI értékelés összehasonlítása", fontsize=16)

panel_names = ["Sonnet_Ind", "Sonnet_All", "Opus_Ind", "Opus_All"]
panel_dfs = [sonnet_ind, sonnet_all, opus_ind, opus_all]

ax = axes[0, 0]
xs = np.arange(len(students))
w = 0.15
ax.bar(xs - 2 * w, total(human_df).loc[students], w, label="Human")
for i, (name, df) in enumerate(zip(panel_names, panel_dfs)):
    ax.bar(xs + (i - 1) * w, total(df).loc[students], w, label=name)
ax.set_xticks(xs)
ax.set_xticklabels(students)
ax.set_ylabel("Pont")
ax.set_title("Összesített pontszámok")
ax.legend()

def diff_heatmap(ax, ai_df, title):
    d = (ai_df.loc[students, CRITERIA].astype(float)
         - human_df.loc[students, CRITERIA].astype(float)).round(0).T
    vmin, vmax = d.values.min(), d.values.max()
    im = ax.imshow(d.values, cmap="RdYlGn", vmin=vmin, vmax=vmax, aspect="auto")
    ax.set_xticks(range(len(students)))
    ax.set_xticklabels(students)
    ax.set_yticks(range(len(CRITERIA)))
    ax.set_yticklabels(CRITERIA)
    for i in range(len(CRITERIA)):
        for j in range(len(students)):
            ax.text(j, i, f"{int(d.values[i, j])}", ha="center", va="center", fontsize=8)
    ax.set_title(title)
    fig.colorbar(im, ax=ax)

diff_heatmap(axes[0, 1], sonnet_ind, "Sonnet egyenkénti – eltérés kritériumonként")
diff_heatmap(axes[1, 0], opus_ind, "Opus egyenkénti – eltérés kritériumonként")

ax = axes[1, 1]
abs_diff = pd.DataFrame({
    name: (df.loc[students, CRITERIA].astype(float)
           - human_df.loc[students, CRITERIA].astype(float)).abs().sum(axis=1)
    for name, df in zip(panel_names, panel_dfs)
})
w = 0.2
for i, name in enumerate(panel_names):
    ax.bar(xs + (i - 1.5) * w, abs_diff.loc[students, name], w, label=name)
ax.set_xticks(xs)
ax.set_xticklabels(students)
ax.set_ylabel("Pont")
ax.set_title("Összes abszolút eltérés hallgatónként")
ax.legend()

plt.tight_layout()
plt.savefig(os.path.join(BASE, "image", "aigrader_results.png"), dpi=110, bbox_inches="tight")
plt.close()
print("Mentve: aigrader_results.png")
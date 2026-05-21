import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import re
from pathlib import Path
from collections import defaultdict
from sklearn.cluster import KMeans

OUT_DIR = Path("figures")
data    = json.load(open("figures/colors.json"))

BG = "#0f0f0f"

BRANDS = {
    "bv": "Bottega Veneta",
    "lv": "Louis Vuitton",
}

# Ères pour annotations
ERAS = {
    "bv": [
        (2010, 2018, "Tomas Maier"),
        (2019, 2021, "Daniel Lee"),
        (2022, 2026, "Matthieu Blazy"),
    ],
    "lv": [
        (2010, 2013, "Marc Jacobs"),
        (2014, 2026, "Nicolas Ghesquière"),
    ],
}

def extract_year(collection: str):
    m = re.search(r"(20\d{2})", collection)
    return int(m.group(1)) if m else None

def dominant_color(colors: list) -> list:
    """Couleur dominante d'un groupe d'images."""
    arr = np.array(colors, dtype=float)
    if len(arr) == 0:
        return [128, 128, 128]
    if len(arr) < 3:
        return arr.mean(axis=0).astype(int).tolist()
    km = KMeans(n_clusters=3, n_init=3, random_state=42)
    km.fit(arr)
    order = np.argsort(-np.bincount(km.labels_))
    return km.cluster_centers_[order[0]].astype(int).tolist()

# ── Agrégation par marque + année ───────────────────────────────────────
brand_year_colors = defaultdict(lambda: defaultdict(list))
for item in data:
    year = extract_year(item["collection"])
    if year and item["brand"] in BRANDS:
        brand_year_colors[item["brand"]][year].extend(item["colors"])

# Couleur dominante par (marque, année)
brand_year_dom = {}
for brand in BRANDS:
    brand_year_dom[brand] = {}
    for year, colors in sorted(brand_year_colors[brand].items()):
        brand_year_dom[brand][year] = dominant_color(colors)

# ── Figure ───────────────────────────────────────────────────────────────
fig, axes = plt.subplots(2, 1, figsize=(16, 6), gridspec_kw={"hspace": 0.5})
fig.patch.set_facecolor(BG)

for ax, (brand, label) in zip(axes, BRANDS.items()):
    ax.set_facecolor(BG)
    years_data = brand_year_dom[brand]
    years      = sorted(years_data.keys())

    # Barre colorée par année
    for yr in years:
        rgb   = years_data[yr]
        color = [c/255 for c in rgb]
        ax.bar(yr, 1, width=0.85, color=color, edgecolor="none")

    # Annotations ères créatives
    era_list = ERAS[brand]
    for (y_start, y_end, name) in era_list:
        # Rectangle semi-transparent
        ax.axvspan(y_start - 0.5, min(y_end, max(years)) + 0.5,
                   alpha=0.07, color="white")
        # Nom du DA
        mid = (y_start + min(y_end, max(years))) / 2
        ax.text(mid, 1.08, name,
                ha="center", va="bottom",
                color="#aaaaaa", fontsize=8.5, style="italic")
        # Ligne de séparation entre ères
        if y_start > min(years):
            ax.axvline(y_start - 0.5, color="#444444",
                       linewidth=1, linestyle="--")

    ax.set_xlim(min(years) - 0.7, max(years) + 0.7)
    ax.set_ylim(0, 1.25)
    ax.set_xticks(years)
    ax.set_xticklabels([str(y) for y in years],
                       color="white", fontsize=8, rotation=45)
    ax.set_yticks([])
    ax.set_title(label, color="white", fontsize=11, pad=18)
    for spine in ax.spines.values():
        spine.set_visible(False)

fig.suptitle(
    "Évolution de la couleur dominante par saison — BV vs LV (2010–2026)",
    fontsize=13, color="white", y=1.02
)

out = OUT_DIR / "timeline_colors.png"
plt.savefig(out, dpi=180, bbox_inches="tight", facecolor=BG)
print(f"Figure sauvegardée → {out}")

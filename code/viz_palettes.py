import json
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from collections import defaultdict
from sklearn.cluster import KMeans

OUT_DIR = Path("figures")
data    = json.load(open("figures/colors.json"))

ERA_ORDER = [
    "BV — Tomas Maier",
    "BV — Daniel Lee",
    "BV — Matthieu Blazy",
    "LV — Marc Jacobs",
    "LV — Nicolas Ghesquière",
]

BG = "#0f0f0f"

# ── Agrégation couleurs par ère ─────────────────────────────────────────
era_colors = defaultdict(list)
for item in data:
    if item["era"] in ERA_ORDER:
        era_colors[item["era"]].extend(item["colors"])

def get_palette(colors, n=8):
    arr = np.array(colors, dtype=float)
    km  = KMeans(n_clusters=n, n_init=5, random_state=42)
    km.fit(arr)
    order = np.argsort(-np.bincount(km.labels_))
    return km.cluster_centers_[order].astype(int).tolist()

print("Calcul des palettes...")
palettes = {era: get_palette(era_colors[era]) for era in ERA_ORDER}

# ── Figure ───────────────────────────────────────────────────────────────
N_ERAS   = len(ERA_ORDER)
N_COLORS = 8
ROW_H    = 0.8   # hauteur relative de chaque bande couleur
GAP      = 0.4   # espace entre les bandes
LABEL_X  = 0.18  # fraction de largeur réservée au label

fig, ax = plt.subplots(figsize=(13, 6))
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)
ax.axis("off")

total_h = N_ERAS * (ROW_H + GAP)
ax.set_xlim(0, 1)
ax.set_ylim(0, total_h)

for i, era in enumerate(ERA_ORDER):
    # y croissant = bas → on inverse pour que Tomas Maier soit en haut
    row   = N_ERAS - 1 - i
    y_bot = row * (ROW_H + GAP) + GAP / 2

    palette = palettes[era]
    n       = len(palette)
    sw      = (1 - LABEL_X) / n  # largeur d'un swatch

    for j, rgb in enumerate(palette):
        x = LABEL_X + j * sw
        ax.add_patch(plt.Rectangle(
            (x, y_bot), sw - 0.003, ROW_H,
            color=[c/255 for c in rgb],
            transform=ax.transData
        ))

    # Label
    brand, da = era.split(" — ")
    ax.text(LABEL_X - 0.02, y_bot + ROW_H / 2,
            f"{brand}  —  {da}",
            va="center", ha="right",
            color="white", fontsize=10,
            transform=ax.transData)

    # Séparateur BV / LV après Matthieu Blazy (i==2)
    if i == 2:
        sep_y = y_bot - GAP / 2
        ax.axhline(sep_y, xmin=LABEL_X, color="#666666",
                   linewidth=1, linestyle="--")

fig.suptitle(
    "Signature colorimétrique par ère créative — BV vs LV",
    fontsize=13, color="white", y=0.98
)

out = OUT_DIR / "palettes.png"
plt.savefig(out, dpi=180, bbox_inches="tight", facecolor=BG)
print(f"Figure sauvegardée → {out}")
import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import colorsys
import re
from pathlib import Path
from collections import defaultdict

OUT_DIR = Path("figures")
data    = json.load(open("figures/colors.json"))

BG = "#0f0f0f"

ERA_ORDER = [
    "BV — Tomas Maier",
    "BV — Daniel Lee",
    "BV — Matthieu Blazy",
    "LV — Marc Jacobs",
    "LV — Nicolas Ghesquière",
]

def get_era(brand, collection):
    m = re.search(r"(20\d{2})", collection)
    if not m:
        return "inconnu"
    year = int(m.group(1))
    if brand == "bv":
        if year <= 2018: return "BV — Tomas Maier"
        elif year <= 2021: return "BV — Daniel Lee"
        else: return "BV — Matthieu Blazy"
    elif brand == "lv":
        if year <= 2013: return "LV — Marc Jacobs"
        else: return "LV — Nicolas Ghesquière"
    return "inconnu"

def rgb_to_hsv(rgb):
    """Convertit [R,G,B] (0-255) en (H, S, V)."""
    r, g, b = [c/255 for c in rgb]
    return colorsys.rgb_to_hsv(r, g, b)

# ── Calcul H, S, V moyen par ère ────────────────────────────────────────
era_hsv = defaultdict(lambda: {"h": [], "s": [], "v": []})

for item in data:
    era = get_era(item["brand"], item["collection"])
    if era not in ERA_ORDER:
        continue
    for rgb in item["colors"]:
        h, s, v = rgb_to_hsv(rgb)
        era_hsv[era]["h"].append(h)
        era_hsv[era]["s"].append(s)
        era_hsv[era]["v"].append(v)

# Matrices pour la heatmap (ères × métriques)
metrics     = ["Saturation\nmoyenne", "Luminosité\nmoyenne", "Diversité\ncouleurs"]
matrix      = np.zeros((len(ERA_ORDER), len(metrics)))

for i, era in enumerate(ERA_ORDER):
    s_vals = era_hsv[era]["s"]
    v_vals = era_hsv[era]["v"]
    h_vals = era_hsv[era]["h"]

    matrix[i, 0] = np.mean(s_vals)                    # saturation
    matrix[i, 1] = np.mean(v_vals)                    # luminosité
    matrix[i, 2] = np.std(h_vals)                     # diversité (écart-type teinte)

# Normalise chaque colonne entre 0 et 1 pour la comparaison
matrix_norm = (matrix - matrix.min(axis=0)) / (matrix.max(axis=0) - matrix.min(axis=0) + 1e-8)

# ── Figure ───────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(10, 6))
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)

im = ax.imshow(matrix_norm, cmap="RdYlBu_r", aspect="auto", vmin=0, vmax=1)

# Labels axes
ax.set_xticks(range(len(metrics)))
ax.set_xticklabels(metrics, color="white", fontsize=10)
ax.set_yticks(range(len(ERA_ORDER)))
ax.set_yticklabels(ERA_ORDER, color="white", fontsize=10)

# Valeurs dans les cellules
for i in range(len(ERA_ORDER)):
    for j in range(len(metrics)):
        val_raw  = matrix[i, j]
        val_norm = matrix_norm[i, j]
        txt_color = "white" if val_norm < 0.6 else "#111111"
        ax.text(j, i, f"{val_raw:.3f}",
                ha="center", va="center",
                color=txt_color, fontsize=9.5, fontweight="bold")

# Séparateur BV / LV
ax.axhline(2.5, color="#888888", linewidth=1.2, linestyle="--")

# Colorbar
cbar = plt.colorbar(im, ax=ax, fraction=0.03, pad=0.02)
cbar.set_label("Score normalisé (0 = min, 1 = max)",
               color="white", fontsize=9)
cbar.ax.yaxis.set_tick_params(color="white")
plt.setp(cbar.ax.yaxis.get_ticklabels(), color="white")

ax.set_title(
    "Intensité colorimétrique par ère créative — BV vs LV",
    color="white", fontsize=13, pad=15
)

for spine in ax.spines.values():
    spine.set_visible(False)
ax.tick_params(colors="white", length=0)

plt.tight_layout()
out = OUT_DIR / "heatmap_colors.png"
plt.savefig(out, dpi=180, bbox_inches="tight", facecolor=BG)
print(f"Figure sauvegardée → {out}")

import json
import re
import numpy as np
from pathlib import Path
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# Chargement
with open("figures/embeddings.json") as f:
    data = json.load(f)

embeddings  = np.array([d["embedding"] for d in data])
brands      = [d["brand"] for d in data]
collections = [d["collection"] for d in data]

print(f"{len(embeddings)} embeddings chargés")


def get_era(brand: str, collection: str) -> str:
    """Retourne l'ère créative à partir du brand + slug de collection."""
    # Extrait l'année du slug (ex: "bottega-veneta-men-women-fall-winter-2022-milan")
    match = re.search(r"(20\d{2})", collection)
    if not match:
        return "inconnu"
    year = int(match.group(1))

    if brand == "bv":
        if year <= 2018:
            return "BV — Tomas Maier"
        elif year <= 2021:
            return "BV — Daniel Lee"
        else:
            return "BV — Matthieu Blazy"
    elif brand == "lv":
        if year <= 2013:
            return "LV — Marc Jacobs"
        else:
            return "LV — Nicolas Ghesquière"
    return "inconnu"


# Palette par ère créative
ERA_COLORS = {
    "BV — Tomas Maier":      "#4a4e69",   # bleu-gris foncé
    "BV — Daniel Lee":       "#9a8c98",   # mauve
    "BV — Matthieu Blazy":   "#c9ada7",   # rose poudré
    "LV — Marc Jacobs":      "#b5843a",   # or foncé
    "LV — Nicolas Ghesquière": "#f2cc8f", # or clair
    "inconnu":               "#cccccc",
}

eras = [get_era(b, c) for b, c in zip(brands, collections)]
point_colors = [ERA_COLORS[e] for e in eras]

# t-SNE
print("Calcul t-SNE...")
tsne = TSNE(n_components=2, perplexity=80, n_iter=2000, random_state=42)
coords = tsne.fit_transform(embeddings)

# Plot
fig, ax = plt.subplots(figsize=(16, 10))

ax.scatter(
    coords[:, 0], coords[:, 1],
    c=point_colors,
    s=15,
    alpha=0.65,
    edgecolors="none",
)

# Légende par ère (ordre chronologique)
legend_order = [
    "BV — Tomas Maier",
    "BV — Daniel Lee",
    "BV — Matthieu Blazy",
    "LV — Marc Jacobs",
    "LV — Nicolas Ghesquière",
]
legend_handles = [
    mpatches.Patch(color=ERA_COLORS[era], label=era)
    for era in legend_order
]
ax.legend(
    handles=legend_handles,
    loc="upper right",
    framealpha=0.92,
    fontsize=10,
    title="Directeur artistique",
    title_fontsize=10,
)

ax.set_title(
    "Espace esthétique — BV vs LV par ère créative (CLIP + t-SNE)",
    fontsize=14,
    pad=15,
)
ax.axis("off")

plt.tight_layout()
out = Path("figures/tsne.png")
plt.savefig(out, dpi=150, bbox_inches="tight")
print(f"Figure sauvegardée → {out}")
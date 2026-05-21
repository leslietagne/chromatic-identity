import json
import re
from pathlib import Path
from PIL import Image
import numpy as np
from sklearn.cluster import KMeans
from collections import defaultdict
import colorsys

def rgb_to_hsv(rgb: list) -> tuple:
    """Convertit [R, G, B] (0-255) en (H, S, V) dans [0, 1]."""
    r, g, b = [c / 255 for c in rgb]
    return colorsys.rgb_to_hsv(r, g, b)

DATA_DIR  = Path("data")
OUT_DIR   = Path("figures")
OUT_DIR.mkdir(exist_ok=True)

N_COLORS  = 5   # couleurs dominantes par image
N_SAMPLE  = 150 # pixels échantillonnés par image (rapide)


def get_dominant_colors(img_path: Path, n: int = N_COLORS) -> list[list[int]]:
    """Retourne les N couleurs dominantes d'une image via KMeans RGB."""
    img = Image.open(img_path).convert("RGB")
    img = img.resize((100, 100))  # resize pour accélérer
    pixels = np.array(img).reshape(-1, 3).astype(float)

    # Échantillonnage aléatoire pour accélérer
    if len(pixels) > N_SAMPLE:
        idx = np.random.choice(len(pixels), N_SAMPLE, replace=False)
        pixels = pixels[idx]

    kmeans = KMeans(n_clusters=n, n_init=3, random_state=42)
    kmeans.fit(pixels)

    # Trie par fréquence (cluster le plus représenté en premier)
    counts = np.bincount(kmeans.labels_)
    order  = np.argsort(-counts)
    colors = kmeans.cluster_centers_[order].astype(int).tolist()
    return colors


def get_era(brand: str, collection: str) -> str:
    match = re.search(r"(20\d{2})", collection)
    if not match:
        return "inconnu"
    year = int(match.group(1))
    if brand == "bv":
        if year <= 2018: return "BV — Tomas Maier"
        elif year <= 2021: return "BV — Daniel Lee"
        else: return "BV — Matthieu Blazy"
    elif brand == "lv":
        if year <= 2013: return "LV — Marc Jacobs"
        else: return "LV — Nicolas Ghesquière"
    return "inconnu"


def run():
    images = sorted(DATA_DIR.rglob("*.jpg"))
    print(f"{len(images)} images trouvées")

    results   = []
    errors    = 0

    for i, img_path in enumerate(images):
        parts      = img_path.parts
        brand      = parts[1]
        collection = parts[2]
        era        = get_era(brand, collection)

        try:
            colors = get_dominant_colors(img_path)
            results.append({
                "path":       str(img_path),
                "brand":      brand,
                "collection": collection,
                "era":        era,
                "colors":     colors,  # liste de [R,G,B]
            })
        except Exception as e:
            errors += 1

        if (i + 1) % 200 == 0:
            print(f"[{i+1}/{len(images)}] ✓  ({errors} erreurs)", end="\r")

    out = OUT_DIR / "colors.json"
    with open(out, "w") as f:
        json.dump(results, f)

    print(f"\nDone — {len(results)} images → {out}  ({errors} erreurs)")


if __name__ == "__main__":
    run()

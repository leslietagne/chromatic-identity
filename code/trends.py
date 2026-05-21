import time
import json
import pandas as pd
from pathlib import Path
from pytrends.request import TrendReq

OUT_DIR = Path("figures")
OUT_DIR.mkdir(exist_ok=True)

# Initialisation
pytrends = TrendReq(hl="en-US", tz=360)

BRANDS = {
    "bv": "Bottega Veneta",
    "lv": "Louis Vuitton",
}

# Périodes à couvrir (par bloc de 5 ans max — limite Google Trends)
TIMEFRAMES = [
    "2010-01-01 2014-12-31",
    "2015-01-01 2019-12-31",
    "2020-01-01 2026-05-01",
]

def fetch_trends(keywords: list[str], timeframe: str) -> pd.DataFrame:
    """Récupère les trends pour une liste de mots-clés sur une période."""
    pytrends.build_payload(keywords, cat=0, timeframe=timeframe, geo="", gprop="")
    time.sleep(2)  # politesse pour éviter le rate limit
    return pytrends.interest_over_time()


def run():
    all_data = {brand: [] for brand in BRANDS}

    for timeframe in TIMEFRAMES:
        print(f"\nPériode : {timeframe}")
        keywords = list(BRANDS.values())

        try:
            df = fetch_trends(keywords, timeframe)
        except Exception as e:
            print(f"  Erreur : {e}")
            continue

        if df.empty:
            print("  Aucune donnée retournée")
            continue

        # Supprime la colonne isPartial si présente
        if "isPartial" in df.columns:
            df = df.drop(columns=["isPartial"])

        print(df.tail(3))

        for brand, keyword in BRANDS.items():
            if keyword in df.columns:
                series = df[keyword].reset_index()
                series.columns = ["date", "interest"]
                series["date"] = series["date"].astype(str)
                all_data[brand].extend(series.to_dict(orient="records"))

        time.sleep(3)

    # Sauvegarde JSON
    out = OUT_DIR / "trends.json"
    with open(out, "w") as f:
        json.dump(all_data, f, indent=2)
    print(f"\n✓ Trends sauvegardés → {out}")

    # Aperçu
    for brand, records in all_data.items():
        print(f"  {brand.upper()} : {len(records)} points de données")


if __name__ == "__main__":
    run()

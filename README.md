# Chromatic Identity
### Extracting the visual DNA of luxury fashion houses through computer vision

> *What if the shift in a creative director's vision could be measured, not just felt?*

**[→ Live Dashboard](https://your-app.streamlit.app)** &nbsp;|&nbsp; Built by [Leslie Tagne](https://linkedin.com/in/leslietagne)

---

## The Project

Two luxury houses. Five creative directors. Fifteen years of runway archives. **6,731 images.**

This project uses computer vision and unsupervised machine learning to extract and compare the chromatic DNA of **Bottega Veneta** and **Louis Vuitton** — quantifying what the fashion industry has always described with words: the radical visual shift of a new creative director.

The central question: **does a change in creative direction leave a measurable trace in colour data?**

The answer, it turns out, is yes.

---

## Key Findings

| Finding | What the data shows |
|---|---|
| **BV 2018 → 2019** | Highest proportion of luminous tones ever recorded — not the introduction of white, but its dominance |
| **Matthieu Blazy** | Highest colour diversity of any BV era, despite BV's "quiet luxury" reputation |
| **LV search volume** | 20× higher than BV on Google Trends — confirming the visible/invisible luxury thesis |
| **t-SNE projection** | BV and LV form clearly distinct clusters in CLIP embedding space |

---

## Pipeline

```
Nowfashion.com
    → Playwright scraper (50 collections × 2 houses)
    → 6,731 runway images
    → KMeans colour extraction (5 dominant colours / image, RGB → HSV)
    → CLIP ViT-B/32 embeddings (512 dimensions)
    → t-SNE 2D projection
    → Streamlit interactive dashboard
```

---

## Stack

| Layer | Tools |
|---|---|
| **Scraping** | Playwright, httpx, BeautifulSoup |
| **Computer Vision** | CLIP (OpenAI / HuggingFace), PIL |
| **ML** | KMeans (scikit-learn), t-SNE |
| **Feature Engineering** | RGB → HSV colour space conversion |
| **Proxies** | Google Trends (pytrends) |
| **Viz** | Matplotlib, Plotly |
| **Dashboard** | Streamlit |
| **Experiment Tracking** | MLflow |
| **Testing** | pytest |
| **Version Control** | Git / GitHub |

---

## Project Structure

```
chromatic-identity/
├── app.py                      # Streamlit dashboard
├── code/
│   ├── scraper_nowfashion.py   # Runway image scraper
│   ├── embeddings.py           # CLIP feature extraction
│   ├── colors.py               # KMeans colour extraction
│   ├── clustering.py           # t-SNE visualisation
│   ├── viz_palettes.py         # Palette figures
│   ├── viz_timeline.py         # Timeline figure
│   ├── viz_heatmap.py          # HSV heatmap figure
│   └── trends.py               # Google Trends collection
├── figures/                    # Generated outputs (gitignored)
├── assets/                     # Runway photos (gitignored)
├── tests/
│   └── test_colors.py          # Unit tests
├── requirements.txt
└── README.md
```

---

## Run Locally

```bash
git clone https://github.com/leslietagne/chromatic-identity
cd chromatic-identity
pip install -r requirements.txt
streamlit run app.py
```

> **Note:** `figures/` (embeddings, colour data) and `assets/` (runway photos) are not included in the repo due to size. Run `code/scraper_nowfashion.py` → `code/embeddings.py` → `code/colors.py` to regenerate.

---

## The Two Houses

**Bottega Veneta** — Kering · Milan · Quiet Luxury
Three creative directors (Tomas Maier → Daniel Lee → Matthieu Blazy), 2,756 images, 2011–2026.

**Louis Vuitton** — LVMH · Paris · Visible Luxury
Two creative directors (Marc Jacobs → Nicolas Ghesquière), 3,975 images, 2011–2026.

---

## About

Built as part of a Master's-level thesis on AI applications in the luxury fashion industry.

**Leslie Tagne** — Data Analytics, Paris 1 Panthéon-Sorbonne (2025–2026)
Python · Machine Learning · Deep Learning · Computer Vision · MLOps

[LinkedIn](https://linkedin.com/in/leslietagne) &nbsp;·&nbsp; [GitHub](https://github.com/leslietagne)

---

*Data source: Nowfashion.com runway archives. Images used for academic research purposes.*

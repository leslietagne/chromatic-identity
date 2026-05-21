import streamlit as st
import streamlit.components.v1 as components
import json
import numpy as np
import plotly.graph_objects as go
from collections import defaultdict
from sklearn.cluster import KMeans
import re
import colorsys
import base64
from pathlib import Path

st.set_page_config(
    page_title="Chromatic Identity",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def img_b64(path: str) -> str:
    p = Path(path)
    if not p.exists():
        return f'<div style="background:#0e0e0e;width:100%;height:100%;display:flex;align-items:center;justify-content:center;font-size:0.55rem;color:#2a2a2a;letter-spacing:0.1em;text-transform:uppercase">{p.name}</div>'
    data = base64.b64encode(p.read_bytes()).decode()
    ext  = p.suffix.lower().replace(".", "")
    if ext == "jpg": ext = "jpeg"
    return f'<img src="data:image/{ext};base64,{data}" style="width:100%;height:100%;object-fit:cover;display:block">'

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bodoni+Moda:ital,wght@0,400;0,500;1,400&family=DM+Sans:wght@300;400;500&display=swap');

.stApp, .main, section[data-testid="stMain"],
div[data-testid="stVerticalBlock"],
div[data-testid="stHorizontalBlock"],
div[data-testid="column"] { background-color: #0a0a0a !important; }
.block-container { padding: 0 5rem 6rem 5rem !important; max-width: 1200px !important; background-color: #0a0a0a !important; }
#MainMenu, footer, header { visibility: hidden; }
body, p, div, span, label { font-family: 'DM Sans', sans-serif !important; color: #e8e8e8; }

@keyframes fadeUp {
    from { opacity: 0; transform: translateY(20px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes fadeIn {
    from { opacity: 0; }
    to   { opacity: 1; }
}
@keyframes revealLine {
    from { clip-path: inset(0 100% 0 0); }
    to   { clip-path: inset(0 0% 0 0); }
}

.hero { padding: 7rem 0 4rem 0; border-bottom: 1px solid #1a1a1a; }
.hero-title { font-family: 'Bodoni Moda', serif !important; font-size: 5rem; font-weight: 400; line-height: 1.05; color: #f2f2f2; letter-spacing: -0.01em; margin-bottom: 2.5rem; }
.hero-line { display: block; overflow: hidden; animation: revealLine 1s cubic-bezier(0.77,0,0.175,1) both; }
.hero-line:nth-child(1) { animation-delay: 0.1s; }
.hero-line:nth-child(2) { animation-delay: 0.35s; }
.hero-line:nth-child(3) { animation-delay: 0.6s; }
.hero-sub { font-size: 0.92rem; color: #888; line-height: 2; max-width: 500px; font-weight: 300; animation: fadeIn 1.2s ease 1s both; }

.stat-val { font-family: 'Bodoni Moda', serif !important; font-size: 2.8rem; font-weight: 400; color: #f2f2f2; line-height: 1; animation: fadeUp 0.8s ease 1.2s both; }
.stat-lbl { font-size: 0.6rem; color: #555; letter-spacing: 0.2em; text-transform: uppercase; margin-top: 0.4rem; }

.section-label { font-size: 0.6rem; letter-spacing: 0.25em; text-transform: uppercase; color: #555; margin-bottom: 0.5rem; margin-top: 5rem; }
.section-title { font-family: 'Bodoni Moda', serif !important; font-size: 2.8rem; font-weight: 400; color: #e8e8e8; margin-bottom: 3rem; line-height: 1.1; }

.houses-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; align-items: start; }
.house-card { border: 1px solid #1a1a1a; padding: 2.5rem; background: #0a0a0a; }
.house-name { font-family: 'Bodoni Moda', serif !important; font-size: 2rem; font-weight: 400; color: #f2f2f2; margin-bottom: 0.2rem; letter-spacing: 0.02em; }
.house-meta { font-size: 0.6rem; color: #555; letter-spacing: 0.2em; text-transform: uppercase; margin-bottom: 1.2rem; }
.house-desc { font-size: 0.88rem; color: #888; line-height: 1.9; font-weight: 300; margin-bottom: 0; min-height: 6rem; }
.stats-row { display: flex; gap: 2rem; padding: 1.5rem 0; border-top: 1px solid #1a1a1a; }
.stat-item .val { font-family: 'Bodoni Moda', serif; font-size: 1.8rem; font-weight: 400; color: #e8e8e8; line-height: 1; }
.stat-item .lbl { font-size: 0.55rem; color: #555; letter-spacing: 0.18em; text-transform: uppercase; margin-top: 0.3rem; }

.photos-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; margin-top: 2rem; }
.photo-box { aspect-ratio: 3/4; overflow: hidden; border: 1px solid #1a1a1a; animation: fadeUp 0.9s ease both; }
.photo-box:nth-child(1) { animation-delay: 0.2s; }
.photo-box:nth-child(2) { animation-delay: 0.4s; }

.era-photos { display: grid; grid-template-columns: repeat(5, 1fr); gap: 1rem; margin-top: 1rem; }
.era-photo-box {
    border: 1px solid #1a1a1a;
    display: flex;
    flex-direction: column;
    height: 440px;
    overflow: hidden;
    animation: fadeUp 0.7s ease both;
}
.era-photo-box:nth-child(1) { animation-delay: 0.1s; }
.era-photo-box:nth-child(2) { animation-delay: 0.25s; }
.era-photo-box:nth-child(3) { animation-delay: 0.4s; }
.era-photo-box:nth-child(4) { animation-delay: 0.55s; }
.era-photo-box:nth-child(5) { animation-delay: 0.7s; }
.era-caption {
    padding: 0.6rem 0.5rem 0.5rem 0.5rem;
    background: #0a0a0a;
    border-top: 1px solid #1a1a1a;
    flex-shrink: 0;
    height: 95px;
    overflow: hidden;
}
.era-caption .director { font-size: 0.58rem; color: #777; letter-spacing: 0.1em; text-transform: uppercase; display: block; margin-bottom: 0.15rem; }
.era-caption .year { font-family: 'Bodoni Moda', serif; font-size: 0.85rem; color: #e8e8e8; display: block; margin-bottom: 0.2rem; }
.era-caption .desc { font-size: 0.6rem; color: #444; line-height: 1.5; display: block; }

.compare-strip { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin: 1.5rem 0; }
.compare-box { overflow: hidden; border: 1px solid #1a1a1a; display: flex; flex-direction: column; animation: fadeUp 0.8s ease both; }
.compare-box:nth-child(1) { animation-delay: 0.1s; }
.compare-box:nth-child(2) { animation-delay: 0.35s; }
.compare-box img { width: 100%; aspect-ratio: 4/5; object-fit: cover; display: block; }
.compare-caption { padding: 0.6rem 0.75rem; background: #0a0a0a; border-top: 1px solid #1a1a1a; flex-shrink: 0; }
.compare-caption .label { font-size: 0.58rem; color: #777; letter-spacing: 0.1em; text-transform: uppercase; display: block; margin-bottom: 0.15rem; }
.compare-caption .title { font-family: 'Bodoni Moda', serif; font-size: 0.9rem; color: #e8e8e8; display: block; }

.divider { border: none; border-top: 1px solid #1a1a1a; margin: 5rem 0; background: transparent; }
.chart-label { font-size: 0.6rem; letter-spacing: 0.2em; text-transform: uppercase; color: #555; margin-bottom: 0.5rem; display: block; }
.insight { border-left: 1px solid #2a2a2a; padding: 0.8rem 1.5rem; margin-top: 1rem; }
.insight-text { font-size: 0.85rem; color: #777; line-height: 1.9; font-style: italic; }

.pipeline-container { display: flex; align-items: flex-start; margin-top: 2rem; gap: 0; }
.pipeline-step { flex: 1; border-left: 1px solid #1a1a1a; padding: 0 1.8rem 0 1.5rem; animation: fadeUp 0.6s ease both; }
.pipeline-step:first-child { border-left: none; }
.pipeline-step:nth-child(1) { animation-delay: 0.1s; }
.pipeline-step:nth-child(2) { animation-delay: 0.25s; }
.pipeline-step:nth-child(3) { animation-delay: 0.4s; }
.pipeline-step:nth-child(4) { animation-delay: 0.55s; }
.pipeline-step:nth-child(5) { animation-delay: 0.7s; }
.pipeline-step:nth-child(6) { animation-delay: 0.85s; }
.pipeline-step:nth-child(7) { animation-delay: 1.0s; }
.pipeline-num { font-family: 'Bodoni Moda', serif; font-size: 2.2rem; font-weight: 400; color: #1e1e1e; line-height: 1; margin-bottom: 0.8rem; }
.pipeline-name { font-size: 0.6rem; letter-spacing: 0.18em; text-transform: uppercase; color: #888; margin-bottom: 0.5rem; }
.pipeline-desc { font-size: 0.72rem; color: #666; line-height: 1.7; }

.skills-container { margin-top: 1.5rem; }
.skill-tag { display: inline-block; border: 1px solid #1e1e1e; color: #666; font-size: 0.6rem; letter-spacing: 0.14em; text-transform: uppercase; padding: 0.45rem 0.9rem; margin: 0.25rem 0.2rem; background: #0a0a0a; animation: fadeUp 0.5s ease both; }
.skill-tag:nth-child(1)  { animation-delay: 0.05s; }
.skill-tag:nth-child(2)  { animation-delay: 0.10s; }
.skill-tag:nth-child(3)  { animation-delay: 0.15s; }
.skill-tag:nth-child(4)  { animation-delay: 0.20s; }
.skill-tag:nth-child(5)  { animation-delay: 0.25s; }
.skill-tag:nth-child(6)  { animation-delay: 0.30s; }
.skill-tag:nth-child(7)  { animation-delay: 0.35s; }
.skill-tag:nth-child(8)  { animation-delay: 0.40s; }
.skill-tag:nth-child(9)  { animation-delay: 0.45s; }
.skill-tag:nth-child(10) { animation-delay: 0.50s; }
.skill-tag:nth-child(11) { animation-delay: 0.55s; }
.skill-tag:nth-child(12) { animation-delay: 0.60s; }
.skill-tag:nth-child(13) { animation-delay: 0.65s; }
.skill-tag:nth-child(14) { animation-delay: 0.70s; }
.skill-tag:nth-child(15) { animation-delay: 0.75s; }

.footer { text-align: center; color: #2a2a2a; font-size: 0.65rem; letter-spacing: 0.18em; padding: 3rem 0 1rem 0; }
div[data-baseweb="select"] > div { background-color: #0a0a0a !important; border-color: #1e1e1e !important; }
div[data-baseweb="select"] * { background-color: #0a0a0a !important; color: #777 !important; font-size: 0.7rem !important; letter-spacing: 0.1em !important; }
</style>
""", unsafe_allow_html=True)

components.html("""
<script>
(function() {
    var p = window.parent;
    if (p.document.getElementById('ci-bar')) return;
    var bar = p.document.createElement('div');
    bar.id = 'ci-bar';
    bar.style.cssText = 'position:fixed;top:0;left:0;height:2px;width:0%;background:#ffffff;z-index:99999;transition:width 0.08s linear;pointer-events:none';
    p.document.body.appendChild(bar);
    var main = p.document.querySelector('section[data-testid="stMain"]');
    if (main) {
        main.addEventListener('scroll', function() {
            var pct = main.scrollHeight > main.clientHeight
                ? (main.scrollTop / (main.scrollHeight - main.clientHeight)) * 100 : 0;
            bar.style.width = pct + '%';
        }, {passive:true});
    }
})();
</script>
""", height=0)

@st.cache_data
def load_data():
    with open("figures/colors.json") as f:
        return json.load(f)

@st.cache_data
def compute_palettes(data):
    ERA_ORDER = ["BV — Tomas Maier","BV — Daniel Lee","BV — Matthieu Blazy","LV — Marc Jacobs","LV — Nicolas Ghesquière"]
    era_colors = defaultdict(list)
    for item in data:
        if item["era"] in ERA_ORDER:
            era_colors[item["era"]].extend(item["colors"])
    palettes = {}
    for era in ERA_ORDER:
        arr = np.array(era_colors[era], dtype=float)
        km  = KMeans(n_clusters=8, n_init=5, random_state=42)
        km.fit(arr)
        palettes[era] = km.cluster_centers_[np.argsort(-np.bincount(km.labels_))].astype(int).tolist()
    return palettes

@st.cache_data
def compute_timeline(data):
    def dominant(colors):
        arr = np.array(colors, dtype=float)
        if len(arr) < 3: return arr.mean(axis=0).astype(int).tolist()
        km = KMeans(n_clusters=3, n_init=3, random_state=42)
        km.fit(arr)
        return km.cluster_centers_[np.argsort(-np.bincount(km.labels_))[0]].astype(int).tolist()
    brand_year = defaultdict(lambda: defaultdict(list))
    for item in data:
        m = re.search(r"(20\d{2})", item["collection"])
        if m and item["brand"] in ["bv","lv"]:
            brand_year[item["brand"]][int(m.group(1))].extend(item["colors"])
    return {b: {yr: dominant(c) for yr, c in sorted(brand_year[b].items())} for b in ["bv","lv"]}

@st.cache_data
def compute_heatmap(data):
    ERA_ORDER = ["BV — Tomas Maier","BV — Daniel Lee","BV — Matthieu Blazy","LV — Marc Jacobs","LV — Nicolas Ghesquière"]
    def get_era(brand, collection):
        m = re.search(r"(20\d{2})", collection)
        if not m: return "inconnu"
        year = int(m.group(1))
        if brand == "bv":
            if year <= 2018: return "BV — Tomas Maier"
            elif year <= 2021: return "BV — Daniel Lee"
            else: return "BV — Matthieu Blazy"
        return "LV — Marc Jacobs" if year <= 2013 else "LV — Nicolas Ghesquière"
    era_hsv = defaultdict(lambda: {"s":[],"v":[],"h":[]})
    for item in data:
        era = get_era(item["brand"], item["collection"])
        if era not in ERA_ORDER: continue
        for rgb in item["colors"]:
            h,s,v = colorsys.rgb_to_hsv(*[c/255 for c in rgb])
            era_hsv[era]["h"].append(h); era_hsv[era]["s"].append(s); era_hsv[era]["v"].append(v)
    matrix = np.zeros((len(ERA_ORDER), 3))
    for i, era in enumerate(ERA_ORDER):
        matrix[i,0] = np.mean(era_hsv[era]["s"])
        matrix[i,1] = np.mean(era_hsv[era]["v"])
        matrix[i,2] = np.std(era_hsv[era]["h"])
    norm = (matrix - matrix.min(0)) / (matrix.max(0) - matrix.min(0) + 1e-8)
    return ERA_ORDER, matrix, norm

data     = load_data()
palettes = compute_palettes(data)
timeline = compute_timeline(data)
ERA_ORDER, matrix_raw, matrix_norm = compute_heatmap(data)
BG  = "#0a0a0a"
CFG = {"displayModeBar": False}

def palette_fig(eras, height_per_row=52):
    fig = go.Figure()
    for era in eras:
        for j, c in enumerate(palettes[era]):
            fig.add_trace(go.Bar(
                x=[1], y=[era], orientation='h',
                marker_color=f"rgb({c[0]},{c[1]},{c[2]})",
                marker_line_width=0, width=0.72,
                showlegend=False, base=j, hoverinfo='skip',
            ))
    fig.update_layout(
        barmode='stack', height=height_per_row*len(eras)+20,
        margin=dict(l=170,r=20,t=10,b=10),
        paper_bgcolor=BG, plot_bgcolor=BG,
        xaxis=dict(visible=False, range=[0,8]),
        yaxis=dict(tickfont=dict(color="#777",size=10,family="DM Sans"), gridcolor=BG, ticksuffix="  "),
        bargap=0.28,
    )
    return fig

# ① HERO
st.markdown("""
<div class="hero">
  <div class="hero-title">
    <span class="hero-line">6731 runway images.</span>
    <span class="hero-line">5 creative directors.</span>
    <span class="hero-line">One data story.</span>
  </div>
  <div class="hero-sub">
    What if the shift in a creative director's vision could be measured, not just felt?
    This project sits at the intersection of fashion and data science — using computer vision
    and unsupervised learning to extract the chromatic DNA of two luxury houses
    across fifteen years of runway archives.
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
c1,c2,c3,c4,c5 = st.columns(5)
for col, (val, lbl) in zip([c1,c2,c3,c4,c5],[
    ("6,731","images analysed"),("5","creative eras"),
    ("2","luxury houses"),("15","years of runway"),("512","CLIP dimensions"),
]):
    with col:
        st.markdown(f'<div class="stat-val">{val}</div><div class="stat-lbl">{lbl}</div>', unsafe_allow_html=True)

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ② THE HOUSES
st.markdown('<div class="section-label">The Houses</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">Two identities. One opposition.</div>', unsafe_allow_html=True)

st.markdown("""
<div class="houses-grid">
  <div>
    <div class="house-card">
      <div class="house-name">Bottega Veneta</div>
      <div class="house-meta">Kering &nbsp;·&nbsp; Milan &nbsp;·&nbsp; Quiet Luxury</div>
      <div class="house-desc">Defined by craft over logo, restraint over spectacle. Bottega Veneta built its identity on the Intrecciato weave — a signature visible only to those who know. Three directors. Three distinct readings of the same silence.</div>
    </div>
    <div class="stats-row">
      <div class="stat-item"><div class="val">2,756</div><div class="lbl">Images</div></div>
      <div class="stat-item"><div class="val">3</div><div class="lbl">Directors</div></div>
      <div class="stat-item"><div class="val">2011–26</div><div class="lbl">Period</div></div>
    </div>
  </div>
  <div>
    <div class="house-card">
      <div class="house-name">Louis Vuitton</div>
      <div class="house-meta">LVMH &nbsp;·&nbsp; Paris &nbsp;·&nbsp; Visible Luxury</div>
      <div class="house-desc">The most recognised monogram in fashion. Louis Vuitton operates at the intersection of heritage and cultural moment — dressing not just bodies, but eras. A house that has always known how to be seen.</div>
    </div>
    <div class="stats-row">
      <div class="stat-item"><div class="val">3,975</div><div class="lbl">Images</div></div>
      <div class="stat-item"><div class="val">2</div><div class="lbl">Directors</div></div>
      <div class="stat-item"><div class="val">2011–26</div><div class="lbl">Period</div></div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="photos-grid">
  <div class="photo-box">{img_b64("assets/hero_bv.jpg")}</div>
  <div class="photo-box">{img_b64("assets/hero_lv.jpg")}</div>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
col_bv, _, col_lv = st.columns([1, 0.06, 1])
with col_bv:
    st.markdown('<span class="chart-label">Chromatic signature — Bottega Veneta</span>', unsafe_allow_html=True)
    st.plotly_chart(palette_fig(["BV — Tomas Maier","BV — Daniel Lee","BV — Matthieu Blazy"]), use_container_width=True, config=CFG)
with col_lv:
    st.markdown('<span class="chart-label">Chromatic signature — Louis Vuitton</span>', unsafe_allow_html=True)
    st.plotly_chart(palette_fig(["LV — Marc Jacobs","LV — Nicolas Ghesquière"]), use_container_width=True, config=CFG)

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ③ ANALYSIS
st.markdown('<div class="section-label">The Analysis</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">When colour tells the story.</div>', unsafe_allow_html=True)

eras_shown   = ERA_ORDER
brands_shown = ["bv","lv"]

st.markdown("<br><span class='chart-label'>Chromatic signature by creative era</span>", unsafe_allow_html=True)
st.plotly_chart(palette_fig(eras_shown, height_per_row=56), use_container_width=True, config=CFG)
st.markdown("""<div class="insight"><div class="insight-text">
The Daniel Lee shift (2019) marks the highest proportion of luminous tones ever recorded in the BV dataset — not the introduction of white, but its dominance. Matthieu Blazy reads as a synthesis: warmth retained, spectrum widened.
</div></div>""", unsafe_allow_html=True)

era_data = [
    ("assets/bv_maier.jpg",      "Tomas Maier · BV",   "FW 2016", "Earth tones, structured silhouette. A palette that barely wavered for eight years."),
    ("assets/bv_lee.jpg",        "Daniel Lee · BV",    "SS 2019",  "All-white, luminous, radical. The sharpest chromatic break in the dataset."),
    ("assets/bv_blazy.jpg",      "Matthieu Blazy · BV","FW 2022",  "Camel meets orange python. The widest colour spectrum of any BV era."),
    ("assets/lv_jacobs.jpg",     "Marc Jacobs · LV",   "FW 2012",  "Theatrical staging, dark anthracite palette. Logomania at its peak."),
    ("assets/lv_ghesquiere.jpg", "N. Ghesquière · LV", "FW 2019",  "Architectural, camel and grey. A shifting but restrained chromatic identity."),
]

photos_html = '<div style="margin-top:1.5rem"><span class="chart-label">Representative look — one per creative era</span></div><div class="era-photos">'
for path, director, year, desc in era_data:
    photos_html += f"""
    <div class="era-photo-box">
      <div style="flex:1;overflow:hidden;min-height:0">{img_b64(path)}</div>
      <div class="era-caption">
        <span class="director">{director}</span>
        <span class="year">{year}</span>
        <span class="desc">{desc}</span>
      </div>
    </div>"""
photos_html += "</div>"
st.markdown(photos_html, unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

st.markdown("<span class='chart-label'>Dominant colour per season</span>", unsafe_allow_html=True)
ERAS_BY_BRAND = {
    "bv": [(2010,2018,"Tomas Maier"),(2019,2021,"Daniel Lee"),(2022,2026,"Matthieu Blazy")],
    "lv": [(2010,2013,"Marc Jacobs"),(2014,2026,"Nicolas Ghesquière")],
}
BRAND_LABELS = {"bv":"Bottega Veneta","lv":"Louis Vuitton"}

for brand in brands_shown:
    years_data = timeline[brand]
    years = sorted(years_data.keys())
    fig_tl = go.Figure()
    for yr in years:
        rgb = years_data[yr]
        fig_tl.add_trace(go.Bar(x=[yr], y=[1], width=0.85, marker_color=f"rgb({rgb[0]},{rgb[1]},{rgb[2]})", marker_line_width=0, showlegend=False, hovertemplate=f"<b>{yr}</b><extra></extra>"))
    for (y0,y1,name) in ERAS_BY_BRAND[brand]:
        yr_list = [y for y in years if y0<=y<=y1]
        if not yr_list: continue
        fig_tl.add_annotation(x=(min(yr_list)+max(yr_list))/2, y=1.12, text=f"<i>{name}</i>", showarrow=False, font=dict(color="#555",size=9,family="DM Sans"), yref="y")
        if y0 > min(years):
            fig_tl.add_vline(x=y0-0.5, line_color="#1e1e1e", line_width=1, line_dash="dot")
    fig_tl.update_layout(
        title=dict(text=BRAND_LABELS[brand], font=dict(color="#555",size=9,family="DM Sans"), x=0),
        height=160, margin=dict(l=20,r=20,t=35,b=35),
        paper_bgcolor=BG, plot_bgcolor=BG,
        xaxis=dict(tickvals=years, ticktext=[str(y) for y in years], tickfont=dict(color="#555",size=8,family="DM Sans"), gridcolor="#111"),
        yaxis=dict(visible=False, range=[0,1.3]), barmode="stack", showlegend=False,
    )
    st.plotly_chart(fig_tl, use_container_width=True, config=CFG)

st.markdown("""<div class="insight"><div class="insight-text">
BV shows a sharp chromatic break in 2019 — the data captures what the industry felt instantly. LV under Ghesquière evolves more gradually, shifting toward cooler, more architectural tones from 2019 onward.
</div></div>""", unsafe_allow_html=True)

st.markdown(f"""
<div style="margin-top:2rem">
  <span class="chart-label">The 2018 → 2019 shift — before and after</span>
</div>
<div class="compare-strip">
  <div class="compare-box">
    <div style="flex:1;overflow:hidden;min-height:0">{img_b64("assets/bv_before.jpg")}</div>
    <div class="compare-caption">
      <span class="label">Tomas Maier · BV · FW 2018</span>
      <span class="title">Last collection — dark leather, monochrome depth</span>
    </div>
  </div>
  <div class="compare-box">
    <div style="flex:1;overflow:hidden;min-height:0">{img_b64("assets/bv_after.jpg")}</div>
    <div class="compare-caption">
      <span class="label">Daniel Lee · BV · FW 2019</span>
      <span class="title">First collection — luminous tones at their peak, a dominance shift</span>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

st.markdown("<span class='chart-label'>Colourimetric intensity — Saturation · Brightness · Diversity</span>", unsafe_allow_html=True)
idx_shown = [ERA_ORDER.index(e) for e in eras_shown]
mat_show  = matrix_norm[idx_shown]
raw_show  = matrix_raw[idx_shown]
fig_hm = go.Figure(data=go.Heatmap(
    z=mat_show, x=["Avg Saturation","Avg Brightness","Colour Diversity"], y=eras_shown,
    colorscale="RdYlBu_r", zmin=0, zmax=1,
    text=[[f"{raw_show[i,j]:.3f}" for j in range(3)] for i in range(len(eras_shown))],
    texttemplate="%{text}", textfont=dict(size=11,color="white",family="DM Sans"),
    hovertemplate="<b>%{y}</b><br>%{x}: %{text}<extra></extra>", showscale=True,
    colorbar=dict(title=dict(text="score",font=dict(color="#555",size=9,family="DM Sans")), tickfont=dict(color="#555",family="DM Sans"), thickness=8, len=0.6)
))
fig_hm.update_layout(
    height=75*len(eras_shown)+80, margin=dict(l=20,r=80,t=20,b=50),
    paper_bgcolor=BG, plot_bgcolor=BG,
    xaxis=dict(tickfont=dict(color="#777",size=10,family="DM Sans"), side="bottom"),
    yaxis=dict(tickfont=dict(color="#777",size=10,family="DM Sans"), autorange="reversed"),
)
st.plotly_chart(fig_hm, use_container_width=True, config=CFG)
st.markdown("""<div class="insight"><div class="insight-text">
Matthieu Blazy records the highest colour diversity of any BV era — counterintuitive for a house defined by restraint. Low saturation, wide hue spectrum: sophistication through variety, not intensity.
</div></div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# t-SNE
st.markdown("<span class='chart-label'>CLIP embedding space — t-SNE projection by creative era</span>",
            unsafe_allow_html=True)
st.markdown(f"""
<div style="border:1px solid #1a1a1a;overflow:hidden;animation:fadeUp 0.8s ease both">
  {img_b64("figures/tsne.png")}
</div>
""", unsafe_allow_html=True)
st.markdown("""<div class="insight"><div class="insight-text">
Each point is one runway image projected into 2D space via t-SNE on 512-dimensional CLIP embeddings.
The separation between BV (dark tones) and LV (gold tones) confirms that the two houses occupy
distinct regions of the visual embedding space — their aesthetic DNA is measurably different.
Within each house, sub-clusters correspond to creative eras, validating that director transitions
leave a structural trace in the data.
</div></div>""", unsafe_allow_html=True)

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ⑤ CONCLUSION
st.markdown('<div class="section-label">Results</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">What the data tells us.</div>', unsafe_allow_html=True)

st.markdown("""
<div style="display:grid;grid-template-columns:1fr 1fr;gap:2rem;margin-top:1rem">

  <div style="border:1px solid #1a1a1a;padding:2rem;background:#0a0a0a">
    <div style="font-size:0.6rem;letter-spacing:0.2em;text-transform:uppercase;color:#555;margin-bottom:0.8rem">H1 — Validated</div>
    <div style="font-family:'Bodoni Moda',serif;font-size:1.3rem;color:#e8e8e8;margin-bottom:1rem;line-height:1.3">BV and LV occupy distinct regions of the visual embedding space.</div>
    <div style="font-size:0.82rem;color:#666;line-height:1.8">The t-SNE projection of 6,731 CLIP embeddings shows clear separation between the two houses. Their chromatic DNA is measurably different — quiet luxury vs visible luxury is not just a marketing concept, it is a data signal.</div>
  </div>

  <div style="border:1px solid #1a1a1a;padding:2rem;background:#0a0a0a">
    <div style="font-size:0.6rem;letter-spacing:0.2em;text-transform:uppercase;color:#555;margin-bottom:0.8rem">H2 — Partially Validated</div>
    <div style="font-family:'Bodoni Moda',serif;font-size:1.3rem;color:#e8e8e8;margin-bottom:1rem;line-height:1.3">Director transitions leave a measurable chromatic trace.</div>
    <div style="font-size:0.82rem;color:#666;line-height:1.8">The 2019 BV shift is the sharpest chromatic break in the dataset, coinciding with Daniel Lee's first collection. However, correlation with commercial proxies (Google Trends, resale prices) requires further investigation to establish causality.</div>
  </div>

</div>

<div style="border:1px solid #1a1a1a;padding:2rem;background:#0a0a0a;margin-top:2rem">
  <div style="font-size:0.6rem;letter-spacing:0.2em;text-transform:uppercase;color:#555;margin-bottom:0.8rem">Key Finding</div>
  <div style="font-family:'Bodoni Moda',serif;font-size:1.5rem;color:#e8e8e8;margin-bottom:1rem;line-height:1.3">Matthieu Blazy's BV records the widest colour spectrum of any era — counterintuitive for a house defined by restraint.</div>
  <div style="font-size:0.82rem;color:#666;line-height:1.8">Low saturation, high colour diversity. Sophistication through variety, not intensity. A finding that challenges the "quiet luxury = monochrome" narrative.</div>
</div>
""", unsafe_allow_html=True)

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ④ METHODOLOGY
st.markdown('<div class="section-label">Methodology</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">The pipeline, step by step.</div>', unsafe_allow_html=True)

steps = [
    ("01","Scraping","Playwright + httpx\nNowfashion.com\n50 collections per house"),
    ("02","Processing","6,731 high-res images\nStructured by collection,\nseason and era"),
    ("03","Colour","KMeans clustering\n5 dominant colours\nper image — RGB"),
    ("04","HSV Analysis","RGB → HSV conversion\nSaturation, brightness\nand hue diversity"),
    ("05","Embeddings","CLIP ViT-B/32\n512-dim vectors\nt-SNE 2D projection"),
    ("06","Tracking","MLflow logging\nParameters, metrics\nand artefacts"),
    ("07","Dashboard","Streamlit + Plotly\nInteractive interface\nCloud deployment"),
]
pipeline_html = '<div class="pipeline-container">'
for num, name, desc in steps:
    pipeline_html += f'<div class="pipeline-step"><div class="pipeline-num">{num}</div><div class="pipeline-name">{name}</div><div class="pipeline-desc">{desc.replace(chr(10),"<br>")}</div></div>'
pipeline_html += "</div>"
st.markdown(pipeline_html, unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown('<div class="section-label">Skills</div>', unsafe_allow_html=True)
skills = ["Python","Playwright","Computer Vision","KMeans Clustering","CLIP (OpenAI)","t-SNE","HSV Feature Engineering","Plotly","Streamlit","MLflow","AWS S3","pytest","Unsupervised Learning","Data Visualisation","Git"]
st.markdown('<div class="skills-container">' + "".join(f'<span class="skill-tag">{s}</span>' for s in skills) + "</div>", unsafe_allow_html=True)

st.markdown('<div class="footer">LESLIE TAGNE &nbsp;—&nbsp; DATA × FASHION &nbsp;—&nbsp; 2026</div>', unsafe_allow_html=True)

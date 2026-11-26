from pathlib import Path

import folium
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from streamlit_folium import st_folium

st.set_page_config(
    page_title="Karnala Bird Santury",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed",
)

ROOT = Path(__file__).parent
WBT_FILE = ROOT / "Statistcial Ecology Group_4 - WBT.csv"
TREE_FILE = ROOT / "Statistcial Ecology Group_4 - Tree.csv"

POLYGONS = {
    2: [(73.1144804073,18.8913513095),(73.1145554029,18.8912777951),(73.1146101738,18.8913553449),(73.1145470541,18.8914386354)],
    3: [(73.1138859681,18.8914820163),(73.1138970448,18.8913889304),(73.1139439856,18.8913535761),(73.1139683948,18.8914353806)],
    4: [(73.1129590770,18.8911947186),(73.1130230016,18.8912243172),(73.1130005045,18.8912858638),(73.1129309708,18.8912553647)],
    5: [(73.1172111258,18.8943514109),(73.1172856252,18.8944244357),(73.1171620442,18.8944716976),(73.1171099445,18.8944130782)],
    6: [(73.1157972020,18.8946759522),(73.1158695539,18.8946013849),(73.1159559280,18.8946486551),(73.1159463464,18.8946623316)],
}
CENTERS = {
    1: (73.11513,18.89154), 2: (73.11455,18.89137),
    3: (73.11392,18.89142), 4: (73.11298,18.89124),
    5: (73.11720,18.89442), 6: (73.11588,18.89465),
}
THERMAL = {
    1: {"ground": [24.8,24.0,25.5,24.7], "canopy": [11.5,25.4,25.3,25.5], "ground_range": "22.0–29.0", "canopy_range": "-9.0–30.0", "samples": 4},
    2: {"ground": [29.0,32.0,29.6], "canopy": [29.7,33.0,-11.0], "ground_range": "27.5–42.3", "canopy_range": "-11.0–42.2", "samples": 3},
    3: {"ground": [36.0,31.5,33.7], "canopy": [32.5,35.5,73.8], "ground_range": "28.2–50.8", "canopy_range": "-1.6–160+", "samples": 3},
    4: {"ground": [27.1,26.9,25.0], "canopy": [30.7,26.7,30.4], "ground_range": "23.8–40.9", "canopy_range": "-5.8–41.7", "samples": 3},
    5: {"ground": [32.8,28.1,29.3], "canopy": [32.3,31.0,30.0], "ground_range": "26.6–37.9", "canopy_range": "-7.0–43.2", "samples": 3},
    6: {"ground": [27.1,28.4,27.5], "canopy": [32.3,30.6,29.4], "ground_range": "25.3–36.0", "canopy_range": "-4.7–36.0", "samples": 3},
}

@st.cache_data
def load_data():
    wbt = pd.read_csv(WBT_FILE)
    wbt.columns = [str(c).strip().lower() for c in wbt.columns]
    wbt = wbt.rename(columns={"qudrant": "quadrant", "temprature": "temperature"})

    trees = pd.read_csv(TREE_FILE)
    trees.columns = [str(c).strip() for c in trees.columns]
    q_col = next(c for c in trees.columns if c.lower() == "quadrant")
    name_col = next(c for c in trees.columns if c.lower() == "local name")
    trees[q_col] = pd.to_numeric(trees[q_col], errors="coerce").ffill().astype(int)
    top_col = next(c for c in trees.columns if c.lower() == "height 2p (top)")
    hag_col = next(c for c in trees.columns if c.lower() == "height hagameter 20m")

    result = {}
    for q in range(1, 7):
        records = trees[trees[q_col] == q]
        height_col = hag_col if q == 6 else top_col
        heights = pd.to_numeric(records[height_col], errors="coerce").dropna()
        counts = records[name_col].dropna().astype(str).value_counts()
        result[q] = {
            "tree_count": len(records),
            "mean_height": float(heights.mean()) if not heights.empty else None,
            "height_n": int(heights.size),
            "height_method": "Hagameter 20m" if q == 6 else "2P top",
            "common": counts.index[0] if not counts.empty else "Not recorded",
            "common_count": int(counts.iloc[0]) if not counts.empty else 0,
            "species_count": int(records[name_col].nunique()),
        }
    return wbt, result

wbt_df, tree_info = load_data()
rows = {}
for _, row in wbt_df.iterrows():
    q = int(row["quadrant"])
    rows[q] = {"wbt": float(row["wbt"]), "temperature": float(row["temperature"]), "humidity": float(row["humidity"])}

st.markdown("""
<style>
:root {
    --background: #D8D4D1;
    --surface: #FBF3E6;
    --surface-hover: #292929;
    --text: #000000;
    --muted: #55514d;
    --border: #c9c0b6;
    --accent: #7acb91;
}
html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
    background: var(--background) !important;
    color: var(--text) !important;
}
[data-testid="stSidebar"] { background: #111111 !important; }
h1, h2, h3, h4, h5, h6, p, label { color: var(--text) !important; }
.block-container { max-width: 1500px; padding: 1.5rem 2rem 2.5rem; }
.hero { padding: .5rem 0 1.1rem; }
.eyebrow { font-size: .72rem; letter-spacing: .14em; text-transform: uppercase; color: var(--muted); font-weight: 700; }
.hero h1 { font-family: Manrope, sans-serif; font-size: 2.25rem; letter-spacing: -.05em; margin: .4rem 0; }
.hero p { color: var(--muted) !important; margin: 0; }
.kpi {
    box-sizing: border-box; min-height: 132px; height: 100%; padding: 18px 20px;
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    text-align: center; gap: 7px; background: var(--surface);
    border: 1px solid var(--border); border-radius: 16px;
}
.kpi-label { color: var(--muted); font-size: .82rem; font-weight: 600; }
.kpi-value { color: var(--text); font: 800 1.8rem Manrope, sans-serif; line-height: 1.2; }
.kpi-foot { color: var(--muted); font-size: .74rem; line-height: 1.35; }
.panel-title { font: 700 1rem Manrope, sans-serif; margin: 0; }
.panel-sub { font-size: .76rem; color: var(--muted); margin: .25rem 0 .75rem; }

[data-testid="stMetric"]
{ background: var(--surface) !important; border: 1px solid var(--border) 
!important; border-radius: 14px; padding: 14px; }

[data-testid="stMetricLabel"], [data-testid="stMetricValue"] { color: var(--text) !important; }
[data-testid="stMetricDelta"] { color: var(--muted) !important; }
[data-baseweb="select"] > div, [data-baseweb="input"] > div { background: var(--surface) !important; color: var(--text)
!important; border-color: var(--border) !important; }
.js-plotly-plot, .folium-map { border-radius: 14px; overflow: hidden; }
@media (max-width: 800px) {
    .block-container { padding: 1rem 1rem 2rem; }
    .kpi { min-height: 112px; padding: 12px 8px; }
    .kpi-value { font-size: 1.45rem; }
    .kpi-foot { font-size: .68rem; }
}

[data-testid="stHeader"] {
    background: transparent !important;
}

[data-testid="stToolbar"] {
    top: 8px;
    right: 16px;
}

.block-container {
    padding-top: 3.2rem !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="hero"><div class="eyebrow">Biodiversity & microclimate survey</div><h1>Karnala Bird Sanctury.</h1><p>Explore field observations across six survey quadrants at Karnala Wildlife Sanctuary.</p></div>', unsafe_allow_html=True)

all_wbt = [rows[q]["wbt"] for q in rows]
c1, c2, c3, c4 = st.columns(4)
for col, label, value, foot in [
    (c1, "Survey quadrants", "06", "Mapped field locations"),
    (c2, "Trees recorded", str(sum(x["tree_count"] for x in tree_info.values())), "Across all six quadrants"),
    (c3, "WBT range", f"{min(all_wbt):.1f}–{max(all_wbt):.1f} °C", "Wet-bulb temperature"),
    (c4, "Distinct tree names", str(sum(x["species_count"] for x in tree_info.values())), "Quadrant species records summed"),
]:
    col.markdown(f'<div class="kpi"><div class="kpi-label">{label}</div><div class="kpi-value">{value}</div><div class="kpi-foot">{foot}</div></div>', unsafe_allow_html=True)

st.write("")
map_col, detail_col = st.columns([1.55, 1], gap="medium")
with map_col:
    st.markdown('<div class="panel-title">Quadrant field map</div><div class="panel-sub"> inspect the satellite map and survey boudaries.</div>', unsafe_allow_html=True)
    field_map = folium.Map(location=[18.8925, 73.1150], zoom_start=15, tiles=None, control_scale=True)
    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr="Tiles © Esri — Sources: Esri, Maxar, Earthstar Geographics, and the GIS User Community",
        name="Satellite imagery", overlay=False, control=True, max_zoom=19,
    ).add_to(field_map)
    folium.TileLayer(
        tiles="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
        attr="&copy; OpenStreetMap contributors", name="Street map", overlay=False, control=True,
    ).add_to(field_map)

    for q in range(1, 7):
        
        if q in POLYGONS:
            locations = [(lat, lon) for lon, lat in POLYGONS[q]]
            folium.Polygon(
                locations=locations, color="#52748", weight=2, fill=True,
                fill_color="#b8cfb4", fill_opacity=0.55,
                tooltip=f"<b>Quadrant {q}</b><br>WBT {rows[q]['wbt']} °C<br>Air {rows[q]['temperature']} °C<br>Most common: {tree_info[q]['common']}",
            ).add_to(field_map)
        lon, lat = CENTERS[q]
        folium.CircleMarker(
            location=[lat, lon], radius=7, color="white", weight=2,
            fill=True, fill_color="#3f7954", fill_opacity=1,
            tooltip=f"<b>Quadrant {q}</b><br>WBT {rows[q]['wbt']} °C<br>Most common: {tree_info[q]['common']}",
        ).add_to(field_map)
        folium.Marker(
            location=[lat, lon],
            icon=folium.DivIcon(html=f'<div style="font-weight:700;font-size:11px;color:#173c2a;text-shadow:0 1px 4px white,0 0 4px white">Q{q}</div>'),
        ).add_to(field_map)

    folium.LayerControl(position="topright").add_to(field_map)
    st_folium(field_map, height=390, use_container_width=True, returned_objects=[])
    st.caption("The map combines Esri satellite imagery and KML-derived survey boundaries. Q1 is a marker because no Q1 polygon was supplied.")

    st.markdown('<div class="panel-title">Microclimate by quadrant</div><div class="panel-sub">Compare readings across the survey area.</div>', unsafe_allow_html=True)
    chart_metric = st.radio("Chart metric", ["WBT", "Air temperature", "Humidity"], horizontal=True, label_visibility="collapsed")
    key = {"WBT": "wbt", "Air temperature": "temperature", "Humidity": "humidity"}[chart_metric]
    bar = go.Figure(go.Bar(
        x=[f"Q{q}" for q in rows], y=[rows[q][key] for q in rows],
        marker_color="#285b43",
        text=[f"{rows[q][key]:g}" for q in rows], textposition="outside",
    ))
    bar.update_layout(
        height=280, margin={"l": 5, "r": 5, "t": 15, "b": 5},
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font={"color": "#000000"}, showlegend=False,
        yaxis={"title": "°C" if key != "humidity" else "%", "gridcolor": "#c9c0b6"},
        xaxis={"title": ""},
    )
    st.plotly_chart(bar, use_container_width=True, config={"displayModeBar": False})

with detail_col:
    selected_q = st.selectbox("Selected quadrant", list(range(1, 7)), format_func=lambda q: f"Quadrant {q}")
    r, tree = rows[selected_q], tree_info[selected_q]
    st.markdown(f"### Quadrant {selected_q} · {r['wbt']:.1f} °C WBT")
    a, b = st.columns(2)
    a.metric("Air temperature", f"{r['temperature']:.1f} °C")
    b.metric("Relative humidity", f"{r['humidity']:.1f}%")
    a, b = st.columns(2)
    a.metric("Mean tree height", f"{tree['mean_height']:.1f} m" if tree['mean_height'] is not None else "Not recorded", help=f"{tree['height_method']}; n={tree['height_n']}")
    b.metric("Tree records", str(tree["tree_count"]))
    st.markdown("**Most recorded local name**")
    st.write(f"{tree['common']} · {tree['common_count']} trees · {tree['species_count']} local names in this quadrant")

    thermal = THERMAL[selected_q]
    ground = [x for x in thermal["ground"] if 0 <= x <= 60]
    canopy = [x for x in thermal["canopy"] if 0 <= x <= 60]
    st.markdown("**Thermal image · centre readings**")
    a, b = st.columns(2)
    a.metric("Ground mean", f"{sum(ground)/len(ground):.1f} °C", help=f"Reported range {thermal['ground_range']} °C")
    b.metric("Canopy mean*", f"{sum(canopy)/len(canopy):.1f} °C", help=f"Reported range {thermal['canopy_range']} °C")
    if any(x < 0 or x > 60 for x in thermal["canopy"]):
        st.info("Source canopy readings include negative or unusually high values. The displayed mean excludes values outside 0–60 °C; ranges retain the reported values.")
    st.caption(f"Height from {tree['height_method']} measurements (n={tree['height_n']}). Q1–Q5 and Q6 use different measurement methods.")

st.markdown('<div class="panel-title">Quadrant comparison</div><div class="panel-sub">Summary of the field measurements.</div>', unsafe_allow_html=True)
summary = []
for q in rows:
    tree = tree_info[q]
    summary.append({
        "Quadrant": f"Q{q}", "WBT (°C)": rows[q]["wbt"],
        "Air temp. (°C)": rows[q]["temperature"], "Humidity (%)": rows[q]["humidity"],
        "Mean height (m)": round(tree["mean_height"], 1) if tree["mean_height"] is not None else None,
        "Trees": tree["tree_count"], "Most common": tree["common"],
    })
st.dataframe(pd.DataFrame(summary), use_container_width=True, hide_index=True)

st.download_button("Download quadrant summary CSV", pd.DataFrame(summary).to_csv(index=False), file_name="karnala-quadrant-summary.csv", mime="text/csv")
st.caption("Field data supplied by Statistical Ecology Group 04. Thermal camera values should be reviewed against the original images before formal analysis.")

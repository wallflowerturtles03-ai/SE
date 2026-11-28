from pathlib import Path

import folium
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from streamlit_folium import st_folium

st.set_page_config(
    page_title="Karnala Bird Sanctuary",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed",
)

ROOT = Path(__file__).parent
WBT_FILE = ROOT / "Statistcial Ecology Group_4 - WBT.csv"
TREE_FILE = ROOT / "Statistcial Ecology Group_4 - Tree.csv"

POLYGONS = {
    2: [(73.1144804073, 18.8913513095), (73.1145554029, 18.8912777951), (73.1146101738, 18.8913553449), (73.1145470541, 18.8914386354)],
    3: [(73.1138859681, 18.8914820163), (73.1138970448, 18.8913889304), (73.1139439856, 18.8913535761), (73.1139683948, 18.8914353806)],
    4: [(73.1129590770, 18.8911947186), (73.1130230016, 18.8912243172), (73.1130005045, 18.8912858638), (73.1129309708, 18.8912553647)],
    5: [(73.1172111258, 18.8943514109), (73.1172856252, 18.8944244357), (73.1171620442, 18.8944716976), (73.1171099445, 18.8944130782)],
    6: [(73.1157972020, 18.8946759522), (73.1158695539, 18.8946013849), (73.1159559280, 18.8946486551), (73.1159463464, 18.8946623316)],
}
CENTERS = {
    1: (73.11513, 18.89154), 2: (73.11455, 18.89137),
    3: (73.11392, 18.89142), 4: (73.11298, 18.89124),
    5: (73.11720, 18.89442), 6: (73.11588, 18.89465),
}
THERMAL = {
    1: {"ground": [24.8, 24.0, 25.5, 24.7], "canopy": [11.5, 25.4, 25.3, 25.5], "ground_range": "22.0–29.0", "canopy_range": "-9.0–30.0", "samples": 4},
    2: {"ground": [29.0, 32.0, 29.6], "canopy": [29.7, 33.0, -11.0], "ground_range": "27.5–42.3", "canopy_range": "-11.0–42.2", "samples": 3},
    3: {"ground": [36.0, 31.5, 33.7], "canopy": [32.5, 35.5, 73.8], "ground_range": "28.2–50.8", "canopy_range": "-1.6–160+", "samples": 3},
    4: {"ground": [27.1, 26.9, 25.0], "canopy": [30.7, 26.7, 30.4], "ground_range": "23.8–40.9", "canopy_range": "-5.8–41.7", "samples": 3},
    5: {"ground": [32.8, 28.1, 29.3], "canopy": [32.3, 31.0, 30.0], "ground_range": "26.6–37.9", "canopy_range": "-7.0–43.2", "samples": 3},
    6: {"ground": [27.1, 28.4, 27.5], "canopy": [32.3, 30.6, 29.4], "ground_range": "25.3–36.0", "canopy_range": "-4.7–36.0", "samples": 3},
}

if "selected_quadrant" not in st.session_state:
    st.session_state.selected_quadrant = 1
if "quadrant_selector" not in st.session_state:
    st.session_state.quadrant_selector = st.session_state.selected_quadrant


def sync_from_selector():
    st.session_state.selected_quadrant = st.session_state.quadrant_selector


def sync_from_chart():
    selection = st.session_state.get("microclimate_chart", {}).get("selection", {})
    points = selection.get("points", [])
    if points:
        customdata = points[0].get("customdata")
        if isinstance(customdata, (list, tuple)):
            customdata = customdata[0]
        if customdata is not None:
            q = int(customdata)
            st.session_state.selected_quadrant = q
            st.session_state.quadrant_selector = q


def sync_from_table():
    selection = st.session_state.get("comparison_table", {}).get("selection", {})
    selected_rows = selection.get("rows", [])
    if selected_rows:
        q = int(selected_rows[0]) + 1
        st.session_state.selected_quadrant = q
        st.session_state.quadrant_selector = q


@st.cache_data
def load_data():
    wbt = pd.read_csv(WBT_FILE)
    wbt.columns = [str(column).strip().lower() for column in wbt.columns]
    wbt = wbt.rename(columns={"qudrant": "quadrant", "temprature": "temperature"})

    trees = pd.read_csv(TREE_FILE)
    trees.columns = [str(column).strip() for column in trees.columns]
    q_col = next(column for column in trees.columns if column.lower() == "quadrant")
    name_col = next(column for column in trees.columns if column.lower() == "local name")
    trees[q_col] = pd.to_numeric(trees[q_col], errors="coerce").ffill().astype(int)
    top_col = next(column for column in trees.columns if column.lower() == "height 2p (top)")
    hag_col = next(column for column in trees.columns if column.lower() == "height hagameter 20m")

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
            "species_counts": counts.to_dict(),
        }
    return wbt, result


wbt_df, tree_info = load_data()
rows = {}
for _, row in wbt_df.iterrows():
    q = int(row["quadrant"])
    rows[q] = {
        "wbt": float(row["wbt"]),
        "temperature": float(row["temperature"]),
        "humidity": float(row["humidity"]),
    }


def mix_color(start, end, amount):
    return tuple(round(a + (b - a) * amount) for a, b in zip(start, end))


def wbt_color(value):
    low = min(item["wbt"] for item in rows.values())
    high = max(item["wbt"] for item in rows.values())
    position = 0 if high == low else (value - low) / (high - low)
    stops = [(0.0, (190, 213, 192)), (0.5, (101, 153, 113)), (1.0, (220, 153, 76))]
    for index in range(len(stops) - 1):
        left_pos, left_rgb = stops[index]
        right_pos, right_rgb = stops[index + 1]
        if position <= right_pos:
            fraction = (position - left_pos) / (right_pos - left_pos)
            return "#{:02x}{:02x}{:02x}".format(*mix_color(left_rgb, right_rgb, fraction))
    return "#{:02x}{:02x}{:02x}".format(*stops[-1][1])


st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');
:root { --page:#F3EBDO; --card:#fffdf7; --ink:#26352c; --muted:#68756c; --line:#dedfd4; --forest:#285b43; --sage:#91b29a; }
html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] { background:var(--page) !important; color:var(--ink) !important; }
.block-container { max-width:1440px; padding:2rem 2.2rem 2.5rem; }
h1, h2, h3, h4, h5, h6 { color:var(--ink) !important; font-family:"Times New Roman", Times, serif !important; }
body, p, label { font-family:"Times New Roman", Times, serif; }
.hero { margin:0 0 1.5rem; }
.hero h1 { font:800 2.5rem "Times New Roman", Times, serif !important; letter-spacing:-.045em; margin:0 0 .35rem; }
.hero p { color:var(--muted) !important; margin:0; }
.section-title { font:700 1.15rem "Times New Roman", Times, serif; color:var(--ink); margin:0 0 .2rem; }
.section-note { font-size:.88rem; color:var(--muted); margin:0 0 .9rem; }
.kpi { height:118px; box-sizing:border-box; background:var(--card); border:1px solid var(--line); border-radius:15px; padding:16px; display:flex; flex-direction:column; justify-content:center; align-items:flex-start; gap:5px; }
.kpi-label { font-size:.82rem; color:var(--muted); }
.kpi-value { font:800 1.65rem "Times New Roman", Times, serif; color:var(--forest); }
.kpi-foot { font-size:.74rem; color:var(--muted); }
.species-tag { display:inline-block; background:#e7eee5; color:var(--forest); border-radius:999px; padding:4px 10px; margin:2px 4px 2px 0; font-size:.78rem; white-space:nowrap; }
.closing { border-top:1px solid var(--line); margin-top:1.5rem; padding-top:1rem; color:var(--muted); font-size:.82rem; }
[data-testid="stMetric"] { background:var(--card); border:1px solid var(--line); border-radius:13px; padding:12px 14px; }
[data-testid="stMetricLabel"], [data-testid="stMetricValue"] { color:var(--ink) !important; }
[data-baseweb="select"] > div { background:var(--card); border-color:var(--line); }
@media (max-width:850px) { .block-container { padding:1.2rem 1rem 2rem; } .hero h1 { font-size:2rem !important; } }
</style>
""", unsafe_allow_html=True)

st.markdown(
    '<div class="hero"><h1>Karnala Bird Sanctuary</h1>'
    '<p>Biodiversity and microclimate observations across six survey quadrants.</p></div>',
    unsafe_allow_html=True,
)

all_wbt = [rows[q]["wbt"] for q in rows]
kpi_columns = st.columns(4)
kpi_items = [
    ("Survey quadrants", "06", "Mapped field locations"),
    ("Trees recorded", str(sum(item["tree_count"] for item in tree_info.values())), "Across all six quadrants"),
    ("WBT range", f"{min(all_wbt):.1f}–{max(all_wbt):.1f} °C", "Wet-bulb temperature"),
    ("Distinct tree names", str(sum(item["species_count"] for item in tree_info.values())), "Quadrant species records summed"),
]
for column, (label, value, foot) in zip(kpi_columns, kpi_items):
    column.markdown(
        f'<div class="kpi"><div class="kpi-label">{label}</div>'
        f'<div class="kpi-value">{value}</div><div class="kpi-foot">{foot}</div></div>',
        unsafe_allow_html=True,
    )

st.write("")
map_column, detail_column = st.columns([1.2, 1], gap="large")
with map_column:
    st.markdown('<div class="section-title">Quadrant field map</div><div class="section-note">Select a quadrat on the map to update the selected quadrant.</div>', unsafe_allow_html=True)
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

    current_q = st.session_state.selected_quadrant
    for q in range(1, 7):
        fill = wbt_color(rows[q]["wbt"])
        if q in POLYGONS:
            locations = [(lat, lon) for lon, lat in POLYGONS[q]]
            folium.Polygon(
                locations=locations,
                color="#285b43" if q == current_q else fill,
                weight=4 if q == current_q else 2,
                fill=True,
                fill_color=fill,
                fill_opacity=0.68,
                tooltip=f"<b>Quadrant {q}</b><br>WBT {rows[q]['wbt']:.1f} °C<br>Air {rows[q]['temperature']:.1f} °C<br>Most common: {tree_info[q]['common']}",
                popup=folium.Popup(f"Quadrant {q}", max_width=150),
            ).add_to(field_map)
        lon, lat = CENTERS[q]
        folium.CircleMarker(
            location=[lat, lon], radius=10 if q == current_q else 7,
            color="#173c2a" if q == current_q else "#fffdf7",
            weight=3 if q == current_q else 2, fill=True, fill_color=fill, fill_opacity=1,
            tooltip=f"Quadrant {q} · WBT {rows[q]['wbt']:.1f} °C",
            popup=folium.Popup(f"Quadrant {q}", max_width=150),
        ).add_to(field_map)
        folium.Marker(
            location=[lat, lon],
            icon=folium.DivIcon(html=f'<div style="font-weight:700;font-size:11px;color:#173c2a;text-shadow:0 1px 4px white,0 0 4px white">Q{q}</div>'),
        ).add_to(field_map)

    folium.LayerControl(position="topright").add_to(field_map)
    map_result = st_folium(field_map, height=390, use_container_width=True, returned_objects=["last_object_clicked"], key="field_map")
    clicked = (map_result or {}).get("last_object_clicked")
    if isinstance(clicked, dict) and "lat" in clicked and "lng" in clicked:
        signature = (round(clicked["lat"], 5), round(clicked["lng"], 5))
        if signature != st.session_state.get("last_map_click"):
            nearest_q = min(CENTERS, key=lambda q: (CENTERS[q][1] - clicked["lat"]) ** 2 + (CENTERS[q][0] - clicked["lng"]) ** 2)
            st.session_state.selected_quadrant = nearest_q
            st.session_state.quadrant_selector = nearest_q
            st.session_state.last_map_click = signature
    st.caption("WBT colours share one cool-green to warm-amber scale across map, chart, and table. Q1 is a marker because no Q1 polygon was supplied.")

    # The chart now fills the unused area directly under the map.
    st.markdown('<div class="section-title">Microclimate by quadrant</div><div class="section-note">Select a bar to update the selected quadrant. Bars use a focused axis range for easier comparison.</div>', unsafe_allow_html=True)
    chart_metric = st.radio("Chart metric", ["WBT", "Air temperature", "Humidity"], horizontal=True, label_visibility="collapsed")
    metric_key = {"WBT": "wbt", "Air temperature": "temperature", "Humidity": "humidity"}[chart_metric]
    units = "°C" if chart_metric != "Humidity" else "%"
    chart_values = {q: rows[q][metric_key] for q in rows}
    chart_min, chart_max = min(chart_values.values()), max(chart_values.values())
    chart_span = chart_max - chart_min or 1
    non_wbt_colors = ["#d9e3d8", "#a9c2aa", "#73977b", "#456f53", "#285b43"]
    bar_colors = [
        wbt_color(chart_values[q]) if chart_metric == "WBT"
        else non_wbt_colors[min(4, int((chart_values[q] - chart_min) / chart_span * 5))]
        for q in rows
    ]
    selected_q = st.session_state.selected_quadrant
    bar_lines = ["#173c2a" if q == selected_q else "#fffdf7" for q in rows]
    bar_widths = [3 if q == selected_q else 1 for q in rows]
    chart = go.Figure(go.Bar(
        x=[f"Q{q}" for q in rows],
        y=[chart_values[q] - chart_min for q in rows],
        base=[chart_min] * len(rows),
        customdata=[[q, chart_values[q]] for q in rows],
        marker={"color": bar_colors, "line": {"color": bar_lines, "width": bar_widths}},
        text=[f"{chart_values[q]:g}" for q in rows],
        textposition="outside",
        hovertemplate=f"Quadrant %{{customdata[0]}}<br>{chart_metric}: %{{customdata[1]:.1f}} {units}<extra></extra>",
    ))
    chart.update_layout(
        height=330, margin={"l": 15, "r": 15, "t": 25, "b": 10},
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", showlegend=False,
        clickmode="event+select",
        yaxis={"title": units, "range": [chart_min, chart_max + chart_span * 0.18], "gridcolor": "#e2e4da"},
        xaxis={"title": None}, font={"color": "#26352c"},
    )
    st.plotly_chart(chart, use_container_width=True, config={"displayModeBar": False}, key="microclimate_chart", on_select=sync_from_chart, selection_mode="points")

with detail_column:
    st.markdown('<div class="section-title">Selected quadrant</div><div class="section-note">Details and local-name records for the selected survey area.</div>', unsafe_allow_html=True)
    st.selectbox(
        "Quadrant", list(range(1, 7)), format_func=lambda q: f"Quadrant {q}",
        key="quadrant_selector", on_change=sync_from_selector, label_visibility="collapsed",
    )
    selected_q = st.session_state.selected_quadrant
    climate = rows[selected_q]
    tree = tree_info[selected_q]
    st.markdown(f"### Quadrant {selected_q} · {climate['wbt']:.1f} °C WBT")
    metric_col1, metric_col2 = st.columns(2)
    metric_col1.metric("Air temperature", f"{climate['temperature']:.1f} °C")
    metric_col2.metric("Relative humidity", f"{climate['humidity']:.1f}%")
    metric_col1, metric_col2 = st.columns(2)
    metric_col1.metric("Mean tree height", f"{tree['mean_height']:.1f} m" if tree["mean_height"] is not None else "Not recorded", help=f"{tree['height_method']}; n={tree['height_n']}")
    metric_col2.metric("Tree records", str(tree["tree_count"]))

    st.markdown("**Thermal image · centre readings**")
    ground_values = [value for value in THERMAL[selected_q]["ground"] if 0 <= value <= 60]
    canopy_values = [value for value in THERMAL[selected_q]["canopy"] if 0 <= value <= 60]
    ground_mean = sum(ground_values) / len(ground_values)
    canopy_mean = sum(canopy_values) / len(canopy_values)
    thermal_chart = go.Figure()
    thermal_chart.add_trace(go.Bar(x=[ground_mean], y=["Ground"], orientation="h", marker_color="#91b29a", text=[f"{ground_mean:.1f} °C"], textposition="outside", name="Ground", hovertemplate="Ground mean: %{x:.1f} °C<extra></extra>"))
    thermal_chart.add_trace(go.Bar(x=[canopy_mean], y=["Canopy"], orientation="h", marker_color="#d49a58", text=[f"{canopy_mean:.1f} °C"], textposition="outside", name="Canopy", hovertemplate="Canopy mean: %{x:.1f} °C<extra></extra>"))
    thermal_chart.update_layout(barmode="group", height=125, margin={"l": 8, "r": 8, "t": 5, "b": 5}, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", showlegend=False, xaxis={"title": None, "visible": False, "range": [0, 45]}, yaxis={"title": None}, font={"color": "#26352c"})
    st.plotly_chart(thermal_chart, use_container_width=True, config={"displayModeBar": False})
    if any(value < 0 or value > 60 for value in THERMAL[selected_q]["canopy"]):
        st.caption(f"Reported thermal ranges: ground {THERMAL[selected_q]['ground_range']} °C; canopy {THERMAL[selected_q]['canopy_range']} °C. Displayed canopy mean excludes readings outside 0–60 °C.")
    else:
        st.caption(f"Reported ranges: ground {THERMAL[selected_q]['ground_range']} °C; canopy {THERMAL[selected_q]['canopy_range']} °C.")

    st.markdown("**Local-name breakdown**")
    species_counts = tree["species_counts"]
    if species_counts:
        tags = " ".join(f'<span class="species-tag">{name} · {count}</span>' for name, count in species_counts.items())
        st.markdown(tags, unsafe_allow_html=True)
    else:
        st.caption("No local names recorded for this quadrant.")

    st.markdown("**WBT compared with survey mean**")
    survey_wbt_mean = sum(item["wbt"] for item in rows.values()) / len(rows)
    comparison_chart = go.Figure(go.Bar(
        x=[survey_wbt_mean, climate["wbt"]], y=["Survey mean", f"Quadrant {selected_q}"],
        orientation="h", marker_color=["#b9c9b8", wbt_color(climate["wbt"])],
        text=[f"{survey_wbt_mean:.1f} °C", f"{climate['wbt']:.1f} °C"], textposition="outside",
        hovertemplate="%{y}: %{x:.1f} °C<extra></extra>",
    ))
    comparison_chart.update_layout(height=115, margin={"l": 8, "r": 35, "t": 0, "b": 0}, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", showlegend=False, xaxis={"title": None, "visible": False, "range": [0, max(all_wbt) * 1.2]}, yaxis={"title": None}, font={"color": "#26352c"})
    st.plotly_chart(comparison_chart, use_container_width=True, config={"displayModeBar": False})
    st.caption(f"Height from {tree['height_method']} measurements (n={tree['height_n']}); Q1–Q5 and Q6 use different measurement methods.")

# The comparison table now occupies the former full-width chart section.
st.write("")
st.markdown('<div class="section-title">Quadrant comparison</div><div class="section-note">Select a row to update the map and selected-quadrant details.</div>', unsafe_allow_html=True)
summary = []
for q in rows:
    item = tree_info[q]
    summary.append({
        "Quadrant": f"Q{q}", "WBT (°C)": rows[q]["wbt"],
        "Air temp. (°C)": rows[q]["temperature"], "Humidity (%)": rows[q]["humidity"],
        "Mean height (m)": round(item["mean_height"], 1) if item["mean_height"] is not None else None,
        "Trees": item["tree_count"], "Most common": item["common"],
    })
summary_df = pd.DataFrame(summary)


def shade_wbt(value):
    return f"background-color: {wbt_color(float(value))}; color: #26352c;"


humidity_min, humidity_max = summary_df["Humidity (%)"].min(), summary_df["Humidity (%)"].max()


def shade_humidity(value):
    fraction = 0 if humidity_max == humidity_min else (float(value) - humidity_min) / (humidity_max - humidity_min)
    color = mix_color((232, 239, 229), (145, 178, 154), fraction)
    return "background-color: #{:02x}{:02x}{:02x}; color: #26352c;".format(*color)


styled_summary = (
    summary_df.style
    .map(shade_wbt, subset=["WBT (°C)"])
    .map(shade_humidity, subset=["Humidity (%)"])
    .set_properties(subset=["Most common"], **{"background-color": "#e7eee5", "color": "#285b43", "font-weight": "600"})
    .format({"WBT (°C)": "{:.1f}", "Air temp. (°C)": "{:.1f}", "Humidity (%)": "{:.1f}", "Mean height (m)": "{:.1f}"})
)
st.dataframe(
    styled_summary, use_container_width=True, hide_index=True,
    on_select=sync_from_table, selection_mode="single-row", key="comparison_table",
    column_config={
        "Quadrant": st.column_config.TextColumn("Quadrant", width="small"),
        "WBT (°C)": st.column_config.NumberColumn("WBT (°C)", width="small"),
        "Air temp. (°C)": st.column_config.NumberColumn("Air temp. (°C)", width="small"),
        "Humidity (%)": st.column_config.NumberColumn("Humidity (%)", width="small"),
        "Mean height (m)": st.column_config.NumberColumn("Mean height (m)", width="small"),
        "Trees": st.column_config.NumberColumn("Trees", width="small"),
        "Most common": st.column_config.TextColumn("Most common", width="small"),
    },
)

st.markdown('<div class="closing">', unsafe_allow_html=True)
st.download_button("Download quadrant summary CSV", summary_df.to_csv(index=False), file_name="karnala-quadrant-summary.csv", mime="text/csv")
st.caption("Field data supplied by Statistical Ecology Group 04. Thermal camera values should be reviewed against the original images before formal analysis.")
st.markdown("</div>", unsafe_allow_html=True)

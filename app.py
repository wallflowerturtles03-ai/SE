from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="Karnala Field Notes",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed",
)

ROOT = Path(__file__).parent
WBT_FILE = ROOT / "Statistcial Ecology Group_4 - WBT.csv"
TREE_FILE = ROOT / "Statistcial Ecology Group_4 - Tree.csv"

# Polygons are copied from the supplied Google Earth KML. Q1 has no quadrant
# polygon in that KML, so it is intentionally shown as an observation marker.
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
    wbt = wbt.rename(columns={"qudrant": "quadrant", "quadrant ": "quadrant", "temprature": "temperature", "temperature ": "temperature"})

    trees = pd.read_csv(TREE_FILE)
    trees.columns = [str(c).strip() for c in trees.columns]
    q_col = next(c for c in trees.columns if c.lower().strip() == "quadrant")
    name_col = next(c for c in trees.columns if c.lower().strip() == "local name")
    trees[q_col] = pd.to_numeric(trees[q_col], errors="coerce").ffill().astype(int)
    top_col = next(c for c in trees.columns if c.lower().strip() == "height 2p (top)")
    hag_col = next(c for c in trees.columns if c.lower().strip() == "height hagameter 20m")

    result = {}
    for q in range(1, 7):
        rows = trees[trees[q_col] == q]
        height_col = hag_col if q == 6 else top_col
        heights = pd.to_numeric(rows[height_col], errors="coerce").dropna()
        counts = rows[name_col].dropna().astype(str).value_counts()
        result[q] = {
            "tree_count": len(rows),
            "mean_height": float(heights.mean()) if not heights.empty else None,
            "height_n": int(heights.size),
            "height_method": "Hagameter 20m" if q == 6 else "2P top",
            "common": counts.index[0] if not counts.empty else "Not recorded",
            "common_count": int(counts.iloc[0]) if not counts.empty else 0,
            "species_count": int(rows[name_col].nunique()),
        }
    wbt = wbt.rename(columns={"qudrant":"quadrant", "temprature":"temperature"})
    return wbt, result

wbt_df, tree_info = load_data()
rows = {}
for _, row in wbt_df.iterrows():
    q = int(row["quadrant"])
    rows[q] = {"wbt": float(row["wbt"]), "temperature": float(row["temperature"]), "humidity": float(row["humidity"])}

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');
html,body,[class*="css"]{font-family:'DM Sans',sans-serif} .block-container{max-width:1500px;padding-top:1.2rem;padding-bottom:2rem}
.hero{padding:.5rem 0 1.1rem}.eyebrow{font-size:.72rem;letter-spacing:.14em;text-transform:uppercase;color:#718078;font-weight:700}.hero h1{font-family:Manrope,sans-serif;font-size:2.25rem;letter-spacing:-.05em;margin:.4rem 0}.hero p{color:#758078;margin:0}
.kpi{background:white;border:1px solid #e6e9e2;border-radius:15px;padding:17px 18px;min-height:105px}.kpi-label{font-size:.8rem;color:#758078}.kpi-value{font:800 1.55rem Manrope,sans-serif;margin:.35rem 0}.kpi-foot{font-size:.72rem;color:#8a948c}
.panel{background:white;border:1px solid #e6e9e2;border-radius:15px;padding:17px 18px;margin-bottom:1rem}.panel-title{font:700 1rem Manrope,sans-serif;margin:0}.panel-sub{font-size:.76rem;color:#758078;margin:.25rem 0 .75rem}.map-hint{font-size:.75rem;color:#758078;margin-top:.3rem}.data-note{background:#fff8ec;border:1px solid #f4e4c7;padding:10px;border-radius:9px;color:#86653c;font-size:.78rem}
[data-testid="stMetricValue"]{font-family:Manrope,sans-serif}.stDownloadButton button{border-radius:9px}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="hero"><div class="eyebrow">Biodiversity & microclimate survey</div><h1>A closer look at the forest.</h1><p>Explore field observations across six survey quadrants at Karnala Wildlife Sanctuary.</p></div>', unsafe_allow_html=True)

all_wbt = [rows[q]["wbt"] for q in rows]
all_species = set()
for info in tree_info.values():
    all_species.add(info["common"])

c1,c2,c3,c4 = st.columns(4)
for col,label,value,foot in [
    (c1,"Survey quadrants","06","Mapped field locations"),
    (c2,"Trees recorded",str(sum(x["tree_count"] for x in tree_info.values())),"Across all six quadrants"),
    (c3,"WBT range",f"{min(all_wbt):.1f}–{max(all_wbt):.1f} °C","Wet-bulb temperature"),
    (c4,"Distinct tree names",str(sum(x["species_count"] for x in tree_info.values())),"Quadrant species records summed"),
]:
    col.markdown(f'<div class="kpi"><div class="kpi-label">{label}</div><div class="kpi-value">{value}</div><div class="kpi-foot">{foot}</div></div>', unsafe_allow_html=True)

st.write("")
map_col, detail_col = st.columns([1.55, 1], gap="medium")
with map_col:
    st.markdown('<div class="panel-title">Quadrant field map</div><div class="panel-sub">Hover over a shape or marker for a quick summary. Select a quadrant to view details.</div>', unsafe_allow_html=True)
    metric_label = st.selectbox("Color polygons by", ["WBT", "Air temperature", "Tree count"], horizontal=True, label_visibility="collapsed")
    metric_key = {"WBT":"wbt", "Air temperature":"temperature", "Tree count":"tree_count"}[metric_label]
    values = {q: rows[q][metric_key] if metric_key != "tree_count" else tree_info[q]["tree_count"] for q in rows}
    low, high = min(values.values()), max(values.values())
    fig = go.Figure()
    for q in range(1,7):
        color_value = values[q]
        t = 0 if high == low else (color_value-low)/(high-low)
        hue = int(145 - 120*t)
        fill = f"hsl({hue}, 38%, {82-16*t:.0f}%)"
        if q in POLYGONS:
            coords = POLYGONS[q] + [POLYGONS[q][0]]
            fig.add_trace(go.Scatter(x=[p[0] for p in coords], y=[p[1] for p in coords], mode="lines", fill="toself", fillcolor=fill, line={"color":"#54805f","width":2}, name=f"Q{q}", customdata=[[q,rows[q]['wbt'],rows[q]['temperature'],tree_info[q]['common']]]*len(coords), hovertemplate="<b>Quadrant %{customdata[0]}</b><br>WBT %{customdata[1]} °C<br>Air %{customdata[2]} °C<br>Most common: %{customdata[3]}<extra></extra>"))
        fig.add_trace(go.Scatter(x=[CENTERS[q][0]],y=[CENTERS[q][1]],mode="markers+text",text=[f"Q{q}"],textposition="top center",marker={"size":12,"color":"#3f7954","line":{"color":"white","width":2}},name=f"Q{q} observation",customdata=[[q,rows[q]['wbt'],rows[q]['temperature'],tree_info[q]['common']]],hovertemplate="<b>Quadrant %{customdata[0]}</b><br>WBT %{customdata[1]} °C<br>Air %{customdata[2]} °C<br>Most common: %{customdata[3]}<extra></extra>",showlegend=False))
    fig.update_layout(height=390,margin={"l":5,"r":5,"t":10,"b":5},paper_bgcolor="white",plot_bgcolor="#eef1e8",showlegend=False,hoverlabel={"bgcolor":"white"},xaxis={"visible":False,"scaleanchor":"y","scaleratio":1},yaxis={"visible":False,"scaleanchor":"x","scaleratio":1},dragmode="pan")
    fig.add_annotation(x=73.115,y=18.893,xref="x",yref="y",text="No external map tiles · survey coordinates and KML boundaries",showarrow=False,font={"size":10,"color":"#67736a"},bgcolor="rgba(255,255,255,.82)")
    st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":True,"scrollZoom":False})
    st.caption("Q1 has no boundary polygon in the supplied KML, so it is shown as a survey-location marker. Map is key-free and uses no third-party basemap tiles.")

with detail_col:
    options = list(range(1,7))
    selected_q = st.selectbox("Selected quadrant",options,format_func=lambda q:f"Quadrant {q}")
    r, tree = rows[selected_q], tree_info[selected_q]
    st.markdown(f"### Quadrant {selected_q}  ·  {r['wbt']:.1f} °C WBT")
    a,b=st.columns(2)
    a.metric("Air temperature",f"{r['temperature']:.1f} °C")
    b.metric("Relative humidity",f"{r['humidity']:.1f}%")
    a,b=st.columns(2)
    a.metric("Mean tree height",f"{tree['mean_height']:.1f} m" if tree['mean_height'] is not None else "Not recorded",help=f"{tree['height_method']}; n={tree['height_n']}")
    b.metric("Tree records",str(tree['tree_count']))
    st.markdown("**Most recorded local name**")
    st.write(f"{tree['common']} · {tree['common_count']} trees · {tree['species_count']} local names in this quadrant")
    thermal=THERMAL[selected_q]
    g=[x for x in thermal['ground'] if 0<=x<=60]; c=[x for x in thermal['canopy'] if 0<=x<=60]
    st.markdown("**Thermal image · centre readings**")
    a,b=st.columns(2)
    a.metric("Ground mean",f"{sum(g)/len(g):.1f} °C",help=f"Reported range {thermal['ground_range']} °C")
    b.metric("Canopy mean*",f"{sum(c)/len(c):.1f} °C",help=f"Reported range {thermal['canopy_range']} °C")
    if any(x<0 or x>60 for x in thermal['canopy']):
        st.info("Source canopy readings include negative or unusually high values. The displayed mean excludes values outside 0–60 °C; ranges retain the reported values.")
    st.caption(f"Height from {tree['height_method']} measurements (n={tree['height_n']}). Q1–Q5 and Q6 use different measurement methods.")

st.write("")
chart_col, table_col = st.columns([1,1.5],gap="medium")
with chart_col:
    st.markdown('<div class="panel-title">Microclimate by quadrant</div><div class="panel-sub">Compare readings across the survey area</div>',unsafe_allow_html=True)
    chart_metric=st.radio("Chart metric",["WBT","Air temperature","Humidity"],horizontal=True,label_visibility="collapsed")
    ck={"WBT":"wbt","Air temperature":"temperature","Humidity":"humidity"}[chart_metric]
    bar=go.Figure(go.Bar(x=[f"Q{q}" for q in rows],y=[rows[q][ck] for q in rows],marker_color=["#285b43" if q==selected_q else "#83a98a" for q in rows],text=[f"{rows[q][ck]:g}" for q in rows],textposition="outside",hovertemplate="%{x}: %{y}<extra></extra>"))
    bar.update_layout(height=290,margin={"l":5,"r":5,"t":15,"b":5},paper_bgcolor="white",plot_bgcolor="white",showlegend=False,yaxis={"title":"°C" if ck!="humidity" else "%","gridcolor":"#edf0ea"},xaxis={"title":""})
    st.plotly_chart(bar,use_container_width=True,config={"displayModeBar":False})
with table_col:
    st.markdown('<div class="panel-title">Quadrant comparison</div><div class="panel-sub">Summary of the field measurements</div>',unsafe_allow_html=True)
    summary=[]
    for q in rows:
        t=tree_info[q]
        summary.append({"Quadrant":f"Q{q}","WBT (°C)":rows[q]["wbt"],"Air temp. (°C)":rows[q]["temperature"],"Humidity (%)":rows[q]["humidity"],"Mean height (m)":round(t["mean_height"],1) if t["mean_height"] is not None else None,"Trees":t["tree_count"],"Most common":t["common"]})
    st.dataframe(pd.DataFrame(summary),use_container_width=True,hide_index=True)

st.download_button("Download quadrant summary CSV",pd.DataFrame(summary).to_csv(index=False),file_name="karnala-quadrant-summary.csv",mime="text/csv")
st.caption("Field data supplied by Statistical Ecology Group 04. Thermal camera values should be reviewed against the original images before formal analysis.")

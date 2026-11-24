# Karnala Field Notes

A Streamlit dashboard for the Karnala Wildlife Sanctuary ecology survey. It includes a key-free interactive coordinate map, quadrant details, microclimate chart, comparison table, and CSV export.

## Run locally

Python 3.10+ recommended.

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Keep `app.py`, `requirements.txt`, and the two source CSVs in the repository root. The app reads the WBT and tree measurements from the supplied CSV files. The thermal centre values are included from the supplied thermal CSV after normalizing its multi-row headers.

## Deploy on Streamlit Community Cloud

1. Push the project files and source CSVs to GitHub.
2. Go to https://share.streamlit.io/ and sign in with GitHub.
3. Choose **Create app**, select this repository and branch, and set the main file to `app.py`.
4. Deploy. The Plotly map draws the provided coordinates and KML outlines directly, so it does not request map tiles or need a map API key.

Q1 has observation points but no quadrant polygon in the supplied KML; it is displayed as a point rather than inventing a boundary. Q1–Q5 tree heights use 2P top observations while Q6 uses Hagameter 20m readings, so height comparisons are method-dependent. Thermal canopy data contains anomalous negative and very high values; the displayed mean excludes values outside 0–60 °C and should be checked against original images.

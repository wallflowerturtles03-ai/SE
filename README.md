# Karnala Field Notes

A responsive, single-page dashboard for the Statistical Ecology Group 04 field survey at Karnala Wildlife Sanctuary.

## View the dashboard

Open `index.html` in a browser, or enable GitHub Pages for this repository and use the repository's Pages URL. The page uses Leaflet and OpenStreetMap tiles, so an internet connection is required to display the basemap. No build step or package installation is needed.

## Dashboard features

- Interactive map of the six quadrants, using the supplied `Karnala_fw.kml` coordinates and boundaries where available.
- Hover, click, or tap a quadrant to view WBT, air temperature, humidity, tree height, dominant local tree name, and thermal observations.
- Map coloring by WBT, air temperature, or number of recorded trees.
- Microclimate comparison chart and quadrant comparison table.
- Export a normalized quadrant summary as CSV.

## Notes on interpreting the data

- The KML contains polygon boundaries for Q2–Q4 and Q6, and a boundary for Q5. Q1 has nearby survey points but no quadrant polygon, so the map shows an approximate outline based on those points. Q5 and Q6 are in a separate cluster from Q1–Q4, as in the supplied coordinates.
- Tree height values use available `Height 2P (Top)` observations for Q1–Q5 and `Height Hagameter 20m` for Q6. Q4 has seven usable 2P top measurements from 11 tree records. These methods are not directly comparable; the detail panel labels the method.
- Thermal data includes negative values and values recorded as `160+`. The thermal centre averages shown exclude negative values and values above 60 °C; source ranges remain visible in the quadrant detail. Review these readings against the original images before using the averages in formal analysis.
- The displayed common species are local names from the tree survey, not taxonomically validated scientific names. Q5 has a tie between Sag and Chera.

## Source data

The dashboard is based on the CSV and KML files stored alongside this page. The source files are preserved as supplied.

import pandas as pd
import sqlite3
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import FancyBboxPatch, Patch
import matplotlib.patheffects as pe
import numpy as np

conn = sqlite3.connect('data/ms_health.db')
df = pd.read_sql_query('''
    SELECT
        c.fips,
        c.county_name,
        c.population,
        h.diabetes_rate,
        h.obesity_rate,
        s.poverty_rate,
        s.svi_score,
        r.composite_risk_score,
        r.risk_rank,
        r.high_risk_flag,
        r.primary_risk_driver
    FROM counties c
    JOIN health_indicators h ON c.fips = h.fips
    JOIN social_vulnerability s ON c.fips = s.fips
    JOIN risk_scores r ON c.fips = r.fips
''', conn)
conn.close()

url = 'https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json'
gdf = gpd.read_file(url)

gdf = gdf[gdf['STATE'] == '28'].copy()
gdf = gdf.rename(columns={'id': 'fips'})
gdf = gdf.merge(df, on='fips', how='left')

BG        = '#ffffff'
TXT_DARK  = '#1f2937'
TXT_MID   = '#4b5563'
TXT_LIGHT = '#9ca3af'
GRID      = '#e5e7eb'
SOURCE    = 'Source: CDC PLACES (2025 Release)  |  CDC/ATSDR Social Vulnerability Index (SVI 2022)  |  Analysis: Mississippi Health Risk Project'

RISK_CMAP = LinearSegmentedColormap.from_list('risk',
    ['#d4edda', '#fff3cd', '#f8d7da', '#c0392b'], N=256)

fig, ax = plt.subplots(1, 1, figsize=(13, 11), facecolor=BG)
ax.set_facecolor(BG)

gdf.plot(
    column='composite_risk_score',
    cmap=RISK_CMAP,
    linewidth=0.5,
    edgecolor='white',
    ax=ax,
    vmin=0,
    vmax=1,
    missing_kwds={'color': '#f0f0f0'}
)

high_risk = gdf[gdf['high_risk_flag'] == 1]
high_risk.plot(
    ax=ax,
    facecolor='none',
    edgecolor='#c0392b',
    linewidth=1.8,
    linestyle='--'
)

label_counties = gdf[gdf['risk_rank'] <= 10].copy()
for _, row in label_counties.iterrows():
    if row.geometry is None:
        continue
    cx = row.geometry.centroid.x
    cy = row.geometry.centroid.y
    name = row['county_name']
    score = row['composite_risk_score']

    ax.text(cx, cy + 0.06, name,
            fontsize=7.5, ha='center', va='bottom',
            color='#1f2937', fontweight='700',
            path_effects=[pe.withStroke(linewidth=2, foreground='white')])
    ax.text(cx, cy - 0.06, f'{score:.3f}',
            fontsize=6.5, ha='center', va='top',
            color='#555555',
            path_effects=[pe.withStroke(linewidth=2, foreground='white')])

# Hattiesburg area: Forrest County (28035) and Lamar County (28073)
hattiesburg_fips = ['28035', '28073']
hatt_counties = gdf[gdf['fips'].isin(hattiesburg_fips)]

hatt_counties.plot(
    ax=ax,
    facecolor='none',
    edgecolor='#2f80ed',
    linewidth=2.2,
    linestyle='-'
)

for _, row in hatt_counties.iterrows():
    if row.geometry is None:
        continue
    cx = row.geometry.centroid.x
    cy = row.geometry.centroid.y
    ax.text(cx, cy + 0.06, row['county_name'],
            fontsize=7.5, ha='center', va='bottom',
            color='#2f80ed', fontweight='700',
            path_effects=[pe.withStroke(linewidth=2, foreground='white')])
    ax.text(cx, cy - 0.06, f'{row["composite_risk_score"]:.3f}',
            fontsize=6.5, ha='center', va='top',
            color='#2f80ed',
            path_effects=[pe.withStroke(linewidth=2, foreground='white')])

ax.set_axis_off()

fig.text(0.5, 0.94,
         'Mississippi County Health Risk Map',
         fontsize=20, fontweight='bold', color=TXT_DARK,
         ha='center', va='top')

fig.text(0.5, 0.905,
         'Composite risk score by county  ·  dashed border = high-risk flag (top quartile + SVI > 0.75)',
         fontsize=11, color=TXT_MID, ha='center', va='top')

sm = plt.cm.ScalarMappable(cmap=RISK_CMAP, norm=plt.Normalize(vmin=0, vmax=1))
sm.set_array([])
cbar_ax = fig.add_axes([0.88, 0.18, 0.018, 0.55])
cb = fig.colorbar(sm, cax=cbar_ax)
cb.set_label('Composite Risk Score', fontsize=10, color=TXT_MID, labelpad=10)
cb.outline.set_visible(False)
cb.ax.yaxis.set_tick_params(color=TXT_LIGHT, labelsize=9)
plt.setp(cb.ax.yaxis.get_ticklabels(), color=TXT_MID)

cb.ax.axhline(y=0.75, color='#c0392b', linewidth=1.5,
              linestyle='--', xmin=-1.5, xmax=2.5, clip_on=False)
cb.ax.text(1.8, 0.75, 'High-risk\nthreshold',
           fontsize=8, color='#c0392b', va='center',
           transform=cb.ax.transAxes)

legend_items = [
    Patch(facecolor='#d4edda', edgecolor=GRID, label='Low risk (0.0 - 0.25)'),
    Patch(facecolor='#fff3cd', edgecolor=GRID, label='Moderate risk (0.25 - 0.50)'),
    Patch(facecolor='#f8d7da', edgecolor=GRID, label='High risk (0.50 - 0.75)'),
    Patch(facecolor='#c0392b', edgecolor=GRID, label='Critical risk (0.75 - 1.00)'),
    mpatches.Patch(facecolor='none', edgecolor='#c0392b',
                   linestyle='--', linewidth=1.8,
                   label='High-risk flag (top quartile + SVI > 0.75)'),
    mpatches.Patch(facecolor='none', edgecolor='#2f80ed',
                   linewidth=2.2,
                   label='Hattiesburg area (Forrest & Lamar)'),
]

leg = ax.legend(handles=legend_items, loc='lower left',
                fontsize=9, frameon=True, framealpha=1,
                edgecolor=GRID, borderpad=0.9,
                handlelength=1.6, handleheight=1.2)
leg.get_frame().set_linewidth(1)
for t in leg.get_texts():
    t.set_color(TXT_DARK)

fig.text(0.5, 0.03, SOURCE, fontsize=8.5,
         color=TXT_LIGHT, ha='center', va='bottom', style='italic')

plt.savefig('output/map_mississippi_risk.png',
            bbox_inches='tight', facecolor=BG, dpi=180)
plt.close()
print("Saved output/map_mississippi_risk.png")
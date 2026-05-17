import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import os

os.makedirs('output', exist_ok=True)
conn = sqlite3.connect('data/ms_health.db')

df = pd.read_sql_query('''
    SELECT
        c.fips,
        c.county_name,
        c.population,
        h.diabetes_rate,
        h.obesity_rate,
        h.hypertension_rate,
        h.copd_rate,
        s.svi_score,
        s.poverty_rate,
        s.uninsured_rate,
        r.composite_risk_score,
        r.risk_rank,
        r.high_risk_flag,
        r.primary_risk_driver
    FROM counties c
    JOIN health_indicators h ON c.fips = h.fips
    JOIN social_vulnerability s ON c.fips = s.fips
    JOIN risk_scores r ON c.fips = r.fips
    ORDER BY r.risk_rank
''', conn)
conn.close()

BG          = '#ffffff'
GRID        = '#e5e7eb'
TXT_DARK    = '#1f2937'
TXT_MID     = '#4b5563'
TXT_LIGHT   = '#9ca3af'

C_BLUE   = '#2f80ed'
C_AMBER  = '#f5a623'
C_RED    = '#eb5757'
C_TEAL   = '#27ae60'
C_PURPLE = '#9b51e0'

plt.rcParams.update({
    'font.family':        'DejaVu Sans',
    'font.size':          10.5,
    'text.color':         TXT_DARK,
    'axes.labelcolor':    TXT_MID,
    'xtick.color':        TXT_MID,
    'ytick.color':        TXT_MID,
    'xtick.labelsize':    10,
    'ytick.labelsize':    10,
    'axes.spines.top':    False,
    'axes.spines.right':  False,
    'axes.spines.left':   False,
    'axes.spines.bottom': True,
    'axes.edgecolor':     '#d1d5db',
    'axes.linewidth':     0.8,
    'figure.dpi':         180,
})

SOURCE = 'Source: CDC PLACES (2025 Release)  |  CDC/ATSDR Social Vulnerability Index (SVI 2022)  |  Analysis: Mississippi Health Risk Project'

def add_footer(fig):
    fig.text(0.05, 0.02, SOURCE, fontsize=8.5,
             color=TXT_LIGHT, ha='left', va='bottom', style='italic')


# Chart 1: Top 15 counties by composite risk score
fig, ax = plt.subplots(figsize=(11, 7.5), facecolor=BG)
top15 = df.head(15).sort_values('composite_risk_score')
colors = [C_RED if f == 1 else C_BLUE for f in top15['high_risk_flag']]
bars = ax.barh(top15['county_name'], top15['composite_risk_score'],
               color=colors, height=0.65, zorder=3)

ax.set_xlabel('Composite Risk Score', fontsize=10.5, labelpad=10, color=TXT_MID)
ax.set_title('Top 15 Highest-Risk Counties in Mississippi',
             fontsize=15, fontweight='bold', pad=18, color=TXT_DARK)
ax.set_xlim(0, 1.18)
ax.xaxis.grid(True, color=GRID, linewidth=0.8, linestyle='--', zorder=0)
ax.yaxis.grid(False)
ax.tick_params(axis='y', length=0, pad=6, labelsize=10.5)
ax.tick_params(axis='x', length=0)

ax.axvline(x=0.75, color=TXT_LIGHT, linestyle='--', linewidth=1, alpha=0.7)
ax.text(0.755, len(top15) - 0.5, 'High-risk\nthreshold',
        fontsize=8.5, color=TXT_LIGHT, va='center', style='italic')

red_patch  = mpatches.Patch(color=C_RED,  label='High-risk flag (top quartile + SVI > 0.75)')
blue_patch = mpatches.Patch(color=C_BLUE, label='Elevated risk')
leg = ax.legend(handles=[red_patch, blue_patch], fontsize=9.5,
                loc='lower right', bbox_to_anchor=(1.0, 0.12),
                frameon=True, framealpha=1,
                edgecolor=GRID, borderpad=0.8)
leg.get_frame().set_linewidth(1)

for bar, score in zip(bars, top15['composite_risk_score']):
    ax.text(bar.get_width() + 0.012, bar.get_y() + bar.get_height() / 2,
            f'{score:.3f}', va='center', fontsize=9.5,
            color=TXT_DARK, fontweight='600')

plt.tight_layout()
add_footer(fig)
plt.subplots_adjust(bottom=0.10)
plt.savefig('output/chart1_top15_risk.png', bbox_inches='tight', facecolor=BG)
plt.close()
print("Saved chart1_top15_risk.png")


# Chart 2: Poverty rate vs diabetes rate scatter
from matplotlib.colors import LinearSegmentedColormap
RISK_CMAP = LinearSegmentedColormap.from_list('risk',
    [C_TEAL, C_AMBER, C_RED], N=256)

fig, ax = plt.subplots(figsize=(10, 7.5), facecolor=BG)
scatter = ax.scatter(
    df['poverty_rate'], df['diabetes_rate'],
    c=df['composite_risk_score'], cmap=RISK_CMAP,
    vmin=0, vmax=1,
    s=df['population'] / 350, alpha=0.78,
    edgecolors='white', linewidth=1.2, zorder=3
)

cbar = plt.colorbar(scatter, ax=ax, pad=0.02)
cbar.set_label('Composite Risk Score', fontsize=9.5, color=TXT_MID, labelpad=8)
cbar.outline.set_visible(False)
cbar.ax.yaxis.set_tick_params(color=TXT_LIGHT, labelsize=8.5)
plt.setp(cbar.ax.yaxis.get_ticklabels(), color=TXT_MID)

ax.set_xlabel('Poverty Rate (%)', fontsize=10.5, labelpad=10, color=TXT_MID)
ax.set_ylabel('Diabetes Rate (%)', fontsize=10.5, labelpad=10, color=TXT_MID)
ax.set_title('Poverty Rate vs Diabetes Rate Across Mississippi',
             fontsize=15, fontweight='bold', pad=10, color=TXT_DARK)
ax.text(0.5, 0.98, 'Bubble size = county population',
        ha='center', fontsize=10, color=TXT_MID, transform=ax.transAxes)

ax.xaxis.grid(True, color=GRID, linewidth=0.8, linestyle='--', zorder=0)
ax.yaxis.grid(True, color=GRID, linewidth=0.8, linestyle='--', zorder=0)
ax.tick_params(axis='both', length=0)

for _, row in df[df['high_risk_flag'] == 1].iterrows():
    ax.annotate(row['county_name'],
                (row['poverty_rate'], row['diabetes_rate']),
                fontsize=8.5, color=TXT_DARK, fontweight='600',
                xytext=(6, 5), textcoords='offset points',
                arrowprops=dict(arrowstyle='-', color=TXT_LIGHT, lw=0.5))

z = np.polyfit(df['poverty_rate'], df['diabetes_rate'], 1)
p = np.poly1d(z)
x_line = np.linspace(df['poverty_rate'].min(), df['poverty_rate'].max(), 100)
ax.plot(x_line, p(x_line), '--', color=TXT_LIGHT, linewidth=1.3,
        label='Trend line', zorder=2)

leg = ax.legend(fontsize=9.5, frameon=False, loc='upper left')
for t in leg.get_texts():
    t.set_color(TXT_MID)

plt.tight_layout()
add_footer(fig)
plt.subplots_adjust(bottom=0.10)
plt.savefig('output/chart2_poverty_vs_diabetes.png', bbox_inches='tight', facecolor=BG)
plt.close()
print("Saved chart2_poverty_vs_diabetes.png")


# Chart 3: Health outcomes by SVI vulnerability tier
tiers = ['Low vulnerability (Q1)', 'Medium-low (Q2)', 'Medium-high (Q3)', 'High vulnerability (Q4)']
metrics = {
    'Diabetes Rate':     ([14.47, 16.54, 17.43, 20.53], C_BLUE),
    'Obesity Rate':      ([38.52, 41.64, 42.98, 46.84], C_AMBER),
    'Hypertension Rate': ([43.31, 46.84, 47.73, 51.88], C_RED),
}
x = np.arange(len(tiers))
width = 0.26
gap   = 0.015

fig, ax = plt.subplots(figsize=(12, 7), facecolor=BG)

for i, (metric, (values, color)) in enumerate(metrics.items()):
    offset = (i - 1) * (width + gap)
    rects  = ax.bar(x + offset, values, width, label=metric,
                    color=color, alpha=0.95, zorder=3, linewidth=0)
    for rect in rects:
        h = rect.get_height()
        ax.text(rect.get_x() + rect.get_width() / 2, h + 0.8,
                f'{h:.1f}%', ha='center', va='bottom',
                fontsize=9.5, color=TXT_DARK, fontweight='600')

ax.set_xticks(x)
ax.set_xticklabels(tiers, fontsize=10.5, color=TXT_DARK)
ax.set_ylabel('Average Rate (%)', fontsize=10.5, labelpad=10, color=TXT_MID)
ax.set_title('Health Outcomes Worsen as Social Vulnerability Increases',
             fontsize=15, fontweight='bold', pad=18, color=TXT_DARK)
ax.set_ylim(0, 62)
ax.yaxis.grid(True, color=GRID, linewidth=0.8, linestyle='--', zorder=0)
ax.xaxis.grid(False)
ax.tick_params(axis='x', length=0, pad=8)
ax.tick_params(axis='y', length=0)

leg = ax.legend(fontsize=10, frameon=True, framealpha=1,
                edgecolor=GRID, loc='upper left',
                handlelength=1.4, handleheight=1.0, borderpad=0.8)
leg.get_frame().set_linewidth(1)
for t in leg.get_texts():
    t.set_color(TXT_DARK)

plt.tight_layout()
add_footer(fig)
plt.subplots_adjust(bottom=0.12)
plt.savefig('output/chart3_svi_tier_outcomes.png', bbox_inches='tight', facecolor=BG)
plt.close()
print("Saved chart3_svi_tier_outcomes.png")


# Chart 4: Primary risk driver distribution
driver_counts = df['primary_risk_driver'].value_counts()
driver_colors_map = {
    'High social vulnerability':    C_RED,
    'High hypertension prevalence': C_AMBER,
    'High COPD prevalence':         C_BLUE,
    'High obesity prevalence':      C_TEAL,
    'High diabetes prevalence':     C_PURPLE,
}
colors4 = [driver_colors_map.get(d, TXT_LIGHT) for d in driver_counts.index]

fig, ax = plt.subplots(figsize=(9, 7.5), facecolor=BG)
wedges, texts, autotexts = ax.pie(
    driver_counts.values,
    labels=driver_counts.index,
    autopct='%1.0f%%',
    colors=colors4,
    startangle=140,
    pctdistance=0.75,
    wedgeprops={'edgecolor': BG, 'linewidth': 3, 'width': 0.45}
)

for text in texts:
    text.set_fontsize(10)
    text.set_color(TXT_DARK)
    text.set_fontweight('500')
for autotext in autotexts:
    autotext.set_fontsize(11)
    autotext.set_fontweight('bold')
    autotext.set_color(TXT_DARK)

ax.text(0, 0.08, str(driver_counts.sum()), ha='center', va='center',
        fontsize=28, fontweight='bold', color=TXT_DARK)
ax.text(0, -0.10, 'counties', ha='center', va='center',
        fontsize=11, color=TXT_MID)

ax.set_title('Primary Risk Driver Across 82 Mississippi Counties',
             fontsize=15, fontweight='bold', pad=20, color=TXT_DARK)

plt.tight_layout()
add_footer(fig)
plt.subplots_adjust(bottom=0.08)
plt.savefig('output/chart4_risk_driver_distribution.png',
            bbox_inches='tight', facecolor=BG)
plt.close()
print("Saved chart4_risk_driver_distribution.png")

print("\nAll charts saved to output/")
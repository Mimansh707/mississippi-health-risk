import pandas as pd
import sqlite3

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
        s.unemployment_rate,
        s.uninsured_rate
    FROM counties c
    JOIN health_indicators h ON c.fips = h.fips
    JOIN social_vulnerability s ON c.fips = s.fips
''', conn)

def normalize(series):
    return (series - series.min()) / (series.max() - series.min())

df['diabetes_norm']     = normalize(df['diabetes_rate'])
df['obesity_norm']      = normalize(df['obesity_rate'])
df['hypertension_norm'] = normalize(df['hypertension_rate'])
df['copd_norm']         = normalize(df['copd_rate'])

# SVI is already 0-1 from CDC
df['composite_risk_score'] = (
    0.25 * df['diabetes_norm'] +
    0.20 * df['obesity_norm'] +
    0.20 * df['hypertension_norm'] +
    0.25 * df['svi_score'] +
    0.10 * df['copd_norm']
)

df['composite_risk_score'] = df['composite_risk_score'].round(4)
df['risk_rank'] = df['composite_risk_score'].rank(ascending=False).astype(int)

df['high_risk_flag'] = (
    (df['composite_risk_score'] > df['composite_risk_score'].quantile(0.75)) &
    (df['svi_score'] > 0.75)
).astype(int)

# Identify the primary risk driver per county
health_cols = {
    'diabetes_norm':     'High diabetes prevalence',
    'obesity_norm':      'High obesity prevalence',
    'hypertension_norm': 'High hypertension prevalence',
    'copd_norm':         'High COPD prevalence',
    'svi_score':         'High social vulnerability',
}

df['primary_risk_driver'] = df[list(health_cols.keys())].idxmax(axis=1).map(health_cols)

cursor = conn.cursor()
cursor.execute('DROP TABLE IF EXISTS risk_scores')
cursor.execute('''
    CREATE TABLE risk_scores (
        fips                 TEXT PRIMARY KEY,
        composite_risk_score REAL,
        risk_rank            INTEGER,
        high_risk_flag       INTEGER,
        primary_risk_driver  TEXT,
        FOREIGN KEY (fips) REFERENCES counties(fips)
    )
''')

for _, row in df.iterrows():
    cursor.execute(
        'INSERT INTO risk_scores VALUES (?, ?, ?, ?, ?)',
        (row['fips'], row['composite_risk_score'],
         row['risk_rank'], row['high_risk_flag'],
         row['primary_risk_driver'])
    )

conn.commit()

print("Top 10 highest-risk counties:\n")
top10 = df.sort_values('composite_risk_score', ascending=False).head(10)
print(top10[['county_name', 'composite_risk_score', 'risk_rank',
             'high_risk_flag', 'primary_risk_driver']].to_string(index=False))

print(f"\nHigh-risk counties (top quartile + high SVI): {df['high_risk_flag'].sum()}")
conn.close()
print("\nRisk scores saved to risk_scores table in ms_health.db")
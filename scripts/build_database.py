import pandas as pd
import sqlite3

df = pd.read_csv('data/clean/ms_health_clean.csv', dtype={'fips': str})

conn = sqlite3.connect('data/ms_health.db')
cursor = conn.cursor()

cursor.executescript('''
    DROP TABLE IF EXISTS counties;
    DROP TABLE IF EXISTS health_indicators;
    DROP TABLE IF EXISTS social_vulnerability;

    CREATE TABLE counties (
        fips        TEXT PRIMARY KEY,
        county_name TEXT NOT NULL,
        population  INTEGER
    );

    CREATE TABLE health_indicators (
        fips              TEXT PRIMARY KEY,
        diabetes_rate     REAL,
        obesity_rate      REAL,
        hypertension_rate REAL,
        copd_rate         REAL,
        FOREIGN KEY (fips) REFERENCES counties(fips)
    );

    CREATE TABLE social_vulnerability (
        fips               TEXT PRIMARY KEY,
        poverty_rate       REAL,
        unemployment_rate  REAL,
        no_hs_diploma_rate REAL,
        uninsured_rate     REAL,
        no_vehicle_rate    REAL,
        svi_score          REAL,
        FOREIGN KEY (fips) REFERENCES counties(fips)
    );
''')

for _, row in df.iterrows():
    cursor.execute(
        'INSERT INTO counties VALUES (?, ?, ?)',
        (row['fips'], row['county_full'], int(row['population']))
    )
    cursor.execute(
        'INSERT INTO health_indicators VALUES (?, ?, ?, ?, ?)',
        (row['fips'], row['diabetes_rate'], row['obesity_rate'],
         row['hypertension_rate'], row['copd_rate'])
    )
    cursor.execute(
        'INSERT INTO social_vulnerability VALUES (?, ?, ?, ?, ?, ?, ?)',
        (row['fips'], row['poverty_rate'], row['unemployment_rate'],
         row['no_hs_diploma_rate'], row['uninsured_rate'],
         row['no_vehicle_rate'], row['svi_score'])
    )

conn.commit()

print("Tables created:")
for row in cursor.execute("SELECT name FROM sqlite_master WHERE type='table'"):
    print(" -", row[0])

for table in ['counties', 'health_indicators', 'social_vulnerability']:
    count = cursor.execute(f'SELECT COUNT(*) FROM {table}').fetchone()[0]
    print(f" {table}: {count} rows")

conn.close()
print("\nDatabase saved to data/ms_health.db")
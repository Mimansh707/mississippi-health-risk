import pandas as pd
import sqlite3
import os

conn = sqlite3.connect('data/ms_health.db')

queries = {
    'full_ranking':         open('sql/analysis_queries.sql').read().split(';')[0],
    'top10':                open('sql/analysis_queries.sql').read().split(';')[1],
    'high_risk_counties':   open('sql/analysis_queries.sql').read().split(';')[2],
    'poverty_vs_diabetes':  open('sql/analysis_queries.sql').read().split(';')[3],
    'svi_quartile_summary': open('sql/analysis_queries.sql').read().split(';')[4],
    'risk_driver_summary':  open('sql/analysis_queries.sql').read().split(';')[5],
}

os.makedirs('output', exist_ok=True)

for name, query in queries.items():
    query = query.strip()
    if not query:
        continue
    df = pd.read_sql_query(query, conn)
    df.to_csv(f'output/{name}.csv', index=False)
    print(f"\n=== {name} ===")
    print(df.to_string(index=False))

conn.close()
print("\nAll query results saved to output/")
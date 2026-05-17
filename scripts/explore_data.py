import pandas as pd

# Load datasets
places = pd.read_csv('data/raw/places_county.csv', dtype={'LocationID': str})
svi    = pd.read_csv('data/raw/svi_mississippi.csv', dtype={'FIPS': str})

# Filter PLACES to Mississippi only
ms_places = places[places['StateAbbr'] == 'MS']

print("=== PLACES: Mississippi rows ===")
print(f"Shape: {ms_places.shape}")
print(ms_places[['LocationName', 'Category', 'Measure', 'Data_Value']].head(20).to_string())

print("\n=== PLACES: Unique Measures ===")
print(ms_places['Measure'].unique())

print("\n=== SVI: Shape ===")
print(svi.shape)
print(svi.columns.tolist())
print(svi.head(5).to_string())
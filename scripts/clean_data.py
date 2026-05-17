import pandas as pd

places = pd.read_csv('data/raw/places_county.csv',
                     dtype={'LocationID': str}, low_memory=False)
svi    = pd.read_csv('data/raw/svi_mississippi.csv',
                     dtype={'FIPS': str})

measures = [
    'Diagnosed diabetes among adults',
    'Obesity among adults',
    'High blood pressure among adults',
    'Chronic obstructive pulmonary disease among adults',
]

ms = places[(places['StateAbbr'] == 'MS') &
            (places['Measure'].isin(measures)) &
            (places['Data_Value_Type'] == 'Crude prevalence')].copy()

ms = ms[['LocationID', 'LocationName', 'Measure', 'Data_Value']]

ms_pivot = ms.pivot_table(
    index=['LocationID', 'LocationName'],
    columns='Measure',
    values='Data_Value'
).reset_index()

# Rename columns
ms_pivot.columns.name = None
ms_pivot = ms_pivot.rename(columns={
    'LocationID':   'fips',
    'LocationName': 'county',
    'Diagnosed diabetes among adults':                          'diabetes_rate',
    'Obesity among adults':                                     'obesity_rate',
    'High blood pressure among adults':                         'hypertension_rate',
    'Chronic obstructive pulmonary disease among adults':       'copd_rate',
})

svi_cols = ['FIPS', 'COUNTY', 'E_TOTPOP',
            'EP_POV150', 'EP_UNEMP', 'EP_NOHSDP',
            'EP_UNINSUR', 'EP_NOVEH', 'RPL_THEMES']

svi_clean = svi[svi_cols].copy()
svi_clean = svi_clean.rename(columns={
    'FIPS':       'fips',
    'COUNTY':     'county_full',
    'E_TOTPOP':   'population',
    'EP_POV150':  'poverty_rate',
    'EP_UNEMP':   'unemployment_rate',
    'EP_NOHSDP':  'no_hs_diploma_rate',
    'EP_UNINSUR': 'uninsured_rate',
    'EP_NOVEH':   'no_vehicle_rate',
    'RPL_THEMES': 'svi_score',
})

svi_clean['county_full'] = svi_clean['county_full'].str.replace(' County', '', regex=False)

merged = pd.merge(ms_pivot, svi_clean, on='fips', how='inner')
merged = merged.dropna()

print(f"Merged shape: {merged.shape}")
print(merged.head(3).to_string())

merged.to_csv('data/clean/ms_health_clean.csv', index=False)
print("\nSaved to data/clean/ms_health_clean.csv")
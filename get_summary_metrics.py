import pandas as pd
file_path = "/Users/shetu/Downloads/SWW_RERA AREAs Final 28-1-26 Bajaj  (1).xlsx"
df = pd.read_excel(file_path, sheet_name="AREA statement ", header=None)
data_df = df.iloc[2:].copy()
data_df[0] = data_df[0].ffill()
data_df = data_df[data_df[1].notnull()]

columns_mapping = {
    0: 'FLOOR', 1: 'SL_NO', 2: 'TOWER', 3: 'FLAT_NO', 4: 'TYPE',
    5: 'SBA_SFT', 6: 'CARPET_SFT', 7: 'BALCONY_SFT', 8: 'BUILT_UP_SFT',
    9: 'WALL_SFT', 10: 'COMMON_SFT', 11: 'UDS_SFT', 12: 'PRIVATE_GARDEN_SFT'
}
data_df.rename(columns=columns_mapping, inplace=True)
data_df = data_df[list(columns_mapping.values())]

for col in ['SBA_SFT', 'CARPET_SFT', 'BALCONY_SFT', 'BUILT_UP_SFT', 'WALL_SFT', 'COMMON_SFT', 'UDS_SFT', 'PRIVATE_GARDEN_SFT']:
    data_df[col] = pd.to_numeric(data_df[col], errors='coerce')

total_units = len(data_df)
total_sba = data_df['SBA_SFT'].sum()
avg_carpet = data_df['CARPET_SFT'].mean()
total_garden = data_df['PRIVATE_GARDEN_SFT'].sum()

print("--- SUMMARY METRICS ---")
print(f"Total Units: {total_units}")
print(f"Total Saleable Area (SBA): {total_sba:,.2f} SFT")
print(f"Average Carpet Area: {avg_carpet:,.2f} SFT")
print(f"Total Private Garden Area: {total_garden:,.2f} SFT")

import pandas as pd
file_path = "/Users/shetu/Downloads/SWW_RERA AREAs Final 28-1-26 Bajaj  (1).xlsx"
df = pd.read_excel(file_path, sheet_name="AREA statement ", header=None)

# Process columns
data_df = df.iloc[2:].copy()
data_df[0] = data_df[0].ffill()
data_df = data_df[data_df[1].notnull()]

# Set column names
columns_mapping = {
    0: 'FLOOR', 1: 'SL_NO', 2: 'TOWER', 3: 'FLAT_NO', 4: 'TYPE',
    5: 'SBA_SFT', 6: 'CARPET_SFT', 7: 'BALCONY_SFT', 8: 'BUILT_UP_SFT',
    9: 'WALL_SFT', 10: 'COMMON_SFT', 11: 'UDS_SFT', 12: 'PRIVATE_GARDEN_SFT'
}
data_df.rename(columns=columns_mapping, inplace=True)
data_df = data_df[list(columns_mapping.values())]

# Show garden details
garden_units = data_df[data_df['PRIVATE_GARDEN_SFT'].notnull()]
print("Number of units with private garden values:", len(garden_units))
print("Floors of units with private garden:", garden_units['FLOOR'].unique())
print("Garden values distribution:")
print(garden_units['PRIVATE_GARDEN_SFT'].describe())
print(garden_units[['FLOOR', 'TOWER', 'FLAT_NO', 'TYPE', 'PRIVATE_GARDEN_SFT']])

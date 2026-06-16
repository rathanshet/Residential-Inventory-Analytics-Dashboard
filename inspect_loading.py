import pandas as pd
file_path = "/Users/shetu/Downloads/SWW_RERA AREAs Final 28-1-26 Bajaj  (1).xlsx"
df = pd.read_excel(file_path, sheet_name="AREA statement ", header=None)
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

for col in ['SBA_SFT', 'CARPET_SFT', 'BALCONY_SFT', 'BUILT_UP_SFT', 'WALL_SFT', 'COMMON_SFT']:
    data_df[col] = pd.to_numeric(data_df[col], errors='coerce')

data_df['SBA_DIFF'] = data_df['SBA_SFT'] - (data_df['BUILT_UP_SFT'] + data_df['COMMON_SFT'])
b_units = data_df[data_df['FLOOR'] != 'G ']

print("SBA - (BUILT_UP + COMMON) for B-type units (Floors 1-10):")
print(b_units['SBA_DIFF'].value_counts())

print("\nShow some rows with SBA_DIFF != 0:")
print(b_units[b_units['SBA_DIFF'] != 0][['FLOOR', 'TOWER', 'FLAT_NO', 'TYPE', 'SBA_SFT', 'BUILT_UP_SFT', 'COMMON_SFT', 'SBA_DIFF']])

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

# Calculate ratios
data_df['CARPET_RATIO'] = data_df['CARPET_SFT'] / data_df['SBA_SFT']
data_df['BALCONY_RATIO'] = data_df['BALCONY_SFT'] / data_df['SBA_SFT']
data_df['WALL_RATIO'] = data_df['WALL_SFT'] / data_df['SBA_SFT']
data_df['COMMON_RATIO'] = data_df['COMMON_SFT'] / data_df['SBA_SFT']

print("Average Contribution Ratios to SBA:")
print(f"Carpet Area Ratio:  {data_df['CARPET_RATIO'].mean() * 100:.2f}%")
print(f"Balcony Area Ratio: {data_df['BALCONY_RATIO'].mean() * 100:.2f}%")
print(f"Wall Area Ratio:    {data_df['WALL_RATIO'].mean() * 100:.2f}%")
print(f"Common Area Ratio:  {data_df['COMMON_RATIO'].mean() * 100:.2f}%")

print("\nBy Tower:")
tower_stats = data_df.groupby('TOWER').agg(
    avg_sba=('SBA_SFT', 'mean'),
    carpet_pct=('CARPET_RATIO', lambda x: x.mean() * 100),
    balcony_pct=('BALCONY_RATIO', lambda x: x.mean() * 100),
    common_pct=('COMMON_RATIO', lambda x: x.mean() * 100),
).reset_index()
print(tower_stats)

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

data_df['BUILT_UP_CALC'] = data_df['CARPET_SFT'] + data_df['BALCONY_SFT'] + data_df['WALL_SFT']
data_df['SBA_CALC'] = data_df['BUILT_UP_SFT'] + data_df['COMMON_SFT']
data_df['SBA_DIFF'] = data_df['SBA_SFT'] - data_df['SBA_CALC']

print("Built-up Calculation Error count (where CARPET + BALCONY + WALL != BUILT_UP):")
print((data_df['BUILT_UP_CALC'] != data_df['BUILT_UP_SFT']).sum())

print("\nSBA - (BUILT_UP + COMMON) difference distribution:")
print(data_df['SBA_DIFF'].value_counts())

print("\nRows where SBA - (BUILT_UP + COMMON) is not -1 or 39:")
print(data_df[~data_df['SBA_DIFF'].isin([-1, 39])][['FLOOR', 'TOWER', 'FLAT_NO', 'TYPE', 'SBA_SFT', 'BUILT_UP_SFT', 'COMMON_SFT', 'SBA_DIFF']])

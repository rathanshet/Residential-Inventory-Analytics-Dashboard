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

for col in ['SBA_SFT', 'CARPET_SFT', 'BALCONY_SFT', 'BUILT_UP_SFT', 'WALL_SFT', 'COMMON_SFT', 'PRIVATE_GARDEN_SFT']:
    data_df[col] = pd.to_numeric(data_df[col], errors='coerce')

for f_no in ['A0104', 'A0204', 'B0104', 'B0204', 'F0106', 'F0206']:
    print(f"\n--- {f_no} ---")
    print(data_df[data_df['FLAT_NO'] == f_no].iloc[0].to_dict())

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

# Show floors of all TYPEs ending in '-A'
a_types = data_df[data_df['TYPE'].str.endswith('-A')]
print("Floors of '-A' types:")
print(a_types['FLOOR'].value_counts())

# Show floors of all TYPEs ending in '-B'
b_types = data_df[data_df['TYPE'].str.endswith('-B')]
print("\nFloors of '-B' types:")
print(b_types['FLOOR'].value_counts())

# Let's inspect some records of '-A' vs '-B'
print("\nExample A-type records (first 5):")
print(a_types[['FLOOR', 'TOWER', 'FLAT_NO', 'TYPE', 'SBA_SFT', 'PRIVATE_GARDEN_SFT']].head(5))

print("\nExample B-type records (first 5):")
print(b_types[['FLOOR', 'TOWER', 'FLAT_NO', 'TYPE', 'SBA_SFT', 'PRIVATE_GARDEN_SFT']].head(5))

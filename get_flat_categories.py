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

# Extract simplified category from TYPE (e.g. 2B2T, 3B2T, 3B3T, 4B4T)
def get_category(t):
    t = str(t).upper()
    if '2B2T' in t:
        return '2B2T'
    elif '3B2T' in t:
        return '3B2T'
    elif '3B3T' in t:
        return '3B3T'
    elif '4B4T' in t:
        return '4B4T'
    else:
        return 'OTHER'

data_df['CATEGORY'] = data_df['TYPE'].apply(get_category)

print("Units by Category:")
print(data_df['CATEGORY'].value_counts())

print("\nAverage SBA by Category:")
print(data_df.groupby('CATEGORY')['SBA_SFT'].mean())

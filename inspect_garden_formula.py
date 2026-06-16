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

# Get ground floor units
g_units = data_df[data_df['FLOOR'] == 'G '].copy()

# We want to find their corresponding B-type standard units
# A standard unit will have the same TOWER and the same position (flat number like A0201 corresponds to A0101)
# Let's map each ground floor flat (e.g. A0101) to its floor 1 equivalent (e.g. A0201)
results = []
for idx, g_row in g_units.iterrows():
    flat_no = g_row['FLAT_NO']
    tower = g_row['TOWER']
    # replace '01' with '02' in flat number to get the 1st floor unit
    f1_flat_no = flat_no[0] + '02' + flat_no[3:]
    f1_row = data_df[data_df['FLAT_NO'] == f1_flat_no]
    if not f1_row.empty:
        f1_sba = f1_row.iloc[0]['SBA_SFT']
        f1_bu = f1_row.iloc[0]['BUILT_UP_SFT']
        f1_common = f1_row.iloc[0]['COMMON_SFT']
    else:
        f1_sba, f1_bu, f1_common = None, None, None
    
    results.append({
        'FLAT_NO': flat_no,
        'TYPE': g_row['TYPE'],
        'G_SBA': g_row['SBA_SFT'],
        'G_BU': g_row['BUILT_UP_SFT'],
        'G_COMMON': g_row['COMMON_SFT'],
        'GARDEN': g_row['PRIVATE_GARDEN_SFT'],
        'F1_FLAT': f1_flat_no,
        'F1_SBA': f1_sba,
        'F1_BU': f1_bu,
        'F1_COMMON': f1_common
    })

res_df = pd.DataFrame(results)
res_df['SBA_DIFF'] = res_df['G_SBA'] - res_df['F1_SBA']
res_df['GARDEN_PCT'] = (res_df['SBA_DIFF'] / res_df['GARDEN']) * 100

print(res_df[['FLAT_NO', 'G_SBA', 'F1_SBA', 'SBA_DIFF', 'GARDEN', 'GARDEN_PCT']])

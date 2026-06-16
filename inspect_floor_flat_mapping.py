import pandas as pd
file_path = "/Users/shetu/Downloads/SWW_RERA AREAs Final 28-1-26 Bajaj  (1).xlsx"
df = pd.read_excel(file_path, sheet_name="AREA statement ", header=None)
data_df = df.iloc[2:].copy()
data_df[0] = data_df[0].ffill()
data_df = data_df[data_df[1].notnull()]

# Group by floor and see the flat numbers
for floor, group in data_df.groupby(0):
    flat_prefixes = group[3].apply(lambda x: str(x)[1:3]).unique()
    floor_str = str(floor).strip()
    print(f"Floor raw value: {floor_str:4s} -> Flat No Prefixes: {flat_prefixes} -> Row Count: {len(group)}")

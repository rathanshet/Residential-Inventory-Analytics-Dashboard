import pandas as pd
file_path = "/Users/shetu/Downloads/SWW_RERA AREAs Final 28-1-26 Bajaj  (1).xlsx"
df = pd.read_excel(file_path, sheet_name="AREA statement ", header=None)

# Find all non-null values in the first column (column index 0)
floor_vals = df[df[0].notnull()]
for idx, row in floor_vals.iterrows():
    print(f"Row {idx:3d}: Col 0: {row[0]}, Col 1 (SL): {row[1]}, Col 2 (TOWER): {row[2]}, Col 3 (FLAT): {row[3]}")

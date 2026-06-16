import pandas as pd
file_path = "/Users/shetu/Downloads/SWW_RERA AREAs Final 28-1-26 Bajaj  (1).xlsx"
df = pd.read_excel(file_path, sheet_name="AREA statement ", header=None)
print("Shape:", df.shape)
for i in range(15):
    print(f"Row {i:2d}: {df.iloc[i].tolist()}")

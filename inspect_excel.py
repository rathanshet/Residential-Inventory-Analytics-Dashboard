import pandas as pd
import openpyxl
import os

file_path = "/Users/shetu/Downloads/SWW_RERA AREAs Final 28-1-26 Bajaj  (1).xlsx"

print("Checking file existence:", os.path.exists(file_path))

try:
    xl = pd.ExcelFile(file_path)
    print("Sheet names:", xl.sheet_names)
    for name in xl.sheet_names[:5]:
        df = xl.parse(name)
        print(f"\n--- Sheet: {name} ---")
        print("Columns:", df.columns.tolist()[:15])
        print("Shape:", df.shape)
        print("First 5 rows:")
        print(df.head(5))
except Exception as e:
    print("Error reading Excel:", e)

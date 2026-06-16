import pandas as pd
file_path = "/Users/shetu/Downloads/SWW_RERA AREAs Final 28-1-26 Bajaj  (1).xlsx"
xl = pd.ExcelFile(file_path)
df = xl.parse("AREA statement ", header=None)

print("First 20 rows:")
print(df.iloc[:20, :18])

print("\nLast 10 rows:")
print(df.iloc[-10:, :18])

# Let's count unique values for floor, tower, type
print("\nUnique Floors (raw):", df[0].unique())
print("Unique Towers (raw):", df[2].unique())
print("Unique Types (raw):", df[4].unique())

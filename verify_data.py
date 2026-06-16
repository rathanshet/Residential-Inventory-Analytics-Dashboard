import pandas as pd
import numpy as np

file_path = "/Users/shetu/Downloads/SWW_RERA AREAs Final 28-1-26 Bajaj  (1).xlsx"
df = pd.read_excel(file_path, sheet_name="AREA statement ", header=None)

# The headers are on row 1
headers = df.iloc[1].tolist()
print("Headers length:", len(headers))
print("Original Headers:", headers)

# Row 2 onwards contains data
data_df = df.iloc[2:].copy()

# Forward fill the Floor column (column 0)
data_df[0] = data_df[0].ffill()

# Drop rows where SL no (column 1) is null, because the Excel sheet might have empty trailing rows
data_df = data_df[data_df[1].notnull()]

# Let's assign column names. Some column names are repeated (e.g. CARPET AREA, BALCONY AREA)
# Column 0: FLOOR
# Column 1: SL_NO
# Column 2: TOWER
# Column 3: FLAT_NO
# Column 4: TYPE
# Column 5: SBA_SALABLE_SFT
# Column 6: CARPET_AREA_SFT
# Column 7: BALCONY_AREA_SFT
# Column 8: BUILT_UP_AREA_SFT
# Column 9: WALL_AREA_SFT
# Column 10: COMMON_AREA_SFT
# Column 11: UDS_SFT
# Column 12: PRIVATE_GARDEN_SFT
# Column 13: CARPET_AREA_SQM
# Column 14: BALCONY_AREA_SQM
# Column 15: BUILT_UP_AREA_SQM (let's verify if column 15 is built up area sqm)
# Column 16: WALL_AREA_SQM (let's verify if column 16 is wall area sqm)
# Column 17: COMMON_AREA_SQM (let's verify if column 17 is common area sqm)

columns_mapping = {
    0: 'FLOOR',
    1: 'SL_NO',
    2: 'TOWER',
    3: 'FLAT_NO',
    4: 'TYPE',
    5: 'SBA_SFT',
    6: 'CARPET_SFT',
    7: 'BALCONY_SFT',
    8: 'BUILT_UP_SFT',
    9: 'WALL_SFT',
    10: 'COMMON_SFT',
    11: 'UDS_SFT',
    12: 'PRIVATE_GARDEN_SFT',
    13: 'CARPET_SQM',
    14: 'BALCONY_SQM',
    15: 'BUILT_UP_SQM',
    16: 'WALL_SQM',
    17: 'COMMON_SQM'
}

data_df.rename(columns=columns_mapping, inplace=True)
data_df = data_df[list(columns_mapping.values())]

print("\nData Shape:", data_df.shape)
print("Data columns:", data_df.columns.tolist())
print("\nUnique Floors after ffill:", data_df['FLOOR'].unique())
print("Unique Towers:", data_df['TOWER'].unique())
print("\nFirst 5 rows of cleaned data:")
print(data_df.head(5))

print("\nChecking null values:")
print(data_df.isnull().sum())

# Check data types and print descriptive stats for numeric columns
numeric_cols = ['SBA_SFT', 'CARPET_SFT', 'BALCONY_SFT', 'BUILT_UP_SFT', 'WALL_SFT', 'COMMON_SFT', 'UDS_SFT', 'PRIVATE_GARDEN_SFT']
for col in numeric_cols:
    data_df[col] = pd.to_numeric(data_df[col], errors='coerce')

print("\nSummary statistics of SFT columns:")
print(data_df[numeric_cols].describe())

# Check if there are any non-numeric values that got converted to NaN
print("\nChecking rows where SBA_SFT is null after numeric conversion:")
print(data_df[data_df['SBA_SFT'].isnull()])

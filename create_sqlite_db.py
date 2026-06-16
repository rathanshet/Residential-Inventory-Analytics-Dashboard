import pandas as pd
import sqlite3
import numpy as np

file_path = "/Users/shetu/Downloads/SWW_RERA AREAs Final 28-1-26 Bajaj  (1).xlsx"
df = pd.read_excel(file_path, sheet_name="AREA statement ", header=None)

# Headers and clean data
data_df = df.iloc[2:].copy()
data_df[0] = data_df[0].ffill()
data_df = data_df[data_df[1].notnull()]

# Set column names
columns_mapping = {
    0: 'FLOOR', 1: 'SL_NO', 2: 'TOWER', 3: 'FLAT_NO', 4: 'TYPE',
    5: 'SBA_SFT', 6: 'CARPET_SFT', 7: 'BALCONY_SFT', 8: 'BUILT_UP_SFT',
    9: 'WALL_SFT', 10: 'COMMON_SFT', 11: 'UDS_SFT', 12: 'PRIVATE_GARDEN_SFT',
    13: 'CARPET_SQM', 14: 'BALCONY_SQM', 15: 'BUILT_UP_SQM', 16: 'WALL_SQM', 17: 'COMMON_SQM'
}
data_df.rename(columns=columns_mapping, inplace=True)
data_df = data_df[list(columns_mapping.values())]

# Clean types
for col in ['SBA_SFT', 'CARPET_SFT', 'BALCONY_SFT', 'BUILT_UP_SFT', 'WALL_SFT', 'COMMON_SFT', 'UDS_SFT', 'PRIVATE_GARDEN_SFT',
            'CARPET_SQM', 'BALCONY_SQM', 'BUILT_UP_SQM', 'WALL_SQM', 'COMMON_SQM']:
    data_df[col] = pd.to_numeric(data_df[col], errors='coerce')

# Fill NaN in private garden with 0
data_df['PRIVATE_GARDEN_SFT'] = data_df['PRIVATE_GARDEN_SFT'].fillna(0)

# Connect to sqlite
conn = sqlite3.connect('inventory.db')
data_df.to_sql('inventory', conn, if_exists='replace', index=False)

# Let's run some diagnostic queries
print("--- SQL Diagnostic Queries ---")

# 1. How many units exist in each tower?
q1 = """
SELECT TOWER, COUNT(*) as Unit_Count 
FROM inventory 
GROUP BY TOWER 
ORDER BY TOWER;
"""
print("\nUnits by Tower:")
print(pd.read_sql_query(q1, conn))

# 2. Which apartment type occupies the largest area? (total SBA or average SBA or single largest unit?)
# Let's check both total SBA by flat type and max SBA
q2 = """
SELECT TYPE, COUNT(*) as Unit_Count, SUM(SBA_SFT) as Total_SBA, AVG(SBA_SFT) as Avg_SBA
FROM inventory 
GROUP BY TYPE 
ORDER BY Total_SBA DESC 
LIMIT 5;
"""
print("\nTop 5 Apartment Types by Total SBA:")
print(pd.read_sql_query(q2, conn))

# 3. Average SBA by flat type?
q3 = """
SELECT TYPE, AVG(SBA_SFT) as Avg_SBA
FROM inventory 
GROUP BY TYPE 
ORDER BY Avg_SBA DESC;
"""
print("\nAverage SBA by Flat Type:")
print(pd.read_sql_query(q3, conn))

# 4. Floor-wise inventory distribution?
q4 = """
SELECT FLOOR, COUNT(*) as Unit_Count, SUM(SBA_SFT) as Total_SBA
FROM inventory 
GROUP BY FLOOR 
ORDER BY CAST(FLOOR as INTEGER) ASC, FLOOR;
"""
print("\nFloor-wise Inventory Distribution:")
print(pd.read_sql_query(q4, conn))

# 5. Private garden allocation analysis?
q5 = """
SELECT TOWER, COUNT(*) as Units_With_Garden, SUM(PRIVATE_GARDEN_SFT) as Total_Garden_Area, AVG(PRIVATE_GARDEN_SFT) as Avg_Garden_Area
FROM inventory 
WHERE PRIVATE_GARDEN_SFT > 0
GROUP BY TOWER
ORDER BY TOWER;
"""
print("\nPrivate Garden Allocation by Tower:")
print(pd.read_sql_query(q5, conn))

conn.close()

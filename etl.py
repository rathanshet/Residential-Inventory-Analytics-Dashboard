import pandas as pd
import sqlite3
import numpy as np
import os

file_path = "/Users/shetu/Downloads/SWW_RERA AREAs Final 28-1-26 Bajaj  (1).xlsx"
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "inventory.db")

print("📂 Reading Excel file...")
df = pd.read_excel(file_path, sheet_name="AREA statement ", header=None)

# ── Step 1: Extract data rows (row 2 = index 1 is header, row 3+ is data) ──
data_df = df.iloc[2:].copy()

# ── Step 2: Forward-fill FLOOR column ──
data_df[0] = data_df[0].ffill()

# ── Step 3: Drop empty rows (where SL_NO is null) ──
data_df = data_df[data_df[1].notnull() & data_df[1].apply(lambda x: str(x).strip().isdigit() or isinstance(x, (int, float)))]

# ── Step 4: Rename columns ──
columns_mapping = {
    0: 'FLOOR', 1: 'SL_NO', 2: 'TOWER', 3: 'FLAT_NO', 4: 'TYPE',
    5: 'SBA_SFT', 6: 'CARPET_SFT', 7: 'BALCONY_SFT', 8: 'BUILT_UP_SFT',
    9: 'WALL_SFT', 10: 'COMMON_SFT', 11: 'UDS_SFT', 12: 'PRIVATE_GARDEN_SFT',
    13: 'CARPET_SQM', 14: 'BALCONY_SQM', 15: 'BUILT_UP_SQM', 16: 'UDS_SQM', 17: 'COMMON_SQM'
}
data_df.rename(columns=columns_mapping, inplace=True)
data_df = data_df[list(columns_mapping.values())]
data_df = data_df.reset_index(drop=True)

# ── Step 5: Normalize FLOOR column ──
def normalize_floor(f):
    f_str = str(f).strip()
    if f_str.upper().startswith('G'):
        return 'G'
    try:
        return str(int(float(f_str)))
    except:
        return f_str

data_df['FLOOR'] = data_df['FLOOR'].apply(normalize_floor)

# ── Step 6: Convert numeric columns ──
num_cols = ['SBA_SFT','CARPET_SFT','BALCONY_SFT','BUILT_UP_SFT','WALL_SFT',
            'COMMON_SFT','UDS_SFT','PRIVATE_GARDEN_SFT','CARPET_SQM',
            'BALCONY_SQM','BUILT_UP_SQM','UDS_SQM','COMMON_SQM']
for col in num_cols:
    data_df[col] = pd.to_numeric(data_df[col], errors='coerce')

# ── Step 7: Fill NaN garden with 0 ──
data_df['PRIVATE_GARDEN_SFT'] = data_df['PRIVATE_GARDEN_SFT'].fillna(0)

# ── Step 8: Extract apartment category (2B2T, 3B2T, 3B3T, 4B4T) ──
def get_category(t):
    t = str(t).upper()
    if '4B4T' in t:
        return '4B4T'
    elif '3B3T' in t:
        return '3B3T'
    elif '3B2T' in t:
        return '3B2T'
    elif '2B2T' in t:
        return '2B2T'
    else:
        return 'OTHER'

data_df['CATEGORY'] = data_df['TYPE'].apply(get_category)

# ── Step 9: Extract base type without floor suffix (-A or -B) ──
def get_base_type(t):
    t = str(t)
    if t.endswith('-A') or t.endswith('-B'):
        return t[:-2]
    return t

data_df['BASE_TYPE'] = data_df['TYPE'].apply(get_base_type)

# ── Step 10: Add floor order for sorting ──
def floor_order(f):
    if f == 'G':
        return 0
    try:
        return int(f)
    except:
        return 99

data_df['FLOOR_ORDER'] = data_df['FLOOR'].apply(floor_order)

# ── Step 11: Flag ground floor units ──
data_df['IS_GROUND'] = data_df['FLOOR'] == 'G'
data_df['HAS_GARDEN'] = data_df['PRIVATE_GARDEN_SFT'] > 0

# ── Step 12: Calculate contribution ratios ──
data_df['CARPET_RATIO'] = (data_df['CARPET_SFT'] / data_df['SBA_SFT'] * 100).round(2)
data_df['BALCONY_RATIO'] = (data_df['BALCONY_SFT'] / data_df['SBA_SFT'] * 100).round(2)
data_df['COMMON_RATIO'] = (data_df['COMMON_SFT'] / data_df['SBA_SFT'] * 100).round(2)
data_df['WALL_RATIO'] = (data_df['WALL_SFT'] / data_df['SBA_SFT'] * 100).round(2)

# ── Step 13: Write to SQLite ──
print(f"💾 Writing {len(data_df)} rows to SQLite database...")
conn = sqlite3.connect(db_path)
data_df.to_sql('inventory', conn, if_exists='replace', index=False)

# ── Step 14: Create helpful views ──
conn.execute("""
CREATE VIEW IF NOT EXISTS v_tower_summary AS
SELECT 
    TOWER,
    COUNT(*) AS unit_count,
    SUM(SBA_SFT) AS total_sba,
    AVG(SBA_SFT) AS avg_sba,
    AVG(CARPET_SFT) AS avg_carpet,
    SUM(PRIVATE_GARDEN_SFT) AS total_garden
FROM inventory
GROUP BY TOWER
ORDER BY TOWER;
""")

conn.execute("""
CREATE VIEW IF NOT EXISTS v_floor_summary AS
SELECT 
    FLOOR,
    FLOOR_ORDER,
    COUNT(*) AS unit_count,
    SUM(SBA_SFT) AS total_sba,
    AVG(SBA_SFT) AS avg_sba
FROM inventory
GROUP BY FLOOR, FLOOR_ORDER
ORDER BY FLOOR_ORDER;
""")

conn.execute("""
CREATE VIEW IF NOT EXISTS v_category_summary AS
SELECT 
    CATEGORY,
    COUNT(*) AS unit_count,
    SUM(SBA_SFT) AS total_sba,
    AVG(SBA_SFT) AS avg_sba,
    AVG(CARPET_SFT) AS avg_carpet,
    AVG(BALCONY_SFT) AS avg_balcony,
    AVG(COMMON_SFT) AS avg_common
FROM inventory
GROUP BY CATEGORY
ORDER BY avg_sba DESC;
""")

conn.execute("""
CREATE VIEW IF NOT EXISTS v_garden_analysis AS
SELECT
    TOWER,
    COUNT(CASE WHEN HAS_GARDEN = 1 THEN 1 END) AS units_with_garden,
    SUM(PRIVATE_GARDEN_SFT) AS total_garden_area,
    AVG(CASE WHEN HAS_GARDEN = 1 THEN PRIVATE_GARDEN_SFT END) AS avg_garden_area,
    MIN(CASE WHEN HAS_GARDEN = 1 THEN PRIVATE_GARDEN_SFT END) AS min_garden,
    MAX(PRIVATE_GARDEN_SFT) AS max_garden
FROM inventory
WHERE IS_GROUND = 1
GROUP BY TOWER
ORDER BY TOWER;
""")

conn.commit()

# ── Final summary ──
print("\n✅ ETL Complete!")
print(f"   Database: {db_path}")
print(f"   Total records: {len(data_df)}")
print(f"   Towers: {sorted(data_df['TOWER'].unique())}")
print(f"   Floors: {sorted(data_df['FLOOR'].unique(), key=floor_order)}")
print(f"   Categories: {data_df['CATEGORY'].value_counts().to_dict()}")
print(f"   Total SBA: {data_df['SBA_SFT'].sum():,.0f} SFT")
print(f"   Avg Carpet: {data_df['CARPET_SFT'].mean():,.0f} SFT")
print(f"   Total Garden: {data_df['PRIVATE_GARDEN_SFT'].sum():,.0f} SFT")
print(f"   Units with Garden: {data_df['HAS_GARDEN'].sum()}")

conn.close()
print("\n🎉 Database ready!")

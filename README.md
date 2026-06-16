# 🏢 Residential Inventory Analytics Dashboard

🚀 **[Live Demo on Render](https://residential-inventory-analytics-dashboard.onrender.com)**

A premium, glassmorphic dark-themed real estate analytics dashboard designed for developers to analyze residential inventory distribution across towers, floors, and flat categories. Powered by a Python ETL pipeline, a SQLite database, a Node.js/Express backend, and a modern vanilla HTML/CSS/JS frontend.

---

## 🌟 Key Features

- **📊 Executive Summary**: High-level KPIs (Total Units, Saleable Area, Avg Carpet Area, Private Gardens) with animated counters and visual charts mapping tower and floor distribution.
- **🏗️ Inventory Analysis**: Advanced breakdowns including Tower × Flat Type distribution matrices, average area per flat category, and detailed inventory metrics tables.
- **📐 Area Ratio Analysis**: Detailed comparison of Saleable Area (SBA) vs. Carpet Area, with composition splits for Carpet, Balcony, Walls, and Common areas.
- **🌿 Private Garden Allocation**: Dedicated analytics for ground-floor private garden layouts, detailing units with gardens and min/max/average garden size.
- **💾 Interactive SQL Console**: A built-in terminal interface allowing users to execute custom `SELECT` queries directly against the SQLite database in real-time.
- **📐 DAX & measures**: Clear cross-references detailing Power BI DAX formulas equivalent to the SQL calculations used.
- **⚙️ Self-Documenting ETL**: Step-by-step documentation detailing how raw area statement spreadsheets are sanitized, forward-filled, and mapped to the database.

---

## 🛠️ Technology Stack

- **Data Processing**: Python 3, Pandas, SQLite3
- **Backend**: Node.js, Express, `sqlite3` driver, CORS
- **Frontend**: Vanilla HTML5 (Semantic elements), CSS3 (Custom HSL tokens, Glassmorphism backdrop-filters, custom scrollbars), ES6 JavaScript
- **Visualizations**: Chart.js (v4), Chart.js Datalabels plugin
- **Typography**: Outfit, JetBrains Mono (Google Fonts)

---

## 📊 Database Schema (`inventory.db`)

The SQLite database contains the central `inventory` table with 272 cleaned unit records:

| Column | Type | Description |
| :--- | :--- | :--- |
| `SL_NO` | INTEGER | Serial number of the unit |
| `TOWER` | TEXT | Tower identifier (`A`, `B`, `C`, `D`, `E`, `F`) |
| `FLOOR` | TEXT | Floor designation (`G`, `1`–`10`) |
| `FLAT_NO` | TEXT | Distinct unit/flat number |
| `TYPE` | TEXT | Full type code (e.g., `C 3B2T_TYPE 1-A`) |
| `CATEGORY` | TEXT | Simplified category (`2B2T`, `3B2T`, `3B3T`, `4B4T`) |
| `BASE_TYPE` | TEXT | Flat type base designation (stripped floor suffix) |
| `SBA_SFT` | REAL | Saleable Area in Sq. Ft. |
| `CARPET_SFT` | REAL | Carpet Area in Sq. Ft. |
| `BALCONY_SFT` | REAL | Balcony Area in Sq. Ft. |
| `COMMON_SFT` | REAL | Common Area contribution in Sq. Ft. |
| `WALL_SFT` | REAL | Wall Area contribution in Sq. Ft. |
| `PRIVATE_GARDEN_SFT` | REAL | Private Garden Area (Ground Floor units) |
| `HAS_GARDEN` | INTEGER | Boolean flag (1 = Has garden, 0 = No garden) |
| `IS_GROUND` | INTEGER | Boolean flag (1 = Ground floor unit, 0 = Upper floor) |

---

## 🚀 Getting Started

### Prerequisites
Make sure you have **Python 3** and **Node.js** installed on your system.

### 1. Run the ETL Pipeline
Extracts, cleans, and loads raw Excel spreadsheet data into the SQLite database:
```bash
# Navigate to project root
cd /Users/shetu/.gemini/antigravity-ide/scratch/residential_inventory

# Execute pipeline
python3 etl.py
```

### 2. Install Dependencies & Start Server
Installs Express dependencies and launches the local web server:
```bash
# Install Node modules
npm install

# Start local server
npm start
```
The server will boot on port **`3737`**:
- **App URL**: [http://localhost:3737](http://localhost:3737)
- **KPI Summary API**: `http://localhost:3737/api/summary`
- **SQL Console API**: `http://localhost:3737/api/query`

---

## 📈 Sample SQL Queries (Run in Console)

### Tower-wise Units & Total Area
```sql
SELECT TOWER, COUNT(*) as Units, SUM(SBA_SFT) as Total_SBA 
FROM inventory 
GROUP BY TOWER 
ORDER BY TOWER;
```

### Private Garden Allocations by Tower
```sql
SELECT TOWER, FLAT_NO, TYPE, PRIVATE_GARDEN_SFT 
FROM inventory 
WHERE HAS_GARDEN = 1 
ORDER BY PRIVATE_GARDEN_SFT DESC;
```

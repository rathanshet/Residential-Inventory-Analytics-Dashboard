const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const cors = require('cors');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3737;
const DB_PATH = path.join(__dirname, 'inventory.db');

app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

// ── Database helper ──
function getDb() {
  return new sqlite3.Database(DB_PATH, sqlite3.OPEN_READONLY);
}

function query(sql, params = []) {
  return new Promise((resolve, reject) => {
    const db = getDb();
    db.all(sql, params, (err, rows) => {
      db.close();
      if (err) reject(err);
      else resolve(rows);
    });
  });
}

// ═══════════════════════════════════════════════════
// API: Executive Summary KPIs
// ═══════════════════════════════════════════════════
app.get('/api/summary', async (req, res) => {
  try {
    const [kpi] = await query(`
      SELECT
        COUNT(*) AS total_units,
        SUM(SBA_SFT) AS total_sba,
        ROUND(AVG(SBA_SFT), 0) AS avg_sba,
        ROUND(AVG(CARPET_SFT), 0) AS avg_carpet,
        SUM(PRIVATE_GARDEN_SFT) AS total_garden,
        COUNT(DISTINCT TOWER) AS total_towers,
        COUNT(DISTINCT FLOOR) AS total_floors,
        COUNT(DISTINCT CATEGORY) AS total_categories
      FROM inventory
    `);

    const categoryBreakdown = await query(`
      SELECT CATEGORY, COUNT(*) AS count, SUM(SBA_SFT) AS total_sba
      FROM inventory GROUP BY CATEGORY ORDER BY avg(SBA_SFT) DESC
    `);

    const towerBreakdown = await query(`SELECT * FROM v_tower_summary`);
    const floorBreakdown = await query(`SELECT * FROM v_floor_summary`);

    res.json({ kpi, categoryBreakdown, towerBreakdown, floorBreakdown });
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// ═══════════════════════════════════════════════════
// API: Inventory Analysis
// ═══════════════════════════════════════════════════
app.get('/api/inventory', async (req, res) => {
  try {
    const unitsByTower = await query(`SELECT * FROM v_tower_summary`);

    const unitsByFlat = await query(`
      SELECT CATEGORY, COUNT(*) AS unit_count,
        ROUND(AVG(SBA_SFT),0) AS avg_sba,
        ROUND(AVG(CARPET_SFT),0) AS avg_carpet,
        SUM(SBA_SFT) AS total_sba
      FROM inventory GROUP BY CATEGORY ORDER BY avg_sba DESC
    `);

    const floorDist = await query(`SELECT * FROM v_floor_summary`);

    const towerTypeMatrix = await query(`
      SELECT TOWER, CATEGORY, COUNT(*) AS count
      FROM inventory GROUP BY TOWER, CATEGORY ORDER BY TOWER, CATEGORY
    `);

    const topTypes = await query(`
      SELECT BASE_TYPE, CATEGORY, COUNT(*) AS unit_count,
        ROUND(AVG(SBA_SFT),0) AS avg_sba
      FROM inventory GROUP BY BASE_TYPE, CATEGORY ORDER BY unit_count DESC LIMIT 20
    `);

    res.json({ unitsByTower, unitsByFlat, floorDist, towerTypeMatrix, topTypes });
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// ═══════════════════════════════════════════════════
// API: Area Analysis
// ═══════════════════════════════════════════════════
app.get('/api/area', async (req, res) => {
  try {
    const overallContrib = await query(`
      SELECT
        ROUND(AVG(CARPET_SFT),0) AS avg_carpet,
        ROUND(AVG(BALCONY_SFT),0) AS avg_balcony,
        ROUND(AVG(WALL_SFT),0) AS avg_wall,
        ROUND(AVG(COMMON_SFT),0) AS avg_common,
        ROUND(AVG(CARPET_RATIO),2) AS carpet_pct,
        ROUND(AVG(BALCONY_RATIO),2) AS balcony_pct,
        ROUND(AVG(WALL_RATIO),2) AS wall_pct,
        ROUND(AVG(COMMON_RATIO),2) AS common_pct
      FROM inventory
    `);

    const byCategory = await query(`
      SELECT CATEGORY,
        ROUND(AVG(SBA_SFT),0) AS avg_sba,
        ROUND(AVG(CARPET_SFT),0) AS avg_carpet,
        ROUND(AVG(BALCONY_SFT),0) AS avg_balcony,
        ROUND(AVG(WALL_SFT),0) AS avg_wall,
        ROUND(AVG(COMMON_SFT),0) AS avg_common,
        ROUND(AVG(CARPET_RATIO),2) AS carpet_pct,
        ROUND(AVG(BALCONY_RATIO),2) AS balcony_pct,
        ROUND(AVG(COMMON_RATIO),2) AS common_pct
      FROM inventory GROUP BY CATEGORY ORDER BY avg_sba DESC
    `);

    const sbavsCarpet = await query(`
      SELECT TOWER, ROUND(AVG(SBA_SFT),0) AS avg_sba, ROUND(AVG(CARPET_SFT),0) AS avg_carpet
      FROM inventory GROUP BY TOWER ORDER BY TOWER
    `);

    const gardenAnalysis = await query(`SELECT * FROM v_garden_analysis`);

    const gardenByType = await query(`
      SELECT CATEGORY,
        COUNT(CASE WHEN HAS_GARDEN = 1 THEN 1 END) AS units_with_garden,
        SUM(PRIVATE_GARDEN_SFT) AS total_garden_area,
        ROUND(AVG(CASE WHEN HAS_GARDEN = 1 THEN PRIVATE_GARDEN_SFT END),0) AS avg_garden
      FROM inventory WHERE IS_GROUND = 1
      GROUP BY CATEGORY ORDER BY total_garden_area DESC
    `);

    res.json({ overallContrib: overallContrib[0], byCategory, sbavsCarpet, gardenAnalysis, gardenByType });
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// ═══════════════════════════════════════════════════
// API: Interactive SQL Console
// ═══════════════════════════════════════════════════
app.post('/api/query', async (req, res) => {
  const { sql: rawSql } = req.body;
  if (!rawSql) return res.status(400).json({ error: 'No SQL provided' });

  // Block destructive operations
  const forbidden = /^\s*(DROP|DELETE|UPDATE|INSERT|ALTER|CREATE|REPLACE)\b/i;
  if (forbidden.test(rawSql)) {
    return res.status(403).json({ error: 'Only SELECT queries are allowed in the console.' });
  }

  try {
    const db = new sqlite3.Database(DB_PATH, sqlite3.OPEN_READONLY);
    db.all(rawSql, [], (err, rows) => {
      db.close();
      if (err) {
        res.status(400).json({ error: err.message });
      } else {
        res.json({ rows, count: rows.length });
      }
    });
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// ═══════════════════════════════════════════════════
// API: Schema (for SQL Console helper)
// ═══════════════════════════════════════════════════
app.get('/api/schema', async (req, res) => {
  try {
    const tables = await query(`SELECT name FROM sqlite_master WHERE type='table' OR type='view' ORDER BY name`);
    const columns = await query(`PRAGMA table_info(inventory)`);
    res.json({ tables, columns });
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// ── Serve index.html for all other routes ──
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

app.listen(PORT, () => {
  console.log(`\n🏗️  Residential Inventory Dashboard`);
  console.log(`🚀 Server running at: http://localhost:${PORT}`);
  console.log(`📊 API Endpoints:`);
  console.log(`   GET  /api/summary   - Executive KPIs`);
  console.log(`   GET  /api/inventory - Inventory analysis`);
  console.log(`   GET  /api/area      - Area analysis`);
  console.log(`   POST /api/query     - SQL console`);
  console.log(`   GET  /api/schema    - DB schema info\n`);
});

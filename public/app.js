/* ═══════════════════════════════════════════════════════════
   RESIDENTIAL INVENTORY ANALYTICS – app.js
   Chart.js v4 · Fetch API · SQL Console
═══════════════════════════════════════════════════════════ */

'use strict';

// ── Register datalabels plugin globally ──
Chart.register(ChartDataLabels);

// ── Chart.js global defaults ──
Chart.defaults.font.family = "'Outfit', sans-serif";
Chart.defaults.color       = 'hsl(215, 15%, 60%)';
Chart.defaults.plugins.legend.labels.usePointStyle = true;
Chart.defaults.plugins.legend.labels.padding       = 16;
Chart.defaults.plugins.datalabels.display          = false; // off by default

// ── Palette ──
const PALETTE = {
  blue:   'hsl(210, 100%, 60%)',
  green:  'hsl(152, 80%, 45%)',
  amber:  'hsl(38, 95%, 55%)',
  purple: 'hsl(270, 85%, 65%)',
  cyan:   'hsl(185, 90%, 55%)',
  rose:   'hsl(350, 85%, 60%)',
};

const TOWER_COLORS = ['#3b9eff','#22c55e','#a78bfa','#fbbf24','#34d399','#f87171'];
const CAT_COLORS   = {
  '4B4T': PALETTE.amber,
  '3B3T': PALETTE.purple,
  '3B2T': PALETTE.blue,
  '2B2T': PALETTE.cyan,
};

function alpha(hex, a) {
  // accepts hsl string or hex
  if (hex.startsWith('hsl')) return hex.replace(')', `, ${a})`).replace('hsl(', 'hsla(');
  return hex + Math.round(a * 255).toString(16).padStart(2, '0');
}

const charts = {};

// ═══════════════════════════════════════════════════
// NAVIGATION
// ═══════════════════════════════════════════════════
const PAGE_TITLES = {
  summary:   'Executive Summary',
  inventory: 'Inventory Analysis',
  area:      'Area Analysis',
  sql:       'SQL Console',
  dax:       'DAX Measures',
  etl:       'Data Cleaning',
};

function showPage(name) {
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
  document.getElementById('page-' + name).classList.add('active');
  document.getElementById('nav-' + name).classList.add('active');
  document.getElementById('topbar-breadcrumb').textContent = PAGE_TITLES[name];

  // close sidebar on mobile after nav
  if (window.innerWidth <= 900) {
    document.getElementById('sidebar').classList.remove('open');
  }
}

function toggleSidebar() {
  document.getElementById('sidebar').classList.toggle('open');
}

// ═══════════════════════════════════════════════════
// TOPBAR DATE
// ═══════════════════════════════════════════════════
function updateDate() {
  const now = new Date();
  document.getElementById('topbar-date').textContent =
    now.toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' });
}
updateDate();

// ═══════════════════════════════════════════════════
// COUNTER ANIMATION
// ═══════════════════════════════════════════════════
function animateCounter(el, target, format = v => v.toLocaleString('en-IN')) {
  const duration = 1200;
  const start = performance.now();
  function step(now) {
    const t  = Math.min((now - start) / duration, 1);
    const ease = 1 - Math.pow(1 - t, 3);
    el.textContent = format(Math.round(ease * target));
    if (t < 1) requestAnimationFrame(step);
  }
  requestAnimationFrame(step);
}

// ═══════════════════════════════════════════════════
// CHART HELPERS
// ═══════════════════════════════════════════════════
function gridLines() {
  return { color: 'hsl(222, 20%, 17%)', drawBorder: false };
}

function tickStyle() {
  return { color: 'hsl(215, 15%, 50%)', font: { size: 11 } };
}

function baseBarOptions(horizontal = false) {
  return {
    indexAxis: horizontal ? 'y' : 'x',
    responsive: true,
    maintainAspectRatio: false,
    plugins: { legend: { display: false }, datalabels: { display: false }, tooltip: { mode: 'index', intersect: false } },
    scales: {
      x: { grid: gridLines(), ticks: tickStyle(), border: { display: false } },
      y: { grid: horizontal ? gridLines() : { color: 'transparent' }, ticks: tickStyle(), border: { display: false } },
    },
  };
}

// ═══════════════════════════════════════════════════
// PAGE 1 – EXECUTIVE SUMMARY
// ═══════════════════════════════════════════════════
async function loadSummary() {
  const data = await fetch('/api/summary').then(r => r.json());
  const { kpi, categoryBreakdown, towerBreakdown, floorBreakdown } = data;

  // KPI counters
  animateCounter(document.getElementById('kpi-total-units'),  kpi.total_units);
  animateCounter(document.getElementById('kpi-total-sba'),    kpi.total_sba,    v => (v/1000).toFixed(0)+'K SFT');
  animateCounter(document.getElementById('kpi-avg-carpet'),   kpi.avg_carpet,   v => v.toLocaleString('en-IN') + ' SFT');
  animateCounter(document.getElementById('kpi-total-garden'), kpi.total_garden, v => v.toLocaleString('en-IN') + ' SFT');

  document.getElementById('kpi-units-sub').textContent = `${kpi.total_towers} towers · ${kpi.total_floors} floors`;
  document.getElementById('db-status').querySelector('.status-text').textContent = 'Connected';
  document.getElementById('data-info').textContent = `${kpi.total_units} Units · ${kpi.total_towers} Towers`;

  // Chart: Units by Tower
  destroyChart('chart-units-tower');
  charts['chart-units-tower'] = new Chart(document.getElementById('chart-units-tower'), {
    type: 'bar',
    data: {
      labels: towerBreakdown.map(r => 'Tower ' + r.TOWER),
      datasets: [{
        label: 'Units',
        data:  towerBreakdown.map(r => r.unit_count),
        backgroundColor: TOWER_COLORS.map(c => alpha(c, 0.75)),
        borderColor: TOWER_COLORS,
        borderWidth: 2,
        borderRadius: 8,
        borderSkipped: false,
      }]
    },
    options: {
      ...baseBarOptions(),
      plugins: {
        ...baseBarOptions().plugins,
        datalabels: {
          display: true,
          anchor: 'end', align: 'end',
          color: 'hsl(215, 15%, 65%)',
          font: { size: 11, weight: 600 },
        },
      },
      scales: {
        x: { grid: { color: 'transparent' }, ticks: tickStyle(), border: { display: false } },
        y: { grid: gridLines(), ticks: tickStyle(), border: { display: false } },
      }
    }
  });

  // Chart: Category donut
  destroyChart('chart-type-donut');
  charts['chart-type-donut'] = new Chart(document.getElementById('chart-type-donut'), {
    type: 'doughnut',
    data: {
      labels: categoryBreakdown.map(r => r.CATEGORY),
      datasets: [{
        data:            categoryBreakdown.map(r => r.count),
        backgroundColor: categoryBreakdown.map(r => alpha(CAT_COLORS[r.CATEGORY] || PALETTE.blue, 0.8)),
        borderColor:     categoryBreakdown.map(r => CAT_COLORS[r.CATEGORY] || PALETTE.blue),
        borderWidth: 2,
        hoverOffset: 8,
      }]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      cutout: '65%',
      plugins: {
        legend: { position: 'bottom', labels: { padding: 14, font: { size: 11 } } },
        datalabels: {
          display: true,
          color: '#fff',
          font: { size: 11, weight: 700 },
          formatter: (v, ctx) => {
            const total = ctx.dataset.data.reduce((a, b) => a + b, 0);
            return Math.round(v / total * 100) + '%';
          }
        },
        tooltip: {
          callbacks: {
            label: ctx => ` ${ctx.label}: ${ctx.parsed} units`
          }
        }
      }
    }
  });

  // Chart: Floor distribution (line)
  destroyChart('chart-floor-dist');
  const floorLabels = floorBreakdown.map(r => r.FLOOR === 'G' ? 'Ground' : 'Floor ' + r.FLOOR);
  charts['chart-floor-dist'] = new Chart(document.getElementById('chart-floor-dist'), {
    type: 'line',
    data: {
      labels: floorLabels,
      datasets: [{
        label: 'Units',
        data: floorBreakdown.map(r => r.unit_count),
        borderColor: PALETTE.purple,
        backgroundColor: alpha(PALETTE.purple, 0.12),
        fill: true,
        tension: 0.35,
        pointBackgroundColor: PALETTE.purple,
        pointRadius: 5,
        pointHoverRadius: 7,
      }]
    },
    options: {
      ...baseBarOptions(),
      plugins: { ...baseBarOptions().plugins, legend: { display: false } },
      scales: {
        x: { grid: { color: 'transparent' }, ticks: tickStyle(), border: { display: false } },
        y: { grid: gridLines(), ticks: tickStyle(), border: { display: false } },
      }
    }
  });

  // Chart: SBA by Tower
  destroyChart('chart-sba-tower');
  charts['chart-sba-tower'] = new Chart(document.getElementById('chart-sba-tower'), {
    type: 'bar',
    data: {
      labels: towerBreakdown.map(r => 'Tower ' + r.TOWER),
      datasets: [{
        label: 'Total SBA (SFT)',
        data: towerBreakdown.map(r => r.total_sba),
        backgroundColor: TOWER_COLORS.map(c => alpha(c, 0.6)),
        borderColor: TOWER_COLORS,
        borderWidth: 2,
        borderRadius: 8,
        borderSkipped: false,
      }]
    },
    options: {
      ...baseBarOptions(),
      scales: {
        x: { grid: { color: 'transparent' }, ticks: tickStyle(), border: { display: false } },
        y: {
          grid: gridLines(), border: { display: false },
          ticks: { ...tickStyle(), callback: v => (v / 1000).toFixed(0) + 'K' }
        },
      }
    }
  });
}

// ═══════════════════════════════════════════════════
// PAGE 2 – INVENTORY ANALYSIS
// ═══════════════════════════════════════════════════
async function loadInventory() {
  const data = await fetch('/api/inventory').then(r => r.json());
  const { unitsByFlat, towerTypeMatrix, floorDist, topTypes } = data;

  const categories = ['2B2T','3B2T','3B3T','4B4T'];
  const towers = [...new Set(towerTypeMatrix.map(r => r.TOWER))].sort();

  // Stacked bar: Tower × Category matrix
  destroyChart('chart-tower-type-matrix');
  charts['chart-tower-type-matrix'] = new Chart(document.getElementById('chart-tower-type-matrix'), {
    type: 'bar',
    data: {
      labels: towers.map(t => 'Tower ' + t),
      datasets: categories.map(cat => ({
        label: cat,
        data: towers.map(tower => {
          const found = towerTypeMatrix.find(r => r.TOWER === tower && r.CATEGORY === cat);
          return found ? found.count : 0;
        }),
        backgroundColor: alpha(CAT_COLORS[cat] || PALETTE.blue, 0.75),
        borderColor:     CAT_COLORS[cat] || PALETTE.blue,
        borderWidth: 1.5,
        borderRadius: 4,
        borderSkipped: false,
      }))
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: {
        datalabels: { display: true, color: '#fff', font: { size: 10, weight: 600 }, formatter: v => v > 0 ? v : '' },
        legend: { position: 'top', labels: { padding: 16, font: { size: 11 } } },
        tooltip: { mode: 'index', intersect: false },
      },
      scales: {
        x: { stacked: true, grid: { color: 'transparent' }, ticks: tickStyle(), border: { display: false } },
        y: { stacked: true, grid: gridLines(), ticks: tickStyle(), border: { display: false } },
      }
    }
  });

  // Chart: Avg SBA by category
  destroyChart('chart-avg-sba-cat');
  charts['chart-avg-sba-cat'] = new Chart(document.getElementById('chart-avg-sba-cat'), {
    type: 'bar',
    data: {
      labels: unitsByFlat.map(r => r.CATEGORY),
      datasets: [{
        label: 'Avg SBA (SFT)',
        data: unitsByFlat.map(r => r.avg_sba),
        backgroundColor: unitsByFlat.map(r => alpha(CAT_COLORS[r.CATEGORY] || PALETTE.blue, 0.75)),
        borderColor:     unitsByFlat.map(r => CAT_COLORS[r.CATEGORY] || PALETTE.blue),
        borderWidth: 2, borderRadius: 8, borderSkipped: false,
      }]
    },
    options: {
      ...baseBarOptions(),
      plugins: {
        ...baseBarOptions().plugins,
        datalabels: {
          display: true, anchor: 'end', align: 'end',
          color: 'hsl(215,15%,65%)', font: { size: 10, weight: 600 },
          formatter: v => v.toLocaleString('en-IN'),
        },
      },
      scales: {
        x: { grid: { color: 'transparent' }, ticks: tickStyle(), border: { display: false } },
        y: { grid: gridLines(), ticks: tickStyle(), border: { display: false }, min: 1000 },
      }
    }
  });

  // Chart: Floor horizontal bar
  destroyChart('chart-floor-horiz');
  const sortedFloors = [...floorDist].sort((a, b) => a.FLOOR_ORDER - b.FLOOR_ORDER);
  charts['chart-floor-horiz'] = new Chart(document.getElementById('chart-floor-horiz'), {
    type: 'bar',
    data: {
      labels: sortedFloors.map(r => r.FLOOR === 'G' ? 'Ground' : 'Floor ' + r.FLOOR),
      datasets: [{
        label: 'Units',
        data: sortedFloors.map(r => r.unit_count),
        backgroundColor: sortedFloors.map((_, i) => {
          const hue = 200 + i * 12;
          return `hsla(${hue}, 80%, 55%, 0.75)`;
        }),
        borderWidth: 0, borderRadius: 5,
      }]
    },
    options: {
      ...baseBarOptions(true),
      plugins: {
        ...baseBarOptions(true).plugins,
        datalabels: {
          display: true, anchor: 'end', align: 'end',
          color: 'hsl(215,15%,65%)', font: { size: 10, weight: 600 },
        },
      },
    }
  });

  // Stats table
  const tbody = document.getElementById('inv-table-body');
  const totalSba = unitsByFlat.reduce((a, r) => a + r.total_sba, 0);
  tbody.innerHTML = unitsByFlat.map(r => `
    <tr>
      <td><span class="badge-cat cat-${r.CATEGORY.toLowerCase()}">${r.CATEGORY}</span></td>
      <td>${r.unit_count}</td>
      <td>${Number(r.avg_sba).toLocaleString('en-IN')}</td>
      <td>${Number(r.avg_carpet).toLocaleString('en-IN')}</td>
      <td>${Number(r.total_sba).toLocaleString('en-IN')}</td>
      <td>${(r.total_sba / totalSba * 100).toFixed(1)}%</td>
    </tr>
  `).join('');
}

// ═══════════════════════════════════════════════════
// PAGE 3 – AREA ANALYSIS
// ═══════════════════════════════════════════════════
async function loadArea() {
  const data = await fetch('/api/area').then(r => r.json());
  const { overallContrib, byCategory, sbavsCarpet, gardenAnalysis, gardenByType } = data;

  // Contribution KPI cards
  const setContrib = (id, pct, avg) => {
    document.getElementById(`c-${id}-pct`).textContent  = pct + '%';
    document.getElementById(`c-${id}-avg`).textContent  = `Avg: ${Number(avg).toLocaleString('en-IN')} SFT`;
    document.getElementById(`c-${id}-bar`).style.width  = pct + '%';
  };
  setContrib('carpet',  overallContrib.carpet_pct,  overallContrib.avg_carpet);
  setContrib('balcony', overallContrib.balcony_pct, overallContrib.avg_balcony);
  setContrib('common',  overallContrib.common_pct,  overallContrib.avg_common);
  setContrib('wall',    overallContrib.wall_pct,    overallContrib.avg_wall);

  // Chart: SBA vs Carpet by Tower
  destroyChart('chart-sba-carpet');
  charts['chart-sba-carpet'] = new Chart(document.getElementById('chart-sba-carpet'), {
    type: 'bar',
    data: {
      labels: sbavsCarpet.map(r => 'Tower ' + r.TOWER),
      datasets: [
        {
          label: 'Avg SBA',
          data: sbavsCarpet.map(r => r.avg_sba),
          backgroundColor: alpha(PALETTE.blue, 0.7),
          borderColor: PALETTE.blue,
          borderWidth: 2, borderRadius: 6, borderSkipped: false,
        },
        {
          label: 'Avg Carpet',
          data: sbavsCarpet.map(r => r.avg_carpet),
          backgroundColor: alpha(PALETTE.green, 0.7),
          borderColor: PALETTE.green,
          borderWidth: 2, borderRadius: 6, borderSkipped: false,
        }
      ]
    },
    options: {
      ...baseBarOptions(),
      plugins: {
        ...baseBarOptions().plugins,
        legend: { display: true, position: 'top', labels: { padding: 14, font: { size: 11 } } },
        tooltip: { mode: 'index', intersect: false },
      },
      scales: {
        x: { grid: { color: 'transparent' }, ticks: tickStyle(), border: { display: false } },
        y: { grid: gridLines(), ticks: tickStyle(), border: { display: false }, min: 800 },
      }
    }
  });

  // Chart: Area composition stacked bar by category
  destroyChart('chart-area-composition');
  charts['chart-area-composition'] = new Chart(document.getElementById('chart-area-composition'), {
    type: 'bar',
    data: {
      labels: byCategory.map(r => r.CATEGORY),
      datasets: [
        { label: 'Carpet',  data: byCategory.map(r => r.avg_carpet),  backgroundColor: alpha(PALETTE.blue, 0.75),   borderRadius: 4, stack: 'a' },
        { label: 'Balcony', data: byCategory.map(r => r.avg_balcony), backgroundColor: alpha(PALETTE.green, 0.75),  borderRadius: 4, stack: 'a' },
        { label: 'Wall',    data: byCategory.map(r => r.avg_wall),    backgroundColor: alpha(PALETTE.amber, 0.75),  borderRadius: 4, stack: 'a' },
        { label: 'Common',  data: byCategory.map(r => r.avg_common),  backgroundColor: alpha(PALETTE.purple, 0.75), borderRadius: 4, stack: 'a' },
      ]
    },
    options: {
      ...baseBarOptions(),
      plugins: {
        ...baseBarOptions().plugins,
        legend: { display: true, position: 'top', labels: { padding: 14, font: { size: 11 } } },
        tooltip: { mode: 'index', intersect: false },
      },
      scales: {
        x: { stacked: true, grid: { color: 'transparent' }, ticks: tickStyle(), border: { display: false } },
        y: { stacked: true, grid: gridLines(), ticks: tickStyle(), border: { display: false } },
      }
    }
  });

  // Chart: Garden by Tower
  destroyChart('chart-garden-tower');
  charts['chart-garden-tower'] = new Chart(document.getElementById('chart-garden-tower'), {
    type: 'bar',
    data: {
      labels: gardenAnalysis.map(r => 'Tower ' + r.TOWER),
      datasets: [{
        label: 'Total Garden (SFT)',
        data: gardenAnalysis.map(r => r.total_garden_area),
        backgroundColor: TOWER_COLORS.map(c => alpha(c, 0.7)),
        borderColor: TOWER_COLORS,
        borderWidth: 2, borderRadius: 8, borderSkipped: false,
      }]
    },
    options: {
      ...baseBarOptions(),
      plugins: {
        ...baseBarOptions().plugins,
        datalabels: {
          display: true, anchor: 'end', align: 'end',
          color: 'hsl(215,15%,65%)', font: { size: 10, weight: 600 },
          formatter: v => v.toLocaleString('en-IN') + ' SFT',
        },
      },
      scales: {
        x: { grid: { color: 'transparent' }, ticks: tickStyle(), border: { display: false } },
        y: { grid: gridLines(), ticks: tickStyle(), border: { display: false } },
      }
    }
  });

  // Chart: Balcony contribution % by category
  destroyChart('chart-balcony-contrib');
  charts['chart-balcony-contrib'] = new Chart(document.getElementById('chart-balcony-contrib'), {
    type: 'radar',
    data: {
      labels: ['Carpet %', 'Balcony %', 'Wall %', 'Common %'],
      datasets: byCategory.map((r, i) => ({
        label: r.CATEGORY,
        data: [r.carpet_pct, r.balcony_pct, r.wall_pct, r.common_pct],
        borderColor: Object.values(CAT_COLORS)[i] || PALETTE.blue,
        backgroundColor: alpha(Object.values(CAT_COLORS)[i] || PALETTE.blue, 0.1),
        pointBackgroundColor: Object.values(CAT_COLORS)[i] || PALETTE.blue,
        pointRadius: 4, borderWidth: 2,
      }))
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: {
        legend: { position: 'top', labels: { padding: 14, font: { size: 11 } } },
        datalabels: { display: false },
      },
      scales: {
        r: {
          grid: { color: 'hsl(222,20%,20%)' },
          angleLines: { color: 'hsl(222,20%,20%)' },
          pointLabels: { color: 'hsl(215,15%,60%)', font: { size: 10 } },
          ticks: { display: false },
        }
      }
    }
  });

  // Garden table
  const gBody = document.getElementById('garden-table-body');
  gBody.innerHTML = gardenAnalysis.map(r => `
    <tr>
      <td><strong>Tower ${r.TOWER}</strong></td>
      <td>${r.units_with_garden}</td>
      <td>${Number(r.total_garden_area).toLocaleString('en-IN')}</td>
      <td>${Number(r.avg_garden_area || 0).toFixed(0)}</td>
      <td>${Number(r.min_garden || 0).toLocaleString('en-IN')}</td>
      <td>${Number(r.max_garden || 0).toLocaleString('en-IN')}</td>
    </tr>
  `).join('');
}

// ═══════════════════════════════════════════════════
// PAGE 4 – SQL CONSOLE
// ═══════════════════════════════════════════════════
async function loadSchema() {
  const { columns } = await fetch('/api/schema').then(r => r.json());
  const container = document.getElementById('schema-cols');
  container.innerHTML = columns.map(c => `
    <div class="schema-col">
      <span class="schema-col-name">${c.name}</span>
      <span class="schema-col-type">${c.type || 'TEXT'}</span>
    </div>
  `).join('');
}

async function runSqlQuery() {
  const sql = document.getElementById('sql-input').value.trim();
  if (!sql) return;

  const resultsEl  = document.getElementById('sql-results');
  const countEl    = document.getElementById('sql-row-count');
  const btn        = document.getElementById('sql-run-btn');

  btn.textContent  = '⏳ Running…';
  btn.disabled     = true;
  resultsEl.innerHTML = '<div class="sql-placeholder"><div class="spinner"></div></div>';
  countEl.textContent = '';

  try {
    const res  = await fetch('/api/query', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ sql }),
    });
    const data = await res.json();

    if (data.error) {
      resultsEl.innerHTML = `<div class="sql-error">⚠ ${data.error}</div>`;
      countEl.textContent = '';
    } else if (data.rows.length === 0) {
      resultsEl.innerHTML = '<div class="sql-placeholder">Query returned 0 rows.</div>';
      countEl.textContent = '0 rows';
    } else {
      const cols = Object.keys(data.rows[0]);
      const tableHtml = `
        <div class="sql-table-wrap">
          <table class="sql-result-table">
            <thead><tr>${cols.map(c => `<th>${c}</th>`).join('')}</tr></thead>
            <tbody>
              ${data.rows.map(row =>
                `<tr>${cols.map(c => `<td>${row[c] !== null && row[c] !== undefined ? Number.isFinite(Number(row[c])) && !isNaN(Number(row[c])) && row[c] !== '' ? Number(row[c]).toLocaleString('en-IN', {maximumFractionDigits: 2}) : row[c] : '—'}</td>`).join('')}</tr>`
              ).join('')}
            </tbody>
          </table>
        </div>`;
      resultsEl.innerHTML = tableHtml;
      countEl.textContent = `${data.count} rows`;
    }
  } catch (e) {
    resultsEl.innerHTML = `<div class="sql-error">⚠ Network error: ${e.message}</div>`;
  } finally {
    btn.textContent = '▶ Run';
    btn.disabled    = false;
  }
}

function clearSql() {
  document.getElementById('sql-input').value = '';
  document.getElementById('sql-results').innerHTML = '<div class="sql-placeholder">Run a query to see results here…</div>';
  document.getElementById('sql-row-count').textContent = '';
}

function setQuery(sql) {
  document.getElementById('sql-input').value = sql;
}

// Allow Ctrl+Enter to run query
document.getElementById('sql-input').addEventListener('keydown', e => {
  if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') runSqlQuery();
});

// ═══════════════════════════════════════════════════
// UTILITIES
// ═══════════════════════════════════════════════════
function destroyChart(id) {
  if (charts[id]) { charts[id].destroy(); delete charts[id]; }
}

// ═══════════════════════════════════════════════════
// BOOT
// ═══════════════════════════════════════════════════
async function init() {
  try {
    await Promise.all([loadSummary(), loadInventory(), loadArea()]);
    await loadSchema();

    // Mark DB status
    document.querySelector('.db-status .status-text').textContent = 'Connected';

    console.log('✅ Dashboard ready');
  } catch (err) {
    console.error('Dashboard init error:', err);
    document.querySelector('.db-status .status-text').textContent = 'Error';
    document.querySelector('.status-dot').style.background = 'hsl(350,85%,60%)';
  }
}

init();

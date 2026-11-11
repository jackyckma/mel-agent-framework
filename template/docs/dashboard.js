/* global Chart */

async function loadDashboard() {
  const titleEl = document.getElementById("dash-title");
  const summaryEl = document.getElementById("summary-line");
  const updatedEl = document.getElementById("last-updated");
  const staleEl = document.getElementById("stale-warning");
  const chartsEl = document.getElementById("charts");
  const sectionList = document.getElementById("section-list");

  let data;
  try {
    const res = await fetch("data/dashboard.json", { cache: "no-store" });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    data = await res.json();
  } catch (err) {
    // Fall back to example so the shell still renders on first open / file:// quirks
    try {
      const res = await fetch("data/example.json", { cache: "no-store" });
      data = await res.json();
      summaryEl.textContent = `Using example data (${err.message}).`;
    } catch (err2) {
      titleEl.textContent = "Dashboard unavailable";
      summaryEl.textContent = String(err2);
      return;
    }
  }

  titleEl.textContent = data.title || "MEL dashboard";
  const rowCount = data.summary?.row_count ?? 0;
  const sources = (data.summary?.sources || []).join(", ") || "none";
  summaryEl.textContent = `${rowCount} processed rows · sources: ${sources}`;
  updatedEl.textContent = `Last updated: ${data.last_updated || "unknown"}`;

  // Recompute staleness at view time so a stopped pipeline still warns visitors.
  // Keep any explicit upstream stale flag from build_dashboard.py as well.
  if (data.stale || isStaleAtLoad(data)) {
    staleEl.hidden = false;
  }

  chartsEl.innerHTML = "";
  for (const chart of data.charts || []) {
    const panel = document.createElement("article");
    panel.className = "chart-panel";
    panel.innerHTML = `<h2>${escapeHtml(chart.title || chart.id)}</h2><div class="chart-wrap"><canvas></canvas></div>`;
    chartsEl.appendChild(panel);
    const canvas = panel.querySelector("canvas");
    const labels = chart.labels || [];
    const values = chart.values || [];
    // Empty chart still mounts so layout is stable
    // eslint-disable-next-line no-new
    new Chart(canvas, {
      type: chart.type || "bar",
      data: {
        labels: labels.length ? labels : ["(no data)"],
        datasets: [
          {
            label: chart.title || "Value",
            data: labels.length ? values : [0],
            backgroundColor: "#0f6b5c",
            borderSkipped: false,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          y: { beginAtZero: true, ticks: { precision: 0 } },
        },
      },
    });
  }

  sectionList.innerHTML = "";
  for (const section of data.sections || []) {
    const item = document.createElement("article");
    item.className = "section-item";
    item.innerHTML = `<h3>${escapeHtml(section.title || section.id)}</h3><p>${escapeHtml(section.body || "")}</p>`;
    sectionList.appendChild(item);
  }
}

function isStaleAtLoad(data) {
  const hours = Number(data.stale_after_hours);
  const threshold = Number.isFinite(hours) ? hours : 48;
  const stamp = data.input_fresh_at || data.last_updated;
  if (!stamp) return true;
  const then = Date.parse(stamp);
  if (Number.isNaN(then)) return true;
  return (Date.now() - then) / 3600000 > threshold;
}

function escapeHtml(s) {
  return String(s)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

loadDashboard();

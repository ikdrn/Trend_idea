import { cveByType, notableCVEs } from "./data.js";

// ─── Utilities ────────────────────────────────────────────────────────────────

const tooltip = document.getElementById("tooltip");

function showTooltip(event, html) {
  tooltip.innerHTML = html;
  tooltip.classList.add("visible");
  moveTooltip(event);
}

function moveTooltip(event) {
  const pad = 12;
  let x = event.clientX + pad + window.scrollX;
  let y = event.clientY + pad + window.scrollY;
  if (x + 290 > window.innerWidth + window.scrollX) x -= 300;
  tooltip.style.left = x + "px";
  tooltip.style.top = y + "px";
}

function hideTooltip() {
  tooltip.classList.remove("visible");
}

function cvssColor(score) {
  if (score >= 9) return "var(--critical)";
  if (score >= 8) return "var(--orange)";
  if (score >= 7) return "var(--yellow)";
  return "var(--green)";
}

function cvssClass(score) {
  if (score >= 10) return "cvss-10";
  if (score >= 9) return "cvss-9";
  if (score >= 8) return "cvss-8";
  return "cvss-7";
}

// ─── Donut Chart ──────────────────────────────────────────────────────────────

function renderDonut() {
  const svgEl = document.getElementById("donut-chart");
  const size = 200;
  const radius = size / 2;
  const inner = radius * 0.55;

  const svg = d3.select(svgEl)
    .attr("viewBox", `0 0 ${size} ${size}`);

  const arc = d3.arc().innerRadius(inner).outerRadius(radius - 4);
  const pie = d3.pie().value(d => d.count).sort(null);
  const data = pie(cveByType);

  const g = svg.append("g").attr("transform", `translate(${radius},${radius})`);

  g.selectAll("path")
    .data(data)
    .join("path")
    .attr("d", arc)
    .attr("fill", d => d.data.color)
    .attr("stroke", "#0d1117")
    .attr("stroke-width", 2)
    .style("cursor", "pointer")
    .on("mouseover", (event, d) => {
      d3.select(event.currentTarget).attr("opacity", 0.85);
      showTooltip(event, `
        <strong>${d.data.type}</strong>
        <div>${d.data.count} 件 (${d.data.pct}%)</div>
      `);
    })
    .on("mousemove", moveTooltip)
    .on("mouseout", (event) => {
      d3.select(event.currentTarget).attr("opacity", 1);
      hideTooltip();
    });

  // Center label
  g.append("text")
    .attr("text-anchor", "middle")
    .attr("dy", "-0.2em")
    .attr("fill", "#e6edf3")
    .attr("font-size", "22px")
    .attr("font-weight", "700")
    .text("83");

  g.append("text")
    .attr("text-anchor", "middle")
    .attr("dy", "1.1em")
    .attr("fill", "#8b949e")
    .attr("font-size", "10px")
    .text("CVEs");

  // Legend
  const legend = document.getElementById("donut-legend");
  legend.innerHTML = "";
  cveByType.forEach(d => {
    legend.innerHTML += `
      <div class="legend-item">
        <div class="legend-dot" style="background:${d.color}"></div>
        <span class="legend-label">${d.type}</span>
        <span class="legend-count">${d.count}</span>
      </div>`;
  });
}

// ─── Scatter Chart ────────────────────────────────────────────────────────────

function renderScatter() {
  const container = document.getElementById("scatter-chart");
  const margin = { top: 20, right: 20, bottom: 40, left: 130 };
  const totalHeight = 220;
  const totalWidth = container.parentElement.clientWidth;
  const width = totalWidth - margin.left - margin.right;
  const height = totalHeight - margin.top - margin.bottom;

  const svg = d3.select(container)
    .attr("viewBox", `0 0 ${totalWidth} ${totalHeight}`)
    .append("g")
    .attr("transform", `translate(${margin.left},${margin.top})`);

  const data = notableCVEs;
  const products = [...new Set(data.map(d => d.product))];

  const x = d3.scaleLinear().domain([6, 10.5]).range([0, width]);
  const y = d3.scaleBand().domain(products).range([0, height]).padding(0.4);

  // Grid lines
  svg.append("g").attr("class", "grid")
    .selectAll("line")
    .data(x.ticks(5))
    .join("line")
    .attr("x1", d => x(d))
    .attr("x2", d => x(d))
    .attr("y1", 0)
    .attr("y2", height);

  // X axis
  svg.append("g")
    .attr("class", "axis")
    .attr("transform", `translate(0,${height})`)
    .call(d3.axisBottom(x).ticks(5).tickFormat(d => d.toFixed(1)));

  // X axis label
  svg.append("text")
    .attr("x", width / 2)
    .attr("y", height + 35)
    .attr("text-anchor", "middle")
    .attr("fill", "#8b949e")
    .attr("font-size", "10px")
    .text("CVSS Score");

  // Y axis
  svg.append("g")
    .attr("class", "axis")
    .call(d3.axisLeft(y).tickSize(0))
    .selectAll("text")
    .attr("font-size", "10px")
    .attr("fill", "#8b949e");

  // CVSS 10.0 reference line
  svg.append("line")
    .attr("x1", x(9.0))
    .attr("x2", x(9.0))
    .attr("y1", 0)
    .attr("y2", height)
    .attr("stroke", "var(--critical)")
    .attr("stroke-dasharray", "4,3")
    .attr("stroke-width", 1)
    .attr("opacity", 0.5);

  svg.append("text")
    .attr("x", x(9.0) + 3)
    .attr("y", 12)
    .attr("fill", "var(--critical)")
    .attr("font-size", "9px")
    .text("Critical ≥9.0");

  // Dots
  svg.selectAll("circle")
    .data(data)
    .join("circle")
    .attr("cx", d => x(d.cvss))
    .attr("cy", d => y(d.product) + y.bandwidth() / 2)
    .attr("r", d => d.in_wild ? 8 : 6)
    .attr("fill", d => cvssColor(d.cvss))
    .attr("opacity", 0.85)
    .attr("stroke", d => d.cisa_kev ? "var(--kev)" : (d.in_wild ? "var(--critical)" : "transparent"))
    .attr("stroke-width", d => d.cisa_kev || d.in_wild ? 2 : 0)
    .style("cursor", "pointer")
    .on("mouseover", (event, d) => {
      d3.select(event.currentTarget).attr("r", d.in_wild ? 11 : 9);
      const tags = [
        d.in_wild ? `<span class="tag wild">実環境悪用</span>` : "",
        d.cisa_kev ? `<span class="tag kev">CISA KEV</span>` : "",
      ].filter(Boolean).join(" ");
      showTooltip(event, `
        <strong>${d.id}</strong>
        <div>${d.product}</div>
        <div class="cvss-score ${cvssClass(d.cvss)}">CVSS ${d.cvss}</div>
        <div style="margin-top:0.4rem;color:#8b949e;font-size:0.75rem">${d.description}</div>
        <div style="margin-top:0.4rem">${tags}</div>
      `);
    })
    .on("mousemove", moveTooltip)
    .on("mouseout", (event, d) => {
      d3.select(event.currentTarget).attr("r", d.in_wild ? 8 : 6);
      hideTooltip();
    });
}

// ─── Bubble / Matrix Chart ────────────────────────────────────────────────────

function renderBubble() {
  const container = document.getElementById("bubble-chart");
  const margin = { top: 20, right: 20, bottom: 50, left: 180 };
  const totalHeight = 260;
  const totalWidth = container.parentElement.clientWidth;
  const width = totalWidth - margin.left - margin.right;
  const height = totalHeight - margin.top - margin.bottom;

  const svg = d3.select(container)
    .attr("viewBox", `0 0 ${totalWidth} ${totalHeight}`)
    .append("g")
    .attr("transform", `translate(${margin.left},${margin.top})`);

  // Group CVEs by type and compute avg cvss, max cvss, count
  const grouped = d3.rollup(
    notableCVEs,
    v => ({
      count: v.length,
      avgCvss: d3.mean(v, d => d.cvss),
      maxCvss: d3.max(v, d => d.cvss),
      wildCount: v.filter(d => d.in_wild).length,
      kevCount: v.filter(d => d.cisa_kev).length,
    }),
    d => d.type
  );

  const bubbleData = Array.from(grouped, ([type, stats]) => ({ type, ...stats }));

  const x = d3.scaleLinear()
    .domain([7, 10.5])
    .range([0, width]);

  const types = bubbleData.map(d => d.type);
  const y = d3.scaleBand()
    .domain(types)
    .range([0, height])
    .padding(0.3);

  const r = d3.scaleSqrt()
    .domain([0, d3.max(bubbleData, d => d.count)])
    .range([6, 30]);

  // Grid
  svg.append("g").attr("class", "grid")
    .selectAll("line")
    .data(x.ticks(5))
    .join("line")
    .attr("x1", d => x(d))
    .attr("x2", d => x(d))
    .attr("y1", 0)
    .attr("y2", height);

  // Axes
  svg.append("g")
    .attr("class", "axis")
    .attr("transform", `translate(0,${height})`)
    .call(d3.axisBottom(x).ticks(5).tickFormat(d => d.toFixed(1)));

  svg.append("text")
    .attr("x", width / 2)
    .attr("y", height + 38)
    .attr("text-anchor", "middle")
    .attr("fill", "#8b949e")
    .attr("font-size", "10px")
    .text("平均 CVSS スコア  (バブルサイズ = CVE 件数)");

  svg.append("g")
    .attr("class", "axis")
    .call(d3.axisLeft(y).tickSize(0))
    .selectAll("text")
    .attr("font-size", "10px")
    .attr("fill", "#8b949e");

  // Bubbles
  svg.selectAll("circle")
    .data(bubbleData)
    .join("circle")
    .attr("cx", d => x(d.avgCvss))
    .attr("cy", d => y(d.type) + y.bandwidth() / 2)
    .attr("r", d => r(d.count))
    .attr("fill", d => {
      const typeObj = cveByType.find(t => t.type === d.type);
      return typeObj ? typeObj.color : "#58a6ff";
    })
    .attr("opacity", 0.7)
    .attr("stroke-width", 2)
    .attr("stroke", d => {
      const typeObj = cveByType.find(t => t.type === d.type);
      return typeObj ? typeObj.color : "#58a6ff";
    })
    .style("cursor", "pointer")
    .on("mouseover", (event, d) => {
      d3.select(event.currentTarget).attr("opacity", 1);
      showTooltip(event, `
        <strong>${d.type}</strong>
        <div>件数: ${d.count}</div>
        <div>平均 CVSS: ${d.avgCvss.toFixed(2)}</div>
        <div>最高 CVSS: ${d.maxCvss}</div>
        <div>実環境悪用: ${d.wildCount} 件</div>
        <div>CISA KEV: ${d.kevCount} 件</div>
      `);
    })
    .on("mousemove", moveTooltip)
    .on("mouseout", (event) => {
      d3.select(event.currentTarget).attr("opacity", 0.7);
      hideTooltip();
    });

  // Count labels on bubbles
  svg.selectAll(".bubble-label")
    .data(bubbleData)
    .join("text")
    .attr("class", "bubble-label")
    .attr("x", d => x(d.avgCvss))
    .attr("y", d => y(d.type) + y.bandwidth() / 2 + 4)
    .attr("text-anchor", "middle")
    .attr("fill", "#0d1117")
    .attr("font-size", "11px")
    .attr("font-weight", "700")
    .attr("pointer-events", "none")
    .text(d => d.count);
}

// ─── CVE Table ────────────────────────────────────────────────────────────────

function renderTable(filter = "all") {
  const tbody = document.getElementById("cve-tbody");

  let data = notableCVEs;
  if (filter === "Critical") data = data.filter(d => d.severity === "Critical");
  if (filter === "wild") data = data.filter(d => d.in_wild);
  if (filter === "kev") data = data.filter(d => d.cisa_kev);

  // Sort by CVSS desc
  data = [...data].sort((a, b) => b.cvss - a.cvss);

  tbody.innerHTML = data.map(d => {
    const fillColor = cvssColor(d.cvss);
    const fillWidth = ((d.cvss / 10) * 100).toFixed(0);
    const wildIcon = d.in_wild
      ? `<span class="icon-wild" title="実環境悪用確認">⚠</span>`
      : `<span class="icon-safe" title="悪用未確認">·</span>`;
    const kevIcon = d.cisa_kev
      ? `<span class="icon-kev" title="CISA KEV 掲載">★</span>`
      : "";

    return `<tr>
      <td><span class="cve-id">${d.id}</span></td>
      <td><span class="product-name" title="${d.product}">${d.product}</span></td>
      <td><span class="type-badge">${d.type}</span></td>
      <td><span class="severity-pill severity-${d.severity}">${d.severity}</span></td>
      <td class="cvss-bar-cell">
        <div class="cvss-bar">
          <div class="bar"><div class="fill" style="width:${fillWidth}%;background:${fillColor}"></div></div>
          <span class="cvss-num" style="color:${fillColor}">${d.cvss}</span>
        </div>
      </td>
      <td>${wildIcon}${kevIcon}</td>
      <td style="color:#8b949e;font-size:0.75rem;max-width:300px">${d.description}</td>
    </tr>`;
  }).join("");
}

// ─── Filter Buttons ───────────────────────────────────────────────────────────

document.querySelectorAll(".filter-btn").forEach(btn => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".filter-btn").forEach(b => b.classList.remove("active"));
    btn.classList.add("active");
    renderTable(btn.dataset.filter);
  });
});

// ─── Init ─────────────────────────────────────────────────────────────────────

renderDonut();
renderScatter();
renderBubble();
renderTable();

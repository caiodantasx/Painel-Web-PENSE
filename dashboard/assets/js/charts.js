/* Gráficos SVG: barras horizontais com IC, faixa de IC, linha simples e minigráfico. */
"use strict";

// ------------------------------------------------------------------ gráfico de barras horizontais com IC
/* items: {key, label, row, cls, group} ; opts: {m, ref, onSelect, labelKeys} */
function hbar(container, items, opts) {
  clear(container);
  if (!items.length) { container.append(el("p", { class: "empty", text: "Sem observações aprovadas para esta seleção." })); return; }
  const m = opts.m;
  const rowH = 22, barH = 13, top = 6, charW = 6.2;
  const labelW = Math.min(230, Math.max(...items.map((i) => i.label.length)) * charW + 16);
  const groupGap = 18;
  const groups = [...new Set(items.map((i) => i.group || ""))];
  const hasGroups = groups.length > 1 || groups[0] !== "";
  const W = 640, right = 64;
  const maxV = Math.max(...items.map((i) => (i.row.hi ?? i.row.e) || 0), opts.ref?.e || 0);
  const tickStep = niceStep(maxV || 1, 4);
  const xMax = isPct(m) ? Math.min(100, Math.ceil((maxV || 1) / tickStep) * tickStep) : Math.ceil((maxV || 1) / tickStep) * tickStep;
  const x = (v) => labelW + (Math.max(0, v) / xMax) * (W - labelW - right);
  let y = top + (hasGroups ? 14 : 0);
  const layout = [];
  let lastGroup = null;
  for (const it of items) {
    if (hasGroups && it.group !== lastGroup && lastGroup !== null) y += groupGap;
    layout.push({ it, y, groupStart: hasGroups && it.group !== lastGroup });
    lastGroup = it.group;
    y += rowH;
  }
  if (opts.ref && opts.ref.e !== null) { layout.forEach((l) => { l.y += 16; }); y += 16; }
  const H = y + 24;
  const root = svg("svg", { viewBox: `0 0 ${W} ${H}`, role: "img", "aria-label": opts.aria || "Gráfico de barras com intervalo de confiança" });
  const ticks = Math.round(xMax / tickStep);
  for (let k = 0; k <= ticks; k++) {
    const v = tickStep * k, px = x(v);
    root.append(svg("line", { class: k === 0 ? "baseline" : "grid-line", x1: px, x2: px, y1: top, y2: H - 20 }));
    root.append(svg("g", { class: "tick" }, svg("text", { x: px, y: H - 6, "text-anchor": "middle", text: isPct(m) ? (Number.isInteger(v) ? nf0.format(v) : nf1.format(v)) + "%" : compact(v) })));
  }
  if (opts.ref && opts.ref.e !== null) {
    const px = x(opts.ref.e);
    root.append(svg("line", { class: "refline", x1: px, x2: px, y1: top, y2: H - 20 }));
    const refText = `${opts.refLabel} ${fmt(opts.ref.e, m)}`;
    const nearRight = px > W - right - refText.length * 6.5;
    root.append(svg("text", { x: nearRight ? px - 4 : px + 4, y: top + 9, "text-anchor": nearRight ? "end" : "start",
      class: "label-strong", text: refText }));
  }
  const labelKeys = opts.labelKeys || new Set(items.map((i) => i.key));
  for (const { it, y: yy, groupStart } of layout) {
    const r = it.row;
    if (groupStart && it.group) root.append(svg("text", { class: "group-label", x: 0, y: yy - 4, text: it.group }));
    const g = svg("g", { class: "row", tabindex: "0", role: "button",
      "aria-label": `${it.label}: ${r.e === null ? "sem valor" : fmt(r.e, m)}, margem de erro entre ${fmtCI(r, m)}` });
    const cy = yy + rowH / 2;
    g.append(svg("text", { x: labelW - 8, y: cy + 4, "text-anchor": "end", class: it.cls?.includes("sel") || it.cls?.includes("ref") ? "label-strong" : "", text: fitText(it.label, labelW - 12, charW) }));
    const hit = svg("rect", { class: "hit", x: 0, y: yy, width: W, height: rowH, rx: 3 });
    g.append(hit);
    if (r.e !== null) {
      const x0 = x(0), x1 = x(r.e), w = Math.max(1, x1 - x0);
      const rad = Math.min(4, w / 2);
      g.append(svg("path", { class: `bar ${it.cls || ""} ${lowPrecision(r) ? "low" : ""}`,
        d: `M${x0},${cy - barH / 2}h${w - rad}a${rad},${rad} 0 0 1 ${rad},${rad}v${barH - 2 * rad}a${rad},${rad} 0 0 1 -${rad},${rad}h-${w - rad}z` }));
      if (r.lo !== null && r.hi !== null) {
        const a = x(r.lo), b = x(Math.min(r.hi, xMax));
        g.append(svg("line", { class: "whisker", x1: a, x2: b, y1: cy, y2: cy }));
        g.append(svg("line", { class: "whisker", x1: a, x2: a, y1: cy - 4, y2: cy + 4 }));
        g.append(svg("line", { class: "whisker", x1: b, x2: b, y1: cy - 4, y2: cy + 4 }));
      }
      if (labelKeys.has(it.key)) {
        const end = Math.max(x(r.e), r.hi !== null ? x(Math.min(r.hi, xMax)) : 0);
        g.append(svg("text", { class: "val", x: end + 6, y: cy + 4, text: fmt(r.e, m) + (lowPrecision(r) ? " ‡" : "") }));
      }
    } else {
      g.append(svg("text", { x: x(0) + 6, y: cy + 4, text: r.sym ? `símbolo "${r.sym}"` : "sem valor aprovado" }));
    }
    g.addEventListener("pointermove", (e) => showTip(e, r, m, it.tipTitle || it.label));
    g.addEventListener("pointerleave", hideTip);
    g.addEventListener("focus", (e) => showTip(e, r, m, it.tipTitle || it.label));
    g.addEventListener("blur", hideTip);
    if (opts.onSelect) {
      g.addEventListener("click", () => opts.onSelect(it));
      g.addEventListener("keydown", (e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); opts.onSelect(it); } });
    }
    root.append(g);
  }
  container.append(root);
}

function ciStrip(rows, m, max) {
  const box = el("div", { class: "ci-strip", "aria-hidden": "true" }, el("div", { class: "track" }));
  const pos = (v) => `${(Math.max(0, Math.min(v, max)) / max) * 100}%`;
  for (const { r, cls } of rows) {
    if (r.lo !== null && r.hi !== null) box.append(el("div", { class: "range", style: `left:${pos(r.lo)};width:calc(${pos(r.hi)} - ${pos(r.lo)})` }));
    box.append(el("div", { class: `dot ${cls || ""}`, style: `left:${pos(r.e)}` }));
  }
  return box;
}
function scaleMax(rows, m) {
  const v = Math.max(...rows.map((r) => (r.hi ?? r.e) || 0), 1);
  const step = niceStep(v, 4), top = Math.ceil(v / step) * step;
  return isPct(m) ? Math.min(100, top) : top;
}

function lineChart(points, m) {
  const wrap = el("div", { class: "chart" });
  const terrs = [...new Set(points.map((p) => p.territory_code))].slice(0, 2);
  const years = [...new Set(points.map((p) => p.year))].sort();
  const W = 640, H = 260, L = 48, R = 20, T = 14, Bm = 30;
  const maxV = niceMax(Math.max(...points.map((p) => p.ci_upper ?? p.estimate)));
  const x = (yr) => L + (years.length === 1 ? 0 : ((yr - years[0]) / (years[years.length - 1] - years[0])) * (W - L - R));
  const y = (v) => T + (1 - v / maxV) * (H - T - Bm);
  const root = svg("svg", { viewBox: `0 0 ${W} ${H}`, role: "img", "aria-label": "Série histórica" });
  for (let k = 0; k <= 4; k++) {
    const v = (maxV / 4) * k;
    root.append(svg("line", { class: k ? "grid-line" : "baseline", x1: L, x2: W - R, y1: y(v), y2: y(v) }),
      svg("g", { class: "tick" }, svg("text", { x: L - 6, y: y(v) + 4, "text-anchor": "end", text: fmt(v, m) })));
  }
  years.forEach((yr) => root.append(svg("g", { class: "tick" }, svg("text", { x: x(yr), y: H - 8, "text-anchor": "middle", text: yr }))));
  const colors = ["var(--accent)", "var(--select)"];
  terrs.forEach((tc, ti) => {
    const pts = points.filter((p) => p.territory_code === tc).sort((a, b) => a.year - b.year);
    const band = pts.filter((p) => p.ci_lower !== null);
    if (band.length > 1) root.append(svg("path", { class: "band", fill: colors[ti],
      d: band.map((p, j) => `${j ? "L" : "M"}${x(p.year)},${y(p.ci_upper)}`).join("") +
         band.slice().reverse().map((p) => `L${x(p.year)},${y(p.ci_lower)}`).join("") + "Z" }));
    root.append(svg("path", { class: "series-line", stroke: colors[ti], d: pts.map((p, j) => `${j ? "L" : "M"}${x(p.year)},${y(p.estimate)}`).join("") }));
    pts.forEach((p) => root.append(svg("circle", { cx: x(p.year), cy: y(p.estimate), r: 4.5, fill: colors[ti], stroke: "var(--card)", "stroke-width": 2 })));
    const last = pts[pts.length - 1];
    root.append(svg("text", { x: x(last.year) - 6, y: y(last.estimate) - 9, "text-anchor": "end", class: "label-strong", text: `${last.territory_name} ${fmt(last.estimate, m)}` }));
  });
  wrap.append(root);
  return wrap;
}

function sparkline(points) {
  const W = 120, H = 34, years = [Math.min(2015, ...points.map((p) => p.year)), 2024];
  const vals = points.flatMap((p) => [p.lo ?? p.e, p.hi ?? p.e]);
  const lo = Math.min(...vals), hi = Math.max(...vals), span = hi - lo || 1;
  const x = (yr) => 4 + ((yr - years[0]) / (years[1] - years[0])) * (W - 8);
  const y = (v) => 4 + (1 - (v - lo) / span) * (H - 8);
  const root = svg("svg", { viewBox: `0 0 ${W} ${H}`, "aria-hidden": "true" });
  if (points.length > 1) {
    root.append(svg("path", { class: "band", d: points.map((p, j) => `${j ? "L" : "M"}${x(p.year)},${y(p.hi)}`).join("") +
      points.slice().reverse().map((p) => `L${x(p.year)},${y(p.lo)}`).join("") + "Z" }));
    root.append(svg("path", { class: "ln", d: points.map((p, j) => `${j ? "L" : "M"}${x(p.year)},${y(p.e)}`).join("") }));
  }
  points.forEach((p) => root.append(svg("circle", { cx: x(p.year), cy: y(p.e), r: 3 })));
  return el("span", { class: "spark" }, root);
}

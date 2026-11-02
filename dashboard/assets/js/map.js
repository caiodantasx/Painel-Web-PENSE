/* Mapa do Brasil: projeção da malha das UFs e coroplético / marcadores das capitais. */
"use strict";

function projector() {
  if (PROJ) return PROJ;
  const k = Math.cos((-15 * Math.PI) / 180);
  let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;
  const rings = (g) => (g.type === "Polygon" ? [g.coordinates] : g.coordinates);
  for (const f of GEO.features) for (const poly of rings(f.geometry)) for (const ring of poly) for (const [lon, lat] of ring) {
    minX = Math.min(minX, lon * k); maxX = Math.max(maxX, lon * k); minY = Math.min(minY, -lat); maxY = Math.max(maxY, -lat);
  }
  const W = 560, pad = 6, s = (W - 2 * pad) / (maxX - minX), H = (maxY - minY) * s + 2 * pad;
  const pt = (lon, lat) => [pad + (lon * k - minX) * s, pad + (-lat - minY) * s];
  const shapes = GEO.features.map((f) => {
    let d = "", best = null, bestArea = -1;
    for (const poly of rings(f.geometry)) {
      const outer = poly[0];
      let x0 = Infinity, x1 = -Infinity, y0 = Infinity, y1 = -Infinity;
      for (const ring of poly) {
        d += ring.map(([lon, lat], j) => { const [x, y] = pt(lon, lat); if (ring === outer) { x0 = Math.min(x0, x); x1 = Math.max(x1, x); y0 = Math.min(y0, y); y1 = Math.max(y1, y); }
          return `${j ? "L" : "M"}${x.toFixed(1)},${y.toFixed(1)}`; }).join("") + "Z";
      }
      const area = (x1 - x0) * (y1 - y0);
      if (area > bestArea) { bestArea = area; best = [(x0 + x1) / 2, (y0 + y1) / 2, area]; }
    }
    return { code: f.properties.uf_code, d, center: best };
  });
  PROJ = { W, H, pt, shapes };
  return PROJ;
}

function renderMap() {
  const m = measure(), wrap = clear($("map")), legend = clear($("map-legend"));
  $("map-eyebrow").textContent = `Mapa · PeNSE ${m.year} · Tabela ${m.tables}`;
  $("map-title").textContent = m.category ? `${m.short_label} · ${m.category}` : m.short_label;
  const mr = clear($("map-reading"));
  const href = refRowFor(currentRows());
  mr.append(el("span", { class: "unit-label", text: `Cores do mapa: ${m.unit_label || "%"}${cutText()}. ` }),
    href ? el("span", { text: readingOf(m, href) }) : null);
  const sub = $("map-sub");
  sub.textContent = "";
  if (!isPct(m)) {
    wrap.append(el("div", { class: "map-empty", text: "O mapa só mostra percentuais. Com números absolutos, os estados mais populosos sempre pareceriam piores. Escolha “percentual” em “Mostrar como” ou use a lista abaixo." }));
    return;
  }
  if (!GEO) { wrap.append(el("div", { class: "map-empty", text: "Malha geográfica não carregada." })); return; }
  const mode = state.scope;
  const rows = scopeRows();
  const vals = rows.filter((r) => approved(r) && r.t.type !== "country");
  if (!vals.length) {
    wrap.append(el("div", { class: "map-empty", text: "Sem estimativas aprovadas para este recorte territorial. Troque o recorte acima ou ajuste os filtros." }));
    return;
  }
  const P = projector();
  const lo = Math.min(...vals.map((r) => r.e)), hi = Math.max(...vals.map((r) => r.e));
  const step = (hi - lo) / 5 || 1;
  const cls = (v) => "q" + Math.min(5, Math.floor((v - lo) / step) + 1);
  const root = svg("svg", { viewBox: `0 0 ${P.W} ${P.H.toFixed(0)}`, role: "img",
    "aria-label": `Mapa do Brasil — ${SCOPES[mode].label}; os mesmos valores estão na lista abaixo` });
  const ufTerr = new Map(idx.terr.filter((t) => t.type === "uf").map((t) => [t.uf_code, t]));
  const byCode = new Map(rows.map((r) => [r.t.code, r]));
  const bind = (node, r, code) => {
    node.addEventListener("pointermove", (e) => showTip(e, r, m, r.t.type === "region" ? `Região ${r.t.name}` : shortName(r.t)));
    node.addEventListener("focus", (e) => showTip(e, r, m));
    node.addEventListener("pointerleave", hideTip);
    node.addEventListener("blur", hideTip);
    node.addEventListener("click", () => selectTerritory(code));
    node.addEventListener("keydown", (e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); selectTerritory(code); } });
  };
  for (const sh of P.shapes) {
    const ut = ufTerr.get(sh.code);
    let r = null;
    if (mode === "uf") r = ut ? byCode.get(ut.code) : null;
    else if (mode === "regional") r = ut ? byCode.get(ut.region) : null;
    if (mode === "capital" || !r) {
      root.append(svg("path", { d: sh.d, class: mode === "capital" ? "base" : "nd",
        "aria-label": mode === "capital" ? null : `${ut ? ut.name : sh.code}: sem estimativa aprovada` }));
      continue;
    }
    const ok = approved(r);
    const p = svg("path", { d: sh.d, class: `${ok ? cls(r.e) : "nd"} ${state.selected === r.t.code ? "sel" : ""}`, tabindex: mode === "uf" ? "0" : "-1",
      "aria-label": `${r.t.name}: ${ok ? fmt(r.e, m) : "sem valor confiável"}` });
    bind(p, r, r.t.code);
    root.append(p);
  }
  if (mode === "uf") {
    for (const sh of P.shapes) {
      const ut = ufTerr.get(sh.code);
      if (ut && sh.center && sh.center[2] > 260) root.append(svg("text", { class: "uf-label", x: sh.center[0], y: sh.center[1] + 3, "text-anchor": "middle", text: ut.uf }));
    }
  }
  if (mode === "regional") {
    // selecionado por cima, para o contorno não ficar escondido
    root.querySelectorAll("path.sel").forEach((n) => root.append(n));
  }
  if (mode === "capital") {
    const caps = rows.filter((r) => r.t.type === "capital").sort((a, b) => (a.t.code === state.selected) - (b.t.code === state.selected));
    for (const r of caps) {
      const c = CAPS && CAPS[r.t.uf];
      if (!c) continue;
      const [x, y] = P.pt(c[0], c[1]);
      const ok = approved(r);
      const dot = svg("circle", { cx: x.toFixed(1), cy: y.toFixed(1), r: state.selected === r.t.code ? 9 : 7,
        class: `${ok ? cls(r.e) : "nd"} ${state.selected === r.t.code ? "sel" : ""}`, tabindex: "0",
        "aria-label": `${shortName(r.t)}: ${ok ? fmt(r.e, m) : "sem valor confiável"}` });
      bind(dot, r, r.t.code);
      root.append(dot);
    }
  } else {
    // regiões e UFs: o contorno do selecionado vem por último
    root.querySelectorAll("path.sel").forEach((n) => root.append(n));
  }
  wrap.append(root);
  sub.textContent = mode === "capital"
    ? `${vals.length} capitais · marcador na posição aproximada da sede municipal · cor = estimativa`
    : `${vals.length} ${mode === "uf" ? "estados" : "regiões"} · ${document.documentElement.dataset.theme === "light" ? "do mais claro (menor valor) ao mais escuro (maior valor)" : "do mais escuro (menor valor) ao mais claro e brilhante (maior valor)"}, em 5 faixas de mesmo tamanho · valores em ${unitShort(m)}`;
  const ramp = el("div", { class: "ramp" });
  for (let q = 1; q <= 5; q++) {
    ramp.append(el("span", null, el("i", { style: `background: var(--seq-${q})` }), nf1.format(lo + step * (q - 1))));
  }
  legend.append(ramp, el("span", null, el("span", { class: "sw", style: "background: var(--nodata); outline: 1px solid var(--axis)" }),
    mode === "capital" ? "estado sem cor (o valor é da capital)" : "sem valor confiável"));
}

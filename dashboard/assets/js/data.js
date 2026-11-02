/* Estado global e acesso ao pacote de dados (dashboard/data/pense_bundle.json). */
"use strict";

let B = null, GEO = null, CAPS = null, PROJ = null;
const idx = { byMeasure: new Map(), measures: [], terr: [], indicators: new Map() };
const state = { page: "overview", edition: "", indicator: "", measure: -1, age: "Total", sex: "Total", dep: "Total",
                scope: "uf", availScopes: [], selected: null, sort: "desc" };

// ------------------------------------------------------------------ dados
function prepare() {
  const o = B.obs;
  idx.measures = B.measures;
  idx.terr = B.territories;
  for (let i = 0; i < o.m.length; i++) {
    if (!idx.byMeasure.has(o.m[i])) idx.byMeasure.set(o.m[i], []);
    idx.byMeasure.get(o.m[i]).push(i);
  }
  B.measures.forEach((m, mi) => {
    if (!idx.indicators.has(m.indicator_id)) idx.indicators.set(m.indicator_id, []);
    idx.indicators.get(m.indicator_id).push(mi);
  });
}
function row(i) {
  const o = B.obs;
  return {
    i, m: o.m[i], t: idx.terr[o.t[i]], a: B.dims.age_group[o.a[i]], s: B.dims.sex[o.s[i]], d: B.dims.admin_dependency[o.d[i]],
    e: o.e[i], lo: o.lo[i], hi: o.hi[i], cv: o.cv[i], st: B.meta.status_order[o.st[i]], src: B.sources[o.src[i]],
    cell: o.cell[i], sym: o.sym[i], rules: o.rules[i], id: o.id[i],
  };
}
const rowsOf = (mi) => (idx.byMeasure.get(mi) || []).map(row);
const approved = (r) => APPROVED.has(r.st) && r.e !== null;
const lowPrecision = (r) => (r.rules || "").includes("VAL008");
const dimsMatch = (r, a, s, d) => r.a === a && r.s === s && r.d === d;
function currentRows() { return rowsOf(state.measure).filter((r) => dimsMatch(r, state.age, state.sex, state.dep)); }
function headlineRow(rows) {
  return rows.find((r) => r.t.code === "BR") || rows.find((r) => r.t.code === "CAPITAIS") || null;
}

function editions() {
  // Uma edição por vez no mapa; a série oficial do 9º ano (vários anos na mesma tabela) fica na página "Série histórica".
  const seen = new Map();
  B.measures.forEach((m) => { if (!m.multi_year) seen.set(m.edition_id, m.year); });
  return [...seen.entries()].sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]));
}
const editionMeta = (e) => (B.meta.editions || []).find((x) => x.edition_id === e) || {};
const editionLabel = (e, y) => editionMeta(e).label || `PeNSE ${y}`;

function indicatorsOf(edition) {
  return [...idx.indicators.keys()].filter((k) => B.measures[idx.indicators.get(k)[0]].edition_id === edition)
    .sort((a, b) => {
      const fa = B.measures[idx.indicators.get(a)[0]].table_family_id.split(".").map(Number);
      const fb = B.measures[idx.indicators.get(b)[0]].table_family_id.split(".").map(Number);
      return fb[0] - fa[0] || fa[1] - fb[1] || (fa[2] || 0) - (fb[2] || 0);
    });
}
function categoryLabel(m) {
  const base = m.category || "Indicador geral";
  return m.category_group ? `${base} (${m.category_group.replace("Distribuição percentual por ", "por ")})` : base;
}

function measure() { return B.measures[state.measure]; }

function refRowFor(rows) {
  const sc = SCOPES[state.scope];
  return rows.find((r) => r.t.code === sc.ref && approved(r)) || headlineRow(rows.filter(approved));
}
const shortName = (t) => (t.code === "CAPITAIS" ? "Conjunto das capitais" : t.type === "capital" ? t.name.replace(" (capital)", "") : t.name);

function countBy(arr, f) { const o = {}; for (const x of arr) { const k = f(x); o[k] = (o[k] || 0) + 1; } return o; }

function scopeRows() {
  const sc = SCOPES[state.scope];
  return currentRows().filter((r) => sc.types.includes(r.t.type));
}

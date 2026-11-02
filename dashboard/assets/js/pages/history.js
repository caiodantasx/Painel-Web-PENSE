/* Página “Série histórica”: série harmonizada pelos microdados, série oficial do 9º ano
 * e situação das tabelas publicadas. */
"use strict";

function renderHistory() {
  const m = measure(), box = clear($("history-main"));
  const pairs = B.comparability.filter((p) => p.left_indicator_id === m.indicator_id || p.right_indicator_id === m.indicator_id);
  const series = B.series.filter((p) => p.indicator_id === m.indicator_id || pairs.some((q) => q.concept_id === p.concept_id));
  box.append(el("header", { class: "panel-head" }, el("div", null, el("h2", { text: "Tabelas publicadas: indicador escolhido nos filtros" }),
    el("p", { class: "card-sub", text: "Só entram em série os pares de edições classificados como comparáveis por decisão documentada. A série harmonizada, acima, usa os microdados." }))));
  if (series.length) {
    box.append(lineChart(series, m));
    return;
  }
  const msg = el("div", { class: "empty" });
  if (!pairs.length) {
    msg.append(el("strong", { text: "Sem correspondente identificado em outras edições da base. " }),
      "Este indicador aparece apenas na PeNSE " + m.year + " entre os arquivos processados; por isso não há série histórica.");
  } else {
    msg.append(el("strong", { text: "Nenhuma série histórica aprovada para este indicador. " }),
      "Existem correspondências candidatas, mas a avaliação metodológica encontrou diferenças essenciais. ",
      "Exibir os valores das edições lado a lado sugeriria uma tendência que os dados não sustentam.");
    const ul = el("ul");
    for (const p of pairs) ul.append(el("li", null, el("b", { text: `${p.left_indicator_id} × ${p.right_indicator_id}${p.right_category ? " [" + p.right_category + "]" : ""}: ` }),
      p.differences || p.final_justification));
    msg.append(ul);
  }
  box.append(msg);
}

function renderComparability() {
  const m = measure();
  const rows = B.comparability.slice().sort((a, b) => {
    const ra = a.left_indicator_id === m.indicator_id || a.right_indicator_id === m.indicator_id ? 0 : 1;
    const rb = b.left_indicator_id === m.indicator_id || b.right_indicator_id === m.indicator_id ? 0 : 1;
    return ra - rb || a.concept_id.localeCompare(b.concept_id);
  });
  const lab = (id, cat) => {
    const mi = idx.indicators.get(id);
    const short = mi ? B.measures[mi[0]].short_label : id;
    return `${id.replace("PENSE_", "").replace("__", " · ")} — ${short}${cat ? " [" + cat + "]" : ""}`;
  };
  table($("table-comparability"), [
    { label: "Conceito", cls: "mono", render: (p) => p.concept_id },
    { label: "Edição anterior", render: (p) => lab(p.left_indicator_id, p.left_category) },
    { label: "Edição posterior", render: (p) => lab(p.right_indicator_id, p.right_category) },
    { label: "Status", render: (p) => chip(p.final_status, COMP_LABEL) },
    { label: "Diferenças essenciais", cls: "wrap", render: (p) => p.differences || p.final_justification },
    { label: "Decisão", render: (p) => p.decision_source },
  ], rows, { isSel: (p) => p.left_indicator_id === m.indicator_id || p.right_indicator_id === m.indicator_id });
}

// ------------------------------------------------------------------ série harmonizada (microdados)
const CUTS = [
  ["Total", "Total", "Total", "Total (13 a 17 anos)"], ["13 a 15 anos", "Total", "Total", "13 a 15 anos"],
  ["16 e 17 anos", "Total", "Total", "16 e 17 anos"], ["Total", "Homem", "Total", "Homem"], ["Total", "Mulher", "Total", "Mulher"],
  ["Total", "Total", "Pública", "Escola pública"], ["Total", "Total", "Privada", "Escola privada"],
];
const PERIOD_LABEL = { "30_DIAS": "nos 30 dias anteriores à pesquisa", "12_MESES": "nos 12 meses anteriores à pesquisa", VIDA: "alguma vez na vida" };
const VAL_LABEL = { VALIDADO: ["Reproduz o publicado", "good"], VALIDADO_COM_RESSALVA: ["Reproduz com pequenas diferenças", "warning"],
  NAO_VALIDADO: ["Não reproduz", "critical"] };
let M = null;
const mstate = { key: "", terr: "BR", cut: 0 };

function microPrepare() {
  M = B.micro || null;
  if (!M) return;
  M.idx = new Map();
  const E = M.est;
  for (let i = 0; i < E.k.length; i++) {
    const key = `${E.k[i]}|${E.t[i]}|${E.a[i]}|${E.s[i]}|${E.d[i]}`;
    if (!M.idx.has(key)) M.idx.set(key, []);
    M.idx.get(key).push(i);
  }
  M.tIndex = new Map(M.territories.map((t, i) => [t.code, i]));
  M.kIndex = new Map(M.indicators.map((x, i) => [x.key, i]));
  const first = M.indicators.find((x) => x.editions.length === 3 && x.comparability.final_status.startsWith("COMPARABLE"));
  mstate.key = (first || M.indicators[0]).key;
}
function microPoints(key, terr, cutIdx) {
  const [a, s, d] = CUTS[cutIdx];
  const k = M.kIndex.get(key), t = M.tIndex.get(terr);
  const ia = M.dims.age_group.indexOf(a), is = M.dims.sex.indexOf(s), id = M.dims.admin_dependency.indexOf(d);
  const E = M.est;
  return (M.idx.get(`${k}|${t}|${ia}|${is}|${id}`) || []).map((i) => ({
    ed: M.editions[E.ed[i]], year: M.editions[E.ed[i]].year, e: E.e[i], lo: E.lo[i], hi: E.hi[i], se: E.se[i],
    cv: E.cv[i], n: E.n[i], lp: !!E.lp[i], pe: E.pe ? E.pe[i] : null,
    inSeries: (M.indicators[k].comparability.series_editions || "").split("|").includes(M.editions[E.ed[i]].id),
    excludedByDecision: (M.indicators[k].comparability.excluded_edition_ids || "").split("|").includes(M.editions[E.ed[i]].id),
  })).sort((x, y) => x.year - y.year);
}
const microInd = (key) => M.indicators[M.kIndex.get(key)];
const pp = (v) => (v > 0 ? "+" : v < 0 ? "−" : "") + nf1.format(Math.abs(v)) + " p.p.";
const pct = (v) => (v === null || v === undefined ? "—" : nf1.format(v) + "%");
function microDiff(key, terr, cutIdx, year) {
  const [a, s, d] = CUTS[cutIdx];
  return M.diffs[`${key}|${terr}|${a}|${s}|${d}|${year}`] || null;
}
const comparable = (ind) => ind.comparability.final_status.startsWith("COMPARABLE");
const compChip = (c) => el("span", null, chip(c.final_status, COMP_LABEL),
  el("small", { class: "decision", text: c.decision_status === "DECISAO_REGISTRADA" ? " decisão registrada" : " proposta automática" }));

function renderMicroOverview() {
  const years = [...new Set(M.editions.map((e) => e.year))].sort((x, y) => x - y);
  const rows = M.indicators.filter((ind) => ind.population !== "9ANO").map((ind) => ({ ind, pts: microPoints(ind.key, "BR", 0) }));
  const order = (r) => (r.ind.informant.startsWith("Escola (") ? 1 : 0) * 100 + (3 - r.ind.editions.length);
  rows.sort((a, b) => order(a) - order(b));
  const cols = [
    { label: "Indicador", cls: "ind", render: (r) => el("span", null, r.ind.label,
      el("small", { text: `${r.ind.informant.startsWith("Escola (") ? "Escola (diretor)" : "Aluno"} · ${PERIOD_LABEL[r.ind.period] || r.ind.period}` })) },
    ...years.map((yr) => ({ label: String(yr), cls: "num", render: (r) => {
      const p = r.pts.find((q) => q.year === yr);
      return p ? pct(p.e) + (p.lp ? " ‡" : "") + (p.inSeries ? "" : " †") : (r.ind.editions.some((e) => M.editions.find((x) => x.id === e)?.year === yr) ? "—" : "não comparável");
    } })),
    { label: "Tendência", render: (r) => (comparable(r.ind) ? sparkline(r.pts.filter((p) => p.inSeries)) : "") },
    { label: "Última variação", cls: "num", help: "pp", render: (r) => {
      const last = r.pts.filter((p) => p.inSeries).pop();
      const dd = last && comparable(r.ind) ? microDiff(r.ind.key, "BR", 0, last.year) : null;
      if (!dd) return el("span", { class: "arrow ns", text: "—" });
      const [prev, diff, , , , status] = dd;
      return el("span", { class: `arrow ${confirmed(status) ? (diff > 0 ? "sig-up" : "sig-down") : "ns"}`,
        text: `${diff > 0 ? "▲" : "▼"} ${pp(diff)}`, title: `${prev} → ${last.year} · ${CHANGE_LABEL[status || "NAO_SIGNIFICATIVA"][0]}` });
    } },
    { label: "Diferença significativa?", help: "significativa", render: (r) => {
      const last = r.pts.filter((p) => p.inSeries).pop();
      const dd = last && comparable(r.ind) ? microDiff(r.ind.key, "BR", 0, last.year) : null;
      return dd ? changeChip(dd[5]) : "";
    } },
    { label: "Pode comparar os anos?", render: (r) => compChip(r.ind.comparability), help: "", helpText: "Comparável com ressalvas: mesma pergunta e mesmo público, com pequenas diferenças registradas no detalhe. Pendente de revisão: falta conferir algo antes de comparar. Não comparável: a pergunta ou o público mudou. “Proposta automática” quer dizer que a pipeline sugeriu, mas o pesquisador ainda não decidiu." },
  ];
  table($("table-micro-overview"), cols, rows, { onClick: (r) => { mstate.key = r.ind.key; renderMicroDetail(); $("micro-detail").scrollIntoView({ behavior: "smooth", block: "start" }); },
    isSel: (r) => r.ind.key === mstate.key });
  const lg = clear($("micro-overview-legend"));
  lg.append(el("span", null, el("span", { class: "origin", text: "Calculado dos microdados" }), " ", help("microdados")),
    el("span", null, "▲▼ = quanto mudou entre as duas últimas pesquisas, em pontos percentuais ", help("pp")),
    el("span", null, "“Diferença significativa a 5%” só com decisão do pesquisador registrada; não quer dizer grande nem importante ", help("significativa")),
    el("span", null, "† = ano fora da série principal: sem tabela do IBGE para conferir o cálculo, ou excluído por decisão registrada"),
    el("span", null, "‡ = estimativa pouco precisa ", help("precisao")));
}

function microLineChart(points, m, isComparable) {
  const W = 640, H = 280, L = 52, R = 24, T = 26, Bm = 34;
  const years = [2015, 2024];
  const vmax = Math.max(...points.map((p) => p.hi ?? p.e), 1);
  const step = niceStep(vmax, 4), top = Math.min(100, Math.ceil(vmax / step) * step);
  const x = (yr) => L + ((yr - years[0]) / (years[1] - years[0])) * (W - L - R);
  const y = (v) => T + (1 - v / top) * (H - T - Bm);
  const root = svg("svg", { viewBox: `0 0 ${W} ${H}`, role: "img", "aria-label": "Série histórica com intervalo de confiança de 95%" });
  for (let k = 0; k * step <= top + 1e-9; k++) {
    const v = k * step;
    root.append(svg("line", { class: k ? "grid-line" : "baseline", x1: L, x2: W - R, y1: y(v), y2: y(v) }),
      svg("g", { class: "tick" }, svg("text", { x: L - 8, y: y(v) + 4, "text-anchor": "end", text: (Number.isInteger(v) ? nf0.format(v) : nf1.format(v)) + "%" })));
  }
  M.editions.forEach((e) => root.append(svg("text", { class: "yr", x: x(e.year), y: H - 10, "text-anchor": "middle", text: String(e.year) })));
  if (isComparable && points.length > 1) {
    root.append(svg("path", { class: "ci-band", fill: "var(--accent)", d: points.map((p, j) => `${j ? "L" : "M"}${x(p.year)},${y(p.hi)}`).join("") +
      points.slice().reverse().map((p) => `L${x(p.year)},${y(p.lo)}`).join("") + "Z" }));
    root.append(svg("path", { class: "series-line", stroke: "var(--accent)", d: points.map((p, j) => `${j ? "L" : "M"}${x(p.year)},${y(p.e)}`).join("") }));
  }
  points.forEach((p) => {
    const g = svg("g", { class: "row", tabindex: "0", role: "button", "aria-label": `${p.year}: ${pct(p.e)}, margem de erro entre ${pct(p.lo)} e ${pct(p.hi)}` });
    g.append(svg("line", { class: "whisker", x1: x(p.year), x2: x(p.year), y1: y(p.lo), y2: y(p.hi) }));
    g.append(svg("circle", { cx: x(p.year), cy: y(p.e), r: 6, fill: "var(--accent)", stroke: "var(--card)", "stroke-width": 2 }));
    const anchor = p.year === 2015 ? "start" : p.year === 2024 ? "end" : "middle";
    g.append(svg("text", { class: "pt-label", x: x(p.year) + (anchor === "start" ? 10 : anchor === "end" ? -10 : 0), y: y(p.hi) - 8, "text-anchor": anchor, text: pct(p.e) + (p.lp ? " ‡" : "") }));
    const row = { t: { name: p.ed.label }, e: p.e, lo: p.lo, hi: p.hi, cv: p.cv, st: "VALID", src: `microdados ${p.ed.id}`, cell: `n = ${nf0.format(p.n)}` };
    g.addEventListener("pointermove", (ev) => showTip(ev, row, m, `${p.ed.label} · n = ${nf0.format(p.n)} escolares`));
    g.addEventListener("pointerleave", hideTip);
    g.addEventListener("focus", (ev) => showTip(ev, row, m, `${p.ed.label} · n = ${nf0.format(p.n)} escolares`));
    g.addEventListener("blur", hideTip);
    root.append(g);
  });
  return root;
}

function renderMicroDetail() {
  const ind = microInd(mstate.key);
  const m = { unit: "%" };
  fillSelect($("f-micro-indicator"), M.indicators.map((x) => ({ value: x.key, label: `${x.informant.startsWith("Escola (") ? "Escola · " : ""}${x.label}` })), mstate.key);
  const k = M.kIndex.get(mstate.key);
  const tAvail = new Set();
  for (let i = 0; i < M.est.k.length; i++) if (M.est.k[i] === k) tAvail.add(M.territories[M.est.t[i]].code);
  const terrs = M.territories.filter((t) => tAvail.has(t.code));
  const order = { country: 0, region: 1, aggregate: 2, uf: 3, capital: 4 };
  terrs.sort((a, b) => order[a.type] - order[b.type] || a.name.localeCompare(b.name, "pt-BR"));
  if (!tAvail.has(mstate.terr)) mstate.terr = "BR";
  fillSelect($("f-micro-terr"), terrs.map((t) => ({ value: t.code, label: t.type === "capital" ? `${t.name} (capital)` : t.name })), mstate.terr);
  fillSelect($("f-micro-cut"), CUTS.map((c, i) => ({ value: String(i), label: c[3], disabled: !microPoints(mstate.key, mstate.terr, i).length })), String(mstate.cut));
  const pts = microPoints(mstate.key, mstate.terr, mstate.cut);
  const terrName = (terrs.find((t) => t.code === mstate.terr) || {}).name || mstate.terr;
  $("micro-eyebrow").textContent = `${ind.informant.startsWith("Escola (") ? "Característica da escola informada pelo diretor" : "Resposta do aluno"} · ${PERIOD_LABEL[ind.period] || ""}`;
  $("micro-title").textContent = `${ind.label} — ${terrName}, ${CUTS[mstate.cut][3].toLowerCase()}`;
  $("micro-question").textContent = ind.question;
  const popTxt = ind.population === "9ANO" ? "escolares do 9º ano" : "escolares de 13 a 17 anos";
  const lab = ind.label.replace(/^9º ano · /, "");
  $("micro-reading").textContent = `Como ler: cada valor é a % dos ${popTxt} ` + (ind.informant.startsWith("Escola (")
    ? `que estudam em escolas cujo diretor(a) informou: ${lab.replace(/^Em escolas (cujo diretor |que )/i, "").toLowerCase()}.`
    : `que relataram: ${lab[0].toLowerCase() + lab.slice(1)}.`) + " Respostas a questionário (pesquisa por amostra), não registros de ocorrência.";
  const chartBox = clear($("chart-micro"));
  if (!pts.length) chartBox.append(el("p", { class: "empty", text: "Sem estimativa para esta combinação." }));
  else {
    const linePts = comparable(ind) ? pts.filter((p) => p.inSeries) : pts;
    chartBox.append(microLineChart(linePts.length ? linePts : pts, m, comparable(ind) && linePts.length > 1));
    if (!comparable(ind)) chartBox.append(el("p", { class: "empty" }, el("strong", { text: "Pontos sem linha: " }),
      "a comparação entre anos está pendente de revisão (veja as evidências abaixo). Os valores de cada ano são corretos, mas não devem ser lidos como tendência."));
  }
  const side = clear($("micro-changes"));
  side.append(el("span", { class: "origin", text: "Calculado dos microdados" }));
  if (comparable(ind)) {
    for (const p of pts.slice(1)) {
      const dd = microDiff(mstate.key, mstate.terr, mstate.cut, p.year);
      if (!dd) continue;
      const [prev, diff, lo, hi, sig, status] = dd;
      side.append(el("div", { class: "change" },
        el("span", { class: "yrs", text: `${prev} → ${p.year}` }),
        el("span", { class: "delta" }, pp(diff), el("small", { text: ciDiffText(lo, hi, !!sig) })),
        el("div", null, changeChip(status), " ", help("significativa"))));
    }
  }
  for (const p of pts) side.append(el("div", { class: "detail", text: `${p.year}: ${pct(p.e)} (entre ${pct(p.lo)} e ${pct(p.hi)}) · ${nf0.format(p.n)} alunos responderam${p.lp ? " · pouco preciso" : ""}`
    + (p.pe !== null && p.pe !== undefined ? ` · valor com a regra da série; na tabela do IBGE de ${p.year}: ${pct(p.pe)}` : "")
    + (p.inSeries ? "" : p.excludedByDecision ? " · fora da série principal por decisão registrada (veja as ressalvas); valor disponível só para consulta"
      : " · fora da série (sem tabela do IBGE para conferir)") }));

  const ev = clear($("micro-evidence"));
  const c = ind.comparability;
  ev.append(el("div", { class: "ev" }, el("h3", { text: "Comparabilidade entre anos" }),
    el("div", null, compChip(c)), el("p", { text: c.decision_source }),
    c.evidence_by_edition ? el("p", { text: `Conferência por edição: ${c.evidence_by_edition.replaceAll("DIRETA", "tabela do IBGE reproduzida").replaceAll("INDIRETA", "mesma variável reproduz tabelas da edição").replaceAll("AUSENTE", "sem tabela para conferir").replaceAll("FALHOU", "não reproduz")}` }) : null,
    el("ul", null, ...c.justification.split("; ").filter(Boolean).map((t) => el("li", { text: t })))));
  if (c.caveats) ev.append(el("div", { class: "ev" }, el("h3", { text: "Ressalvas" }),
    el("ul", null, ...c.caveats.split("; ").filter(Boolean).map((t) => el("li", { text: t })))));
  const val = el("div", { class: "ev" }, el("h3", { text: "Conferência com as tabelas do IBGE" }));
  for (const e of M.editions) {
    if (!ind.editions.includes(e.id)) continue;
    const v = ind.validation[e.id];
    if (v) val.append(el("p", null, el("b", { text: `${e.year}: ` }), chip(v.status, VAL_LABEL),
      ` tabela ${v.table}: o cálculo deu igual ao publicado em ${v.reproduz} de ${v.compared} grupos; a maior diferença foi de ${nf1.format(v.max_diff)} ponto percentual.`));
    else val.append(el("p", null, el("b", { text: `${e.year}: ` }), "sem tabela do IBGE para conferir este indicador nesta edição"
      + ((ind.comparability.series_editions || "").split("|").includes(e.id) ? " (validação indireta: a mesma variável reproduz tabelas da edição)." : ": o ano fica fora da série.")));
  }
  ev.append(val, el("div", { class: "ev" }, el("h3", { text: "Método" }), el("p", { text: M.method }),
    ind.definition_note ? el("p", { text: ind.definition_note }) : null));
}

function bindMicro() {
  $("f-micro-indicator").addEventListener("change", (e) => { mstate.key = e.target.value; renderMicro(); });
  $("f-micro-terr").addEventListener("change", (e) => { mstate.terr = e.target.value; renderMicroDetail(); });
  $("f-micro-cut").addEventListener("change", (e) => { mstate.cut = Number(e.target.value); renderMicroDetail(); });
}
function renderMicro() {
  const has = !!M;
  $("micro-overview").hidden = !has;
  $("micro-detail").hidden = !has;
  if (!has) return;
  renderMicroOverview();
  renderMicroDetail();
}

// ------------------------------------------------------------------ série oficial 9º ano (IBGE) + 2024
const ostate = { fam: 0, terr: "CAPITAIS", cut: 0 };
const OCUTS = [["Total", "Total", "Total (9º ano)"], ["Homem", "Total", "Homem"], ["Mulher", "Total", "Mulher"],
  ["Total", "Pública", "Escola pública"], ["Total", "Privada", "Escola privada"]];
function offPoints(O, fi, terr, cut) {
  const [sx, dp] = OCUTS[cut], P = O.pts;
  const t = O.territories.findIndex((x) => x.code === terr), s = O.sexes.indexOf(sx), d = O.deps.indexOf(dp);
  const out = [];
  for (let i = 0; i < P.f.length; i++) {
    if (P.f[i] === fi && P.t[i] === t && P.s[i] === s && P.d[i] === d) out.push({ year: P.y[i], e: P.e[i], lo: P.lo[i], hi: P.hi[i], o: P.o[i], src: P.src[i] });
  }
  return out.sort((a, b) => a.year - b.year);
}
function offChart(points) {
  const W = 640, H = 280, L = 52, R = 24, T = 26, Bm = 34, y0 = 2009, y1 = 2024;
  const vmax = Math.max(...points.map((p) => p.hi ?? p.e), 1);
  const step = niceStep(vmax, 4), top = Math.min(100, Math.ceil(vmax / step) * step);
  const x = (yr) => L + ((yr - y0) / (y1 - y0)) * (W - L - R), y = (v) => T + (1 - v / top) * (H - T - Bm);
  const root = svg("svg", { viewBox: `0 0 ${W} ${H}`, role: "img", "aria-label": "Série do 9º ano com margem de erro" });
  for (let k = 0; k * step <= top + 1e-9; k++) {
    const v = k * step;
    root.append(svg("line", { class: k ? "grid-line" : "baseline", x1: L, x2: W - R, y1: y(v), y2: y(v) }),
      svg("g", { class: "tick" }, svg("text", { x: L - 8, y: y(v) + 4, "text-anchor": "end", text: (Number.isInteger(v) ? nf0.format(v) : nf1.format(v)) + "%" })));
  }
  [2009, 2012, 2015, 2019, 2024].forEach((yr) => root.append(svg("text", { class: "yr", x: x(yr), y: H - 10, "text-anchor": "middle", text: String(yr) })));
  const pub = points.filter((p) => p.o === "P"), mic = points.filter((p) => p.o === "M");
  if (pub.length > 1) {
    root.append(svg("path", { class: "ci-band", fill: "var(--accent)", d: pub.map((p, j) => `${j ? "L" : "M"}${x(p.year)},${y(p.hi)}`).join("") + pub.slice().reverse().map((p) => `L${x(p.year)},${y(p.lo)}`).join("") + "Z" }));
    root.append(svg("path", { class: "series-line", stroke: "var(--accent)", d: pub.map((p, j) => `${j ? "L" : "M"}${x(p.year)},${y(p.e)}`).join("") }));
  }
  if (mic.length && pub.length) {
    const a = pub[pub.length - 1], b = mic[0];
    root.append(svg("path", { class: "seg-micro", d: `M${x(a.year)},${y(a.e)}L${x(b.year)},${y(b.e)}` }));
  }
  points.forEach((p) => {
    const g = svg("g", { class: "row", tabindex: "0", role: "button", "aria-label": `${p.year}: ${pct(p.e)} (${p.o === "P" ? "publicado pelo IBGE" : "calculado dos microdados"})` });
    g.append(svg("line", { class: "whisker", x1: x(p.year), x2: x(p.year), y1: y(p.lo), y2: y(p.hi) }));
    g.append(svg("circle", { cx: x(p.year), cy: y(p.e), r: 6, class: p.o === "M" ? "pt-micro" : "", fill: "var(--accent)", stroke: "var(--card)", "stroke-width": 2 }));
    const anchor = p.year === y0 ? "start" : p.year === y1 ? "end" : "middle";
    g.append(svg("text", { class: "pt-label", x: x(p.year) + (anchor === "start" ? 10 : anchor === "end" ? -10 : 0), y: y(p.hi) - 8, "text-anchor": anchor, text: pct(p.e) }));
    const row = { t: { name: "" }, e: p.e, lo: p.lo, hi: p.hi, cv: null, st: "VALID", src: p.src, cell: "" };
    const title = `${p.year} · ${p.o === "P" ? "publicado pelo IBGE" : "calculado dos microdados"}`;
    g.addEventListener("pointermove", (ev) => showTip(ev, row, { unit: "%" }, title));
    g.addEventListener("pointerleave", hideTip);
    g.addEventListener("focus", (ev) => showTip(ev, row, { unit: "%" }, title));
    g.addEventListener("blur", hideTip);
    root.append(g);
  });
  return root;
}
function renderOfficial() {
  const O = M && M.official;
  $("official-series").hidden = !O || !O.tables;
  if (!O || !O.tables) return;
  const rows = O.tables.map((t, fi) => ({ t, fi, pts: offPoints(O, fi, "CAPITAIS", 0) }));
  const years = [2009, 2012, 2015, 2019, 2024];
  table($("table-official"), [
    { label: "Indicador (9º ano, total das capitais)", cls: "ind", render: (r) => el("span", null, r.t.title, el("small", { text: `Tabela ${r.t.family} · ${r.t.extension_note}` })) },
    ...years.map((yr) => ({ label: String(yr), cls: "num", render: (r) => { const p = r.pts.find((q) => q.year === yr); return p ? pct(p.e) + (p.o === "M" ? " ◇" : "") : "—"; } })),
    { label: "Tendência", render: (r) => sparkline(r.pts.map((p) => ({ year: p.year, e: p.e, lo: p.lo, hi: p.hi }))) },
    { label: "Última variação", cls: "num", render: (r) => {
      const last = r.pts[r.pts.length - 1], dd = last && O.diffs[`${r.fi}|CAPITAIS|Total|Total|${last.year}`];
      if (!dd) return el("span", { class: "arrow ns", text: "—" });
      return el("span", { class: `arrow ${confirmed(dd[6]) ? "sig-up" : "ns"}`, text: `${dd[1] > 0 ? "▲" : "▼"} ${pp(dd[1])}`, title: `${dd[0]} → ${last.year} · ${CHANGE_LABEL[dd[6] || "NAO_SIGNIFICATIVA"][0]}` });
    } },
  ], rows, { onClick: (r) => { ostate.fam = r.fi; renderOfficialDetail(); }, isSel: (r) => r.fi === ostate.fam });
  renderOfficialDetail();
}
function renderOfficialDetail() {
  const O = M.official, t = O.tables[ostate.fam];
  fillSelect($("f-off-table"), O.tables.map((x, i) => ({ value: String(i), label: `${x.family} · ${x.title}` })), String(ostate.fam));
  const terrs = O.territories.slice().sort((a, b) => (a.code === "CAPITAIS" ? -1 : b.code === "CAPITAIS" ? 1 : a.name.localeCompare(b.name, "pt-BR")));
  fillSelect($("f-off-terr"), terrs.map((x) => ({ value: x.code, label: x.code === "CAPITAIS" ? "Total das capitais" : x.name })), ostate.terr);
  fillSelect($("f-off-cut"), OCUTS.map((c, i) => ({ value: String(i), label: c[2] })), String(ostate.cut));
  const pts = offPoints(O, ostate.fam, ostate.terr, ostate.cut);
  const box = clear($("chart-official"));
  box.append(pts.length ? offChart(pts) : el("p", { class: "empty", text: "Sem estimativa para esta combinação." }));
  const side = clear($("official-changes"));
  side.append(el("span", { class: "origin pub", text: "Publicado pelo IBGE" }));
  if (t.extension_2024) side.append(el("span", { class: "origin", text: "◇ 2024 calculado dos microdados" }));
  for (const p of pts.slice(1)) {
    const [sx, dp] = OCUTS[ostate.cut];
    const dd = O.diffs[`${ostate.fam}|${ostate.terr}|${sx}|${dp}|${p.year}`];
    if (!dd) continue;
    side.append(el("div", { class: "change" }, el("span", { class: "yrs", text: `${dd[0]} → ${p.year}` }),
      el("span", { class: "delta" }, pp(dd[1]), el("small", { text: ciDiffText(dd[2], dd[3], !!dd[4]) })),
      el("div", null, changeChip(dd[6]), " ", help("significativa")),
      el("span", { class: "detail", text: dd[5] === "aproximado pelo IC publicado" ? "calculado a partir das margens de erro publicadas (aproximação)" : "calculado com os microdados" })));
  }
  const lg = clear($("official-legend"));
  lg.append(el("span", { text: `Fonte: ${O.source}.` }), el("span", { text: t.extension_note + "." }),
    O.experimental_note ? el("span", { class: "experimental", text: O.experimental_note }) : null,
    el("span", null, "Linha azul e faixa clara: valores publicados e margem de erro ", help("margem")),
    el("span", null, "◇ e tracejado: 2024 calculado dos microdados ", help("microdados")));
}
function bindOfficial() {
  $("f-off-table").addEventListener("change", (e) => { ostate.fam = Number(e.target.value); renderOfficial(); });
  $("f-off-terr").addEventListener("change", (e) => { ostate.terr = e.target.value; renderOfficialDetail(); });
  $("f-off-cut").addEventListener("change", (e) => { ostate.cut = Number(e.target.value); renderOfficialDetail(); });
}

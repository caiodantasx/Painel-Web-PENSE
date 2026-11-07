/* Página “Territórios”: ranking em gráfico e tabela com a célula de origem de cada valor. */
"use strict";

function renderRanking() {
  const m = measure(), sc = SCOPES[state.scope];
  const rows = scopeRows().filter(approved).sort((a, b) => b.e - a.e);
  // contagens: o agregado é soma das partes, não um valor de referência comparável
  const refRow = sc.ref && isPct(m) && state.scope !== "regional" ? currentRows().find((r) => r.t.code === sc.ref && approved(r)) : null;
  const items = rows.map((r) => ({ key: r.t.code, label: r.t.type === "capital" ? r.t.name.replace(" (capital)", "") : r.t.name,
    row: r, cls: [r.t.code === state.selected ? "sel" : "", r.t.type === "country" ? "ref" : ""].join(" "),
    tipTitle: r.t.name }));
  const keys = new Set();
  if (rows.length) { keys.add(rows[0].t.code); keys.add(rows[rows.length - 1].t.code); }
  if (state.selected) keys.add(state.selected);
  rows.filter((r) => r.t.type === "country").forEach((r) => keys.add(r.t.code));
  if (rows.length <= 8) rows.forEach((r) => keys.add(r.t.code));
  $("rank-sub").textContent = `${sc.label} · ${state.age} · ${state.sex} · ${state.dep} · do maior para o menor valor`;
  hbar($("chart-ranking"), items, { m, ref: refRow, refLabel: refRow ? refRow.t.name.replace("Conjunto dos municípios das capitais", "Capitais") : "",
    labelKeys: keys, aria: `Comparação entre ${sc.label}`, onSelect: (it) => selectTerritory(it.key) });
  const lg = clear($("rank-legend"));
  lg.append(
    el("span", null, el("span", { class: "sw", style: "background: var(--accent)" }), "valor estimado"),
    el("span", null, el("span", { class: "sw", style: "background: var(--select)" }), "lugar selecionado"),
    el("span", null, el("span", { class: "sw", style: "background: var(--accent); opacity: .42" }), "‡ estimativa pouco precisa ", help("precisao")),
    el("span", null, "linha fina = margem de erro ", help("margem")),
    el("span", null, "como comparar dois lugares ", help("comparar")),
  );
}

function obsColumns(m) {
  return [
    { label: "Lugar", render: (r) => r.t.name },
    { label: "Valor", cls: "num", render: (r) => (r.e === null ? (r.sym ? `símbolo "${r.sym}"` : "—") : fmt(r.e, m)) },
    { label: "Margem de erro", cls: "num", render: (r) => fmtCI(r, m), help: "margem" },
    { label: "Precisão", render: (r) => { const p = precision(r.cv); return p ? chip("P", { P: [`${p[0]} · CV ${nf1.format(r.cv)}%`, p[1]] }) : "—"; }, help: "precisao" },
    { label: "Situação", render: (r) => chip(r.st), help: "situacao" },
    { label: "Observações", cls: "wrap", render: (r) => (r.rules || "").split("|").filter(Boolean).map((x) => RULE_TEXT[x] || x).join("; ") || "—" },
    { label: "Onde está na planilha do IBGE", cls: "mono", render: (r) => `${r.src.split("!").pop().replace("::", " › ")} › ${r.cell}`, help: "origem" },
  ];
}

function renderTerritoryTable() {
  const m = measure();
  const rows = scopeRows().sort((a, b) => (b.e ?? -1) - (a.e ?? -1));
  table($("table-territory"), obsColumns(m), rows, { onClick: (r) => selectTerritory(r.t.code), isSel: (r) => r.t.code === state.selected });
}

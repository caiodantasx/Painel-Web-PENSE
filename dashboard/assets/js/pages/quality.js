/* Página “Qualidade”: situação dos números e alertas das verificações automáticas. */
"use strict";

function renderQuality() {
  const m = measure(), all = rowsOf(state.measure);
  const t = clear($("tile-status"));
  const c = countBy(all, (r) => r.st);
  t.append(el("div", { class: "label" }, `Situação dos ${nf0.format(all.length)} números do indicador escolhido `, help("situacao")));
  const grid = el("div", { class: "rows" });
  for (const k of B.meta.status_order) if (c[k]) grid.append(chip(k), el("span"), el("span", { class: "num", text: nf0.format(c[k]) }));
  t.append(grid, el("div", { class: "detail", text: "Números em revisão ou com erro ficam fora dos gráficos e aparecem na tabela abaixo, com o motivo." }));
  const sevMap = { ERROR: ["Erro", "critical"], REVIEW: ["Revisão", "serious"], WARNING: ["Ressalva", "warning"], INFO: ["Informativo", "neutral"] };
  const order = { ERROR: 0, REVIEW: 1, WARNING: 2, INFO: 3 };
  table($("table-rules"), [
    { label: "O que foi encontrado", cls: "wrap", render: (r) => RULE_TEXT[r.rule_id] || r.rule_id },
    { label: "Nível", render: (r) => chip(r.severity, sevMap), help: "", helpText: "Veja a legenda “Níveis de alerta”, acima: Informativo, Ressalva, Revisão e Erro." },
    { label: "Interpretação", render: (r) => ISSUE_CLASS[r.issue_class] || r.issue_class.replace(/_/g, " ").toLowerCase() },
    { label: "Quantas vezes", cls: "num", render: (r) => nf0.format(r.count) },
    { label: "Código", cls: "mono", render: (r) => r.rule_id, help: "", helpText: "Código da regra na documentação técnica (docs/04 e relatório de qualidade)." },
  ], B.issues_summary.slice().sort((a, b) => order[a.severity] - order[b.severity] || b.count - a.count));
  const rev = all.filter((r) => r.st !== "VALID");
  $("review-sub").textContent = `${nf0.format(rev.length)} números · ${m.short_label}`;
  table($("table-review"), [
    { label: "Grupo", render: (r) => [r.a, r.s, r.d].filter((x) => x !== "Total").join(" · ") || "Todos os escolares", help: "recorte" }, ...obsColumns(m),
  ], rev.slice(0, 400), { empty: "Todas as observações deste indicador estão válidas sem ressalvas." });
}

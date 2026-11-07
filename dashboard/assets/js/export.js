/* Exportação da seleção atual em CSV (Excel em português) e cópia para a área de transferência. */
"use strict";

// ------------------------------------------------------------------ exportação
function exportRows() {
  const m = measure();
  const rows = scopeRows();
  const head = headlineRow(currentRows());
  if (head && !rows.includes(head)) rows.unshift(head);
  const num = (v) => (v === null || v === undefined ? "" : String(v).replace(".", ","));
  const esc = (v) => { const s = String(v ?? ""); return /[;"\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s; };
  // Cabeçalhos legíveis no Excel; a explicação de cada coluna está na página "Sobre os dados" (dicionário).
  const header = ["Ano da pesquisa", "Tabela IBGE", "Indicador", "Como ler (frase com o valor)", "Os 100% são", "Quem respondeu", "Tipo / categoria", "Unidade", "Lugar", "Tipo de lugar", "Faixa de idade",
    "Sexo", "Rede de ensino", "Valor estimado", "Margem de erro - mínimo", "Margem de erro - máximo",
    "Precisão (boa < 15% de CV; razoável 15–30%; baixa ≥ 30%)", "Coeficiente de variação (%)", "Símbolo publicado",
    "Situação do número", "Observações", "Arquivo e aba de origem", "Célula de origem", "Identificador"];
  const lines = [header.join(";")];
  for (const r of rows) lines.push([m.year, m.tables, m.short_label, readingOf(m, r, false), m.reading_base || "",
    (m.informant || "").startsWith("Escola (") ? "diretor(a) ou responsável pela escola" : "o próprio aluno", m.category || "geral", m.unit === "%" ? "percentual" : "escolares",
    r.t.name, r.t.type, r.a, r.s, r.d, num(r.e), num(r.lo), num(r.hi), (precision(r.cv) || [""])[0], num(r.cv), r.sym,
    (STATUS_LABEL[r.st] || [r.st])[0], (r.rules || "").split("|").filter(Boolean).map((x) => RULE_TEXT[x] || x).join("; "),
    r.src, r.cell, r.id].map(esc).join(";"));
  return "﻿" + lines.join("\n");
}
function doExport() {
  const blob = new Blob([exportRows()], { type: "text/csv;charset=utf-8" });
  const a = el("a", { href: URL.createObjectURL(blob), download: `pense_${measure().id}_${state.scope}.csv` });
  document.body.append(a);
  a.click();
  setTimeout(() => { URL.revokeObjectURL(a.href); a.remove(); }, 1000);
}
async function doCopy() {
  const text = exportRows();
  const n = $("copy-status");   // o aviso aparece junto do botão (avaliação heurística, problema 6)
  n.classList.remove("fail");
  try { await navigator.clipboard.writeText(text); n.textContent = "Copiado."; }
  catch (e) {
    const ta = $("copy-buffer"); ta.value = text; ta.select();
    n.textContent = "Não copiou sozinho: use Ctrl+C.";
    n.classList.add("fail");
  }
  clearTimeout(doCopy.t);
  doCopy.t = setTimeout(() => { n.textContent = ""; }, 6000);
}

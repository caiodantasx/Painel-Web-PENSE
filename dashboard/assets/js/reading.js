/* “X% de quê?”: frases e ficha “Como ler este número”, geradas a partir dos textos da pipeline. */
"use strict";

// "X% de quê?": frase gerada pela pipeline (src/pense/exports/reading.py) com o valor no lugar de {v}.
function cutText() {
  const parts = [state.age, state.sex, state.dep].filter((x) => x !== "Total");
  return parts.length ? ` (recorte: ${parts.join(", ").toLowerCase()})` : "";
}
function readingOf(m, r, withPlace = true) {
  if (!m.reading || !r || r.e === null || r.e === undefined) return "";
  const txt = m.reading.replace("{v}", fmt(r.e, m));
  return (withPlace ? `${shortName(r.t)}, PeNSE ${m.year}: ` : "") + txt + cutText() + ".";
}
function readingBlock(m, r, cls = "reading") {
  const box = el("div", { class: cls });
  const t = readingOf(m, r);
  if (t) box.append(el("p", { class: "reading-main" }, el("b", { text: "Em uma frase: " }), t));
  if (r && r.e !== null && r.e !== undefined) box.append(numberCard(m, r));
  return box;
}
// "X em cada 100": a mesma estimativa em linguagem de contagem (arredondada; o valor exato fica ao lado).
function per100(v) {
  if (v === null || v === undefined) return "";
  if (v < 1) return "menos de 1 em cada 100";
  if (v < 10) return `cerca de 1 em cada ${Math.round(100 / v)}`;
  return `cerca de ${Math.round(v)} em cada 100`;
}
const cap = (t) => (t ? t[0].toUpperCase() + t.slice(1) : t);
// Ficha "Como ler este número": textos gerados pela pipeline (m.explain, src/pense/exports/reading.py)
// a partir do título, da categoria e do informante publicados pelo IBGE — nada fixo por indicador.
function numberCard(m, r) {
  const x = m.explain || {};
  const place = r && r.t ? ` — ${shortName(r.t)}` : "";
  const rows = [];
  if (isPct(m) && x.count_base) rows.push(["Quanto é", `${fmt(r.e, m)} = ${per100(r.e)} ${x.count_base}${place}${cutText()}`]);
  else if (!isPct(m)) rows.push(["Quanto é", `${fmt(r.e, m)} escolares (número estimado a partir da amostra)${place}`]);
  if (x.count_base) rows.push(["Os 100% são", `todos os ${x.count_base}${place}${cutText()}`]);
  if (x.situation) rows.push(["Entram no número os que", cap(x.situation)]);
  if (x.who) rows.push(["Quem respondeu", cap(x.who)]);
  if (x.period) rows.push(["Período", cap(x.period)]);
  if (x.not_this) rows.push(["Não confundir com", x.not_this, "warn"]);
  const dl = el("dl", { class: "nc-list" });
  for (const [k, v, cls] of rows) dl.append(el("div", { class: `nc-row${cls ? " " + cls : ""}` }, el("dt", { text: k }), el("dd", { text: v })));
  return el("section", { class: "number-card", "aria-label": "Como ler este número" }, el("h3", { text: "Como ler este número" }), dl);
}
// Rótulo curto da unidade para listas e tabelas: "% dos escolares de 13 a 17 anos".
const unitShort = (m) => (isPct(m) ? `% dos ${(m.explain && m.explain.count_base) || "alunos"}` : "número estimado de escolares");

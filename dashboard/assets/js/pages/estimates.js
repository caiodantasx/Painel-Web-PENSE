/* Aba "Estimativas": quantos estudantes (cerca de N) sofreram ou praticaram bullying, foram agredidos,
 * brigaram ou faltaram por insegurança, no lugar e no grupo escolhidos. Usa as mesmas escolhas da página
 * inicial (hstate) e os mesmos acessos ao pacote (hRow, hPeople em home.js): nenhum número fica aqui. */
"use strict";

function renderEstimatesChoices() {
  const sel = $("e-place");
  if (!sel.options.length) {
    for (const og of $("h-place").querySelectorAll("optgroup")) sel.append(og.cloneNode(true));
    sel.addEventListener("change", () => { hstate.place = sel.value; homeSave(); renderEstimates(); });
  }
  sel.value = hstate.place;
  const box = clear($("e-group"));
  for (const g of Object.keys(G.groups)) {
    box.append(el("button", { type: "button", class: "seg", role: "radio", "aria-checked": String(g === hstate.group),
      onclick: () => { hstate.group = g; homeSave(); renderEstimates(); } }, g));
  }
}

function estimateRows(keys) {
  return keys.map((k) => ({ k, it: G.items[k], r: hRow(k), br: hRow(k, "BR") })).filter((x) => x.r)
    .map((x) => ({ ...x, ppl: hPeople(x.k, x.r) }));
}

function renderEstimates() {
  if (!G) return;
  if (!$("h-place").options.length) renderHomeChoices();
  renderEstimatesChoices();
  const t = hTerr(hstate.place);
  $("e-title").textContent = `${placeName(t)} · ${hstate.group === "Todos" ? "todos os alunos de 13 a 17 anos" : hstate.group.toLowerCase() + " de 13 a 17 anos"}`;
  const body = clear($("e-body"));
  const all = [];
  for (const sec of G.estimates) {
    const rows = estimateRows(sec.items);
    if (!rows.length) continue;
    all.push(...rows.map((x) => ({ ...x, sec: sec.title })));
    const list = el("ul", { class: "e-list" });
    for (const { k, it, r, br, ppl } of rows) {
      const cmp = vsBrazil(r, br);
      list.append(el("li", { class: "e-row" },
        el("div", { class: "e-what" }, el("b", { text: it.short }), el("span", { text: `${it.phrase[0].toUpperCase()}${it.phrase.slice(1)}.` })),
        el("div", { class: "e-num" },
          ppl ? el("p", { class: "e-people" }, el("b", { text: people(ppl.n) }), el("span", { text: ` estudantes` })) : null,
          ppl ? el("p", { class: "e-range", text: `entre ${people(ppl.lo)} e ${people(ppl.hi)}` }) : null),
        el("div", { class: "e-pct" }, el("p", null, el("b", { text: in100(r.e) }), " em cada 100"), el("p", { class: "e-range", text: between(r) }),
          cmp ? el("span", { class: `h-tag ${cmp[1]}`, text: cmp[0] }) : null),
        hFoot(k, r)));
    }
    body.append(el("article", { class: "panel e-sec" }, el("header", { class: "panel-head" }, el("div", null, el("h2", { text: sec.title }))), list));
  }
  const any = G.blocks.any_violence ? hMicro(G.blocks.any_violence, hstate.place, 2024)[0] : null;
  if (any && any.w) {
    body.prepend(el("article", { class: "panel e-sec e-any" },
      el("p", { class: "e-lead" }, el("b", { text: `Cerca de ${people((any.e / 100) * any.w)} estudantes` }),
        ` (${in100(any.e)} em cada 100, entre ${people((any.lo / 100) * any.w)} e ${people((any.hi / 100) * any.w)}) sofreram pelo menos um tipo de violência: bullying, cyberbullying ou agressão física.`),
      el("p", { class: "h-note", text: "Total calculado pelo projeto com os microdados da PeNSE 2024 (IBGE): quem sofreu mais de um tipo conta uma vez só." })));
  }
  for (const [side, title, who] of [["sofreu", "Por que foram humilhados (motivo dito por quem sofreu)", "quem foi humilhado por colegas"],
    ["praticou", "Por que humilharam colegas (motivo dito por quem praticou)", "quem humilhou colegas"]]) {
    const mv = (G.motives || {})[side];
    if (!mv) continue;
    const ms = mv.measures;
    const [s, d] = groupDims();
    const rows = ms.map((mi) => ({ m: B.measures[mi], r: rowsOf(mi).find((x) => x.t.code === hstate.place && isAgeTotal(x.a) && x.s === s && x.d === d) }))
      .filter((x) => x.r && approved(x.r)).sort((a, b) => b.r.e - a.r.e);
    if (!rows.length) continue;
    const max = niceMax(Math.max(...rows.map((x) => x.r.hi ?? x.r.e)));
    const ul = el("ul", { class: "h-bars" });
    // base: quem sofreu (ou praticou); a contagem é aproximada (produto de duas estimativas, sem faixa)
    const baseRow = mv.base ? hRow(mv.base) : null;
    const basePpl = baseRow ? hPeople(mv.base, baseRow) : null;
    for (const { m, r } of rows) {
      ul.append(el("li", null,
        el("div", { class: "h-bar-head" }, el("span", { class: "h-bar-label", text: m.category }),
          el("span", { class: "h-bar-val" }, el("b", { text: in100(r.e) }), " em cada 100")),
        el("div", { class: "h-track" }, el("span", { class: "h-fill", style: `width:${(r.e / max * 100).toFixed(2)}%` }),
          r.lo !== null ? el("span", { class: "h-ci", style: `left:${(r.lo / max * 100).toFixed(2)}%;width:${((r.hi - r.lo) / max * 100).toFixed(2)}%` }) : null),
        el("div", { class: "h-bar-sub", text: `${between(r)}${basePpl ? ` · aproximadamente ${people((r.e / 100) * basePpl.n)}` : ""}` })));
    }
    body.append(el("article", { class: "panel e-sec" }, el("header", { class: "panel-head" }, el("div", null, el("h2", { text: title }),
      el("p", { class: "card-sub", text: `“X em cada 100” aqui é entre ${who}${basePpl ? ` (cerca de ${people(basePpl.n)} estudantes)` : ""}, não entre todos os alunos. Um aluno pode citar mais de um motivo, por isso a soma passa de 100. Fonte: IBGE, PeNSE 2024, tabela ${side === "sofreu" ? "2.6" : "2.13"}.` }))), ul));
  }
  $("e-download").onclick = () => {
    const esc = (v) => { const x = String(v ?? ""); return /[;"\n]/.test(x) ? `"${x.replace(/"/g, '""')}"` : x; };
    const n = (v) => (v === null || v === undefined ? "" : String(Math.round(v)));
    const p = (v) => (v === null || v === undefined ? "" : String(v).replace(".", ","));
    const lines = [["Lugar", "Alunos", "Grupo", "Situação", "Estudantes (estimativa)", "Mínimo", "Máximo", "Em cada 100 (%)", "Mínimo (%)", "Máximo (%)", "Tabela IBGE"].join(";")];
    for (const x of all) lines.push([placeName(t), hstate.group, x.sec, x.it.short, n(x.ppl && x.ppl.n), n(x.ppl && x.ppl.lo), n(x.ppl && x.ppl.hi), p(x.r.e), p(x.r.lo), p(x.r.hi), x.it.table].map(esc).join(";"));
    const blob = new Blob(["﻿" + lines.join("\n")], { type: "text/csv;charset=utf-8" });
    const a = el("a", { href: URL.createObjectURL(blob), download: `pense_estimativas_${hstate.place}.csv` });
    document.body.append(a); a.click(); setTimeout(() => { URL.revokeObjectURL(a.href); a.remove(); }, 1000);
  };
}

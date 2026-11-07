/* Página "Início": responde, em linguagem simples, às perguntas dos gestores escolares.
 * Três escolhas (onde, sobre o quê, quais alunos) e seis blocos. Nenhum número fica escrito aqui:
 * as frases leem o pacote gerado pela pipeline (B.gestor liga cada frase a uma medida publicada
 * pelo IBGE e, quando existe, ao indicador recalculado pelos microdados, B.micro). */
"use strict";

let G = null;
const hstate = { place: "BR", topic: "bullying", group: "Todos" };
const H_TYPES = { country: "Brasil", region: "Regiões", uf: "Estados", capital: "Capitais" };

function homePrepare() {
  G = B.gestor || null;
  if (!G) return;
  const saved = recall("pense-home");
  if (saved) {
    if (idx.terr.some((t) => t.code === saved.place)) hstate.place = saved.place;
    if (G.topics.some((t) => t.id === saved.topic)) hstate.topic = saved.topic;
    if (G.groups[saved.group]) hstate.group = saved.group;
  }
}
const homeSave = () => store("pense-home", hstate);

// ------------------------------------------------------------------ acesso aos números
const hTerr = (code) => idx.terr.find((t) => t.code === code);
function placeName(t) {
  if (!t) return "";
  if (t.type === "region") return `Região ${t.name}`;
  if (t.type === "capital") return `${t.name.replace(" (capital)", "")} (capital, ${t.uf})`;
  return t.name;
}
const groupDims = () => G.groups[hstate.group] || ["Total", "Total"];
const isAgeTotal = (a) => a === "Total" || a === "13 a 17 anos";
// Número publicado (tabela do IBGE) de um item da tela, no lugar e no grupo escolhidos.
function hRow(itemKey, place, group) {
  const it = G.items[itemKey];
  if (!it) return null;
  const [s, d] = G.groups[group || hstate.group] || ["Total", "Total"];
  const r = rowsOf(it.m).find((x) => x.t.code === (place || hstate.place) && isAgeTotal(x.a) && x.s === s && x.d === d);
  if (!r || !approved(r)) return null;
  // "pelo menos uma vez" = 100% menos "nenhuma vez" (mesma tabela; a margem de erro inverte os limites)
  return it.complement ? { ...r, e: 100 - r.e, lo: r.hi === null ? null : 100 - r.hi, hi: r.lo === null ? null : 100 - r.lo } : r;
}
// Ponto calculado pelos microdados (série e número estimado de estudantes).
function hMicro(key, place, year) {
  if (!M || !key || !M.kIndex.has(key) || !M.tIndex.has(place)) return [];
  const [s, d] = groupDims();
  const k = M.kIndex.get(key), t = M.tIndex.get(place);
  const ia = M.dims.age_group.indexOf("Total"), is = M.dims.sex.indexOf(s), id = M.dims.admin_dependency.indexOf(d);
  const E = M.est;
  const pts = (M.idx.get(`${k}|${t}|${ia}|${is}|${id}`) || []).map((i) => ({
    year: M.editions[E.ed[i]].year, ed: M.editions[E.ed[i]].id, e: E.e[i], lo: E.lo[i], hi: E.hi[i], w: E.w ? E.w[i] : null,
  })).sort((a, b) => a.year - b.year);
  return year ? pts.filter((p) => p.year === year) : pts;
}
// Cerca de quantos estudantes: percentual publicado × total estimado de escolares (soma dos pesos).
function hPeople(itemKey, r) {
  const it = G.items[itemKey];
  const key = it && (it.micro || G.population_micro);
  if (!r || !key) return null;
  const p = hMicro(key, r.t.code, 2024)[0];
  if (!p || !p.w) return null;
  return { n: (r.e / 100) * p.w, lo: (r.lo / 100) * p.w, hi: (r.hi / 100) * p.w };
}
function people(v) {
  if (v >= 1e6) return `${nf1.format(v / 1e6)} ${v >= 2e6 ? "milhões" : "milhão"}`;
  if (v >= 1e4) return `${nf0.format(Math.round(v / 1e3))} mil`;
  if (v >= 1e3) return `${nf1.format(v / 1e3)} mil`;
  return nf0.format(Math.round(v / 10) * 10);
}
const in100 = (v) => nf0.format(Math.round(v));
const pct0 = (v) => `${nf0.format(Math.round(v))}%`;
const pct1 = (v) => `${nf1.format(v)}%`;
const between = (r) => (r.lo === null || r.hi === null ? "" : `entre ${pct1(r.lo)} e ${pct1(r.hi)}`);
// Comparação já interpretada: margens de erro (IC 95%) que se sobrepõem = "parecido".
function vsBrazil(r, br) {
  if (!r || !br || r.t.code === "BR") return null;
  if (r.lo > br.hi) return ["maior que no Brasil", "up"];
  if (r.hi < br.lo) return ["menor que no Brasil", "down"];
  return ["parecido com o Brasil", "same"];
}
const whoText = () => ({ "Todos": "estudantes", "Meninas": "meninas", "Meninos": "meninos",
  "Escola pública": "estudantes de escola pública", "Escola privada": "estudantes de escola privada" }[hstate.group] || "estudantes");

// ------------------------------------------------------------------ rodapé de cada número
function hDownload(itemKey) {
  const it = G.items[itemKey], m = B.measures[it.m];
  const esc = (v) => { const s = String(v ?? ""); return /[;"\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s; };
  const num = (v) => (v === null || v === undefined ? "" : String(v).replace(".", ","));
  const lines = [["Indicador", "Lugar", "Tipo de lugar", "Sexo", "Rede de ensino", "Valor (%)", "Mínimo (%)", "Máximo (%)",
    "Tabela IBGE", "Ano"].join(";")];
  for (const r of rowsOf(it.m).filter((x) => isAgeTotal(x.a) && approved(x))) {
    const v = it.complement ? { e: 100 - r.e, lo: 100 - r.hi, hi: 100 - r.lo } : r;   // "pelo menos uma vez"
    lines.push([it.short, r.t.name, H_TYPES[r.t.type] || r.t.type, r.s, r.d, num(v.e), num(v.lo), num(v.hi), it.table, m.year].map(esc).join(";"));
  }
  const blob = new Blob(["﻿" + lines.join("\n")], { type: "text/csv;charset=utf-8" });
  const a = el("a", { href: URL.createObjectURL(blob), download: `pense_${itemKey}.csv` });
  document.body.append(a);
  a.click();
  setTimeout(() => { URL.revokeObjectURL(a.href); a.remove(); }, 1000);
}
function hHowTo(itemKey, r) {
  const it = G.items[itemKey], m = B.measures[it.m];
  const d = el("details", { class: "h-how" }, el("summary", { text: "Como ler" }));
  const ul = el("ul");
  ul.append(el("li", { text: it.school
    ? "A pergunta foi feita ao diretor da escola. O número é a parte dos alunos que estudam em escolas com essa resposta — não é número de casos."
    : "A pergunta foi respondida pelo próprio estudante, num questionário sigiloso. O número é a parte dos alunos de 13 a 17 anos que responderam assim." }));
  if (r && r.lo !== null) ul.append(el("li", { text: `A pesquisa ouve uma amostra de alunos, por isso o valor real está ${between(r)} (margem de erro).` }));
  ul.append(el("li", { text: "“Cerca de N estudantes” é uma estimativa: a parte dos alunos multiplicada pelo total estimado de escolares do lugar." }));
  ul.append(el("li", { text: `Fonte: IBGE, PeNSE ${m.year}, tabela ${it.table}.` }));
  d.append(ul);
  return d;
}
function hFoot(itemKey, r) {
  return el("div", { class: "h-foot" },
    el("a", { class: "h-act", href: G.ibge_url, target: "_blank", rel: "noopener" }, "Ver no IBGE ↗"),
    el("button", { type: "button", class: "h-act", onclick: () => hDownload(itemKey) }, "Baixar dados"),
    hHowTo(itemKey, r));
}

// ------------------------------------------------------------------ as três escolhas
function renderHomeChoices() {
  const sel = $("h-place");
  if (!sel.options.length) {
    for (const type of ["country", "region", "uf", "capital"]) {
      const list = idx.terr.filter((t) => t.type === type).sort((a, b) => a.name.localeCompare(b.name, "pt-BR"));
      if (!list.length) continue;
      const og = el("optgroup", { label: H_TYPES[type] });
      for (const t of list) og.append(el("option", { value: t.code, text: placeName(t) }));
      sel.append(og);
    }
    sel.addEventListener("change", () => homeSet({ place: sel.value }));
  }
  sel.value = hstate.place;
  const seg = (box, opts, cur, key) => {
    clear(box);
    for (const [val, label] of opts) {
      box.append(el("button", { type: "button", class: "seg", role: "radio", "aria-checked": String(val === cur),
        onclick: () => homeSet({ [key]: val }) }, label));
    }
  };
  seg($("h-topic"), G.topics.map((t) => [t.id, t.label]), hstate.topic, "topic");
  seg($("h-group"), Object.keys(G.groups).map((g) => [g, g]), hstate.group, "group");
}
function homeSet(patch) {
  Object.assign(hstate, patch);
  homeSave();
  animateNext();
  renderHome();
}

// ------------------------------------------------------------------ bloco 1: resposta principal
function renderHomeAnswer() {
  const box = clear($("h-answer"));
  const topic = G.topics.find((t) => t.id === hstate.topic);
  const key = topic.main, it = G.items[key];
  const r = hRow(key), br = hRow(key, "BR");
  const t = hTerr(hstate.place);
  box.append(el("p", { class: "h-eyebrow", text: `${placeName(t)} · ${hstate.group === "Todos" ? "todos os alunos" : hstate.group.toLowerCase()} · PeNSE ${B.measures[it.m].year}` }));
  if (!r) {
    box.append(el("p", { class: "h-big-msg", text: "Não há número confiável publicado para esta combinação. Tente “Todos” ou outro lugar." }));
    return;
  }
  const cmp = vsBrazil(r, br);
  box.append(
    el("p", { class: "h-big" }, el("b", { text: in100(r.e) }), el("span", { text: " em cada 100" })),
    el("p", { class: "h-sentence", text: `${in100(r.e)} em cada 100 ${whoText()} de 13 a 17 anos ${it.phrase}.` }),
    el("p", { class: "h-range", text: `O valor real está ${between(r)} (margem de erro da pesquisa).` }),
  );
  if (cmp) {
    box.append(el("p", { class: `h-cmp ${cmp[1]}` }, el("b", { text: cmp[0][0].toUpperCase() + cmp[0].slice(1) }),
      ` (Brasil: ${in100(br.e)} em cada 100). `, cmp[1] === "same" ? "A diferença cabe na margem de erro." : "A diferença é maior que a margem de erro."));
  }
  const ppl = hPeople(key, r);
  if (ppl) box.append(el("p", { class: "h-people" }, "Isso corresponde a ", el("b", { text: `cerca de ${people(ppl.n)} ${whoText()}` }),
    ` (entre ${people(ppl.lo)} e ${people(ppl.hi)}).`));
  box.append(hFoot(key, r));
}

// ------------------------------------------------------------------ bloco 2: tipos de violência
function renderHomeTypes() {
  const box = clear($("h-types-body"));
  const list = G.blocks.topic_lists[hstate.topic] || G.blocks.types;
  $("h-types-title").textContent = hstate.topic === "entorno" ? "O que os diretores relatam perto da escola, do mais ao menos comum"
    : hstate.topic === "faltas" ? "Faltas por falta de segurança" : "Tipos de violência, do mais ao menos comum";
  const rows = list.map((k) => ({ k, r: hRow(k), br: hRow(k, "BR") })).filter((x) => x.r).sort((a, b) => b.r.e - a.r.e);
  if (!rows.length) { box.append(el("p", { class: "empty", text: "Sem números publicados para esta combinação." })); return; }
  const max = Math.max(...rows.map((x) => Math.max(x.r.hi || x.r.e, x.br ? x.br.e : 0)));
  const scale = (v) => `${Math.min(100, (v / niceMax(max)) * 100).toFixed(2)}%`;
  const ul = el("ul", { class: "h-bars" });
  for (const { k, r, br } of rows) {
    const it = G.items[k];
    const ppl = hPeople(k, r);
    const bar = el("div", { class: "h-track", role: "img", "aria-label": `${it.short}: ${in100(r.e)} em cada 100${br && hstate.place !== "BR" ? `; Brasil ${in100(br.e)} em cada 100` : ""}` },
      el("span", { class: "h-fill", style: `width:${scale(r.e)}` }),
      r.lo !== null ? el("span", { class: "h-ci", style: `left:${scale(r.lo)};width:calc(${scale(r.hi)} - ${scale(r.lo)})` }) : null,
      br && hstate.place !== "BR" ? el("span", { class: "h-ref", style: `left:${scale(br.e)}`, title: `Brasil: ${in100(br.e)} em cada 100` }) : null);
    const cmp = vsBrazil(r, br);
    ul.append(el("li", null,
      el("div", { class: "h-bar-head" }, el("span", { class: "h-bar-label", text: it.short }),
        el("span", { class: "h-bar-val" }, el("b", { text: in100(r.e) }), " em cada 100")),
      bar,
      el("div", { class: "h-bar-sub" }, between(r), ppl ? ` · cerca de ${people(ppl.n)}` : "",
        cmp ? el("span", { class: `h-tag ${cmp[1]}`, text: cmp[0] }) : null)));
  }
  box.append(ul);
  box.append(el("p", { class: "legend h-legend" }, el("span", { class: "h-key fill" }), "valor no lugar ",
    el("span", { class: "h-key ci" }), "margem de erro ", hstate.place !== "BR" ? el("span", { class: "h-key ref" }) : null, hstate.place !== "BR" ? "Brasil" : ""));
}
// "Quantos foram vítimas de algum tipo de violência?" (microdados, indicador composto do projeto).
function renderHomeAny() {
  const key = G.blocks.any_violence;
  const p = key ? hMicro(key, hstate.place, 2024)[0] : null;
  if (!p || p.e === null) return null;
  return el("article", { class: "h-card any" },
    el("h3", { text: "Sofreram algum tipo de violência" }),
    el("p", { class: "h-card-big" }, el("b", { text: in100(p.e) }), " em cada 100"),
    p.w ? el("p", { class: "h-card-people" }, el("b", { text: `cerca de ${people((p.e / 100) * p.w)}` }), ` (entre ${people((p.lo / 100) * p.w)} e ${people((p.hi / 100) * p.w)})`) : null,
    el("p", { class: "h-card-text", text: "Bullying, cyberbullying ou agressão física (quem sofreu mais de um conta uma vez)." }),
    el("p", { class: "h-bar-sub", text: between(p) }),
    el("details", { class: "h-how" }, el("summary", { text: "Como ler" }), el("ul", null,
      el("li", { text: "A pesquisa não publica este total: o projeto calculou com os microdados da PeNSE 2024 (IBGE), com os pesos amostrais oficiais." }),
      el("li", { text: "Conta quem foi humilhado por colegas 2 ou mais vezes ou pela internet no último mês, ou agredido fisicamente no último ano." }),
      el("li", { text: `A pesquisa ouve uma amostra: o valor real está ${between(p)}.` }))));
}

// ------------------------------------------------------------------ bloco 3: bullying em foco
function renderHomeBullying() {
  const box = clear($("h-bully-body"));
  const ks = G.blocks.bullying;
  const card = (k, extraKey) => {
    const it = G.items[k], r = hRow(k), br = hRow(k, "BR");
    if (!r) return el("article", { class: "h-card" }, el("h3", { text: it.short }), el("p", { class: "empty", text: "Sem número confiável." }));
    const cmp = vsBrazil(r, br), ppl = hPeople(k, r);
    const c = el("article", { class: "h-card" },
      el("h3", { text: it.short }),
      el("p", { class: "h-card-big" }, el("b", { text: in100(r.e) }), " em cada 100"),
      el("p", { class: "h-card-text", text: `${it.phrase[0].toUpperCase()}${it.phrase.slice(1)}.` }),
      el("p", { class: "h-bar-sub" }, between(r), ppl ? ` · cerca de ${people(ppl.n)}` : "", cmp ? el("span", { class: `h-tag ${cmp[1]}`, text: cmp[0] }) : null));
    if (extraKey) {
      const x = hRow(extraKey);
      if (x) c.append(el("p", { class: "h-card-extra" }, "Praticaram: ", el("b", { text: `${in100(x.e)} em cada 100` }), ` (${between(x)})`));
    }
    c.append(hFoot(k, r));
    return c;
  };
  const any = renderHomeAny();
  if (any) box.append(any);
  box.append(card(ks[0]), card(ks[1]), card(ks[2], ks[3]));
}

// ------------------------------------------------------------------ bloco 4: bullying e faltas
function renderHomeAbsence() {
  const panel = $("h-absence"), box = clear($("h-absence-body"));
  const ab = G.blocks.absence;
  if (!ab || !M) { panel.hidden = true; return; }
  const w = hMicro(ab.with, hstate.place, 2024)[0], wo = hMicro(ab.without, hstate.place, 2024)[0];
  panel.hidden = false;
  if (!w || !wo) { box.append(el("p", { class: "empty", text: "Sem dados suficientes para este lugar e grupo." })); return; }
  const max = niceMax(Math.max(w.hi, wo.hi));
  const bar = (label, p, cls) => el("li", null,
    el("div", { class: "h-bar-head" }, el("span", { class: "h-bar-label", text: label }), el("span", { class: "h-bar-val" }, el("b", { text: in100(p.e) }), " em cada 100")),
    el("div", { class: "h-track" }, el("span", { class: `h-fill ${cls}`, style: `width:${(p.e / max * 100).toFixed(2)}%` }),
      el("span", { class: "h-ci", style: `left:${(p.lo / max * 100).toFixed(2)}%;width:${((p.hi - p.lo) / max * 100).toFixed(2)}%` })),
    el("div", { class: "h-bar-sub", text: between(p) }));
  const differ = w.lo > wo.hi || w.hi < wo.lo;
  box.append(
    el("p", { class: "h-sentence" }, `Entre quem sofreu bullying (duas ou mais vezes no mês), `, el("b", { text: `${in100(w.e)} em cada 100` }),
      ` faltaram à escola por não se sentirem seguros lá. Entre quem não sofreu, `, el("b", { text: `${in100(wo.e)} em cada 100` }), "."),
    el("ul", { class: "h-bars" }, bar("Sofreram bullying", w, "sel"), bar("Não sofreram bullying", wo, "")),
    el("p", { class: "h-warn" }, el("b", { text: "Atenção: " }),
      differ ? "a diferença entre os dois grupos é maior que a margem de erro, mas isso mostra que as duas coisas andam juntas, não que o bullying causou as faltas. "
             : "a diferença cabe na margem de erro. Mesmo quando há diferença, ela mostra que as duas coisas andam juntas, não que uma causou a outra. ",
      "A pesquisa não pergunta o motivo da falta; pergunta só se o aluno faltou por não se sentir seguro na escola."),
    el("p", { class: "h-note", text: "Calculado pelo projeto com os microdados da PeNSE 2024 (IBGE); não há tabela publicada com este cruzamento." }));
}

// ------------------------------------------------------------------ bloco 5: mudou com o tempo?
function renderHomeTrend() {
  const box = clear($("h-trend-body"));
  const topic = G.topics.find((t) => t.id === hstate.topic), it = G.items[topic.main];
  // no tema Bullying, as três séries pedidas pelos gestores aparecem juntas
  const keys = hstate.topic === "bullying" ? ["bullying_sofreu", "bullying_praticou", "cyber_sofreu"].filter((k) => G.items[k]) : [topic.main];
  $("h-trend-title").textContent = keys.length > 1 ? "Mudou com o tempo?" : `Mudou com o tempo? ${it.short}`;
  for (const k of keys) {
    const sub = el("div", { class: "h-trend-item" });
    if (keys.length > 1) sub.append(el("h3", { class: "h-trend-h", text: G.items[k].short }));
    renderTrendItem(G.items[k], sub);
    box.append(sub);
  }
}
function renderTrendItem(it, box) {
  const key = it.micro;
  const info = M && key && M.kIndex.has(key) ? M.indicators[M.kIndex.get(key)] : null;
  const pts = info ? hMicro(key, hstate.place).filter((p) => p.e !== null) : [];
  if (pts.length < 2) {
    box.append(el("p", { class: "h-verdict none" }, el("b", { text: "Não dá para dizer." }),
      pts.length ? ` Para ${placeName(hTerr(hstate.place))}, este número só existe em ${pts[0].year}.` : " Não há série para este número.",
      hstate.place !== "BR" && info && info.editions.includes("PENSE_2015_A2") ? " Em 2015 a pesquisa só tinha números para o Brasil e as regiões." : ""));
    return;
  }
  const comp = info.comparability;
  const ok = ["COMPARABLE", "COMPARABLE_WITH_CAVEATS"].includes(comp.final_status);
  const inSeries = new Set((comp.series_editions || "").split("|").filter(Boolean));
  const shown = ok ? pts.filter((p) => inSeries.has(p.ed)) : pts;
  let verdict;
  if (!ok) {
    const why = comp.final_status === "NOT_COMPARABLE" ? "a pergunta mudou entre os anos, então os números não se comparam"
      : "a comparação entre os anos ainda não foi conferida e registrada pelo pesquisador";
    verdict = el("p", { class: "h-verdict none" }, el("b", { text: "Ainda não dá para comparar." }), ` Os anos aparecem separados porque ${why}.`);
  } else {
    const last = shown[shown.length - 1], prev = shown[shown.length - 2];
    const [s, d] = groupDims();
    const diff = M.diffs[`${key}|${hstate.place}|Total|${s}|${d}|${last.year}`];
    if (!prev || !diff) verdict = el("p", { class: "h-verdict none" }, el("b", { text: "Não dá para dizer." }), " Falta um ano comparável para este lugar.");
    else if (diff[4]) {
      const up = diff[1] > 0;
      verdict = el("p", { class: `h-verdict ${up ? "up" : "down"}` }, el("b", { text: up ? "Aumentou." : "Diminuiu." }),
        ` De ${in100(prev.e)} em cada 100 (${prev.year}) para ${in100(last.e)} em cada 100 (${last.year}). A mudança é maior que a margem de erro.`);
    } else {
      verdict = el("p", { class: "h-verdict same" }, el("b", { text: "Não dá para dizer se mudou." }),
        ` Foi de ${in100(prev.e)} em cada 100 (${prev.year}) para ${in100(last.e)} em cada 100 (${last.year}), mas a diferença cabe na margem de erro.`);
    }
  }
  box.append(verdict);
  if (ok && shown.length >= 3) {   // trecho anterior da série (ex.: 2015 → 2019)
    const a = shown[shown.length - 3], b = shown[shown.length - 2];
    const [s2, d2] = groupDims();
    const df = M.diffs[`${key}|${hstate.place}|Total|${s2}|${d2}|${b.year}`];
    if (df) box.append(el("p", { class: "h-note" }, `Antes, de ${a.year} para ${b.year}: `,
      el("b", { text: df[4] ? (df[1] > 0 ? "aumentou" : "diminuiu") : "não dá para dizer" }),
      ` (de ${in100(a.e)} para ${in100(b.e)} em cada 100).`));
  }
  box.append(hTrendChart(shown, ok));
  if (ok && shown.length < pts.length) box.append(el("p", { class: "h-note", text: "Anos sem comparação aprovada ficam fora da linha (ver detalhes na página Série histórica)." }));
}
function hTrendChart(pts, joined) {
  const W = 560, H = 210, L = 46, R = 16, T = 16, Bm = 30;
  const years = pts.map((p) => p.year);
  const y0 = Math.min(...years), y1 = Math.max(...years);
  const stepV = niceStep(Math.max(...pts.map((p) => p.hi ?? p.e)) * 1.15, 4);
  const top = stepV * Math.ceil((Math.max(...pts.map((p) => p.hi ?? p.e)) * 1.15) / stepV);
  const x = (y) => (y1 === y0 ? (L + W - R) / 2 : L + ((y - y0) / (y1 - y0)) * (W - L - R));
  const y = (v) => T + (1 - v / top) * (H - T - Bm);
  const root = svg("svg", { viewBox: `0 0 ${W} ${H}`, class: "h-trend-svg", role: "img",
    "aria-label": pts.map((p) => `${p.year}: ${in100(p.e)} em cada 100 (${between(p)})`).join("; ") });
  for (let v = 0; v <= top + 1e-9; v += stepV) {
    root.append(svg("line", { x1: L, x2: W - R, y1: y(v), y2: y(v), class: "grid" }),
      svg("text", { x: L - 6, y: y(v) + 4, "text-anchor": "end", class: "tick", text: pct0(v) }));
  }
  if (joined && pts.length > 1) {
    const band = pts.map((p) => `${x(p.year)},${y(p.hi)}`).concat(pts.slice().reverse().map((p) => `${x(p.year)},${y(p.lo)}`)).join(" ");
    root.append(svg("polygon", { points: band, class: "band" }),
      svg("polyline", { points: pts.map((p) => `${x(p.year)},${y(p.e)}`).join(" "), class: "line" }));
  }
  for (const p of pts) {
    if (!joined) root.append(svg("line", { x1: x(p.year), x2: x(p.year), y1: y(p.lo), y2: y(p.hi), class: "whisker" }));
    root.append(svg("circle", { cx: x(p.year), cy: y(p.e), r: 5, class: "dot" }),
      svg("text", { x: x(p.year) + (p === pts[0] && pts.length > 1 ? 8 : 0), y: y(p.e) - 10,
        "text-anchor": p === pts[0] && pts.length > 1 ? "start" : p === pts[pts.length - 1] && pts.length > 1 ? "end" : "middle", class: "val", text: pct0(p.e) }),
      svg("text", { x: x(p.year), y: H - 8, "text-anchor": "middle", class: "tick", text: p.year }));
  }
  return root;
}

// ------------------------------------------------------------------ bloco 6: mapa
function renderHomeMap() {
  const wrap = clear($("h-map")), legend = clear($("h-map-legend"));
  const topic = G.topics.find((t) => t.id === hstate.topic), it = G.items[topic.main];
  $("h-map-sub").textContent = `${it.short} · ${hstate.group === "Todos" ? "todos os alunos" : hstate.group.toLowerCase()} · clique num estado ou numa capital para ver os números de lá`;
  if (!GEO) { wrap.append(el("p", { class: "map-empty", text: "Mapa não carregado. Use a lista “Onde?” acima." })); return; }
  const [s, d] = groupDims();
  const rows = rowsOf(it.m).filter((r) => isAgeTotal(r.a) && r.s === s && r.d === d && approved(r));
  const ufs = rows.filter((r) => r.t.type === "uf"), caps = rows.filter((r) => r.t.type === "capital");
  if (!ufs.length) { wrap.append(el("p", { class: "map-empty", text: "Sem números por estado para esta combinação." })); return; }
  const P = projector();
  const all = ufs.concat(caps).map((r) => r.e);
  const lo = Math.min(...all), hi = Math.max(...all), step = (hi - lo) / 5 || 1;
  const cls = (v) => "q" + Math.min(5, Math.floor((v - lo) / step) + 1);
  const root = svg("svg", { viewBox: `0 0 ${P.W} ${P.H.toFixed(0)}`, role: "img", "aria-label": `Mapa: ${it.short} por estado e capital` });
  const byUf = new Map(ufs.map((r) => [r.t.uf_code, r]));
  const pick = (code) => homeSet({ place: code });
  const bind = (node, r) => {
    node.addEventListener("pointermove", (e) => { const t = clear(tip());
      t.append(el("div", { class: "tt-name", text: placeName(r.t) }), el("div", { class: "tt-value", text: `${in100(r.e)} em cada 100` }),
        el("div", { class: "tt-meta", text: between(r) })); t.hidden = false; moveTip(e); });
    node.addEventListener("pointerleave", hideTip);
    node.addEventListener("click", () => pick(r.t.code));
    node.addEventListener("keydown", (e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); pick(r.t.code); } });
  };
  const selUf = (hTerr(hstate.place) || {}).type === "uf" ? hstate.place : null;
  for (const sh of P.shapes) {
    const r = byUf.get(sh.code);
    if (!r) { root.append(svg("path", { d: sh.d, class: "nd" })); continue; }
    const p = svg("path", { d: sh.d, class: `${cls(r.e)} ${r.t.code === selUf ? "sel" : ""}`, tabindex: "0",
      "aria-label": `${r.t.name}: ${in100(r.e)} em cada 100` });
    bind(p, r);
    root.append(p);
  }
  root.querySelectorAll("path.sel").forEach((n) => root.append(n));
  for (const r of caps) {
    const c = CAPS && CAPS[r.t.uf];
    if (!c) continue;
    const [cx, cy] = P.pt(c[0], c[1]);
    const on = r.t.code === hstate.place;
    const dot = svg("circle", { cx: cx.toFixed(1), cy: cy.toFixed(1), r: on ? 7 : 4.5, class: `cap ${cls(r.e)} ${on ? "sel" : ""}`, tabindex: "0",
      "aria-label": `${placeName(r.t)}: ${in100(r.e)} em cada 100` });
    bind(dot, r);
    root.append(dot);
  }
  wrap.append(root);
  const ramp = el("div", { class: "ramp" });
  for (let q = 1; q <= 5; q++) ramp.append(el("span", null, el("i", { style: `background: var(--seq-${q})` }), pct0(lo + step * (q - 1))));
  legend.append(ramp, el("span", { class: "card-sub", text: "Mais escuro = menor; mais claro = maior. Pontos = capitais." }));
}

// ------------------------------------------------------------------ página
function renderHome() {
  if (!G) {
    clear($("h-answer")).append(el("p", { class: "empty", text: "A configuração da tela inicial não está no pacote de dados. Rode python scripts/run_all.py." }));
    return;
  }
  renderHomeChoices();
  renderHomeAnswer();
  renderHomeTypes();
  renderHomeBullying();
  renderHomeAbsence();
  renderHomeTrend();
  renderHomeMap();
}

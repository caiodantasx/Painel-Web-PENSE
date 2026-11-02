/* Página “Visão geral”: números-chave, ranking em tabela, categorias, recortes e definição. */
"use strict";

function renderDefinition() {
  const m = measure(), box = clear($("definition"));
  const comp = m.comparability_status || "SEM_CORRESPONDENTE_IDENTIFICADO";
  const head = refRowFor(currentRows());
  box.append(
    el("header", { class: "panel-head" }, el("div", null, el("h2", { text: "O que este número mede" }),
      el("p", { class: "meta", text: `Tabela ${m.tables} · PeNSE ${m.year} · ${m.theme_label}` }))),
    readingBlock(m, head),
    el("p", { class: "source-note", text: B.meta.source_note || "" }),
    el("p", { class: "statement" }, el("b", { text: "Título oficial da tabela: " }), m.definition),
    m.question_text && m.question_text !== "PENDENTE"
      ? el("p", { class: "question" }, el("b", { text: "Pergunta feita: " }), `“${m.question_text}”`)
      : el("p", { class: "question" }, el("b", { text: "Pergunta feita: " }), "ainda não ligada a esta tabela (sem indicador correspondente nos microdados)."),
    el("div", { class: "meta-row" },
      el("span", null, el("b", { text: "Quem: " }), m.population),
      el("span", null, el("b", { text: "Quando: " }), m.period),
      el("span", null, el("b", { text: "Quem respondeu: " }), m.informant.startsWith("Escola") ? "a escola (diretor ou responsável)" : "o próprio aluno"),
      el("span", null, el("b", { text: "Como aparece: " }), m.unit === "%" ? "percentual" : "número estimado de escolares")),
    el("div", { class: "meta-row" },
      el("span", null, el("b", { text: "O percentual é calculado sobre: " }), m.denominator, " "),
      m.denominator_status === "REGRA_DERIVADA_REVISAR" ? chip("REVIEW_REQUIRED", { REVIEW_REQUIRED: ["base de cálculo a conferir", "serious"] }) : null),
    el("div", { class: "meta-row" },
      el("span", null, el("b", { text: "Dá para comparar com outros anos? " })), chip(comp, COMP_LABEL),
      m.multi_response ? el("span", null, " O aluno podia marcar mais de uma resposta: os tipos não somam 100%.") : null),
  );
}

function renderHeroSide() {
  const m = measure(), rows = currentRows(), head = refRowFor(rows);
  const t1 = clear($("tile-headline"));
  if (head) {
    t1.append(
      el("div", { class: "label", text: `${shortName(head.t)} · ${[state.age, state.sex, state.dep].filter((x) => x !== "Total").join(" · ") || "todos os escolares"}` }),
      el("div", { class: "value" }, head.e === null ? "—" : fmt(head.e, m), isPct(m) ? null : el("span", { class: "unit", text: "escolares" })),
      el("div", { class: "detail" }, `Margem de erro: entre ${fmtCI(head, m)} `, help("margem"),
        head.cv !== null ? ` · ${precisionText(head.cv)} ` : "", head.cv !== null ? help("precisao") : null),
      ciStrip([{ r: head }], m, scaleMax([head], m)),
      head.e === null ? null : numberCard(m, head),
      el("div", null, chip(head.st)),
    );
  } else t1.append(el("div", { class: "label", text: "Sem estimativa para Brasil ou para o conjunto das capitais nesta seleção." }));

  const t2 = clear($("tile-selected"));
  const sel = state.selected ? rows.find((r) => r.t.code === state.selected) : null;
  t2.classList.toggle("empty-sel", !sel);
  if (!sel) {
    t2.append(el("div", { class: "label", text: "Território selecionado" }),
      el("p", { class: "hint", text: "Clique em um estado ou capital no mapa, ou numa linha da lista abaixo, para comparar com " +
        (head ? shortName(head.t) : "a referência") + "." }));
  } else {
    const max = scaleMax([sel, head].filter(Boolean), m);
    t2.append(el("div", { class: "label", text: `Selecionado · ${SCOPES[state.scope].short}` }),
      el("div", { class: "value" }, sel.e === null ? (sel.sym ? `"${sel.sym}"` : "—") : fmt(sel.e, m)),
      el("div", { class: "detail", text: `${shortName(sel.t)} · margem de erro: entre ${fmtCI(sel, m)}` }));
    if (sel.e !== null && head && head.e !== null) {
      t2.append(ciStrip([{ r: head }, { r: sel, cls: "sel" }], m, max));
      const cmp = el("div", { class: "compare" },
        el("span", { class: "sw", style: "background: var(--select)" }), el("span", { text: shortName(sel.t) }), el("span", { class: "num", text: fmt(sel.e, m) }),
        el("span", { class: "sw", style: "background: var(--accent)" }), el("span", { text: shortName(head.t) }), el("span", { class: "num", text: fmt(head.e, m) }));
      t2.append(cmp);
      if (isPct(m)) {
        const d = sel.e - head.e;
        t2.append(el("div", { class: "detail" }, `Diferença de ${d > 0 ? "+" : ""}${nf1.format(d)} pontos percentuais `, help("pp"),
          ". Se as faixas acima se sobrepõem, a diferença pode ser só efeito da amostra ", help("comparar")));
      }
    }
    t2.append(el("div", null, chip(sel.st)));
  }

  const t3 = clear($("tile-extremes"));
  const sc = SCOPES[state.scope];
  const pool = scopeRows().filter((r) => approved(r) && r.t.type !== "country").sort((a, b) => b.e - a.e);
  t3.append(el("header", { class: "panel-head" }, el("div", null, el("h2", { text: `Destaques · ${sc.short}` }),
    el("p", { class: "card-sub", text: pool.length ? `${pool.length} lugares com valor confiável · valores em ${unitShort(m)}` : "Nenhum valor confiável neste grupo" }))));
  if (!pool.length) return;
  const max = scaleMax(pool, m);
  const list = (title, arr, startPos) => {
    const box = el("div", { class: "extremes" }, el("h3", { text: title }));
    arr.forEach((r, i) => {
      const b = el("button", { type: "button", class: "mini", "aria-label": `${shortName(r.t)}: ${fmt(r.e, m)} (${unitShort(m)})`,
        title: `${shortName(r.t)}: ${fmt(r.e, m)} = ${per100(r.e)} ${(m.explain && m.explain.count_base) || ""}` },
        el("span", { class: "pos", text: String(startPos(i)) }), el("span", { class: "nm", text: shortName(r.t) }),
        el("span", { class: `bar${r.t.code === state.selected ? " sel" : ""}`, style: `width:${(r.e / max) * 100}%` }),
        el("span", { class: "num", text: fmt(r.e, m) }));
      b.addEventListener("click", () => selectTerritory(r.t.code));
      box.append(b);
    });
    return box;
  };
  const n = Math.min(5, Math.ceil(pool.length / 2));
  t3.append(list("Maiores valores", pool.slice(0, n), (i) => i + 1));
  if (pool.length > n) t3.append(list("Menores valores", pool.slice(-n).reverse(), (i) => pool.length - i));
}

function renderCoverage() {
  const t3 = clear($("tile-coverage"));
  const all = rowsOf(state.measure);
  const ok = all.filter(approved).length;
  t3.append(
    el("div", { class: "label", text: "Cobertura deste indicador na base" }),
    el("div", { class: "big", text: nf0.format(ok) }),
    el("div", { class: "detail", text: `estimativas aprovadas de ${nf0.format(all.length)} publicadas (todos os recortes e territórios)` }),
    el("div", { class: "meta-row" }, ...Object.entries(countBy(all, (r) => r.st)).map(([k, v]) => el("span", null, chip(k), " ", nf0.format(v)))),
  );
}

function renderRankTable() {
  const m = measure(), sc = SCOPES[state.scope];
  const rows = scopeRows();
  const ref = refRowFor(currentRows());
  const ranked = rows.filter(approved).filter((r) => r.t.type !== "country").sort((a, b) => b.e - a.e);
  const rank = new Map(ranked.map((r, i) => [r.t.code, i + 1]));
  const others = rows.filter((r) => !approved(r));
  let body = ranked.slice();
  if (state.sort === "asc") body.reverse();
  if (state.sort === "name") body.sort((a, b) => shortName(a.t).localeCompare(shortName(b.t), "pt-BR"));
  body = body.concat(others);
  const showRef = ref && !body.includes(ref) && approved(ref);
  const max = scaleMax(body.concat(ref ? [ref] : []).filter((r) => r.e !== null), m);
  const pct = (v) => `${(Math.max(0, Math.min(v, max)) / max) * 100}%`;
  const barCell = (r) => {
    const box = el("div", { class: "rbar" });
    if (r.e !== null) {
      box.append(el("span", { class: `fill ${lowPrecision(r) ? "low" : ""}`, style: `width:${pct(r.e)}` }));
      if (r.lo !== null && r.hi !== null) box.append(el("span", { class: "ci", style: `left:${pct(r.lo)};width:calc(${pct(r.hi)} - ${pct(r.lo)})` }));
    }
    if (ref && ref.e !== null && isPct(m) && r !== ref) box.append(el("span", { class: "ref", style: `left:${pct(ref.e)}` }));
    return box;
  };
  const list = (showRef ? [ref] : []).concat(body);
  table($("rank-table"), [
    { label: "#", cls: "pos", render: (r) => (r === ref ? "ref." : rank.get(r.t.code) ? String(rank.get(r.t.code)) : "—") },
    { label: "Território", cls: "terr", render: (r) => el("span", null, shortName(r.t), r.t.uf && r.t.type === "capital" ? el("small", { text: r.t.uf }) : null) },
    { label: isPct(m) ? "Valor e margem de erro" : "Total estimado e margem de erro", cls: "barcell", render: barCell, help: "margem" },
    { label: isPct(m) ? "% de alunos" : "Escolares", cls: "num strong", help: "", helpText: `Valor em ${unitShort(m)}${cutText()}. Não é número de ocorrências nem de escolas.`, render: (r) => (r.e === null ? (r.sym ? `"${r.sym}"` : "—") : fmt(r.e, m) + (lowPrecision(r) ? " ‡" : "")) },
    { label: "Margem de erro", cls: "num", render: (r) => fmtCI(r, m), help: "margem" },
    { label: "Situação", render: (r) => chip(r.st), help: "situacao" },
  ], list, { onClick: (r) => r !== ref && selectTerritory(r.t.code), isSel: (r) => r.t.code === state.selected,
             rowClass: (r) => (r === ref || r.t.type === "country" ? "is-ref" : "") });
  $("rank-table-sub").textContent = `${sc.label} · valores em ${unitShort(m)} · ${[state.age, state.sex, state.dep].join(" · ")} · clique numa linha para destacar no mapa`;
  const lg = clear($("rank-table-legend"));
  lg.append(
    el("span", null, el("span", { class: "sw", style: "background: var(--accent)" }), "estimativa"),
    el("span", null, el("span", { class: "sw", style: "background: var(--select)" }), "selecionado"),
    el("span", null, "traço fino sobre a barra = margem de erro (onde o valor real provavelmente está) ", help("margem")),
    ref && isPct(m) ? el("span", { text: `linha tracejada = ${shortName(ref.t)} (${fmt(ref.e, m)}), para comparar` }) : null,
    el("span", null, "‡ e barra mais clara = estimativa pouco precisa ", help("precisao")),
  );
}

function renderCategories() {
  const m = measure();
  const ms = idx.indicators.get(state.indicator).filter((mi) => B.measures[mi].unit === m.unit);
  const items = [];
  let headName = "";
  for (const mi of ms) {
    const rs = rowsOf(mi).filter((r) => dimsMatch(r, state.age, state.sex, state.dep));
    const h = headlineRow(rs);
    if (!h || !approved(h)) continue;
    headName = h.t.name;
    const mm = B.measures[mi];
    items.push({ key: mi, label: mm.category || "Indicador geral", row: h, cls: mi === state.measure ? "sel" : "",
                 group: mm.category_group || "", tipTitle: `${h.t.name} · ${mm.category || "Indicador geral"}` });
  }
  $("cat-title").textContent = ms.length > 1 ? "Tipos dentro deste indicador" : "Indicador";
  $("cat-sub").textContent = `${headName} · clique em uma barra para trocar a categoria${m.multi_response ? " · múltipla resposta" : ""}`;
  hbar($("chart-categories"), items, { m, aria: "Estimativa por categoria", onSelect: (it) => { state.measure = it.key; update(); } });
}

function renderBreakdown() {
  const m = measure(), rows = rowsOf(state.measure);
  const head = headlineRow(rows.filter((r) => dimsMatch(r, "Total", "Total", "Total")));
  if (!head) { hbar($("chart-breakdown"), [], { m }); return; }
  const code = head.t.code;
  const pick = (a, s, d) => rows.find((r) => r.t.code === code && dimsMatch(r, a, s, d) && approved(r));
  const items = [];
  const push = (group, label, r, sel) => { if (r) items.push({ key: group + label, label, row: r, group, cls: sel ? "sel" : "" }); };
  push("Total", "Total", pick("Total", "Total", "Total"), state.age === "Total" && state.sex === "Total" && state.dep === "Total");
  for (const a of ["13 a 15 anos", "16 e 17 anos"]) push("Grupo de idade", a, pick(a, "Total", "Total"), state.age === a);
  for (const s of ["Homem", "Mulher"]) push("Sexo", s, pick("Total", s, "Total"), state.sex === s);
  for (const d of ["Pública", "Privada"]) push("Rede de ensino", d, pick("Total", "Total", d), state.dep === d);
  $("brk-sub").textContent = `${head.t.name} · um recorte por vez (demais dimensões = Total) · clique para filtrar`;
  hbar($("chart-breakdown"), items, { m, aria: "Estimativa por recorte populacional", onSelect: (it) => {
    const g = it.group;
    state.age = g === "Grupo de idade" ? it.label : "Total";
    state.sex = g === "Sexo" ? it.label : "Total";
    state.dep = g === "Rede de ensino" ? it.label : "Total";
    update();
  } });
}

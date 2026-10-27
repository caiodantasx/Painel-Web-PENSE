/* Painel PeNSE — consome dashboard/data/pense_bundle.json gerado pela pipeline.
 * Nenhuma estimativa é escrita neste arquivo: todo número exibido vem do pacote de dados,
 * com status de validação e célula de origem. */
(function () {
  "use strict";

  const SVGNS = "http://www.w3.org/2000/svg";
  const APPROVED = new Set(["VALID", "VALID_WITH_WARNINGS"]);
  const SCOPES = {
    uf: { label: "Unidades da Federação", short: "Estados (UF)", types: ["uf"], ref: "BR" },
    capital: { label: "Municípios das capitais", short: "Capitais", types: ["capital"], ref: "CAPITAIS" },
    regional: { label: "Brasil e Grandes Regiões", short: "Regiões", types: ["country", "region"], ref: "BR" },
  };
  const SCOPE_PREF = ["uf", "capital", "regional"];
  const STATUS_LABEL = {
    VALID: ["Confiável", "good"], VALID_WITH_WARNINGS: ["Usar com cuidado", "warning"],
    REVIEW_REQUIRED: ["Em revisão", "serious"], ERROR: ["Erro", "critical"], NOT_AVAILABLE: ["Sem valor publicado", "neutral"],
  };
  const COMP_LABEL = {
    COMPARABLE: ["Comparável", "good"], COMPARABLE_WITH_CAVEATS: ["Comparável com ressalvas", "warning"],
    NOT_COMPARABLE: ["Não comparável", "critical"], PENDING_REVIEW: ["Pendente de revisão", "serious"],
    SEM_CORRESPONDENTE_IDENTIFICADO: ["Sem correspondente", "neutral"],
  };
  // Estado da diferença entre dois anos, decidido pela pipeline (src/pense/microdata/series.py):
  // o selo "Diferença significativa a 5%" só existe com decisão registrada do pesquisador e evidência
  // nas duas edições (D27). Significância não é relevância prática nem causa.
  const CHANGE_LABEL = {
    SIGNIFICATIVA_5PCT_COM_DECISAO: ["Diferença significativa a 5%", "good"],
    SIGNIFICATIVA_SEM_DECISAO: ["Significativa · aguarda decisão", "warning"],
    SIGNIFICATIVA_APROXIMADA: ["Significativa (teste aproximado)", "warning"],
    NAO_SIGNIFICATIVA: ["Pode ser acaso da amostra", "neutral"],
  };
  const changeChip = (status) => chip(status || "NAO_SIGNIFICATIVA", CHANGE_LABEL);
  const confirmed = (status) => status === "SIGNIFICATIVA_5PCT_COM_DECISAO";
  const RULE_TEXT = {
    VAL001: "o IBGE publicou um símbolo (ex.: “-”) no lugar do número",
    VAL002F: "arredondamento do computador na planilha (ex.: 100,0000000001%), valor mantido",
    VAL002N: "o limite inferior da margem de erro publicada ficou abaixo de 0%",
    VAL005: "margem de erro publicada igual a zero, comum em grupos com pouquíssimas escolas",
    VAL006: "margem de erro cortada em 0% ou 100% (o valor real não pode passar desses limites)",
    VAL008: "estimativa pouco precisa: a margem de erro é grande em relação ao valor",
    VAL009: "margem de erro e precisão publicadas não batem entre si",
    VAL012: "nome de lugar não reconhecido na lista de territórios",
    VAL014: "as categorias somadas não dão 100%",
    VAL015: "o total ficou fora da faixa das partes (ex.: total menor que meninos e meninas)",
    VAL020: "o mesmo número aparece diferente em duas tabelas",
    VAL022: "cabeçalho da tabela ambíguo: precisa de conferência humana",
    OUT001: "valor muito diferente dos outros lugares (pode ser real, só sinalizado)",
    VAL002: "percentual fora de 0 a 100", VAL003: "limites da margem de erro invertidos",
    VAL004: "o valor ficou fora da própria margem de erro", VAL007: "margem de erro com só um dos limites",
    VAL010: "o valor difere entre a aba principal e a aba de precisão do IBGE",
    VAL011: "a mesma linha aparece duas vezes na tabela", VAL013: "o ano do título difere do ano da fonte",
    VAL016: "texto no lugar do número", VAL017: "erro do Excel na célula", VAL018: "contagem negativa",
    VAL019: "o total não é a soma das partes", VAL021: "seção da tabela não reconhecida",
    VAL023: "o mesmo recorte aparece na linha e na coluna", VAL024: "ano lido da coluna da tabela (série com vários anos)",
    VAL025: "ano não identificado na tabela",
    HDR001: "coluna que a leitura automática não entendeu", HDR005: "cabeçalho deduzido sem células mescladas",
    HDR006: "cabeçalho da tabela ambíguo", STB004: "linha de seção com números repetidos (defeito da planilha), ignorada",
    STB005: "linha de seção com números próprios, não usada",
    NRM003: "sem correspondente na aba de precisão", NRM004: "linha da aba de precisão sem valor principal",
    ING008: "caminho suspeito dentro do ZIP", ING010: "arquivo que não pôde ser lido",
    ADP000: "aba sem leitor reconhecido", ADP900: "falha do leitor da tabela",
    REF001: "tabela do guia oficial que não veio nos arquivos", REF002: "título diferente do guia oficial do IBGE",
    REF003: "aba que não está no guia oficial",
  };
  const ISSUE_CLASS = {
    ERRO_CONFIRMADO: "erro confirmado", POSSIVEL_ANOMALIA: "pode ser problema", POSSIVEL_VALOR_EXTREMO_LEGITIMO: "valor extremo, provavelmente real",
    NAO_VALIDADO: "ainda não conferido", INFORMATIVO: "só registro",
  };
  // Glossário: um texto por termo, usado nos ícones “?” de todo o painel.
  const GLOSS = {
    margem: "Margem de erro (intervalo de confiança de 95%): a PeNSE entrevista uma amostra de alunos, não todos. Por isso cada número é uma estimativa, e a margem mostra a faixa onde o valor real provavelmente está. Ex.: 12% (entre 11% e 13%).",
    precisao: "Precisão (coeficiente de variação, CV): o tamanho da margem de erro em relação ao valor. Boa: CV abaixo de 15%. Razoável: de 15% a 30%. Baixa: 30% ou mais — use o número só como indicação.",
    comparar: "Para dizer que um lugar tem valor maior que outro, as margens de erro não devem se sobrepor muito. Diferenças pequenas com margens sobrepostas podem ser só efeito da amostra.",
    significativa: "Diferença significativa a 5%: o intervalo de confiança de 95% da diferença entre os dois anos não inclui o zero. Em outras palavras, se não houvesse diferença nenhuma entre os anos, uma diferença deste tamanho ou maior apareceria em menos de 5% das amostras possíveis. Isso não é a chance de a mudança ser real, e um resultado significativo não é certeza absoluta. Significativa não quer dizer grande nem importante, não explica a causa e não elimina outras limitações (mudança de pergunta, de público ou de método). “Não significativa” não quer dizer que nada mudou, só que a amostra não permite afirmar. O selo “Diferença significativa a 5%” só aparece quando o pesquisador registrou a decisão de que os anos são comparáveis e as duas edições foram conferidas com as tabelas do IBGE; antes disso, a diferença aparece como “aguarda decisão”. Ser comparável não quer dizer que houve mudança.",
    pp: "Pontos percentuais (p.p.): diferença entre dois percentuais. De 10% para 13% é um aumento de 3 p.p. (e não de 3%).",
    indicador: "Indicador: o que está sendo medido, sempre como percentual dos escolares (ou da escola) que responderam de certa forma.",
    edicao: "Ano da pesquisa (edição): a PeNSE foi feita em 2009, 2012, 2015, 2019 e 2024. Cada edição tem um público diferente (9º ano ou 13 a 17 anos), por isso nem todas podem ser comparadas.",
    recorte: "Recorte: um grupo de alunos dentro do total — faixa de idade, sexo ou rede de ensino (pública ou privada).",
    situacao: "Situação do número: Confiável (passou em todas as verificações), Usar com cuidado (passou, mas tem uma observação), Em revisão (fora dos gráficos até alguém conferir), Sem valor publicado (o IBGE publicou um símbolo).",
    origem: "Onde o número está na planilha original do IBGE (arquivo, aba e célula), para quem quiser conferir.",
    n: "n: número de alunos que responderam à pergunta nesse grupo. Grupos pequenos têm margens de erro maiores.",
    microdados: "Calculado dos microdados: o número não está numa tabela publicada; foi calculado a partir das respostas individuais divulgadas pelo IBGE, com o mesmo método oficial e conferido contra as tabelas que existem.",
  };


  const nf1 = new Intl.NumberFormat("pt-BR", { minimumFractionDigits: 1, maximumFractionDigits: 1 });
  const nf0 = new Intl.NumberFormat("pt-BR", { maximumFractionDigits: 0 });
  // fmt:start — intervalo de confiança da diferença entre anos (D28). Só apresentação: os valores
  // internos não mudam. Usa o menor número de casas (1 a 4) que não transforma um limite diferente
  // de zero em "0,0", com as mesmas casas nos dois limites e sinal explícito.
  const ciDecimals = (v) => {
    if (v === null || v === undefined || Number.isNaN(v) || v === 0) return 1;
    for (let d = 1; d <= 4; d++) if (Number(Math.abs(v).toFixed(d)) !== 0) return d;
    return 4;
  };
  const signedFixed = (v, d) => (v > 0 ? "+" : v < 0 ? "−" : "")
    + new Intl.NumberFormat("pt-BR", { minimumFractionDigits: d, maximumFractionDigits: d }).format(Math.abs(v));
  const ciDiffText = (lo, hi, significant) => {
    const d = Math.max(ciDecimals(lo), ciDecimals(hi));
    return `IC 95% da diferença: de ${signedFixed(lo, d)} a ${signedFixed(hi, d)} p.p. · `
      + (significant ? "o intervalo não inclui o zero" : "o intervalo inclui o zero: a amostra não permite afirmar que houve diferença");
  };
  // fmt:end
  const $ = (id) => document.getElementById(id);

  let B = null, GEO = null, CAPS = null, PROJ = null;
  const idx = { byMeasure: new Map(), measures: [], terr: [], indicators: new Map() };
  const state = { page: "overview", edition: "", indicator: "", measure: -1, age: "Total", sex: "Total", dep: "Total",
                  scope: "uf", availScopes: [], selected: null, sort: "desc" };

  // ------------------------------------------------------------------ utilidades
  function el(tag, attrs, ...children) {
    const n = document.createElement(tag);
    if (attrs) for (const [k, v] of Object.entries(attrs)) {
      if (v === null || v === undefined || v === false) continue;
      if (k === "class") n.className = v; else if (k === "text") n.textContent = v;
      else if (k.startsWith("on")) n.addEventListener(k.slice(2), v); else n.setAttribute(k, v);
    }
    for (const c of children.flat()) if (c !== null && c !== undefined) n.append(c instanceof Node ? c : document.createTextNode(String(c)));
    return n;
  }
  function svg(tag, attrs, ...children) {
    const n = document.createElementNS(SVGNS, tag);
    if (attrs) for (const [k, v] of Object.entries(attrs)) {
      if (v === null || v === undefined) continue;
      if (k === "text") n.textContent = v; else if (k.startsWith("on")) n.addEventListener(k.slice(2), v); else n.setAttribute(k, v);
    }
    for (const c of children.flat()) if (c) n.append(c);
    return n;
  }
  const isPct = (m) => m.unit === "%";
  function fmt(v, m) {
    if (v === null || v === undefined) return "—";
    return isPct(m) ? nf1.format(v) + "%" : nf0.format(v);
  }
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
  function fmtCI(r, m) {
    if (r.lo === null || r.hi === null) return "—";
    const f = (v) => (isPct(m) ? nf1.format(v) + "%" : nf0.format(v));
    return `${f(r.lo)} a ${f(r.hi)}`;
  }
  function help(key, text) {
    const msg = text || GLOSS[key] || "";
    const h = el("span", { class: "help", tabindex: "0", role: "img", "aria-label": "Ajuda: " + msg, text: "?" });
    const show = (e) => { const t = clear(tip()); t.append(el("div", { class: "tt-help", text: msg })); t.hidden = false; moveTip(e); };
    h.addEventListener("pointerenter", show);
    h.addEventListener("pointermove", moveTip);
    h.addEventListener("pointerleave", hideTip);
    h.addEventListener("focus", show);
    h.addEventListener("blur", hideTip);
    return h;
  }
  function precision(cv) {
    if (cv === null || cv === undefined || cv === "") return null;
    return cv < 15 ? ["boa", "good"] : cv < 30 ? ["razoável", "warning"] : ["baixa", "serious"];
  }
  function precisionText(cv) {
    const p = precision(cv);
    return p ? `Precisão ${p[0]} (CV ${nf1.format(cv)}%)` : "";
  }
  function chip(code, map) {
    const [label, cls] = (map || STATUS_LABEL)[code] || [code, "neutral"];
    return el("span", { class: `chip ${cls}`, text: label });
  }
  function clear(node) { while (node.firstChild) node.removeChild(node.firstChild); return node; }
  function niceStep(span, n) {
    const raw = span / n, p = Math.pow(10, Math.floor(Math.log10(raw))), f = raw / p;
    return (f <= 1 ? 1 : f <= 2 ? 2 : f <= 2.5 ? 2.5 : f <= 5 ? 5 : 10) * p;
  }
  function fitText(text, maxPx, pxPerChar) {
    const max = Math.floor(maxPx / pxPerChar);
    return text.length <= max ? text : text.slice(0, Math.max(1, max - 1)).trimEnd() + "…";
  }
  function niceMax(v) {
    if (v <= 0) return 1;
    const p = Math.pow(10, Math.floor(Math.log10(v)));
    const n = v / p;
    return (n <= 1 ? 1 : n <= 2 ? 2 : n <= 2.5 ? 2.5 : n <= 5 ? 5 : 10) * p;
  }
  function store(key, val) { try { localStorage.setItem(key, JSON.stringify(val)); } catch (e) { /* armazenamento opcional */ } }
  function recall(key) { try { return JSON.parse(localStorage.getItem(key) || "null"); } catch (e) { return null; } }

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

  // ------------------------------------------------------------------ filtros
  function fillSelect(sel, options, value) {
    clear(sel);
    for (const o of options) {
      const opt = el("option", { value: o.value, text: o.label + (o.disabled ? " — indisponível" : "") });
      if (o.disabled) opt.disabled = true;
      sel.append(opt);
    }
    sel.value = value;
  }
  function editions() {
    // Uma edição por vez no mapa; a série oficial do 9º ano (vários anos na mesma tabela) fica na página "Série histórica".
    const seen = new Map();
    B.measures.forEach((m) => { if (!m.multi_year) seen.set(m.edition_id, m.year); });
    return [...seen.entries()].sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]));
  }
  const editionMeta = (e) => (B.meta.editions || []).find((x) => x.edition_id === e) || {};
  const editionLabel = (e, y) => editionMeta(e).label || `PeNSE ${y}`;
  function renderEditionSwitch() {
    const box = clear($("edition-switch"));
    if (!box) return;
    const eds = editions();
    box.append(el("span", { class: "es-title", text: `Ano da pesquisa (${eds.length} edições):` }));
    const group = el("div", { class: "es-buttons", role: "radiogroup", "aria-label": "Edição da pesquisa" });
    for (const [e, y] of eds) {
      const meta = editionMeta(e);
      const b = el("button", { type: "button", class: `es-btn${e === state.edition ? " on" : ""}`, role: "radio",
        "aria-checked": e === state.edition ? "true" : "false", title: meta.territorial_coverage || "" },
        el("span", { class: "es-label", text: editionLabel(e, y) }));
      b.addEventListener("click", () => { state.edition = e; state.indicator = ""; state.measure = -1; state.selected = null; update(); });
      group.append(b);
    }
    box.append(group, el("p", { class: "es-note" }, "Uma edição por vez (públicos e territórios diferentes). Evolução no tempo: ",
      el("button", { type: "button", class: "linkish", onclick: () => setPage("history") }, "Série histórica"), "."));
  }
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

  function syncFilters(changed) {
    const eds = editions();
    if (!state.edition || !eds.some(([e]) => e === state.edition)) state.edition = eds.find(([e]) => e === "PENSE_2024")?.[0] || eds[0][0];
    fillSelect($("f-edition"), eds.map(([e, y]) => ({ value: e, label: editionLabel(e, y) })), state.edition);

    const inds = indicatorsOf(state.edition);
    if (!inds.includes(state.indicator)) state.indicator = inds[0];
    fillSelect($("f-indicator"), inds.map((k) => {
      const m = B.measures[idx.indicators.get(k)[0]];
      return { value: k, label: `${m.table_family_id} · ${m.short_label}` };
    }), state.indicator);

    const ms = idx.indicators.get(state.indicator);
    const units = [...new Set(ms.map((mi) => B.measures[mi].unit))];
    let unit = state.measure >= 0 && ms.includes(state.measure) ? B.measures[state.measure].unit : (units.includes("%") ? "%" : units[0]);
    if (changed === "unit") unit = $("f-unit").value;
    $("slicer-unit").hidden = units.length < 2;
    fillSelect($("f-unit"), units.map((u) => ({ value: u, label: u === "%" ? "Percentual (%)" : "Total estimado de escolares" })), unit);

    const cats = ms.filter((mi) => B.measures[mi].unit === unit);
    if (changed === "category") state.measure = Number($("f-category").value);
    if (!cats.includes(state.measure)) {
      const prevCat = state.measure >= 0 ? B.measures[state.measure].category : null;
      state.measure = cats.find((mi) => B.measures[mi].category === prevCat) ?? cats[0];
    }
    fillSelect($("f-category"), cats.map((mi) => ({ value: String(mi), label: categoryLabel(B.measures[mi]) })), String(state.measure));
    $("f-category").disabled = cats.length < 2;

    // dimensões: opção disponível se existe observação aprovada com as demais dimensões atuais
    const rows = rowsOf(state.measure);
    const has = (a, s, d) => rows.some((r) => dimsMatch(r, a, s, d) && approved(r));
    let notice = "";
    if (!has(state.age, state.sex, state.dep)) {
      notice = "A combinação de recortes escolhida não é publicada para este indicador; os filtros voltaram para Total.";
      state.age = state.sex = state.dep = "Total";
    }
    const opts = (vals, f) => vals.map((v) => ({ value: v, label: v, disabled: !f(v) }));
    fillSelect($("f-age"), opts(B.dims.age_group, (v) => has(v, state.sex, state.dep)), state.age);
    fillSelect($("f-sex"), opts(B.dims.sex, (v) => has(state.age, v, state.dep)), state.sex);
    fillSelect($("f-dep"), opts(B.dims.admin_dependency, (v) => has(state.age, state.sex, v)), state.dep);

    const cur = rows.filter((r) => dimsMatch(r, state.age, state.sex, state.dep));
    const avail = SCOPE_PREF.filter((k) => cur.some((r) => SCOPES[k].types.includes(r.t.type) && approved(r)));
    state.availScopes = avail;
    if (!avail.includes(state.scope)) { state.scope = avail[0] || "regional"; state.selected = null; }
    renderScopeSwitches();

    const n = $("notice");
    n.hidden = !notice;
    n.textContent = notice;
    store("pense-filters", { edition: state.edition, indicator: state.indicator, page: state.page });
  }

  function bindFilters() {
    $("f-edition").addEventListener("change", (e) => { state.edition = e.target.value; state.indicator = ""; state.measure = -1; state.selected = null; update(); });
    $("f-indicator").addEventListener("change", (e) => { state.indicator = e.target.value; state.measure = -1; state.selected = null; update(); });
    $("f-unit").addEventListener("change", () => { state.measure = -1; update("unit"); });
    $("f-category").addEventListener("change", () => update("category"));
    $("f-age").addEventListener("change", (e) => { state.age = e.target.value; update(); });
    $("f-sex").addEventListener("change", (e) => { state.sex = e.target.value; update(); });
    $("f-dep").addEventListener("change", (e) => { state.dep = e.target.value; update(); });
    document.querySelectorAll(".sort-switch .seg").forEach((b) => b.addEventListener("click", () => {
      state.sort = b.dataset.sort;
      document.querySelectorAll(".sort-switch .seg").forEach((x) => x.setAttribute("aria-pressed", String(x === b)));
      renderRankTable();
    }));
  }

  function renderScopeSwitches() {
    document.querySelectorAll(".scope-switch").forEach((box) => {
      clear(box);
      for (const k of SCOPE_PREF) {
        const ok = state.availScopes.includes(k);
        const b = el("button", { type: "button", class: "seg", role: "radio", "aria-checked": String(state.scope === k),
          disabled: !ok, title: ok ? SCOPES[k].label : `${SCOPES[k].label}: não publicado para esta seleção`, text: SCOPES[k].short });
        b.addEventListener("click", () => { if (state.scope !== k) { state.scope = k; state.selected = null; update(); } });
        box.append(b);
      }
    });
  }

  // ------------------------------------------------------------------ tooltip
  const tip = () => $("tooltip");
  function showTip(evt, r, m, title) {
    const t = clear(tip());
    t.append(
      el("div", { class: "tt-name", text: title || r.t.name }),
      el("div", { class: "tt-value", text: r.e === null ? (r.sym ? `Símbolo "${r.sym}"` : "—") : fmt(r.e, m) }),
      r.e !== null && m.reading ? el("div", { class: "tt-reading", text: readingOf(m, r, false) }) : null,
      el("div", { class: "tt-meta", text: `Margem de erro: entre ${fmtCI(r, m)}` }),
      r.cv !== null && r.cv !== undefined ? el("div", { class: "tt-meta", text: precisionText(r.cv) }) : null,
      el("div", { class: "tt-meta", text: `Situação: ${(STATUS_LABEL[r.st] || [r.st])[0]}` }),
      el("div", { class: "tt-meta mono", text: `Origem: ${String(r.src).split("!").pop().replace("::", " › ")}${r.cell ? " › " + r.cell : ""}` }),
    );
    t.hidden = false;
    moveTip(evt);
  }
  function moveTip(evt) {
    const t = tip();
    let x, y;
    if (evt && evt.clientX !== undefined && evt.type !== "focus") { x = evt.clientX + 14; y = evt.clientY + 14; }
    else { const b = evt.target.getBoundingClientRect(); x = b.right + 8; y = b.top; }
    const w = t.offsetWidth, h = t.offsetHeight;
    t.style.left = Math.max(8, Math.min(x, window.innerWidth - w - 8)) + "px";
    t.style.top = Math.max(8, Math.min(y, window.innerHeight - h - 8)) + "px";
  }
  const hideTip = () => { tip().hidden = true; };

  // ------------------------------------------------------------------ gráfico de barras horizontais com IC
  /* items: {key, label, row, cls, group} ; opts: {m, ref, onSelect, labelKeys} */
  function hbar(container, items, opts) {
    clear(container);
    if (!items.length) { container.append(el("p", { class: "empty", text: "Sem observações aprovadas para esta seleção." })); return; }
    const m = opts.m;
    const rowH = 22, barH = 13, top = 6, charW = 6.2;
    const labelW = Math.min(230, Math.max(...items.map((i) => i.label.length)) * charW + 16);
    const groupGap = 18;
    const groups = [...new Set(items.map((i) => i.group || ""))];
    const hasGroups = groups.length > 1 || groups[0] !== "";
    const W = 640, right = 64;
    const maxV = Math.max(...items.map((i) => (i.row.hi ?? i.row.e) || 0), opts.ref?.e || 0);
    const tickStep = niceStep(maxV || 1, 4);
    const xMax = isPct(m) ? Math.min(100, Math.ceil((maxV || 1) / tickStep) * tickStep) : Math.ceil((maxV || 1) / tickStep) * tickStep;
    const x = (v) => labelW + (Math.max(0, v) / xMax) * (W - labelW - right);
    let y = top + (hasGroups ? 14 : 0);
    const layout = [];
    let lastGroup = null;
    for (const it of items) {
      if (hasGroups && it.group !== lastGroup && lastGroup !== null) y += groupGap;
      layout.push({ it, y, groupStart: hasGroups && it.group !== lastGroup });
      lastGroup = it.group;
      y += rowH;
    }
    if (opts.ref && opts.ref.e !== null) { layout.forEach((l) => { l.y += 16; }); y += 16; }
    const H = y + 24;
    const root = svg("svg", { viewBox: `0 0 ${W} ${H}`, role: "img", "aria-label": opts.aria || "Gráfico de barras com intervalo de confiança" });
    const ticks = Math.round(xMax / tickStep);
    for (let k = 0; k <= ticks; k++) {
      const v = tickStep * k, px = x(v);
      root.append(svg("line", { class: k === 0 ? "baseline" : "grid-line", x1: px, x2: px, y1: top, y2: H - 20 }));
      root.append(svg("g", { class: "tick" }, svg("text", { x: px, y: H - 6, "text-anchor": "middle", text: isPct(m) ? (Number.isInteger(v) ? nf0.format(v) : nf1.format(v)) + "%" : compact(v) })));
    }
    if (opts.ref && opts.ref.e !== null) {
      const px = x(opts.ref.e);
      root.append(svg("line", { class: "refline", x1: px, x2: px, y1: top, y2: H - 20 }));
      const refText = `${opts.refLabel} ${fmt(opts.ref.e, m)}`;
      const nearRight = px > W - right - refText.length * 6.5;
      root.append(svg("text", { x: nearRight ? px - 4 : px + 4, y: top + 9, "text-anchor": nearRight ? "end" : "start",
        class: "label-strong", text: refText }));
    }
    const labelKeys = opts.labelKeys || new Set(items.map((i) => i.key));
    for (const { it, y: yy, groupStart } of layout) {
      const r = it.row;
      if (groupStart && it.group) root.append(svg("text", { class: "group-label", x: 0, y: yy - 4, text: it.group }));
      const g = svg("g", { class: "row", tabindex: "0", role: "button",
        "aria-label": `${it.label}: ${r.e === null ? "sem valor" : fmt(r.e, m)}, margem de erro entre ${fmtCI(r, m)}` });
      const cy = yy + rowH / 2;
      g.append(svg("text", { x: labelW - 8, y: cy + 4, "text-anchor": "end", class: it.cls?.includes("sel") || it.cls?.includes("ref") ? "label-strong" : "", text: fitText(it.label, labelW - 12, charW) }));
      const hit = svg("rect", { class: "hit", x: 0, y: yy, width: W, height: rowH, rx: 3 });
      g.append(hit);
      if (r.e !== null) {
        const x0 = x(0), x1 = x(r.e), w = Math.max(1, x1 - x0);
        const rad = Math.min(4, w / 2);
        g.append(svg("path", { class: `bar ${it.cls || ""} ${lowPrecision(r) ? "low" : ""}`,
          d: `M${x0},${cy - barH / 2}h${w - rad}a${rad},${rad} 0 0 1 ${rad},${rad}v${barH - 2 * rad}a${rad},${rad} 0 0 1 -${rad},${rad}h-${w - rad}z` }));
        if (r.lo !== null && r.hi !== null) {
          const a = x(r.lo), b = x(Math.min(r.hi, xMax));
          g.append(svg("line", { class: "whisker", x1: a, x2: b, y1: cy, y2: cy }));
          g.append(svg("line", { class: "whisker", x1: a, x2: a, y1: cy - 4, y2: cy + 4 }));
          g.append(svg("line", { class: "whisker", x1: b, x2: b, y1: cy - 4, y2: cy + 4 }));
        }
        if (labelKeys.has(it.key)) {
          const end = Math.max(x(r.e), r.hi !== null ? x(Math.min(r.hi, xMax)) : 0);
          g.append(svg("text", { class: "val", x: end + 6, y: cy + 4, text: fmt(r.e, m) + (lowPrecision(r) ? " ‡" : "") }));
        }
      } else {
        g.append(svg("text", { x: x(0) + 6, y: cy + 4, text: r.sym ? `símbolo "${r.sym}"` : "sem valor aprovado" }));
      }
      g.addEventListener("pointermove", (e) => showTip(e, r, m, it.tipTitle || it.label));
      g.addEventListener("pointerleave", hideTip);
      g.addEventListener("focus", (e) => showTip(e, r, m, it.tipTitle || it.label));
      g.addEventListener("blur", hideTip);
      if (opts.onSelect) {
        g.addEventListener("click", () => opts.onSelect(it));
        g.addEventListener("keydown", (e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); opts.onSelect(it); } });
      }
      root.append(g);
    }
    container.append(root);
  }
  function compact(v) {
    if (v >= 1e6) return nf1.format(v / 1e6) + " mi";
    if (v >= 1e3) return nf0.format(v / 1e3) + " mil";
    return nf0.format(v);
  }

  // ------------------------------------------------------------------ páginas
  function measure() { return B.measures[state.measure]; }

  function renderDefinition() {
    const m = measure(), box = clear($("definition"));
    const comp = m.comparability_status || "SEM_CORRESPONDENTE_IDENTIFICADO";
    const head = refRowFor(currentRows());
    box.append(
      el("div", { class: "eyebrow", text: `Tabela ${m.tables} · PeNSE ${m.year} · ${m.theme_label}` }),
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

  function refRowFor(rows) {
    const sc = SCOPES[state.scope];
    return rows.find((r) => r.t.code === sc.ref && approved(r)) || headlineRow(rows.filter(approved));
  }
  const shortName = (t) => (t.code === "CAPITAIS" ? "Conjunto das capitais" : t.type === "capital" ? t.name.replace(" (capital)", "") : t.name);

  function ciStrip(rows, m, max) {
    const box = el("div", { class: "ci-strip", "aria-hidden": "true" }, el("div", { class: "track" }));
    const pos = (v) => `${(Math.max(0, Math.min(v, max)) / max) * 100}%`;
    for (const { r, cls } of rows) {
      if (r.lo !== null && r.hi !== null) box.append(el("div", { class: "range", style: `left:${pos(r.lo)};width:calc(${pos(r.hi)} - ${pos(r.lo)})` }));
      box.append(el("div", { class: `dot ${cls || ""}`, style: `left:${pos(r.e)}` }));
    }
    return box;
  }
  function scaleMax(rows, m) {
    const v = Math.max(...rows.map((r) => (r.hi ?? r.e) || 0), 1);
    const step = niceStep(v, 4), top = Math.ceil(v / step) * step;
    return isPct(m) ? Math.min(100, top) : top;
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
          el("span", { class: "bar", style: `width:${(r.e / max) * 100}%;${r.t.code === state.selected ? "background:var(--select)" : ""}` }),
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
  function countBy(arr, f) { const o = {}; for (const x of arr) { const k = f(x); o[k] = (o[k] || 0) + 1; } return o; }

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

  function scopeRows() {
    const sc = SCOPES[state.scope];
    return currentRows().filter((r) => sc.types.includes(r.t.type));
  }

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

  function selectTerritory(code, scope) {
    state.selected = state.selected === code ? null : code;
    if (scope && state.scope !== scope) state.scope = scope;
    update();
  }

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

  function table(tableEl, columns, rows, opts = {}) {
    clear(tableEl);
    const thead = el("thead", null, el("tr", null, columns.map((c) => el("th", { scope: "col" }, c.label, c.help || c.helpText ? " " : null,
      c.help || c.helpText ? help(c.help, c.helpText) : null))));
    const tbody = el("tbody");
    for (const r of rows) {
      const tr = el("tr", { class: [opts.onClick ? "clickable" : "", opts.isSel && opts.isSel(r) ? "sel" : "", opts.rowClass ? opts.rowClass(r) : ""].join(" ") });
      for (const c of columns) {
        const v = c.render ? c.render(r) : r[c.key];
        tr.append(el("td", { class: c.cls || "" }, v instanceof Node ? v : (v ?? "")));
      }
      if (opts.onClick) {
        tr.tabIndex = 0;
        tr.addEventListener("click", () => opts.onClick(r));
        tr.addEventListener("keydown", (e) => { if (e.key === "Enter") opts.onClick(r); });
      }
      tbody.append(tr);
    }
    if (!rows.length) tbody.append(el("tr", null, el("td", { colspan: columns.length, text: opts.empty || "Nenhum registro." })));
    tableEl.append(thead, tbody);
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

  function renderHistory() {
    const m = measure(), box = clear($("history-main"));
    const pairs = B.comparability.filter((p) => p.left_indicator_id === m.indicator_id || p.right_indicator_id === m.indicator_id);
    const series = B.series.filter((p) => p.indicator_id === m.indicator_id || pairs.some((q) => q.concept_id === p.concept_id));
    box.append(el("header", { class: "card-head" }, el("h2", { text: "Tabelas publicadas: indicador escolhido nos filtros" }),
      el("p", { class: "card-sub", text: "Tabelas publicadas: só entram em série pares de edições classificados como comparáveis por decisão documentada. A série acima usa os microdados." })));
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

  function lineChart(points, m) {
    const wrap = el("div", { class: "chart" });
    const terrs = [...new Set(points.map((p) => p.territory_code))].slice(0, 2);
    const years = [...new Set(points.map((p) => p.year))].sort();
    const W = 640, H = 260, L = 48, R = 20, T = 14, Bm = 30;
    const maxV = niceMax(Math.max(...points.map((p) => p.ci_upper ?? p.estimate)));
    const x = (yr) => L + (years.length === 1 ? 0 : ((yr - years[0]) / (years[years.length - 1] - years[0])) * (W - L - R));
    const y = (v) => T + (1 - v / maxV) * (H - T - Bm);
    const root = svg("svg", { viewBox: `0 0 ${W} ${H}`, role: "img", "aria-label": "Série histórica" });
    for (let k = 0; k <= 4; k++) {
      const v = (maxV / 4) * k;
      root.append(svg("line", { class: k ? "grid-line" : "baseline", x1: L, x2: W - R, y1: y(v), y2: y(v) }),
        svg("g", { class: "tick" }, svg("text", { x: L - 6, y: y(v) + 4, "text-anchor": "end", text: fmt(v, m) })));
    }
    years.forEach((yr) => root.append(svg("g", { class: "tick" }, svg("text", { x: x(yr), y: H - 8, "text-anchor": "middle", text: yr }))));
    const colors = ["var(--accent)", "var(--select)"];
    terrs.forEach((tc, ti) => {
      const pts = points.filter((p) => p.territory_code === tc).sort((a, b) => a.year - b.year);
      const band = pts.filter((p) => p.ci_lower !== null);
      if (band.length > 1) root.append(svg("path", { class: "band", fill: colors[ti],
        d: band.map((p, j) => `${j ? "L" : "M"}${x(p.year)},${y(p.ci_upper)}`).join("") +
           band.slice().reverse().map((p) => `L${x(p.year)},${y(p.ci_lower)}`).join("") + "Z" }));
      root.append(svg("path", { class: "series-line", stroke: colors[ti], d: pts.map((p, j) => `${j ? "L" : "M"}${x(p.year)},${y(p.estimate)}`).join("") }));
      pts.forEach((p) => root.append(svg("circle", { cx: x(p.year), cy: y(p.estimate), r: 4.5, fill: colors[ti], stroke: "var(--card)", "stroke-width": 2 })));
      const last = pts[pts.length - 1];
      root.append(svg("text", { x: x(last.year) - 6, y: y(last.estimate) - 9, "text-anchor": "end", class: "label-strong", text: `${last.territory_name} ${fmt(last.estimate, m)}` }));
    });
    wrap.append(root);
    return wrap;
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

  function renderAbout() {
    const box = clear($("about-method"));
    box.append(
      el("h2", { text: "Como os números chegam aqui" }),
      el("p", { text: "As tabelas oficiais do IBGE (XLS, XLSX e ZIP) são lidas por uma pipeline em Python. Cada família de tabela tem um adaptador que interpreta o cabeçalho pelas células mescladas, identifica estimativa, limites do intervalo de confiança de 95% e coeficiente de variação, e registra arquivo, aba e célula de cada valor." }),
      el("h3", { text: "Validação" }),
      el("p", { text: "Regras determinísticas conferem percentuais fora de 0–100, intervalos invertidos, estimativa fora do IC, coerência entre CV e IC, somas de distribuições, totais entre as partes e valores iguais publicados em tabelas diferentes. Valores incomuns são sinalizados, nunca removidos." }),
      el("h3", { text: "Leitura correta" }),
      el("ul", null,
        el("li", { text: "Diferenças entre territórios ou grupos só são discutíveis olhando os intervalos de confiança; este painel não executa testes de significância." }),
        el("li", { text: "CV ≥ 30% indica baixa precisão (barra mais clara e símbolo ‡)." }),
        el("li", { text: "Os cruzamentos de idade, sexo e dependência administrativa dependem da tabela publicada; combinações que o IBGE não publica aparecem como indisponíveis nos filtros, nunca estimadas." }),
        el("li", { text: "Para contagens (estimativa total de escolares), o mapa é desativado: totais absolutos refletem o tamanho da população." }),
        el("li", { text: "As edições 2009 e 2015 referem-se a escolares do 9º ano; a de 2024, a escolares de 13 a 17 anos. Por isso não são combinadas em série." })),
      el("h3", { text: "Exportação" }),
      el("p", { text: "O botão Exportar gera um CSV da seleção atual (todos os territórios do recorte, com status e célula de origem), separado por ponto e vírgula e com vírgula decimal para abrir direto no Excel em português." }),
    );
    table($("table-editions"), [
      { label: "Edição", render: (e) => `PeNSE ${e.reference_year}` },
      { label: "População", render: (e) => e.target_population },
      { label: "Cobertura", render: (e) => e.territorial_coverage },
      { label: "Observação", render: (e) => e.notes },
    ], B.meta.editions);
    table($("table-symbols"), [
      { label: "Símbolo", cls: "mono", render: (s) => s.symbol }, { label: "Significado", render: (s) => s.meaning },
      { label: "Tratamento", render: (s) => s.treatment },
    ], B.symbols);
    table($("table-dictionary"), [
      { label: "Campo", cls: "mono", render: (d) => d.field }, { label: "Tipo", cls: "mono", render: (d) => d.type },
      { label: "Descrição", render: (d) => d.description }, { label: "Origem", render: (d) => d.origin },
    ], B.dictionary);
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

  function sparkline(points) {
    const W = 120, H = 34, years = [Math.min(2015, ...points.map((p) => p.year)), 2024];
    const vals = points.flatMap((p) => [p.lo ?? p.e, p.hi ?? p.e]);
    const lo = Math.min(...vals), hi = Math.max(...vals), span = hi - lo || 1;
    const x = (yr) => 4 + ((yr - years[0]) / (years[1] - years[0])) * (W - 8);
    const y = (v) => 4 + (1 - (v - lo) / span) * (H - 8);
    const root = svg("svg", { viewBox: `0 0 ${W} ${H}`, "aria-hidden": "true" });
    if (points.length > 1) {
      root.append(svg("path", { class: "band", d: points.map((p, j) => `${j ? "L" : "M"}${x(p.year)},${y(p.hi)}`).join("") +
        points.slice().reverse().map((p) => `L${x(p.year)},${y(p.lo)}`).join("") + "Z" }));
      root.append(svg("path", { class: "ln", d: points.map((p, j) => `${j ? "L" : "M"}${x(p.year)},${y(p.e)}`).join("") }));
    }
    points.forEach((p) => root.append(svg("circle", { cx: x(p.year), cy: y(p.e), r: 3 })));
    return el("span", { class: "spark" }, root);
  }

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
    const n = $("notice");
    try { await navigator.clipboard.writeText(text); n.textContent = "CSV da seleção copiado para a área de transferência."; }
    catch (e) {
      const ta = $("copy-buffer"); ta.value = text; ta.select();
      n.textContent = "Não foi possível copiar automaticamente; o conteúdo foi selecionado — use Ctrl+C.";
    }
    n.hidden = false;
  }

  // ------------------------------------------------------------------ navegação
  function setPage(page) {
    state.page = page;
    document.querySelectorAll(".tabs [role=tab]").forEach((b) => b.setAttribute("aria-selected", String(b.dataset.page === page)));
    document.querySelectorAll(".page").forEach((p) => { p.hidden = p.id !== `page-${page}`; });
    try { history.replaceState(null, "", "#" + page); } catch (e) { /* hash opcional */ }
    renderPage();
  }
  function renderPage() {
    hideTip();
    if (state.page === "overview") {
      renderEditionSwitch(); renderMap(); renderHeroSide(); renderRankTable(); renderCategories(); renderBreakdown(); renderDefinition(); renderCoverage();
    } else if (state.page === "territory") { renderRanking(); renderTerritoryTable(); }
    else if (state.page === "history") { renderMicro(); renderOfficial(); renderHistory(); renderComparability(); }
    else if (state.page === "quality") renderQuality();
    else if (state.page === "about") renderAbout();
  }
  function update(changed) { syncFilters(changed); renderPage(); }

  async function boot() {
    try {
      const res = await fetch("data/pense_bundle.json", { cache: "no-cache" });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      B = await res.json();
    } catch (e) {
      $("subtitle").textContent = "Não foi possível carregar data/pense_bundle.json. Rode a pipeline (python scripts/run_pipeline.py) e abra o painel por um servidor local: python -m http.server -d dashboard 8000.";
      return;
    }
    try { const g = await fetch("assets/geo/br_uf.json"); if (g.ok) GEO = await g.json(); } catch (e) { GEO = null; }
    try { const c = await fetch("assets/geo/capitais.json"); if (c.ok) CAPS = await c.json(); } catch (e) { CAPS = null; }
    prepare();
    microPrepare();
    const sub = $("subtitle");
    sub.textContent = `Estimativas publicadas pelo IBGE (PeNSE) · ${nf0.format(B.meta.n_observations)} observações extraídas e validadas pela pipeline v${B.meta.pipeline_version} · `;
    sub.append(el("code", { text: "sha256 " + B.meta.content_sha256.slice(0, 12) }));
    const eds = editions().map(([, y]) => y).sort().join(", ");
    $("rail-foot").append(`Fonte: IBGE, PeNSE ${eds}. Cada edição fica separada; base gerada automaticamente, nenhum valor digitado à mão. Malha das UFs: geodata-br (CC0).`);
    const saved = recall("pense-filters");
    if (saved) { state.edition = saved.edition || ""; state.indicator = saved.indicator || ""; }
    bindFilters();
    if (M) bindMicro();
    if (M && M.official) bindOfficial();
    document.querySelectorAll(".tabs [role=tab]").forEach((b) => b.addEventListener("click", () => setPage(b.dataset.page)));
    $("btn-export").addEventListener("click", doExport);
    $("btn-copy").addEventListener("click", doCopy);
    window.addEventListener("scroll", hideTip, { passive: true });
    window.addEventListener("hashchange", () => {
      const h = location.hash.slice(1);
      if (h !== state.page && ["overview", "territory", "history", "quality", "about"].includes(h)) setPage(h);
    });
    const fromHash = (location.hash || "").slice(1);
    syncFilters();
    setPage(["overview", "territory", "history", "quality", "about"].includes(fromHash) ? fromHash : "overview");
  }
  boot();
})();

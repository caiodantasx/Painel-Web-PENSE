/* Filtros da barra superior, faixa de edições e seletores de recorte territorial. */
"use strict";

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
  $("btn-reset").disabled = state.age === "Total" && state.sex === "Total" && state.dep === "Total";
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
  $("btn-reset").addEventListener("click", () => { state.age = state.sex = state.dep = "Total"; update(); });
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

function selectTerritory(code, scope) {
  state.selected = state.selected === code ? null : code;
  if (scope && state.scope !== scope) state.scope = scope;
  update();
}

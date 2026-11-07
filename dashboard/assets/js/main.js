/* Navegação entre páginas e inicialização (carrega o pacote de dados e a malha). */
"use strict";

const PAGES = ["home", "estimates", "overview", "territory", "history", "quality", "about"];

// ------------------------------------------------------------------ navegação
function setPage(page) {
  state.page = page;
  document.querySelectorAll(".tabs [role=tab]").forEach((b) => {
    const on = b.dataset.page === page;
    b.setAttribute("aria-selected", String(on));
    b.tabIndex = on ? 0 : -1;
  });
  document.querySelectorAll(".page").forEach((p) => { p.hidden = p.id !== `page-${page}`; });
  document.body.dataset.page = page;   // filtros detalhados, glossário e exportação só nas páginas de detalhe
  try { history.replaceState(null, "", "#" + page); } catch (e) { /* hash opcional */ }
  renderPage();
}
function renderPage() {
  hideTip();
  if (state.page === "home") renderHome();
  else if (state.page === "estimates") renderEstimates();
  else if (state.page === "overview") {
    renderEditionSwitch(); renderMap(); renderHeroSide(); renderRankTable(); renderCategories(); renderBreakdown(); renderDefinition(); renderCoverage();
  } else if (state.page === "territory") { renderRanking(); renderTerritoryTable(); }
  else if (state.page === "history") { renderMicro(); renderOfficial(); renderHistory(); renderComparability(); }
  else if (state.page === "quality") renderQuality();
  else if (state.page === "about") renderAbout();
}

// As barras crescem só quando o dado exibido muda (indicador, recorte, território), não a cada clique de seleção.
let lastDataKey = "", animTimer = 0;
function update(changed) {
  syncFilters(changed);
  const key = [state.measure, state.age, state.sex, state.dep, state.scope].join("|");
  if (key !== lastDataKey) animateNext();
  lastDataKey = key;
  renderPage();
}
function animateNext() {
  const root = document.documentElement;
  root.dataset.anim = "on";
  clearTimeout(animTimer);
  animTimer = setTimeout(() => { delete root.dataset.anim; }, 900);
}

// Setas do teclado entre as abas (padrão WAI-ARIA de tablist).
function bindTabs() {
  const tabs = [...document.querySelectorAll(".tabs [role=tab]")];
  tabs.forEach((b, i) => {
    b.addEventListener("click", () => setPage(b.dataset.page));
    b.addEventListener("keydown", (e) => {
      const step = { ArrowRight: 1, ArrowLeft: -1 }[e.key];
      const to = step ? tabs[(i + step + tabs.length) % tabs.length] : e.key === "Home" ? tabs[0] : e.key === "End" ? tabs[tabs.length - 1] : null;
      if (!to) return;
      e.preventDefault();
      to.focus();
      setPage(to.dataset.page);
    });
  });
}

// ------------------------------------------------------------------ tema (escuro é o padrão do projeto)
function applyTheme(theme) {
  document.documentElement.dataset.theme = theme;
  const b = $("btn-theme");
  const toLight = theme !== "light";
  b.setAttribute("aria-label", toLight ? "Usar tema claro" : "Usar tema escuro");
  b.title = b.getAttribute("aria-label");
  b.setAttribute("aria-pressed", String(theme === "light"));
}
function bindTheme() {
  applyTheme(recall("pense-theme") === "light" ? "light" : "dark");
  $("btn-theme").addEventListener("click", () => {
    const next = document.documentElement.dataset.theme === "light" ? "dark" : "light";
    applyTheme(next);
    store("pense-theme", next);
    if (B) renderPage();   // a legenda do mapa descreve a rampa de cores, que inverte entre os temas
  });
}

// ------------------------------------------------------------------ carregamento
function setLoading(msg, failed) {
  const box = $("boot");
  document.body.classList.toggle("is-loading", !!msg);
  box.hidden = !msg;
  box.classList.toggle("failed", !!failed);
  if (msg) $("boot-msg").textContent = msg;
}

async function boot() {
  bindTheme();
  setLoading("Carregando a base processada…");
  try {
    const res = await fetch("data/pense_bundle.json", { cache: "no-cache" });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    B = await res.json();
  } catch (e) {
    const msg = "Não foi possível carregar data/pense_bundle.json. Rode a pipeline (python scripts/run_pipeline.py) e abra o painel por um servidor local: python -m http.server -d dashboard 8000.";
    setLoading(msg, true);
    $("subtitle").textContent = msg;
    return;
  }
  try { const g = await fetch("assets/geo/br_uf.json"); if (g.ok) GEO = await g.json(); } catch (e) { GEO = null; }
  try { const c = await fetch("assets/geo/capitais.json"); if (c.ok) CAPS = await c.json(); } catch (e) { CAPS = null; }
  prepare();
  microPrepare();
  homePrepare();
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
  bindTabs();
  $("btn-export").addEventListener("click", doExport);
  $("btn-copy").addEventListener("click", doCopy);
  window.addEventListener("scroll", hideTip, { passive: true });
  window.addEventListener("hashchange", () => {
    const h = location.hash.slice(1);
    if (h !== state.page && PAGES.includes(h)) setPage(h);
  });
  const fromHash = (location.hash || "").slice(1);
  syncFilters();
  setLoading("");
  animateNext();
  document.querySelectorAll("[data-goto]").forEach((b) => b.addEventListener("click", () => { setPage(b.dataset.goto); window.scrollTo(0, 0); }));
  setPage(PAGES.includes(fromHash) ? fromHash : "home");
}
boot();

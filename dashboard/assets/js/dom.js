/* Utilidades de DOM: criação de elementos HTML/SVG, chips, ajuda “?”, tooltip e tabelas. */
"use strict";

const $ = (id) => document.getElementById(id);

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

const changeChip = (status) => chip(status || "NAO_SIGNIFICATIVA", CHANGE_LABEL);
const confirmed = (status) => status === "SIGNIFICATIVA_5PCT_COM_DECISAO";

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

function chip(code, map) {
  const [label, cls] = (map || STATUS_LABEL)[code] || [code, "neutral"];
  return el("span", { class: `chip ${cls}`, text: label });
}
function clear(node) { while (node.firstChild) node.removeChild(node.firstChild); return node; }

function store(key, val) { try { localStorage.setItem(key, JSON.stringify(val)); } catch (e) { /* armazenamento opcional */ } }
function recall(key) { try { return JSON.parse(localStorage.getItem(key) || "null"); } catch (e) { return null; } }

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

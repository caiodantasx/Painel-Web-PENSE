/* Formatação de números (pt-BR), intervalos de confiança e escalas dos gráficos. */
"use strict";

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

const isPct = (m) => m.unit === "%";
function fmt(v, m) {
  if (v === null || v === undefined) return "—";
  return isPct(m) ? nf1.format(v) + "%" : nf0.format(v);
}

function fmtCI(r, m) {
  if (r.lo === null || r.hi === null) return "—";
  const f = (v) => (isPct(m) ? nf1.format(v) + "%" : nf0.format(v));
  return `${f(r.lo)} a ${f(r.hi)}`;
}

function precision(cv) {
  if (cv === null || cv === undefined || cv === "") return null;
  return cv < 15 ? ["boa", "good"] : cv < 30 ? ["razoável", "warning"] : ["baixa", "serious"];
}
function precisionText(cv) {
  const p = precision(cv);
  return p ? `Precisão ${p[0]} (CV ${nf1.format(cv)}%)` : "";
}

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

function compact(v) {
  if (v >= 1e6) return nf1.format(v / 1e6) + " mi";
  if (v >= 1e3) return nf0.format(v / 1e3) + " mil";
  return nf0.format(v);
}

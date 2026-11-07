/* Liquid Glass: o reflexo especular dos cartões acompanha o ponteiro (variáveis --mx/--my lidas pelo
 * glass.css). Só visual, sem dados. Desligado com "reduzir movimento" e em telas de toque. */
"use strict";

(function glassLight() {
  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches || !window.matchMedia("(hover: hover)").matches) return;
  let raf = 0, last = null;
  document.addEventListener("pointermove", (e) => {
    last = e;
    if (raf) return;
    raf = requestAnimationFrame(() => {
      raf = 0;
      const card = last.target.closest && last.target.closest(".panel, .h-card");
      if (!card) return;
      const r = card.getBoundingClientRect();
      card.style.setProperty("--mx", `${last.clientX - r.left}px`);
      card.style.setProperty("--my", `${last.clientY - r.top}px`);
    });
  }, { passive: true });
})();

"""Seleção do adaptador por evidência estrutural (nunca por nome de arquivo)."""
from __future__ import annotations

from dataclasses import dataclass

from .base import BaseAdapter, Detection, SheetContext
from .families import ALL_ADAPTERS

MIN_SCORE = 0.7
AMBIGUITY_MARGIN = 0.1


@dataclass
class Selection:
    adapter: BaseAdapter | None
    detection: Detection | None
    candidates: list[tuple[str, float]]
    reason: str


def select_adapter(ctx: SheetContext, adapters: list[BaseAdapter] | None = None) -> Selection:
    scored = []
    for ad in adapters or ALL_ADAPTERS:
        det = ad.detect(ctx)
        scored.append((ad, det))
    scored.sort(key=lambda x: x[1].score, reverse=True)
    cands = [(a.family_id, round(d.score, 2)) for a, d in scored]
    best, det = scored[0]
    if det.score < MIN_SCORE:
        return Selection(None, det, cands, f"nenhuma família atingiu {MIN_SCORE} (melhor: {best.family_id})")
    if len(scored) > 1 and det.score - scored[1][1].score < AMBIGUITY_MARGIN:
        return Selection(None, det, cands, f"ambiguidade entre {best.family_id} e {scored[1][0].family_id}")
    return Selection(best, det, cands, "selecionado por maior evidência")

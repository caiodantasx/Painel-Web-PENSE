"""Avaliação de comparabilidade entre edições.

Fluxo:
1. ``config/comparability_candidates.csv`` lista pares *candidatos* definidos
   por pessoa (nunca gerados por semelhança de título);
2. a pipeline compara automaticamente os atributos metodológicos extraídos
   (população, período, informante, unidade, tipo de estimativa, cobertura,
   desagregações, IC/CV) e produz um status automático conservador:
   * diferença em atributo essencial -> ``NOT_COMPARABLE``;
   * nenhum impedimento encontrado    -> ``PENDING_REVIEW`` (nunca
     ``COMPARABLE`` automaticamente: falta o texto do questionário);
3. ``config/comparability_decisions.csv`` registra decisões humanas, que
   prevalecem sobre o status automático e exigem justificativa.
"""
from __future__ import annotations

from collections import defaultdict
from typing import Any

from ..models import Comparability
from ..text import slug

ESSENTIAL = [
    ("population_code", "População de referência"),
    ("reference_period_code", "Período de referência"),
    ("informant", "Informante"),
    ("unit", "Unidade"),
    ("estimate_type", "Tipo de estimativa"),
]
CONTEXTUAL = [
    ("reference_period", "Redação do período"),
    ("territory_types", "Cobertura territorial"),
    ("sexes", "Desagregação por sexo"),
    ("admin_dependencies", "Desagregação por dependência administrativa"),
    ("age_groups", "Grupos de idade"),
    ("confidence_levels", "Nível de confiança do IC"),
    ("has_cv", "Disponibilidade de CV"),
    ("denominators", "Denominador"),
]
_STOP = {"de", "do", "da", "dos", "das", "a", "o", "e", "em", "que", "na", "no", "por", "com", "os", "as", "ou", "se"}


def _profile(recs: list[dict[str, Any]]) -> dict[str, Any]:
    f = recs[0]
    return {
        "population_code": f["population_code"],
        "population": f["population"],
        "reference_period": f["reference_period"],
        "reference_period_code": f.get("reference_period_code", ""),
        "informant": f["informant"],
        "unit": f["unit"],
        "estimate_type": f["estimate_type"],
        "statement": f["indicator_definition"],
        "territory_types": "|".join(sorted({r["territory_type"] for r in recs if r["territory_type"]})),
        "sexes": "|".join(sorted({r["sex"] for r in recs})),
        "admin_dependencies": "|".join(sorted({r["admin_dependency"] for r in recs})),
        "age_groups": "|".join(sorted({r["age_group"] for r in recs})),
        "confidence_levels": "|".join(sorted({str(r["confidence_level"]) for r in recs if r.get("confidence_level")})),
        "has_cv": str(any(r.get("coefficient_of_variation") is not None for r in recs)),
        "denominators": "|".join(sorted({r["denominator"] for r in recs})),
        "edition_year": f["edition_year"],
        "n": len(recs),
    }


def _similarity(a: str, b: str) -> float:
    ta = {w for w in slug(a).split() if w not in _STOP}
    tb = {w for w in slug(b).split() if w not in _STOP}
    return round(len(ta & tb) / len(ta | tb), 3) if ta | tb else 0.0


def evaluate(records: list[dict[str, Any]], candidates: list[dict[str, str]],
             decisions: list[dict[str, str]]) -> list[dict[str, Any]]:
    by_measure: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for r in records:
        if r.get("record_kind", "estimate") == "estimate":
            by_measure[(r["indicator_id"], r["response_category"], r["unit"])].append(r)
    dec_index = {(d["concept_id"], d["left_indicator_id"], d["left_category"], d["right_indicator_id"],
                  d["right_category"]): d for d in decisions}
    out: list[dict[str, Any]] = []
    for cand in candidates:
        unit = cand.get("unit") or "%"
        rights = ([k for k in by_measure if k[0] == cand["right_indicator_id"] and k[2] == unit]
                  if cand["right_category"] == "*" else [(cand["right_indicator_id"], cand["right_category"], unit)])
        for right_key in sorted(rights):
            # "*" dos dois lados: pareia categoria com categoria de mesmo nome (ex.: 17.1 de 2019 × 2024)
            left_cat = right_key[1] if cand["left_category"] == "*" else cand["left_category"]
            left_key = (cand["left_indicator_id"], left_cat, unit)
            if cand["left_category"] == "*" and left_key not in by_measure:
                continue
            out.append(_evaluate_pair(cand, left_key, right_key, by_measure, dec_index))
    return out


def _evaluate_pair(cand: dict[str, str], left_key: tuple[str, str, str], right_key: tuple[str, str, str],
                   by_measure: dict[tuple[str, str, str], list[dict[str, Any]]],
                   dec_index: dict[tuple[str, ...], dict[str, str]]) -> dict[str, Any]:
    row: dict[str, Any] = {
        "concept_id": cand["concept_id"],
        "left_indicator_id": left_key[0], "left_category": left_key[1],
        "right_indicator_id": right_key[0], "right_category": right_key[1], "unit": left_key[2],
        "candidate_reason": cand["candidate_reason"],
    }
    lrec, rrec = by_measure.get(left_key), by_measure.get(right_key)
    if not lrec or not rrec:
        missing = "esquerda" if not lrec else "direita"
        row.update(auto_status=Comparability.PENDING_REVIEW.value,
                   auto_justification=f"Medida da {missing} não encontrada nos dados extraídos.",
                   differences="", contextual_differences="", statement_similarity="")
    else:
        lp, rp = _profile(lrec), _profile(rrec)
        shown = {"population_code": "population", "reference_period_code": "reference_period"}
        diffs = [f"{label}: '{lp[shown.get(k, k)]}' × '{rp[shown.get(k, k)]}'" for k, label in ESSENTIAL if lp[k] != rp[k]]
        ctx = [f"{label}: '{lp[k]}' × '{rp[k]}'" for k, label in CONTEXTUAL if lp[k] != rp[k]]
        if diffs:
            status = Comparability.NOT_COMPARABLE.value
            just = ("Diferença em atributo metodológico essencial; as estimativas não medem a mesma "
                    "quantidade e não devem compor uma série. " + "; ".join(diffs))
        else:
            status = Comparability.PENDING_REVIEW.value
            just = ("Nenhum impedimento encontrado nos atributos extraídos. Exige revisão do texto das "
                    "perguntas e das notas metodológicas antes de qualquer decisão.")
        row.update(
            auto_status=status, auto_justification=just, differences="; ".join(diffs),
            contextual_differences="; ".join(ctx),
            statement_similarity=_similarity(lp["statement"], rp["statement"]),
            left_year=lp["edition_year"], right_year=rp["edition_year"],
            left_population=lp["population"], right_population=rp["population"],
            left_period=lp["reference_period"], right_period=rp["reference_period"],
            left_coverage=lp["territory_types"], right_coverage=rp["territory_types"],
            left_statement=lp["statement"], right_statement=rp["statement"],
        )
    dkey = (cand["concept_id"], left_key[0], left_key[1], right_key[0], right_key[1])
    dec = dec_index.get(dkey)
    if dec and dec.get("final_status") in {c.value for c in Comparability}:
        if not dec.get("justification", "").strip():
            row.update(final_status=Comparability.PENDING_REVIEW.value,
                       final_justification="Decisão humana registrada sem justificativa — ignorada.",
                       decision_source="config (inválida)")
        else:
            row.update(final_status=dec["final_status"], final_justification=dec["justification"],
                       decision_source=f"decisão humana ({dec.get('reviewer', '')}, {dec.get('decision_date', '')})",
                       evidence_reference=dec.get("evidence_reference", ""))
    else:
        row.update(final_status=row["auto_status"], final_justification=row["auto_justification"],
                   decision_source="regra automática conservadora")
    row["statement_similarity_note"] = "Semelhança de texto é apenas evidência auxiliar; não decide comparabilidade."
    return row


def status_index(rows: list[dict[str, Any]]) -> dict[tuple[str, str], str]:
    """(indicator_id, categoria) -> status mais favorável encontrado (para o catálogo)."""
    order = {c.value: i for i, c in enumerate([Comparability.NOT_COMPARABLE, Comparability.PENDING_REVIEW,
                                               Comparability.COMPARABLE_WITH_CAVEATS, Comparability.COMPARABLE])}
    idx: dict[tuple[str, str], str] = {}
    for r in rows:
        for side in ("left", "right"):
            k = (r[f"{side}_indicator_id"], r[f"{side}_category"])
            cur = idx.get(k)
            if cur is None or order[r["final_status"]] > order[cur]:
                idx[k] = r["final_status"]
    return idx


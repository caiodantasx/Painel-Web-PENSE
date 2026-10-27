"""Construção de séries históricas — somente para pares aprovados.

* Só entram pares cujo status final é ``COMPARABLE`` ou
  ``COMPARABLE_WITH_CAVEATS`` (decisão humana com justificativa);
* uma observação por ano × série × território × desagregação;
* estimativas e IC publicados são preservados;
* variações absoluta (p.p.) e relativa (%) entre pontos consecutivos são
  descritivas — não indicam significância estatística;
* média aritmética das estimativas anuais só é calculada se habilitada em
  ``settings.toml`` e é rotulada como estatística descritiva.
"""
from __future__ import annotations

from collections import defaultdict
from typing import Any

from ..models import Comparability
from ..text import code_from_label

APPROVED = {Comparability.COMPARABLE.value, Comparability.COMPARABLE_WITH_CAVEATS.value}
SERIES_NOTE = ("Variações calculadas entre estimativas pontuais publicadas; não constituem teste de "
               "significância nem estimativa de tendência. Consulte os IC de cada ano.")


def build_series(records: list[dict[str, Any]], comparability: list[dict[str, Any]], editions: list[str],
                 allow_mean: bool = False) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    """Retorna (pontos, resumo por série, status por par candidato)."""
    canon = [r for r in records if r.get("approved_for_analysis") and not r.get("analytical_duplicate_of")
             and r.get("record_kind", "estimate") == "estimate"]
    by_measure: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for r in canon:
        by_measure[(r["indicator_id"], r["response_category"], r["unit"])].append(r)

    points: list[dict[str, Any]] = []
    status_rows: list[dict[str, Any]] = []
    for pair in comparability:
        included = pair["final_status"] in APPROVED
        status_rows.append({
            "concept_id": pair["concept_id"], "left_indicator_id": pair["left_indicator_id"],
            "left_category": pair["left_category"], "right_indicator_id": pair["right_indicator_id"],
            "right_category": pair["right_category"], "final_status": pair["final_status"],
            "included_in_series": included,
            "reason": ("Par aprovado: " if included else "Excluído da série: ") + pair["final_justification"],
        })
        if not included:
            continue
        cat_code = code_from_label(pair["right_category"] or pair["left_category"] or "geral", 32)
        series_id = f"{pair['concept_id']}__{cat_code}"
        sides = [(pair["left_indicator_id"], pair["left_category"]), (pair["right_indicator_id"], pair["right_category"])]
        by_key: dict[tuple[Any, ...], dict[int, dict[str, Any]]] = defaultdict(dict)
        for ind, cat in sides:
            for r in by_measure.get((ind, cat, pair["unit"]), []):
                k = (r["territory_code"], r["age_group"], r["sex"], r["admin_dependency"])
                by_key[k][int(r["edition_year"])] = r
        for k, by_year in by_key.items():
            if len(by_year) < 2:
                continue  # só há série quando o mesmo recorte existe em 2+ edições
            for year in sorted(by_year):
                r = by_year[year]
                points.append({
                    "series_id": series_id, "concept_id": pair["concept_id"],
                    "comparability_status": pair["final_status"], "comparability_note": pair["final_justification"],
                    "territory_code": k[0], "territory_name": r["territory_name"], "territory_type": r["territory_type"],
                    "age_group": k[1], "sex": k[2], "admin_dependency": k[3],
                    "year": year, "edition_id": r["edition_id"], "indicator_id": r["indicator_id"],
                    "response_category": r["response_category"], "unit": r["unit"],
                    "estimate": r["estimate"], "ci_lower": r["ci_lower"], "ci_upper": r["ci_upper"],
                    "coefficient_of_variation": r.get("coefficient_of_variation"),
                    "observation_id": r["observation_id"], "source_file": r["source_file"],
                    "source_cell": f"{r['source_sheet']}!{r['source_cell']}",
                })
    points = _dedupe(points)
    _add_changes(points)
    summary = _summarize(points, editions, allow_mean)
    return points, summary, status_rows


def _dedupe(points: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen, out = set(), []
    for p in points:
        k = (p["series_id"], p["territory_code"], p["age_group"], p["sex"], p["admin_dependency"], p["year"])
        if k not in seen:
            seen.add(k)
            out.append(p)
    return sorted(out, key=lambda p: (p["series_id"], p["territory_code"], p["age_group"], p["sex"],
                                      p["admin_dependency"], p["year"]))


def _add_changes(points: list[dict[str, Any]]) -> None:
    prev: dict[tuple[Any, ...], dict[str, Any]] = {}
    for p in points:
        k = (p["series_id"], p["territory_code"], p["age_group"], p["sex"], p["admin_dependency"])
        q = prev.get(k)
        p["previous_year"] = q["year"] if q else None
        if q and q["estimate"] is not None and p["estimate"] is not None:
            p["abs_change"] = p["estimate"] - q["estimate"]
            p["abs_change_unit"] = "p.p." if p["unit"] == "%" else p["unit"]
            p["rel_change_pct"] = (p["estimate"] / q["estimate"] - 1) * 100 if q["estimate"] > 0 else None
        else:
            p["abs_change"] = p["rel_change_pct"] = None
            p["abs_change_unit"] = ""
        p["interpretation_note"] = SERIES_NOTE
        prev[k] = p


def _summarize(points: list[dict[str, Any]], editions: list[str], allow_mean: bool) -> list[dict[str, Any]]:
    groups: dict[tuple[Any, ...], list[dict[str, Any]]] = defaultdict(list)
    for p in points:
        groups[(p["series_id"], p["territory_code"], p["age_group"], p["sex"], p["admin_dependency"])].append(p)
    out = []
    for k, pts in groups.items():
        present = {p["edition_id"] for p in pts}
        row = {
            "series_id": k[0], "territory_code": k[1], "age_group": k[2], "sex": k[3], "admin_dependency": k[4],
            "n_points": len(pts), "years": "|".join(str(p["year"]) for p in pts),
            "first_year": pts[0]["year"], "last_year": pts[-1]["year"],
            "editions_without_point": "|".join(e for e in editions if e not in present),
            "comparability_status": pts[0]["comparability_status"],
            "interpretation_note": SERIES_NOTE,
        }
        if allow_mean:
            vals = [p["estimate"] for p in pts if p["estimate"] is not None]
            row["descriptive_mean"] = sum(vals) / len(vals) if vals else None
            row["descriptive_mean_note"] = ("Média aritmética simples das estimativas anuais — estatística "
                                            "descritiva; NÃO é estimativa combinada nem evidência de tendência.")
        out.append(row)
    return out

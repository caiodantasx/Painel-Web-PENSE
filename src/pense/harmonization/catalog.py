"""Catálogo de indicadores: uma linha por indicador × categoria × unidade."""
from __future__ import annotations

from collections import defaultdict
from typing import Any

from ..text import code_from_label

CATALOG_KEY = ("indicator_id", "category_group", "response_category", "unit")


def indicator_key(rec: dict[str, Any]) -> tuple[Any, ...]:
    return tuple(rec.get(k) for k in CATALOG_KEY)


def measure_id(rec: dict[str, Any]) -> str:
    """Id estável de uma medida: indicador + categoria + unidade."""
    parts = [rec["indicator_id"]]
    if rec.get("category_group"):
        parts.append(code_from_label(rec["category_group"], 24))
    parts.append(rec.get("category_code") or "geral")
    parts.append("pct" if rec.get("unit") == "%" else "n")
    return "__".join(parts)


def _join(values: Any) -> str:
    return " | ".join(sorted({str(v) for v in values if v not in (None, "")}))


def build_catalog(records: list[dict[str, Any]], comparability: dict[tuple[str, str], str]) -> list[dict[str, Any]]:
    groups: dict[tuple[Any, ...], list[dict[str, Any]]] = defaultdict(list)
    for r in records:
        if r.get("record_kind", "estimate") == "estimate":
            groups[indicator_key(r)].append(r)
    rows = []
    for _key, recs in sorted(groups.items(), key=lambda kv: [str(x) for x in kv[0]]):
        f = recs[0]
        mid = measure_id(f)
        approved = [r for r in recs if r.get("approved_for_analysis") and not r.get("analytical_duplicate_of")]
        rows.append({
            "measure_id": mid,
            "indicator_id": f["indicator_id"],
            "edition_id": f["edition_id"],
            "edition_year": f["edition_year"],
            "theme_id": f["theme_id"],
            "table_family_id": f["table_family_id"],
            "table_ids": _join(r["table_id"] for r in recs),
            "original_code": f["table_family_id"],
            "original_name": f["indicator_name"],
            "canonical_name": f["indicator_name"] + (f" — {f['response_category']}" if f["response_category"] else ""),
            "definition": f["indicator_definition"],
            "question_text": f["question_text"],
            "population": f["population"],
            "denominator": f["denominator"],
            "denominator_status": f["denominator_status"],
            "unit": f["unit"],
            "estimate_type": f["estimate_type"],
            "reference_period": f["reference_period"],
            "informant": f["informant"],
            "category_group": f["category_group"],
            "response_category": f["response_category"],
            "age_groups": _join(r["age_group"] for r in recs),
            "sexes": _join(r["sex"] for r in recs),
            "admin_dependencies": _join(r["admin_dependency"] for r in recs),
            "territory_types": _join(r["territory_type"] for r in recs),
            "n_territories": len({r["territory_code"] for r in recs if r["territory_code"]}),
            "has_ci": any(r.get("ci_lower") is not None for r in recs),
            "has_cv": any(r.get("coefficient_of_variation") is not None for r in recs),
            "multi_response": bool(f.get("multi_response")),
            "n_observations": len(recs),
            "n_approved_canonical": len(approved),
            "source_files": _join(r["source_file"] for r in recs),
            "source_sheets": _join(r["source_sheet"] for r in recs),
            "methodological_note": f["methodological_note"],
            "comparability_status": comparability.get((f["indicator_id"], f["response_category"]),
                                                      "SEM_CORRESPONDENTE_IDENTIFICADO"),
        })
    return rows

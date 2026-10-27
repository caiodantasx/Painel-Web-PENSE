"""Pacote de dados do dashboard (``dashboard/data/pense_bundle.json``).

Formato colunar com dicionários de índices para reduzir o tamanho. O
JavaScript não contém nenhuma estimativa: tudo vem deste arquivo, gerado pela
pipeline a cada execução.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any

from ..harmonization.catalog import indicator_key, measure_id
from .reading import SOURCE_NOTE, reading
from ..standardization.schema import CANONICAL_SCHEMA

STATUS_ORDER = ["VALID", "VALID_WITH_WARNINGS", "REVIEW_REQUIRED", "ERROR", "NOT_AVAILABLE"]


def _round(v: Any, nd: int = 6) -> Any:
    return None if v is None else round(float(v), nd)


def build_bundle(records: list[dict[str, Any]], catalog: list[dict[str, Any]], comparability: list[dict[str, Any]],
                 series_points: list[dict[str, Any]], series_status: list[dict[str, Any]], territories: list[dict[str, str]],
                 issues_summary: list[dict[str, Any]], editions: dict[str, dict[str, str]], version: str,
                 symbols: dict[str, dict[str, str]], labels: dict[str, dict[str, str]] | None = None) -> dict[str, Any]:
    labels = labels or {}
    canon = [r for r in records if not r.get("analytical_duplicate_of") and r.get("record_kind", "estimate") == "estimate"]
    cat_by_key = {(c["indicator_id"], c["category_group"], c["response_category"], c["unit"]): c for c in catalog}
    measures: list[dict[str, Any]] = []
    m_index: dict[str, int] = {}
    for r in canon:
        mid = measure_id(r)
        if mid in m_index:
            continue
        c = cat_by_key.get(indicator_key(r), {})
        m_index[mid] = len(measures)
        measures.append({
            "id": mid, "indicator_id": r["indicator_id"], "edition_id": r["edition_id"], "year": r["edition_year"],
            "theme_id": r["theme_id"], "table_family_id": r["table_family_id"], "name": r["indicator_name"],
            "definition": r["indicator_definition"], "category": r["response_category"],
            "category_group": r["category_group"], "unit": r["unit"], "estimate_type": r["estimate_type"],
            "population": r["population"], "denominator": r["denominator"],
            "denominator_status": r["denominator_status"], "period": r["reference_period"],
            "informant": r["informant"], "multi_response": bool(r.get("multi_response")),
            "note": r["methodological_note"], "comparability_status": c.get("comparability_status", ""),
            "tables": c.get("table_ids", r["table_id"]), "question_text": r["question_text"],
            "short_label": labels.get(r["indicator_id"], {}).get("short_label", "")
                           or (r["indicator_name"][:80] + ("…" if len(r["indicator_name"]) > 80 else "")),
            "theme_label": labels.get(r["indicator_id"], {}).get("theme_label", f"Tema {r['theme_id']}"),
        })
        rd = reading(measures[-1])
        measures[-1].update({"reading": rd["reading"], "reading_base": rd["base"], "reading_respondent": rd["respondent"],
                             "unit_label": rd["unit_label"],
                             "explain": {k: rd.get(k, "") for k in ("count_base", "situation", "who", "period", "not_this")}})
    # tabelas com vários anos na mesma medida (série oficial do 9º ano) não entram nos mapas de uma edição
    years_by_measure: dict[str, set] = {}
    for r in canon:
        years_by_measure.setdefault(measure_id(r), set()).add(r["edition_year"])
    for mm in measures:
        mm["multi_year"] = len(years_by_measure.get(mm["id"], ())) > 1
    terr_codes = sorted({r["territory_code"] for r in canon if r["territory_code"]})
    terr_meta = {t["territory_code"]: t for t in territories}
    t_index = {c: i for i, c in enumerate(terr_codes)}
    dims_vals = {d: sorted({r[d] for r in canon}) for d in ("age_group", "sex", "admin_dependency")}
    d_index = {d: {v: i for i, v in enumerate(vals)} for d, vals in dims_vals.items()}
    sources = sorted({f"{r['source_file']}::{r['source_sheet']}" for r in canon})
    s_index = {s: i for i, s in enumerate(sources)}
    cols: dict[str, list[Any]] = {k: [] for k in ("m", "t", "a", "s", "d", "e", "lo", "hi", "cv", "st", "src",
                                                  "cell", "sym", "rules", "id")}
    for r in sorted(canon, key=lambda r: (m_index[measure_id(r)], r["territory_code"] or "~", r["age_group"],
                                          r["sex"], r["admin_dependency"])):
        if not r["territory_code"]:
            continue
        cols["m"].append(m_index[measure_id(r)])
        cols["t"].append(t_index[r["territory_code"]])
        cols["a"].append(d_index["age_group"][r["age_group"]])
        cols["s"].append(d_index["sex"][r["sex"]])
        cols["d"].append(d_index["admin_dependency"][r["admin_dependency"]])
        cols["e"].append(_round(r.get("estimate")))
        cols["lo"].append(_round(r.get("ci_lower")))
        cols["hi"].append(_round(r.get("ci_upper")))
        cols["cv"].append(_round(r.get("coefficient_of_variation"), 3))
        cols["st"].append(STATUS_ORDER.index(r["validation_status"]))
        cols["src"].append(s_index[f"{r['source_file']}::{r['source_sheet']}"])
        cols["cell"].append(r["source_cell"])
        cols["sym"].append(r.get("estimate_symbol") or "")
        cols["rules"].append(r.get("issue_rules") or "")
        cols["id"].append(r["observation_id"])
    bundle = {
        "meta": {
            "pipeline_version": version,
            "n_observations": len(cols["m"]),
            "n_measures": len(measures),
            "status_order": STATUS_ORDER,
            "editions": [dict(editions[e], label=_edition_label(editions[e])) for e in sorted(editions)],
            "source_note": SOURCE_NOTE,
            "note": ("Estimativas oficiais publicadas pelo IBGE (PeNSE), extraídas e validadas pela pipeline. "
                     "Nenhum valor é digitado manualmente no dashboard."),
        },
        "territories": [{"code": c, "name": terr_meta.get(c, {}).get("territory_name", c),
                         "type": terr_meta.get(c, {}).get("territory_type", ""),
                         "uf": terr_meta.get(c, {}).get("uf_sigla", ""),
                         "uf_code": terr_meta.get(c, {}).get("uf_code", ""),
                         "region": terr_meta.get(c, {}).get("region_code", "")} for c in terr_codes],
        "dims": dims_vals,
        "sources": sources,
        "measures": measures,
        "obs": cols,
        "comparability": comparability,
        "series": series_points,
        "series_status": series_status,
        "issues_summary": issues_summary,
        "dictionary": [{"field": f, "type": t, "description": d, "origin": o} for f, t, d, o in CANONICAL_SCHEMA],
        "symbols": list(symbols.values()),
    }
    stamp_hash(bundle)
    return bundle


def _edition_label(e: dict[str, str]) -> str:
    """Rótulo do seletor de edição: ano, amostra e população (evita dois "PeNSE 2019" iguais)."""
    pop = (e.get("target_population") or "").replace("Escolares frequentando o ", "").replace("Escolares de ", "")
    pop = pop.replace(" do ensino fundamental", "")
    eid = e.get("edition_id", "")
    if eid.startswith("PENSE_SERIE"):
        return f"Série oficial 2009–2019 · {pop} · capitais"
    sample = " · Amostra 1" if eid.endswith("_A1") else " · Amostra 2" if eid.endswith("_A2") else ""
    cov = " · capitais" if eid == "PENSE_2009" else ""
    return f"PeNSE {e.get('reference_year', '')}{sample} · {pop}{cov}"


def stamp_hash(bundle: dict[str, Any]) -> None:
    """SHA-256 do conteúdo (sem o próprio campo de hash); refeito se o pacote mudar."""
    bundle["meta"].pop("content_sha256", None)
    payload = json.dumps(bundle, ensure_ascii=False, sort_keys=True, default=str).encode()
    bundle["meta"]["content_sha256"] = hashlib.sha256(payload).hexdigest()

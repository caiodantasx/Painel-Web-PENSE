"""Normalização pós-extração.

* junta o CV publicado (abas "(CV)") às observações de estimativa, conferindo
  se a estimativa repetida na aba de CV é idêntica à da aba principal;
* deriva o erro-padrão a partir de IC simétrico — sempre marcado como
  *derivado*, nunca como publicado.
"""
from __future__ import annotations

from typing import Any

from ..models import Issue, IssueClass, Severity

KEY_FIELDS = ("edition_id", "edition_year", "table_id", "territory_code", "territory_label_original", "age_group", "sex",
              "admin_dependency", "category_group", "response_category", "unit")


def record_key(rec: dict[str, Any]) -> tuple[Any, ...]:
    return tuple(rec.get(k) for k in KEY_FIELDS)


def join_cv(estimates: list[dict[str, Any]], cv_records: list[dict[str, Any]],
            rel_tol: float = 1e-9) -> tuple[list[Issue], int]:
    """Retorna (alertas, nº de estimativas comparadas entre aba principal e aba de CV)."""
    issues: list[Issue] = []
    compared = 0
    by_key: dict[tuple[Any, ...], dict[str, Any]] = {}
    for cv in cv_records:
        k = record_key(cv)
        if k in by_key:
            issues.append(_issue("NRM002", Severity.REVIEW, IssueClass.NOT_VALIDATED,
                                 "Chave duplicada na aba de CV", cv, "Conferir a aba de CV."))
            continue
        by_key[k] = cv
    tables_with_cv = {(c["edition_id"], c["table_id"]) for c in cv_records}
    matched: set[tuple[Any, ...]] = set()
    for rec in estimates:
        k = record_key(rec)
        cv = by_key.get(k)
        if cv is None:
            if (rec["edition_id"], rec["table_id"]) in tables_with_cv:
                issues.append(_issue("NRM003", Severity.INFO, IssueClass.INFORMATIONAL,
                                     "Observação sem correspondente na aba de CV", rec,
                                     "Conferir se a aba de CV omite esta linha/coluna."))
            continue
        matched.add(k)
        rec["coefficient_of_variation"] = cv["coefficient_of_variation"]
        rec["cv_kind"] = cv.get("cv_kind", "")
        rec["cv_source"] = f"{cv['source_file']}!{cv['source_sheet']}!{cv['cv_source'].split('!')[-1]}"
        e1, e2 = rec.get("estimate"), cv.get("estimate")
        if e1 is not None and e2 is not None:
            compared += 1
            if abs(e1 - e2) > rel_tol * max(1.0, abs(e1)):
                issues.append(_issue("VAL010", Severity.ERROR, IssueClass.CONFIRMED_ERROR,
                                     f"Estimativa difere entre aba principal ({e1}) e aba de CV ({e2})", rec,
                                     "Verificar qual aba está correta na publicação oficial.",
                                     observed=f"{e1} vs {e2}"))
        elif (e1 is None) != (e2 is None):
            issues.append(_issue("VAL010", Severity.REVIEW, IssueClass.POSSIBLE_ANOMALY,
                                 "Estimativa presente em apenas uma das abas (principal/CV)", rec,
                                 "Conferir as duas abas."))
    for k, cv in by_key.items():
        if k not in matched:
            issues.append(_issue("NRM004", Severity.REVIEW, IssueClass.NOT_VALIDATED,
                                 "Linha da aba de CV sem correspondente na aba principal", cv,
                                 "Verificar rótulos de território/categoria entre as abas."))
    return issues, compared


def derive_standard_error(rec: dict[str, Any], z: float, sym_tol: float = 1e-6) -> None:
    """Erro-padrão = (LS − LI) / (2·z) somente se o IC for simétrico e não truncado."""
    est, lo, hi = rec.get("estimate"), rec.get("ci_lower"), rec.get("ci_upper")
    if est is None or lo is None or hi is None or hi <= lo:
        return
    scale = max(1.0, abs(est))
    if abs((est - lo) - (hi - est)) > sym_tol * scale:
        return
    if rec.get("unit") == "%" and (lo <= 0 or hi >= 100):
        return
    rec["standard_error"] = (hi - lo) / (2 * z)
    rec["standard_error_method"] = f"derivado: (LS−LI)/(2×{z:.2f}); IC simétrico e não truncado"


def _issue(rule: str, sev: Severity, cls: IssueClass, msg: str, rec: dict[str, Any], action: str,
           observed: str = "") -> Issue:
    return Issue(rule_id=rule, severity=sev.value, issue_class=cls.value, message=msg, recommended_action=action,
                 source_file=rec.get("source_file", ""), source_sheet=rec.get("source_sheet", ""),
                 source_cell=rec.get("source_cell", ""), observation_id=rec.get("observation_id", ""),
                 table_id=rec.get("table_id", ""), observed_value=observed or str(rec.get("estimate")),
                 context=f"{rec.get('territory_name')} | {rec.get('response_category')}", stage="normalization")

"""Estimação com microdados: estimador de desenho, série harmonizada e validação contra o publicado."""
import csv
import math
from pathlib import Path

import numpy as np
import pytest

from pense.microdata.estimator import DesignArrays, ratio
from pense.microdata.series import assess_comparability, build_series

ROOT = Path(__file__).resolve().parents[1]


def test_ratio_equals_closed_form_for_simple_random_sample():
    # um estrato, cada aluno é a própria UPA, pesos iguais: V(p) = p(1-p)/(n-1)
    y = np.array([1, 0, 0, 1, 0, 1, 0, 0, 0, 1])
    n = len(y)
    d = DesignArrays.build(np.full(n, 3.0), np.zeros(n), np.arange(n))
    e = ratio(d, y.astype(bool), np.ones(n, dtype=bool))
    p = y.mean()
    assert e.p == pytest.approx(p)
    assert e.se == pytest.approx(math.sqrt(p * (1 - p) / (n - 1)))
    assert e.ci_lower == pytest.approx(max(0, p - 1.959963984540054 * e.se))


def test_ratio_domain_and_empty_domain():
    w = np.array([1.0, 2.0, 1.0, 4.0])
    d = DesignArrays.build(w, [1, 1, 2, 2], ["a", "b", "c", "d"])
    num = np.array([1, 0, 1, 0], dtype=bool)
    dom = np.array([1, 1, 0, 0], dtype=bool)
    e = ratio(d, num & dom, dom)
    assert e.p == pytest.approx(1 / 3) and e.n_den == 2
    assert ratio(d, num & False, np.zeros(4, dtype=bool)) is None


def test_poststratification_reduces_variance_when_strata_explain_outcome():
    rng = np.random.default_rng(1)
    g = np.repeat([0, 1], 200)
    y = (rng.random(400) < np.where(g == 0, 0.1, 0.6)).astype(bool)
    d0 = DesignArrays.build(np.ones(400), np.zeros(400), np.arange(400))
    d1 = DesignArrays.build(np.ones(400), np.zeros(400), np.arange(400), g)
    a, b = ratio(d0, y, np.ones(400, dtype=bool)), ratio(d1, y, np.ones(400, dtype=bool))
    assert a.p == pytest.approx(b.p) and b.se < a.se


def _est(key, year, e, se):
    return {"indicator_key": key, "edition_id": f"E{year}", "edition_year": str(year), "territory_code": "BR",
            "territory_name": "Brasil", "territory_type": "country", "age_group": "Total", "sex": "Total",
            "admin_dependency": "Total", "estimate": str(e), "standard_error": str(se),
            "ci_lower": str(e - 1.96 * se), "ci_upper": str(e + 1.96 * se), "low_precision": "False"}


def test_series_difference_uses_independent_samples_variance():
    comp = [{"indicator_key": "X", "final_status": "COMPARABLE_WITH_CAVEATS", "series_editions": "E2019|E2024",
             "decision_status": "PROPOSTA_AUTOMATICA"}]
    pts = build_series([_est("X", 2019, 10.0, 0.3), _est("X", 2024, 11.0, 0.4)], comp)
    last = pts[-1]
    assert last["diff_pp"] == pytest.approx(1.0)
    half = 1.959963984540054 * 0.5  # √(0,3² + 0,4²) = 0,5
    assert last["diff_ci_lower"] == pytest.approx(1.0 - half, abs=1e-4) and last["significant_5pct"] is True
    assert last["change_status"] == "SIGNIFICATIVA_SEM_DECISAO", "sem decisão registrada não há selo 'Diferença significativa a 5%'"


def test_series_excludes_not_comparable_indicators():
    comp = [{"indicator_key": "X", "final_status": "PENDING_REVIEW"}]
    assert build_series([_est("X", 2019, 10, 1), _est("X", 2024, 11, 1)], comp) == []


def test_comparability_rules():
    eds = {"A": {"year": 2019, "nonresponse_in_denominator": [9], "nonresponse_rule_status": "PENDENTE"},
           "B": {"year": 2024, "nonresponse_in_denominator": [-9], "nonresponse_rule_status": "CONFIRMADA"}}
    inds = {"SAME": {"label": "", "period": "30_DIAS", "var": "B1", "num": [1], "den": [1, 2], "editions": ["A", "B"]},
            "CHANGED": {"label": "", "period": "30_DIAS", "var_by_edition": {"A": "E1", "B": "E1A"}, "num": [1],
                        "den": [1, 2], "editions": ["A", "B"]},
            "ONLY": {"label": "", "period": "30_DIAS", "var": "B2", "num": [1], "den": [1, 2], "editions": ["B"]}}
    summ = [{"edition_id": "B", "indicator_key": "SAME", "status": "VALIDADO"},
            {"edition_id": "A", "indicator_key": "SAME", "status": "VALIDADO"}]
    out = {c["indicator_key"]: c for c in assess_comparability(inds, eds, summ, [])}
    assert out["SAME"]["final_status"] == "COMPARABLE_WITH_CAVEATS"
    assert "< 0,2 p.p." not in out["SAME"]["caveats"], "efeito de não resposta nunca é texto fixo"
    assert out["SAME"]["decision_status"] == "PROPOSTA_AUTOMATICA" and "proposta automática" in out["SAME"]["decision_source"]
    assert out["CHANGED"]["final_status"] == "PENDING_REVIEW"
    assert out["ONLY"]["final_status"] == "NOT_COMPARABLE"
    dec = [{"indicator_key": "SAME", "final_status": "COMPARABLE", "justification": "conferido no questionário",
            "evidence_reference": "dicionários 2019/2024", "reviewer": "Pesquisador", "decision_date": "2026-10-26"}]
    out = {c["indicator_key"]: c for c in assess_comparability(inds, eds, summ, dec)}
    assert out["SAME"]["final_status"] == "COMPARABLE" and "Pesquisador" in out["SAME"]["decision_source"]
    assert out["SAME"]["decision_status"] == "DECISAO_REGISTRADA"


def _summary():
    path = ROOT / "data" / "curated" / "microdata_validation_summary.csv"
    if not path.exists():
        pytest.skip("rode scripts/run_microdata.py (microdados não versionados)")
    with path.open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def test_2024_microdata_reproduce_every_published_table():
    rows = [r for r in _summary() if r["edition_id"] == "PENSE_2024"]
    assert len(rows) >= 20
    assert all(r["status"].startswith("VALIDADO") for r in rows)
    assert all(r["brasil_reproduz"] == "True" for r in rows), "Brasil, total: diferença ≤ 0,05 p.p. e IC ≤ 0,15 p.p."
    assert max(float(r["max_abs_diff_estimate_pp"]) for r in rows) < 0.3


def test_2019_reproduces_published_totals_and_explains_the_rest():
    rows = [r for r in _summary() if r["edition_id"] == "PENSE_2019"]
    tables = {r["published_table"] for r in rows}
    assert {"17.1", "17.2", "9.7", "10.7"} <= tables, "Tema 9, Tema 17 e série oficial do 9º ano"
    bad = {r["indicator_key"] for r in rows if r["status"] == "NAO_VALIDADO"}
    assert bad == {"NONO_CINTO_FRENTE_OU_TRAS"}, "única regra não reproduzida (tabela 10.3) fica fora da série"
    assert all(r["brasil_reproduz"] == "True" for r in rows if r["indicator_key"] not in bad
               and not r["indicator_key"].startswith("NONO_")), "totais do Brasil reproduzem"


def test_wording_comparison_from_dictionaries():
    from pense.microdata.dictionary import compare
    same = compare({"2019": "NOS ÚLTIMOS 30 DIAS, você esteve envolvido(a) em briga?",
                    "2024": "NOS ÚLTIMOS 30 DIAS, você esteve envolvido(a) em briga?"})
    assert same["identical"]
    diff = compare({"2019": "alguém vendendo drogas na localidade", "2024": "alguém vendendo ou usando drogas na localidade"})
    assert not diff["identical"] and "ou usando" in diff["changes"][0]


def test_changed_code_and_wording_is_not_comparable():
    eds = {"A": {"year": 2019, "nonresponse_in_denominator": [9]}, "B": {"year": 2024, "nonresponse_in_denominator": [-9]}}
    inds = {"D": {"label": "", "period": "12_MESES", "var_by_edition": {"A": "E81", "B": "E81A"}, "num": [3, 4],
                  "den": [1, 2, 3, 4], "editions": ["A", "B"]}}
    q = {"D": {"A": "alguém vendendo drogas", "B": "alguém vendendo ou usando drogas"}}
    out = assess_comparability(inds, eds, [], [], q)[0]
    assert out["final_status"] == "NOT_COMPARABLE" and "ou usando" in out["caveats"]

"""Regras de qualidade com registros sintéticos mínimos."""
import pytest

from pense.standardization.normalize import derive_standard_error
from pense.validation.rules import ValidationSettings, Validator, assign_status

SYMBOLS = {"-": {"meaning": "zero absoluto"}}
_n = 0


def rec(**kw):
    global _n
    _n += 1
    base = {
        "observation_id": f"OBS-{_n}", "edition_id": "E", "edition_year": 2024, "table_id": "1.1.1",
        "table_family_id": "1.1", "indicator_id": "E__1.1", "source_file": "f.xlsx", "source_sheet": f"S{_n}",
        "source_row": _n, "source_column": "B", "source_cell": f"B{_n}", "ci_lower_cell": f"C{_n}",
        "ci_upper_cell": f"D{_n}", "territory_code": "BR", "territory_name": "Brasil", "territory_type": "country",
        "territory_label_original": "Brasil", "region_code": "", "row_group_label": "", "age_group": "Total",
        "sex": "Total", "admin_dependency": "Total", "category_group": "", "response_category": f"cat{_n}", "unit": "%",
        "estimate_type": "percentual", "estimate": 30.0, "estimate_kind": "number", "estimate_raw": "30.0",
        "estimate_symbol": "", "ci_lower": 28.0, "ci_upper": 32.0, "coefficient_of_variation": None,
        "standard_error": None, "multi_response": False, "nonresponse_excluded": False, "extraction_flags": "",
    }
    base.update(kw)
    return base


def run(records):
    v = Validator(ValidationSettings(), SYMBOLS)
    issues = v.run(records)
    assign_status(records, issues)
    return issues


def rules(issues):
    return {i.rule_id for i in issues}


def test_valid_record_passes():
    r = rec()
    issues = run([r])
    assert not issues and r["validation_status"] == "VALID" and r["approved_for_analysis"]


def test_percent_out_of_range_is_error_but_float_artifact_is_info():
    bad, fp = rec(estimate=101.0, ci_upper=102.0), rec(estimate=100.00000000000016, ci_lower=99.9999999999, ci_upper=100.0)
    run([bad, fp])
    assert bad["validation_status"] == "ERROR" and "VAL002" in bad["issue_rules"]
    # IC [99.9999999999, 100] tem amplitude ~0 -> aviso VAL005; o artefato em si é só informativo
    assert fp["validation_status"] == "VALID_WITH_WARNINGS" and "VAL002F" in fp["issue_rules"]
    assert fp["estimate"] == 100.00000000000016, "o valor nunca é corrigido"


def test_negative_published_ci_bound_is_warning_and_preserved():
    r = rec(estimate=1.78, ci_lower=-0.247, ci_upper=3.81)
    run([r])
    assert r["validation_status"] == "VALID_WITH_WARNINGS" and r["ci_lower"] == -0.247


def test_inverted_ci_and_estimate_outside_ci():
    inv, out = rec(ci_lower=35.0, ci_upper=25.0), rec(estimate=40.0)
    run([inv, out])
    assert "VAL003" in inv["issue_rules"] and "VAL004" in out["issue_rules"]
    assert inv["validation_status"] == out["validation_status"] == "ERROR"


def test_degenerate_and_truncated_ci():
    deg, trunc = rec(estimate=0.0, ci_lower=0.0, ci_upper=0.0), rec(estimate=2.0, ci_lower=0.0, ci_upper=5.0)
    run([deg, trunc])
    assert "VAL005" in deg["issue_rules"] and deg["validation_status"] == "VALID_WITH_WARNINGS"
    assert "VAL006" in trunc["issue_rules"] and trunc["validation_status"] == "VALID"


def test_cv_high_and_cv_ci_coherence():
    ok = rec(estimate=30.0, ci_lower=28.04, ci_upper=31.96, coefficient_of_variation=3.333)
    derive_standard_error(ok, 1.959964)
    incoherent = rec(estimate=30.0, ci_lower=28.04, ci_upper=31.96, coefficient_of_variation=10.0)
    derive_standard_error(incoherent, 1.959964)
    high = rec(coefficient_of_variation=45.0)
    run([ok, incoherent, high])
    assert "VAL009" not in ok["issue_rules"]
    assert "VAL009" in incoherent["issue_rules"]
    assert "VAL008" in high["issue_rules"] and high["validation_status"] == "VALID_WITH_WARNINGS"


def test_standard_error_only_from_symmetric_untruncated_ci():
    sym = rec(estimate=30.0, ci_lower=28.0, ci_upper=32.0)
    asym = rec(estimate=30.0, ci_lower=27.0, ci_upper=32.0)
    trunc = rec(estimate=1.0, ci_lower=0.0, ci_upper=2.0)
    for r in (sym, asym, trunc):
        derive_standard_error(r, 1.959964)
    assert sym["standard_error"] == pytest.approx(4 / (2 * 1.959964))
    assert "derivado" in sym["standard_error_method"]
    assert asym["standard_error"] is None and trunc["standard_error"] is None


def test_duplicate_key_in_same_sheet_detected():
    a, b = rec(source_sheet="X", response_category="x"), rec(source_sheet="X", response_category="x")
    run([a, b])
    assert "VAL011" in b["issue_rules"]


def test_cross_table_duplicates_marked_and_inconsistency_flagged():
    a = rec(table_id="1.1.1", source_sheet="1.1.1", response_category="x")
    b = rec(table_id="1.1.2", source_sheet="1.1.2", response_category="x")
    c = rec(table_id="1.1.2", source_sheet="1.1.2b", territory_code="N", territory_name="Norte", territory_type="region",
            response_category="x")
    d = rec(table_id="1.1.1", source_sheet="1.1.1", territory_code="N", territory_name="Norte", territory_type="region",
            estimate=31.0, ci_lower=29.0, ci_upper=33.0, response_category="x")
    run([a, b, c, d])
    assert b["analytical_duplicate_of"] == a["observation_id"] and "VAL020" not in b["issue_rules"]
    assert c["analytical_duplicate_of"] == d["observation_id"] and "VAL020" in c["issue_rules"]


def test_distribution_sum_rules():
    def dist(vals, **kw):
        row = 900 + len(vals) + int(sum(vals))
        return [rec(estimate_type="distribuicao_percentual", response_category=f"c{i}", estimate=v,
                    ci_lower=v - 0.5, ci_upper=v + 0.5, source_row=row, source_sheet=f"D{row}",
                    indicator_id=f"E__D{row}", **kw)
                for i, v in enumerate(vals)]
    over = dist([60.0, 50.0])
    under = dist([40.0, 50.0])
    explained = dist([45.0, 50.0], nonresponse_excluded=True)
    multi = dist([70.0, 60.0], multi_response=True)
    issues = run(over + under + explained + multi)
    by = {i.observation_id: i for i in issues if i.rule_id == "VAL014"}
    assert all(r["validation_status"] == "ERROR" for r in over)
    assert all(r["validation_status"] == "VALID_WITH_WARNINGS" for r in under)
    assert by[explained[0]["observation_id"]].severity == "INFO"
    assert not any(r["observation_id"] in by for r in multi), "múltipla resposta não deve somar 100%"


def test_partition_bound_violation():
    kw = dict(source_sheet="P", response_category="x")
    tot = rec(sex="Total", estimate=50.0, ci_lower=48, ci_upper=52, **kw)
    h = rec(sex="Homem", estimate=30.0, ci_lower=28, ci_upper=32, **kw)
    m = rec(sex="Mulher", estimate=40.0, ci_lower=38, ci_upper=42, **kw)
    run([tot, h, m])
    assert "VAL015" in tot["issue_rules"]


def test_count_additivity():
    kw = dict(unit="escolares", estimate_type="total_estimado", source_row=500, ci_lower=None, ci_upper=None,
              source_sheet="C", response_category="x")
    t = rec(admin_dependency="Total", estimate=1000.0, **kw)
    p = rec(admin_dependency="Pública", estimate=700.0, **kw)
    q = rec(admin_dependency="Privada", estimate=200.0, **kw)
    run([t, p, q])
    assert "VAL019" in t["issue_rules"]


def test_outlier_is_informative_not_error():
    ufs = [rec(territory_type="uf", territory_code=str(10 + i), territory_name=f"UF{i}", estimate=20.0 + i * 0.1,
               ci_lower=18.0, ci_upper=25.0, response_category="x") for i in range(10)]
    ufs.append(rec(territory_type="uf", territory_code="99", territory_name="UFX", estimate=90.0, ci_lower=85,
                   ci_upper=95, response_category="x"))
    run(ufs)
    assert "OUT001" in ufs[-1]["issue_rules"] and ufs[-1]["validation_status"] == "VALID"


def test_symbol_and_unknown_territory_statuses():
    sym = rec(estimate=None, estimate_kind="symbol", estimate_symbol="-", ci_lower=None, ci_upper=None)
    unk = rec(territory_code="", extraction_flags="TERRITORIO_NAO_RECONHECIDO")
    run([sym, unk])
    assert sym["validation_status"] == "NOT_AVAILABLE" and not sym["approved_for_analysis"]
    assert unk["validation_status"] == "REVIEW_REQUIRED" and not unk["approved_for_analysis"]


def test_validation_never_removes_records():
    records = [rec(estimate=150.0), rec(), rec(ci_lower=40, ci_upper=20)]
    run(records)
    assert len(records) == 3

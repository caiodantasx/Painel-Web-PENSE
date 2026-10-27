"""Comparabilidade e série histórica."""
import pytest

from pense.harmonization.catalog import build_catalog, measure_id
from pense.harmonization.comparability import evaluate, status_index
from pense.historical.series import build_series


def obs(ind, year, est, terr="BR", pop="ESCOLARES_13_17_ANOS", period="30_DIAS", cat="", **kw):
    r = {
        "observation_id": f"{ind}-{year}-{terr}-{cat}-{est}", "indicator_id": ind, "edition_id": f"E{year}",
        "edition_year": year, "theme_id": "9", "table_family_id": ind.split("__")[-1], "table_id": "9.1.1",
        "indicator_name": "Percentual de escolares", "indicator_definition": "Percentual de escolares que X",
        "question_text": "PENDENTE", "population": pop, "population_code": pop, "reference_period": period,
        "reference_period_code": period, "informant": "Escolar", "unit": "%", "estimate_type": "percentual",
        "territory_code": terr, "territory_name": terr, "territory_type": "country", "age_group": "Total",
        "sex": "Total", "admin_dependency": "Total", "category_group": "", "response_category": cat,
        "category_code": "geral", "confidence_level": 95, "coefficient_of_variation": None,
        "denominator": pop, "denominator_status": "EXTRAIDO_DO_TITULO", "estimate": est, "ci_lower": est - 1,
        "ci_upper": est + 1, "approved_for_analysis": True, "analytical_duplicate_of": "", "record_kind": "estimate",
        "source_file": "f", "source_sheet": "s", "source_cell": "B1", "methodological_note": "", "multi_response": False,
    }
    r.update(kw)
    return r


CAND = [{"concept_id": "C1", "unit": "%", "left_indicator_id": "A__1", "left_category": "",
         "right_indicator_id": "B__1", "right_category": "", "candidate_reason": "teste"}]


def test_different_population_is_not_comparable():
    recs = [obs("A__1", 2009, 10, pop="ESCOLARES_9ANO_EF"), obs("B__1", 2024, 12)]
    row = evaluate(recs, CAND, [])[0]
    assert row["final_status"] == "NOT_COMPARABLE" and "População" in row["differences"]


def test_identical_attributes_never_become_comparable_automatically():
    recs = [obs("A__1", 2019, 10), obs("B__1", 2024, 12)]
    row = evaluate(recs, CAND, [])[0]
    assert row["final_status"] == "PENDING_REVIEW"


def test_human_decision_requires_justification():
    recs = [obs("A__1", 2019, 10), obs("B__1", 2024, 12)]
    base = {"concept_id": "C1", "left_indicator_id": "A__1", "left_category": "", "right_indicator_id": "B__1",
            "right_category": "", "final_status": "COMPARABLE", "evidence_reference": "Nota técnica X",
            "reviewer": "Caio", "decision_date": "2026-10-26"}
    ok = evaluate(recs, CAND, [dict(base, justification="Mesma pergunta e universo (nota técnica X, p. 3)")])[0]
    bad = evaluate(recs, CAND, [dict(base, justification="  ")])[0]
    assert ok["final_status"] == "COMPARABLE" and "decisão humana" in ok["decision_source"]
    assert bad["final_status"] == "PENDING_REVIEW"


def test_wildcard_category_expands_pairs():
    recs = [obs("A__1", 2015, 10), obs("B__1", 2024, 12, cat="x"), obs("B__1", 2024, 13, cat="y")]
    cand = [dict(CAND[0], right_category="*")]
    rows = evaluate(recs, cand, [])
    assert {r["right_category"] for r in rows} == {"x", "y"}
    idx = status_index(rows)
    assert idx[("B__1", "x")] == "PENDING_REVIEW"


def test_series_only_for_approved_pairs_with_changes():
    recs = [obs("A__1", 2019, 10.0), obs("B__1", 2024, 12.5), obs("A__1", 2019, 20.0, terr="N"),
            obs("B__1", 2024, 15.0, terr="N"), obs("B__1", 2024, 9.0, terr="S")]
    comp = [{"concept_id": "C1", "left_indicator_id": "A__1", "left_category": "", "right_indicator_id": "B__1",
             "right_category": "", "unit": "%", "final_status": "COMPARABLE_WITH_CAVEATS",
             "final_justification": "teste"}]
    pts, summ, status = build_series(recs, comp, ["E2015", "E2019", "E2024"])
    br = [p for p in pts if p["territory_code"] == "BR"]
    assert [p["year"] for p in br] == [2019, 2024]
    assert br[1]["abs_change"] == pytest.approx(2.5) and br[1]["abs_change_unit"] == "p.p."
    assert br[1]["rel_change_pct"] == pytest.approx(25.0)
    assert not [p for p in pts if p["territory_code"] == "S"], "recorte com um único ano não forma série"
    s = [x for x in summ if x["territory_code"] == "BR"][0]
    assert s["editions_without_point"] == "E2015" and "descriptive_mean" not in s
    assert status[0]["included_in_series"]


def test_incompatible_tables_are_never_combined():
    recs = [obs("A__1", 2009, 10.0), obs("B__1", 2024, 12.5)]
    comp = [{"concept_id": "C1", "left_indicator_id": "A__1", "left_category": "", "right_indicator_id": "B__1",
             "right_category": "", "unit": "%", "final_status": "NOT_COMPARABLE", "final_justification": "pop."}]
    pts, summ, status = build_series(recs, comp, ["E2009", "E2024"])
    assert pts == [] and summ == [] and not status[0]["included_in_series"]


def test_descriptive_mean_only_when_enabled_and_labelled():
    recs = [obs("A__1", 2019, 10.0), obs("B__1", 2024, 14.0)]
    comp = [{"concept_id": "C1", "left_indicator_id": "A__1", "left_category": "", "right_indicator_id": "B__1",
             "right_category": "", "unit": "%", "final_status": "COMPARABLE", "final_justification": "ok"}]
    _, summ, _ = build_series(recs, comp, ["E2019", "E2024"], allow_mean=True)
    assert summ[0]["descriptive_mean"] == pytest.approx(12.0)
    assert "NÃO é estimativa combinada" in summ[0]["descriptive_mean_note"]


def test_non_approved_records_do_not_enter_series():
    recs = [obs("A__1", 2019, 10.0), obs("B__1", 2024, 14.0, approved_for_analysis=False)]
    comp = [{"concept_id": "C1", "left_indicator_id": "A__1", "left_category": "", "right_indicator_id": "B__1",
             "right_category": "", "unit": "%", "final_status": "COMPARABLE", "final_justification": "ok"}]
    pts, _, _ = build_series(recs, comp, ["E2019", "E2024"])
    assert pts == []


def test_catalog_one_row_per_measure():
    recs = [obs("B__1", 2024, 12, cat="x"), obs("B__1", 2024, 13, cat="x", terr="N"), obs("B__1", 2024, 9, cat="y")]
    cat = build_catalog(recs, {})
    assert len(cat) == 2 and {c["n_observations"] for c in cat} == {1, 2}
    assert measure_id(recs[0]) == "B__1__geral__pct"

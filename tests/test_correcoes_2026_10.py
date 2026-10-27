"""Correções da auditoria de 27/10/2026 (docs/04, D21 a D23).

* Tabelas da PeNSE 2015 Amostra 2 lidas por adaptador próprio, sem confundir com 2024/2019.
* Convenções de não resposta: PUBLICAÇÃO (validação) × SÉRIE (sem resposta entra, abandono sai).
* Comparabilidade: proposta automática ≠ decisão; edições sem evidência fora da série;
  selo "Diferença significativa a 5%" só com decisão registrada (D27; antes "mudança confirmada").
* Recálculo real a partir dos microdados quando eles estão presentes (não só leitura de CSV).
"""
from __future__ import annotations

import csv
import math
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from pense.adapters.families import Pense2015Amostra2Adapter
from pense.microdata.estimator import DesignArrays
from pense.microdata.run import CONV_PUB, CONV_SERIE, EditionData, _masks, needed_convention
from pense.microdata.series import (CHANGE_NS, CHANGE_PENDING, CHANGE_SIGNIFICANT, assess_comparability,
                                    build_series, valid_decisions)
from pense.parsing.title import parse_title

ROOT = Path(__file__).resolve().parents[1]
CUR = ROOT / "data" / "curated"


def _csv(path: Path) -> list[dict]:
    if not path.exists():
        pytest.skip(f"{path.name} ausente: rode scripts/run_all.py")
    with path.open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


# --------------------------------------------------------------------------- adaptador 2015 A2
def test_title_2015_a2_population_and_sample():
    t = parse_title("Tabela 2.11.1 - Percentual de escolares com idade de 13 a 17 anos que não compareceram à escola "
                    "por falta de segurança no trajeto casa-escola nos 30 dias anteriores à pesquisa, por sexo, com "
                    "indicação do intervalo de confiança de 95%, segundo a faixa etária do escolar e as Grandes Regiões - 2015",
                    ["Fonte: IBGE, Diretoria de Pesquisas, Coordenação de População e Indicadores Sociais, "
                     "Pesquisa Nacional de Saúde do Escolar, Amostra 2, 2015."])
    assert t.population_code == "ESCOLARES_13_17_ANOS" and t.sample == "Amostra 2" and t.year == 2015


def test_2015_a2_third_level_is_the_table_not_a_cut():
    assert Pense2015Amostra2Adapter().table_codes("2.11.10") == ("11", "2.11.10")
    assert Pense2015Amostra2Adapter().table_codes("2.11.1") != Pense2015Amostra2Adapter().table_codes("2.11.10")


def test_2015_a2_tables_extracted_with_traceability():
    obs = [r for r in _csv(ROOT / "data" / "processed" / "observations_validated.csv") if r["edition_id"] == "PENSE_2015_A2"]
    assert obs, "tabelas 2.11.x devem ser lidas pelo adaptador PENSE_2015_A2"
    assert {r["adapter_family"] for r in obs} == {"PENSE_2015_A2"}
    assert {r["validation_status"] for r in obs} <= {"VALID", "VALID_WITH_WARNINGS"}
    br = [r for r in obs if r["table_id"] == "2.11.1" and r["territory_code"] == "BR" and r["age_group"] == "Total"
          and r["sex"] == "Total" and r["admin_dependency"] == "Total"]
    assert len(br) == 1
    r = br[0]
    assert float(r["estimate"]) == pytest.approx(13.09713959) and float(r["ci_lower"]) == pytest.approx(11.87947437)
    assert r["source_cell"] == "B8" and r["population_code"] == "ESCOLARES_13_17_ANOS"
    cats = {r["response_category"] for r in obs if r["table_id"] == "2.11.4"}
    assert cats == {"Banco da frente", "Banco de trás"}


# --------------------------------------------------------------------------- não resposta
def _edition(values: dict[str, list], split: bool) -> EditionData:
    df = pd.DataFrame(values)
    n = len(df)
    spec = {"var_prefix": "V", "nonresponse_in_denominator": [], "year": 2015}
    last = qpos = None
    if split:
        spec["series_nonresponse"] = {"split_code": 99, "in_denominator": [], "question_prefix": "VB",
                                      "not_answer_codes": [-1], "description": "teste"}
        qcols = [c for c in df.columns if c.startswith("VB")]
        A = df[qcols].to_numpy(dtype=float)
        answered = ~np.isnan(A) & ~np.isin(A, [99, -1])
        last = np.where(answered.any(1), (answered * np.arange(len(qcols))).max(1), -1)
        qpos = {c: i for i, c in enumerate(qcols)}
    return EditionData("T", spec, df, DesignArrays.build(np.ones(n), np.zeros(n), np.arange(n)), last, qpos)


def test_series_convention_keeps_nonresponse_and_drops_abandonment():
    # aluno 0: respondeu 2 (num); aluno 1: respondeu 1; aluno 2: 99 mas respondeu pergunta posterior (sem resposta);
    # aluno 3: 99 e nada depois (abandono)
    ed = _edition({"VB1": [2, 1, 99, 99], "VB2": [1, 1, 1, 99]}, split=True)
    ind = {"var": "B1", "num": [2], "den": [1, 2]}
    _, den_pub, _, _ = _masks(ed, ind, CONV_PUB)
    num, den_ser, _, rule = _masks(ed, ind, CONV_SERIE)
    assert den_pub.tolist() == [True, True, False, False], "publicação 2015: 99 fora"
    assert den_ser.tolist() == [True, True, True, False], "série: sem resposta entra, abandono sai"
    assert num.tolist() == [True, False, False, False] and "abandono" in rule


def test_editions_without_series_rule_use_publication_rule():
    ed = _edition({"VB1": [2, 1, 9]}, split=False)
    ed.spec["nonresponse_in_denominator"] = [9]
    a = _masks(ed, {"var": "B1", "num": [2], "den": [1, 2]}, CONV_PUB)[1]
    b = _masks(ed, {"var": "B1", "num": [2], "den": [1, 2]}, CONV_SERIE)[1]
    assert a.tolist() == b.tolist() == [True, True, True]


def test_series_tables_are_validated_with_series_convention():
    assert needed_convention("PENSE_SERIE_9ANO_CAPITAIS@10.7") == CONV_SERIE
    assert needed_convention("2.11.1") == CONV_PUB


def test_no_fixed_nonresponse_effect_claim_in_code():
    for f in (ROOT / "src" / "pense" / "microdata").glob("*.py"):
        assert "< 0,2 p.p." not in f.read_text(encoding="utf-8"), f"afirmação fixa de efeito em {f.name}"


# --------------------------------------------------------------------------- governança da série
EDS = {"A": {"year": 2015, "nonresponse_in_denominator": []}, "B": {"year": 2019, "nonresponse_in_denominator": [9]},
       "C": {"year": 2024, "nonresponse_in_denominator": [-9]}}


def _ind(**kw):
    base = {"label": "", "period": "30_DIAS", "var": "B1", "num": [1], "den": [1, 2], "editions": ["A", "B", "C"]}
    base.update(kw)
    return base


def _val(*pairs):
    return [{"edition_id": e, "indicator_key": k, "status": st} for e, k, st in pairs]


def test_edition_without_validation_is_kept_out_of_the_series():
    out = assess_comparability({"X": _ind()}, EDS, _val(("B", "X", "VALIDADO"), ("C", "X", "VALIDADO")), [])[0]
    assert out["series_editions"] == "B|C" and "2015" in out["caveats"]
    assert out["proposed_status"] == "COMPARABLE_WITH_CAVEATS" and out["decision_status"] == "PROPOSTA_AUTOMATICA"


def test_failed_validation_and_configured_exclusion_are_pending():
    v = _val(("A", "X", "NAO_VALIDADO"), ("B", "X", "VALIDADO"), ("C", "X", "VALIDADO"))
    assert assess_comparability({"X": _ind()}, EDS, v, [])[0]["proposed_status"] == "PENDING_REVIEW"
    v = _val(("A", "X", "VALIDADO"), ("B", "X", "VALIDADO"), ("C", "X", "VALIDADO"))
    out = assess_comparability({"X": _ind(series_exclude="fora da série por decisão metodológica")}, EDS, v, [])[0]
    assert out["proposed_status"] == "PENDING_REVIEW" and "fora da série" in out["caveats"]


def test_indirect_validation_only_when_declared():
    v = _val(("A", "X", "VALIDADO"), ("B", "X", "VALIDADO"), ("C", "Y", "VALIDADO"))
    assert assess_comparability({"X": _ind()}, EDS, v, [])[0]["series_editions"] == "A|B"
    out = assess_comparability({"X": _ind(indirect_validation={"C": ["Y"]})}, EDS, v, [])[0]
    assert out["series_editions"] == "A|B|C" and "INDIRETA" in out["evidence_by_edition"]
    assert "não oficial" in out["caveats"]


def test_incomplete_decisions_never_approve():
    ok, bad = valid_decisions([{"indicator_key": "X", "final_status": "COMPARABLE", "justification": "ok",
                                "evidence_reference": "", "reviewer": "R", "decision_date": "2026-10-27"}])
    assert ok == {} and bad
    v = _val(("B", "X", "VALIDADO"), ("C", "X", "VALIDADO"))
    out = assess_comparability({"X": _ind()}, EDS, v, [{"indicator_key": "X", "final_status": "COMPARABLE",
                                                       "justification": "ok", "reviewer": "R", "decision_date": "d"}])[0]
    assert out["decision_status"] == "PROPOSTA_AUTOMATICA"


def _est(year, e, se, ed=None):
    return {"indicator_key": "X", "edition_id": ed or f"E{year}", "edition_year": str(year), "territory_code": "BR",
            "territory_name": "Brasil", "territory_type": "country", "age_group": "Total", "sex": "Total",
            "admin_dependency": "Total", "estimate": str(e), "standard_error": str(se), "ci_lower": str(e - 1),
            "ci_upper": str(e + 1), "low_precision": "False", "nonresponse_convention": "PUBLICACAO+SERIE"}


def test_change_is_confirmed_only_with_registered_decision():
    est = [_est(2015, 10, 0.2, "A"), _est(2019, 12, 0.2, "B"), _est(2024, 12.1, 0.2, "C")]
    comp = [{"indicator_key": "X", "final_status": "COMPARABLE_WITH_CAVEATS", "series_editions": "B|C",
             "decision_status": "PROPOSTA_AUTOMATICA"}]
    pts = build_series(est, comp)
    assert [p["year"] for p in pts] == [2019, 2024], "ponto de edição sem evidência não entra (mas não é apagado)"
    assert pts[-1]["change_status"] == CHANGE_NS
    comp[0]["series_editions"] = "A|B|C"
    pts = build_series(est, comp)
    assert pts[1]["change_status"] == CHANGE_PENDING
    comp[0]["decision_status"] = "DECISAO_REGISTRADA"
    assert build_series(est, comp)[1]["change_status"] == CHANGE_SIGNIFICANT


def test_series_uses_harmonized_rows_not_publication_rows():
    pub = dict(_est(2015, 10, 0.2, "A"), nonresponse_convention="PUBLICACAO")
    ser = dict(_est(2015, 9.8, 0.2, "A"), nonresponse_convention="SERIE")
    comp = [{"indicator_key": "X", "final_status": "COMPARABLE_WITH_CAVEATS", "series_editions": "A|B",
             "decision_status": "PROPOSTA_AUTOMATICA"}]
    pts = build_series([pub, ser, _est(2019, 11, 0.2, "B")], comp)
    assert [p["estimate"] for p in pts] == [9.8, 11.0]


# --------------------------------------------------------------------------- critérios de aceitação (saídas)
def test_2015_a2_reproduces_published_tables_with_estrato_exp():
    rows = [r for r in _csv(CUR / "microdata_validation_summary.csv") if r["edition_id"] == "PENSE_2015_A2"]
    assert len(rows) == 10, "tabelas 2.11.1–2.11.7, 2.11.9 e 2.11.10"
    assert all(r["status"] == "VALIDADO" and r["reproduz"] == r["compared"] for r in rows), \
        "estimativa ≤ 0,05 p.p. e limites do IC ≤ 0,15 p.p. em todos os recortes"


def test_criterion_a_2015_a1_reproduces_official_series_totals():
    rows = [r for r in _csv(CUR / "microdata_validation.csv") if r["edition_id"] == "PENSE_2015_A1"
            and r["territory_code"] == "CAPITAIS" and r["sex"] == "Total" and r["admin_dependency"] == "Total"]
    ok = [r for r in rows if r["indicator_key"] != "NONO_CINTO_FRENTE_OU_TRAS"]
    assert len(ok) == 9 and all(abs(float(r["diff_estimate_pp"])) <= 0.05 for r in ok), \
        "convenção da série (sem resposta entra, abandono sai) reproduz a série oficial de 2015"
    assert any(abs(float(r["diff_estimate_pp"])) > 0.3 for r in rows if r["indicator_key"] == "NONO_CINTO_FRENTE_OU_TRAS"), \
        "10.3 continua não reproduzido (regra de derivação desconhecida)"


def test_capacete_as_vezes_out_of_series_and_no_confirmed_change_without_decisions():
    comp = {r["indicator_key"]: r for r in _csv(CUR / "microdata_comparability.csv")}
    assert comp["CAPACETE_AS_VEZES_OU_MAIS"]["final_status"] == "PENDING_REVIEW"
    series = _csv(CUR / "microdata_series.csv")
    assert not any(r["indicator_key"] == "CAPACETE_AS_VEZES_OU_MAIS" for r in series)
    decided = {k for k, c in comp.items() if c["decision_status"] == "DECISAO_REGISTRADA"}
    assert all(r["change_status"] != CHANGE_SIGNIFICANT for r in series if r["indicator_key"] not in decided)


# --------------------------------------------------------------------------- recálculo real
def _recompute(edition: str, key: str, convention: str = CONV_PUB):
    from pense.config import Config
    from pense.microdata import run as R
    from pense.microdata.estimator import ratio
    cfg = Config(root=ROOT)
    eds, inds = R.load_config(cfg)
    if not (ROOT / eds[edition]["file"]).exists():
        pytest.skip(f"microdados {edition} ausentes (ver scripts/extract_microdata.py)")
    ed = R.load_edition(cfg, edition, eds[edition], {key: inds[key]})
    num, den, _, _ = R._masks(ed, inds[key], convention)
    pop = inds[key].get("population", "13_17")
    terr = "CAPITAIS" if pop == "9ANO" else "BR"     # série oficial do 9º ano = conjunto das capitais
    dom = next(m for lab, m in R.domains(ed, cfg, pop)
               if lab["territory_code"] == terr and lab["age_group"] == "Total" and lab["sex"] == "Total"
               and lab["admin_dependency"] == "Total")
    return ratio(ed.design, num & dom, den & dom)


@pytest.mark.parametrize("edition,key,table,pub", [
    ("PENSE_2015_A2", "TRAJETO_INSEGURO", "2.11.1", (13.09713959, 11.87947437, 14.31480481)),
    ("PENSE_2024", "TRAJETO_INSEGURO", "9.7", None),
])
def test_recompute_from_microdata_matches_published_table(edition, key, table, pub):
    e = _recompute(edition, key)
    if pub is None:   # valor publicado lido da base extraída (célula de origem rastreável)
        obs = [r for r in _csv(ROOT / "data" / "processed" / "observations_validated.csv")
               if r["edition_id"] == edition and r["table_family_id"] == table and r["territory_code"] == "BR"
               and r["age_group"] == "Total" and r["sex"] == "Total" and r["admin_dependency"] == "Total"]
        pub = (float(obs[0]["estimate"]), float(obs[0]["ci_lower"]), float(obs[0]["ci_upper"]))
    assert 100 * e.p == pytest.approx(pub[0], abs=0.05)
    assert 100 * e.ci_lower == pytest.approx(pub[1], abs=0.15) and 100 * e.ci_upper == pytest.approx(pub[2], abs=0.15)
    assert not math.isnan(e.se)


def test_recompute_2015_a1_series_convention_matches_official_series():
    e = _recompute("PENSE_2015_A1", "NONO_TRAJETO_INSEGURO", CONV_SERIE)
    assert 100 * e.p == pytest.approx(12.74565, abs=0.05), "série oficial 10.7, 2015, total das capitais"

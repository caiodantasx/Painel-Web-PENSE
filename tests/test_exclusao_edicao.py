"""Exclusão de UMA edição da série principal por decisão registrada (D26).

Pedido do pesquisador (27/10/2026, TRAJETO_INSEGURO): retirar 2015 (Amostra 2) da série principal
até resolver a diferença de cobertura escolar, sem excluir o indicador e sem apagar os dados de 2015.
Garantias testadas:
* padrão: sem linha válida, nada é excluído;
* com a exclusão, a série principal fica só com as edições restantes (2019 e 2024);
* a comparação 2015→2019 (variação e selo) deixa de existir na série principal;
* os demais indicadores não mudam;
* configuração inválida (campo vazio, indicador/edição inexistente, edição que o indicador não
  tem, data inválida ou futura, duplicata, cabeçalho fora do esquema) interrompe a pipeline;
* texto livre numa justificativa de comparabilidade não exclui nada;
* estimativas, validação e valores de 2015 continuam disponíveis; o motivo é rastreável.

Os nomes de responsável usados aqui são marcadores de teste ("REVISOR_DE_TESTE"), não decisões.
"""
from __future__ import annotations

import copy
import csv
import shutil
from datetime import date
from pathlib import Path

import pytest

from pense.microdata.series import (EXCLUSION_FIELDS, SeriesExclusionError, assess_comparability, build_series,
                                    check_exclusion_header, load_exclusions)

ROOT = Path(__file__).resolve().parents[1]
CUR = ROOT / "data" / "curated"
TODAY = date(2026, 10, 27)
TESTER = "REVISOR_DE_TESTE"

EDS = {"A": {"year": 2015, "nonresponse_in_denominator": []}, "B": {"year": 2019, "nonresponse_in_denominator": [9]},
       "C": {"year": 2024, "nonresponse_in_denominator": [-9]}, "D": {"year": 2009, "nonresponse_in_denominator": []}}
IND = {"label": "", "period": "30_DIAS", "var": "B1", "num": [1], "den": [1, 2], "editions": ["A", "B", "C"]}
INDS = {"X": dict(IND), "Y": dict(IND)}
VAL = [{"edition_id": e, "indicator_key": k, "status": "VALIDADO"} for e in "ABC" for k in "XY"]
ROW = {"indicator_key": "X", "edition_id": "A", "reason": "cobertura escolar diferente (6º ano)",
       "evidence_reference": "IBGE 2022 p. 14-16", "reviewer": TESTER, "decision_date": "2026-10-27"}
DEC = [{"indicator_key": "X", "final_status": "COMPARABLE_WITH_CAVEATS", "justification": "j",
        "evidence_reference": "e", "reviewer": TESTER, "decision_date": "2026-10-27"}]


def _est(key, ed, year, e, se=0.2):
    return {"indicator_key": key, "edition_id": ed, "edition_year": str(year), "territory_code": "BR",
            "territory_name": "Brasil", "territory_type": "country", "age_group": "Total", "sex": "Total",
            "admin_dependency": "Total", "estimate": str(e), "standard_error": str(se), "ci_lower": str(e - 1),
            "ci_upper": str(e + 1), "low_precision": "False", "nonresponse_convention": "PUBLICACAO+SERIE"}


EST = [_est(k, ed, y, v) for k in "XY" for ed, y, v in (("A", 2015, 13.0), ("B", 2019, 11.6), ("C", 2024, 12.5))]


def _comp(rows=(), decisions=()):
    return {c["indicator_key"]: c for c in assess_comparability(
        INDS, EDS, VAL, list(decisions), None, None, load_exclusions(list(rows), INDS, EDS, today=TODAY))}


def _pts(comp, key="X"):
    return [p for p in build_series(EST, list(comp.values())) if p["indicator_key"] == key]


# --------------------------------------------------------------------------- comportamento
def test_default_excludes_nothing():
    assert load_exclusions([], INDS, EDS, today=TODAY) == {}
    c = _comp()["X"]
    assert c["series_editions"] == "A|B|C" and c["excluded_editions"] == "" and c["excluded_edition_ids"] == ""
    assert [p["year"] for p in _pts(_comp())] == [2015, 2019, 2024]


def test_blank_lines_are_not_exclusions():
    blank = {f: "" for f in EXCLUSION_FIELDS}
    assert load_exclusions([blank, {f: "  " for f in EXCLUSION_FIELDS}], INDS, EDS, today=TODAY) == {}


def test_excluded_edition_leaves_main_series_only_2019_and_2024():
    c = _comp([ROW])["X"]
    assert c["series_editions"] == "B|C" and c["editions"] == "A|B|C", "o indicador continua com as três edições"
    assert [p["year"] for p in _pts(_comp([ROW]))] == [2019, 2024]


def test_2015_to_2019_comparison_and_its_badge_disappear_even_with_decision():
    pts = _pts(_comp([ROW], DEC))
    assert not any(p["previous_year"] == 2015 for p in pts), "nenhuma variação 2015→2019 na série principal"
    first = next(p for p in pts if p["year"] == 2019)
    assert first["diff_pp"] == "" and first["change_status"] == "" and first["significant_5pct"] == ""
    second = next(p for p in pts if p["year"] == 2024)
    assert second["previous_year"] == 2019, "a única comparação restante é 2019→2024"


def test_exclusion_is_traceable():
    c = _comp([ROW])["X"]
    assert c["excluded_edition_ids"] == "A"
    assert c["excluded_editions"] == f"A: cobertura escolar diferente (6º ano) ({TESTER}, 2026-10-27)"
    assert "2015: DIRETA (EXCLUÍDA POR DECISÃO)" in c["evidence_by_edition"]
    assert f"2015 fora da série principal por decisão registrada ({TESTER}, 2026-10-27)" in c["caveats"]
    assert "evidência: IBGE 2022 p. 14-16" in c["caveats"] and "continuam disponíveis para consulta" in c["caveats"]


def test_exclusion_does_not_touch_estimates_or_validation():
    est, val = copy.deepcopy(EST), copy.deepcopy(VAL)
    comp = assess_comparability(INDS, EDS, val, [], None, None, load_exclusions([ROW], INDS, EDS, today=TODAY))
    build_series(est, comp)
    assert est == EST and val == VAL, "entradas não são alteradas"
    assert [e for e in est if e["indicator_key"] == "X" and e["edition_id"] == "A"], "2015 continua nas estimativas"


def test_other_indicators_unchanged():
    before, after = _comp(), _comp([ROW])
    assert before["Y"] == after["Y"]
    assert _pts(before, "Y") == _pts(after, "Y")


def test_free_text_in_comparability_justification_never_excludes():
    dec = [dict(DEC[0], justification="excluir 2015 da série principal; 2015 fora da série")]
    c = _comp([], dec)["X"]
    assert c["series_editions"] == "A|B|C" and c["excluded_edition_ids"] == ""
    assert any(p["previous_year"] == 2015 for p in _pts(_comp([], dec)))


# --------------------------------------------------------------------------- configuração inválida
@pytest.mark.parametrize("bad, msg", [
    ({"indicator_key": ""}, "campos vazios"),
    ({"edition_id": ""}, "campos vazios"),
    ({"reason": ""}, "campos vazios"),
    ({"evidence_reference": "  "}, "campos vazios"),
    ({"reviewer": ""}, "campos vazios"),
    ({"decision_date": ""}, "campos vazios"),
    ({"indicator_key": "Z"}, "indicador desconhecido"),
    ({"edition_id": "PENSE_2099"}, "edição desconhecida"),
    ({"edition_id": "D"}, "não pertence ao indicador X"),
    ({"decision_date": "27/10/2026"}, "data inválida"),
    ({"decision_date": "2026-02-30"}, "data inválida"),
    ({"decision_date": "20261027"}, "data inválida"),
    ({"decision_date": "2026-10-28"}, "data futura"),
])
def test_invalid_exclusion_stops_the_pipeline(bad, msg):
    with pytest.raises(SeriesExclusionError, match=msg):
        load_exclusions([dict(ROW, **bad)], INDS, EDS, today=TODAY)


def test_duplicate_exclusion_is_an_error():
    with pytest.raises(SeriesExclusionError, match="duplicada"):
        load_exclusions([ROW, dict(ROW)], INDS, EDS, today=TODAY)


def test_one_bad_line_invalidates_the_whole_file():
    """Nada de aplicar as linhas boas e pular as ruins: o arquivo inteiro é recusado."""
    with pytest.raises(SeriesExclusionError, match="linha 3"):
        load_exclusions([ROW, dict(ROW, indicator_key="Y", reviewer="")], INDS, EDS, today=TODAY)


@pytest.mark.parametrize("header", [
    ["indicator_key", "edition_id", "reason", "evidence_reference", "reviewer"],
    list(EXCLUSION_FIELDS) + ["extra"],
    ["indicator_key", "edition_id", "reason", "reviewer", "evidence_reference", "decision_date"],
])
def test_header_must_match_schema(header):
    with pytest.raises(SeriesExclusionError, match="cabeçalho"):
        check_exclusion_header(header)


def test_pipeline_reader_rejects_bad_file(tmp_path):
    from pense.microdata.integrate import read_exclusions
    p = tmp_path / "series_exclusions.csv"
    p.write_text("indicator_key,edition_id,reason\nX,A,motivo\n", encoding="utf-8")
    with pytest.raises(SeriesExclusionError, match="cabeçalho"):
        read_exclusions(p, INDS, EDS)
    p.write_text(",".join(EXCLUSION_FIELDS) + "\nX,A,motivo,evidência,,\n", encoding="utf-8")
    with pytest.raises(SeriesExclusionError, match="campos vazios"):
        read_exclusions(p, INDS, EDS)
    assert read_exclusions(tmp_path / "nao_existe.csv", INDS, EDS) == {}


# --------------------------------------------------------------------------- dados reais do projeto
@pytest.fixture(scope="module")
def real(tmp_path_factory):
    """Roda a integração dos microdados duas vezes sobre as saídas reais, em cópias temporárias de
    config/ (os arquivos do projeto não são tocados): sem nenhuma decisão nem exclusão, e só com a
    exclusão de TRAJETO_INSEGURO × 2015 A2. Assim o teste vale com ou sem decisões registradas no projeto."""
    if not (CUR / "microdata_estimates.csv").exists():
        pytest.skip("rode scripts/run_all.py")
    from pense.config import Config
    from pense.microdata.integrate import load_microdata_outputs

    def root(name: str, exclusion: dict | None) -> Path:
        tmp = tmp_path_factory.mktemp(name)
        shutil.copytree(ROOT / "config", tmp / "config")
        (tmp / "data").symlink_to(ROOT / "data", target_is_directory=True)
        micro = tmp / "config" / "microdata"
        (micro / "comparability_decisions.csv").write_text(
            "indicator_key,final_status,justification,evidence_reference,reviewer,decision_date\n", encoding="utf-8")
        with (micro / "series_exclusions.csv").open("w", encoding="utf-8", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=EXCLUSION_FIELDS, lineterminator="\n")
            w.writeheader()
            if exclusion:
                w.writerow(exclusion)
        return tmp

    row = dict(ROW, indicator_key="TRAJETO_INSEGURO", edition_id="PENSE_2015_A2", decision_date=date.today().isoformat())
    return (load_microdata_outputs(Config(root=root("sem", None))),
            load_microdata_outputs(Config(root=root("com", row))))


def _br_total(rows, key):
    return [p for p in rows if p["indicator_key"] == key and p["territory_code"] == "BR"
            and p["age_group"] == "Total" and p["sex"] == "Total" and p["admin_dependency"] == "Total"]


def test_real_trajeto_inseguro_main_series_is_2019_2024(real):
    base, new = real
    cb = {c["indicator_key"]: c for c in base["comparability"]}
    cn = {c["indicator_key"]: c for c in new["comparability"]}
    assert cb["TRAJETO_INSEGURO"]["series_editions"] == "PENSE_2015_A2|PENSE_2019|PENSE_2024"
    assert cn["TRAJETO_INSEGURO"]["series_editions"] == "PENSE_2019|PENSE_2024"
    assert cn["TRAJETO_INSEGURO"]["excluded_edition_ids"] == "PENSE_2015_A2"
    assert cn["TRAJETO_INSEGURO"]["proposed_status"] == "COMPARABLE_WITH_CAVEATS"
    assert cn["TRAJETO_INSEGURO"]["decision_status"] == "PROPOSTA_AUTOMATICA", "exclusão não é decisão de comparabilidade"
    pts = _br_total(new["series"], "TRAJETO_INSEGURO")
    assert [p["year"] for p in pts] == [2019, 2024]
    assert not any(p["previous_year"] == 2015 for p in new["series"] if p["indicator_key"] == "TRAJETO_INSEGURO")
    p24 = pts[1]
    assert p24["previous_year"] == 2019 and round(p24["diff_pp"], 2) == 0.87, "2019→2024 inalterada pela exclusão"
    fields = ("diff_pp", "diff_ci_lower", "diff_ci_upper", "significant_5pct", "change_status")
    old24 = _br_total(base["series"], "TRAJETO_INSEGURO")[2]
    assert {k: p24[k] for k in fields} == {k: old24[k] for k in fields}


def test_real_2015_values_preserved_and_flagged(real):
    base, new = real
    assert base["estimates"] == new["estimates"], "estimativas calculadas idênticas"
    e15 = [e for e in new["estimates"] if e["indicator_key"] == "TRAJETO_INSEGURO" and e["edition_id"] == "PENSE_2015_A2"
           and e["territory_code"] == "BR" and e["age_group"] == "Total" and e["sex"] == "Total"
           and e["admin_dependency"] == "Total"]
    conv = {e["nonresponse_convention"]: round(float(e["estimate"]), 2) for e in e15}
    assert conv == {"PUBLICACAO": 13.10, "SERIE": 12.99}, "publicado (13,10) e harmonizado (12,99) continuam distintos"
    b = new["bundle"]
    k = next(i for i, ind in enumerate(b["indicators"]) if ind["key"] == "TRAJETO_INSEGURO")
    ed = next(i for i, e in enumerate(b["editions"]) if e["id"] == "PENSE_2015_A2")
    assert any(ki == k and ei == ed for ki, ei in zip(b["est"]["k"], b["est"]["ed"])), "2015 continua no painel"
    comp = b["indicators"][k]["comparability"]
    assert comp["excluded_edition_ids"] == "PENSE_2015_A2"
    assert "fora da série principal por decisão registrada" in comp["caveats"]


def test_real_other_35_indicators_identical(real):
    base, new = real
    cb = {c["indicator_key"]: c for c in base["comparability"]}
    cn = {c["indicator_key"]: c for c in new["comparability"]}
    others = [k for k in cb if k != "TRAJETO_INSEGURO"]
    assert len(others) == 35
    assert all(cb[k] == cn[k] for k in others)
    rest = lambda r: [p for p in r["series"] if p["indicator_key"] != "TRAJETO_INSEGURO"]  # noqa: E731
    assert rest(base) == rest(new)


def test_project_exclusions_file_is_valid():
    """O arquivo do projeto existe, segue o esquema e só tem linhas completas e válidas
    (a própria pipeline pararia com SeriesExclusionError se não fosse assim)."""
    from pense.config import Config
    from pense.microdata.integrate import read_exclusions
    from pense.microdata.run import load_config
    path = ROOT / "config" / "microdata" / "series_exclusions.csv"
    assert path.exists(), "arquivo de exclusões deve existir (mesmo vazio) para ser auditável"
    eds, inds = load_config(Config(root=ROOT))
    for ind, by_ed in read_exclusions(path, inds, eds).items():
        for ed, row in by_ed.items():
            assert all(row[f] for f in EXCLUSION_FIELDS), (ind, ed)

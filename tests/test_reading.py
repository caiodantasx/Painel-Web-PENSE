"""Frase "Como ler" de cada medida: o painel precisa dizer X% DE QUÊ (base, informante, não é ocorrência)."""
import json
from pathlib import Path

import pytest

from pense.exports.reading import reading

ROOT = Path(__file__).resolve().parents[1]


def _m(**kw):
    base = {"name": "", "category": "", "category_group": "", "unit": "%", "population": "Escolares de 13 a 17 anos",
            "denominator": "Escolares de 13 a 17 anos", "informant": "Escolar (autopreenchimento)"}
    base.update(kw)
    return base


def test_school_informed_violence_in_locality_reads_as_share_of_students():
    r = reading(_m(name="Percentual de escolares de 13 a 17 anos em escolas cujo diretor(a) ou responsável presenciou ou "
                        "ouviu falar sempre ou algumas vezes situações de violência na localidade onde a escola está situada "
                        "nos 12 meses anteriores à pesquisa, por tipos de violência",
                   category="Assaltos e roubos a pessoas, residências e comércios",
                   informant="Escola (diretor(a) ou responsável)"))
    txt = r["reading"].replace("{v}", "28,4%")
    assert txt.startswith("28,4% dos escolares de 13 a 17 anos em escolas cujo diretor")
    assert "localidade onde a escola está situada" in txt and "“Assaltos e roubos" in txt
    assert "não é a proporção de escolas nem o número de ocorrências" in r["respondent"]
    assert "boletins de ocorrência" in r["source"]


def test_student_reported_knife_fight_reads_as_share_of_students():
    r = reading(_m(name="Percentual de escolares de 13 a 17 anos que estiveram envolvidos em briga na qual alguma pessoa "
                        "usou arma branca nos 30 dias anteriores à pesquisa"))
    assert r["reading"] == ("{v} dos escolares de 13 a 17 anos que estiveram envolvidos em briga na qual alguma pessoa "
                            "usou arma branca nos 30 dias anteriores à pesquisa")
    assert "o próprio aluno" in r["respondent"] and "não é o número de ocorrências" in r["respondent"]
    assert r["base"] == "Escolares de 13 a 17 anos" and r["unit_label"] == "% dos escolares de 13 a 17 anos"


def test_distribution_base_is_the_subgroup_not_all_students():
    r = reading(_m(name="Distribuição percentual dos escolares de 13 a 17 anos que sofreram acidente ou agressão alguma vez "
                        "nos 12 meses anteriores à pesquisa por tipo de ferimento ou lesão mais grave",
                   category="Corte ou perfuração"))
    assert r["reading"].startswith("Entre os escolares de 13 a 17 anos que sofreram acidente ou agressão")
    assert "“Corte ou perfuração”" in r["reading"] and r["base"].startswith("Escolares de 13 a 17 anos que sofreram")


def test_counts_are_not_percentages():
    r = reading(_m(name="Estimativa total de escolares frequentando o 9º ano em escolas que informaram X", unit="escolares",
                   denominator="Não se aplica (contagem estimada)"))
    assert r["reading"].startswith("{v} escolares") and "não de ocorrências" in r["reading"] and r["base"] == ""


def test_every_dashboard_measure_has_a_reading_with_placeholder():
    p = ROOT / "dashboard" / "data" / "pense_bundle.json"
    if not p.exists():
        pytest.skip("rode a pipeline")
    b = json.loads(p.read_text(encoding="utf-8"))
    for m in b["measures"]:
        assert "{v}" in m["reading"] and m["reading_respondent"], m["id"]
        assert m["unit"] != "%" or m["unit_label"].startswith("%"), m["id"]
    assert all(e.get("label") for e in b["meta"]["editions"])
    assert {m["edition_id"] for m in b["measures"] if m["multi_year"]} == {"PENSE_SERIE_9ANO_CAPITAIS"}


def test_number_card_for_school_reported_violence_says_what_it_is_not():
    r = reading(_m(name="Percentual de escolares de 13 a 17 anos em escolas cujo diretor(a) ou responsável presenciou ou "
                        "ouviu falar sempre ou algumas vezes situações de violência na localidade onde a escola está situada "
                        "nos 12 meses anteriores à pesquisa, por tipos de violência",
                   category="Assaltos e roubos a pessoas, residências e comércios",
                   informant="Escola (diretor(a) ou responsável)", period="12 meses anteriores à pesquisa"))
    assert r["count_base"] == "escolares de 13 a 17 anos"
    assert r["situation"].startswith("estudam em escolas cujo diretor") and "“Assaltos e roubos" in r["situation"]
    assert "não significa que esses alunos sofreram ou viram a violência" in r["not_this"].lower()
    assert "% de escolas" in r["not_this"] and "boletim de ocorrência" in r["not_this"]


def test_number_card_for_student_report_and_subgroup_base():
    r = reading(_m(name="Percentual de escolares de 13 a 17 anos que usaram capacete dentre aqueles que andaram de "
                        "motocicleta ou moto nos 30 dias anteriores à pesquisa",
                   denominator="Escolares de 13 a 17 anos que andaram de motocicleta ou moto nos 30 dias anteriores à pesquisa"))
    assert r["count_base"].startswith("escolares de 13 a 17 anos que andaram de motocicleta")
    assert r["situation"] == "usaram capacete nos 30 dias anteriores à pesquisa"
    assert "questionário" in r["not_this"] and "registro policial" in r["not_this"]


def test_dimension_group_label_is_not_a_subgroup_2009_table_8_1():
    """2009, 8.1: 'Trajeto' e 'Escola' são % de TODOS os escolares (6,4% e 5,5% nas capitais; série oficial 6,3% e 5,4%)."""
    r = reading(_m(name="Percentual de escolares frequentando o 9º ano do ensino fundamental que não compareceram à escola, "
                        "nos últimos 30 dias, por falta de segurança no trajeto casa-escola ou na escola",
                   category="Trajeto casa-escola", category_group="Local",
                   population="Escolares do 9º ano do ensino fundamental",
                   denominator="Escolares do 9º ano do ensino fundamental"))
    assert r["reading"].startswith("{v} dos escolares frequentando o 9º ano")
    assert r["base"] == "Escolares do 9º ano do ensino fundamental"
    assert r["count_base"] == "escolares do 9º ano do ensino fundamental"

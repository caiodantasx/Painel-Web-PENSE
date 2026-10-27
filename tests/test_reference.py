"""Documentos de referência do IBGE: guia de tabelas 2024 e questionário do aluno 2015."""
import csv
from pathlib import Path

import pytest

from pense.validation.reference import check_against_guide, normalize_title

ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / "config" / "reference"


def _read(name):
    path = REF / name
    if not path.exists():
        pytest.skip(f"{name} ausente: rode python scripts/build_reference.py")
    with path.open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def test_guide_covers_all_themes():
    g = _read("guia_tabelas_pense_2024.csv")
    assert len(g) == 1510 and len({r["theme_id"] for r in g}) == 19
    t17 = [r for r in g if r["theme_id"] == "17"]
    assert len(t17) == 18 and {r["territorial_cut"] for r in t17} == {"region", "uf", "capital"}
    assert sum(r["measure_sheet"] == "cv" for r in t17) == 9


def test_questionnaire_2015_security_section_matches_pdf():
    q = _read("questionario_pense_2015_aluno.csv")
    b9 = [r for r in q if r["section"] == "B9"]
    assert len(b9) == 18 and b9[0]["section_name"] == "SEGURANÇA"
    first = b9[0]  # página 15 do PDF
    assert first["variable"] == "B09001" and first["question_number"] == "01"
    assert first["question_text"].startswith("NOS ÚLTIMOS 30 DIAS, em quantos dias você deixou de ir à escola")
    assert first["reference_period_code"] == "30_DIAS" and first["change_vs_previous"] == "MANTIDA"
    by = {r["variable"]: r for r in b9}
    assert by["B09006a1"]["change_vs_previous"] == "ALTERADA"   # código em vermelho
    assert by["B09015"]["change_vs_previous"] == "NOVA"          # código em verde
    assert by["B09006a1"]["options"].startswith("Não andei nesse tipo de veículo no banco da frente nos últimos 30 dias |")
    assert "permitir múltipla resposta" in by["B09017"]["filters_and_checks"]
    assert all(r["options"] for r in q), "toda pergunta tem opções"


def _sheet(name, title, year="2024"):
    return {"sheet": name, "title": title, "year": year, "footer_year": year, "source_file": "x.xlsx"}


def test_guide_check_flags_missing_changed_and_unknown_sheets():
    guide = [{"sheet_name": "17.1.1", "theme_id": "17", "title": "Percentual de algo, segundo as Grandes Regiões - 2024"},
             {"sheet_name": "17.1.2", "theme_id": "17", "title": "Percentual de algo, segundo as UFs - 2024"},
             {"sheet_name": "3.1.1", "theme_id": "3", "title": "Outro tema - 2024"}]
    sheets = [_sheet("17.1.1", "Tabela 17.1.1 - Percentual de  algo, segundo as Grandes  Regiões - 2024"),
              _sheet("17.9.9", "Tabela 17.9.9 - Inesperada - 2024"),
              _sheet("8.1", "Tabela 8.1 - de 2009 - 2009", year="2009")]
    issues, report, checks = check_against_guide(sheets, guide)
    rules = sorted(i.rule_id for i in issues)
    assert rules == ["REF001", "REF003"], "17.1.2 ausente; 17.9.9 fora do guia; tema 3 e 2009 ignorados"
    assert checks["REF_titulos_iguais"] == 1
    sheets[0]["title"] = "Tabela 17.1.1 - Percentual de outra coisa - 2024"
    issues, _, _ = check_against_guide(sheets, guide)
    assert "REF002" in {i.rule_id for i in issues}


def test_normalize_title_ignores_prefix_suffix_spacing():
    assert normalize_title("Tabela 9.1.1 - Percentual  de X - 2024") == normalize_title("Percentual de X")

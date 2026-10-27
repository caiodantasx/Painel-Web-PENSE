"""Fixtures compartilhadas.

* ``cfg``: configuração real do projeto (config/).
* ``build_ibge_xlsx``: gera uma planilha sintética pequena com a mesma
  gramática das tabelas do IBGE (título mesclado, cabeçalho multinível com
  mesclagens, seções no stub, rodapé). Valores sintéticos — usados apenas
  para testar a mecânica, nunca exportados como dados.
* ``raw_file``: caminho de um arquivo real (dados públicos do IBGE) em
  data/raw, para testes de regressão.
"""
from __future__ import annotations

import io
import shutil
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from pense.config import Config  # noqa: E402
from pense.models import SourceFile  # noqa: E402


@pytest.fixture(scope="session")
def cfg() -> Config:
    return Config(root=ROOT)


@pytest.fixture
def src_factory():
    def make(name: str = "sintetico.xlsx", fmt: str = "xlsx") -> SourceFile:
        return SourceFile(source_id=name, file_name=name, container="", sha256="0" * 64, size_bytes=0, fmt=fmt)
    return make


def _ibge_workbook(values_by_row: dict[str, list[float]], with_sections: bool = True, year: int = 2024):
    import openpyxl

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "1.1.1"
    ws["A1"] = (f"Tabela 1.1.1 - Percentual de escolares de 13 a 17 anos que fizeram algo nos 30 dias "
                f"anteriores à pesquisa, por sexo, com indicação do intervalo de confiança de 95%, "
                f"segundo os grupos de idade e as Grandes Regiões - {year}")
    ws.merge_cells("A1:J3")
    ws["A4"] = "Grupos de idade e Grandes Regiões"
    ws.merge_cells("A4:A9")
    ws["B4"] = "Percentual de escolares de 13 a 17 anos que fizeram algo (%)"
    ws.merge_cells("B4:J4")
    ws["B5"] = "Total"
    ws.merge_cells("B5:D6")
    ws["E5"] = "Sexo"
    ws.merge_cells("E5:J5")
    ws["E6"] = "Homem"
    ws.merge_cells("E6:G6")
    ws["H6"] = "Mulher"
    ws.merge_cells("H6:J6")
    for col in ("B", "E", "H"):
        ws[f"{col}7"] = "Percentual"
        ws.merge_cells(f"{col}7:{col}9")
    for lo, hi in (("C", "D"), ("F", "G"), ("I", "J")):
        ws[f"{lo}7"] = "Intervalo de confiança de 95%"
        ws.merge_cells(f"{lo}7:{hi}8")
        ws[f"{lo}9"] = "Limite inferior"
        ws[f"{hi}9"] = "Limite superior"
    r = 10
    if with_sections:
        ws.cell(r, 1, "13 a 17 anos")
        r += 1
    for label, vals in values_by_row.items():
        ws.cell(r, 1, label)
        for j, v in enumerate(vals):
            ws.cell(r, 2 + j, v)
        r += 1
    r += 1
    ws.cell(r, 1, f"Fonte: IBGE, Diretoria de Pesquisas, Pesquisa Nacional de Saúde do Escolar {year}")
    return wb


@pytest.fixture
def build_ibge_xlsx():
    def build(values_by_row: dict[str, list[float]] | None = None, **kw) -> bytes:
        values = values_by_row or {
            "Brasil": [30.0, 28.0, 32.0, 25.0, 23.0, 27.0, 35.0, 33.0, 37.0],
            "Norte": [40.0, 36.0, 44.0, 38.0, 34.0, 42.0, 42.0, 38.0, 46.0],
        }
        bio = io.BytesIO()
        _ibge_workbook(values, **kw).save(bio)
        return bio.getvalue()
    return build


@pytest.fixture(scope="session")
def raw_dir() -> Path:
    return ROOT / "data" / "raw"


@pytest.fixture
def temp_project(tmp_path: Path) -> Path:
    """Projeto isolado: copia config/ e cria data/raw vazio."""
    shutil.copytree(ROOT / "config", tmp_path / "config")
    (tmp_path / "data" / "raw").mkdir(parents=True)
    return tmp_path

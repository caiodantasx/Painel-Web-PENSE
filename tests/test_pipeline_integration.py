"""Integração ponta a ponta em projeto temporário + rastreabilidade + idempotência."""
import json
import shutil
import zipfile

import openpyxl
import pytest
import xlrd

from pense.config import Config
from pense.exports.writers import read_csv, write_csv
from pense.pipeline import run

ARCHIVES = ["Tema_17_Seguranca_da_Escola_XLSX_20260525 (1).zip", "tab08avs.zip",
            "Amostra_1_Tema_06_Seguranca_da_Escola.xls"]


@pytest.fixture(scope="module")
def project(tmp_path_factory, raw_dir):
    root = tmp_path_factory.mktemp("proj")
    shutil.copytree(raw_dir.parent.parent / "config", root / "config")
    raw = root / "data" / "raw"
    raw.mkdir(parents=True)
    for name in ARCHIVES:
        shutil.copy(raw_dir / name, raw / name)
    (raw / "corrompido.xlsx").write_bytes(b"isto nao e uma planilha")
    res = run(Config(root=root))
    return root, res


def test_pipeline_outputs_exist(project):
    root, _ = project
    for rel in ["data/processed/inventory_files.csv", "data/processed/inventory_sheets.csv",
                "data/staging/observations_extracted.csv", "data/processed/observations_validated.csv",
                "data/processed/quality_issues.csv", "data/curated/pense_observations_approved.csv",
                "data/curated/indicator_catalog.csv", "data/curated/comparability_catalog.csv",
                "data/curated/historical_series.csv", "dashboard/data/pense_bundle.json",
                "reports/relatorio_qualidade.md", "data/processed/run_manifest.json"]:
        assert (root / rel).exists(), rel


def test_failure_in_one_file_does_not_stop_others(project):
    _, res = project
    assert any(i.rule_id == "ING010" and "corrompido" in i.source_file for i in res.issues)
    assert {r["edition_id"] for r in res.estimates} == {"PENSE_2009", "PENSE_2015_A1", "PENSE_2024"}


def test_every_approved_value_traces_back_to_its_source_cell(project):
    """Reabre o arquivo original e confere a célula de cada amostra de observações aprovadas."""
    root, res = project
    approved = [r for r in res.estimates if r["approved_for_analysis"]]
    sample = approved[:: max(1, len(approved) // 150)]
    books: dict[str, object] = {}
    for r in sample:
        container, _, member = r["source_file"].partition("!")
        key = r["source_file"]
        if key not in books:
            if member:
                with zipfile.ZipFile(root / "data" / "raw" / container) as zf:
                    data = zf.read(member)
            else:
                data = (root / "data" / "raw" / container).read_bytes()
            books[key] = (openpyxl.load_workbook(__import__("io").BytesIO(data), data_only=True)
                          if key.endswith(".xlsx") else xlrd.open_workbook(file_contents=data))
        book = books[key]
        if key.endswith(".xlsx"):
            value = book[r["source_sheet"]][r["source_cell"]].value
        else:
            sh = book.sheet_by_name(r["source_sheet"])
            col = openpyxl.utils.column_index_from_string(r["source_column"]) - 1
            value = sh.cell_value(r["source_row"] - 1, col)
        assert value == r["estimate"], (r["source_file"], r["source_sheet"], r["source_cell"])


def test_curated_layer_only_contains_approved_canonical(project):
    root, _ = project
    rows = read_csv(root / "data/curated/pense_observations_approved.csv")
    assert rows and all(r["approved_for_analysis"] == "true" and r["analytical_duplicate_of"] == "" for r in rows)
    assert all(r["data_stage"] == "approved" for r in rows)


def test_bundle_values_come_from_pipeline_records(project):
    root, res = project
    bundle = json.loads((root / "dashboard/data/pense_bundle.json").read_text(encoding="utf-8"))
    known = {round(r["estimate"], 6) for r in res.estimates if r["estimate"] is not None}
    assert all(e is None or e in known for e in bundle["obs"]["e"]), "dashboard não pode ter valor sem origem"
    assert bundle["meta"]["n_observations"] == len(bundle["obs"]["e"])


def test_run_is_idempotent(project):
    root, _ = project
    first = (root / "data/processed/observations_validated.csv").read_bytes()
    issues1 = (root / "data/processed/quality_issues.csv").read_bytes()
    run(Config(root=root))
    assert (root / "data/processed/observations_validated.csv").read_bytes() == first
    assert (root / "data/processed/quality_issues.csv").read_bytes() == issues1


def test_no_series_from_incompatible_editions_in_real_data(project):
    _, res = project
    assert res.series == []
    assert {p["final_status"] for p in res.comparability} <= {"NOT_COMPARABLE", "PENDING_REVIEW"}


def test_csv_writer_roundtrip(tmp_path):
    p = tmp_path / "x.csv"
    write_csv(p, [{"a": 0.1 + 0.2, "b": None, "c": True, "d": "Ação"}])
    row = read_csv(p)[0]
    assert row == {"a": "0.30000000000000004", "b": "", "c": "true", "d": "Ação"}
    assert p.read_bytes().startswith(b"\xef\xbb\xbf"), "BOM para abrir corretamente no Excel"

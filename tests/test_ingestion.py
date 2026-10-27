"""Descoberta de arquivos, ZIPs e leitores por formato."""
import io
import zipfile

import pytest

from pense.config import Config
from pense.ingestion.discovery import discover
from pense.ingestion.readers import ReadError, read_csv, read_grids, read_ods, read_xls, read_xlsx


def _zip(members: dict[str, bytes]) -> bytes:
    bio = io.BytesIO()
    with zipfile.ZipFile(bio, "w") as zf:
        for name, data in members.items():
            zf.writestr(name, data)
    return bio.getvalue()


def test_zip_members_are_read_in_memory_and_duplicates_detected(temp_project, build_ibge_xlsx):
    data = build_ibge_xlsx()
    raw = temp_project / "data" / "raw"
    (raw / "a.zip").write_bytes(_zip({"Tabelas 1.1.xlsx": data}))
    (raw / "copia.zip").write_bytes(_zip({"Tabelas 1.1.xlsx": data, "leia-me.txt": b"x"}))
    (raw / "solta.xlsx").write_bytes(data)
    res = discover(Config(root=temp_project))
    assert len(res.items) == 1, "o mesmo conteúdo deve ser processado uma única vez"
    dups = [s for s in res.all_sources if s.duplicate_of]
    assert {s.source_id for s in dups} == {"copia.zip!Tabelas 1.1.xlsx", "solta.xlsx"}
    assert res.items[0].source.source_id == "a.zip!Tabelas 1.1.xlsx"
    assert res.items[0].source.container == "a.zip"


def test_zip_slip_names_never_touch_disk(temp_project, build_ibge_xlsx):
    raw = temp_project / "data" / "raw"
    (raw / "mal.zip").write_bytes(_zip({"../../fora.xlsx": build_ibge_xlsx()}))
    res = discover(Config(root=temp_project))
    assert not (temp_project.parent / "fora.xlsx").exists()
    assert res.items[0].source.file_name == "fora.xlsx"
    assert any(i.rule_id == "ING008" for i in res.issues)


def test_corrupted_zip_and_unsupported_files_are_reported_not_fatal(temp_project, build_ibge_xlsx):
    raw = temp_project / "data" / "raw"
    (raw / "quebrado.zip").write_bytes(b"isto nao e um zip")
    (raw / "nota.docx").write_bytes(b"x")
    (raw / "ok.xlsx").write_bytes(build_ibge_xlsx())
    res = discover(Config(root=temp_project))
    rules = {i.rule_id for i in res.issues}
    assert "ING004" in rules and "ING001" in rules
    assert len(res.items) == 1


def test_nested_zip_respects_depth_limit(temp_project, build_ibge_xlsx):
    inner = _zip({"t.xlsx": build_ibge_xlsx()})
    outer = _zip({"inner.zip": _zip({"inner2.zip": inner})})
    (temp_project / "data" / "raw" / "outer.zip").write_bytes(outer)
    res = discover(Config(root=temp_project))
    assert any(i.rule_id == "ING003" for i in res.issues)


def test_xlsx_reader_preserves_merges(src_factory, build_ibge_xlsx):
    g = read_xlsx(src_factory(), build_ibge_xlsx())[0]
    assert g.sheet == "1.1.1"
    assert g.merge_info == "native" and len(g.merges) > 5
    assert g.merged_text(5, 3) == "Total"  # D6 pertence à mesclagem B5:D6


def test_xls_reader_reads_legacy_file_with_merges(raw_dir, src_factory):
    with zipfile.ZipFile(raw_dir / "tab08avs.zip") as zf:
        data = zf.read("tab801.xls")
    g = read_xls(src_factory("tab801.xls", "xls"), data)[0]
    assert g.sheet == "tab 8.1" and g.merges
    assert g.text(11, 0) == "Porto Velho"
    assert g.raw(10, 1) == pytest.approx(6.403346390648046)


def test_csv_reader_detects_semicolon_and_latin1(src_factory):
    data = "Território;Percentual\nBrasil;12,5\nAmapá;7,1\n".encode("cp1252")
    g = read_csv(src_factory("t.csv", "csv"), data)[0]
    assert g.text(2, 0) == "Amapá" and g.text(1, 1) == "12,5"
    assert g.merge_info == "unavailable"


def test_ods_reader_reads_spans_as_merges(tmp_path, src_factory):
    from odf.opendocument import OpenDocumentSpreadsheet
    from odf.table import CoveredTableCell, Table, TableCell, TableRow
    from odf.text import P

    doc = OpenDocumentSpreadsheet()
    t = Table(name="1.1.1")
    r1 = TableRow()
    c = TableCell(numbercolumnsspanned=2)
    c.addElement(P(text="Sexo"))
    r1.addElement(TableCell())
    r1.addElement(c)
    r1.addElement(CoveredTableCell())
    t.addElement(r1)
    r2 = TableRow()
    r2.addElement(TableCell(valuetype="string"))
    for v in (1.5, 2.5):
        cell = TableCell(valuetype="float", value=v)
        cell.addElement(P(text=str(v)))
        r2.addElement(cell)
    t.addElement(r2)
    doc.spreadsheet.addElement(t)
    path = tmp_path / "x.ods"
    doc.save(str(path))
    g = read_ods(src_factory("x.ods", "ods"), path.read_bytes())[0]
    assert g.merges and g.merged_text(0, 2) == "Sexo"
    assert g.raw(1, 2) == 2.5


def test_unreadable_file_raises_read_error(src_factory):
    with pytest.raises(ReadError):
        read_grids(src_factory("ruim.xlsx", "xlsx"), b"nao e um xlsx")

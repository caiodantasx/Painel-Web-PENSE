"""Converte os dicionários de microdados do IBGE (2009, 2012, 2015 A1/A2, 2019, 2024) em CSV.

Saída: config/reference/dicionario_<EDIÇÃO>.csv com uma linha por categoria:
edition_id, sheet, variable, description, code, code_label, start, length

* start/length existem só nos arquivos de largura fixa (2009 e 2012) e são usados para ler
  os microdados (ver pense.microdata.run);
* nada é digitado à mão: cada formato de dicionário tem um leitor próprio.

Entradas em data/reference/dicionarios/ (cópias dos arquivos do IBGE).
Uso:  python scripts/build_dictionaries.py
"""
from __future__ import annotations

import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "data" / "reference" / "dicionarios"
OUT = ROOT / "config" / "reference"
FIELDS = ["edition_id", "sheet", "variable", "description", "code", "code_label", "start", "length"]
_VAR = re.compile(r"^[A-Za-z][A-Za-z0-9_]*$")


def _num(v) -> str:
    if isinstance(v, float) and v.is_integer():
        return str(int(v))
    return str(v).strip()


def _split_domain(text: str) -> list[tuple[str, str]]:
    """'1;Sim\\n2;Não' ou '1 - norte\\n2 - nordeste' ou '1-SIM,2-NÃO' → [(código, rótulo)]."""
    out = []
    text = str(text or "").replace("\r", "\n")
    parts = re.split(r"\n|,(?=\s*-?\d+\s*[-;])|;(?=\s*-?\d+\s*[-;])", text)
    for p in parts:
        m = re.match(r"^\s*(-?\d+)\s*[;\-–:]\s*(.+?)\s*$", p)
        if m:
            out.append((m.group(1), m.group(2)))
    return out


def stacked_xls(path: Path, edition: str, two_col: bool) -> list[dict]:
    """2015 (2 colunas) e 2019 (4 colunas): linha da variável seguida de linhas de categoria."""
    import xlrd

    rows: list[dict] = []
    book = xlrd.open_workbook(str(path))
    for sh in book.sheets():
        var = desc = ""
        for r in range(sh.nrows):
            v = [sh.cell_value(r, c) for c in range(sh.ncols)]
            first = _num(v[0])
            if two_col:
                if first and _VAR.match(first) and not first.isdigit() and str(v[1]).strip():
                    var, desc = first, str(v[1]).strip()
                    rows.append(dict(edition_id=edition, sheet=sh.name, variable=var, description=desc, code="", code_label=""))
                elif var and re.match(r"^-?\d+$", first) and str(v[1]).strip():
                    rows.append(dict(edition_id=edition, sheet=sh.name, variable=var, description=desc, code=first,
                                     code_label=str(v[1]).strip()))
            else:
                code, label = (_num(v[2]), str(v[3]).strip()) if sh.ncols >= 4 else ("", "")
                if first and _VAR.match(first) and str(v[1]).strip() and first not in ("Código",):
                    var, desc = first, str(v[1]).strip()
                    rows.append(dict(edition_id=edition, sheet=sh.name, variable=var, description=desc,
                                     code=code, code_label=label))
                elif var and not first and code != "" and label:
                    rows.append(dict(edition_id=edition, sheet=sh.name, variable=var, description=desc,
                                     code=code, code_label=label))
    return rows


def xlsx_2024(path: Path) -> list[dict]:
    import openpyxl

    rows = []
    wb = openpyxl.load_workbook(path, read_only=True)
    for ws in wb.worksheets:
        for r in list(ws.iter_rows(values_only=True))[1:]:
            if not r or not r[2]:
                continue
            var, desc, cat = str(r[2]).strip(), str(r[3] or "").strip(), r[4]
            cats = _split_domain(cat) if cat else []
            if not cats:
                rows.append(dict(edition_id="PENSE_2024", sheet=ws.title, variable=var, description=desc, code="", code_label=""))
            for code, label in cats:
                rows.append(dict(edition_id="PENSE_2024", sheet=ws.title, variable=var, description=desc, code=code,
                                 code_label=label))
    return rows


def fixed_width_xls(path: Path, edition: str, cols: dict[str, int]) -> list[dict]:
    """2009 e 2012: CAMPO/VARIÁVEL, INÍCIO, TÉRMINO|TAMANHO, DESCRIÇÃO, DOMÍNIO."""
    import xlrd

    rows = []
    book = xlrd.open_workbook(str(path))
    for sh in book.sheets():
        for r in range(1, sh.nrows):
            v = sh.row_values(r)
            var = _num(v[cols["var"]])
            if not var or not _VAR.match(var):
                continue
            start = int(float(v[cols["start"]])) if str(v[cols["start"]]).strip() else ""
            if "end" in cols:
                length = int(float(v[cols["end"]])) - start + 1 if start != "" else ""
            else:
                length = int(float(v[cols["len"]])) if str(v[cols["len"]]).strip() else ""
            desc = str(v[cols["desc"]]).strip()
            cats = _split_domain(v[cols["dom"]])
            base = dict(edition_id=edition, sheet=sh.name, variable=var, description=desc, start=start, length=length)
            if not cats:
                rows.append(dict(base, code="", code_label=""))
            for code, label in cats:
                rows.append(dict(base, code=code, code_label=label))
    return rows


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    jobs = {
        "PENSE_2009": lambda: fixed_width_xls(SRC / "Dicionario_Base_Pense_Completa_2009.xls", "PENSE_2009",
                                              {"var": 0, "start": 2, "end": 3, "desc": 5, "dom": 6}),
        "PENSE_2012": lambda: fixed_width_xls(SRC / "Dicionario_PENSE_2012_VF.xls", "PENSE_2012",
                                              {"var": 0, "start": 2, "len": 3, "desc": 5, "dom": 6}),
        "PENSE_2015_A1": lambda: stacked_xls(SRC / "Dicionario_PENSE_Microdados_Amostra1.xls", "PENSE_2015_A1", True),
        "PENSE_2015_A2": lambda: stacked_xls(SRC / "Dicionario_PENSE_Microdados_AMOSTRA2.xls", "PENSE_2015_A2", True),
        "PENSE_2019": lambda: stacked_xls(SRC / "Dicionario_PENSE2019_Microdados.xls", "PENSE_2019", False),
        "PENSE_2024": lambda: xlsx_2024(SRC / "Dicionario_Microdados_PeNSE2024.xlsx"),
    }
    for ed, job in jobs.items():
        rows = job()
        with (OUT / f"dicionario_{ed}.csv").open("w", encoding="utf-8-sig", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=FIELDS, extrasaction="ignore", lineterminator="\n")
            w.writeheader()
            w.writerows(rows)
        print(f"{ed}: {len({r['variable'] for r in rows})} variáveis, {len(rows)} linhas")


if __name__ == "__main__":
    main()

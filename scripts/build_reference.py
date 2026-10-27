"""Extrai documentos de referência do IBGE para CSV versionável (config/reference/).

Entradas (data/reference/, cópias dos originais):
* Guia_Tabelas_PeNSE_2024_20260525.xlsx — catálogo oficial das abas da PeNSE 2024
  (uma aba do guia por tema; colunas "Nome da aba" e "Título da tabela").
* questionario_pense_2015_aluno.pdf (IBGE, doc4595) — questionário do aluno da PeNSE 2015,
  com código da variável, pergunta, opções, pulos/filtros e legenda de cores
  (vermelho = alterada, verde = nova, azul = pulos, filtros, críticas e alertas).

Saídas:
* config/reference/guia_tabelas_pense_2024.csv
* config/reference/questionario_pense_2015_aluno.csv

O PDF é lido pelas cores e posições reais do texto (pdfplumber): a página tem duas
colunas, lidas da esquerda para a direita. Nada é reescrito à mão; o que não for
reconhecido como pergunta fica fora do CSV e é contado no resumo impresso.

Uso:  python scripts/build_reference.py
"""
from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from pense.parsing.title import period_code  # noqa: E402

REF_IN = ROOT / "data" / "reference"
REF_OUT = ROOT / "config" / "reference"
GUIDE = REF_IN / "Guia_Tabelas_PeNSE_2024_20260525.xlsx"
QUEST_2015 = REF_IN / "questionario_pense_2015_aluno.pdf"

RED, GREEN, BLUE = (1.0, 0.0, 0.0), (0.0, 0.5, 0.0), (0.0, 0.0, 1.0)
_CODE = re.compile(r"^B\d{5}[a-z0-9]*$")
_SECTION = re.compile(r"^(B\d{1,2})\.\s+(.+)$")
_NUMBER = re.compile(r"^(\d{1,2})\.\s+(.*)$")
_PERIOD = re.compile(r"(NOS ÚLTIMOS \d+ (?:DIAS|MESES)|ALGUMA VEZ NA VIDA|NA SUA VIDA)", re.I)


def build_guide() -> list[dict[str, str]]:
    import openpyxl

    wb = openpyxl.load_workbook(GUIDE, read_only=True)
    out = []
    for ws in wb.worksheets:
        rows = list(ws.iter_rows(values_only=True))
        theme_title = str(rows[0][0] or "")
        m = re.match(r"^(\d+)\s*-\s*(.+)$", theme_title)
        theme_id, theme_name = (m.group(1).lstrip("0"), m.group(2).strip()) if m else (ws.title, theme_title)
        for r in rows[2:]:
            if not r or not r[0]:
                continue
            sheet = str(r[0]).strip()
            is_cv = sheet.endswith("(CV)")
            table_id = sheet.replace("(CV)", "").strip()
            parts = table_id.split(".")
            out.append({
                "edition_id": "PENSE_2024", "theme_id": theme_id, "theme_name": theme_name,
                "sheet_name": sheet, "table_id": table_id, "table_family_id": ".".join(parts[:2]),
                "territorial_cut": {"1": "region", "2": "uf", "3": "capital"}.get(parts[-1], "PENDENTE") if len(parts) == 3 else "PENDENTE",
                "measure_sheet": "cv" if is_cv else "estimativa",
                "title": " ".join(str(r[1] or "").split()),
                "source": f"{GUIDE.name}!{ws.title}",
            })
    return out


def _lines(page) -> list[list[dict]]:
    """Linhas de texto em ordem de leitura (coluna esquerda, depois direita)."""
    words = page.extract_words(extra_attrs=["non_stroking_color", "fontname"], keep_blank_chars=False)
    mid = page.width / 2
    cols: dict[int, dict[int, list[dict]]] = {0: {}, 1: {}}
    for w in words:
        if w["top"] > page.height - 80 and re.fullmatch(r"\d{1,2}", w["text"]):
            continue  # número da página
        col = 0 if w["x0"] < mid - 4 else 1
        key = round(w["top"] / 3)
        cols[col].setdefault(key, []).append(w)
    out = []
    for col in (0, 1):
        for key in sorted(cols[col]):
            out.append(sorted(cols[col][key], key=lambda w: w["x0"]))
    return out


def _color(w: dict) -> tuple:
    c = w.get("non_stroking_color") or (0, 0, 0)
    return tuple(round(float(x), 2) for x in c)[:3]


def build_questionnaire() -> tuple[list[dict[str, str]], int]:
    import pdfplumber

    rows: list[dict[str, str]] = []
    section, section_name = "", ""
    q: dict | None = None
    context: list[str] = []
    skipped = 0

    def close() -> None:
        nonlocal q
        if q:
            q["question_text"] = " ".join(q.pop("_text")).strip()
            m = _NUMBER.match(q["question_text"])
            if m:
                q["question_number"], q["question_text"] = m.group(1), m.group(2)
            p = _PERIOD.search(q["question_text"])
            q["reference_period"] = p.group(1).lower() if p else ""
            q["reference_period_code"] = period_code(q["reference_period"]) if p else ""
            q["options"] = " | ".join(q.pop("_opts"))
            q["filters_and_checks"] = " ".join(q.pop("_blue")).strip()
            rows.append(q)
        q = None

    with pdfplumber.open(QUEST_2015) as pdf:
        for pno, page in enumerate(pdf.pages, start=1):
            for line in _lines(page):
                black = " ".join(w["text"] for w in line if _color(w) != BLUE).strip()
                blue = " ".join(w["text"] for w in line if _color(w) == BLUE).strip()
                first = line[0]
                if _CODE.match(first["text"]):
                    close()
                    c = _color(first)
                    q = {"edition_id": "PENSE_2015", "questionnaire": "ALUNO", "section": section,
                         "section_name": section_name, "variable": first["text"], "question_number": "",
                         "change_vs_previous": "ALTERADA" if c == RED else "NOVA" if c == GREEN else "MANTIDA",
                         "context": " ".join(context).strip(), "page": str(pno), "source": QUEST_2015.name,
                         "_text": [], "_opts": [], "_blue": [blue] if blue else []}
                    context = []
                    continue
                ms = _SECTION.match(black)
                if ms and "Bold" in first["fontname"] and _color(first) == (0.0, 0.0, 0.0):
                    close()
                    section = ms.group(1)
                    section_name = re.sub(r"\s*\[.*$", "", ms.group(2)).strip()
                    context = []
                    continue
                if q is None:
                    if black:
                        context.append(black)
                    else:
                        skipped += 1
                    continue
                if black.startswith("□"):
                    opt = black.lstrip("□ ").strip()
                    q["_opts"].append(opt + (f" [{blue.strip('[]')}]" if blue else ""))
                    continue
                if blue and not black:
                    q["_blue"].append(blue)
                    continue
                if q["_opts"] and not black[:1].isupper():
                    # opção que quebrou em duas linhas ("…no banco da" / "frente nos últimos 30 dias")
                    q["_opts"][-1] = (q["_opts"][-1] + " " + black + (f" [{blue.strip('[]')}]" if blue else "")).strip()
                    continue
                if q["_opts"]:
                    # texto preto depois das opções = introdução do bloco seguinte
                    close()
                    context.append(black)
                    continue
                q["_text"].append(black)
                if blue:
                    q["_blue"].append(blue)
    close()
    return rows, skipped


def main() -> None:
    REF_OUT.mkdir(parents=True, exist_ok=True)
    guide = build_guide()
    _write(REF_OUT / "guia_tabelas_pense_2024.csv", guide)
    quest, skipped = build_questionnaire()
    _write(REF_OUT / "questionario_pense_2015_aluno.csv", quest)
    themes = sorted({(int(r["theme_id"]), r["theme_name"]) for r in guide})
    print(f"Guia 2024: {len(guide)} abas em {len(themes)} temas")
    print(f"Questionário 2015 (aluno): {len(quest)} perguntas; linhas fora de pergunta: {skipped}")


def _write(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


if __name__ == "__main__":
    main()

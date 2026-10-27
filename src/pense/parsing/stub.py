"""Leitura da coluna indicadora (stub): rótulos de grupo e linhas de dados.

Nas tabelas do IBGE, linhas sem valores funcionam como cabeçalho de seção
("Total", "13 a 15 anos", "Homem", "Pública"); as linhas seguintes, até a
próxima seção, pertencem àquele recorte. As seções são mutuamente exclusivas
(não aninhadas) em todas as famílias inspecionadas; se uma seção tiver rótulo
desconhecido, ela é marcada para revisão em vez de ser descartada.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from ..text import compact, parse_cell, slug
from .grid import Grid
from .header import MeasureBlock, Vocab
from .title import year_label

_FOOTNOTE = re.compile(r"^(fonte|nota|notas|obs)\b")
_NOTE_MARK = re.compile(r"\s*\(\d+\)\s*$|\s+\d\)$")


@dataclass
class RowSpec:
    row: int
    label: str
    kind: str  # data | group | blank | footnote
    group_dim: str = ""     # age_group | sex | admin_dependency | total | unknown
    group_value: str = ""
    group_label: str = ""
    context: dict[str, str] = field(default_factory=dict)
    context_label: str = ""


@dataclass
class StubLayout:
    rows: list[RowSpec]
    footnote_start: int | None
    problems: list[tuple[str, str, str]]


def strip_note_marker(label: str) -> str:
    return _NOTE_MARK.sub("", label).strip()


def classify_group_label(label: str, vocab: Vocab, population_ages: tuple[int, int] | None) -> tuple[str, str]:
    c = compact(label)
    s = slug(label)
    if c in vocab.total_labels:
        return "total", "Total"
    if year_label(label):
        return "year", year_label(label)
    m = vocab.age_row_pattern.match(s)
    if m:
        lo, hi = int(m.group(1)), int(m.group(3))
        if population_ages and (lo, hi) == population_ages:
            return "total", "Total"  # "13 a 17 anos" == universo da tabela
        return "age_group", f"{lo} {'a' if m.group(2) == 'a' else 'e'} {hi} anos"
    if c in vocab.dim_values:
        return vocab.dim_values[c]
    return "unknown", label


def parse_stub(grid: Grid, body_start: int, blocks: list[MeasureBlock], vocab: Vocab,
               symbols: frozenset[str], population_ages: tuple[int, int] | None) -> StubLayout:
    value_cols = sorted({c for b in blocks for c in b.columns()})
    rows: list[RowSpec] = []
    problems: list[tuple[str, str, str]] = []
    context: dict[str, str] = {}
    context_label = ""
    footnote_start = None
    for r in range(body_start, grid.nrows):
        label = grid.text(r, 0)
        if label and _FOOTNOTE.match(slug(label)):
            footnote_start = r
            break
        kinds = [parse_cell(grid.raw(r, c), symbols).kind for c in value_cols]
        has_values = any(k in ("number", "symbol", "excel_error") for k in kinds)
        has_text = any(k == "text" for k in kinds)
        if not label and not has_values:
            if has_text:
                problems.append(("STB003", "Linha com texto inesperado nas colunas de dados", grid.ref(r, 1)))
            rows.append(RowSpec(r, "", "blank"))
            continue
        if label and not has_values:
            dim, value = classify_group_label(label, vocab, population_ages)
            if dim == "unknown":
                problems.append(("STB001", f"Rótulo de seção não reconhecido: '{label}'", grid.ref(r, 0)))
            context = {} if dim == "total" else {dim: value}
            context_label = label
            rows.append(RowSpec(r, label, "group", dim, value, label, dict(context), context_label))
            continue
        if label and has_values:
            dim, value = classify_group_label(label, vocab, population_ages)
            if dim in ("age_group", "sex", "admin_dependency", "year"):
                # Rótulo de seção com números (ex.: PeNSE 2019, tabela 9.10.1): se os números repetem a
                # linha seguinte, é artefato da publicação — vira seção e o artefato é registrado.
                same = r + 1 < grid.nrows and all(
                    parse_cell(grid.raw(r, c), symbols).value == parse_cell(grid.raw(r + 1, c), symbols).value
                    for c in value_cols)
                code = "STB004" if same else "STB005"
                msg = ("Linha de seção com valores repetidos da linha seguinte (artefato da publicação); tratada como seção"
                       if same else "Linha de seção com valores próprios; tratada como seção e valores não extraídos")
                problems.append((code, f"{msg}: '{label}'", grid.ref(r, 0)))
                context = {dim: value}
                context_label = label
                rows.append(RowSpec(r, label, "group", dim, value, label, dict(context), context_label))
                continue
        if not label:
            problems.append(("STB002", "Linha com valores mas sem rótulo de território", grid.ref(r, 0)))
        rows.append(RowSpec(r, strip_note_marker(label), "data", context=dict(context),
                            context_label=context_label))
    return StubLayout(rows, footnote_start, problems)

"""Leitura do cabeçalho multinível a partir das células mescladas.

Para cada coluna de dados, monta-se o *caminho* de rótulos de cima para baixo
(ex.: ``[enunciado, "Sexo", "Homem", "Intervalo de confiança de 95%",
"Limite inferior"]``). O caminho é então classificado com o vocabulário
controlado em ``config/vocabulary.toml``:

* folha -> papel da coluna (estimativa, limite inferior/superior, CV);
* rótulos de dimensão -> sexo / dependência administrativa;
* demais rótulos -> categoria de resposta (e grupo de categoria).

Colunas que compartilham enunciado, dimensões e categoria formam um *bloco de
medida* (estimativa + IC ou estimativa + CV). Nenhuma posição de coluna é
presumida: tudo vem do texto do cabeçalho.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from ..text import clean_text, compact, parse_cell, slug
from .grid import Grid
from .title import year_label

ROLE_ESTIMATE, ROLE_LO, ROLE_HI, ROLE_CV, ROLE_UNKNOWN = "estimate", "ci_lower", "ci_upper", "cv", "unknown"

_UNIT_MARK = re.compile(r"\s*\(%\)")
_NOTE_MARK = re.compile(r"\s*\(\d+\)")


def strip_label_marks(label: str) -> str:
    """Remove marcas de unidade "(%)" e de nota "(1)" de rótulos de categoria.

    O rótulo completo continua preservado em ``header_path`` para auditoria.
    """
    return _NOTE_MARK.sub("", _UNIT_MARK.sub("", clean_text(label))).strip()


@dataclass
class Vocab:
    """Vocabulário compilado (formas compactas) para classificação rápida."""

    leaf: dict[str, str]
    ci_containers: list[str]
    statement_prefixes: dict[str, list[str]]
    dim_containers: dict[str, str]
    dim_values: dict[str, tuple[str, str]]
    total_labels: set[str]
    continuation: set[str]
    age_row_pattern: re.Pattern[str]
    dim_names: dict[str, str]

    @classmethod
    def from_config(cls, vocab: dict[str, Any]) -> "Vocab":
        leaf: dict[str, str] = {}
        for role, labels in vocab["measure_leaf"].items():
            for lab in labels:
                leaf[compact(lab)] = role
        dim_containers, dim_values, dim_names = {}, {}, {}
        for dim, spec in vocab["dimensions"].items():
            dim_names[dim] = spec.get("label", dim)
            for c in spec.get("containers", []):
                dim_containers[compact(c)] = dim
            for k, v in spec.get("values", {}).items():
                dim_values[compact(k)] = (dim, v)
        return cls(
            leaf=leaf,
            ci_containers=[compact(x) for x in vocab["measure_containers"]["ci"]],
            statement_prefixes={k: [slug(p) for p in v] for k, v in vocab["statement_prefixes"].items()},
            dim_containers=dim_containers,
            dim_values=dim_values,
            total_labels={compact(x) for x in vocab["total_labels"]["values"]},
            continuation={compact(x) for x in vocab["continuation_markers"]["values"]},
            age_row_pattern=re.compile(vocab["dimensions"]["age_group"]["row_pattern"]),
            dim_names=dim_names,
        )

    def statement_kind(self, label: str) -> str:
        s = slug(label)
        for kind, prefixes in self.statement_prefixes.items():
            if any(s.startswith(p) for p in prefixes):
                return kind
        return ""

    def is_ci_container(self, label: str) -> bool:
        c = compact(label)
        return any(c.startswith(x) for x in self.ci_containers)

    def is_continuation(self, label: str) -> bool:
        return compact(label) in self.continuation


@dataclass
class ColumnSpec:
    col: int
    path: list[str]
    path_cells: list[tuple[int, int]]
    role: str = ROLE_UNKNOWN
    statement: str = ""
    statement_kind: str = ""
    dims: dict[str, str] = field(default_factory=dict)
    dim_labels: dict[str, str] = field(default_factory=dict)
    category_path: list[str] = field(default_factory=list)
    ci_level: int | None = None

    @property
    def block_key(self) -> tuple[Any, ...]:
        return (self.statement, tuple(sorted(self.dims.items())), tuple(self.category_path))


@dataclass
class MeasureBlock:
    key: tuple[Any, ...]
    statement: str
    statement_kind: str
    dims: dict[str, str]
    dim_labels: dict[str, str]
    category_path: list[str]
    estimate_col: int | None = None
    ci_lower_col: int | None = None
    ci_upper_col: int | None = None
    cv_col: int | None = None
    ci_level: int | None = None
    header_path: str = ""

    @property
    def category(self) -> str:
        return self.category_path[-1] if self.category_path else ""

    @property
    def category_group(self) -> str:
        return " > ".join(self.category_path[:-1])

    def columns(self) -> list[int]:
        return [c for c in (self.estimate_col, self.ci_lower_col, self.ci_upper_col, self.cv_col) if c is not None]


@dataclass
class HeaderLayout:
    header_rows: list[int]
    body_start: int
    stub_header: str
    columns: list[ColumnSpec]
    blocks: list[MeasureBlock]
    problems: list[tuple[str, str, str]]  # (rule, mensagem, célula)
    inferred_without_merges: bool = False


def _is_year_label_row(grid: Grid, r: int, symbols: frozenset[str]) -> bool:
    """Linha de cabeçalho com anos ("2009 | 2012"), que o Excel guarda como números.

    Só vale se a coluna do território estiver vazia e todas as células numéricas forem
    anos inteiros — linhas de dados sempre têm rótulo de território.
    """
    if grid.text(r, 0):
        return False
    nums = []
    for c in range(1, grid.ncols):
        pv = parse_cell(grid.raw(r, c), symbols)
        if pv.kind in ("symbol", "excel_error"):
            return False
        if pv.kind == "number":
            nums.append(pv.value)
    return bool(nums) and all(float(v).is_integer() and 1990 <= v <= 2099 for v in nums)


def _first_value_row(grid: Grid, start: int, symbols: frozenset[str]) -> int | None:
    for r in range(start, grid.nrows):
        if _is_year_label_row(grid, r, symbols):
            continue
        for c in range(1, grid.ncols):
            pv = parse_cell(grid.raw(r, c), symbols)
            if pv.kind in ("number", "symbol", "excel_error"):
                return r
    return None


def _column_path_native(grid: Grid, rows: list[int], c: int) -> tuple[list[str], list[tuple[int, int]]]:
    path, cells, seen = [], [], set()
    for r in rows:
        anchor = grid.anchor(r, c)
        if anchor in seen:
            continue
        t = grid.text(*anchor)
        if t:
            seen.add(anchor)
            path.append(t)
            cells.append(anchor)
    return path, cells


def _column_paths_inferred(grid: Grid, rows: list[int]) -> dict[int, tuple[list[str], list[tuple[int, int]]]]:
    """Sem mesclagens (CSV/ODS simples): preenche à direita dentro do grupo-pai.

    Um rótulo vazio herda o rótulo à esquerda na mesma linha somente se a
    coluna tiver o mesmo caminho-pai da coluna de onde o rótulo vem.
    """
    paths: dict[int, tuple[list[str], list[tuple[int, int]]]] = {c: ([], []) for c in range(1, grid.ncols)}
    for r in rows:
        last_label, last_cell, last_parent = "", None, None
        for c in range(1, grid.ncols):
            parent = tuple(paths[c][0])
            t = grid.text(r, c)
            if t:
                last_label, last_cell, last_parent = t, (r, c), parent
            elif last_label and parent == last_parent and r != rows[-1]:
                t = last_label
            if t:
                paths[c][0].append(t)
                paths[c][1].append(last_cell if last_cell else (r, c))
    return paths


def parse_header(grid: Grid, title_rows: list[int], vocab: Vocab, symbols: frozenset[str],
                 title_statement: str = "") -> HeaderLayout | None:
    problems: list[tuple[str, str, str]] = []
    start = (max(title_rows) + 1) if title_rows else 0
    first_val = _first_value_row(grid, start, symbols)
    if first_val is None:
        return None
    header_rows = []
    stub_header = ""
    for r in range(start, first_val):
        texts = [grid.text(r, c) for c in range(1, grid.ncols)]
        meaningful = [t for t in texts if t and not vocab.is_continuation(t)]
        if meaningful:
            header_rows.append(r)
            if not stub_header and grid.text(r, 0):
                stub_header = grid.text(r, 0)
    if not header_rows:
        return None
    body_start = header_rows[-1] + 1
    inferred = grid.merge_info != "native"
    inferred_paths = _column_paths_inferred(grid, header_rows) if inferred else {}
    if inferred:
        problems.append(("HDR005", "Aba sem informação de células mescladas; caminhos de cabeçalho inferidos "
                                   "por preenchimento à direita — revisar.", ""))

    columns: list[ColumnSpec] = []
    for c in range(1, grid.ncols):
        path, cells = inferred_paths[c] if inferred else _column_path_native(grid, header_rows, c)
        path = [p for p in path if not vocab.is_continuation(p)]
        if not path:
            continue
        spec = ColumnSpec(col=c, path=path, path_cells=cells)
        _classify_column(spec, vocab, title_statement)
        columns.append(spec)

    blocks = _build_blocks(columns, grid, problems)
    _check_structure(blocks, problems)
    return HeaderLayout(header_rows, body_start, stub_header, columns, blocks, problems, inferred)


def _classify_column(spec: ColumnSpec, vocab: Vocab, title_statement: str) -> None:
    labels = list(spec.path)
    leaf_role = vocab.leaf.get(compact(labels[-1]))
    if leaf_role:
        spec.role = leaf_role
        labels = labels[:-1]
    remaining = []
    for lab in labels:
        if vocab.is_ci_container(lab):
            m = re.search(r"(\d{2})\s*%", lab)
            spec.ci_level = int(m.group(1)) if m else None
            continue
        kind = vocab.statement_kind(lab)
        if kind and not spec.statement:
            spec.statement = re.sub(r"\s*\(%\)\s*$", "", clean_text(lab))
            spec.statement_kind = kind
            continue
        remaining.append(lab)
    if not spec.statement:
        spec.statement = title_statement
        spec.statement_kind = vocab.statement_kind(title_statement)
    for lab in remaining:
        c = compact(lab)
        if year_label(lab):
            # Coluna de um ano específico (tabela multianual): ano é dimensão, não categoria.
            spec.dims["year"] = year_label(lab)
            spec.dim_labels["year"] = clean_text(lab)
            continue
        if c in vocab.dim_containers:
            continue
        if c in vocab.dim_values:
            dim, canonical = vocab.dim_values[c]
            spec.dims[dim] = canonical
            spec.dim_labels[dim] = clean_text(lab)
            continue
        if c in vocab.total_labels:
            continue
        spec.category_path.append(strip_label_marks(lab))


def _build_blocks(columns: list[ColumnSpec], grid: Grid,
                  problems: list[tuple[str, str, str]]) -> list[MeasureBlock]:
    blocks: dict[tuple[Any, ...], MeasureBlock] = {}
    for spec in columns:
        if spec.role == ROLE_UNKNOWN:
            problems.append(("HDR001", f"Coluna não interpretada (rótulo final '{spec.path[-1]}')",
                             grid.ref(spec.path_cells[-1][0], spec.col)))
            continue
        key = spec.block_key
        blk = blocks.get(key)
        if blk is None:
            blk = MeasureBlock(key=key, statement=spec.statement, statement_kind=spec.statement_kind,
                               dims=dict(spec.dims), dim_labels=dict(spec.dim_labels),
                               category_path=list(spec.category_path))
            blocks[key] = blk
        attr = {"estimate": "estimate_col", "ci_lower": "ci_lower_col",
                "ci_upper": "ci_upper_col", "cv": "cv_col"}[spec.role]
        if getattr(blk, attr) is not None:
            problems.append(("HDR002", f"Mais de uma coluna com papel '{spec.role}' no mesmo bloco",
                             grid.ref(spec.path_cells[-1][0], spec.col)))
            continue
        setattr(blk, attr, spec.col)
        if spec.ci_level:
            blk.ci_level = spec.ci_level
        if spec.role == "estimate":
            blk.header_path = " > ".join(spec.path)
    out = []
    for blk in blocks.values():
        if blk.estimate_col is None:
            problems.append(("HDR003", f"Bloco sem coluna de estimativa: {blk.key}", ""))
            continue
        if (blk.ci_lower_col is None) != (blk.ci_upper_col is None):
            problems.append(("HDR004", f"Bloco com apenas um limite do IC: {blk.header_path}", ""))
        out.append(blk)
    return sorted(out, key=lambda b: b.estimate_col or 0)


def _check_structure(blocks: list[MeasureBlock], problems: list[tuple[str, str, str]]) -> None:
    """Detecta cabeçalhos assimétricos que exigem interpretação humana.

    Ex.: tabela 8.1 (2009) tem colunas por categoria ("Local") e colunas por
    dependência administrativa sem categoria e sem coluna total geral — não é
    possível afirmar, só pelo cabeçalho, a qual indicador as colunas por
    dependência se referem.
    """
    by_statement: dict[str, list[MeasureBlock]] = {}
    for b in blocks:
        by_statement.setdefault(b.statement, []).append(b)
    for _statement, blks in by_statement.items():
        with_cat = [b for b in blks if b.category_path]
        no_cat_dims = [b for b in blks if not b.category_path and b.dims]
        overall = [b for b in blks if not b.category_path and not b.dims]
        if with_cat and no_cat_dims and not overall:
            problems.append((
                "HDR006",
                "Cabeçalho assimétrico: há colunas por categoria e colunas por dimensão sem categoria, "
                "sem coluna total geral. As colunas por dimensão foram registradas como indicador geral "
                "(sem categoria) e marcadas para revisão.",
                "",
            ))

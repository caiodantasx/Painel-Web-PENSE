"""Representação neutra de uma aba: matriz de valores + células mescladas.

Os adaptadores trabalham sobre ``Grid`` e nunca sobre objetos específicos de
openpyxl/xlrd, o que permite tratar XLSX, XLS, ODS e CSV da mesma forma.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ..models import SourceFile
from ..text import cell_ref, clean_text


@dataclass(frozen=True)
class Merge:
    """Intervalo mesclado, índices base 0 e inclusivos."""

    r0: int
    r1: int
    c0: int
    c1: int

    def contains(self, r: int, c: int) -> bool:
        return self.r0 <= r <= self.r1 and self.c0 <= c <= self.c1


@dataclass
class Grid:
    source: SourceFile
    sheet: str
    sheet_index: int
    values: list[list[Any]]
    merges: list[Merge] = field(default_factory=list)
    merge_info: str = "native"  # native | unavailable
    _anchor: dict[tuple[int, int], tuple[int, int]] = field(default_factory=dict, repr=False)

    def __post_init__(self) -> None:
        self._trim()
        for m in self.merges:
            for r in range(m.r0, m.r1 + 1):
                for c in range(m.c0, m.c1 + 1):
                    self._anchor[(r, c)] = (m.r0, m.c0)

    def _trim(self) -> None:
        """Remove linhas/colunas finais vazias (ex.: XLS com 256 colunas)."""
        last_col = -1
        for row in self.values:
            for c in range(len(row) - 1, -1, -1):
                if clean_text(row[c]) != "":
                    last_col = max(last_col, c)
                    break
        while self.values and all(clean_text(v) == "" for v in self.values[-1]):
            self.values.pop()
        width = last_col + 1
        self.values = [(list(row) + [None] * width)[:width] for row in self.values]

    @property
    def nrows(self) -> int:
        return len(self.values)

    @property
    def ncols(self) -> int:
        return len(self.values[0]) if self.values else 0

    def raw(self, r: int, c: int) -> Any:
        if 0 <= r < self.nrows and 0 <= c < self.ncols:
            return self.values[r][c]
        return None

    def text(self, r: int, c: int) -> str:
        return clean_text(self.raw(r, c))

    def anchor(self, r: int, c: int) -> tuple[int, int]:
        """Célula âncora da mesclagem que contém (r, c) — ou a própria célula."""
        return self._anchor.get((r, c), (r, c))

    def merged_text(self, r: int, c: int) -> str:
        ar, ac = self.anchor(r, c)
        return self.text(ar, ac)

    def merge_at(self, r: int, c: int) -> Merge | None:
        for m in self.merges:
            if m.contains(r, c):
                return m
        return None

    def row_texts(self, r: int) -> list[str]:
        return [self.text(r, c) for c in range(self.ncols)]

    def ref(self, r: int, c: int) -> str:
        return cell_ref(r, c)

    def nonempty_count(self) -> int:
        return sum(1 for row in self.values for v in row if clean_text(v) != "")

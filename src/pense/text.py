"""Normalização de textos e valores de células.

Funções puras, sem dependência de pandas, para facilitar testes unitários.
"""
from __future__ import annotations

import math
import re
import unicodedata
from dataclasses import dataclass
from typing import Any

_WS = re.compile(r"\s+")
_EXCEL_ERROR = re.compile(r"^#(DIV/0!|N/A|VALUE!|REF!|NAME\?|NUM!|NULL!|GETTING_DATA)$", re.I)
_PT_NUMBER = re.compile(r"^[+-]?(\d{1,3}(\.\d{3})+|\d+)(,\d+)?$")
_EN_NUMBER = re.compile(r"^[+-]?(\d+(\.\d+)?|\.\d+)([eE][+-]?\d+)?$")


def clean_text(value: Any) -> str:
    """Texto de exibição: remove quebras de linha, NBSP e espaços repetidos."""
    if value is None:
        return ""
    if isinstance(value, float) and math.isnan(value):
        return ""
    s = str(value).replace(" ", " ").replace("\r", " ").replace("\n", " ")
    return _WS.sub(" ", s).strip()


def slug(value: Any) -> str:
    """Forma normalizada para comparação: sem acento, minúscula, só [a-z0-9 ]."""
    s = unicodedata.normalize("NFKD", clean_text(value)).encode("ascii", "ignore").decode()
    s = re.sub(r"[^a-z0-9]+", " ", s.lower())
    return s.strip()


def compact(value: Any) -> str:
    """Slug sem espaços — cobre hifenizações como "Limite infe- rior"."""
    return slug(value).replace(" ", "")


def code_from_label(value: Any, max_len: int = 48) -> str:
    """Código estável (snake_case ASCII) a partir de um rótulo."""
    s = slug(value).replace(" ", "_")
    return s[:max_len].rstrip("_") or "na"


@dataclass(frozen=True)
class ParsedValue:
    """Resultado da interpretação de uma célula de dados."""

    kind: str  # number | symbol | empty | text | excel_error
    value: float | None = None
    raw: str = ""
    symbol: str | None = None

    @property
    def is_number(self) -> bool:
        return self.kind == "number"


def parse_cell(value: Any, symbols: set[str] | frozenset[str] = frozenset()) -> ParsedValue:
    """Interpreta uma célula sem nunca inventar valores.

    * números nativos são mantidos com a precisão publicada;
    * símbolos (``-``, ``..``, ``x``) viram ``kind='symbol'`` e valor nulo;
    * textos numéricos com vírgula decimal ("12,5" ou "1.234,5") são lidos
      no padrão pt-BR; sem vírgula ("12.5") no padrão com ponto decimal —
      só ocorre em CSV/ODS, já que células numéricas do Excel são nativas;
    * erros do Excel são identificados explicitamente.
    """
    if value is None:
        return ParsedValue("empty")
    if isinstance(value, bool):
        return ParsedValue("text", raw=str(value))
    if isinstance(value, (int, float)):
        if isinstance(value, float) and math.isnan(value):
            return ParsedValue("empty")
        return ParsedValue("number", float(value), raw=repr(value))
    raw = clean_text(value)
    if raw == "":
        return ParsedValue("empty")
    if raw in symbols:
        return ParsedValue("symbol", None, raw=raw, symbol=raw)
    if _EXCEL_ERROR.match(raw):
        return ParsedValue("excel_error", None, raw=raw)
    s = raw.replace("%", "").replace(" ", "")
    if "," in s and _PT_NUMBER.match(s):
        try:
            return ParsedValue("number", float(s.replace(".", "").replace(",", ".")), raw=raw)
        except ValueError:  # pragma: no cover - regex garante formato
            pass
    if _EN_NUMBER.match(s):
        return ParsedValue("number", float(s), raw=raw)
    return ParsedValue("text", None, raw=raw)


def col_letter(index0: int) -> str:
    """Índice de coluna (base 0) -> letra do Excel (0 -> A, 26 -> AA)."""
    n = index0 + 1
    out = ""
    while n:
        n, rem = divmod(n - 1, 26)
        out = chr(65 + rem) + out
    return out


def cell_ref(row0: int, col0: int) -> str:
    return f"{col_letter(col0)}{row0 + 1}"

"""Decisões de revisão humana aplicadas pela pipeline (``config/review_decisions.csv``).

Alertas do tipo "ainda não conferido" (REVIEW) só saem desse estado com uma decisão registrada:
quem conferiu, quando, o que decidiu e com que evidência. A pipeline aplica a decisão e registra a
regra REV001 (informativa) em cada aba afetada, para a decisão ficar visível na página Qualidade.

Ações suportadas:
* ``FOOTER_ERRATUM`` — o rodapé do IBGE cita outra edição (erro de digitação da planilha): vale o ano
  do título; ``value`` = ano correto.
* ``CATEGORY_FOR_DIMENSION_COLUMNS`` — cabeçalho assimétrico (HDR006): as colunas por dimensão sem
  categoria recebem a categoria ``value``, definida pela leitura do título e conferida com outra fonte.
"""
from __future__ import annotations

import csv
from functools import lru_cache
from pathlib import Path

FIELDS = ("source_file", "source_sheet", "action", "value", "justification", "evidence", "reviewer", "decision_date")
ACTIONS = {"FOOTER_ERRATUM", "CATEGORY_FOR_DIMENSION_COLUMNS"}


@lru_cache(maxsize=8)
def _load(path: str, mtime: float) -> dict[tuple[str, str, str], dict[str, str]]:
    out: dict[tuple[str, str, str], dict[str, str]] = {}
    with open(path, encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh):
            missing = [f for f in FIELDS if not (row.get(f) or "").strip()]
            if missing or row["action"] not in ACTIONS:
                raise ValueError(f"config/review_decisions.csv: decisão incompleta ou ação inválida "
                                 f"({row.get('source_file')} {row.get('source_sheet')}: {missing or row['action']})")
            out[(row["source_file"], row["source_sheet"], row["action"])] = row
    return out


def decisions(config_dir: Path) -> dict[tuple[str, str, str], dict[str, str]]:
    p = Path(config_dir) / "review_decisions.csv"
    return _load(str(p), p.stat().st_mtime) if p.exists() else {}


def decision(config_dir: Path, source_file: str, sheet: str, action: str) -> dict[str, str] | None:
    return decisions(config_dir).get((source_file, sheet, action))


def apply_title_review(info, source_file: str, sheet: str, config_dir: Path) -> dict[str, str] | None:
    """Errata de rodapé: antes de escolher o adaptador, o rodapé errado deixa de valer."""
    d = decision(config_dir, source_file, sheet, "FOOTER_ERRATUM")
    if d:
        info.footer_year = int(d["value"])
        info.sample = ""
    return d

"""Escrita determinística de CSV (UTF-8 com BOM, compatível com Excel) e JSON.

Decisão de formato: o volume real (dezenas de milhares de linhas) não
justifica Parquet; CSV é aberto em qualquer ferramenta (Excel, R, pandas) e
JSON é consumido diretamente pelo dashboard. Assim evitamos dependências
como ``pyarrow``.
"""
from __future__ import annotations

import csv
import json
import math
from pathlib import Path
from typing import Any, Iterable

# Campos da versão enxuta da base aprovada (JSON e download do painel): os textos longos
# do indicador (definição, notas, denominador) ficam no catálogo de indicadores.
SLIM_FIELDS = ["observation_id", "edition_id", "edition_year", "table_id", "indicator_id", "indicator_name",
               "category_group", "response_category", "unit", "estimate_type", "territory_type", "territory_code",
               "territory_name", "age_group", "sex", "admin_dependency", "estimate", "ci_lower", "ci_upper",
               "coefficient_of_variation", "validation_status", "issue_rules", "comparability_status",
               "source_file", "source_sheet", "source_cell"]


def _cell(v: Any) -> Any:
    if v is None:
        return ""
    if isinstance(v, float) and math.isnan(v):
        return ""
    if isinstance(v, bool):
        return "true" if v else "false"
    return v


def write_csv(path: Path, rows: Iterable[dict[str, Any]], fields: list[str] | None = None) -> int:
    rows = list(rows)
    if fields is None:
        fields = []
        for r in rows:
            for k in r:
                if k not in fields:
                    fields.append(k)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow({k: _cell(r.get(k)) for k in fields})
    return len(rows)


def write_json(path: Path, data: Any, compact: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        if compact:
            json.dump(data, fh, ensure_ascii=False, separators=(",", ":"), default=str)
        else:
            json.dump(data, fh, ensure_ascii=False, indent=2, default=str)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))

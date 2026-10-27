"""Pergunta de origem das tabelas publicadas, a partir dos dicionários de microdados do IBGE.

Duas fontes de ligação tabela → variável, sempre registradas em ``question_source``:
* **comprovada por reprodução numérica** — indicadores de config/microdata/indicators.toml
  cujo cálculo com os microdados reproduz a tabela publicada (2019, 2024 e série 9º ano);
* **manual** — config/question_map.csv (2009 e 2015 Amostra 1), marcada "conferir".
Sem ligação, ``question_text`` continua PENDENTE.
"""
from __future__ import annotations

import csv
from typing import Any

from ..config import Config
from ..microdata.dictionary import lookup

PENDING = "PENDENTE"


def _text(cfg: Config, dict_edition: str, variables: str, prefix: str = "") -> str:
    parts = []
    for v in variables.split("+"):
        d = lookup(cfg.config_dir, dict_edition, v, prefix)
        if d:
            parts.append(d["description"])
    return " / ".join(parts)


def build_question_map(cfg: Config) -> dict[tuple[str, str, str], dict[str, str]]:
    out: dict[tuple[str, str, str], dict[str, str]] = {}
    try:
        from ..microdata.run import _conditions, load_config
        editions, indicators = load_config(cfg)
    except FileNotFoundError:
        editions, indicators = {}, {}
    validated = _validated(cfg)
    for key, ind in indicators.items():
        for ed, ref in ind.get("published", {}).items():
            if ed not in editions or (ed, key) not in validated:
                continue
            pub_ed, _, ref = ref.rpartition("@") if "@" in ref else (ed, "", ref)
            fam, _, cat = ref.partition("|")
            var = "+".join(c["var"] for c in _conditions(ind, ed))
            text = _text(cfg, ed, var, editions[ed].get("var_prefix", ""))
            if text:
                out.setdefault((pub_ed, fam, cat or "*"), {
                    "question_text": text, "question_variable": f"{var} ({editions[ed]['year']})",
                    "question_source": f"dicionário IBGE {editions[ed]['year']}; ligação comprovada por reprodução da tabela com os microdados"})
    path = cfg.config_dir / "question_map.csv"
    if path.exists():
        with path.open(encoding="utf-8-sig", newline="") as fh:
            for r in csv.DictReader(fh):
                prefix = "" if r["edition_id"] == "PENSE_2009" else ""
                text = _text(cfg, r["edition_id"], r["variable"], prefix)
                if text:
                    out[(r["edition_id"], r["table_family_id"], r["response_category"])] = {
                        "question_text": text, "question_variable": r["variable"], "question_source": r["mapping_basis"]}
    return out


def _validated(cfg: Config) -> set[tuple[str, str]]:
    path = cfg.path("curated") / "microdata_validation_summary.csv"
    if not path.exists():
        return set()
    with path.open(encoding="utf-8-sig", newline="") as fh:
        return {(r["edition_id"], r["indicator_key"]) for r in csv.DictReader(fh) if r["status"].startswith("VALIDADO")}


def apply_questions(records: list[dict[str, Any]], qmap: dict[tuple[str, str, str], dict[str, str]]) -> int:
    n = 0
    for r in records:
        hit = (qmap.get((r["edition_id"], r["table_family_id"], r.get("response_category", "")))
               or qmap.get((r["edition_id"], r["table_family_id"], "*")))
        if hit:
            r.update(hit)
            n += 1
        else:
            r.setdefault("question_variable", "")
            r.setdefault("question_source", "")
    return n

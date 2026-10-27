"""Dicionários de microdados do IBGE (config/reference/dicionario_<EDIÇÃO>.csv).

Usados para (1) trazer o texto exato de cada pergunta e (2) comparar a redação entre
edições, palavra por palavra, como evidência de comparabilidade.
"""
from __future__ import annotations

import csv
import difflib
import re
import unicodedata
from functools import lru_cache
from pathlib import Path


@lru_cache(maxsize=None)
def load(config_dir: str, edition: str) -> dict[str, dict]:
    path = Path(config_dir) / "reference" / f"dicionario_{edition}.csv"
    out: dict[str, dict] = {}
    if not path.exists():
        return out
    with path.open(encoding="utf-8-sig", newline="") as fh:
        for r in csv.DictReader(fh):
            v = out.setdefault(r["variable"].upper(), {"description": r["description"], "codes": {}})
            if r["code"] != "":
                v["codes"][r["code"]] = r["code_label"]
    return out


def lookup(config_dir: Path, edition: str, var: str, prefix: str = "") -> dict | None:
    d = load(str(config_dir), edition)
    return d.get((prefix + var).upper()) or d.get(var.upper())


def _norm_tokens(text: str) -> list[str]:
    t = unicodedata.normalize("NFKD", text.lower()).encode("ascii", "ignore").decode()
    t = re.sub(r"\(a\)|\(as\)|\(os\)", "", t)
    return re.findall(r"[a-z0-9]+", t)


def compare(texts: dict[str, str]) -> dict:
    """Compara a redação entre edições (pares consecutivos).

    Retorna ``identical`` (bool), ``changes`` (lista de 'ano: +palavras / −palavras') e o
    número máximo de palavras alteradas entre duas edições consecutivas.
    """
    eds = [e for e in texts if texts[e]]
    changes, max_changed = [], 0
    for a, b in zip(eds, eds[1:]):
        ta, tb = _norm_tokens(texts[a]), _norm_tokens(texts[b])
        added, removed = [], []
        for op, i1, i2, j1, j2 in difflib.SequenceMatcher(a=ta, b=tb, autojunk=False).get_opcodes():
            if op in ("replace", "delete"):
                removed += ta[i1:i2]
            if op in ("replace", "insert"):
                added += tb[j1:j2]
        n = max(len(added), len(removed))
        max_changed = max(max_changed, n)
        if n:
            parts = []
            if added:
                parts.append("acrescenta “" + " ".join(added) + "”")
            if removed:
                parts.append("retira “" + " ".join(removed) + "”")
            changes.append(f"{a} → {b}: " + "; ".join(parts))
    return {"identical": not changes, "changes": changes, "max_changed": max_changed}

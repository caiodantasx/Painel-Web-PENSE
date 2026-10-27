"""Resolução de rótulos territoriais com base em ``config/territories.csv``.

A resolução depende do *escopo* da tabela (lido do título): numa tabela "segundo
os Municípios das Capitais", "Total" é o conjunto das capitais e "Distrito
Federal" (2009) é Brasília; numa tabela por UF, "Distrito Federal" é a UF 53.
"""
from __future__ import annotations

from dataclasses import dataclass

from ..config import Config
from ..text import slug


@dataclass(frozen=True)
class Territory:
    code: str
    name: str
    type: str
    ibge_code: str
    uf_code: str
    uf_sigla: str
    region_code: str
    code_source: str


@dataclass(frozen=True)
class Resolution:
    territory: Territory | None
    method: str


class TerritoryResolver:
    def __init__(self, cfg: Config):
        self.by_scope: dict[str, dict[str, Territory]] = {"uf": {}, "region": {}, "capital": {}}
        self.by_code: dict[str, Territory] = {}
        for row in cfg.territories:
            t = Territory(row["territory_code"], row["territory_name"], row["territory_type"], row["ibge_code"],
                          row["uf_code"], row["uf_sigla"], row["region_code"], row["code_source"])
            self.by_code[t.code] = t
            keys = {slug(row["territory_name"])} | {slug(a) for a in row["aliases"].split("|") if a}
            for scope in row["scopes"].split("|"):
                for k in keys:
                    self.by_scope.setdefault(scope, {})[k] = t

    def resolve(self, label: str, scope: str) -> Resolution:
        key = slug(label)
        if not key:
            return Resolution(None, "rótulo vazio")
        order = {"capital": ["capital"], "uf": ["uf"], "region": ["region", "uf"]}.get(scope, ["uf", "capital"])
        for sc in order:
            t = self.by_scope.get(sc, {}).get(key)
            if t:
                return Resolution(t, f"dicionário territorial (escopo '{sc}')")
        return Resolution(None, f"não encontrado no escopo '{scope}'")

    def get(self, code: str) -> Territory | None:
        return self.by_code.get(code)

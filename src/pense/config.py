"""Carregamento da configuração externa (TOML/CSV) do projeto.

Toda regra metodológica ou mapeamento que possa mudar sem alterar o código
fica em ``config/``. Este módulo apenas lê e expõe esses arquivos.
"""
from __future__ import annotations

import csv
from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path
from typing import Any

import tomllib

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as fh:
        return [dict(row) for row in csv.DictReader(fh)]


@dataclass
class Config:
    """Configuração imutável de uma execução."""

    root: Path = PROJECT_ROOT
    overrides: dict[str, Any] = field(default_factory=dict)

    @property
    def config_dir(self) -> Path:
        return self.root / "config"

    @cached_property
    def settings(self) -> dict[str, Any]:
        with (self.config_dir / "settings.toml").open("rb") as fh:
            data = tomllib.load(fh)
        for dotted, value in self.overrides.items():
            section, key = dotted.split(".", 1)
            data.setdefault(section, {})[key] = value
        return data

    @cached_property
    def vocabulary(self) -> dict[str, Any]:
        with (self.config_dir / "vocabulary.toml").open("rb") as fh:
            return tomllib.load(fh)

    @cached_property
    def territories(self) -> list[dict[str, str]]:
        return _read_csv(self.config_dir / "territories.csv")

    @cached_property
    def symbols(self) -> dict[str, dict[str, str]]:
        return {row["symbol"]: row for row in _read_csv(self.config_dir / "symbols.csv")}

    @cached_property
    def editions(self) -> dict[str, dict[str, str]]:
        return {row["edition_id"]: row for row in _read_csv(self.config_dir / "editions.csv")}

    def optional_csv(self, name: str) -> list[dict[str, str]]:
        path = self.config_dir / name
        return _read_csv(path) if path.exists() else []

    def path(self, key: str) -> Path:
        """Resolve um caminho de ``[paths]`` relativo à raiz do projeto."""
        p = self.root / self.settings["paths"][key]
        p.mkdir(parents=True, exist_ok=True)
        return p

    def v(self, section: str, key: str) -> Any:
        return self.settings[section][key]

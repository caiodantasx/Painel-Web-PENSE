"""Configuração da tela inicial para gestores (``config/painel_gestor.toml``) no pacote do painel.

Só resolve ligações: cada item aponta para o índice de uma medida publicada (``bundle["measures"]``)
e, se houver, para a chave do indicador recalculado pelos microdados (``bundle["micro"]``). Nenhuma
estimativa é copiada aqui. Uma ligação que não existe no pacote derruba a geração (erro explícito),
para a tela nunca mostrar um número trocado.
"""
from __future__ import annotations

import logging
import tomllib
from pathlib import Path
from typing import Any

log = logging.getLogger(__name__)


def gestor_section(config_dir: Path, bundle: dict[str, Any]) -> dict[str, Any] | None:
    path = config_dir / "painel_gestor.toml"
    if not path.exists():
        return None
    with path.open("rb") as fh:
        conf = tomllib.load(fh)
    m_index = {m["id"]: i for i, m in enumerate(bundle["measures"])}
    micro_keys = {i["key"] for i in (bundle.get("micro") or {}).get("indicators", [])}
    items: dict[str, Any] = {}
    missing: list[str] = []
    for key, it in conf["items"].items():
        if it["measure"] not in m_index:
            missing.append(f"{key}: medida {it['measure']}")
            continue
        micro = it.get("micro", "")
        items[key] = {"short": it["short"], "phrase": it["phrase"], "m": m_index[it["measure"]],
                      "micro": micro if micro in micro_keys else "", "table": it.get("table", ""),
                      "school": bool(it.get("school")), "complement": bool(it.get("complement"))}
    if missing:
        log.warning("painel_gestor.toml: medidas ausentes do pacote (itens fora da tela inicial)",
                    extra={"detail": "; ".join(missing)})
    if not items:
        return None
    blocks = dict(conf.get("blocks", {}))
    for k in ("types", "bullying"):
        blocks[k] = [x for x in blocks.get(k, []) if x in items]
    lists = {}
    for t, v in blocks.get("topic_lists", {}).items():
        lists[t] = blocks[v] if isinstance(v, str) else [x for x in v if x in items]
    blocks["topic_lists"] = lists
    for k in ("absence",):
        if k in blocks and not all(v in micro_keys for v in blocks[k].values()):
            blocks.pop(k)
    if blocks.get("any_violence") not in micro_keys:
        blocks.pop("any_violence", None)
    estimates = [{"title": e["title"], "items": [k for k in e["items"] if k in items]} for e in conf.get("estimates", [])]
    motives = {}
    for side, mv in conf.get("motives", {}).items():
        ms = [i for i, m in enumerate(bundle["measures"]) if m["indicator_id"] == mv["indicator"]]
        if ms:
            motives[side] = {"measures": ms, "base": mv["base"] if mv.get("base") in items else ""}
    links = [lk for lk in conf.get("links", []) if lk["with"] in micro_keys and lk["without"] in micro_keys]
    pop = conf.get("population_micro", "")
    return {"ibge_url": conf["ibge_url"], "edition": conf["edition"], "groups": conf["groups"],
            "population_micro": pop if pop in micro_keys else "", "estimates": estimates, "motives": motives, "links": links,
            "topics": [t for t in conf["topics"] if t["main"] in items], "items": items, "blocks": blocks}

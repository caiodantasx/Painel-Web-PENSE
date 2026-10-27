"""Gera dashboard/assets/geo/br_uf.json (limites das UFs) a partir da malha municipal.

Fonte: tbrugz/geodata-br (`geojson/geojs-100-mun.json`), derivada da malha
municipal do IBGE, licença CC0 1.0. Os municípios são dissolvidos por código
de UF (2 primeiros dígitos do código IBGE) e simplificados para uso web.

Uso (só é preciso rodar de novo se quiser trocar a malha):
    python scripts/build_uf_geometry.py caminho/geojs-100-mun.json
Requer: shapely>=2 (dependência apenas deste script, não da pipeline).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "dashboard" / "assets" / "geo" / "br_uf.json"
TOLERANCE_DEG = 0.03
DECIMALS = 3


def main(src: str) -> None:
    from shapely.geometry import mapping, shape
    from shapely.ops import unary_union

    data = json.loads(Path(src).read_text(encoding="utf-8"))
    by_uf: dict[str, list] = {}
    for feat in data["features"]:
        code = str(feat["properties"]["id"])[:2]
        by_uf.setdefault(code, []).append(shape(feat["geometry"]).buffer(0))
    features = []
    for code, geoms in sorted(by_uf.items()):
        merged = unary_union(geoms).buffer(0.0005).buffer(-0.0005)
        simple = merged.simplify(TOLERANCE_DEG, preserve_topology=True)
        geo = json.loads(json.dumps(mapping(simple)), parse_float=lambda x: round(float(x), DECIMALS))
        features.append({"type": "Feature", "properties": {"uf_code": code}, "geometry": geo})
    out = {
        "type": "FeatureCollection",
        "metadata": {
            "source": "tbrugz/geodata-br geojson/geojs-100-mun.json (malha municipal IBGE, 5564 municípios), CC0 1.0",
            "processing": f"dissolve por UF + simplify({TOLERANCE_DEG}°) + coordenadas com {DECIMALS} casas",
            "note": "Uso exclusivamente visual (mapa coroplético); não usar para cálculos de área.",
        },
        "features": features,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, separators=(",", ":")), encoding="utf-8")
    print(f"{len(features)} UFs -> {OUT} ({OUT.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main(sys.argv[1])

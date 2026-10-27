"""Calcula os indicadores a partir dos microdados e valida contra as tabelas publicadas.

Pré-requisitos: microdados em data/microdata/<EDIÇÃO>/ (ver config/microdata/editions.toml)
e a pipeline principal já executada (usa data/processed/observations_validated.csv para a
validação contra o publicado).

Uso:  python scripts/run_microdata.py
"""
from __future__ import annotations

import csv
import logging
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from pense.config import Config  # noqa: E402
from pense.microdata.run import (FIELDS, estimate_all, summarize_validation,  # noqa: E402
                                 validate_against_published, write_csv)


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)-7s %(message)s")
    cfg = Config(root=ROOT)
    t0 = time.perf_counter()
    effects: list[dict] = []
    est = estimate_all(cfg, effects)
    curated = cfg.path("curated")
    write_csv(curated / "microdata_estimates.csv", est, FIELDS)
    write_csv(curated / "microdata_nonresponse_effect.csv", effects)
    pub_path = cfg.path("processed") / "observations_validated.csv"
    with pub_path.open(encoding="utf-8-sig", newline="") as fh:
        published = list(csv.DictReader(fh))
    val = validate_against_published(est, published)
    write_csv(curated / "microdata_validation.csv", val)
    from pense.microdata.run import load_config
    editions, _ = load_config(cfg)
    summ = summarize_validation(val, {k: v.get("validation") for k, v in editions.items() if v.get("validation")})
    write_csv(curated / "microdata_validation_summary.csv", summ)
    print(f"{len(est)} estimativas; {len(val)} comparações com o publicado; {time.perf_counter() - t0:.1f} s")
    for s in summ:
        print(f"  {s['edition_id']:14s} {s['indicator_key']:24s} {s['published_table']:5s} {s['published_category'][:16]:16s} "
              f"{s['reproduz']:>4}/{s['compared']:<4} ic≠ {s['estimativa_ok_ic_difere']:<3} ≈ {s['proximo']:<3} ✗ {s['nao_reproduz']:<3} "
              f"máx Δ {s['max_abs_diff_estimate_pp']:.4f} {s['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Sensibilidade de TRAJETO_INSEGURO (Brasil, 13 a 17 anos, regra da série) ao 6º ano do EF.

Uso (na raiz do projeto):  python reports/auditoria_2026-10-27/scripts/sensibilidade_6ano_trajeto.py
      [raiz do projeto] [saída.md]   (padrões: este projeto; reports/auditoria_2026-10-27/sensibilidade_6ano_trajeto.md)
Exige os microdados em data/microdata/ (scripts/extract_microdata.py).

Só lê arquivos. Usa o estimador e o desenho do próprio projeto (pense.microdata.run/estimator).
Variáveis de ano escolar (dicionários do IBGE, config/reference/):
* 2015 A2: VB01021 "Em que ano/série você está?" (autodeclarado) — 1 = 6º ano / 5ª série do EF;
* 2019:    B01021A (dicionário: B01021a) "Em que ano escolar você está?" (autodeclarado) — 1 = 6º ano do EF;
           ANO_TURMA (cadastro da turma) — começa no 7º ano (código 1);
* 2024:    B01021B (autodeclarado) e ANO_TURMA (cadastro) — ambos começam no 7º ano.
Recortes calculados como domínio (o desenho inteiro é mantido; fora do domínio = 0).
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parents[3]
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "reports" / "auditoria_2026-10-27" / "sensibilidade_6ano_trajeto.md"
sys.path.insert(0, str(ROOT / "src"))
from pense.config import Config  # noqa: E402
from pense.microdata.estimator import ratio  # noqa: E402
from pense.microdata.run import CONV_SERIE, _masks, load_config, load_edition  # noqa: E402

Z = 1.959963984540054
cfg = Config(root=ROOT)
editions, indicators = load_config(cfg)
ind = indicators["TRAJETO_INSEGURO"]
GRADE = {"PENSE_2015_A2": ("VB01021", 1), "PENSE_2019": ("B01021A", 1), "PENSE_2024": ("B01021B", None)}


def extra_col(spec: dict, col: str) -> np.ndarray:
    path = cfg.root / spec["file"]
    df = pd.read_csv(path, sep=spec["sep"], decimal=spec["decimal"], usecols=[spec["weight"], col], low_memory=False)
    df = df[df[spec["weight"]].notna() & (df[spec["weight"]] > 0)].reset_index(drop=True)
    return df[col].to_numpy()


res, lines = {}, []
for ed in ("PENSE_2015_A2", "PENSE_2019", "PENSE_2024"):
    spec = editions[ed]
    data = load_edition(cfg, ed, spec, {"TRAJETO_INSEGURO": ind})
    gvar, code6 = GRADE[ed]
    grade = extra_col(spec, gvar)
    assert len(grade) == len(data.frame), "alinhamento das linhas"
    age = data.frame[spec["age_var"]].isin(spec["age_groups"]["13 a 17 anos"]).to_numpy()
    num, den, _, _ = _masks(data, ind, CONV_SERIE)
    w = data.design.weight
    six = (grade == code6) if code6 is not None else np.zeros(len(grade), dtype=bool)
    share = float(np.dot(w, age & den & six) / np.dot(w, age & den))
    n6 = int((age & den & six).sum())
    full = ratio(data.design, num & age, den & age)
    sans = ratio(data.design, num & age & ~six, den & age & ~six)
    only6 = ratio(data.design, num & age & six, den & age & six) if n6 else None
    res[ed] = (full, sans)
    lines.append(f"| {spec['year']} ({ed}) | `{gvar}` = {code6 if code6 is not None else '— (sem 6º ano)'} | "
                 f"{n6:,} | {100*share:.2f}% | {100*full.p:.2f} [{100*full.ci_lower:.2f}; {100*full.ci_upper:.2f}] | "
                 f"{100*sans.p:.2f} [{100*sans.ci_lower:.2f}; {100*sans.ci_upper:.2f}] | "
                 f"{f'{100*only6.p:.2f} (EP {100*only6.se:.2f})' if only6 else '—'} |")


def diff(a, b):
    d = 100 * (b.p - a.p)
    sd = 100 * math.hypot(a.se, b.se)
    return f"{d:+.2f} [{d - Z*sd:+.2f}; {d + Z*sd:+.2f}] {'significativa' if abs(d) > Z*sd else 'não significativa'} a 5%"


A, B, C = (res[e] for e in ("PENSE_2015_A2", "PENSE_2019", "PENSE_2024"))
out = ["# Sensibilidade ao 6º ano — TRAJETO_INSEGURO, Brasil, 13 a 17 anos, regra da série", "",
       f"Gerado por `{Path(__file__).name}` na raiz do projeto (desenho e estimador do projeto; IC 95% por linearização).", "",
       "| Edição | Variável de ano (autodeclarado) | Registros 6º ano no denominador | Peso do 6º ano | Total (%) | Sem 6º ano (%) | Só 6º ano (%) |",
       "|---|---|---|---|---|---|---|", *lines, "",
       "## Comparações 2015→2019 e 2019→2024 (amostras independentes, EP = √(EP₁²+EP₂²))", "",
       f"* 2015→2019, todos: {diff(A[0], B[0])}",
       f"* 2015 sem 6º ano → 2019 todos: {diff(A[1], B[0])}",
       f"* 2015 sem 6º ano → 2019 sem 6º ano autodeclarado: {diff(A[1], B[1])}",
       f"* 2019→2024, todos: {diff(B[0], C[0])}",
       f"* 2019 sem 6º ano autodeclarado → 2024: {diff(B[1], C[0])}", "",
       "Leitura: o recorte por ano autodeclarado é aproximação. Em 2015 A2 a amostra inclui turmas do 6º ano; em 2019 as "
       "turmas começam no 7º ano (ANO_TURMA), mas há alunos que se declaram no 6º ano (B01021A = 1). Nenhum dos "
       "resultados prova erro em um dos valores: mostra quanto a comparação depende do 6º ano."]
OUT.write_text("\n".join(out) + "\n", encoding="utf-8")
print("\n".join(out))

"""Sensibilidade ao 6º ano do EF de TODOS os indicadores 13–17 anos com 2015 (Amostra 2) — Brasil, regra da série.

Generalização de reports/auditoria_2026-10-27/scripts/sensibilidade_6ano_trajeto.py (mesmo método, mesmas
variáveis de ano escolar, mesmo estimador/desenho do projeto). Só lê arquivos.
Uso: python sensibilidade_6ano_todos.py <raiz do projeto> <saída.md> <saída.csv>
"""
from __future__ import annotations
import csv, math, sys
from pathlib import Path
import numpy as np
import pandas as pd
ROOT = Path(sys.argv[1]).resolve()
OUT = Path(sys.argv[2]); OUTCSV = Path(sys.argv[3])
sys.path.insert(0, str(ROOT / "src"))
from pense.config import Config  # noqa: E402
from pense.microdata.estimator import ratio  # noqa: E402
from pense.microdata.run import CONV_SERIE, _masks, load_config, load_edition  # noqa: E402
Z = 1.959963984540054
cfg = Config(root=ROOT)
editions, indicators = load_config(cfg)
KEYS = [k for k, v in indicators.items() if "PENSE_2015_A2" in v["editions"] and not k.startswith("NONO_")]
GRADE = {"PENSE_2015_A2": ("VB01021", 1), "PENSE_2019": ("B01021A", 1), "PENSE_2024": ("B01021B", None)}

def extra_col(spec, col):
    df = pd.read_csv(cfg.root / spec["file"], sep=spec["sep"], decimal=spec["decimal"], usecols=[spec["weight"], col], low_memory=False)
    df = df[df[spec["weight"]].notna() & (df[spec["weight"]] > 0)].reset_index(drop=True)
    return df[col].to_numpy()

def diff(a, b):
    d = 100 * (b.p - a.p); sd = 100 * math.hypot(a.se, b.se)
    return d, d - Z*sd, d + Z*sd, abs(d) > Z*sd

res = {}
share = {}
for ed in ("PENSE_2015_A2", "PENSE_2019", "PENSE_2024"):
    spec = editions[ed]
    sub = {k: indicators[k] for k in KEYS}
    data = load_edition(cfg, ed, spec, sub)
    gvar, code6 = GRADE[ed]
    grade = extra_col(spec, gvar)
    assert len(grade) == len(data.frame)
    age = data.frame[spec["age_var"]].isin(spec["age_groups"]["13 a 17 anos"]).to_numpy()
    six = (grade == code6) if code6 is not None else np.zeros(len(grade), dtype=bool)
    w = data.design.weight
    for k in KEYS:
        num, den, _, _ = _masks(data, indicators[k], CONV_SERIE)
        res[(k, ed)] = (ratio(data.design, num & age, den & age), ratio(data.design, num & age & ~six, den & age & ~six))
        share[(k, ed)] = float(np.dot(w, age & den & six) / np.dot(w, age & den))

rows = []
for k in KEYS:
    A, B = res[(k, "PENSE_2015_A2")], res[(k, "PENSE_2019")]
    full = diff(A[0], B[0]); s1 = diff(A[1], B[0]); s2 = diff(A[1], B[1])
    robust = full[3] == s1[3] == s2[3]
    rows.append(dict(indicator_key=k, peso_6ano_2015=round(100*share[(k,"PENSE_2015_A2")],2),
        p2015=round(100*A[0].p,2), p2015_sem6=round(100*A[1].p,2), p2019=round(100*B[0].p,2),
        d_todos=f"{full[0]:+.2f} [{full[1]:+.2f}; {full[2]:+.2f}]", sig_todos=full[3],
        d_2015sem6=f"{s1[0]:+.2f} [{s1[1]:+.2f}; {s1[2]:+.2f}]", sig_2015sem6=s1[3],
        d_ambos_sem6=f"{s2[0]:+.2f} [{s2[1]:+.2f}; {s2[2]:+.2f}]", sig_ambos_sem6=s2[3],
        conclusao_2015_2019_robusta=robust))
with OUTCSV.open("w", newline="", encoding="utf-8") as fh:
    wr = csv.DictWriter(fh, fieldnames=list(rows[0])); wr.writeheader(); wr.writerows(rows)
L = ["# Sensibilidade ao 6º ano — indicadores 13 a 17 anos com 2015 (Amostra 2), Brasil, regra da série", "",
     "Método idêntico ao de `reports/auditoria_2026-10-27/sensibilidade_6ano_trajeto.md` (recorte pelo ano autodeclarado: "
     "2015 `VB01021`=1; 2019 `B01021A`=1). Diferença entre edições: amostras independentes, EP=√(EP₁²+EP₂²), z=1,96.", "",
     "| Indicador | Peso 6º ano 2015 | 2015 | 2015 sem 6º | 2019 | 2015→2019 (todos) | 2015 sem 6º→2019 | ambos sem 6º | Conclusão robusta? |",
     "|---|---|---|---|---|---|---|---|---|"]
for r in rows:
    f = lambda d, s: f"{d} {'**sig.**' if s else 'n.s.'}"
    L.append(f"| {r['indicator_key']} | {r['peso_6ano_2015']}% | {r['p2015']} | {r['p2015_sem6']} | {r['p2019']} | "
             f"{f(r['d_todos'], r['sig_todos'])} | {f(r['d_2015sem6'], r['sig_2015sem6'])} | {f(r['d_ambos_sem6'], r['sig_ambos_sem6'])} | "
             f"{'sim' if r['conclusao_2015_2019_robusta'] else '**NÃO**'} |")
L += ["", "Robusta = a conclusão de significância a 5% de 2015→2019 é a mesma nas três versões. O recorte por ano autodeclarado é "
      "aproximação da cobertura por turma; o resultado mostra dependência do 6º ano, não prova erro em nenhum valor."]
OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
print("\n".join(L))

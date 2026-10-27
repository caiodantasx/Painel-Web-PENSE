"""Valida os microdados da PeNSE 2015 Amostra 2 contra as tabelas publicadas 2.11.x (Tema 11).

Uso: python valida_2015_a2.py <raiz_do_projeto> <Amostra_2_Tema_11_Seguranca.xls>
Convenção da publicação 2015 (Nota metodológica 03): código 99 fora do denominador.
Compara duas definições de estrato: ESTRATOGEOREG (Nota 01/2018, Quadro 3) e ESTRATO_EXP.
"""
import sys, tomllib, csv
import numpy as np, pandas as pd, xlrd
ROOT, XLS = sys.argv[1], sys.argv[2]
sys.path.insert(0, ROOT + "/src")
from pense.microdata.estimator import DesignArrays, ratio

inds = tomllib.load(open(f"{ROOT}/config/microdata/indicators.toml", "rb"))
TAB = {"2.11.1": ["TRAJETO_INSEGURO"], "2.11.2": ["ESCOLA_INSEGURA"], "2.11.3": ["CINTO_NUNCA_RARAMENTE"],
       "2.11.4": ["CINTO_FRENTE", "CINTO_TRAS"], "2.11.5": ["CAPACETE_AS_VEZES_OU_MAIS"], "2.11.6": ["CONDUZIU_VEICULO"],
       "2.11.7": ["CONDUTOR_ALCOOL"], "2.11.9": ["BRIGA_ARMA_FOGO"], "2.11.10": ["BRIGA_ARMA_BRANCA"]}
AGES = {"13 a 17 anos": [13, 14, 15, 16, 17], "13 a 15 anos": [13, 14, 15], "16 e 17 anos": [16, 17]}
TER = {"Brasil": None, "Norte": 1, "Nordeste": 2, "Sudeste": 3, "Sul": 4, "Centro-Oeste": 5}
CUTS5 = ["Total", "Masculino", "Feminino", "Pública", "Privada"]

def published():
    wb = xlrd.open_workbook(XLS); out = {}
    for tab, keys in TAB.items():
        sh = wb.sheet_by_name(tab); age = None
        hdr_row = 7 if tab == "2.11.4" else 6
        for r in range(hdr_row, sh.nrows):
            lab = str(sh.cell_value(r, 0)).strip()
            if lab in AGES: age = lab; continue
            if lab not in TER or age is None: continue
            vals = [sh.cell_value(r, c) for c in range(1, sh.ncols)]
            if tab == "2.11.4":   # (Total F,T)(Masc F,T)(Fem F,T)(Púb F,T)(Priv F,T)
                for i, cut in enumerate(CUTS5):
                    for j, k in enumerate(keys):
                        b = (2 * i + j) * 3
                        if b + 2 < len(vals): out[(k, age, lab, cut)] = (vals[b], vals[b + 1], vals[b + 2], f"{tab}!R{r+1}C{b+2}")
            else:
                for i, cut in enumerate(CUTS5):
                    b = 3 * i; out[(keys[0], age, lab, cut)] = (vals[b], vals[b + 1], vals[b + 2], f"{tab}!R{r+1}C{b+2}")
    return out

def conds(ind): return ind["any"] if "any" in ind else [{"var": ind["var"], "num": ind["num"], "den": ind["den"]}]

pub = published()
keys = sorted({k for k, *_ in pub})
cols = {"PESO", "ESTRATOGEOREG", "ESTRATO_EXP", "escola", "VB01003", "VB01001", "V0007", "REGEOGR"} | {"V" + c["var"] for k in keys for c in conds(inds[k])}
df = pd.read_csv(f"{ROOT}/data/microdata/PENSE_2015_A2/PENSE_AMOSTRA2_ALUNO.CSV", sep=";", decimal=",", usecols=list(cols), low_memory=False)
df = df[df.PESO > 0].reset_index(drop=True)
designs = {s: DesignArrays.build(df.PESO.to_numpy(), df[s].to_numpy(), (df[s].astype(str) + "|" + df.escola.astype(str)).to_numpy(), None)
           for s in ("ESTRATOGEOREG", "ESTRATO_EXP")}
cutmask = {"Total": np.ones(len(df), bool), "Masculino": (df.VB01001 == 1).to_numpy(), "Feminino": (df.VB01001 == 2).to_numpy(),
           "Pública": (df.V0007 == 1).to_numpy(), "Privada": (df.V0007 == 2).to_numpy()}
rows = []
for k in keys:
    num = np.zeros(len(df), bool); den = np.zeros(len(df), bool)
    for c in conds(inds[k]):
        col = df["V" + c["var"]]; num |= col.isin(c["num"]).to_numpy(); den |= col.isin(c["den"]).to_numpy()
    num &= den
    for age, al in AGES.items():
        am = df.VB01003.isin(al).to_numpy()
        for ter, code in TER.items():
            tm = np.ones(len(df), bool) if code is None else (df.REGEOGR == code).to_numpy()
            for cut, cm in cutmask.items():
                p = pub.get((k, age, ter, cut))
                if p is None or p[0] in ("", "-"): continue
                d = den & am & tm & cm
                rec = {"indicator_key": k, "age_group": age, "territory": ter, "cut": cut, "published": float(p[0]),
                       "pub_lo": float(p[1]), "pub_hi": float(p[2]), "cell": p[3]}
                for s, D in designs.items():
                    e = ratio(D, (num & d).astype(float), d.astype(float)); tag = "geo" if s == "ESTRATOGEOREG" else "exp"
                    rec[f"est_{tag}"] = 100 * e.p; rec[f"lo_{tag}"] = 100 * e.ci_lower; rec[f"hi_{tag}"] = 100 * e.ci_upper
                rows.append(rec)
out = pd.DataFrame(rows)
out["d_est"] = out.est_exp - out.published
for t in ("geo", "exp"):
    out[f"d_ci_{t}"] = np.maximum(abs(out[f"lo_{t}"] - out.pub_lo), abs(out[f"hi_{t}"] - out.pub_hi))
out.to_csv(sys.argv[3] if len(sys.argv) > 3 else "validacao_2015_a2.csv", index=False, encoding="utf-8-sig")
print(f"recortes comparados: {len(out)}  (indicadores: {len(keys)})")
print(f"estimativa: |Δ| ≤ 0,05 p.p. em {(abs(out.d_est) <= 0.05).mean():.1%}; máx |Δ| = {abs(out.d_est).max():.4f} p.p.")
for t, nome in (("geo", "ESTRATOGEOREG (config atual)"), ("exp", "ESTRATO_EXP")):
    print(f"IC com {nome:28}: limites ≤ 0,15 p.p. em {(out[f'd_ci_{t}'] <= 0.15).mean():6.1%}; mediana {out[f'd_ci_{t}'].median():.3f}; máx {out[f'd_ci_{t}'].max():.3f}")
g = out.groupby("indicator_key").agg(n=("d_est", "size"), max_d_est=("d_est", lambda s: s.abs().max()),
                                     ci_ok_geo=("d_ci_geo", lambda s: (s <= 0.15).mean()), ci_ok_exp=("d_ci_exp", lambda s: (s <= 0.15).mean()))
print(g.round(4).to_string())

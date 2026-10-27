import pandas as pd, numpy as np, tomllib, sys
P = sys.argv[1]
inds = tomllib.load(open(f"{P}/config/microdata/indicators.toml","rb"))
keys = [k for k,v in inds.items() if "PENSE_2015_A2" in v.get("editions",[])]
spec = {"PENSE_2019": (f"{P}/data/microdata/PENSE_2019/PENSE2019_MICRODADOS.csv", ",", "", "B01003", [2,3], 9, "PESO_ALUNO_FREQ"),
        "PENSE_2024": (f"{P}/data/microdata/PENSE_2024/PENSE2024_MICRODADOS.csv", ",", "", "IDADE_AGREG", [2,3], -9, "PESO_ALUNO_FREQ"),
        "PENSE_2015_A2": (f"{P}/data/microdata/PENSE_2015_A2/PENSE_AMOSTRA2_ALUNO.CSV", ";", "V", "VB01003", [13,14,15,16,17], 99, "PESO")}
def conds(ind): return ind["any"] if "any" in ind else [{"var":ind["var"],"num":ind["num"],"den":ind["den"]}]
print(f"{'indicador':28} {'edição':14} {'sem NR':>8} {'com NR':>8} {'Δ p.p.':>7} {'%NR no den':>10}")
for ed,(f,sep,pre,agev,ages,nr,wv) in spec.items():
    cols = {agev, wv} | {pre+c["var"] for k in keys for c in conds(inds[k])}
    df = pd.read_csv(f, sep=sep, decimal="," if sep==";" else ".", usecols=list(cols), low_memory=False)
    df = df[(df[wv]>0) & df[agev].isin(ages)]; w = df[wv]
    for k in keys:
        num = np.zeros(len(df),bool); d0 = np.zeros(len(df),bool); d1 = np.zeros(len(df),bool)
        for c in conds(inds[k]):
            col = df[pre+c["var"]]; num |= col.isin(c["num"]); d0 |= col.isin(c["den"]); d1 |= col.isin(list(c["den"])+[nr])
        a = 100*w[num&d0].sum()/w[d0].sum(); b = 100*w[num&d1].sum()/w[d1].sum()
        print(f"{k:28} {ed:14} {a:8.3f} {b:8.3f} {b-a:7.3f} {100*(w[d1].sum()-w[d0].sum())/w[d1].sum():10.2f}")

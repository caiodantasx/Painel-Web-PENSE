import sys; sys.path.insert(0, sys.argv[1] + "/src")
import pandas as pd, numpy as np
from pense.microdata.estimator import DesignArrays, ratio
f = sys.argv[1] + "/data/microdata/PENSE_2015_A2/PENSE_AMOSTRA2_ALUNO.CSV"
df = pd.read_csv(f, sep=";", decimal=",", usecols=["PESO","ESTRATOGEOREG","ESTRATO_EXP","escola","VB01003","VB09001","VB09007A","VB09006A2","VB09008"], low_memory=False)
df = df[(df.PESO > 0)].reset_index(drop=True); dom = df.VB01003.isin([13,14,15,16,17]).to_numpy()
for s in ["ESTRATOGEOREG", "ESTRATO_EXP"]:
    psu = (df[s].astype(str) + "|" + df.escola.astype(str)).to_numpy()
    D = DesignArrays.build(df.PESO.to_numpy(), df[s].to_numpy(), psu, None)
    out = []
    for v, n, d in [("VB09001",[2,3,4,5,6],[1,2,3,4,5,6]),("VB09007A",[3,4,5,6],[2,3,4,5,6]),("VB09006A2",[2,3],[2,3,4,5,6]),("VB09008",[2,3,4,5],[1,2,3,4,5])]:
        den = df[v].isin(d).to_numpy() & dom; num = df[v].isin(n).to_numpy() & den
        e = ratio(D, num.astype(float), den.astype(float)); out.append(f"{v}: {100*e.p:.2f} ± EP {100*e.se:.3f}")
    print(f"{s:14} estratos={int(D.stratum.max()+1):4d}  " + " | ".join(out))

import pandas as pd, numpy as np, sys
path = sys.argv[1]
cols = pd.read_csv(path, sep=";", nrows=0).columns.tolist()
q = [c for c in cols if c.startswith("VB") and c not in ("VB00004",)]
df = pd.read_csv(path, sep=";", decimal=",", usecols=q + ["MUNICIPIO_CAP", "PESO"], low_memory=False)
d = df[(df.PESO > 0) & (df.MUNICIPIO_CAP.fillna(0) > 0)].reset_index(drop=True); w = d.PESO.to_numpy()
A = d[q].to_numpy(dtype=float)
answered = ~np.isin(A, [99]) & ~np.isnan(A) & (A != -1)        # resposta efetiva (não 99, não pulo)
idx = np.arange(len(q))
last = np.where(answered.any(1), (answered * idx).max(1), -1)   # última pergunta respondida
T = {"10.7 trajeto":("VB09001",[2,3,4,5,6],[1,2,3,4,5,6],12.74565), "10.8 escola":("VB09002",[2,3,4,5,6],[1,2,3,4,5,6],9.281001),
     "10.1 cinto frente":("VB09006A1",[2,3],[2,3,4,5,6],15.37358), "10.2 cinto trás":("VB09006A2",[2,3],[2,3,4,5,6],32.22794),
     "10.4 capacete":("VB09007A",[2,3],[2,3,4,5,6],18.62891), "10.5 conduziu":("VB09008",[2,3,4,5],[1,2,3,4,5],24.59877),
     "10.6 condutor álcool":("VB09009",[2,3,4,5],[1,2,3,4,5],25.19689), "10.11 arma branca":("VB09005",[1],[1,2],8.113085)}
print(f"{'tabela':22} {'publicado':>9} {'sem 99':>8} {'com 99':>8} {'99 s/ aband.':>12} {'Δ p.p.':>7}")
for k,(v,n,dn,pub) in T.items():
    j = q.index(v); c = A[:, j]
    nr = c == 99; aband = nr & (last < j)
    num = np.isin(c, n); den_valid = np.isin(c, dn)
    s = lambda m: w[m].sum()
    a, b, h = 100*s(num)/s(den_valid), 100*s(num)/s(den_valid|nr), 100*s(num)/s(den_valid|(nr&~aband))
    print(f"{k:22} {pub:9.3f} {a:8.3f} {b:8.3f} {h:12.3f} {h-pub:7.3f}")

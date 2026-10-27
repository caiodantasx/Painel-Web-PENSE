import pandas as pd, sys
df = pd.read_csv(sys.argv[1], sep=";", decimal=",", usecols=["MUNICIPIO_CAP","PESO","VB09001","VB09002","VB09006A1","VB09006A2","VB09007A","VB09008","VB09009","VB09005"], low_memory=False)
d = df[(df.PESO>0)&(df.MUNICIPIO_CAP.fillna(0)>0)]; w = d.PESO
T = {"10.7 trajeto":("VB09001",[2,3,4,5,6],[1,2,3,4,5,6],12.74565), "10.8 escola":("VB09002",[2,3,4,5,6],[1,2,3,4,5,6],9.281001),
     "10.1 cinto frente":("VB09006A1",[2,3],[2,3,4,5,6],15.37358), "10.2 cinto trás":("VB09006A2",[2,3],[2,3,4,5,6],32.22794),
     "10.4 capacete":("VB09007A",[2,3],[2,3,4,5,6],18.62891), "10.5 conduziu":("VB09008",[2,3,4,5],[1,2,3,4,5],24.59877),
     "10.6 condutor álcool":("VB09009",[2,3,4,5],[1,2,3,4,5],25.19689), "10.11 arma branca":("VB09005",[1],[1,2],8.113085)}
print(f"{'tabela':22} {'publicado':>9} {'sem 99':>8} {'com 99':>8}  códigos presentes")
for k,(v,n,dn,pub) in T.items():
    c = d[v]; a = 100*w[c.isin(n)].sum()/w[c.isin(dn)].sum(); b = 100*w[c.isin(n)].sum()/w[c.isin(dn+[99])].sum()
    print(f"{k:22} {pub:9.3f} {a:8.3f} {b:8.3f}  {sorted(c.dropna().unique().astype(int))}")

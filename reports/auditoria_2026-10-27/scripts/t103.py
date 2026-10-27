import pandas as pd, numpy as np, sys
df = pd.read_csv(sys.argv[1], usecols=["ANO_TURMA","MUNICIPIO_CAP","B09006A1","B09006A2","PESO_ALUNO_FREQ"])
d = df[(df.ANO_TURMA==3)&(df.MUNICIPIO_CAP>0)&(df.PESO_ALUNO_FREQ>0)]
f, b, w = d.B09006A1, d.B09006A2, d.PESO_ALUNO_FREQ
print("códigos frente:", sorted(f.unique()), "trás:", sorted(b.unique()))
R = lambda s: s.isin([2,3]); RODE = lambda s: s.isin([2,3,4,5,6])
def p(num, den): return round(100*w[num&den].sum()/w[den].sum(), 4)
V = {
 "V0 atual: den = (f∈2-6,9) ou (b∈2-6,9)": p(R(f)|R(b), f.isin([2,3,4,5,6,9])|b.isin([2,3,4,5,6,9])),
 "V1 den = andou em algum banco (sem 9)": p(R(f)|R(b), RODE(f)|RODE(b)),
 "V2 den = andou em algum + ambos respondidos (≠9,-2)": p(R(f)|R(b), (RODE(f)|RODE(b)) & ~f.isin([9,-2]) & ~b.isin([9,-2])),
 "V3 den = andou em algum, 9 no outro conta": p(R(f)|R(b), (RODE(f)|RODE(b)) | ((f==9)&(b==9))),
 "V4 den = andou em algum ou 9 em algum (≠-2)": p(R(f)|R(b), (RODE(f)|RODE(b)) | (f==9) | (b==9)),
}
for k,v in V.items(): print(f"{v:8.4f}  {k}")
print("---")
W = {
 "V5 den inclui -2 em qualquer": p(R(f)|R(b), f.isin([2,3,4,5,6,9,-2])|b.isin([2,3,4,5,6,9,-2])),
 "V6 num ambos (e)": p(R(f)&R(b), RODE(f)|RODE(b)),
 "V7 num: frente se andou na frente, senão trás": p(np.where(RODE(f), R(f), R(b)), RODE(f)|RODE(b)),
 "V8 den todos respondentes (inclui 1)": p(R(f)|R(b), f.isin([1,2,3,4,5,6,9])|b.isin([1,2,3,4,5,6,9])),
 "V9 den andou em algum ou 1 em ambos 9?": p(R(f)|R(b), (RODE(f)|RODE(b)) | f.isin([9,-2]) | b.isin([9,-2])),
}
for k,v in W.items(): print(f"{v:8.4f}  {k}")
print("alvo publicado 32.3544")

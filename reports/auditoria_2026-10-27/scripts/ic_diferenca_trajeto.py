"""Verifica os métodos do IC da diferença 2019→2024 de TRAJETO_INSEGURO (Brasil, total).

Uso (na raiz do projeto): python reports/auditoria_2026-10-27/scripts/ic_diferenca_trajeto.py [data/curated] [saída.md]
(padrões: data/curated deste projeto; reports/auditoria_2026-10-27/ic_diferenca_trajeto_2019_2024.md).
Usa as estimativas na convenção da série e os IC publicados conferidos em microdata_validation.csv.
Lê só arquivos; não escreve no projeto.
"""
import csv, math, sys
from pathlib import Path

Z = 1.959963984540054
PROJ = Path(__file__).resolve().parents[3]
cur = Path(sys.argv[1]) if len(sys.argv) > 1 else PROJ / "data" / "curated"
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else PROJ / "reports" / "auditoria_2026-10-27" / "ic_diferenca_trajeto_2019_2024.md"
rows = list(csv.DictReader(open(cur / "microdata_estimates.csv", encoding="utf-8-sig")))
tot = lambda r: r["territory_code"] == "BR" and r["age_group"] == "Total" and r["sex"] == "Total" and r["admin_dependency"] == "Total"
m = {r["edition_id"]: r for r in rows if r["indicator_key"] == "TRAJETO_INSEGURO" and tot(r)
     and "SERIE" in r["nonresponse_convention"].split("+")}
val = [r for r in csv.DictReader(open(cur / "microdata_validation.csv", encoding="utf-8-sig"))
       if r["indicator_key"] == "TRAJETO_INSEGURO" and tot(r) and r["edition_id"] in ("PENSE_2019", "PENSE_2024")]
ser = [r for r in csv.DictReader(open(cur / "microdata_series.csv", encoding="utf-8-sig"))
       if r["indicator_key"] == "TRAJETO_INSEGURO" and tot(r) and r["year"] == "2024"][0]
out = ["# IC da diferença 2019→2024 — TRAJETO_INSEGURO, Brasil, total", ""]

# A) microdados: EP de desenho (Taylor; estrato+UPA; pós-estratificação), amostras independentes
e19, e24 = (float(m[e]["estimate"]) for e in ("PENSE_2019", "PENSE_2024"))
s19, s24 = (float(m[e]["standard_error"]) for e in ("PENSE_2019", "PENSE_2024"))
d = e24 - e19; sd = math.hypot(s19, s24)
out += ["## A. Microdados (método usado pela pipeline, `series.build_series`)", "",
        f"* 2019: {e19:.4f} % (EP {s19:.4f}); 2024: {e24:.4f} % (EP {s24:.4f})",
        f"* d = {d:.4f} p.p.; EP(d) = √(EP₁² + EP₂²) = {sd:.4f}; IC 95% = [{d - Z*sd:.4f}; {d + Z*sd:.4f}]; "
        f"|d|/EP(d) = {abs(d)/sd:.3f} (> 1,96 → significativa)",
        f"* conferência com `microdata_series.csv`: diff_pp {float(ser['diff_pp']):.4f}, IC [{float(ser['diff_ci_lower']):.4f}; "
        f"{float(ser['diff_ci_upper']):.4f}], significant_5pct {ser['significant_5pct']}", ""]

# B) só com os IC publicados: EP aproximado = (sup − inf)/(2·1,96)
pub = {}
for r in val:
    lo, hi = (float(x) for x in r["ci_published"].split("–"))
    pub[r["edition_id"]] = (float(r["estimate_published"]), lo, hi, r["published_cell"])
out += ["## B. Só com os IC publicados (aproximação)", ""]
for e, (p, lo, hi, cell) in pub.items():
    out.append(f"* {e}: {p:.4f} [{lo:.4f}; {hi:.4f}] (célula {cell}); assimetria (sup−est) − (est−inf) = {(hi-p)-(p-lo):+.4f}")
(p19, l19, h19, _), (p24, l24, h24, _) = pub["PENSE_2019"], pub["PENSE_2024"]
a19, a24 = (h19 - l19) / (2*Z), (h24 - l24) / (2*Z)
dp = p24 - p19; sdp = math.hypot(a19, a24)
out += [f"* EP derivado: 2019 {a19:.4f} (microdados {s19:.4f}); 2024 {a24:.4f} (microdados {s24:.4f})",
        f"* d = {dp:.4f} p.p.; EP(d) ≈ {sdp:.4f}; IC 95% ≈ [{dp - Z*sdp:.4f}; {dp + Z*sdp:.4f}]; |d|/EP(d) = {abs(dp)/sdp:.3f}", ""]

# C) sobreposição dos IC (NÃO é teste da diferença)
out += ["## C. Sobreposição dos IC publicados (não é teste)", "",
        f"* os IC se sobrepõem ({l24:.2f} < {h19:.2f}) e mesmo assim a diferença é significativa: sobreposição não serve como teste.", ""]

# sensibilidade ao arredondamento: só com os valores impressos (2 casas) a ±0,005
r2 = lambda x: round(x, 2)
p19, l19, h19, p24, l24, h24 = map(r2, (p19, l19, h19, p24, l24, h24)); dp = p24 - p19
worst = []
for dl19 in (-0.005, 0.005):
    for dh19 in (-0.005, 0.005):
        for dl24 in (-0.005, 0.005):
            for dh24 in (-0.005, 0.005):
                s = math.hypot((h19+dh19-l19-dl19)/(2*Z), (h24+dh24-l24-dl24)/(2*Z))
                for de in (-0.01, 0.0, 0.01):
                    worst.append((dp+de) - Z*s)
out += ["## D. Sensibilidade ao arredondamento (método B)", "",
        f"* usando os valores impressos com 2 casas ({p19}, [{l19}; {h19}]; {p24}, [{l24}; {h24}]) e variando cada um em ±0,005 "
        f"(±0,01 na diferença): o limite inferior do IC da diferença vai de {min(worst):.4f} a {max(worst):.4f}.", ""]
OUT.write_text("\n".join(out) + "\n", encoding="utf-8")
print("\n".join(out))

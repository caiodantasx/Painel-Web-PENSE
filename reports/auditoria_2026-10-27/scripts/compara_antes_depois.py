"""Compara a série histórica antes (pacote de 27/10 07:40) e depois das correções.

Uso: python compara_antes_depois.py <antes/microdata_series.csv> <depois/microdata_series.csv> <saida.csv>
Recorte: total (Brasil para 13 a 17 anos; conjunto das capitais para o 9º ano).
"""
import csv
import sys


def load(p):
    with open(p, encoding="utf-8-sig", newline="") as fh:
        return {(r["indicator_key"], r["year"]): r for r in csv.DictReader(fh)
                if r["territory_code"] == ("CAPITAIS" if r["indicator_key"].startswith("NONO_") else "BR")
                and r["age_group"] == "Total" and r["sex"] == "Total"
                and r["admin_dependency"] == "Total"}


def lab_before(r):
    if not r or r.get("diff_pp", "") == "":
        return ""
    return "Mudança confirmada" if r["significant_5pct"].lower() == "true" else "Pode ser acaso"


LAB_AFTER = {"MUDANCA_CONFIRMADA": "Mudança confirmada", "SIGNIFICATIVA_SEM_DECISAO": "Significativa · aguardando decisão",
             "NAO_SIGNIFICATIVA": "Pode ser acaso", "": ""}

a, b = load(sys.argv[1]), load(sys.argv[2])
rows = []
for key in sorted(set(a) | set(b), key=lambda k: (k[0], int(k[1]))):
    ra, rb = a.get(key), b.get(key)
    f = lambda r, c: (f"{float(r[c]):.2f}" if r and r.get(c) not in ("", None) else "")  # noqa: E731
    rows.append({
        "indicator_key": key[0], "year": key[1],
        "estimativa_antes": f(ra, "estimate"), "estimativa_depois": f(rb, "estimate"),
        "variacao_antes_pp": f(ra, "diff_pp"), "variacao_depois_pp": f(rb, "diff_pp"),
        "ic_variacao_depois": (f"[{float(rb['diff_ci_lower']):.2f}; {float(rb['diff_ci_upper']):.2f}]"
                               if rb and rb.get("diff_ci_lower") not in ("", None) else ""),
        "selo_antes": lab_before(ra), "selo_depois": LAB_AFTER.get(rb.get("change_status", "") if rb else "", ""),
        "significativa_antes": (ra or {}).get("significant_5pct", ""), "significativa_depois": (rb or {}).get("significant_5pct", ""),
        "situacao": ("removido da série" if ra and not rb else "novo na série" if rb and not ra else
                     "significância mudou" if ra and rb and ra.get("significant_5pct") != rb.get("significant_5pct")
                     and ra.get("diff_pp") != "" else ""),
    })
with open(sys.argv[3], "w", encoding="utf-8-sig", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0]), lineterminator="\n")
    w.writeheader()
    w.writerows(rows)
print(f"{len(rows)} linhas → {sys.argv[3]}")
for r in rows:
    if r["situacao"] or r["selo_antes"] == "Mudança confirmada":
        print(f"{r['indicator_key'][:30]:30} {r['year']}  est {r['estimativa_antes']:>6}→{r['estimativa_depois']:>6}  "
              f"Δ {r['variacao_antes_pp']:>6}→{r['variacao_depois_pp']:>6}  {r['selo_antes'] or '—':20}→ {r['selo_depois'] or '—':34} {r['situacao']}")

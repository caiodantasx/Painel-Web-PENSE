"""Matriz de evidências metodológicas (indicador × edição), gerada das saídas — nada digitado à mão.

Saídas:
* data/curated/methodological_evidence_matrix.csv
* docs/13_matriz_evidencias.md

Uso:  python scripts/build_evidence_matrix.py   (rodado por scripts/run_all.py)
"""
from __future__ import annotations

import csv
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CUR = ROOT / "data" / "curated"
sys.path.insert(0, str(ROOT / "src"))

FIELDS = ["indicator_key", "indicator_label", "edition_id", "edition_year", "question_text", "question_source",
          "informant", "population", "numerator_rule", "denominator_rule", "nonresponse_rule_publication",
          "nonresponse_rule_series", "nonresponse_effect_pp", "official_source", "official_location",
          "estimate_validation", "ci_validation", "evidence_level", "in_series", "comparability_proposed",
          "comparability_final", "decision_status", "justification", "limitations"]

UNRESOLVED = [
    ("Tabela 8.1 (PeNSE 2009)", "56 observações em revisão (VAL022/HDR006): colunas por dependência sem categoria",
     "Publicação PeNSE 2009 (notas da tabela 8.1)"),
    ("Símbolo “–” nas tabelas de 2015 (Amostra 1)", "120 células mantidas como indisponíveis (VAL001), nunca convertidas em zero",
     "Convenções da publicação PeNSE 2015"),
    ("Regra de derivação da tabela oficial 10.3 (cinto, frente ou trás, 9º ano)",
     "Não reproduzida em 2015 nem 2019 (10 variantes testadas); fora da série",
     "Plano tabular específico da análise histórica (IBGE, 2022) ou código de derivação do IBGE"),
    ("Limiares de coeficiente de variação (15% e 30%)", "Critério de projeto, sem fonte oficial identificada",
     "Notas técnicas da PeNSE 2024 (seção de precisão), se houver"),
]


def rd(p: Path) -> list[dict]:
    if not p.exists():
        return []
    with p.open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def main() -> None:
    from pense.config import Config
    from pense.microdata.integrate import question_texts
    from pense.microdata.run import load_config

    cfg = Config(root=ROOT)
    editions, indicators = load_config(cfg)
    q = question_texts(cfg, indicators, editions)
    est = rd(CUR / "microdata_estimates.csv")
    summ = {(r["edition_id"], r["indicator_key"]): r for r in rd(CUR / "microdata_validation_summary.csv")}
    val = defaultdict(list)
    for r in rd(CUR / "microdata_validation.csv"):
        val[(r["edition_id"], r["indicator_key"])].append(r)
    comp = {r["indicator_key"]: r for r in rd(CUR / "microdata_comparability.csv")}
    eff = {(r["indicator_key"], r["edition_id"]): r for r in rd(CUR / "microdata_nonresponse_effect.csv")}
    tot = {}
    for e in est:
        if e["age_group"] == "Total" and e["sex"] == "Total" and e["admin_dependency"] == "Total" \
                and e["territory_code"] in ("BR", "CAPITAIS"):
            tot.setdefault((e["indicator_key"], e["edition_id"], e["nonresponse_convention"].split("+")[0]), e)
    rows = []
    for k, ind in indicators.items():
        c = comp.get(k, {})
        evid = {y: v.split(" (")[0] for y, v in (x.split(": ", 1) for x in c.get("evidence_by_edition", "").split("; ") if ": " in x)}
        for ed in ind["editions"]:
            if ed not in editions:
                continue
            spec, y = editions[ed], str(editions[ed]["year"])
            s, vs = summ.get((ed, k)), val.get((ed, k), [])
            t = tot.get((k, ed, "SERIE")) or tot.get((k, ed, "PUBLICACAO")) or {}
            ci_ok = sum(1 for r in vs if r["verdict"] == "REPRODUZ")
            ci_bad = sum(1 for r in vs if r["verdict"] == "ESTIMATIVA_OK_IC_DIFERE")
            loc = next((r["published_cell"] for r in vs if r["territory_code"] in ("BR", "CAPITAIS")
                        and r["age_group"] == "Total" and r["sex"] == "Total" and r["admin_dependency"] == "Total"), "")
            sr = spec.get("series_nonresponse")
            ef = eff.get((k, ed), {})
            rows.append({
                "indicator_key": k, "indicator_label": ind["label"], "edition_id": ed, "edition_year": y,
                "question_text": q.get(k, {}).get(ed, "") or "PENDENTE (variável sem texto no dicionário)",
                "question_source": f"dicionário de microdados {ed}" if q.get(k, {}).get(ed) else "",
                "informant": ind.get("informant", "Escolar (autopreenchimento)"),
                "population": t.get("population", ""), "numerator_rule": t.get("numerator_rule", ""),
                "denominator_rule": t.get("denominator_rule", ""),
                "nonresponse_rule_publication": f"códigos {spec.get('nonresponse_in_denominator', [])} no denominador — {spec.get('nonresponse_rule_status', '')}",
                "nonresponse_rule_series": sr["description"] if sr else "igual à da publicação (sem resposta entra, abandono sai)",
                "nonresponse_effect_pp": ef.get("efeito_harmonizacao_pp", ""),
                "official_source": ind.get("published", {}).get(ed, "") or "sem tabela publicada",
                "official_location": loc,
                "estimate_validation": (f"{s['status']}: {s['reproduz']}/{s['compared']} recortes reproduzem; máx Δ "
                                        f"{float(s['max_abs_diff_estimate_pp']):.3f} p.p.") if s else "NÃO VALIDADO (sem tabela)",
                "ci_validation": (f"estimativa e IC reproduzem em {ci_ok}/{len(vs)}; estimativa igual e IC diferente em {ci_bad}") if vs else "",
                "evidence_level": evid.get(y, ""),
                "in_series": ("não (excluída por decisão registrada; ver limitations)"
                              if ed in c.get("excluded_edition_ids", "").split("|") else
                              "sim" if (ed in c.get("series_editions", "").split("|")
                                        and c.get("final_status") in ("COMPARABLE", "COMPARABLE_WITH_CAVEATS")) else "não"),
                "comparability_proposed": c.get("proposed_status", ""), "comparability_final": c.get("final_status", ""),
                "decision_status": c.get("decision_status", ""), "justification": c.get("justification", ""),
                "limitations": c.get("caveats", ""),
            })
    out = CUR / "methodological_evidence_matrix.csv"
    with out.open("w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)

    L = ["# Matriz de evidências metodológicas", "",
         "Gerada por `scripts/build_evidence_matrix.py` a partir de `data/curated/microdata_*.csv` e da configuração. "
         "Tabela completa (com pergunta, regras de numerador/denominador e ressalvas): "
         "`data/curated/methodological_evidence_matrix.csv`.", "",
         "**Evidência:** DIRETA = o cálculo reproduz a tabela publicada da edição; INDIRETA = a mesma variável reproduz "
         "tabelas da edição (declarada em `indicators.toml`), valor calculado e não oficial; AUSENTE = sem tabela para "
         "conferir (ponto fora da série); FALHOU = não reproduz.", "",
         "**Decisão:** nenhuma comparação é aprovada automaticamente. `PROPOSTA_AUTOMATICA` aguarda o pesquisador em "
         "`config/microdata/comparability_decisions.csv` (modelo em `comparability_decisions_MODELO.csv`).", "",
         "| Indicador | Edição | Informante | Validação da estimativa | Estimativa e IC reproduzem | Evidência | Na série | Proposta | Decisão | Efeito harmonização (p.p.) |",
         "|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        L.append(f"| {r['indicator_key']} | {r['edition_year']} ({r['edition_id'].replace('PENSE_', '')}) | "
                 f"{'Escola (diretor)' if r['informant'].startswith('Escola (') else 'Aluno'} | {r['estimate_validation']} | "
                 f"{r['ci_validation'].split(';')[0].replace('estimativa e IC reproduzem em ', '') if r['ci_validation'] else '—'} | "
                 f"{r['evidence_level']} | {r['in_series']} | {r['comparability_proposed']} | {r['decision_status']} | "
                 f"{r['nonresponse_effect_pp'] or '—'} |")
    L += ["", "## Dúvidas NÃO resolvidas (sem evidência documental suficiente)", "",
          "| Item | Situação | Documento necessário |", "|---|---|---|"]
    L += [f"| {a} | {b} | {c} |" for a, b, c in UNRESOLVED]
    (ROOT / "docs" / "13_matriz_evidencias.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"matriz de evidências: {len(rows)} linhas → {out.relative_to(ROOT)} e docs/13_matriz_evidencias.md")


if __name__ == "__main__":
    main()

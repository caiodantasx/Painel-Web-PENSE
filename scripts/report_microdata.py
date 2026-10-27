"""Gera docs/12_microdados.md a partir dos resultados (nada é digitado à mão).

Uso:  python scripts/report_microdata.py   (rodado por scripts/run_all.py)
"""
from __future__ import annotations

import csv
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CUR = ROOT / "data" / "curated"


def rd(p: Path) -> list[dict]:
    if not p.exists():
        return []
    with p.open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def f1(v) -> str:
    return f"{float(v):.1f}".replace(".", ",")


def main() -> None:
    est, summ = rd(CUR / "microdata_estimates.csv"), rd(CUR / "microdata_validation_summary.csv")
    comp = {r["indicator_key"]: r for r in rd(CUR / "microdata_comparability.csv")}
    ser = rd(CUR / "microdata_series.csv")
    tent = rd(ROOT / "reports" / "tentativa_microdados_2009_2012_2015A1.csv")
    with (ROOT / "config" / "microdata" / "indicators.toml").open("rb") as fh:
        inds = tomllib.load(fh)
    with (ROOT / "config" / "microdata" / "editions.toml").open("rb") as fh:
        eds = tomllib.load(fh)
    tot = lambda r, t: r["territory_code"] == t and r["age_group"] == "Total" and r["sex"] == "Total" and r["admin_dependency"] == "Total"  # noqa: E731
    serie = lambda e: "SERIE" in e.get("nonresponse_convention", "PUBLICACAO+SERIE").split("+")  # noqa: E731
    br = {(e["indicator_key"], e["edition_year"]): e for e in est if tot(e, "BR") and serie(e)}
    effects = rd(CUR / "microdata_nonresponse_effect.csv")
    sig = {(s["indicator_key"], s["year"]): s for s in ser if tot(s, "BR")}

    L = ["# Microdados: indicadores recalculados, validação e séries", "",
         "Gerado por `scripts/report_microdata.py` a partir de `data/curated/microdata_*.csv`.", "",
         "## Fontes e desenho amostral", "",
         "| Edição | Arquivo | Estrato | UPA | Peso | Pós-estrato | Não resposta |", "|---|---|---|---|---|---|---|"]
    for k, e in eds.items():
        L.append(f"| {e['label']} | `{Path(e['file']).name}` | `{e['strata']}` | `{'+'.join(e['psu'])}` | `{e['weight']}` | "
                 f"`{e.get('poststrata') or '—'}` | {e.get('nonresponse_rule_status', '')} |")
    L += ["", "O exemplo oficial do IBGE (documentação 2019 e 2024: `svydesign(ids=~ESCOLA, strata=~ESTRATO_EXP, "
          "weights=~PESO_INICIAL, nest=TRUE)` + `postStratify(~POSEST)`, domínio `IND_EXPANSAO = 1`) é o desenho "
          "implementado; os pesos finais `PESO_ALUNO_FREQ` já são os pós-estratificados.", "",
          "## Validação contra as tabelas publicadas", "",
          "Por recorte: **REPRODUZ** (Δ estimativa ≤ 0,05 p.p. e limites do IC ≤ 0,15 p.p.), **PRÓXIMO** (≤ 0,30 p.p.). "
          "Indicador **VALIDADO**: nenhum recorte além de 0,30 p.p. e ≥ 95% reproduzindo. 2019 usa critério próprio "
          "(Nota técnica 01/2022): totais reproduzindo e nenhum recorte além de 2 p.p.", "",
          "| Ano | Indicador | Tabela | Iguais | Próximos | Fora | Máx. Δ | Status |", "|---|---|---|---|---|---|---|---|"]
    for s in summ:
        L.append(f"| {s['edition_id'].replace('PENSE_', '')} | {s['indicator_key']} | {s['published_table']} "
                 f"{s['published_category'][:24]} | {s['reproduz']}/{s['compared']} | {s.get('proximo', '')} | "
                 f"{s['nao_reproduz']} | {float(s['max_abs_diff_estimate_pp']):.3f} | {s['status']} |")
    L += ["", "## Achados", "",
          "* **2015 Amostra 2 (tabelas 2.11.x recebidas em 27/10/2026):** estimativas e IC reproduzem as tabelas em todos os "
          "recortes, desde que o estrato seja `ESTRATO_EXP` (com `ESTRATOGEOREG`, citado no Quadro 3 da Nota n. 01/2018, só "
          "64,6% dos IC reproduziam). Na Amostra 1 vale o inverso: `ESTRATOGEOREG` reproduz 97,1% dos IC da série oficial.",
          "* **Não resposta harmonizada (IBGE 2022, p. 18, nota 7):** a série usa 'sem resposta' no denominador e exclui o "
          "'abandono'. Em 2015 o código 99 mistura os dois; o abandono é reconstruído (99 sem nenhuma resposta posterior). "
          "Com essa regra a Amostra 1 reproduz os valores oficiais de 2015 da série do 9º ano (total das capitais, "
          "Δ ≤ 0,05 p.p.). O efeito medido por indicador está em `data/curated/microdata_nonresponse_effect.csv`.",
          "* **2019 — confidencialidade (Nota técnica 01/2022):** idade agregada e sexo/idade suprimidos em 0,3% dos "
          "registros (recodificados para 9). Totais de Brasil reproduzem (≤ 0,02 p.p.); como o registro com idade "
          "suprimida sai do domínio de 13 a 17 anos, as diferenças aparecem em TODOS os recortes (rede, UF, sexo), não só "
          "por sexo. A série do 9º ano (sem filtro de idade) reproduz o total das capitais exatamente.",
          "* **Capacete:** 2015 publicou 'às vezes a sempre'; 2019 e 2024 publicaram 'raramente a sempre' "
          "(confirmado pelos microdados). As duas definições são calculadas em todas as edições.",
          "* **Venda de drogas no entorno (17.1):** 2024 acrescenta 'ou usando' à pergunta (dicionários): não comparável.",
          "* **Tabela 9.10.1 de 2019:** linhas de seção com números repetidos (artefato da publicação), tratado (STB004).",
          "* **Tabela oficial 10.3 (cinto, frente ou trás, 9º ano):** regra não reproduzida em 2015 nem 2019 (definição do "
          "glossário do IBGE testada em 10 variantes); fora da série e da extensão 2024.",
          "* **Dicionário 2009:** rótulos de `DEP2` invertidos em relação aos dados (`DEPEND_ADM` = PRIVADA tem `DEP2` = 1); "
          "usa-se o texto.", ""]
    if tent:
        L += ["## Registro histórico: tentativa com os microdados de 2009, 2012 e 2015 (Amostra 1)", "",
              "Arquivo de registro (`reports/tentativa_microdados_2009_2012_2015A1.csv`, gerado em sessão anterior, SEM "
              "script gerador no projeto — mantido só como histórico). As linhas de 2015 A1 estão **superadas**: a Amostra 1 "
              "agora é validada pela pipeline na convenção da série (tabela de validação acima). 2009 e 2012 continuam "
              "pendentes; a série usa os **valores oficiais publicados** para 2009–2015.", "",
              "| Ano | Indicador | Tabela | Iguais | Fora | Máx. Δ | Status |", "|---|---|---|---|---|---|---|"]
        for s in tent:
            L.append(f"| {s['edition_id'].replace('PENSE_', '')} | {s['indicator_key']} | {s['published_table']} | "
                     f"{s['reproduz']}/{s['compared']} | {s['nao_reproduz']} | {float(s['max_abs_diff_estimate_pp']):.2f} | {s['status']} |")
        L.append("")
    import json
    bpath = ROOT / "dashboard" / "data" / "pense_bundle.json"
    off = json.loads(bpath.read_text(encoding="utf-8")).get("micro", {}).get("official") if bpath.exists() else None
    if off:
        cap = next(i for i, t in enumerate(off["territories"]) if t["code"] == "CAPITAIS")
        P = off["pts"]
        L += ["## Série oficial do 9º ano, total das capitais (IBGE 2009–2019 + extensão 2024)", "",
              "Estatística experimental do IBGE (Estudos e Pesquisas n. 46, 2022). ◇ = 2024 calculado com os microdados "
              "(não oficial; mesma regra que reproduz a tabela oficial de 2019). `*` = diferença significativa a 5% em "
              "relação à edição anterior. Entre anos publicados, o teste é aproximado (erro-padrão derivado do IC "
              "publicado) e nunca recebe o selo 'Diferença significativa a 5%'; na comparação 2019→2024 (microdados), "
              "o selo exige decisão metodológica registrada.", "",
              "| Tabela | Indicador | 2009 | 2012 | 2015 | 2019 | 2024 |", "|---|---|---|---|---|---|---|"]
        for fi, t in enumerate(off["tables"]):
            vals = {P["y"][i]: (P["e"][i], P["o"][i]) for i in range(len(P["f"]))
                    if P["f"][i] == fi and P["t"][i] == cap and P["s"][i] == 0 and P["d"][i] == 0}
            cells = []
            for y in (2009, 2012, 2015, 2019, 2024):
                if y not in vals:
                    cells.append("—")
                    continue
                d = off["diffs"].get(f"{fi}|CAPITAIS|Total|Total|{y}")
                cells.append(f1(vals[y][0]) + (" ◇" if vals[y][1] == "M" else "") + (" *" if d and d[4] else ""))
            L.append(f"| {t['family']} | {t['title'][:90]} | {' | '.join(cells)} |")
        L.append("")
    L += ["## Série harmonizada, Brasil, 13 a 17 anos (estimativa e IC 95%, %)", "",
          "Valores na convenção da série (2015 difere da tabela publicada pelo efeito da harmonização). `*` = diferença "
          "significativa a 5% em relação à edição anterior (IC 95% da diferença não inclui o zero). Na série harmonizada, "
          "o selo 'Diferença significativa a 5%' exige, além disso, decisão metodológica registrada aprovando a "
          "comparação (`config/microdata/comparability_decisions.csv`); sem decisão registrada, a diferença não recebe "
          "esse selo e aparece como 'aguarda decisão'. `*✓` = significativa e com decisão registrada (recebe o selo). "
          "Significância não indica relevância prática, causa nem ausência de outras limitações. "
          "`†` = ponto fora da série (sem tabela publicada para conferir).", "",
          "| Indicador | 2015 | 2019 | 2024 | Proposta | Decisão |", "|---|---|---|---|---|---|"]
    for k, ind in inds.items():
        if ind.get("population") == "9ANO":
            continue
        cells = []
        c = comp.get(k, {})
        ser_eds = c.get("series_editions", "").split("|")
        for y in ("2015", "2019", "2024"):
            e = br.get((k, y))
            s_ = sig.get((k, y), {})
            mark = (" *✓" if s_.get("change_status") == "SIGNIFICATIVA_5PCT_COM_DECISAO" else
                    " *" if s_.get("significant_5pct", "").lower() == "true" else "")
            excl_ids = c.get("excluded_edition_ids", "").split("|")
            out_ = (" ⊘" if e and e["edition_id"] in excl_ids else " †" if e and e["edition_id"] not in ser_eds else "")
            cells.append(f"{f1(e['estimate'])} ({f1(e['ci_lower'])}–{f1(e['ci_upper'])}){mark}{out_}" if e else "—")
        L.append(f"| {ind['label']} | {' | '.join(cells)} | `{c.get('proposed_status', '')}` | {c.get('decision_status', '')} |")
    excl_rows = [(k, c) for k, c in comp.items() if c.get("excluded_editions")]
    if excl_rows:
        L += ["", "`⊘` = edição fora da série principal por decisão registrada em `config/microdata/series_exclusions.csv` "
              "(o valor continua disponível para consulta; não entra em variação nem selo).", "",
              "### Edições fora da série principal por decisão registrada", ""]
        L += [f"* `{k}` — {c['excluded_editions']}" for k, c in excl_rows]
    L += ["", "## Comparabilidade: proposta automática e decisão do pesquisador", "",
          "Evidências usadas: mesma variável e códigos; **redação comparada palavra por palavra nos dicionários do IBGE**; "
          "mesmo universo; reprodução das tabelas publicadas. Para confirmar ou alterar, registrar em "
          "`config/microdata/comparability_decisions.csv`.", ""]
    for k, c in comp.items():
        if c["final_status"] != "COMPARABLE_WITH_CAVEATS":
            L.append(f"* `{k}` → **{c['final_status']}**: {c['caveats'][:300]}")
    if effects:
        L += ["", "## Efeito medido da harmonização da não resposta (total: Brasil ou conjunto das capitais)", "",
              "| Indicador | Edição | Sem não resposta | Publicação | Série | Série − publicação (p.p.) |", "|---|---|---|---|---|---|"]
        for r in effects:
            if r["efeito_harmonizacao_pp"] not in ("", "0.0"):
                L.append(f"| {r['indicator_key']} | {r['edition_id'].replace('PENSE_', '')} | {f1(r['estimate_sem_nao_resposta'])} | "
                         f"{f1(r['estimate_publicacao'])} | {f1(r['estimate_serie'])} | {float(r['efeito_harmonizacao_pp']):+.2f} |")
    (ROOT / "docs" / "12_microdados.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("docs/12_microdados.md atualizado")


if __name__ == "__main__":
    main()

"""Regras de qualidade determinísticas e detecção de valores incomuns.

Princípios:
* nenhuma observação é removida ou corrigida — as regras só *sinalizam*;
* cada alerta traz regra, valor, contexto, célula, severidade, classe,
  justificativa e ação recomendada;
* valores extremos não são tratados como erro: recebem classe
  ``POSSIVEL_VALOR_EXTREMO_LEGITIMO`` e severidade informativa.
"""
from __future__ import annotations

import statistics
from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Any, Iterable

from ..models import APPROVABLE, Issue, IssueClass, Severity, ValidationStatus

DIMS = ("age_group", "sex", "admin_dependency")
FLAG_RULES = {
    "TERRITORIO_NAO_RECONHECIDO": ("VAL012", "Território não reconhecido no dicionário territorial",
                                   "Adicionar alias em config/territories.csv ou corrigir o rótulo."),
    "SECAO_NAO_RECONHECIDA": ("VAL021", "Seção (rótulo de linha) não reconhecida",
                              "Adicionar o rótulo ao vocabulário ou tratar no adaptador."),
    "CABECALHO_ASSIMETRICO": ("VAL022", "Coluna de dimensão sem categoria em cabeçalho assimétrico",
                              "Consultar a publicação para definir o indicador destas colunas."),
    "CONFLITO_DIMENSAO_LINHA_COLUNA": ("VAL023", "Mesma dimensão definida na linha e na coluna",
                                       "Revisar a interpretação da aba."),
    "ANO_INCONSISTENTE": ("VAL013", "Ano do título difere do ano do rodapé",
                          "Conferir a edição correta na publicação."),
    "ANO_DA_CELULA": ("VAL024", "Ano lido do cabeçalho/seção (tabela com vários anos)",
                      "Conferir na publicação se as colunas de anos medem o mesmo indicador e universo."),
    "ANO_INDEFINIDO": ("VAL025", "Tabela com vários anos sem ano identificável para este valor",
                       "Identificar o ano na planilha e ajustar o adaptador; o valor não entra na análise."),
}
FLAG_SEVERITY = {"ANO_INCONSISTENTE": Severity.ERROR, "ANO_DA_CELULA": Severity.INFO}


@dataclass
class ValidationSettings:
    float_tol: float = 1e-6
    ci_tol: float = 1e-6
    dist_sum_tol: float = 0.5
    count_rel_tol: float = 0.005
    cv_high: float = 30.0
    cv_ci_rel_tol: float = 0.05
    robust_z: float = 3.5
    min_group: int = 8

    @classmethod
    def from_config(cls, v: dict[str, Any]) -> "ValidationSettings":
        return cls(v["float_tolerance"], v["estimate_in_ci_tolerance"], v["distribution_sum_tolerance"],
                   v["count_additivity_rel_tolerance"], v["cv_high_threshold"], v["cv_ci_rel_tolerance"],
                   v["robust_z_threshold"], int(v["min_group_size_for_outliers"]))


class Validator:
    def __init__(self, settings: ValidationSettings, symbols: dict[str, dict[str, str]]):
        self.s = settings
        self.symbols = symbols
        self.issues: list[Issue] = []
        self.checks: Counter[str] = Counter()  # nº de avaliações por regra (prova de que a regra rodou)

    # ------------------------------------------------------------------ API
    def run(self, records: list[dict[str, Any]]) -> list[Issue]:
        for rec in records:
            self._record_rules(rec)
        self._duplicates(records)
        self._cross_table(records)
        self._distribution_sums(records)
        self._partition_bounds(records)
        self._count_additivity(records)
        self._outliers(records)
        return self.issues

    # ------------------------------------------------------ regras por linha
    def _record_rules(self, rec: dict[str, Any]) -> None:
        s = self.s
        kind = rec.get("estimate_kind")
        est, lo, hi, cv = rec.get("estimate"), rec.get("ci_lower"), rec.get("ci_upper"), rec.get("coefficient_of_variation")
        pct = rec.get("unit") == "%"
        for flag in filter(None, (rec.get("extraction_flags") or "").split("|")):
            rule, msg, action = FLAG_RULES.get(flag, ("VAL099", f"Alerta do adaptador: {flag}", "Revisar."))
            sev = FLAG_SEVERITY.get(flag, Severity.REVIEW)
            cls = IssueClass.INFORMATIONAL if sev in (Severity.WARNING, Severity.INFO) else IssueClass.NOT_VALIDATED
            self._add(rule, sev, cls, msg, rec, action)
        if kind == "symbol":
            meaning = self.symbols.get(rec["estimate_symbol"], {}).get("meaning", "símbolo não documentado")
            self._add("VAL001", Severity.INFO, IssueClass.INFORMATIONAL,
                      f"Estimativa publicada como símbolo '{rec['estimate_symbol']}' ({meaning})", rec,
                      "Nenhuma: valor mantido como indisponível; não converter em zero sem decisão documentada.")
        elif kind == "empty":
            self._add("VAL001", Severity.REVIEW, IssueClass.NOT_VALIDATED, "Célula da estimativa vazia", rec,
                      "Conferir se a ausência é intencional na publicação.")
        elif kind == "excel_error":
            self._add("VAL017", Severity.ERROR, IssueClass.CONFIRMED_ERROR,
                      f"Erro do Excel na célula ({rec['estimate_raw']})", rec, "Obter nova versão do arquivo.")
        elif kind == "text":
            self._add("VAL016", Severity.REVIEW, IssueClass.NOT_VALIDATED,
                      f"Texto não numérico na célula da estimativa ('{rec['estimate_raw']}')", rec,
                      "Verificar se é símbolo não documentado (config/symbols.csv).")
        for name, val, cell in (("estimativa", est, rec.get("source_cell")), ("limite inferior", lo, rec.get("ci_lower_cell")),
                                ("limite superior", hi, rec.get("ci_upper_cell"))):
            if val is None:
                continue
            self.checks["VAL002"] += 1
            if pct and name != "estimativa" and val < -s.float_tol:
                self._add("VAL002N", Severity.WARNING, IssueClass.POSSIBLE_ANOMALY,
                          f"Limite inferior do IC publicado abaixo de zero ({val}); IC normal não truncado na "
                          "publicação. Valor preservado; o gráfico exibe o IC limitado a 0 com nota", rec,
                          "Citar o IC como publicado; não substituir por 0 na base.", observed=val, cell=cell)
            elif pct and (val < -s.float_tol or val > 100 + s.float_tol):
                self._add("VAL002", Severity.ERROR, IssueClass.CONFIRMED_ERROR,
                          f"Percentual fora de [0, 100] ({name} = {val})", rec,
                          "Conferir a unidade da coluna e o valor publicado.", observed=val, cell=cell)
            elif pct and (val < 0 or val > 100):
                self._add("VAL002F", Severity.INFO, IssueClass.INFORMATIONAL,
                          f"Artefato de ponto flutuante ({name} = {val!r}); valor preservado sem arredondar", rec,
                          "Nenhuma: diferença menor que a tolerância numérica.", observed=val, cell=cell)
            if not pct and val < 0:
                self._add("VAL018", Severity.ERROR, IssueClass.CONFIRMED_ERROR,
                          f"Valor negativo em contagem ({name} = {val})", rec, "Conferir o valor publicado.",
                          observed=val, cell=cell)
        has_lo, has_hi = lo is not None, hi is not None
        if rec.get("ci_lower_cell") and has_lo != has_hi and kind == "number":
            self._add("VAL007", Severity.ERROR, IssueClass.CONFIRMED_ERROR, "IC com apenas um dos limites", rec,
                      "Conferir as células do IC.")
        if has_lo and has_hi:
            self.checks["VAL003/VAL004"] += 1
            if lo > hi + s.ci_tol:
                self._add("VAL003", Severity.ERROR, IssueClass.CONFIRMED_ERROR,
                          f"IC invertido (LI {lo} > LS {hi})", rec, "Conferir a ordem das colunas do IC.")
            elif est is not None and (est < lo - s.ci_tol * max(1, abs(est)) or est > hi + s.ci_tol * max(1, abs(est))):
                self._add("VAL004", Severity.ERROR, IssueClass.CONFIRMED_ERROR,
                          f"Estimativa {est} fora do IC [{lo}, {hi}]", rec,
                          "Verificar se as colunas de estimativa e IC foram associadas corretamente.")
            if hi - lo <= s.float_tol and est is not None:
                self._add("VAL005", Severity.WARNING, IssueClass.POSSIBLE_ANOMALY,
                          f"IC com amplitude zero ([{lo}, {hi}]): estimativa sem variabilidade amostral "
                          "aparente — típico de recortes com pouquíssimas unidades", rec,
                          "Interpretar com cautela; não usar para comparação sem consultar o CV.")
            elif pct and (lo <= s.float_tol or hi >= 100 - s.float_tol):
                self._add("VAL006", Severity.INFO, IssueClass.INFORMATIONAL,
                          "IC truncado no limite do intervalo [0, 100]", rec,
                          "Nenhuma: o IBGE limita o IC ao domínio do percentual; o IC fica assimétrico.")
        if cv is not None:
            self.checks["VAL008"] += 1
        if cv is not None and cv >= s.cv_high:
            self._add("VAL008", Severity.WARNING, IssueClass.LEGIT_EXTREME,
                      f"CV elevado ({cv:.1f}% ≥ {s.cv_high:.0f}%): baixa precisão", rec,
                      "Exibir com aviso de baixa precisão; evitar ranqueamentos baseados neste valor.", observed=cv)
        se = rec.get("standard_error")
        if se is not None and cv is not None and est:
            se_cv = cv * est / 100
            self.checks["VAL009"] += 1
            if se_cv > 0 and abs(se - se_cv) / se_cv > s.cv_ci_rel_tol:
                self._add("VAL009", Severity.WARNING, IssueClass.POSSIBLE_ANOMALY,
                          f"CV publicado ({cv:.3f}%) incoerente com a amplitude do IC (EP derivado {se:.4f} vs "
                          f"EP pelo CV {se_cv:.4f})", rec,
                          "Conferir se IC e CV se referem à mesma estimativa.", observed=cv)

    # -------------------------------------------------- regras entre linhas
    def _duplicates(self, records: list[dict[str, Any]]) -> None:
        seen: dict[tuple[Any, ...], dict[str, Any]] = {}
        for rec in records:
            key = (rec["edition_id"], rec["edition_year"], rec["table_id"], rec["source_sheet"],
                   rec["territory_code"] or rec["territory_label_original"],
                   *(rec[d] for d in DIMS), rec["category_group"], rec["response_category"], rec["unit"])
            self.checks["VAL011"] += 1
            if key in seen:
                first = seen[key]
                self._add("VAL011", Severity.ERROR, IssueClass.CONFIRMED_ERROR,
                          f"Chave analítica duplicada na mesma aba (primeira ocorrência {first['source_cell']})", rec,
                          "Verificar rótulos repetidos ou erro de interpretação do cabeçalho.")
            else:
                seen[key] = rec

    def _cross_table(self, records: list[dict[str, Any]]) -> None:
        """Mesmo indicador publicado em mais de uma tabela (ex.: Brasil em 17.1.1 e 17.1.2).

        Os valores devem ser idênticos. A primeira ocorrência (ordem de tabela)
        vira a observação canônica; as demais recebem ``analytical_duplicate_of``.
        """
        groups: dict[tuple[Any, ...], list[dict[str, Any]]] = defaultdict(list)
        for rec in records:
            if not rec["territory_code"]:
                continue
            key = (rec["indicator_id"], rec["edition_year"], rec["territory_code"], *(rec[d] for d in DIMS),
                   rec["category_group"], rec["response_category"], rec["unit"])
            groups[key].append(rec)
        for recs in groups.values():
            recs.sort(key=lambda r: (_table_order(r["table_id"]), r["source_sheet"], r["source_row"]))
            canon = recs[0]
            canon["analytical_duplicate_of"] = ""
            for other in recs[1:]:
                self.checks["VAL020"] += 1
                other["analytical_duplicate_of"] = canon["observation_id"]
                a, b = canon.get("estimate"), other.get("estimate")
                if a is None and b is None:
                    continue
                if a is None or b is None or abs(a - b) > self.s.float_tol * max(1, abs(a)):
                    self._add("VAL020", Severity.ERROR, IssueClass.CONFIRMED_ERROR,
                              f"Mesmo recorte publicado com valores diferentes em {canon['table_id']} ({a}) e "
                              f"{other['table_id']} ({b})", other, "Conferir as duas tabelas na publicação.",
                              observed=f"{a} vs {b}")

    def _distribution_sums(self, records: list[dict[str, Any]]) -> None:
        groups: dict[tuple[Any, ...], list[dict[str, Any]]] = defaultdict(list)
        for rec in records:
            if rec["estimate_type"] != "distribuicao_percentual" or rec.get("multi_response"):
                continue
            key = (rec["source_file"], rec["source_sheet"], rec["source_row"], rec["edition_year"], rec["category_group"],
                   *(rec[d] for d in ("sex", "admin_dependency")))
            groups[key].append(rec)
        for recs in groups.values():
            vals = [r["estimate"] for r in recs]
            if len(recs) < 2 or any(v is None for v in vals):
                continue
            total = sum(vals)
            first = recs[0]
            self.checks["VAL014"] += 1
            cats = ", ".join(r["response_category"] for r in recs)
            if total > 100 + self.s.dist_sum_tol:
                for r in recs:
                    self._add("VAL014", Severity.ERROR, IssueClass.CONFIRMED_ERROR,
                              f"Categorias de distribuição somam {total:.2f}% (> 100%): {cats}", r,
                              "Verificar se a questão admite múltiplas respostas ou se há colunas duplicadas.",
                              observed=total)
            elif total < 100 - self.s.dist_sum_tol:
                if first.get("nonresponse_excluded"):
                    # Explicado pela nota da tabela: registro informativo da linha, sem afetar o status.
                    self._add("VAL014", Severity.INFO, IssueClass.INFORMATIONAL,
                              f"Categorias somam {total:.2f}%; a nota informa que não-respostas não são "
                              f"apresentadas — a diferença ({100 - total:.2f} p.p.) corresponde a elas", first,
                              "Nenhuma: exibir a nota junto à distribuição; não redistribuir.", observed=total)
                else:
                    for r in recs:
                        self._add("VAL014", Severity.WARNING, IssueClass.POSSIBLE_ANOMALY,
                                  f"Categorias de distribuição somam {total:.2f}% (< 100%) sem nota explicativa", r,
                                  "Verificar categorias omitidas; não redistribuir proporcionalmente.", observed=total)

    def _partition_bounds(self, records: list[dict[str, Any]]) -> None:
        """O total de uma partição completa é média ponderada das partes: deve ficar entre o mínimo e o máximo."""
        pct = [r for r in records if r["unit"] == "%" and r.get("estimate") is not None]
        partitions = {"sex": {"Homem", "Mulher"}, "admin_dependency": {"Pública", "Privada"},
                      "age_group": {"13 a 15 anos", "16 e 17 anos"}}
        for dim, parts in partitions.items():
            groups: dict[tuple[Any, ...], dict[str, dict[str, Any]]] = defaultdict(dict)
            for r in pct:
                key = (r["source_file"], r["source_sheet"], r["edition_year"],
                       r["territory_code"] or r["territory_label_original"],
                       r["category_group"], r["response_category"], *(r[d] for d in DIMS if d != dim))
                groups[key][r[dim]] = r
            for members in groups.values():
                if "Total" in members and parts <= set(members):
                    self._check_bound(members["Total"], [members[p] for p in parts], f"partição '{dim}'")
        # territorial: Brasil x regiões; região x UFs; capitais x conjunto
        by_sheet: dict[tuple[Any, ...], list[dict[str, Any]]] = defaultdict(list)
        for r in pct:
            by_sheet[(r["source_file"], r["source_sheet"], r["source_column"], r["row_group_label"])].append(r)
        for recs in by_sheet.values():
            regions = [r for r in recs if r["territory_type"] == "region"]
            br = [r for r in recs if r["territory_type"] == "country"]
            if br and len(regions) == 5:
                self._check_bound(br[0], regions, "Brasil × Grandes Regiões")
            for reg in regions:
                ufs = [r for r in recs if r["territory_type"] == "uf" and r["region_code"] == reg["territory_code"]]
                if len(ufs) >= 3:
                    self._check_bound(reg, ufs, f"{reg['territory_name']} × UFs")
            agg = [r for r in recs if r["territory_code"] == "CAPITAIS"]
            caps = [r for r in recs if r["territory_type"] == "capital"]
            if agg and len(caps) >= 20:
                self._check_bound(agg[0], caps, "Conjunto das capitais × capitais")

    def _check_bound(self, total: dict[str, Any], parts: list[dict[str, Any]], label: str) -> None:
        vals = [p["estimate"] for p in parts if p.get("estimate") is not None]
        if len(vals) < 2:
            return
        self.checks["VAL015"] += 1
        t = total["estimate"]
        tol = 1e-6 * max(1.0, abs(t))
        if t < min(vals) - tol or t > max(vals) + tol:
            self._add("VAL015", Severity.WARNING, IssueClass.POSSIBLE_ANOMALY,
                      f"Total ({t:.4f}) fora do intervalo das partes [{min(vals):.4f}, {max(vals):.4f}] na {label}",
                      total, "Verificar denominadores (ex.: categoria 'sem declaração' não publicada) ou erro de extração.",
                      observed=t)

    def _count_additivity(self, records: list[dict[str, Any]]) -> None:
        cnt = [r for r in records if r["unit"] == "escolares"]
        groups: dict[tuple[Any, ...], dict[str, dict[str, Any]]] = defaultdict(dict)
        for r in cnt:
            groups[(r["source_file"], r["source_sheet"], r["source_row"], r["sex"], r["age_group"])][r["admin_dependency"]] = r
        for members in groups.values():
            if not {"Total", "Pública", "Privada"} <= set(members):
                continue
            tot, pub, pri = members["Total"], members["Pública"], members["Privada"]
            if tot.get("estimate") is None or pub.get("estimate") is None:
                continue
            if pri.get("estimate") is None:
                if pri.get("estimate_kind") == "symbol":
                    if abs(tot["estimate"] - pub["estimate"]) > self.s.count_rel_tol * tot["estimate"]:
                        self._add("VAL019", Severity.WARNING, IssueClass.POSSIBLE_ANOMALY,
                                  "Privada publicada como símbolo, mas Total ≠ Pública", tot,
                                  "Conferir o significado do símbolo nesta tabela.")
                continue
            soma = pub["estimate"] + pri["estimate"]
            self.checks["VAL019"] += 1
            if abs(soma - tot["estimate"]) > self.s.count_rel_tol * max(1, tot["estimate"]):
                self._add("VAL019", Severity.WARNING, IssueClass.POSSIBLE_ANOMALY,
                          f"Total ({tot['estimate']:.1f}) ≠ Pública + Privada ({soma:.1f})", tot,
                          "Conferir arredondamentos e categorias não publicadas.", observed=tot["estimate"])

    def _outliers(self, records: list[dict[str, Any]]) -> None:
        """Valores incomuns entre territórios do mesmo tipo (mediana/MAD).

        Não é teste de significância e não implica erro: serve para revisão.
        """
        groups: dict[tuple[Any, ...], list[dict[str, Any]]] = defaultdict(list)
        for r in records:
            if r.get("estimate") is None or r["territory_type"] not in ("uf", "capital") or r["unit"] != "%":
                continue  # contagens refletem o tamanho da população; não faz sentido buscar extremos
            if r.get("analytical_duplicate_of"):
                continue
            key = (r["indicator_id"], r["edition_year"], r["territory_type"], r["category_group"],
                   r["response_category"], *(r[d] for d in DIMS), r["unit"])
            groups[key].append(r)
        for recs in groups.values():
            if len(recs) < self.s.min_group:
                continue
            vals = [r["estimate"] for r in recs]
            med = statistics.median(vals)
            mad = statistics.median([abs(v - med) for v in vals])
            if mad == 0:
                continue
            for r in recs:
                self.checks["OUT001"] += 1
                z = 0.6745 * (r["estimate"] - med) / mad
                if abs(z) > self.s.robust_z:
                    cv = r.get("coefficient_of_variation")
                    cvtxt = f"; CV {cv:.1f}%" if cv is not None else ""
                    self._add("OUT001", Severity.INFO, IssueClass.LEGIT_EXTREME,
                              f"Valor incomum entre {len(recs)} territórios (z robusto {z:+.1f}; mediana {med:.2f}{cvtxt})",
                              r, "Revisar contexto; manter o valor — extremos podem ser legítimos.", observed=r["estimate"])

    # ------------------------------------------------------------- suporte
    def _add(self, rule: str, sev: Severity, cls: IssueClass, msg: str, rec: dict[str, Any], action: str,
             observed: Any = None, cell: str | None = None) -> None:
        self.issues.append(Issue(
            rule_id=rule, severity=sev.value, issue_class=cls.value, message=msg, recommended_action=action,
            source_file=rec.get("source_file", ""), source_sheet=rec.get("source_sheet", ""),
            source_cell=cell or rec.get("source_cell", ""), observation_id=rec.get("observation_id", ""),
            table_id=rec.get("table_id", ""),
            observed_value="" if observed is None and rec.get("estimate") is None else str(observed if observed is not None else rec.get("estimate")),
            context=f"{rec.get('indicator_id')} | {rec.get('territory_name') or rec.get('territory_label_original')} | "
                    f"{rec.get('age_group')}/{rec.get('sex')}/{rec.get('admin_dependency')} | {rec.get('response_category')}",
            stage="validation"))


def _table_order(table_id: str) -> tuple[int, ...]:
    try:
        return tuple(int(p) for p in table_id.split("."))
    except ValueError:
        return (9999,)


SEVERITY_RANK = {"ERROR": 4, "REVIEW": 3, "WARNING": 2, "INFO": 1}


def assign_status(records: list[dict[str, Any]], issues: Iterable[Issue]) -> None:
    by_obs: dict[str, list[Issue]] = defaultdict(list)
    for iss in issues:
        if iss.observation_id:
            by_obs[iss.observation_id].append(iss)
    for rec in records:
        its = by_obs.get(rec["observation_id"], [])
        worst = max((SEVERITY_RANK[i.severity] for i in its), default=0)
        if worst == 4:
            status = ValidationStatus.ERROR
        elif worst == 3:
            status = ValidationStatus.REVIEW_REQUIRED
        elif rec.get("estimate") is None:
            status = ValidationStatus.NOT_AVAILABLE
        elif worst == 2:
            status = ValidationStatus.VALID_WITH_WARNINGS
        else:
            status = ValidationStatus.VALID
        rec["validation_status"] = status.value
        rec["issue_rules"] = "|".join(sorted({i.rule_id for i in its}))
        rec["approved_for_analysis"] = status.value in APPROVABLE and rec.get("estimate") is not None

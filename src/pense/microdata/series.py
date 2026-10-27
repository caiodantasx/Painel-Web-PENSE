"""Série histórica a partir das estimativas calculadas com os microdados.

Por que os microdados permitem o que as tabelas publicadas não permitiam:
* o MESMO indicador (mesma variável, mesmos códigos de numerador e denominador, mesmo
  universo) é calculado em todas as edições, na MESMA convenção de não resposta (a da série
  harmonizada do IBGE: "sem resposta" entra no denominador, "abandono" sai — D21);
* cada ponto tem erro-padrão de desenho; como as edições são amostras independentes, a
  diferença entre dois anos tem EP = √(EP₁² + EP₂²).

Governança (D23):
* Evidência por edição: DIRETA (o cálculo reproduz uma tabela publicada da edição), INDIRETA
  (declarada em ``indirect_validation``: indicadores com a mesma variável e o mesmo denominador
  reproduzem tabelas da edição), FALHOU (não reproduz) ou AUSENTE.
* Só edições com evidência DIRETA ou INDIRETA entram na série; os pontos das demais são
  mantidos em microdata_estimates.csv, nunca apagados.
* ``proposed_status`` é sempre uma PROPOSTA AUTOMÁTICA. ``final_status`` só difere dela quando há
  decisão completa (status, justificativa, evidência, responsável e data) em
  config/microdata/comparability_decisions.csv; ``decision_status`` diz qual é o caso.
* O selo "Diferença significativa a 5%" (``SIGNIFICATIVA_5PCT_COM_DECISAO``, D27) exige: decisão
  registrada aprovando a comparação, evidência nas duas edições e diferença significativa a 5%
  (|d| > 1,96·EP da diferença, isto é, IC 95% da diferença sem o zero). Sem decisão, a diferença
  significativa aparece como "significativa — aguardando decisão do pesquisador". O critério
  estatístico é o mesmo do rótulo anterior (histórico em docs/04, D27); só o nome mudou, porque
  significância não confirma mudança real, relevância prática nem causa.
"""
from __future__ import annotations

import math
from collections import defaultdict
from datetime import date
from typing import Any

Z95 = 1.959963984540054
KEY_DIMS = ("territory_code", "age_group", "sex", "admin_dependency")
APPROVED = ("COMPARABLE", "COMPARABLE_WITH_CAVEATS")
DECISION_FIELDS = ("indicator_key", "final_status", "justification", "evidence_reference", "reviewer", "decision_date")
CHANGE_SIGNIFICANT = "SIGNIFICATIVA_5PCT_COM_DECISAO"
CHANGE_PENDING = "SIGNIFICATIVA_SEM_DECISAO"
CHANGE_NS = "NAO_SIGNIFICATIVA"
EXCLUSION_FIELDS = ("indicator_key", "edition_id", "reason", "evidence_reference", "reviewer", "decision_date")


class SeriesExclusionError(ValueError):
    """Exclusão de edição incompleta ou inconsistente: a pipeline para em vez de decidir sozinha."""


def check_exclusion_header(fieldnames: list[str] | None) -> None:
    """O arquivo de exclusões precisa ter exatamente o esquema documentado (nem a mais, nem a menos)."""
    if fieldnames is not None and tuple(f.strip() for f in fieldnames) != EXCLUSION_FIELDS:
        raise SeriesExclusionError(f"config/microdata/series_exclusions.csv: cabeçalho {fieldnames!r} difere do esquema "
                                   f"{list(EXCLUSION_FIELDS)}")


def _bad_date(value: str, today: date) -> str | None:
    """Data da decisão: AAAA-MM-DD, existente no calendário e não posterior ao dia da execução."""
    try:
        d = date.fromisoformat(value)
    except ValueError:
        return f"data inválida {value!r} (use AAAA-MM-DD)"
    if len(value) != 10:
        return f"data inválida {value!r} (use AAAA-MM-DD)"
    if d > today:
        return f"data futura {value!r}: decisão não pode ser registrada com data antecipada"
    return None


def load_exclusions(rows: list[dict], indicators: dict[str, dict], editions: dict[str, dict],
                    today: date | None = None) -> dict[str, dict[str, dict]]:
    """Exclusões de edição da série principal, registradas pelo pesquisador (D26).

    Arquivo: config/microdata/series_exclusions.csv — uma linha por indicador × edição, com motivo,
    evidência, responsável e data. Regras:
    * sem linha, nenhuma edição é excluída (o padrão é incluir tudo que tem evidência);
    * linha com campo vazio, indicador ou edição inexistentes, edição que o indicador não tem,
      data inválida ou futura, ou linha duplicada → SeriesExclusionError (nada é excluído nem
      ignorado em silêncio);
    * só este arquivo exclui: texto livre em justificativas (ex.: comparability_decisions.csv)
      nunca retira edição da série;
    * a exclusão só tira a edição da SÉRIE PRINCIPAL; as estimativas continuam em
      microdata_estimates.csv e no painel, marcadas como "fora da série principal".
    """
    today = today or date.today()
    out: dict[str, dict[str, dict]] = {}
    problems = []
    for i, r in enumerate(rows, start=2):
        if not any((v or "").strip() for v in r.values() if isinstance(v, str)):
            continue
        missing = [f for f in EXCLUSION_FIELDS if not (r.get(f) or "").strip()]
        k, e = (r.get("indicator_key") or "").strip(), (r.get("edition_id") or "").strip()
        if missing:
            problems.append(f"linha {i}: campos vazios {missing}")
        elif k not in indicators:
            problems.append(f"linha {i}: indicador desconhecido {k!r}")
        elif e not in editions:
            problems.append(f"linha {i}: edição desconhecida {e!r}")
        elif e not in indicators[k]["editions"]:
            problems.append(f"linha {i}: edição {e!r} não pertence ao indicador {k}")
        elif (why := _bad_date(r["decision_date"].strip(), today)):
            problems.append(f"linha {i}: {why}")
        elif e in out.get(k, {}):
            problems.append(f"linha {i}: exclusão duplicada {k} × {e}")
        else:
            out.setdefault(k, {})[e] = {f: r[f].strip() for f in EXCLUSION_FIELDS}
    if problems:
        raise SeriesExclusionError("config/microdata/series_exclusions.csv inválido: " + "; ".join(problems))
    return out


def _f(v: Any) -> float | None:
    try:
        x = float(v)
        return None if math.isnan(x) else x
    except (TypeError, ValueError):
        return None


def valid_decisions(decisions: list[dict]) -> tuple[dict[str, dict], list[str]]:
    """Só vale decisão completa; as incompletas são ignoradas e listadas (nunca aprovam nada)."""
    ok, bad = {}, []
    for d in decisions:
        if not (d.get("indicator_key") or "").strip():
            continue
        missing = [f for f in DECISION_FIELDS if not (d.get(f) or "").strip()]
        if missing or d["final_status"] not in ("COMPARABLE", "COMPARABLE_WITH_CAVEATS", "NOT_COMPARABLE", "PENDING_REVIEW"):
            bad.append(f"{d.get('indicator_key')}: decisão incompleta ou status inválido ({', '.join(missing) or d['final_status']})")
            continue
        ok[d["indicator_key"]] = d
    return ok, bad


def edition_evidence(ind: dict, key: str, editions: dict[str, dict], val: dict[tuple, dict]) -> dict[str, str]:
    out = {}
    for e in ind["editions"]:
        if e not in editions:
            continue
        st = val.get((e, key), {}).get("status", "")
        if st.startswith("VALIDADO"):
            out[e] = "DIRETA"
        elif st == "NAO_VALIDADO":
            out[e] = "FALHOU"
        else:
            via = ind.get("indirect_validation", {}).get(e, [])
            out[e] = "INDIRETA" if via and all(val.get((e, k), {}).get("status", "").startswith("VALIDADO") for k in via) else "AUSENTE"
    return out


def assess_comparability(indicators: dict[str, dict], editions: dict[str, dict],
                         validation_summary: list[dict], decisions: list[dict],
                         questions: dict[str, dict[str, str]] | None = None,
                         effects: list[dict] | None = None,
                         exclusions: dict[str, dict[str, dict]] | None = None) -> list[dict[str, Any]]:
    """Proposta de comparabilidade por indicador, com evidências e ressalvas explícitas.

    Regras da PROPOSTA (nunca equivale a decisão):
    * fora da série por configuração (``series_exclude``) → PENDING_REVIEW;
    * cálculo não reproduz a tabela publicada em alguma edição → PENDING_REVIEW;
    * menos de duas edições com evidência → PENDING_REVIEW (edições sem evidência ficam fora);
    * código da variável muda e a redação muda → NOT_COMPARABLE; só um dos dois, ou redação com
      mais de 3 palavras alteradas → PENDING_REVIEW;
    * demais casos → COMPARABLE_WITH_CAVEATS (proposta), com as ressalvas registradas.

    ``exclusions`` (de ``load_exclusions``): edições retiradas da série principal por decisão
    registrada. A avaliação passa a valer só para as edições restantes; a exclusão aparece em
    ``excluded_editions`` e nas ressalvas, com motivo, responsável e data.
    """
    from .dictionary import compare

    questions = questions or {}
    val = {(r["edition_id"], r["indicator_key"]): r for r in validation_summary}
    dec, _ = valid_decisions(decisions)
    eff = {(r["indicator_key"], r["edition_id"]): r for r in (effects or [])}
    out = []
    for key, ind in indicators.items():
        eds_all = [e for e in ind["editions"] if e in editions]
        evid = edition_evidence(ind, key, editions, val)
        excl = (exclusions or {}).get(key, {})
        eds = [e for e in eds_all if evid.get(e) in ("DIRETA", "INDIRETA") and e not in excl]
        year = lambda e: str(editions[e]["year"])  # noqa: E731
        evidence, caveats = [], []
        qtext = {year(e): questions.get(key, {}).get(e, "") for e in eds_all}
        wording = compare({year(e): qtext[year(e)] for e in eds}) if sum(1 for e in eds if qtext[year(e)]) >= 2 else None
        wording_all = compare(qtext) if sum(1 for t in qtext.values() if t) >= 2 else None
        excluded = [e for e in eds_all if e not in eds and e not in excl]
        for e, x in excl.items():
            caveats.append(f"{year(e)} fora da série principal por decisão registrada ({x['reviewer']}, {x['decision_date']}): "
                           f"{x['reason']} — evidência: {x['evidence_reference']}; os valores de {year(e)} continuam "
                           f"disponíveis para consulta separada")
        if excluded:
            caveats.append("fora da série por falta de evidência: " + ", ".join(
                f"{year(e)} ({'cálculo não reproduz a tabela publicada' if evid[e] == 'FALHOU' else 'sem tabela publicada para conferir'})"
                for e in excluded))
        same_var = "var_by_edition" not in ind
        if not same_var and wording_all and not wording_all["identical"]:
            status = "NOT_COMPARABLE"   # código e redação mudaram: decide mesmo sem validação
            caveats.append(f"variável muda entre edições ({ind['var_by_edition']}); sufixo novo indica pergunta alterada")
            caveats.append("redação difere nos dicionários: " + " | ".join(wording_all["changes"]))
        elif ind.get("series_exclude"):
            status = "PENDING_REVIEW"
            caveats.insert(0, ind["series_exclude"])
        elif any(evid.get(e) == "FALHOU" for e in eds_all):
            status = "PENDING_REVIEW"
        elif len(eds) < 2:
            status = "PENDING_REVIEW" if len(eds_all) >= 2 else "NOT_COMPARABLE"
            evidence.append("menos de duas edições com evidência" if len(eds_all) >= 2 else "variável disponível em uma só edição")
        else:
            status = None
        if len(eds) >= 2:
            years = ", ".join(year(e) for e in eds)
            if same_var:
                var = "+".join(c["var"] for c in ind["any"]) if "any" in ind else ind["var"]
                evidence.append(f"mesma variável ({var}) e mesmos códigos de numerador e denominador nas edições {years}")
            elif status != "NOT_COMPARABLE":
                caveats.append(f"variável muda entre edições ({ind['var_by_edition']}); sufixo novo indica pergunta alterada")
            if wording and wording["identical"]:
                evidence.append(f"redação idêntica nos dicionários do IBGE ({', '.join(year(e) for e in eds if qtext[year(e)])})")
            elif wording and status != "NOT_COMPARABLE":
                caveats.append("redação difere nos dicionários: " + " | ".join(wording["changes"]))
            pop = "9º ano do ensino fundamental (todas as idades)" if ind.get("population") == "9ANO" else "13 a 17 anos"
            evidence.append(f"mesmo universo em todas as edições: escolares de {pop}")
            direct = [year(e) for e in eds if evid[e] == "DIRETA"]
            indirect = [year(e) for e in eds if evid[e] == "INDIRETA"]
            if direct:
                evidence.append("cálculo reproduz a tabela publicada em " + ", ".join(direct))
            if indirect:
                caveats.append("validação indireta em " + ", ".join(indirect) + " (sem tabela publicada para este universo, "
                               "mas a mesma variável reproduz as tabelas da edição): valor calculado, não oficial")
            evidence.append("não resposta harmonizada em todas as edições: sem resposta no denominador e abandono fora "
                            "(IBGE 2022, p. 18, nota 7)")
            effs = [(year(e), eff[(key, e)]["efeito_harmonizacao_pp"]) for e in eds
                    if (key, e) in eff and eff[(key, e)].get("efeito_harmonizacao_pp") not in (None, "", 0, 0.0, "0.0")]
            if effs:
                caveats.append("efeito medido da harmonização sobre o valor da publicação (total): "
                               + ", ".join(f"{y}: {float(v):+.2f} p.p.".replace(".", ",", 1) for y, v in effs))
            for e in eds:
                pol = (editions[e].get("validation") or {}).get("reason")
                if pol and val.get((e, key), {}).get("status") == "VALIDADO_COM_RESSALVA":
                    caveats.append(f"{year(e)}: {pol}")
            if any(e.endswith("_A2") for e in eds):
                caveats.append("2015 (Amostra 2) só representa Brasil e Grandes Regiões; desenhos amostrais diferem entre edições")
            if status is None:
                if not same_var and wording and not wording["identical"]:
                    status = "NOT_COMPARABLE"
                elif not same_var or (wording and wording["max_changed"] > 3):
                    status = "PENDING_REVIEW"
                else:
                    status = "COMPARABLE_WITH_CAVEATS"
        if any(evid.get(e) == "FALHOU" for e in eds_all):
            caveats.append("cálculo NÃO reproduz a tabela publicada em " + ", ".join(year(e) for e in eds_all if evid[e] == "FALHOU"))
        if ind.get("definition_note"):
            caveats.append(ind["definition_note"])
        d = dec.get(key)
        out.append({
            "indicator_key": key, "label": ind["label"], "period_code": ind["period"],
            "population": "9ANO" if ind.get("population") == "9ANO" else "13_17",
            "editions": "|".join(eds_all), "series_editions": "|".join(eds),
            "evidence_by_edition": "; ".join(f"{year(e)}: {evid[e]}" + (" (EXCLUÍDA POR DECISÃO)" if e in excl else "")
                                             for e in eds_all),
            "excluded_edition_ids": "|".join(excl),
            "excluded_editions": " | ".join(f"{e}: {x['reason']} ({x['reviewer']}, {x['decision_date']})" for e, x in excl.items()),
            "proposed_status": status,
            "final_status": d["final_status"] if d else status,
            "decision_status": "DECISAO_REGISTRADA" if d else "PROPOSTA_AUTOMATICA",
            "decision_source": (f"decisão registrada ({d['reviewer']}, {d['decision_date']}; evidência: {d['evidence_reference']})"
                                if d else "proposta automática por evidência documental — aguardando decisão do pesquisador"),
            "justification": d["justification"] if d else "; ".join(evidence),
            "caveats": "; ".join(caveats),
            "questions": " || ".join(f"{y}: {t}" for y, t in qtext.items() if t),
        })
    return out


def change_status(significant: bool, decided: bool) -> str:
    if not significant:
        return CHANGE_NS
    return CHANGE_SIGNIFICANT if decided else CHANGE_PENDING


def series_estimates(estimates: list[dict]) -> list[dict]:
    """Estimativas na convenção da série (as de 2019/2024 valem para as duas convenções)."""
    return [e for e in estimates if "SERIE" in e.get("nonresponse_convention", "PUBLICACAO+SERIE").split("+")]


def build_series(estimates: list[dict], comparability: list[dict]) -> list[dict[str, Any]]:
    """Pontos da série (só edições com evidência) para indicadores com comparação proposta ou aprovada.

    A diferença entre anos é sempre calculada (fato estatístico); ``change_status`` diz se ela pode
    receber o selo "Diferença significativa a 5%" (decisão registrada) ou não.
    """
    ok = {c["indicator_key"]: c for c in comparability if c["final_status"] in APPROVED}
    groups: dict[tuple, list[dict]] = defaultdict(list)
    for e in series_estimates(estimates):
        c = ok.get(e["indicator_key"])
        if c and e["edition_id"] in c["series_editions"].split("|"):
            groups[(e["indicator_key"],) + tuple(e[k] for k in KEY_DIMS)].append(e)
    out = []
    for key, pts in groups.items():
        pts = sorted(pts, key=lambda r: int(r["edition_year"]))
        if len(pts) < 2:
            continue
        c = ok[key[0]]
        decided = c["decision_status"] == "DECISAO_REGISTRADA"
        prev = None
        for p in pts:
            est, se = _f(p["estimate"]), _f(p["standard_error"])
            row = {"indicator_key": key[0], "territory_code": p["territory_code"], "territory_name": p["territory_name"],
                   "territory_type": p["territory_type"], "age_group": p["age_group"], "sex": p["sex"],
                   "admin_dependency": p["admin_dependency"], "edition_id": p["edition_id"], "year": int(p["edition_year"]),
                   "estimate": est, "ci_lower": _f(p["ci_lower"]), "ci_upper": _f(p["ci_upper"]), "standard_error": se,
                   "low_precision": p["low_precision"], "comparability_status": c["final_status"],
                   "decision_status": c["decision_status"],
                   "previous_year": "", "diff_pp": "", "diff_ci_lower": "", "diff_ci_upper": "", "significant_5pct": "",
                   "change_status": ""}
            if prev and est is not None and prev["estimate"] is not None and se is not None and prev["standard_error"] is not None:
                d = est - prev["estimate"]
                sd = math.sqrt(se ** 2 + prev["standard_error"] ** 2)
                sig = bool(abs(d) > Z95 * sd)
                row.update(previous_year=prev["year"], diff_pp=round(d, 4), diff_ci_lower=round(d - Z95 * sd, 4),
                           diff_ci_upper=round(d + Z95 * sd, 4), significant_5pct=sig, change_status=change_status(sig, decided))
            out.append(row)
            prev = row
    return out

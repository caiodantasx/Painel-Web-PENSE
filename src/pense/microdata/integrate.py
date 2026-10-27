"""Liga as estimativas dos microdados à pipeline principal (sem reler os microdados).

``scripts/run_microdata.py`` grava data/curated/microdata_estimates.csv e o resumo da
validação. Aqui eles são lidos, a comparabilidade é avaliada, a série é montada e uma
versão compacta vai para o pacote do painel. Se os arquivos não existirem, nada muda.
"""
from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from ..config import Config
from .run import load_config
from .series import (CHANGE_NS, CHANGE_PENDING, CHANGE_SIGNIFICANT, assess_comparability, build_series,
                     check_exclusion_header, load_exclusions, series_estimates, valid_decisions)


def _read(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def read_exclusions(path: Path, indicators: dict[str, dict], editions: dict[str, dict]) -> dict[str, dict[str, dict]]:
    """Lê config/microdata/series_exclusions.csv (D26). Arquivo ausente ou só com cabeçalho: nada é excluído."""
    if not path.exists():
        return {}
    with path.open(encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        check_exclusion_header(reader.fieldnames)
        rows = list(reader)
    return load_exclusions(rows, indicators, editions)


def _num(v: str) -> float | None:
    try:
        return round(float(v), 4)
    except (TypeError, ValueError):
        return None


def question_texts(cfg: Config, indicators: dict[str, dict], editions: dict[str, dict]) -> dict[str, dict[str, str]]:
    """Texto da pergunta por indicador e edição, tirado dos dicionários do IBGE (vazio se ausente)."""
    from .dictionary import lookup
    from .run import _conditions

    out: dict[str, dict[str, str]] = {}
    for key, ind in indicators.items():
        for e in ind["editions"]:
            if e not in editions:
                continue
            texts = []
            for c in _conditions(ind, e):
                d = lookup(cfg.config_dir, e, c["var"], editions[e].get("var_prefix", ""))
                if d:
                    texts.append(d["description"])
            out.setdefault(key, {})[e] = " / ".join(texts)
    return out


def load_microdata_outputs(cfg: Config, published: list[dict] | None = None) -> dict[str, Any]:
    curated = cfg.path("curated")
    estimates = _read(curated / "microdata_estimates.csv")
    if not estimates:
        return {}
    editions, indicators = load_config(cfg)
    summary = _read(curated / "microdata_validation_summary.csv")
    effects = _read(curated / "microdata_nonresponse_effect.csv")
    decisions = _read(cfg.config_dir / "microdata" / "comparability_decisions.csv")
    _, bad_decisions = valid_decisions(decisions)
    exclusions = read_exclusions(cfg.config_dir / "microdata" / "series_exclusions.csv", indicators, editions)
    comp = assess_comparability(indicators, editions, summary, decisions, question_texts(cfg, indicators, editions), effects,
                                exclusions)
    series = build_series(estimates, comp)
    ser_est = series_estimates(estimates)
    pub_values = {(e["indicator_key"], e["edition_id"], e["territory_code"], e["age_group"], e["sex"], e["admin_dependency"]): e
                  for e in estimates if e.get("nonresponse_convention") == "PUBLICACAO"}
    bundle = _bundle(ser_est, comp, series, editions, indicators, summary, pub_values)
    if published:
        bundle["official"] = official_series(published, ser_est, comp, indicators, summary)
    return {"estimates": estimates, "comparability": comp, "series": series, "bundle": bundle,
            "decision_template": decision_template(comp), "invalid_decisions": bad_decisions}


def decision_template(comp: list[dict]) -> list[dict]:
    """Modelo para o pesquisador (NÃO é lido como decisão): copiar as linhas aprovadas, preencher
    responsável e data e colar em config/microdata/comparability_decisions.csv."""
    return [{"indicator_key": c["indicator_key"], "proposed_status": c["proposed_status"],
             "final_status": "", "justification": "", "evidence_reference": "", "reviewer": "", "decision_date": "",
             "series_editions": c["series_editions"], "evidence_by_edition": c["evidence_by_edition"],
             "proposal_justification": c["justification"] if c["decision_status"] == "PROPOSTA_AUTOMATICA" else "",
             "caveats": c["caveats"]} for c in comp]


def official_series(published: list[dict], estimates: list[dict], comp: list[dict], indicators: dict[str, dict],
                    summary: list[dict]) -> dict[str, Any]:
    """Série oficial do 9º ano nas capitais (IBGE, 2009–2019) + extensão 2024 pelos microdados.

    Os pontos publicados mantêm célula de origem. O ponto de 2024 entra só para indicadores
    cuja regra reproduz a tabela oficial em 2019 e cuja comparação 2019→2024 foi aprovada.
    """
    import math

    Z = 1.959963984540054
    pub = [r for r in published if r["edition_id"] == "PENSE_SERIE_9ANO_CAPITAIS" and r.get("estimate") is not None
           and r.get("validation_status") in ("VALID", "VALID_WITH_WARNINGS")]
    if not pub:
        return {}
    fam_to_key = {}
    for k, ind in indicators.items():
        for ref in ind.get("published", {}).values():
            if ref.startswith("PENSE_SERIE_9ANO_CAPITAIS@"):
                fam_to_key[ref.split("@")[1]] = k
    ok_val = {(s["edition_id"], s["indicator_key"]) for s in summary if s["status"].startswith("VALIDADO")}
    comp_by = {c["indicator_key"]: c for c in comp}
    terr = sorted({(r["territory_code"], r["territory_name"]) for r in pub})
    t_idx = {c: i for i, (c, _) in enumerate(terr)}
    sexes, deps = ["Total", "Homem", "Mulher"], ["Total", "Pública", "Privada"]
    tables, cols = [], {k: [] for k in ("f", "t", "s", "d", "y", "e", "lo", "hi", "o", "src")}
    pts_by = {}
    fams = sorted({r["table_family_id"] for r in pub}, key=lambda f: [int(x) for x in f.split(".")])
    for fi, fam in enumerate(fams):
        rows = [r for r in pub if r["table_family_id"] == fam]
        key = fam_to_key.get(fam, "")
        c = comp_by.get(key, {})
        ext = (bool(key) and ("PENSE_2019", key) in ok_val and c.get("final_status", "").startswith("COMPARABLE")
               and "PENSE_2024" in c.get("series_editions", "").split("|"))
        title = rows[0]["indicator_definition"].split(", por sexo")[0].replace("Percentual de escolares do 9º ano do Ensino Fundamental", "").strip(" ,")
        excl_2024 = "PENSE_2024" in (c.get("excluded_edition_ids") or "").split("|")
        if ext:
            note = ("2024 calculado com os microdados (não oficial): a mesma regra reproduz a tabela "
                    "oficial de 2019 e as mesmas variáveis reproduzem as tabelas de 2024")
        elif excl_2024:   # a regra reproduz 2019, mas 2024 saiu da série por decisão registrada (D29)
            note = ("2024 fora desta série por decisão registrada (sem tabela oficial do 9º ano para validar); "
                    "o valor calculado continua na aba de microdados, marcado como fora da série principal")
        elif key:
            note = "regra da tabela oficial não reproduzida pelos microdados"
        else:
            note = "pergunta mudou em 2019; série termina na última edição publicada"
        tables.append({"family": fam, "title": title[:1].upper() + title[1:], "indicator_key": key,
                       "years": sorted({int(r["edition_year"]) for r in rows}) + ([2024] if ext else []),
                       "extension_2024": ext,
                       "decision_status": c.get("decision_status", ""),
                       "extension_note": note,
                       "comparability_2024": comp_by.get(key, {}).get("final_status", "") if key else ""})
        for r in rows:
            if r["sex"] not in sexes or r["admin_dependency"] not in deps or r["age_group"] != "Total":
                continue
            _add(cols, fi, t_idx[r["territory_code"]], sexes.index(r["sex"]), deps.index(r["admin_dependency"]),
                 int(r["edition_year"]), r["estimate"], r.get("ci_lower"), r.get("ci_upper"), "P",
                 f"{r['source_file'].split('!')[-1]} › {r['source_sheet']} › {r['source_cell']}")
            pts_by[(fi, r["territory_code"], r["sex"], r["admin_dependency"], int(r["edition_year"]))] = (
                r["estimate"], r.get("ci_lower"), r.get("ci_upper"), None)
        if ext:
            for e in estimates:
                if e["indicator_key"] != key or e["territory_code"] not in t_idx or e["age_group"] != "Total":
                    continue
                if e["sex"] not in sexes or e["admin_dependency"] not in deps:
                    continue
                y = int(e["edition_year"])
                if y == 2024:
                    _add(cols, fi, t_idx[e["territory_code"]], sexes.index(e["sex"]), deps.index(e["admin_dependency"]),
                         2024, e["estimate"], e["ci_lower"], e["ci_upper"], "M", "microdados PeNSE 2024")
                pts_by.setdefault((fi, e["territory_code"], e["sex"], e["admin_dependency"], y), None)
                pts_by[("se", fi, e["territory_code"], e["sex"], e["admin_dependency"], y)] = float(e["standard_error"])
    diffs = {}
    for fi, t in enumerate(tables):
        ys = t["years"]
        for (code, _) in terr:
            for sx in sexes:
                for dp in deps:
                    for a, b in zip(ys, ys[1:]):
                        pa, pb = pts_by.get((fi, code, sx, dp, a)), pts_by.get((fi, code, sx, dp, b))
                        sea = pts_by.get(("se", fi, code, sx, dp, a))
                        seb = pts_by.get(("se", fi, code, sx, dp, b))
                        if b == 2024:
                            if sea is None or seb is None:
                                continue
                            ea = _num_e(estimates, t["indicator_key"], code, sx, dp, a)
                            eb = _num_e(estimates, t["indicator_key"], code, sx, dp, b)
                            method = "microdados (EP de desenho)"
                            decided = t.get("decision_status") == "DECISAO_REGISTRADA"
                        else:
                            if not pa or not pb or None in (pa[1], pa[2], pb[1], pb[2]):
                                continue
                            ea, eb = float(pa[0]), float(pb[0])
                            sea = (float(pa[2]) - float(pa[1])) / (2 * Z)
                            seb = (float(pb[2]) - float(pb[1])) / (2 * Z)
                            method = "aproximado pelo IC publicado"
                            decided = False   # série experimental do IBGE; teste aproximado → nunca recebe o selo
                        if ea is None or eb is None:
                            continue
                        sd = math.sqrt(sea ** 2 + seb ** 2)
                        d = eb - ea
                        sig = abs(d) > Z * sd
                        status = (CHANGE_NS if not sig else CHANGE_SIGNIFICANT if decided
                                  else CHANGE_PENDING if b == 2024 else "SIGNIFICATIVA_APROXIMADA")
                        diffs[f"{fi}|{code}|{sx}|{dp}|{b}"] = [a, round(d, 4), round(d - Z * sd, 4), round(d + Z * sd, 4),
                                                              1 if sig else 0, method, status]
    return {"tables": tables, "territories": [{"code": c, "name": n} for c, n in terr], "sexes": sexes, "deps": deps,
            "pts": cols, "diffs": diffs,
            "source": "IBGE, PeNSE — indicadores comparáveis do 9º ano, 2009–2019 (Tema 10, Segurança e violências)",
            "experimental_note": "O IBGE classifica a série 2009–2019 como estatística experimental (Estudos e Pesquisas "
                                 "n. 46, 2022): use com cautela. Diferenças entre anos publicados são testadas de forma "
                                 "aproximada (erro-padrão derivado do IC publicado); o IBGE usa regressão logística."}


def _num_e(estimates, key, code, sx, dp, year):
    for e in estimates:
        if (e["indicator_key"] == key and e["territory_code"] == code and e["sex"] == sx and e["admin_dependency"] == dp
                and e["age_group"] == "Total" and int(e["edition_year"]) == year):
            return float(e["estimate"])
    return None


def _add(cols, f, t, s, d, y, e, lo, hi, origin, src):
    cols["f"].append(f)
    cols["t"].append(t)
    cols["s"].append(s)
    cols["d"].append(d)
    cols["y"].append(y)
    cols["e"].append(_num(e))
    cols["lo"].append(_num(lo))
    cols["hi"].append(_num(hi))
    cols["o"].append(origin)
    cols["src"].append(src)


def _bundle(estimates, comp, series, editions, indicators, summary, pub_values=None) -> dict[str, Any]:
    keys = list(indicators)
    eds = [e for e in editions if any(r["edition_id"] == e for r in estimates)]
    terr = sorted({(r["territory_code"], r["territory_name"], r["territory_type"]) for r in estimates})
    t_index = {c: i for i, (c, _, _) in enumerate(terr)}
    dims = {d: sorted({r[d] for r in estimates}) for d in ("age_group", "sex", "admin_dependency")}
    comp_by = {c["indicator_key"]: c for c in comp}
    val = {}
    for s in summary:
        val.setdefault(s["indicator_key"], {})[s["edition_id"]] = {
            "status": s["status"], "compared": int(s["compared"]), "reproduz": int(s["reproduz"]),
            "proximo": int(s.get("proximo") or 0), "max_diff": float(s["max_abs_diff_estimate_pp"]),
            "table": s["published_table"], "brasil": s.get("brasil_reproduz") == "True"}
    cols: dict[str, list] = {k: [] for k in ("k", "ed", "t", "a", "s", "d", "e", "lo", "hi", "se", "cv", "n", "lp", "pe")}
    pub_values = pub_values or {}
    for r in estimates:
        cols["k"].append(keys.index(r["indicator_key"]))
        cols["ed"].append(eds.index(r["edition_id"]))
        cols["t"].append(t_index[r["territory_code"]])
        cols["a"].append(dims["age_group"].index(r["age_group"]))
        cols["s"].append(dims["sex"].index(r["sex"]))
        cols["d"].append(dims["admin_dependency"].index(r["admin_dependency"]))
        for c, f in (("e", "estimate"), ("lo", "ci_lower"), ("hi", "ci_upper"), ("se", "standard_error"),
                     ("cv", "coefficient_of_variation")):
            cols[c].append(_num(r[f]))
        cols["n"].append(int(r["n_denominator"]))
        cols["lp"].append(1 if r["low_precision"] == "True" else 0)
        pv = pub_values.get((r["indicator_key"], r["edition_id"], r["territory_code"], r["age_group"], r["sex"],
                             r["admin_dependency"])) if r.get("nonresponse_convention") == "SERIE" else None
        cols["pe"].append(_num(pv["estimate"]) if pv else None)   # valor na convenção da publicação (2015)
    diffs = {}
    for p in series:
        if p["diff_pp"] == "":
            continue
        diffs[f"{p['indicator_key']}|{p['territory_code']}|{p['age_group']}|{p['sex']}|{p['admin_dependency']}|{p['year']}"] = [
            p["previous_year"], p["diff_pp"], p["diff_ci_lower"], p["diff_ci_upper"],
            1 if p["significant_5pct"] in (True, "True") else 0, p["change_status"]]
    return {
        "editions": [{"id": e, "label": editions[e]["label"], "year": editions[e]["year"],
                      "levels": editions[e].get("territorial_levels", []),
                      "nonresponse": editions[e].get("nonresponse_rule_status", ""),
                      "design_note": editions[e].get("design_note", "")} for e in eds],
        "indicators": [{"key": k, "label": indicators[k]["label"], "period": indicators[k]["period"],
                        "population": indicators[k].get("population", "13_17"),
                        "question": comp_by[k].get("questions") or indicators[k].get("question", ""),
                        "informant": indicators[k].get("informant", "Escolar"),
                        "editions": indicators[k]["editions"], "definition_note": indicators[k].get("definition_note", ""),
                        "published": indicators[k].get("published", {}),
                        "comparability": {f: comp_by[k][f] for f in ("proposed_status", "final_status", "decision_status",
                                                                     "decision_source", "justification", "caveats",
                                                                     "series_editions", "evidence_by_edition",
                                                                     "excluded_edition_ids", "excluded_editions")},
                        "validation": val.get(k, {})} for k in keys],
        "territories": [{"code": c, "name": n, "type": t} for c, n, t in terr],
        "dims": dims, "est": cols, "diffs": diffs,
        "method": "Razão ponderada com pesos amostrais; IC 95% por linearização de Taylor (estratos e UPAs; "
                  "pós-estratificação em 2019 e 2024). Não resposta harmonizada entre edições (sem resposta no "
                  "denominador, abandono fora; IBGE 2022). Diferença entre anos: amostras independentes, "
                  "EP = √(EP₁² + EP₂²).",
    }

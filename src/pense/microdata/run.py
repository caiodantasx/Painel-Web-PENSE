"""Calcula indicadores a partir dos microdados e valida contra as tabelas publicadas.

Entradas: config/microdata/editions.toml, config/microdata/indicators.toml, microdados em
data/microdata/<EDIÇÃO>/ (não versionados; ver docs/12_microdados.md).

Saídas (data/curated/):
* microdata_estimates.csv  — uma linha por indicador × edição × território × recorte;
  ``data_origin = MICRODADOS_CALCULADO``, nunca misturada às estimativas publicadas;
* microdata_validation.csv — mesma estimativa comparada com a tabela publicada pelo IBGE
  (diferença de estimativa e de limites do IC) e veredito por regra de tolerância.

Recortes: Total, cada grupo de idade, sexo e dependência (um de cada vez, como nas tabelas
do IBGE), para Brasil, Grandes Regiões, UFs e capitais conforme a edição permitir.
"""
from __future__ import annotations

import csv
import logging
import math
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterator

import numpy as np

from ..config import Config
from .estimator import DesignArrays, ratio

log = logging.getLogger("pense.microdata")

TOL_ESTIMATE_PP = 0.05   # diferença máxima aceita na estimativa (pontos percentuais)
TOL_CI_PP = 0.15         # diferença máxima aceita em cada limite do IC
TOL_NEAR_PP = 0.30       # "próximo": diferença pequena, típica de domínios com poucas escolas
FIELDS = ["estimate_id", "data_origin", "indicator_key", "indicator_label", "edition_id", "edition_year", "period_code",
          "territory_type", "territory_code", "territory_name", "age_group", "sex", "admin_dependency",
          "estimate", "ci_lower", "ci_upper", "standard_error", "coefficient_of_variation", "n_denominator",
          "n_numerator", "weighted_denominator", "psu_in_domain", "low_precision", "small_sample",
          "estimation_method", "numerator_rule", "denominator_rule", "nonresponse_rule", "nonresponse_rule_status",
          "source_file", "published_reference", "definition_note", "informant", "variable", "population",
          "nonresponse_convention"]

# Convenções de não resposta (ver docs/04, D21):
# * PUBLICACAO — a da publicação oficial de cada edição; usada para validar contra as tabelas da edição.
# * SERIE — a da série harmonizada do IBGE (PeNSE 2009/2019, p. 18, nota 7): "sem resposta" entra no
#   denominador, "abandono de questionário" sai. Em 2019 e 2024 coincide com a da publicação.
CONV_PUB, CONV_SERIE = "PUBLICACAO", "SERIE"


@dataclass
class EditionData:
    key: str
    spec: dict[str, Any]
    frame: Any                 # pandas.DataFrame já filtrado (peso válido)
    design: DesignArrays
    last_answered: Any = None  # índice da última pergunta respondida (só edições com regra de abandono)
    question_pos: dict[str, int] | None = None


def series_rule(spec: dict[str, Any]) -> dict[str, Any] | None:
    """Regra de não resposta da série, se diferente da publicação (None = igual à publicação)."""
    return spec.get("series_nonresponse") or None


def conventions(spec: dict[str, Any]) -> list[str]:
    return [CONV_PUB, CONV_SERIE] if series_rule(spec) else [f"{CONV_PUB}+{CONV_SERIE}"]


def load_config(cfg: Config) -> tuple[dict[str, dict], dict[str, dict]]:
    base = cfg.config_dir / "microdata"
    with (base / "editions.toml").open("rb") as fh:
        editions = tomllib.load(fh)
    with (base / "indicators.toml").open("rb") as fh:
        indicators = tomllib.load(fh)
    return editions, indicators


def _columns(spec: dict, indicators: dict[str, dict], key: str) -> list[str]:
    pre = spec.get("var_prefix", "")
    cols = {spec["weight"], spec["strata"], *spec["psu"], spec["sex_var"], spec["dep_var"]}
    for c in ("age_var", "region_var"):
        if spec.get(c):
            cols.add(spec[c])
    for c in ("poststrata", "uf_var", "capital_var", "grade_var"):
        if spec.get(c):
            cols.add(spec[c])
    for ind in indicators.values():
        if key in ind["editions"]:
            for cond in _conditions(ind, key):
                cols.add(pre + cond["var"])
    return sorted(cols)


def _conditions(ind: dict, edition: str = "") -> list[dict]:
    """Condições de numerador/denominador da edição.

    ``by_edition`` troca variável e códigos numa edição com codificação própria (2009: B08Pxx,
    2012: B09xxx); ``var_by_edition`` só troca o nome (pergunta alterada, sufixo novo).
    """
    over = ind.get("by_edition", {}).get(edition)
    if over:
        return over["any"] if "any" in over else [{"var": over["var"], "num": over["num"], "den": over["den"]}]
    if "any" in ind:
        return ind["any"]
    var = ind["var_by_edition"][edition] if "var_by_edition" in ind else ind["var"]
    return [{"var": var, "num": ind["num"], "den": ind["den"]}]


def load_edition(cfg: Config, key: str, spec: dict, indicators: dict[str, dict]) -> EditionData | None:
    import pandas as pd

    path = cfg.root / spec["file"]
    if not path.exists():
        log.warning("Microdados ausentes — edição ignorada", extra={"edition": key, "path": str(path)})
        return None
    rule = series_rule(spec)
    qcols: list[str] = []
    if spec.get("format") == "fixed":
        df = _read_fixed(cfg, spec, _columns(spec, indicators, key))
    else:
        cols = _columns(spec, indicators, key)
        if rule and rule.get("split_code") is not None:
            header = pd.read_csv(path, sep=spec["sep"], nrows=0).columns.tolist()
            qcols = [c for c in header if c.startswith(rule["question_prefix"]) and c not in rule.get("exclude", [])]
            cols = list(dict.fromkeys(cols + qcols))
        df = pd.read_csv(path, sep=spec["sep"], decimal=spec["decimal"], usecols=cols, low_memory=False)
    df = df[df[spec["weight"]].notna() & (df[spec["weight"]] > 0)].reset_index(drop=True)
    last, qpos = None, None
    if qcols:
        # Abandono (IBGE 2022, p. 18, nota 7): o aluno parou antes da pergunta. Reconstrução: código de
        # não resposta numa pergunta SEM nenhuma resposta efetiva em perguntas posteriores (ordem do arquivo).
        A = df[qcols].to_numpy(dtype=float)
        skip = rule.get("not_answer_codes", [])
        answered = ~np.isnan(A) & ~np.isin(A, [rule["split_code"], *skip])
        idx = np.arange(len(qcols))
        last = np.where(answered.any(axis=1), (answered * idx).max(axis=1), -1)
        qpos = {c: i for i, c in enumerate(qcols)}
    psu = df[spec["psu"]].astype(str).agg("|".join, axis=1)
    post = df[spec["poststrata"]] if spec.get("poststrata") else None
    design = DesignArrays.build(df[spec["weight"]].to_numpy(), df[spec["strata"]].to_numpy(), psu.to_numpy(),
                                None if post is None else post.to_numpy())
    log.info("Microdados carregados", extra={"edition": key, "records": len(df),
                                             "psu": int(design.psu.max() + 1), "strata": int(design.stratum.max() + 1)})
    return EditionData(key, spec, df, design, last, qpos)


def _read_fixed(cfg: Config, spec: dict, columns: list[str]):
    """Arquivo de largura fixa (2009, 2012): posições tiradas do dicionário do IBGE."""
    import pandas as pd

    layout: dict[str, tuple[int, int]] = {}
    path = cfg.config_dir / "reference" / f"dicionario_{spec['layout_dictionary']}.csv"
    with path.open(encoding="utf-8-sig", newline="") as fh:
        for r in csv.DictReader(fh):
            if r["sheet"] == spec["layout_sheet"] and r["start"] and r["variable"] not in layout:
                layout[r["variable"]] = (int(r["start"]) - 1, int(r["start"]) - 1 + int(r["length"]))
    missing = [c for c in columns if c not in layout]
    if missing:
        raise KeyError(f"variáveis sem posição no dicionário: {missing}")
    df = pd.read_fwf(cfg.root / spec["file"], colspecs=[layout[c] for c in columns], names=columns,
                     dtype=str, encoding="latin-1", header=None)
    text_cols = set(spec.get("text_columns", []))
    for c in columns:
        df[c] = df[c].str.strip() if c in text_cols else pd.to_numeric(df[c], errors="coerce")
    return df


def _masks(ed: EditionData, ind: dict, convention: str = CONV_PUB) -> tuple[np.ndarray, np.ndarray, str, str]:
    """Numerador e denominador (antes do domínio), com a regra de não resposta da convenção pedida.

    ``convention``: PUBLICACAO (regra da publicação da edição), SERIE (regra harmonizada) ou
    NENHUMA (toda não resposta fora do denominador; só para medir efeitos).
    """
    df, pre = ed.frame, ed.spec.get("var_prefix", "")
    rule = series_rule(ed.spec) if convention == CONV_SERIE else None
    if convention == "NENHUMA":
        nr: list = []
    elif rule:
        nr = list(rule.get("in_denominator", []))
    else:
        nr = list(ed.spec.get("nonresponse_in_denominator", []))
    num = np.zeros(len(df), dtype=bool)
    den = np.zeros(len(df), dtype=bool)
    conds = _conditions(ind, ed.key)
    extra = ""
    for c in conds:
        col = df[pre + c["var"]]
        num |= col.isin(c["num"]).to_numpy()
        den |= col.isin(list(c["den"]) + nr).to_numpy()
        if rule and rule.get("split_code") is not None:
            if ed.last_answered is None or ed.question_pos is None or pre + c["var"] not in ed.question_pos:
                raise KeyError(f"{ed.key}: sem posição de pergunta para {pre + c['var']} (regra de abandono)")
            sem_resposta = (col == rule["split_code"]).to_numpy() & (ed.last_answered > ed.question_pos[pre + c["var"]])
            den |= sem_resposta
            extra = f"; código {rule['split_code']} com resposta posterior = sem resposta (entra); sem resposta posterior = abandono (sai)"
    num &= den
    rule_n = " OU ".join(f"{pre}{c['var']} ∈ {c['num']}" for c in conds)
    rule_d = " OU ".join(f"{pre}{c['var']} ∈ {list(c['den']) + nr}" for c in conds) + extra
    return num, den, rule_n, rule_d


def _territories(cfg: Config) -> dict[str, dict[str, str]]:
    return {t["territory_code"]: t for t in cfg.territories}


POPULATIONS = {"13_17": "Escolares de 13 a 17 anos", "9ANO": "Escolares do 9º ano do ensino fundamental"}


def domains(ed: EditionData, cfg: Config, population: str = "13_17") -> Iterator[tuple[dict[str, str], np.ndarray]]:
    """(rótulos do domínio, máscara) para cada território × recorte.

    ``population``: "13_17" (universo da PeNSE desde 2015 A2) ou "9ANO" (turmas do 9º ano, todas
    as idades — universo da série comparável 2009–2019 publicada pelo IBGE).
    """
    df, s = ed.frame, ed.spec
    terr = _territories(cfg)
    cuts: list[tuple[str, str, str, np.ndarray]]
    if population == "9ANO" and s.get("all_ninth_grade"):
        base = np.ones(len(df), dtype=bool)
        cuts = [("Total", "Total", "Total", base)]
    elif population == "9ANO":
        base = df[s["grade_var"]].isin(s["grade_9_codes"]).to_numpy()
        cuts = [("Total", "Total", "Total", base)]
    else:
        age = {g: df[s["age_var"]].isin(codes).to_numpy() for g, codes in s["age_groups"].items()}
        base = age["13 a 17 anos"]
        cuts = [("Total", "Total", "Total", base)]
        for g in ("13 a 15 anos", "16 e 17 anos"):
            cuts.append((g, "Total", "Total", age[g]))
    for lab, code in s["sex_codes"].items():
        cuts.append(("Total", lab, "Total", base & (df[s["sex_var"]] == code).to_numpy()))
    for lab, code in s["dep_codes"].items():
        codes = code if isinstance(code, list) else [code]
        cuts.append(("Total", "Total", lab, base & df[s["dep_var"]].isin(codes).to_numpy()))

    levels = s.get("territorial_levels", [])
    places: list[tuple[str, str, str, np.ndarray]] = []
    if "country" in levels:
        places.append(("country", "BR", "Brasil", np.ones(len(df), dtype=bool)))
    if "region" in levels:
        for rc, code in s["region_codes"].items():
            places.append(("region", rc, terr[rc]["territory_name"], (df[s["region_var"]] == code).to_numpy()))
    if "uf" in levels:
        for t in terr.values():
            if t["territory_type"] == "uf":
                places.append(("uf", t["territory_code"], t["territory_name"], (df[s["uf_var"]] == int(t["territory_code"])).to_numpy()))
    if "capital" in levels:
        cap_any = np.zeros(len(df), dtype=bool)
        for t in terr.values():
            if t["territory_type"] != "capital":
                continue
            if s.get("capital_kind") == "flag":
                m = ((df[s["uf_var"]] == int(t["uf_code"])) & (df[s["capital_var"]] == 1)).to_numpy()
            elif s.get("capital_kind") == "uf_code":      # 2009: só capitais; campo = código da UF da capital
                m = (df[s["capital_var"]] == int(t["uf_code"])).to_numpy()
            else:
                m = (df[s["capital_var"]] == int(t["territory_code"])).to_numpy()
            cap_any |= m
            places.append(("capital", t["territory_code"], t["territory_name"], m))
        places.append(("aggregate", "CAPITAIS", terr["CAPITAIS"]["territory_name"], cap_any))
    for ptype, pcode, pname, pmask in places:
        for a, sx, dp, cmask in cuts:
            yield ({"territory_type": ptype, "territory_code": pcode, "territory_name": pname,
                    "age_group": a, "sex": sx, "admin_dependency": dp}, pmask & cmask)


def estimate_all(cfg: Config, effects: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    """Estimativas por indicador × edição × domínio, em cada convenção de não resposta necessária.

    ``effects`` (opcional) recebe, para o total de cada indicador × edição (Brasil ou conjunto das
    capitais), a estimativa sem nenhuma não resposta no denominador, na convenção da publicação e
    na da série — base do efeito medido citado nas ressalvas (nada de valor fixo).
    """
    editions, indicators = load_config(cfg)
    cv_max = float(cfg.v("validation", "cv_high_threshold"))
    out: list[dict[str, Any]] = []
    for key, spec in editions.items():
        if not any(key in ind["editions"] for ind in indicators.values()):
            log.info("Edição sem indicador configurado — não carregada", extra={"edition": key})
            continue
        ed = load_edition(cfg, key, spec, indicators)
        if ed is None:
            continue
        doms_cache: dict[str, list] = {}
        for ikey, ind in indicators.items():
            if key not in ind["editions"]:
                continue
            pop = ind.get("population", "13_17")
            if pop == "9ANO" and not (spec.get("grade_var") or spec.get("all_ninth_grade")):
                continue
            if spec.get("only_populations") and pop not in spec["only_populations"]:
                continue
            if pop not in doms_cache:
                doms_cache[pop] = list(domains(ed, cfg, pop))
            if effects is not None:
                _effects(ed, ind, ikey, doms_cache[pop], effects)
            for conv in conventions(spec):
                num, den, rule_n, rule_d = _masks(ed, ind, CONV_SERIE if conv == CONV_SERIE else CONV_PUB)
                nr_text = (f"série harmonizada: {series_rule(spec).get('description', '')}" if conv == CONV_SERIE
                           else f"códigos {spec.get('nonresponse_in_denominator', [])} no denominador")
                for labels, dmask in doms_cache[pop]:
                    e = ratio(ed.design, num & dmask, den & dmask)
                    if e is None:
                        continue
                    pct = lambda v: round(100 * v, 6)  # noqa: E731
                    rec = {
                        "estimate_id": f"{key}|{ikey}|{labels['territory_code']}|{labels['age_group']}|{labels['sex']}|{labels['admin_dependency']}"
                                       + ("|SERIE" if conv == CONV_SERIE else ""),
                        "data_origin": "MICRODADOS_CALCULADO", "indicator_key": ikey, "indicator_label": ind["label"],
                        "edition_id": key, "edition_year": spec["year"], "period_code": ind["period"],
                        "population": POPULATIONS[pop], **labels,
                        "estimate": pct(e.p), "ci_lower": pct(e.ci_lower), "ci_upper": pct(e.ci_upper),
                        "standard_error": pct(e.se), "coefficient_of_variation": round(e.cv, 4) if not math.isnan(e.cv) else "",
                        "n_denominator": e.n_den, "n_numerator": e.n_num, "weighted_denominator": round(e.weighted_den, 2),
                        "psu_in_domain": e.psu_in_domain,
                        "low_precision": bool(not math.isnan(e.cv) and e.cv >= cv_max),
                        "small_sample": e.n_den < 100,
                        "estimation_method": "Razão ponderada; variância por linearização de Taylor (UPA com reposição no estrato)"
                                             + ("; ajuste de pós-estratificação" if spec.get("poststrata") else ""),
                        "numerator_rule": rule_n, "denominator_rule": rule_d,
                        "nonresponse_rule": nr_text,
                        "nonresponse_rule_status": spec.get("nonresponse_rule_status", ""),
                        "source_file": spec["file"], "published_reference": ind.get("published", {}).get(key, ""),
                        "definition_note": ind.get("definition_note", ""),
                        "informant": ind.get("informant", "Escolar"),
                        "variable": "+".join(c["var"] for c in _conditions(ind, key)),
                        "nonresponse_convention": conv,
                    }
                    out.append(rec)
        log.info("Indicadores calculados", extra={"edition": key, "estimates": sum(1 for r in out if r["edition_id"] == key)})
    return out


def _effects(ed: EditionData, ind: dict, ikey: str, doms: list, out: list[dict[str, Any]]) -> None:
    total = next(((lab, m) for lab, m in doms if lab["age_group"] == "Total" and lab["sex"] == "Total"
                  and lab["admin_dependency"] == "Total" and lab["territory_code"] in ("BR", "CAPITAIS")), None)
    if total is None:
        return
    lab, m = total
    vals = {}
    for conv in ("NENHUMA", CONV_PUB, CONV_SERIE):
        num, den, _, _ = _masks(ed, ind, conv)
        e = ratio(ed.design, num & m, den & m)
        vals[conv] = None if e is None else round(100 * e.p, 4)
    out.append({"indicator_key": ikey, "edition_id": ed.key, "edition_year": ed.spec["year"],
                "territory_code": lab["territory_code"], "estimate_sem_nao_resposta": vals["NENHUMA"],
                "estimate_publicacao": vals[CONV_PUB], "estimate_serie": vals[CONV_SERIE],
                "efeito_harmonizacao_pp": None if None in (vals[CONV_PUB], vals[CONV_SERIE])
                else round(vals[CONV_SERIE] - vals[CONV_PUB], 4),
                "efeito_incluir_nao_resposta_pp": None if None in (vals["NENHUMA"], vals[CONV_SERIE])
                else round(vals[CONV_SERIE] - vals["NENHUMA"], 4)})


def needed_convention(ref: str) -> str:
    """Tabelas da série comparável (referência com '@') usam a convenção da série; as demais, a da publicação."""
    return CONV_SERIE if "@" in ref else CONV_PUB


def validate_against_published(estimates: list[dict], published: list[dict]) -> list[dict[str, Any]]:
    """Compara cada estimativa com a observação publicada correspondente (mesmo recorte)."""
    pub: dict[tuple, dict] = {}
    for r in published:
        cat = r.get("response_category", "")
        key = (r["edition_id"], str(r["edition_year"]), r["table_family_id"], cat, r["territory_code"], r["age_group"],
               r["sex"], r["admin_dependency"])
        pub.setdefault(key, r)
    rows = []
    for e in estimates:
        ref = e["published_reference"]
        if not ref or needed_convention(ref) not in e.get("nonresponse_convention", CONV_PUB).split("+"):
            continue
        # "PENSE_SERIE_9ANO_CAPITAIS@10.7" = tabela de outra publicação (série), no mesmo ano da edição
        pub_ed, _, ref = ref.rpartition("@") if "@" in ref else (e["edition_id"], "", ref)
        fam, _, cat = ref.partition("|")
        p = pub.get((pub_ed, str(e["edition_year"]), fam, cat, e["territory_code"], e["age_group"], e["sex"],
                     e["admin_dependency"]))
        if p is None or p.get("estimate") in ("", None):
            continue
        pe, pl, pu = float(p["estimate"]), _f(p.get("ci_lower")), _f(p.get("ci_upper"))
        d_est = e["estimate"] - pe
        d_lo = None if pl is None else e["ci_lower"] - pl
        d_hi = None if pu is None else e["ci_upper"] - pu
        ok_est = abs(d_est) <= TOL_ESTIMATE_PP
        ok_ci = all(d is None or abs(d) <= TOL_CI_PP for d in (d_lo, d_hi))
        rows.append({
            "edition_id": e["edition_id"], "indicator_key": e["indicator_key"], "published_table": fam,
            "published_category": cat, "territory_code": e["territory_code"], "territory_name": e["territory_name"],
            "age_group": e["age_group"], "sex": e["sex"], "admin_dependency": e["admin_dependency"],
            "estimate_microdata": e["estimate"], "estimate_published": pe, "diff_estimate_pp": round(d_est, 4),
            "ci_microdata": f"{e['ci_lower']:.4f}–{e['ci_upper']:.4f}",
            "ci_published": "" if pl is None else f"{pl:.4f}–{pu:.4f}",
            "diff_ci_lower_pp": "" if d_lo is None else round(d_lo, 4), "diff_ci_upper_pp": "" if d_hi is None else round(d_hi, 4),
            "verdict": ("REPRODUZ" if ok_est and ok_ci else "ESTIMATIVA_OK_IC_DIFERE" if ok_est
                        else "PROXIMO" if abs(d_est) <= TOL_NEAR_PP else "NAO_REPRODUZ"),
            "published_cell": f"{p.get('source_file', '')}::{p.get('source_sheet', '')}!{p.get('source_cell', '')}",
        })
    return rows


def _f(v: Any) -> float | None:
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def summarize_validation(rows: list[dict], policies: dict[str, dict] | None = None) -> list[dict[str, Any]]:
    from collections import defaultdict

    g: dict[tuple, list[dict]] = defaultdict(list)
    for r in rows:
        g[(r["edition_id"], r["indicator_key"], r["published_table"], r["published_category"])].append(r)
    out = []
    for (ed, ik, tab, cat), rs in sorted(g.items()):
        n = len(rs)
        out.append({"edition_id": ed, "indicator_key": ik, "published_table": tab, "published_category": cat,
                    "compared": n, "reproduz": sum(r["verdict"] == "REPRODUZ" for r in rs),
                    "estimativa_ok_ic_difere": sum(r["verdict"] == "ESTIMATIVA_OK_IC_DIFERE" for r in rs),
                    "proximo": sum(r["verdict"] == "PROXIMO" for r in rs),
                    "nao_reproduz": sum(r["verdict"] == "NAO_REPRODUZ" for r in rs),
                    "share_reproduz": round(sum(r["verdict"] == "REPRODUZ" for r in rs) / n, 4),
                    "max_abs_diff_estimate_pp": max(abs(r["diff_estimate_pp"]) for r in rs),
                    "brasil_reproduz": any(r["verdict"] == "REPRODUZ" and r["territory_code"] == "BR"
                                           and r["age_group"] == "Total" and r["sex"] == "Total"
                                           and r["admin_dependency"] == "Total" for r in rs),
                    "status": _status(rs, (policies or {}).get(ed)),
                    "policy": ((policies or {}).get(ed) or {}).get("reason", "")})
    return out


def _status(rs: list[dict], policy: dict | None = None) -> str:
    """VALIDADO: nenhum recorte fora de 0,3 p.p. e ≥ 95% reproduzindo exatamente.

    Com ``policy`` (edições com microdados perturbados, ex.: 2019), aceita até ``max_pp`` em
    recortes, desde que os totais (sem recorte de idade, sexo ou dependência) reproduzam.
    """
    share = sum(r["verdict"] == "REPRODUZ" for r in rs) / len(rs)
    if not any(r["verdict"] == "NAO_REPRODUZ" for r in rs):
        return "VALIDADO" if share >= 0.95 else "VALIDADO_COM_RESSALVA"
    if policy:
        totals = [r for r in rs if r["age_group"] == "Total" and r["sex"] == "Total" and r["admin_dependency"] == "Total"
                  and r["territory_code"] in ("BR", "CAPITAIS")]
        within = all(abs(r["diff_estimate_pp"]) <= float(policy["max_pp"]) for r in rs)
        if within and totals and all(r["verdict"] == "REPRODUZ" for r in totals):
            return "VALIDADO_COM_RESSALVA"
    return "NAO_VALIDADO"


def write_csv(path: Path, rows: list[dict], fields: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = fields or (list(rows[0]) if rows else [])
    with path.open("w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        w.writeheader()
        w.writerows(rows)

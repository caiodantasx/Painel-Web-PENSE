"""Relatórios em Markdown gerados a cada execução (pasta ``reports/``)."""
from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any

from ..config import Config


def _table(headers: list[str], rows: list[list[Any]]) -> str:
    out = ["| " + " | ".join(headers) + " |", "|" + "---|" * len(headers)]
    for r in rows:
        out.append("| " + " | ".join("" if v is None else str(v).replace("|", "/") for v in r) + " |")
    return "\n".join(out)


def write_reports(cfg: Config, res: Any, manifest: dict[str, Any]) -> None:
    rep = cfg.path("reports")
    (rep / "relatorio_qualidade.md").write_text(_quality(res, manifest), encoding="utf-8")
    (rep / "relatorio_cobertura.md").write_text(_coverage(res), encoding="utf-8")
    (rep / "relatorio_comparabilidade.md").write_text(_comparability(res), encoding="utf-8")


def _quality(res: Any, manifest: dict[str, Any]) -> str:
    c = manifest["counts"]
    sev = Counter(i.severity for i in res.issues)
    by_rule: dict[tuple[str, str, str], list[Any]] = defaultdict(list)
    for i in res.issues:
        by_rule[(i.rule_id, i.severity, i.issue_class)].append(i)
    rule_rows = []
    for (rule, s, cls), items in sorted(by_rule.items(), key=lambda kv: ({"ERROR": 0, "REVIEW": 1, "WARNING": 2,
                                                                         "INFO": 3}[kv[0][1]], -len(kv[1]))):
        ex = items[0]
        rule_rows.append([rule, s, cls, len(items), ex.message[:140],
                          f"{ex.source_file.split('!')[-1]} / {ex.source_sheet} / {ex.source_cell}",
                          ex.recommended_action[:120]])
    status_rows = [[k, v] for k, v in sorted(c["validation_status"].items())]
    lines = [
        "# Relatório de qualidade dos dados",
        "",
        f"Gerado pela pipeline v{manifest['pipeline_version']} em {manifest['executed_at_utc']} (UTC).",
        "",
        "## Resumo",
        "",
        f"- Arquivos inventariados: **{c['files_inventoried']}** ({c['duplicates']} duplicados por SHA-256, não reprocessados)",
        f"- Abas lidas: **{c['sheets']}** — por família: {c['sheets_by_family']}",
        f"- Observações de estimativa: **{c['estimate_records']}** (+ {c['cv_records']} linhas de CV usadas para enriquecer/validar)",
        f"- Observações aprovadas para análise (canônicas, sem duplicidade entre tabelas): **{c['approved_canonical']}**",
        f"- Duplicidades analíticas (mesmo recorte publicado em mais de uma tabela): {c['analytical_duplicates']}",
        f"- Itens não interpretados (ver `data/processed/unparsed_report.csv`): {c['unparsed_items']}",
        "",
        "### Status de validação das observações",
        "",
        _table(["Status", "Observações"], status_rows),
        "",
        "### Alertas por severidade",
        "",
        _table(["Severidade", "Alertas"], [[k, sev[k]] for k in ("ERROR", "REVIEW", "WARNING", "INFO") if sev[k]]),
        "",
        "Significado: **ERROR** bloqueia a aprovação; **REVIEW** exige decisão humana; **WARNING** é aprovável com "
        "ressalva visível; **INFO** é registro de rastreabilidade. Nenhum valor foi removido ou corrigido.",
        "",
        "## Regras executadas",
        "",
        "Número de avaliações feitas por regra nesta execução (uma regra com 0 alertas e muitas avaliações "
        "é evidência de consistência, não de regra inativa):",
        "",
        _table(["Regra", "Avaliações", "Alertas"], [[k, v, sum(1 for i in res.issues if i.rule_id.startswith(k.split('/')[0]))]
                                                  for k, v in manifest.get("rule_checks", {}).items()]),
        "",
        "## Alertas por regra",
        "",
        _table(["Regra", "Severidade", "Classe", "Qtde", "Exemplo", "Origem do exemplo", "Ação recomendada"], rule_rows),
        "",
        "Lista completa, com célula de origem e status de revisão: `data/processed/quality_issues.csv`.",
        "",
    ]
    return "\n".join(lines)


def _coverage(res: Any) -> str:
    by_file: dict[str, dict[str, Any]] = {}
    for s in res.sheets:
        f = by_file.setdefault(s["source_file"], {"sheets": 0, "records": 0, "families": set(), "years": set(),
                                                  "tables": set(), "status": Counter()})
        f["sheets"] += 1
        f["records"] += s["records"]
        f["families"].add(s["adapter_family"] or "—")
        if s["year"]:
            f["years"].add(str(s["year"]))
        if s["table_id"]:
            f["tables"].add(s["table_id"])
        f["status"][s["status"]] += 1
    file_rows = [[k.split("!")[-1], k.split("!")[0] if "!" in k else "", v["sheets"], ", ".join(sorted(v["families"])),
                  ", ".join(sorted(v["years"])), v["records"], dict(v["status"])] for k, v in sorted(by_file.items())]
    ind: dict[tuple[str, str], dict[str, Any]] = {}
    for r in res.estimates:
        k = (r["edition_id"], r["table_family_id"])
        d = ind.setdefault(k, {"n": 0, "ok": 0, "terr": set(), "cats": set(), "name": r["indicator_name"]})
        d["n"] += 1
        d["ok"] += 1 if r.get("approved_for_analysis") and not r.get("analytical_duplicate_of") else 0
        d["terr"].add(r["territory_type"])
        d["cats"].add(r["response_category"] or "(geral)")
    ind_rows = [[e, f, v["name"][:90], len(v["cats"]), ", ".join(sorted(t for t in v["terr"] if t)), v["n"], v["ok"]]
                for (e, f), v in sorted(ind.items())]
    files = [[f["file_name"], f["container"], f["format"], f["status"], f["sha256"][:12], f["duplicate_of"]]
             for f in res.files]
    return "\n".join([
        "# Relatório de cobertura", "",
        "## Arquivos de entrada", "",
        _table(["Arquivo", "Contêiner", "Formato", "Status", "SHA-256 (12)", "Duplicado de"], files), "",
        "## Abas por arquivo", "",
        _table(["Arquivo", "ZIP", "Abas", "Família", "Ano", "Observações", "Status das abas"], file_rows), "",
        "## Indicadores por edição", "",
        _table(["Edição", "Tabela", "Indicador", "Categorias", "Territórios", "Observações", "Aprovadas (canônicas)"],
               ind_rows), "",
    ])


def _comparability(res: Any) -> str:
    rows = [[p["concept_id"], f"{p['left_indicator_id']} [{p['left_category'] or 'geral'}]",
             f"{p['right_indicator_id']} [{p['right_category'] or 'geral'}]", p["final_status"],
             p["decision_source"], (p.get("differences") or p["final_justification"])[:260]]
            for p in res.comparability]
    st = [[s["concept_id"], s["final_status"], "sim" if s["included_in_series"] else "não"] for s in res.series_status]
    return "\n".join([
        "# Catálogo de comparabilidade entre edições", "",
        "Pares candidatos definidos em `config/comparability_candidates.csv`. O status automático é conservador: "
        "diferença em atributo essencial → `NOT_COMPARABLE`; ausência de impedimento → `PENDING_REVIEW`. "
        "`COMPARABLE` só por decisão humana registrada em `config/comparability_decisions.csv`.", "",
        _table(["Conceito", "Esquerda", "Direita", "Status final", "Origem da decisão", "Diferenças / justificativa"], rows),
        "", "## Inclusão na série histórica", "",
        _table(["Conceito", "Status", "Na série?"], st), "",
        f"Pontos de série histórica gerados: **{len(res.series)}**.", "",
    ])

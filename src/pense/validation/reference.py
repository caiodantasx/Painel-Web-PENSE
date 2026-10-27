"""Conferência das abas lidas contra o guia oficial de tabelas do IBGE (PeNSE 2024).

O guia (``config/reference/guia_tabelas_pense_2024.csv``, gerado por
``scripts/build_reference.py``) lista, para cada tema, o nome de cada aba e o título
publicado. A conferência responde três perguntas para os temas presentes na base:

* REF001 — alguma aba do guia não foi encontrada nos arquivos? (tabela faltando no download)
* REF002 — o título extraído pela pipeline difere do título do guia? (erro de leitura do título
  ou arquivo de outra versão)
* REF003 — há aba de 2024 que o guia não lista? (arquivo inesperado)

Temas que não estão na base não geram alerta: o guia cobre os 19 temas e a base, por
enquanto, só os de segurança.
"""
from __future__ import annotations

import re
from typing import Any

from ..models import Issue, IssueClass, Severity
from ..text import compact

_PREFIX = re.compile(r"^Tabela\s+[\d.]+\s*[-–]\s*", re.I)
_SUFFIX = re.compile(r"\s*[-–]\s*(?:19|20)\d{2}\s*$")


def normalize_title(title: str) -> str:
    """Remove "Tabela x.y.z -" e o sufixo de ano; compara sem acentos, espaços e caixa."""
    return compact(_SUFFIX.sub("", _PREFIX.sub("", (title or "").strip())))


def check_against_guide(sheets: list[dict[str, Any]], guide: list[dict[str, str]],
                        edition_year: str = "2024") -> tuple[list[Issue], list[dict[str, str]], dict[str, int]]:
    if not guide:
        return [], [], {}
    by_sheet = {g["sheet_name"]: g for g in guide}
    ours = [s for s in sheets if str(s.get("year")) == edition_year or str(s.get("footer_year")) == edition_year]
    themes = {str(s["sheet"]).split(".")[0] for s in ours if str(s["sheet"]).split(".")[0].isdigit()}
    issues: list[Issue] = []
    report: list[dict[str, str]] = []
    seen: set[str] = set()
    for s in ours:
        name = str(s["sheet"])
        seen.add(name)
        g = by_sheet.get(name)
        if g is None:
            status = "NAO_LISTADA_NO_GUIA"
            issues.append(Issue(rule_id="REF003", severity=Severity.REVIEW.value, issue_class=IssueClass.NOT_VALIDATED.value,
                                message=f"Aba '{name}' não consta do guia oficial de tabelas {edition_year}",
                                recommended_action="Conferir se o arquivo é da mesma versão do guia.",
                                source_file=str(s["source_file"]), source_sheet=name, stage="reference"))
        elif normalize_title(str(s.get("title", ""))) != normalize_title(g["title"]):
            status = "TITULO_DIFERENTE"
            issues.append(Issue(rule_id="REF002", severity=Severity.WARNING.value, issue_class=IssueClass.POSSIBLE_ANOMALY.value,
                                message=f"Título extraído difere do guia oficial: '{g['title'][:160]}'",
                                recommended_action="Conferir a leitura do título (linhas mescladas) e a versão do arquivo.",
                                source_file=str(s["source_file"]), source_sheet=name,
                                observed_value=str(s.get("title", ""))[:300], stage="reference"))
        else:
            status = "CONFERE"
        report.append({"sheet_name": name, "source_file": str(s["source_file"]), "status": status,
                       "title_extracted": str(s.get("title", "")), "title_guide": g["title"] if g else ""})
    for g in guide:
        if g["theme_id"] in themes and g["sheet_name"] not in seen:
            issues.append(Issue(rule_id="REF001", severity=Severity.INFO.value, issue_class=IssueClass.INFORMATIONAL.value,
                                message=f"Aba '{g['sheet_name']}' do guia (tema {g['theme_id']}) não está nos arquivos",
                                recommended_action="Baixar a tabela no site do IBGE se ela for necessária.",
                                source_sheet=g["sheet_name"], stage="reference"))
            report.append({"sheet_name": g["sheet_name"], "source_file": "", "status": "AUSENTE_NOS_ARQUIVOS",
                           "title_extracted": "", "title_guide": g["title"]})
    checks = {"REF_abas_conferidas": len(ours), "REF_temas": len(themes),
              "REF_titulos_iguais": sum(1 for r in report if r["status"] == "CONFERE")}
    return issues, sorted(report, key=lambda r: r["sheet_name"]), checks

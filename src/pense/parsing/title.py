"""Interpretação de títulos, enunciados e notas de rodapé das tabelas do IBGE.

Cada campo extraído vem acompanhado do método/evidência. Quando um padrão não
é encontrado, o campo fica vazio e o status é ``PENDENTE`` — nada é inferido
silenciosamente.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from ..text import clean_text, slug
from .grid import Grid

PENDING = "PENDENTE"

_TABLE_ID = re.compile(r"^Tabela\s+([0-9]+(?:\.[0-9]+)*)\s*[-–]\s*", re.I)
_YEAR_SUFFIX = re.compile(r"[-–]\s*((?:19|20)\d{2})\s*$")
# Sufixo com mais de um ano: "- 2009-2015", "- 2009/2015", "- 2009, 2012 e 2015", "- 2009 a 2015"
_YEAR_LIST_SUFFIX = re.compile(
    r"[-–]\s*((?:19|20)\d{2}(?:\s*(?:,|e|a|/|-|–)\s*(?:19|20)\d{2})+)\s*$")
YEAR_LABEL = re.compile(r"^((?:19|20)\d{2})(?:\.0+)?(?:\s*\(\d+\))?$")


def year_label(label: str) -> str:
    """'2009', '2009.0' (número do .xls) ou '2009 (1)' -> '2009'; demais rótulos -> ''."""
    m = YEAR_LABEL.match(label.strip())
    return m.group(1) if m else ""
_FOOTER_YEAR = re.compile(r"Sa[uú]de do Escolar(?:,\s*Amostra\s*(\d+))?,?\s*((?:19|20)\d{2})", re.I)
_AGE_RANGE = re.compile(r"escolares (?:com idade )?de (\d{1,2}) a (\d{1,2}) anos", re.I)  # 2015 A2: "com idade de"
_GRADE_9 = re.compile(r"escolares (?:frequentando o|do) 9[ºo°] ano", re.I)
_UNDER_18 = re.compile(r"menores de 18 anos", re.I)
_PERIOD = [
    (re.compile(r"nos (\d+) (dias|meses) anteriores [àa] pesquisa", re.I), "{0} {1} anteriores à pesquisa"),
    (re.compile(r"nos [uú]ltimos (\d+) (dias|meses)", re.I), "últimos {0} {1}"),
    (re.compile(r"alguma vez na vida", re.I), "alguma vez na vida"),
]


def period_code(text: str) -> str:
    """Código canônico do período: "30 dias anteriores à pesquisa" e "últimos 30 dias" -> 30_DIAS."""
    m = re.search(r"(\d+) (dias|meses)", text)
    if m:
        return f"{m.group(1)}_{m.group(2).upper()}"
    if "vida" in text:
        return "VIDA"
    return PENDING
# "em escolas cujo diretor…", "em escolas que informaram…", "em escolas que tiveram de suspender…" (2019):
# característica da escola, informada pelo diretor(a) — a PeNSE é amostra de alunos (Nota n. 01, 2015).
_INFORMANT_SCHOOL = re.compile(r"em escolas (?:cujo diretor|que )", re.I)
_CONDITIONAL = re.compile(r"(?:dentre|entre) (?:aqueles|os|as) que ([^,]+?)(?:,|$)", re.I)
_CI_LEVEL = re.compile(r"intervalo de confian[cç]a de (\d{2})\s*%", re.I)


@dataclass
class TitleInfo:
    title: str = ""
    title_rows: list[int] = field(default_factory=list)
    table_id: str = ""
    statement: str = ""
    year: int | None = None
    year_method: str = PENDING
    footer_year: int | None = None
    sample: str = ""
    population: str = PENDING
    population_code: str = PENDING
    age_min: int | None = None
    age_max: int | None = None
    reference_period: str = PENDING
    reference_period_code: str = PENDING
    informant: str = PENDING
    informant_method: str = PENDING
    conditional_on: str = ""
    territorial_scope: str = PENDING
    estimate_type: str = PENDING
    confidence_level: int | None = None
    is_cv_sheet: bool = False
    multi_year: bool = False
    years_in_title: list[int] = field(default_factory=list)
    footnotes: list[str] = field(default_factory=list)
    footnote_rows: list[int] = field(default_factory=list)
    denominator_note: str = ""
    nonresponse_excluded: bool = False
    multi_response: bool = False
    continuation: str = ""


def extract_title(grid: Grid, max_scan: int = 12) -> tuple[str, list[int]]:
    """Junta as linhas de título (2009 quebra o título em até 4 linhas)."""
    start = None
    for r in range(min(max_scan, grid.nrows)):
        if _TABLE_ID.match(grid.text(r, 0)):
            start = r
            break
    if start is None:
        return "", []
    parts, rows = [], []
    for r in range(start, min(start + 6, grid.nrows)):
        t = grid.text(r, 0)
        others = [grid.text(r, c) for c in range(1, grid.ncols)]
        if not t or (r > start and any(others) and not all(o in ("", "(continua)", "(continuação)", "(conclusão)")
                                                         for o in others)):
            break
        parts.append(t)
        rows.append(r)
        if _YEAR_SUFFIX.search(t) or _YEAR_LIST_SUFFIX.search(t):
            break
    return clean_text(" ".join(parts)), rows


def extract_footnotes(grid: Grid, from_row: int) -> tuple[list[str], list[int]]:
    notes, rows = [], []
    for r in range(from_row, grid.nrows):
        t = grid.text(r, 0)
        if not t:
            continue
        s = slug(t)
        if s.startswith(("fonte", "nota", "notas", "obs")) or re.match(r"^\(?\d+\)", t):
            notes.append(t)
            rows.append(r)
    return notes, rows


def parse_title(title: str, footnotes: list[str] | None = None) -> TitleInfo:
    info = TitleInfo(title=title)
    footnotes = footnotes or []
    info.footnotes = footnotes
    m = _TABLE_ID.match(title)
    if m:
        info.table_id = m.group(1)
    body = _TABLE_ID.sub("", title)
    ml = _YEAR_LIST_SUFFIX.search(body)
    m = None if ml else _YEAR_SUFFIX.search(body)
    if ml:
        # Tabela com vários anos: o ano NÃO é atribuído pelo título; vem de cada coluna/linha.
        info.years_in_title = [int(y) for y in re.findall(r"(?:19|20)\d{2}", ml.group(1))]
        info.multi_year = True
        info.year_method = "título com vários anos — ano obrigatório por coluna ou linha"
        body = _YEAR_LIST_SUFFIX.sub("", body).strip()
    if m:
        info.year = int(m.group(1))
        info.year_method = "sufixo do título"
        body = _YEAR_SUFFIX.sub("", body).strip()
    info.statement = re.split(r",\s*com indica[cç][aã]o d", body, maxsplit=1)[0].strip()
    for note in footnotes:
        fm = _FOOTER_YEAR.search(note)
        if fm:
            info.footer_year = int(fm.group(2))
            if fm.group(1):
                info.sample = f"Amostra {fm.group(1)}"
            if info.year is None and not info.multi_year:
                info.year = info.footer_year
                info.year_method = "rodapé (fonte)"
    _parse_population(info, body)
    for rx, fmt in _PERIOD:
        pm = rx.search(body)
        if pm:
            info.reference_period = fmt.format(*pm.groups())
            info.reference_period_code = period_code(info.reference_period)
            break
    if _INFORMANT_SCHOOL.search(body):
        info.informant = "Escola (diretor(a) ou responsável)"
        info.informant_method = "título menciona informação prestada pela escola"
    else:
        info.informant = "Escolar (autopreenchimento)"
        info.informant_method = "inferido: título não menciona informante escolar — conferir questionário"
    cm = _CONDITIONAL.search(body)
    if cm:
        info.conditional_on = cm.group(1).strip()
    info.territorial_scope = _scope(body)
    low = slug(body)
    if low.startswith("distribuicao percentual"):
        info.estimate_type = "distribuicao_percentual"
    elif low.startswith("estimativas total e percentual"):
        info.estimate_type = "total_e_percentual"
    elif low.startswith("percentual"):
        info.estimate_type = "percentual"
    ci = _CI_LEVEL.search(title)
    if ci:
        info.confidence_level = int(ci.group(1))
    info.is_cv_sheet = "coeficiente de variacao" in slug(title)
    for note in footnotes:
        s = slug(note)
        if "exclusive" in s:
            info.denominator_note = clean_text(note.split(":", 1)[-1])
        if "sem resposta" in s:
            info.nonresponse_excluded = True
        if "mais de uma resposta" in s:
            info.multi_response = True
    return info


def _parse_population(info: TitleInfo, body: str) -> None:
    am = _AGE_RANGE.search(body)
    if am:
        info.age_min, info.age_max = int(am.group(1)), int(am.group(2))
        info.population = f"Escolares de {info.age_min} a {info.age_max} anos"
        info.population_code = f"ESCOLARES_{info.age_min}_{info.age_max}_ANOS"
    elif _GRADE_9.search(body):
        info.population = "Escolares do 9º ano do ensino fundamental"
        info.population_code = "ESCOLARES_9ANO_EF"
        if _UNDER_18.search(body):
            info.population += " menores de 18 anos"
            info.population_code += "_MENORES_18"


def _scope(body: str) -> str:
    s = slug(body.split("segundo", 1)[-1]) if "segundo" in body else slug(body)
    if "capitais" in s:
        return "capital"
    if "unidades da federacao" in s:
        return "uf"
    if "grandes regioes" in s:
        return "region"
    return PENDING

"""Frase de leitura de cada medida do painel ("X% de quê?").

Gera, a partir dos metadados extraídos do título e das notas do IBGE (nada digitado à mão por
indicador), três textos que o painel mostra junto do número:

* ``reading``: frase completa com o marcador ``{v}`` no lugar do valor, por exemplo
  "{v} dos escolares de 13 a 17 anos que estiveram envolvidos em briga na qual alguma pessoa usou
  arma branca nos 30 dias anteriores à pesquisa";
* ``base``: quem são os 100% (o denominador publicado);
* ``respondent``: quem respondeu e o que o número NÃO é (proporção de alunos — não número de
  ocorrências, de escolas ou de boletins de ocorrência).

E a "ficha do número" (``explain``), mostrada em blocos curtos no painel:
``count_base`` (quem são os 100%, para ler "X em cada 100 …"), ``situation`` (o que os alunos
contados têm em comum), ``who`` (quem respondeu), ``period`` e ``not_this`` (com o que NÃO
confundir). Tudo derivado do título, da categoria e do informante publicados pelo IBGE.

Quando o nome não segue nenhum padrão conhecido, a frase é genérica e diz isso, em vez de
inventar uma construção gramatical.
"""
from __future__ import annotations

import re
from typing import Any

_PCT = re.compile(r"^(Distribuição percentual|Percentual) (de|dos|das|do|da) ", re.I)
_COUNT = re.compile(r"^Estimativa total de ", re.I)
_TAIL_POR = re.compile(r"\s+por ((?:tipo|principal causa|idade|identificação|localização|número)[^,]*)$", re.I)
_FREQ = re.compile(r"^(escolares .*?) por frequência com que, (.*)$", re.I)

SOURCE_NOTE = ("Fonte: PeNSE/IBGE, pesquisa por amostra respondida em questionário. É uma estimativa com margem de "
               "erro, não uma contagem de registros policiais, boletins de ocorrência ou queixas.")


def _clean(text: str) -> str:
    t = re.sub(r"\s+", " ", (text or "")).strip().rstrip(".")
    return t.replace(" nos nos ", " nos ")


def _quote(c: str) -> str:
    return f"“{c}”"


def respondent_note(informant: str) -> str:
    if (informant or "").startswith("Escola ("):
        return ("Quem respondeu: o diretor(a) ou responsável pela escola, no questionário da escola. O número conta "
                "ALUNOS: é a parcela dos escolares que estudam em escolas que deram essa resposta — não é a proporção "
                "de escolas nem o número de ocorrências.")
    if (informant or "").startswith("Escolar"):
        return ("Quem respondeu: o próprio aluno, em questionário sigiloso e sem identificação. O número é a parcela "
                "dos alunos que relataram a situação — não é o número de ocorrências nem de registros policiais.")
    return "Quem respondeu: não identificado com segurança no título da tabela (PENDENTE)."


_POP_PREFIX = re.compile(
    r"^(?:escolares|alunos)\s+(?:com idade\s+)?(?:de\s+\d{1,2}\s+a\s+\d{1,2}\s+anos"
    r"|(?:frequentando o|do)\s+9[ºo°]\s+ano(?:\s+do\s+ensino\s+fundamental)?(?:\s+menores de 18 anos de idade)?)\s*", re.I)
_AMONG = re.compile(r"^,?\s*dentre aqueles que [^,]*,\s*", re.I)


def _lower_first(t: str) -> str:
    return t[:1].lower() + t[1:] if t else t


def explain(m: dict[str, Any], base: str) -> dict[str, str]:
    """Ficha do número: blocos curtos para responder "X% de quê?" sem ambiguidade."""
    name, cat, group = _clean(m.get("name", "")), _clean(m.get("category", "")), _clean(m.get("category_group", ""))
    informant = m.get("informant", "") or ""
    school = informant.startswith("Escola (")
    period = _clean(m.get("period", ""))
    out = {"count_base": "", "situation": "", "who": "", "period": period, "not_this": ""}
    if school:
        out["who"] = ("o diretor(a) ou responsável pela escola, no questionário da escola — "
                      "a resposta é sobre a escola ou sobre a localidade (o entorno) da escola")
        out["not_this"] = ("Não é a % de escolas, nem o número de ocorrências, nem registro policial ou boletim de "
                           "ocorrência. Também não significa que esses alunos sofreram ou viram a violência: quem "
                           "respondeu foi o diretor; o número diz quantos alunos estudam em escolas com essa resposta.")
    elif informant.startswith("Escolar"):
        out["who"] = "o próprio aluno, em questionário sigiloso, sem identificação, respondido na escola"
        out["not_this"] = ("Não é o número de casos, nem registro policial ou boletim de ocorrência: é a parcela de "
                           "alunos que relatou a situação no questionário. Um aluno conta uma vez, mesmo que a situação "
                           "tenha acontecido várias vezes.")
    else:
        out["who"] = "não identificado com segurança no título da tabela (PENDENTE)"
    if m.get("unit") != "%":
        out["not_this"] = "Número estimado de alunos (expansão da amostra), não de ocorrências." + (
            " " + out["not_this"] if school else "")
        return out
    b = re.sub(r"\s*\(nota:.*$", "", base or "", flags=re.I).strip()
    out["count_base"] = _lower_first(b)
    mm = _PCT.match(name)
    body = name[mm.end():] if mm else name
    rest = _POP_PREFIX.sub("", body, count=1)
    rest = _AMONG.sub("", rest)
    if cat and not group and ", por " in rest:
        rest = rest.rsplit(", por ", 1)[0]
    is_dist = bool(cat) and (group.lower().startswith(("percentual dos", "distribuição"))
                             or bool(mm and (mm.group(1).lower().startswith("distribuição") or mm.group(2).lower() == "dos")))
    if cat and rest.lower().startswith("por frequência com que"):
        situation = f"responderam {_quote(cat)} quando perguntados com que frequência{rest[len('por frequência com que'):]}"
    elif is_dist:
        por = re.sub(r"^distribuição percentual por |^percentual dos escolares .*? por ", "", group, flags=re.I) if group else ""
        if not por:
            tail = _TAIL_POR.search(name) or re.search(r"\s+por ([^,]+)$", name)
            por = tail.group(1) if tail else ""
        situation = f"estão na categoria {_quote(cat)}" + (f" ({_lower_first(por)})" if por else "")
    else:
        r = re.sub(r"^que,?\s*", "", rest.strip(" ,"), flags=re.I)
        r = re.sub(r"\s+dentre aqueles que .*?(?=\s+nos \d+ dias|$)", "", r, flags=re.I)
        if r.lower().startswith("em escolas"):
            r = "estudam " + r
        situation = r + (f" — {_quote(cat)}" if cat else "")
    out["situation"] = _lower_first(situation.strip())
    return out


def reading(m: dict[str, Any]) -> dict[str, str]:
    """Textos de leitura de uma medida (``m`` = registro de medida do pacote do painel)."""
    name, cat, group = _clean(m.get("name", "")), _clean(m.get("category", "")), _clean(m.get("category_group", ""))
    pop = (m.get("population") or "").strip()
    den = _clean(m.get("denominator", ""))
    base = den if den and not den.startswith("Não se aplica") else ""
    out = {"base": base, "respondent": respondent_note(m.get("informant", "")), "source": SOURCE_NOTE}

    if m.get("unit") != "%" and _COUNT.match(name):
        body = _COUNT.sub("", name)
        out["reading"] = f"{{v}} {body} (número estimado de alunos, não de ocorrências)"
        out["unit_label"] = "número estimado de escolares"
        out.update(explain(m, ""))
        return out

    mm = _PCT.match(name)
    if not mm:
        out["reading"] = f"{{v}} — {name}"
        out["unit_label"] = "%"
        out.update(explain(m, out["base"]))
        return out
    body = name[mm.end():]
    if not body.lower().startswith("escolares"):
        body = "escolares " + body
    # Subgrupo (os 100% são um grupo menor que a população) só quando o título ou o grupo de colunas
    # descreve o subgrupo ("Distribuição percentual…", "Percentual dos escolares que…"). Um rótulo de
    # dimensão como "Local" (2009, tabela 8.1) NÃO indica subgrupo: lá cada categoria é % de TODOS os
    # escolares (trajeto 6,4% e escola 5,5% nas capitais; a série oficial 10.7/10.8 dá 6,3% e 5,4%).
    subgroup = (mm.group(1).lower().startswith("distribuição") or mm.group(2).lower() == "dos"
                or group.lower().startswith(("percentual dos", "distribuição")))
    por = ""
    if cat and not group:   # com grupo de categorias, o "por" do título faz parte do conceito (ex.: 2009, 8.1)
        if ", por " in body:
            body, por = body.rsplit(", por ", 1)
        elif _TAIL_POR.search(body):
            por = _TAIL_POR.search(body).group(1)
            body = _TAIL_POR.sub("", body)
    if group and not por:
        por = re.sub(r"^distribuição percentual por ", "", group, flags=re.I)

    freq = _FREQ.match(body) if cat else None
    if freq:
        out["reading"] = (f"{{v}} dos {freq.group(1)} responderam {_quote(cat)} quando perguntados com que frequência, "
                          f"{freq.group(2)}")
    elif cat and subgroup:
        if ", por " in body:   # o "por <dimensão>" descreve as categorias, não quem são os 100%
            body, por0 = body.rsplit(", por ", 1)
            por = por or por0
        out["reading"] = f"Entre os {body}, {{v}} estão na categoria {_quote(cat)}" + (f" ({por})" if por else "")
        if not base or base.lower() == pop.lower():
            out["base"] = body[0].upper() + body[1:]   # os 100% são o grupo descrito, não todos os escolares
    elif cat:
        out["reading"] = f"{{v}} dos {body} — {por or 'categoria'}: {_quote(cat)}"
    else:
        out["reading"] = f"{{v}} dos {body}"
    out["unit_label"] = ("% dentro do grupo descrito na base" if subgroup
                         else f"% dos {pop[0].lower() + pop[1:]}" if pop else "%")
    out.update(explain(m, out["base"]))
    return out

"""Adaptadores concretos para as famílias identificadas na auditoria.

| Família                | Arquivos                         | Particularidades                                   |
|------------------------|----------------------------------|----------------------------------------------------|
| PENSE_2024_IC          | Tabelas 9.x / 17.x (abas x.y.z)  | Percentual + IC95%; seções de idade/sexo/dependência|
| PENSE_2024_CV          | Abas "x.y.z (CV)"                | Percentual + CV; usado para enriquecer e validar   |
| PENSE_2019_IC          | Tema_17_..._20260615.xls (2019)  | Mesma gramática de 2024; sem CV; seções por dependência|
| PENSE_2009_CAPITAIS    | tab8xx.xls                       | 9º ano; só capitais; "Total" = conjunto das capitais;|
|                        |                                  | rótulo da estimativa é "Total"; abas de continuação |
| PENSE_2015_A1          | Amostra_1_Tema_06 (*.xls)        | 9º ano; contagem estimada + percentual na mesma aba |
| PENSE_2015_A2          | Amostra_2_Tema_11 (*.xls)        | 13 a 17 anos; percentual + IC95%; Brasil e regiões  |
"""
from __future__ import annotations

import re

from .base import BaseAdapter, Detection, SheetContext

_THREE_PART = re.compile(r"^\d+\.\d+\.\d+$")
_FOUR_PART = re.compile(r"^\d+\.\d+\.\d+\.\d+$")
_TWO_PART = re.compile(r"^\d+\.\d+$")


class Pense2024EstimateAdapter(BaseAdapter):
    family_id = "PENSE_2024_IC"
    description = "PeNSE 2024 — abas de estimativa com intervalo de confiança de 95%"
    year = 2024

    def detect(self, ctx: SheetContext) -> Detection:
        t, ev, score = ctx.title, [], 0.0
        years = {y for y in (t.year, t.footer_year) if y}
        if years and self.year not in years:
            return Detection(0.0, [f"ano {sorted(years)} no título/rodapé difere de {self.year}"])
        if _THREE_PART.match(t.table_id):
            score += 0.3
            ev.append(f"código de tabela em 3 níveis ({t.table_id})")
        if t.year == self.year or t.footer_year == self.year:
            score += 0.3
            ev.append(f"ano {self.year} no título/rodapé")
        if t.confidence_level == 95 and not t.is_cv_sheet:
            score += 0.3
            ev.append("título indica intervalo de confiança de 95%")
        if "(cv)" in ctx.grid.sheet.lower():
            score = 0.0
            ev.append("aba de CV — não pertence a esta família")
        if t.population_code.startswith("ESCOLARES_13_17"):
            score += 0.1
            ev.append("população: escolares de 13 a 17 anos")
        return Detection(score, ev)

    def edition_id(self, ctx: SheetContext) -> str:
        return f"PENSE_{self.year}"


class Pense2019EstimateAdapter(Pense2024EstimateAdapter):
    """PeNSE 2019: mesma gramática das tabelas de 2024 (x.y.z, percentual + IC95%, 13 a 17 anos).

    Diferenças observadas no Tema 17: sem abas de CV; nas abas x.y.1 as seções de linha
    são a dependência administrativa (Total / Pública / Privada), não os grupos de idade.
    """

    family_id = "PENSE_2019_IC"
    description = "PeNSE 2019 — abas de estimativa com intervalo de confiança de 95%"
    year = 2019


class Pense2015Amostra2Adapter(Pense2024EstimateAdapter):
    """PeNSE 2015 Amostra 2 (escolares de 13 a 17 anos; Brasil e Grandes Regiões).

    Tabelas 2.x.y com percentual + IC95%, colunas Total / Sexo / Dependência administrativa e
    seções de linha por faixa etária. Exige "Amostra 2" no rodapé para não confundir com a
    Amostra 1 (9º ano) do mesmo ano.
    """

    family_id = "PENSE_2015_A2"
    description = "PeNSE 2015 Amostra 2 — percentual com intervalo de confiança de 95% (13 a 17 anos)"
    year = 2015

    def detect(self, ctx: SheetContext) -> Detection:
        if ctx.title.sample != "Amostra 2":
            return Detection(0.0, ["rodapé não indica Amostra 2"])
        det = super().detect(ctx)
        return Detection(min(1.0, det.score + 0.1), det.evidence + ["rodapé indica Amostra 2"])

    def edition_id(self, ctx: SheetContext) -> str:
        return "PENSE_2015_A2"

    def table_codes(self, table_id: str) -> tuple[str, str]:
        # 2.<tema>.<tabela>: o 3º nível é a TABELA (2.11.1 ≠ 2.11.10), não um recorte como em 2024
        p = table_id.split(".")
        return p[1], table_id


class Pense2024CVAdapter(Pense2024EstimateAdapter):
    family_id = "PENSE_2024_CV"
    description = "PeNSE 2024 — abas de coeficiente de variação (CV)"
    record_kind = "cv"

    def detect(self, ctx: SheetContext) -> Detection:
        t, ev, score = ctx.title, [], 0.0
        if _THREE_PART.match(t.table_id):
            score += 0.3
            ev.append(f"código de tabela em 3 níveis ({t.table_id})")
        if t.year == self.year or t.footer_year == self.year:
            score += 0.3
            ev.append(f"ano {self.year} no título/rodapé")
        if t.is_cv_sheet:
            score += 0.3
            ev.append("título indica coeficiente de variação")
        if "(cv)" in ctx.grid.sheet.lower():
            score += 0.1
            ev.append("nome da aba termina em (CV)")
        return Detection(score, ev)


class Pense2009CapitaisAdapter(BaseAdapter):
    family_id = "PENSE_2009_CAPITAIS"
    description = "PeNSE 2009 — tabelas legadas XLS por capitais (9º ano)"

    def detect(self, ctx: SheetContext) -> Detection:
        t, ev, score = ctx.title, [], 0.0
        if t.multi_year:
            return Detection(0.0, ["título com vários anos — tratado pela família PENSE_MULTIANO"])
        if _TWO_PART.match(t.table_id):
            score += 0.3
            ev.append(f"código de tabela em 2 níveis ({t.table_id})")
        if t.year == 2009 or t.footer_year == 2009:
            score += 0.3
            ev.append("ano 2009 no título/rodapé")
        if t.territorial_scope == "capital":
            score += 0.2
            ev.append("recorte: municípios das capitais")
        if t.population_code.startswith("ESCOLARES_9ANO"):
            score += 0.2
            ev.append("população: escolares do 9º ano")
        return Detection(score, ev)

    def edition_id(self, ctx: SheetContext) -> str:
        return "PENSE_2009"


class Pense2015Amostra1Adapter(BaseAdapter):
    family_id = "PENSE_2015_A1"
    description = "PeNSE 2015 Amostra 1 — estimativas total e percentual (9º ano)"

    def detect(self, ctx: SheetContext) -> Detection:
        t, ev, score = ctx.title, [], 0.0
        if _FOUR_PART.match(t.table_id):
            score += 0.3
            ev.append(f"código de tabela em 4 níveis ({t.table_id})")
        if t.year == 2015 or t.footer_year == 2015:
            score += 0.3
            ev.append("ano 2015 no título/rodapé")
        if t.sample == "Amostra 1":
            score += 0.2
            ev.append("rodapé indica Amostra 1")
        if t.population_code.startswith("ESCOLARES_9ANO"):
            score += 0.2
            ev.append("população: escolares do 9º ano")
        return Detection(score, ev)

    def edition_id(self, ctx: SheetContext) -> str:
        return "PENSE_2015_A1"

    def table_codes(self, table_id: str) -> tuple[str, str]:
        # 1.<recorte>.<tema>.<tabela>: 1.1.6.1 (UF) e 1.2.6.1 (capitais) são o mesmo indicador
        p = table_id.split(".")
        return p[2], f"{p[0]}.{p[2]}.{p[3]}"


class PenseMultiYearAdapter(BaseAdapter):
    """Tabelas com mais de um ano (ex.: título "- 2009-2015" e colunas "2009 | 2012 | 2015").

    O ano de cada valor vem do cabeçalho ou da seção da linha; o título só informa o
    intervalo. Valores sem ano identificável ficam ``ANO_INDEFINIDO`` (revisão). Nenhuma
    tabela deste tipo existe nos arquivos atuais — a família garante que, se aparecer,
    os anos não sejam misturados nem lidos como categorias.
    """

    family_id = "PENSE_MULTIANO"
    description = "PeNSE — tabelas com vários anos na mesma aba"

    def detect(self, ctx: SheetContext) -> Detection:
        t, ev, score = ctx.title, [], 0.0
        if t.multi_year:
            score += 0.6
            ev.append(f"título com vários anos ({', '.join(map(str, t.years_in_title))})")
        if t.table_id:
            score += 0.2
            ev.append(f"código de tabela ({t.table_id})")
        if any("saude do escolar" in n.lower().replace("ú", "u") for n in t.footnotes):
            score += 0.2
            ev.append("rodapé cita a PeNSE")
        return Detection(score, ev)

    def edition_id(self, ctx: SheetContext) -> str:
        """Série publicada como um conjunto: o ano fica em ``edition_year`` de cada valor.

        Ex.: indicadores comparáveis do 9º ano nas capitais (IBGE, 2009–2019). Um id estável
        mantém o mesmo indicador ao longo dos anos e evita misturar a série com a edição
        regular do mesmo ano (ex.: PeNSE 2019 de 13 a 17 anos).
        """
        t = ctx.title
        if t.population_code.startswith("ESCOLARES_9ANO"):
            return "PENSE_SERIE_9ANO_CAPITAIS" if t.territorial_scope == "capital" else "PENSE_SERIE_9ANO"
        return "PENSE_SERIE_MULTIANO"

    def edition_for_year(self, ctx: SheetContext, year: int) -> str:
        return self.edition_id(ctx)


ALL_ADAPTERS: list[BaseAdapter] = [
    Pense2024EstimateAdapter(),
    Pense2024CVAdapter(),
    Pense2019EstimateAdapter(),
    Pense2009CapitaisAdapter(),
    Pense2015Amostra1Adapter(),
    Pense2015Amostra2Adapter(),
    PenseMultiYearAdapter(),
]
